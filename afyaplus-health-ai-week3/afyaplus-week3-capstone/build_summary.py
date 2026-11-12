"""Phase 5: builds a one-page executive memo from Phase 1-4 outputs.
Run:  python build_summary.py   then open executive_summary.html -> Print -> Save as PDF."""
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

E, D, C = config.EVAL_DIR, config.DRIFT_DIR, config.COST_DIR
comp = pd.read_csv(E / "model_comparison.csv")
gates = pd.read_csv(E / "quality_gate_summary.csv")
routing = pd.read_csv(E / "routing_table.csv")
judge = pd.read_csv(E / "llm_judge_matrix.csv")
raw = pd.read_csv(E / "raw_metrics_log.csv")
run = json.loads((E / "run_status.json").read_text())
drift = json.loads((D / "drift_alert_log.json").read_text())
by_model = pd.read_csv(C / "cost_by_model.csv").set_index("model")
savings = pd.read_csv(C / "routing_savings.csv")
prompts = pd.read_csv(C / "prompt_config_savings.csv")
cpr = pd.read_csv(C / "cost_per_request.csv")
budget = json.loads((C / "budget_status.json").read_text())

LABEL = {"rouge_l": "answer quality (ROUGE-L)", "latency_ms": "response time", "input_tokens": "patient message length"}
FEAT = {"triage_advisor": "USSD triage", "medication_assistant": "Mobile App medication help", "clinical_faq": "Web Portal health FAQ"}
money = lambda x: f"${x:,.2f}"
score = lambda x, p=1: "n/a" if pd.isna(x) else f"{x:.{p}f}"

overall = comp[comp.feature == "ALL"].set_index("model")
n_q = raw["id"].nunique()
n_pass, n_combo = int((gates.gate_status == "PASS").sum()), len(gates)
passed = {m: [FEAT[f] for f in gates[(gates.model == m) & (gates.gate_status == "PASS")].feature] for m in config.MODELS}
low_ground = judge[judge.judge_groundedness <= 2].groupby("model").size().reindex(config.MODELS, fill_value=0)
min_corr = judge.groupby("model").judge_correctness.min()
total = savings[savings.feature == "TOTAL"].iloc[0]
weighted = cpr[(cpr.prompt_config == config.PRODUCTION_PROMPT_CONFIG) & (cpr.feature == "traffic_weighted")].set_index("model").cost_per_request_usd
best_prompt = prompts.sort_values("monthly_token_cost_usd").iloc[0]
first, alerts = drift.get("first_drift"), drift.get("alerts", [])
hitl_ratio = total.current_hitl_cost_usd / max(total.current_token_cost_usd, 1e-9)
if n_pass < n_combo:
    hitl_txt = (f"Clinician review is the bigger cost: answers from a model that failed a channel's safety check need 100% review "
                f"at {money(config.HITL_COST_PER_REVIEW_USD)} each (assumed ~2 minutes of clinical officer time), adding "
                f"{money(total.current_hitl_cost_usd)} per month, {hitl_ratio:,.0f}× the API bill.")
else:
    hitl_txt = (f"Clinician review is the bigger cost: every model passed, so only a {config.HITL_REVIEW_RATE_PASS:.0%} spot audit is needed "
                f"at {money(config.HITL_COST_PER_REVIEW_USD)} per reviewed answer (assumed ~2 minutes of clinical officer time). "
                f"That still adds {money(total.current_hitl_cost_usd)} per month, {hitl_ratio:,.0f}× the API bill.")

triage_routed = routing.set_index("feature").loc["triage_advisor", "routed_model"]
canary_txt = (" Each channel was tested on only 5 questions, so move USSD triage gradually (start with 10% of triage traffic) "
              "and re-run the safety check weekly." if triage_routed == "gpt-4o-mini" else "")
drift_txt = (f"drift monitoring first flagged a shift in {LABEL[first['column']]} in Month {first['month']}"
             if first else "drift monitoring found no significant shift across three months")
exec_summary = (
    f"We tested gpt-4o and gpt-4o-mini on {n_q} clinical questions across USSD, Mobile App and Web Portal. "
    f"On a 1–5 clinical review scale gpt-4o averaged {score(overall.loc['gpt-4o', 'judge_overall'])} and gpt-4o-mini "
    f"{score(overall.loc['gpt-4o-mini', 'judge_overall'])}; {n_pass} of {n_combo} model–channel combinations met every safety threshold. "
    f"Sending each feature to the cheapest model that meets those thresholds moves monthly running cost (API fees plus clinician "
    f"review) from {money(total.current_total_usd)} to {money(total.optimised_total_usd)}, and {drift_txt}.")

def model_line(m):
    o = overall.loc[m]
    return (f"<li><b>{m}</b>: correctness {score(o.judge_correctness)}/5 (±{score(o.judge_correctness_std)} between answers), "
            f"groundedness {score(o.judge_groundedness)}/5, relevance {score(o.judge_relevance)}/5, "
            f"helpfulness {score(o.judge_helpfulness)}/5; weakest single answer scored {score(min_corr.get(m), 0)}/5 for correctness; "
            f"wording overlap with the protocol (ROUGE-L, 0–1) {score(o.rouge_l, 2)}. "
            f"Meets safety thresholds for: {', '.join(passed[m]) or 'none'}.</li>")

route_txt = "; ".join(f"{FEAT[r.feature]} → {r.routed_model}" + (" with full clinician review (no model passed)" if r.human_review_required else "")
                      for r in routing.itertuples())
alert_txt = "; ".join(f"Month {a['month']}: {LABEL[a['column']]} ({a['pct_change']:+.0f}% vs launch)" for a in alerts) or "no measure changed significantly"
prompt_rec = (f"Moving from the {config.PRODUCTION_PROMPT_CONFIG.replace('_', ' ')} prompt to {best_prompt.prompt_config.replace('_', ' ')} "
              f"cuts API fees by {money(best_prompt.saving_vs_production_usd)} per month ({best_prompt.saving_pct:.0f}%). "
              f"Safety condition: roll out only after the shorter prompt passes the same 15-question safety check."
              if best_prompt.prompt_config != config.PRODUCTION_PROMPT_CONFIG else
              "The current prompt is already the cheapest configuration tested; no prompt change recommended.")

mock_note = ('<p class="warn"><b>Simulation notice:</b> model answers and clinical scores were produced in mock mode '
             '(no live API calls). Re-run with API credit before acting on these figures.</p>') if run["mode"] == "mock" else ""

CSS = """<style>@page{size:A4;margin:12mm}body{font-family:Arial,Helvetica,sans-serif;font-size:9.2pt;line-height:1.33;color:#111;max-width:186mm;margin:auto}
h1{font-size:13pt;margin:0 0 3px}h2{font-size:10pt;margin:7px 0 3px;color:#0b5394;border-bottom:1px solid #ccc}
ul,ol{margin:2px 0 2px 16px;padding:0}li{margin-bottom:2px}p{margin:3px 0}.meta{font-size:8.5pt;color:#444}
.warn{background:#fff3cd;border:1px solid #e0c36a;padding:3px 6px;font-size:8.5pt}.foot{font-size:7.5pt;color:#555;margin-top:6px}</style>"""

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>AfyaPlus Executive Summary</title>{CSS}</head><body>
<h1>Memorandum: AfyaPlus Generative AI Layer, Quality, Cost and Risk</h1>
<p class="meta"><b>To:</b> CTO; Medical Director &nbsp; <b>From:</b> Olu, AI Engineering &nbsp; <b>Date:</b> {date.today():%d %B %Y}</p>
{mock_note}
<h2>Executive summary</h2><p>{exec_summary}</p>

<h2>Quality performance</h2>
<p>An independent AI reviewer (gpt-4o acting as judge) scored each answer against an approved clinical protocol. <i>Correctness</i> = clinically accurate;
<i>groundedness</i> = makes no claims beyond the protocol, which is our guard against made-up advice ("hallucination"). Safety threshold: average ≥ 4/5
and no single answer below 3/5.</p>
<ul>{model_line('gpt-4o')}{model_line('gpt-4o-mini')}</ul>

<h2>Cost &amp; efficiency</h2><ul>
<li>30-day API spend at today's split (75% gpt-4o-mini, 25% gpt-4o): {money(by_model.token_cost_usd.sum())} for {int(by_model.requests.sum()):,} requests.
gpt-4o handles {by_model.loc['gpt-4o', 'share_of_requests_pct']:.0f}% of requests but accounts for {by_model.loc['gpt-4o', 'share_of_token_cost_pct']:.0f}% of spend.</li>
<li>Cost per request: gpt-4o-mini ${weighted['gpt-4o-mini']:.5f}, gpt-4o ${weighted['gpt-4o']:.5f} ({weighted['gpt-4o'] / weighted['gpt-4o-mini']:.0f}× more).</li>
<li>{hitl_txt}</li>
<li>Routing by safety check: API fees {money(total.current_token_cost_usd)} → {money(total.optimised_token_cost_usd)}; clinician review
{money(total.current_hitl_cost_usd)} → {money(total.optimised_hitl_cost_usd)}; net saving {money(total.total_saving_usd)} ({total.total_saving_pct:.0f}%).</li></ul>

<h2>Operational risks</h2><ul>
<li><b>Drift</b> (a statistically significant change in incoming patient messages or answer quality compared with launch, measured on
three months of simulated traffic): {alert_txt}.</li>
<li><b>Hallucination</b>: {low_ground['gpt-4o-mini']} of {n_q} gpt-4o-mini answers and {low_ground['gpt-4o']} of {n_q} gpt-4o answers scored 2/5 or lower on
groundedness; {run['judge_parse_failures']} reviewer outputs could not be read.</li>
<li><b>Budget</b>: day-{budget['latest_day']} spend is {budget['daily_utilisation_pct']:.0f}% of the {money(budget['daily_cap_usd'])} daily cap; on current growth, next month is
projected at {money(budget['projected_next_month_usd'])} ({budget['projected_next_month_utilisation_pct']:.0f}% of the {money(budget['monthly_cap_usd'])} monthly cap).</li></ul>

<h2>Recommended actions</h2><ol>
<li><b>Route each channel by safety check</b>: {route_txt}. Saves {money(total.total_saving_usd)} per month, and every live model meets the clinical thresholds.{canary_txt}</li>
<li><b>Shorten the system prompt</b>: {prompt_rec}</li>
<li><b>Re-test automatically when drift is detected</b>: when the alert log flags a change, automatically re-run the 15-question safety check (API cost
{money(run['generation_cost_usd'])} per run) and freeze routing changes until it passes, so declining quality is caught before it reaches patients.</li></ol>
<p class="foot">Sources: evaluation/model_comparison.csv, quality_gate_summary.csv, llm_judge_matrix.csv; drift/drift_alert_log.json; cost/routing_savings.csv,
cost_by_model.csv, cost_per_request.csv, prompt_config_savings.csv, budget_status.json. Pricing: OpenAI list prices in config.py. Data mode: {run['mode']}.</p>
</body></html>"""

(ROOT / "executive_summary.html").write_text(html, encoding="utf-8")
print("Wrote executive_summary.html. Open it in a browser and Print → Save as PDF (executive_summary.pdf).")
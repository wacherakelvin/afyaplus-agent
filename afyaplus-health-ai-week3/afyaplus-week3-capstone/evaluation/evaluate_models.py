"""Phase 1: Clinical evaluation pipeline.
Runs gpt-4o-mini and gpt-4o on the 15-question set, scores BLEU / ROUGE / Token F1 and the
LLM-as-a-Judge, aggregates per model x feature (mean + spread), applies quality gates and derives routing.
Run from the repo root:  python evaluation/evaluate_models.py
"""
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import config  # noqa: E402
from evaluator import evaluate_response  # noqa: E402
from evaluation_data import EVALUATION_DATA  # noqa: E402

DIMS = ["correctness", "groundedness", "relevance", "helpfulness"]
LEX_COLS = ["bleu_4", "rouge_1", "rouge_2", "rouge_l", "token_f1"]
JUDGE_COLS = [f"judge_{d}" for d in DIMS] + ["judge_overall"]
KEY_COLS = ["id", "channel", "feature", "model", "mode"]

BASE_PROMPT = ("You are AfyaPlus, a clinical guidance assistant for patients and community health "
               "workers in Kenya. Give safe, accurate, guideline-based advice. Always say clearly when "
               "the person must go to a health facility or call emergency services. Do not invent facts.")
CHANNEL_STYLE = {"USSD": "Reply in under 60 words of plain text (USSD screen).",
                 "Mobile App": "Reply in under 120 words.",
                 "Web Portal": "Reply in under 200 words."}


def system_prompt(item):
    return f"{BASE_PROMPT} {CHANNEL_STYLE[item['channel']]}"


def est_tokens(text):
    return max(1, round(len(text.split()) * 1.33))


# ---------- generation ----------
_llms = {}

def generate_live(model, item):
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI
    if model not in _llms:
        _llms[model] = ChatOpenAI(model=model, temperature=0, max_tokens=400)
    start = time.perf_counter()
    msg = _llms[model].invoke([SystemMessage(content=system_prompt(item)),
                               HumanMessage(content=item["question"])])
    latency = (time.perf_counter() - start) * 1000
    usage = getattr(msg, "usage_metadata", None) or {}
    return msg.content.strip(), latency, usage.get("input_tokens", 0), usage.get("output_tokens", 0)


MINI_KEEP = {"triage_advisor": (0.35, 0.60), "medication_assistant": (0.50, 0.75), "clinical_faq": (0.80, 0.95)}

def generate_mock(model, item):
    """Deterministic stand-in so the pipeline runs without API credit. Every output is tagged mode=mock."""
    rng = random.Random(f"{model}:{item['id']}")
    words = item["clinical_reference"].split()
    if model == "gpt-4o":
        text = " ".join(w for w in words if rng.random() > 0.15)      # keeps ~85% of the protocol
        latency = rng.gauss(1800, 250)
    else:
        lo, hi = MINI_KEEP[item["feature"]]                          # omits part of the protocol
        text = " ".join(words[: int(len(words) * rng.uniform(lo, hi))])
        text += " Please visit a health facility if you are worried."
        latency = rng.gauss(850, 120)
    return text, max(latency, 100.0), est_tokens(system_prompt(item) + " " + item["question"]), est_tokens(text)


# ---------- judging ----------
def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def judge_mock(item, hypothesis):
    ref, hyp = _words(item["clinical_reference"]), _words(hypothesis)
    recall = len(ref & hyp) / max(len(ref), 1)
    precision = len(ref & hyp) / max(len(hyp), 1)
    score = lambda x: int(min(5, max(1, round(1 + 4 * x))))
    return {"correctness": score(recall), "groundedness": score(precision),
            "relevance": score((recall + precision) / 2 + 0.1), "helpfulness": score(recall + 0.05),
            "reasoning": "MOCK heuristic score from overlap with the reference protocol (no LLM call)."}

def judge_live(item, hypothesis):
    from llm_judge import llm_judge
    return llm_judge(item["question"], item["clinical_reference"], hypothesis, judge_model=config.JUDGE_MODEL)

def parse_scores(j):
    try:
        s = {d: float(j[d]) for d in DIMS}
    except (KeyError, TypeError, ValueError):
        return None
    return s if all(1 <= v <= 5 for v in s.values()) else None


# ---------- pipeline ----------
def main():
    generate = generate_mock if config.MOCK_MODE else generate_live
    judge = judge_mock if config.MOCK_MODE else judge_live
    print(f"Phase 1 | mode={config.MODE} | {len(EVALUATION_DATA)} questions x {len(config.MODELS)} models")

    rows, gen_errors, judge_failures = [], 0, 0
    for item in EVALUATION_DATA:
        for model in config.MODELS:
            row = {"id": item["id"], "channel": item["channel"], "feature": item["feature"],
                   "model": model, "mode": config.MODE, "question": item["question"],
                   "clinical_reference": item["clinical_reference"], "error": None}
            try:
                text, latency, tin, tout = generate(model, item)
            except Exception as exc:
                gen_errors += 1
                print(f"  ! generation failed {item['id']} {model}: {exc}")
                rows.append({**row, "error": str(exc)})
                continue
            price = config.PRICING[model]
            row.update(response=text, latency_ms=round(latency, 1), input_tokens=tin, output_tokens=tout,
                       cost_usd=(tin * price["input"] + tout * price["output"]) / 1e6,
                       **evaluate_response(item["clinical_reference"], text))
            try:
                raw_judge = judge(item, text)
            except Exception as exc:
                raw_judge = {"reasoning": f"Judge error: {exc}"}
            scores = parse_scores(raw_judge)
            if scores is None:
                judge_failures += 1
                row.update({f"judge_{d}": None for d in DIMS}, judge_overall=None, judge_ok=False)
            else:
                row.update({f"judge_{d}": v for d, v in scores.items()},
                           judge_overall=round(sum(scores.values()) / 4, 2), judge_ok=True)
            row["judge_reasoning"] = raw_judge.get("reasoning", "")
            rows.append(row)
            print(f"  {item['id']} {model:<12} ROUGE-L={row['rouge_l']:.2f}  judge={row['judge_overall']}")

    df = pd.DataFrame(rows)
    if "rouge_l" not in df or df["rouge_l"].notna().sum() == 0:
        raise SystemExit("Every generation call failed. If your API balance is $0, run with MOCK_MODE=1.")

    E = config.EVAL_DIR
    df.to_csv(E / "full_evaluation_results.csv", index=False)
    df.reindex(columns=KEY_COLS + LEX_COLS + ["latency_ms", "input_tokens", "output_tokens", "cost_usd"]) \
      .to_csv(E / "raw_metrics_log.csv", index=False)
    df.reindex(columns=KEY_COLS + JUDGE_COLS + ["judge_reasoning"]).to_csv(E / "llm_judge_matrix.csv", index=False)

    # Model comparison: mean scores per model x feature (+ overall), with spread (standard deviation)
    metric_cols = ["bleu_4", "rouge_l", "token_f1"] + JUDGE_COLS + ["latency_ms", "cost_usd"]
    spread_cols = ["rouge_l", "judge_correctness", "judge_overall"]
    by_feature = df.groupby(["model", "feature"])[metric_cols].mean().reset_index()
    spread = (df.groupby(["model", "feature"])[spread_cols].std()
                .add_suffix("_std").reset_index())
    by_feature = by_feature.merge(spread, on=["model", "feature"])
    overall = df.groupby("model")[metric_cols].mean().reset_index()
    overall_spread = df.groupby("model")[spread_cols].std().add_suffix("_std").reset_index()
    overall = overall.merge(overall_spread, on="model").assign(feature="ALL")
    pd.concat([by_feature, overall]).round(4).to_csv(E / "model_comparison.csv", index=False)

    # Quality gates
    G = config.QUALITY_GATES
    checks = [("judge_correctness", "mean", G["mean_correctness"]),
              ("judge_groundedness", "mean", G["mean_groundedness"]),
              ("judge_overall", "mean", G["mean_overall"]),
              ("rouge_l", "mean", G["mean_rouge_l"]),
              ("judge_correctness", "min", G["min_correctness"])]
    gate_rows = []
    for (model, feature), g in df.groupby(["model", "feature"]):
        for col, agg, threshold in checks:
            value = getattr(g[col], agg)()
            passed = pd.notna(value) and value >= threshold
            gate_rows.append({"model": model, "feature": feature, "check": f"{agg}_{col}",
                              "value": round(float(value), 3) if pd.notna(value) else None,
                              "threshold": threshold, "result": "PASS" if passed else "FAIL"})
    gates = pd.DataFrame(gate_rows)
    gates.to_csv(E / "quality_gate_assessment.csv", index=False)
    summary = (gates.assign(failed=gates["check"].where(gates["result"] == "FAIL"))
               .groupby(["model", "feature"])
               .agg(gate_status=("result", lambda r: "PASS" if (r == "PASS").all() else "FAIL"),
                    failed_checks=("failed", lambda s: ", ".join(s.dropna()) or "-"))
               .reset_index())
    summary.to_csv(E / "quality_gate_summary.csv", index=False)

    # Routing: cheapest model that passes every gate for each feature
    cost_per_req = df.groupby(["model", "feature"])["cost_usd"].mean()
    routing = []
    for feature in sorted(df["feature"].unique()):
        passing = summary[(summary.feature == feature) & (summary.gate_status == "PASS")]["model"].tolist()
        if passing:
            best = min(passing, key=lambda m: cost_per_req[(m, feature)])
            routing.append({"feature": feature, "routed_model": best, "gate_status": "PASS",
                            "human_review_required": False})
        else:
            routing.append({"feature": feature, "routed_model": config.FALLBACK_MODEL,
                            "gate_status": "NO_MODEL_PASSED", "human_review_required": True})
    pd.DataFrame(routing).to_csv(E / "routing_table.csv", index=False)

    status = {"mode": config.MODE, "generated_at": datetime.now(timezone.utc).isoformat(),
              "rows": len(df), "generation_errors": gen_errors, "judge_parse_failures": judge_failures,
              "generation_cost_usd": round(float(df["cost_usd"].sum()), 4)}
    (E / "run_status.json").write_text(json.dumps(status, indent=2))

    print("\nQuality gate summary:\n", summary.to_string(index=False))
    print("\nRouting table:\n", pd.DataFrame(routing).to_string(index=False))
    print("\nPhase 1 complete: outputs written to /evaluation")


if __name__ == "__main__":
    main()
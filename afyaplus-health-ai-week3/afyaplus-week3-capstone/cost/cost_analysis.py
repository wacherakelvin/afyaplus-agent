"""Phase 3: Token cost & efficiency analysis.
Simulates 30 days of production at a 75/25 gpt-4o-mini/gpt-4o split, prices it, adds clinician
review overhead, and computes savings from gate-based routing and leaner prompts.
Run from the repo root (after Phase 1):  python cost/cost_analysis.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

PROD = config.PRODUCTION_PROMPT_CONFIG


def tokens(feature, prompt_cfg=PROD):
    f, p = config.FEATURE_TOKENS[feature], config.PROMPT_CONFIGS[prompt_cfg]
    return p["system_tokens"] + f["user_tokens"], f["output_tokens"] * p["output_multiplier"]


def cost_per_request(model, feature, prompt_cfg=PROD):
    tin, tout = tokens(feature, prompt_cfg)
    price = config.PRICING[model]
    return (tin * price["input"] + tout * price["output"]) / 1e6


def load_phase1():
    gates_path, routing_path = config.EVAL_DIR / "quality_gate_summary.csv", config.EVAL_DIR / "routing_table.csv"
    if not (gates_path.exists() and routing_path.exists()):
        raise SystemExit("Run Phase 1 first: python evaluation/evaluate_models.py")
    gates = pd.read_csv(gates_path)
    gate_pass = {(r.model, r.feature): r.gate_status == "PASS" for r in gates.itertuples()}
    return gate_pass, pd.read_csv(routing_path).set_index("feature")


def main():
    C = config.COST_DIR
    gate_pass, routing = load_phase1()
    review_rate = lambda m, f: config.HITL_REVIEW_RATE_PASS if gate_pass.get((m, f), False) else config.HITL_REVIEW_RATE_FAIL
    rng = np.random.default_rng(config.SEED)

    # 1. 30-day simulation
    rows = []
    for day in range(1, config.SIM_DAYS + 1):
        weekday_factor = 0.8 if day % 7 in (6, 0) else 1.0
        total = rng.poisson(config.BASE_DAILY_REQUESTS * weekday_factor * (1 + config.DAILY_GROWTH * (day - 1)))
        for feature, share in config.FEATURE_TRAFFIC_SHARE.items():
            n = int(round(total * share))
            n_mini = int(rng.binomial(n, config.CANARY_SPLIT["gpt-4o-mini"]))
            tin, tout = tokens(feature)
            for model, reqs in (("gpt-4o-mini", n_mini), ("gpt-4o", n - n_mini)):
                rate = review_rate(model, feature)
                rows.append({"day": day, "feature": feature, "model": model, "requests": reqs,
                             "input_tokens": reqs * tin, "output_tokens": reqs * tout,
                             "token_cost_usd": reqs * cost_per_request(model, feature),
                             "hitl_reviews": reqs * rate,
                             "hitl_cost_usd": reqs * rate * config.HITL_COST_PER_REVIEW_USD})
    daily = pd.DataFrame(rows)
    daily.round(6).to_csv(C / "daily_cost_log.csv", index=False)

    # 2. Spend by model and by feature
    sums = ["requests", "input_tokens", "output_tokens", "token_cost_usd", "hitl_reviews", "hitl_cost_usd"]
    by_model = daily.groupby("model")[sums].sum().reset_index()
    by_model["share_of_requests_pct"] = (100 * by_model.requests / by_model.requests.sum()).round(1)
    by_model["share_of_token_cost_pct"] = (100 * by_model.token_cost_usd / by_model.token_cost_usd.sum()).round(1)
    by_model.round(4).to_csv(C / "cost_by_model.csv", index=False)

    by_feature = daily.groupby(["feature", "model"])[sums].sum().reset_index()
    totals = daily.groupby("feature")[sums].sum().reset_index().assign(model="ALL")
    pd.concat([by_feature, totals]).sort_values(["feature", "model"]).round(4).to_csv(C / "cost_by_feature.csv", index=False)

    # 3. Cost per request across prompt configurations
    cpr_rows = []
    for cfg in config.PROMPT_CONFIGS:
        for model in config.MODELS:
            weighted = 0.0
            for feature, share in config.FEATURE_TRAFFIC_SHARE.items():
                tin, tout = tokens(feature, cfg)
                c = cost_per_request(model, feature, cfg)
                weighted += share * c
                cpr_rows.append({"prompt_config": cfg, "model": model, "feature": feature,
                                 "input_tokens": tin, "output_tokens": tout,
                                 "cost_per_request_usd": round(c, 7), "cost_per_1k_requests_usd": round(c * 1000, 4)})
            cpr_rows.append({"prompt_config": cfg, "model": model, "feature": "traffic_weighted",
                             "cost_per_request_usd": round(weighted, 7), "cost_per_1k_requests_usd": round(weighted * 1000, 4)})
    pd.DataFrame(cpr_rows).to_csv(C / "cost_per_request.csv", index=False)

    # 4. Structural savings: route each feature to the cheapest model that clears its gates
    sav_rows = []
    for feature, g in daily.groupby("feature"):
        reqs = g.requests.sum()
        routed = routing.loc[feature, "routed_model"]
        opt_token = reqs * cost_per_request(routed, feature)
        opt_hitl = reqs * review_rate(routed, feature) * config.HITL_COST_PER_REVIEW_USD
        cur_token, cur_hitl = g.token_cost_usd.sum(), g.hitl_cost_usd.sum()
        sav_rows.append({"feature": feature, "requests_30d": int(reqs), "current_routing": "75% mini / 25% 4o",
                         "current_token_cost_usd": cur_token, "current_hitl_cost_usd": cur_hitl,
                         "current_total_usd": cur_token + cur_hitl, "routed_model": routed,
                         "optimised_token_cost_usd": opt_token, "optimised_hitl_cost_usd": opt_hitl,
                         "optimised_total_usd": opt_token + opt_hitl})
    sav = pd.DataFrame(sav_rows)
    num_cols = [c for c in sav.columns if c.endswith("_usd")] + ["requests_30d"]
    total_row = {**sav[num_cols].sum().to_dict(), "feature": "TOTAL", "current_routing": "-", "routed_model": "-"}
    sav = pd.concat([sav, pd.DataFrame([total_row])], ignore_index=True)
    sav["token_saving_usd"] = sav.current_token_cost_usd - sav.optimised_token_cost_usd
    sav["total_saving_usd"] = sav.current_total_usd - sav.optimised_total_usd
    sav["total_saving_pct"] = (100 * sav.total_saving_usd / sav.current_total_usd).round(1)
    sav.round(2).to_csv(C / "routing_savings.csv", index=False)

    # 5. Prompt-configuration savings under optimised routing
    feat_reqs = daily.groupby("feature").requests.sum()
    ps = pd.DataFrame([{"prompt_config": cfg, "monthly_token_cost_usd": sum(
        feat_reqs[f] * cost_per_request(routing.loc[f, "routed_model"], f, cfg) for f in feat_reqs.index)}
        for cfg in config.PROMPT_CONFIGS])
    base = ps.loc[ps.prompt_config == PROD, "monthly_token_cost_usd"].iloc[0]
    ps["saving_vs_production_usd"] = base - ps.monthly_token_cost_usd
    ps["saving_pct"] = (100 * ps.saving_vs_production_usd / base).round(1)
    ps.round(2).to_csv(C / "prompt_config_savings.csv", index=False)

    # 6. Budget status + predictive alert (linear trend projected over the next 30 days)
    per_day = daily.groupby("day").token_cost_usd.sum()
    slope, intercept = np.polyfit(per_day.index, per_day.values, 1)
    next_days = np.arange(config.SIM_DAYS + 1, 2 * config.SIM_DAYS + 1)
    projected = float(np.sum(slope * next_days + intercept))
    latest, month = float(per_day.iloc[-1]), float(per_day.sum())
    d_util, m_util = 100 * latest / config.DAILY_BUDGET_USD, 100 * month / config.MONTHLY_BUDGET_USD
    p_util = 100 * projected / config.MONTHLY_BUDGET_USD
    status = "OVER_BUDGET" if max(d_util, m_util) > 100 else ("AT_RISK" if max(m_util, p_util) >= 80 else "OK")
    budget = {"mode": config.MODE, "daily_cap_usd": config.DAILY_BUDGET_USD, "monthly_cap_usd": config.MONTHLY_BUDGET_USD,
              "latest_day": int(per_day.index[-1]), "latest_day_spend_usd": round(latest, 2),
              "daily_utilisation_pct": round(d_util, 1), "month_spend_usd": round(month, 2),
              "monthly_utilisation_pct": round(m_util, 1), "avg_daily_spend_usd": round(float(per_day.mean()), 2),
              "peak_day_spend_usd": round(float(per_day.max()), 2),
              "days_over_daily_cap": int((per_day > config.DAILY_BUDGET_USD).sum()),
              "projected_next_month_usd": round(projected, 2), "projected_next_month_utilisation_pct": round(p_util, 1),
              "predictive_alert": (f"Projected to exceed monthly cap next month ({p_util:.0f}%)" if p_util >= 100 else None),
              "hitl_month_cost_usd": round(float(daily.hitl_cost_usd.sum()), 2), "status": status}
    (C / "budget_status.json").write_text(json.dumps(budget, indent=2))

    t = sav[sav.feature == "TOTAL"].iloc[0]
    print(f"30-day token spend (75/25): ${month:,.2f} | clinician review: ${budget['hitl_month_cost_usd']:,.2f}")
    print(f"Gate-based routing total: ${t.current_total_usd:,.2f} -> ${t.optimised_total_usd:,.2f} "
          f"(saving ${t.total_saving_usd:,.2f}, {t.total_saving_pct:.1f}%)")
    print(f"Budget status: {status}")
    print("Phase 3 complete: CSVs and budget_status.json in /cost")


if __name__ == "__main__":
    main()
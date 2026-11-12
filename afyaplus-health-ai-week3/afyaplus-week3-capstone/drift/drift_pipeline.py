"""Phase 2: Statistical drift detection with Evidently AI.
Builds a baseline from Phase 1 metrics, simulates three months of production traffic,
writes three HTML reports, a drift trend table and a machine-readable alert log.
Run from the repo root:  python drift/drift_pipeline.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
except ImportError:  # Evidently >= 0.7 moved the classic API under evidently.legacy
    from evidently.legacy.report import Report
    from evidently.legacy.metric_preset import DataDriftPreset

COLUMNS = ["rouge_l", "latency_ms", "input_tokens"]
ROWS_PER_PERIOD = 600
DEFAULT_BASELINE = {"rouge_l": (0.32, 0.10), "latency_ms": (1100.0, 350.0), "input_tokens": (95.0, 25.0)}

# Simulated production story: relative change in each column's mean versus baseline
MONTH_SCENARIOS = {
    1: {"note": "Stable traffic after launch", "rouge_l": 0.0, "latency_ms": 0.0, "input_tokens": 0.0},
    2: {"note": "Mobile App update lets patients paste lab results, so inputs get longer",
        "rouge_l": -0.03, "latency_ms": 0.02, "input_tokens": 0.40},
    3: {"note": "Longer inputs now slow responses and reduce answer quality",
        "rouge_l": -0.20, "latency_ms": 0.30, "input_tokens": 0.65},
}


def baseline_stats():
    log = config.EVAL_DIR / "raw_metrics_log.csv"
    if log.exists():
        df = pd.read_csv(log).dropna(subset=COLUMNS)
        if len(df) >= 5:
            return {c: (float(df[c].mean()), max(float(df[c].std()), 1e-3)) for c in COLUMNS}, "phase1_raw_metrics_log"
    return DEFAULT_BASELINE, "defaults"


def simulate(stats, shifts, rng, n=ROWS_PER_PERIOD):
    df = pd.DataFrame({c: rng.normal(stats[c][0] * (1 + shifts.get(c, 0.0)), stats[c][1], n) for c in COLUMNS})
    df["rouge_l"] = df["rouge_l"].clip(0, 1)
    df["latency_ms"] = df["latency_ms"].clip(lower=50)
    df["input_tokens"] = df["input_tokens"].clip(lower=5).round()
    return df


def column_drift(report_dict):
    """Find Evidently's per-column drift results anywhere in the report dictionary."""
    found = {}
    def walk(obj):
        if isinstance(obj, dict):
            if "drift_by_columns" in obj:
                found.update(obj["drift_by_columns"])
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(report_dict)
    return found


def main():
    D = config.DRIFT_DIR
    rng = np.random.default_rng(config.SEED)
    stats, source = baseline_stats()
    reference = simulate(stats, {}, rng)
    reference.to_csv(D / "reference_baseline.csv", index=False)
    ref_means = {c: float(reference[c].mean()) for c in COLUMNS}

    trend = [{"period": "Baseline", **{f"mean_{c}": round(ref_means[c], 4) for c in COLUMNS}}]
    results = []
    for month, scenario in MONTH_SCENARIOS.items():
        current = simulate(stats, scenario, rng)
        current.to_csv(D / f"month_{month}_production.csv", index=False)
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=reference, current_data=current)
        report.save_html(str(D / f"month_{month}_drift_report.html"))
        drift = column_drift(report.as_dict())

        # Fix 1: never silently report "no drift" because the results could not be parsed
        missing = [c for c in COLUMNS if c not in drift]
        if missing:
            raise SystemExit(f"Could not read Evidently drift results for {missing} in Month {month} "
                             f"(found: {list(drift)}). Check your Evidently version: "
                             'pip install "evidently>=0.4.30,<0.7"')

        row = {"period": f"Month {month}"}
        for c in COLUMNS:
            info = drift[c]
            cur_mean = float(current[c].mean())
            pct = 100 * (cur_mean - ref_means[c]) / ref_means[c]
            detected = bool(info.get("drift_detected", False))
            score = info.get("drift_score")
            row[f"mean_{c}"] = round(cur_mean, 4)
            row[f"pct_change_{c}"] = round(pct, 1)
            row[f"drift_{c}"] = detected
            results.append({"month": month, "column": c, "drift_detected": detected,
                            "drift_score": round(float(score), 6) if score is not None else None,
                            "stattest": info.get("stattest_name"), "threshold": info.get("stattest_threshold"),
                            "reference_mean": round(ref_means[c], 4), "current_mean": round(cur_mean, 4),
                            "pct_change": round(pct, 1)})
        trend.append(row)
        print(f"Month {month}: drift in {[c for c in COLUMNS if row[f'drift_{c}']] or 'none'}")

    pd.DataFrame(trend).to_csv(D / "drift_trend_table.csv", index=False)

    alerts = [{**r, "severity": "CRITICAL" if r["column"] == "rouge_l" else "WARNING",
               "message": f"Drift detected in {r['column']} in Month {r['month']} "
                          f"({r['stattest']}, score={r['drift_score']}, change={r['pct_change']:+.1f}%)"}
              for r in results if r["drift_detected"]]
    first = min(alerts, key=lambda a: (a["month"], a["drift_score"] or 0)) if alerts else None
    first_by_column = {}
    for a in sorted(alerts, key=lambda a: a["month"]):
        first_by_column.setdefault(a["column"], a["month"])

    log = {"generated_at": datetime.now(timezone.utc).isoformat(), "mode": config.MODE,
           "baseline_source": source, "reference_rows": ROWS_PER_PERIOD, "rows_per_month": ROWS_PER_PERIOD,
           "scenario_notes": {m: s["note"] for m, s in MONTH_SCENARIOS.items()},
           "first_drift": first, "first_drift_by_column": first_by_column,
           "alerts": alerts, "monthly_results": results}
    (D / "drift_alert_log.json").write_text(json.dumps(log, indent=2, default=str))

    print("\nFirst drift:", first["message"] if first else "none detected")
    print("Phase 2 complete: 3 HTML reports, drift_trend_table.csv and drift_alert_log.json in /drift")


if __name__ == "__main__":
    main()
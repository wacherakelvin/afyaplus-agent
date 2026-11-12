"""Phase 4: AfyaPlus executive observability dashboard.
Run from the repo root:  uvicorn dashboard.main:app --reload
Endpoints: /  (dashboard)   /health   /api/summary   /metrics (Prometheus)   /reports/<file>.html
"""
import json
import math
import sys
import time
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import config  # noqa: E402

app = FastAPI(title="AfyaPlus Executive Observability Dashboard")
templates = Jinja2Templates(directory=str(HERE / "templates"))
app.mount("/reports", StaticFiles(directory=str(config.DRIFT_DIR), check_dir=False), name="reports")

# ---------- Prometheus metrics ----------
REQUESTS = Counter("afyaplus_dashboard_requests", "HTTP requests served by the dashboard", ["path"])
EXCEPTIONS = Counter("afyaplus_dashboard_exceptions", "Unhandled exceptions in the dashboard", ["path"])
SERVICE_UP = Gauge("afyaplus_service_up", "1 if service is UP (or MOCK), 0 if DOWN", ["service"])
QUALITY = Gauge("afyaplus_quality_score", "Mean evaluation score", ["model", "feature", "metric"])
GATE = Gauge("afyaplus_quality_gate_pass", "1 if the model passes all gates for the feature", ["model", "feature"])
ROUTED = Gauge("afyaplus_feature_routed_model", "1 for the model currently routed per feature", ["feature", "model"])
DRIFT = Gauge("afyaplus_drift_detected", "1 if drift detected in the current month", ["column"])
DRIFT_SCORE = Gauge("afyaplus_drift_score", "Evidently drift score for the current month", ["column"])
SPEND = Gauge("afyaplus_spend_usd", "Token spend in USD", ["window"])
BUDGET = Gauge("afyaplus_budget_utilisation_ratio", "Spend divided by cap", ["window"])
PIPELINE_ERRORS = Gauge("afyaplus_pipeline_errors", "Errors recorded by the last evaluation run", ["type"])
_exceptions = {"n": 0}


@app.middleware("http")
async def track_requests(request: Request, call_next):
    path = "/reports" if request.url.path.startswith("/reports") else request.url.path
    REQUESTS.labels(path).inc()
    try:
        return await call_next(request)
    except Exception:
        EXCEPTIONS.labels(path).inc()
        _exceptions["n"] += 1
        raise


# ---------- data loading ----------
def read_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}

def num(x, digits=3):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else round(x, digits)

_openai = {"t": 0.0, "status": None}

def openai_status():
    if config.MOCK_MODE:
        return "MOCK"
    if _openai["status"] and time.time() - _openai["t"] < 60:
        return _openai["status"]
    try:
        from openai import OpenAI
        OpenAI(timeout=5).models.list()   # free call, confirms key + connectivity
        status = "UP"
    except Exception:
        status = "DOWN"
    _openai.update(t=time.time(), status=status)
    return status


def build_context():
    E, D, C = config.EVAL_DIR, config.DRIFT_DIR, config.COST_DIR
    run = read_json(E / "run_status.json")
    comp = read_csv(E / "model_comparison.csv")
    gates = read_csv(E / "quality_gate_summary.csv")
    routing = read_csv(E / "routing_table.csv")
    drift_log = read_json(D / "drift_alert_log.json")
    budget = read_json(C / "budget_status.json")

    services = {
        "Dashboard API": "UP",
        "Evaluation pipeline (Phase 1)": "UP" if (E / "full_evaluation_results.csv").exists() else "DOWN",
        "Drift pipeline (Phase 2)": "UP" if (D / "drift_alert_log.json").exists() else "DOWN",
        "Cost pipeline (Phase 3)": "UP" if (C / "budget_status.json").exists() else "DOWN",
        "OpenAI API": openai_status(),
    }
    exceptions = {"Dashboard exceptions": _exceptions["n"],
                  "Generation errors (last eval run)": run.get("generation_errors", 0),
                  "Judge parse failures (last eval run)": run.get("judge_parse_failures", 0)}

    routed = dict(zip(routing.feature, routing.routed_model)) if not routing.empty else {}
    gate_map = ({(r.model, r.feature): (r.gate_status, r.failed_checks) for r in gates.itertuples()}
                if not gates.empty else {})
    quality = []
    if not comp.empty:
        for r in comp[comp.feature != "ALL"].sort_values(["feature", "model"]).itertuples():
            gate, failed = gate_map.get((r.model, r.feature), ("N/A", "-"))
            quality.append({"feature": r.feature, "model": r.model,
                            "correctness": num(r.judge_correctness), "groundedness": num(r.judge_groundedness),
                            "overall": num(r.judge_overall), "rouge_l": num(r.rouge_l),
                            "gate": gate, "failed_checks": failed, "routed": routed.get(r.feature) == r.model})

    results = drift_log.get("monthly_results", [])
    current_month = max((r["month"] for r in results), default=None)
    drift_rows = [r for r in results if r["month"] == current_month]

    bars = []
    if budget:
        bars = [
            {"label": f"Daily spend (day {budget['latest_day']})", "spend": budget["latest_day_spend_usd"],
             "cap": budget["daily_cap_usd"], "pct": budget["daily_utilisation_pct"]},
            {"label": "Monthly spend (30 days)", "spend": budget["month_spend_usd"],
             "cap": budget["monthly_cap_usd"], "pct": budget["monthly_utilisation_pct"]},
            {"label": "Projected next month", "spend": budget["projected_next_month_usd"],
             "cap": budget["monthly_cap_usd"], "pct": budget["projected_next_month_utilisation_pct"]},
        ]

    return {"mode": config.MODE, "services": services, "exceptions": exceptions, "quality": quality,
            "routing": routing.to_dict(orient="records") if not routing.empty else [],
            "drift_month": current_month, "drift_rows": drift_rows,
            "first_drift": drift_log.get("first_drift"), "budget": budget, "bars": bars}


def update_metrics(ctx):
    for service, status in ctx["services"].items():
        SERVICE_UP.labels(service).set(0 if status == "DOWN" else 1)
    for name, value in ctx["exceptions"].items():
        if name != "Dashboard exceptions":
            PIPELINE_ERRORS.labels(name.split(" (")[0].lower().replace(" ", "_")).set(value or 0)
    for row in ctx["quality"]:
        for metric in ("correctness", "groundedness", "overall", "rouge_l"):
            if row[metric] is not None:
                QUALITY.labels(row["model"], row["feature"], metric).set(row[metric])
        GATE.labels(row["model"], row["feature"]).set(1 if row["gate"] == "PASS" else 0)
        ROUTED.labels(row["feature"], row["model"]).set(1 if row["routed"] else 0)
    for r in ctx["drift_rows"]:
        DRIFT.labels(r["column"]).set(1 if r["drift_detected"] else 0)
        if r.get("drift_score") is not None:
            DRIFT_SCORE.labels(r["column"]).set(r["drift_score"])
    b = ctx["budget"]
    if b:
        SPEND.labels("daily").set(b["latest_day_spend_usd"])
        SPEND.labels("monthly").set(b["month_spend_usd"])
        BUDGET.labels("daily").set(b["daily_utilisation_pct"] / 100)
        BUDGET.labels("monthly").set(b["monthly_utilisation_pct"] / 100)


# ---------- routes ----------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    ctx = build_context()
    update_metrics(ctx)
    return templates.TemplateResponse(request, "index.html", ctx)

@app.get("/health")
async def health():
    ctx = build_context()
    overall = "UP" if all(s != "DOWN" for s in ctx["services"].values()) else "DEGRADED"
    return {"status": overall, "services": ctx["services"], "exceptions": ctx["exceptions"]}

@app.get("/api/summary")
async def summary():
    return JSONResponse(build_context())

@app.get("/metrics")
async def metrics():
    update_metrics(build_context())
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
# AfyaPlus Week 3 Capstone: Executive Observability Dashboard

## Setup (Windows PowerShell, Python 3.11 recommended)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # add OPENAI_API_KEY; set MOCK_MODE=0 for live runs
```

## Configuration
| Variable | Meaning |
|---|---|
| `OPENAI_API_KEY` | Needed for live generation and the LLM judge |
| `MOCK_MODE` | `1` = deterministic simulated outputs (no API spend). Automatically on if no key is set |
| `JUDGE_MODEL` | Judge model (default `gpt-4o`) |

Pricing, quality gates, traffic split, budgets and clinician-review assumptions are in `config.py`.
Pricing last checked: <add date>.

## Run (from the repo root, in order)
```powershell
python evaluation/evaluate_models.py   # Phase 1 -> /evaluation CSVs + routing_table.csv
python drift/drift_pipeline.py         # Phase 2 -> 3 HTML reports, trend table, alert log
python cost/cost_analysis.py           # Phase 3 -> cost CSVs + budget_status.json
uvicorn dashboard.main:app --reload    # Phase 4 -> http://localhost:8000
python build_summary.py                # Phase 5 -> executive_summary.html -> print to PDF
```

## Dashboard endpoints
- `/` dashboard (health, quality matrix + routing, drift status, budget bars)
- `/metrics` Prometheus scrape endpoint · `/health` · `/api/summary` · `/reports/month_N_drift_report.html`

Prometheus scrape config:
```yaml
scrape_configs:
  - job_name: afyaplus-dashboard
    static_configs: [{ targets: ["host.docker.internal:8000"] }]
```

## Outputs
- **evaluation/**: full_evaluation_results.csv, raw_metrics_log.csv, llm_judge_matrix.csv, model_comparison.csv, quality_gate_assessment.csv, quality_gate_summary.csv, routing_table.csv
- **drift/**: month_{1,2,3}_drift_report.html, drift_trend_table.csv, drift_alert_log.json
- **cost/**: daily_cost_log.csv, cost_by_model.csv, cost_by_feature.csv, cost_per_request.csv, routing_savings.csv, prompt_config_savings.csv, budget_status.json

## Limitations
- Results in `mock` mode are simulated; every output records its mode.
- Drift traffic and 30-day volumes are simulated, seeded with 42 so runs are reproducible.
- Clinical reference answers should be reviewed by a clinician before production use.
# config.py: shared settings for every phase
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL_DIR = ROOT / "evaluation"
DRIFT_DIR = ROOT / "drift"
COST_DIR = ROOT / "cost"
DASH_DIR = ROOT / "dashboard"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# MOCK_MODE=1 runs the whole system on deterministic simulated model outputs (no API spend).
# It also switches on automatically when no OPENAI_API_KEY is set.
MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1" or not os.getenv("OPENAI_API_KEY")
MODE = "mock" if MOCK_MODE else "live"

MODELS = ["gpt-4o-mini", "gpt-4o"]
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4o")
FALLBACK_MODEL = "gpt-4o"   # used when no model passes a feature's gates
SEED = 42

# Channel -> clinical feature
FEATURES = {"USSD": "triage_advisor", "Mobile App": "medication_assistant", "Web Portal": "clinical_faq"}
FEATURE_TRAFFIC_SHARE = {"triage_advisor": 0.50, "medication_assistant": 0.30, "clinical_faq": 0.20}

# USD per 1M tokens. Verify against OpenAI's pricing page and note the date in the README.
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}
CANARY_SPLIT = {"gpt-4o-mini": 0.75, "gpt-4o": 0.25}

# Clinical quality gates (applied per model x feature)
QUALITY_GATES = {
    "mean_correctness": 4.0,
    "mean_groundedness": 4.0,
    "mean_overall": 4.0,
    "mean_rouge_l": 0.20,
    "min_correctness": 3.0,   # safety floor: no single answer may score below this
}

# Token profile per request (assumptions for the 30-day simulation)
FEATURE_TOKENS = {
    "triage_advisor":       {"user_tokens": 40, "output_tokens": 70},
    "medication_assistant": {"user_tokens": 50, "output_tokens": 120},
    "clinical_faq":         {"user_tokens": 60, "output_tokens": 200},
}
PROMPT_CONFIGS = {
    "zero_shot":        {"system_tokens": 80,  "output_multiplier": 1.0},
    "few_shot":         {"system_tokens": 450, "output_multiplier": 1.0},
    "chain_of_thought": {"system_tokens": 200, "output_multiplier": 2.5},
}
PRODUCTION_PROMPT_CONFIG = "chain_of_thought"

# 30-day traffic simulation
SIM_DAYS = 30
BASE_DAILY_REQUESTS = 5000
DAILY_GROWTH = 0.005          # +0.5% per day

# Budget caps (token spend)
DAILY_BUDGET_USD = 6.00
MONTHLY_BUDGET_USD = 160.00

# Human-in-the-loop validation (assumption: ~2 min of clinical officer time per review)
HITL_COST_PER_REVIEW_USD = 0.40
HITL_REVIEW_RATE_FAIL = 1.00  # every answer from a model that failed the feature's gate
HITL_REVIEW_RATE_PASS = 0.02  # 2% spot audit for passing models
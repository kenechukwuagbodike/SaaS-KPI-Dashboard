import logging
import pandas as pd
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

np.random.seed(42)

# ── Config ───────────────────────────────────────────────────────────────────
N_CUSTOMERS = 1000
START_DATE  = pd.Timestamp("2022-01-01")
END_DATE    = pd.Timestamp("2024-12-01")
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "customers.csv"

PLAN_CONFIG = {
    "Starter": {
        "arpu_range":    (60,   120),
        "cac_range":     (200,  400),
        "monthly_churn": 0.060,
        "weight":        0.50,
    },
    "Growth": {
        "arpu_range":    (200,  500),
        "cac_range":     (500,  900),
        "monthly_churn": 0.040,
        "weight":        0.35,
    },
    "Enterprise": {
        "arpu_range":    (800,  2500),
        "cac_range":     (2000, 5000),
        "monthly_churn": 0.015,
        "weight":        0.15,
    },
}

REGIONS        = ["UK", "US", "EU", "APAC"]
REGION_WEIGHTS = [0.30, 0.35, 0.25, 0.10]
NPS_BY_PLAN    = {"Starter": 35, "Growth": 45, "Enterprise": 55}

# ── All calendar months in scope ──────────────────────────────────────────────
all_months   = pd.date_range(START_DATE, END_DATE, freq="MS")
plan_names   = list(PLAN_CONFIG.keys())
plan_weights = [PLAN_CONFIG[p]["weight"] for p in plan_names]

# ── Generate one record per customer ─────────────────────────────────────────
records = []
for cid in range(1, N_CUSTOMERS + 1):
    plan   = np.random.choice(plan_names, p=plan_weights)
    region = np.random.choice(REGIONS, p=REGION_WEIGHTS)
    cfg    = PLAN_CONFIG[plan]

    signup_month = np.random.choice(all_months)

    arpu = round(np.random.uniform(*cfg["arpu_range"]), 2)
    cac  = round(np.random.uniform(*cfg["cac_range"]),  2)

    # Simulate churn month-by-month from signup
    active_months = all_months[all_months >= signup_month]
    churn_month   = None
    for m in active_months:
        if np.random.random() < cfg["monthly_churn"]:
            churn_month = m
            break

    records.append({
        "customer_id":    f"CUST-{cid:04d}",
        "signup_month":   signup_month,
        "plan_tier":      plan,
        "region":         region,
        "arpu":           arpu,
        "cac":            cac,
        "is_active":      churn_month is None,
        "churn_month":    churn_month,
        "nps":            int(np.clip(np.random.normal(NPS_BY_PLAN[plan], 10), 0, 100)),
        "expansion_rate": round(np.random.uniform(0.02, 0.08), 4),
    })

df = pd.DataFrame(records)

# ── Save ──────────────────────────────────────────────────────────────────────
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

logger.info("✓ Generated %d customer records  |  Saved → %s", len(df), OUTPUT_PATH)
logger.info("\nPlan split:\n%s", df["plan_tier"].value_counts().to_string())
logger.info("\nRegion split:\n%s", df["region"].value_counts().to_string())
logger.info("\nActive vs churned: %d active  |  %d churned",
            df["is_active"].sum(), (~df["is_active"]).sum())
logger.info("\nSample (5 rows):\n%s",
            df[["customer_id", "signup_month", "plan_tier", "region", "arpu", "is_active"]]
            .head().to_string(index=False))

"""
pipeline/etl.py
Reads data/customers.csv → outputs data/monthly_kpis.csv
Aggregates 1,000 customer records into 36 monthly KPI rows.
Adds Green / Amber / Red benchmark flags and plain-English insights.
"""
import logging
import numpy as np
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ROOT        = Path(__file__).resolve().parents[1]
INPUT_PATH  = ROOT / "data" / "customers.csv"
OUTPUT_PATH = ROOT / "data" / "monthly_kpis.csv"


# ── Load & prep ───────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, parse_dates=["signup_month", "churn_month"])
ALL_MONTHS = pd.date_range(df["signup_month"].min(), "2024-12-01", freq="MS")


# ── Cohort helpers ────────────────────────────────────────────────────────────
def active_in(month: pd.Timestamp) -> pd.DataFrame:
    """Customers who were paying in `month`."""
    return df[
        (df["signup_month"] <= month)
        & (df["is_active"] | (df["churn_month"] > month))
    ]

def new_in(month: pd.Timestamp) -> pd.DataFrame:
    """Customers who signed up in `month`."""
    return df[df["signup_month"] == month]

def churned_in(month: pd.Timestamp) -> pd.DataFrame:
    """Customers whose churn_month is exactly `month`."""
    return df[df["churn_month"] == month]


# ── RAG flag helper ───────────────────────────────────────────────────────────
def rag(value, green, amber, higher_is_better: bool = True) -> str:
    if pd.isna(value):
        return "N/A"
    if higher_is_better:
        return "Green" if value >= green else ("Amber" if value >= amber else "Red")
    else:
        return "Green" if value <= green else ("Amber" if value <= amber else "Red")


# ── Plain-English insight generator ──────────────────────────────────────────
def build_insight(row: pd.Series) -> str:
    parts = []

    # MRR growth
    if pd.notna(row["mrr_growth_mom"]):
        g = row["mrr_growth_mom"] * 100
        if g > 5:
            parts.append(f"MRR grew {g:.1f}% MoM — strong top-line momentum.")
        elif g >= 0:
            parts.append(f"MRR grew {g:.1f}% MoM — stable but below high-growth benchmark (>5%).")
        else:
            parts.append(f"MRR declined {abs(g):.1f}% MoM — requires immediate attention.")

    # NRR
    if pd.notna(row["nrr"]):
        n = row["nrr"] * 100
        if n > 110:
            parts.append(f"NRR {n:.0f}% — the business grows from existing customers alone.")
        elif n >= 100:
            parts.append(f"NRR {n:.0f}% — revenue retained, but expansion is below best-in-class (>110%).")
        else:
            parts.append(f"NRR {n:.0f}% — churn is outpacing expansion; at-risk revenue base.")

    # LTV:CAC
    if pd.notna(row["ltv_cac"]):
        r = row["ltv_cac"]
        if r >= 3:
            parts.append(f"LTV:CAC {r:.1f}x — above the 3x benchmark; healthy unit economics.")
        elif r >= 2:
            parts.append(f"LTV:CAC {r:.1f}x — approaching benchmark; monitor CAC trend closely.")
        else:
            parts.append(f"LTV:CAC {r:.1f}x — below 2x; acquisition cost is eroding returns.")

    # CAC Payback
    if pd.notna(row["cac_payback_months"]):
        p = row["cac_payback_months"]
        if p <= 12:
            parts.append(f"CAC payback {p:.0f} months — capital-efficient acquisition.")
        elif p <= 18:
            parts.append(f"CAC payback {p:.0f} months — within range but approaching 18-month threshold.")
        else:
            parts.append(f"CAC payback {p:.0f} months — above 18-month benchmark; revisit acquisition spend.")

    # Rule of 40
    if pd.notna(row["rule_of_40"]):
        s = row["rule_of_40"]
        if s >= 40:
            parts.append(f"Rule of 40: {s:.0f} — passes benchmark; strong growth-efficiency balance.")
        elif s >= 20:
            parts.append(f"Rule of 40: {s:.0f} — below 40; growth or margins need improvement.")
        else:
            parts.append(f"Rule of 40: {s:.0f} — significant underperformance on growth-efficiency score.")

    return " | ".join(parts)


# ── Build monthly KPI rows ────────────────────────────────────────────────────
rows     = []
prev_mrr = None

for month in ALL_MONTHS:
    active   = active_in(month)
    new_custs = new_in(month)
    churned  = churned_in(month)

    prev_month  = month - pd.DateOffset(months=1)
    prev_active = active_in(prev_month) if month > ALL_MONTHS[0] else pd.DataFrame()

    n_active  = len(active)
    n_prev    = len(prev_active)

    # ── Revenue ───────────────────────────────────────────────────────────────
    mrr = active["arpu"].sum()
    arr = mrr * 12

    new_mrr     = new_custs["arpu"].sum()
    churned_mrr = churned["arpu"].sum()

    # Expansion MRR: retained customers × their expansion rate
    if not prev_active.empty:
        retained_ids = set(active["customer_id"]) & set(prev_active["customer_id"])
        retained     = active[active["customer_id"].isin(retained_ids)]
        expansion_mrr = (retained["arpu"] * retained["expansion_rate"]).sum()
    else:
        expansion_mrr = 0.0

    # ── NRR ───────────────────────────────────────────────────────────────────
    nrr = ((prev_mrr + expansion_mrr - churned_mrr) / prev_mrr
           if prev_mrr and prev_mrr > 0 else np.nan)

    # ── Churn rate ────────────────────────────────────────────────────────────
    monthly_churn_rate = len(churned) / n_prev if n_prev > 0 else np.nan

    # ── LTV : CAC ─────────────────────────────────────────────────────────────
    if n_active > 0 and pd.notna(monthly_churn_rate) and monthly_churn_rate > 0:
        avg_arpu = active["arpu"].mean()
        avg_cac  = active["cac"].mean()
        ltv      = avg_arpu / monthly_churn_rate
        ltv_cac  = ltv / avg_cac
    else:
        ltv = ltv_cac = np.nan

    # ── CAC Payback ───────────────────────────────────────────────────────────
    cac_payback = (
        new_custs["cac"].mean() / new_custs["arpu"].mean()
        if len(new_custs) > 0 and new_custs["arpu"].mean() > 0
        else np.nan
    )

    # ── MRR growth ───────────────────────────────────────────────────────────
    mrr_growth_mom = (
        (mrr - prev_mrr) / prev_mrr
        if prev_mrr and prev_mrr > 0 else np.nan
    )

    # ── NPS ───────────────────────────────────────────────────────────────────
    avg_nps = active["nps"].mean() if n_active > 0 else np.nan

    rows.append({
        "month":                  month,
        "n_active_customers":     n_active,
        "n_new_customers":        len(new_custs),
        "n_churned_customers":    len(churned),
        "mrr":                    round(mrr, 2),
        "arr":                    round(arr, 2),
        "new_mrr":                round(new_mrr, 2),
        "expansion_mrr":          round(expansion_mrr, 2),
        "churned_mrr":            round(churned_mrr, 2),
        "nrr":                    round(nrr, 4) if pd.notna(nrr) else np.nan,
        "monthly_churn_rate":     round(monthly_churn_rate, 4) if pd.notna(monthly_churn_rate) else np.nan,
        "ltv_cac":                round(ltv_cac, 2) if pd.notna(ltv_cac) else np.nan,
        "cac_payback_months":     round(cac_payback, 1) if pd.notna(cac_payback) else np.nan,
        "mrr_growth_mom":         round(mrr_growth_mom, 4) if pd.notna(mrr_growth_mom) else np.nan,
        "avg_nps":                round(avg_nps, 1) if pd.notna(avg_nps) else np.nan,
    })

    prev_mrr = mrr

kpis = pd.DataFrame(rows)


# ── Rule of 40 (YoY MRR growth + estimated margin) ───────────────────────────
kpis["mrr_yoy_growth_pct"] = (
    (kpis["mrr"] - kpis["mrr"].shift(12)) / kpis["mrr"].shift(12) * 100
).round(2)
est_margin = (kpis["ltv_cac"] - 1).mul(12).clip(-20, 50).fillna(20.0)
kpis["rule_of_40"] = (kpis["mrr_yoy_growth_pct"] + est_margin).clip(upper=200).round(1)


# ── RAG flags ─────────────────────────────────────────────────────────────────
kpis["rag_churn"]       = kpis["monthly_churn_rate"].apply(lambda x: rag(x, 0.03, 0.05, higher_is_better=False))
kpis["rag_ltv_cac"]     = kpis["ltv_cac"].apply(lambda x: rag(x, 3.0, 2.0))
kpis["rag_cac_payback"] = kpis["cac_payback_months"].apply(lambda x: rag(x, 12, 18, higher_is_better=False))
kpis["rag_nrr"]         = kpis["nrr"].apply(lambda x: rag(x * 100 if pd.notna(x) else np.nan, 110, 100))
kpis["rag_rule_of_40"]  = kpis["rule_of_40"].apply(lambda x: rag(x, 40, 20))
kpis["rag_mrr_growth"]  = kpis["mrr_growth_mom"].apply(lambda x: rag(x * 100 if pd.notna(x) else np.nan, 5, 0))


# ── Insights ──────────────────────────────────────────────────────────────────
kpis["insights"] = kpis.apply(build_insight, axis=1)


# ── Save ─────────────────────────────────────────────────────────────────────
kpis.to_csv(OUTPUT_PATH, index=False)
logger.info("✓  %d monthly KPI rows  |  Saved → %s", len(kpis), OUTPUT_PATH)

# ── Spot-check: latest month ──────────────────────────────────────────────────
latest = kpis.iloc[-1]
logger.info("\n── Latest month (%s) ──────────────────────────────", latest["month"].strftime("%b %Y"))
logger.info("  MRR              : £{:,.0f}".format(latest["mrr"]))
logger.info("  ARR              : £{:,.0f}".format(latest["arr"]))
logger.info("  Active customers : {:,}".format(int(latest["n_active_customers"])))
logger.info("  NRR              : {:.1f}%  [{}]".format(latest["nrr"] * 100, latest["rag_nrr"]))
logger.info("  Churn rate       : {:.1f}%  [{}]".format(latest["monthly_churn_rate"] * 100, latest["rag_churn"]))
logger.info("  LTV:CAC          : {:.2f}x  [{}]".format(latest["ltv_cac"], latest["rag_ltv_cac"]))
logger.info("  CAC Payback      : {:.0f} months  [{}]".format(latest["cac_payback_months"], latest["rag_cac_payback"]))
logger.info("  Rule of 40       : {:.0f}  [{}]".format(latest["rule_of_40"], latest["rag_rule_of_40"]))
logger.info("\n  Insight: %s", latest["insights"][:120] + "...")
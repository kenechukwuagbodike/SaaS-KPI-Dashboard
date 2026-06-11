# Project 3 — Executive KPI Dashboard

## What this project does
Board-ready SaaS metrics dashboard. Calculates MRR, ARR, NRR, LTV:CAC ratio,
CAC payback period, and Rule of 40. Benchmarks each KPI against SaaS industry
standards with Green/Amber/Red flags. Generates plain-English insights.
One-click PDF export for investor and board meetings.

## Dataset
- Type: Synthetic SaaS metrics (you generate it)
- Generator: `pipeline/generate_data.py`
- Output: `data/saas_metrics.csv`
- Period: 24 months (2023-01 to 2024-12)
- Fields: month, new_customers, churn_rate, expansion_rate, arpu, cac, nps, support_tickets
- Derived: mrr, ltv, ltv_cac

## Folder structure
```
saas-kpi-dashboard/
├── data/saas_metrics.csv
├── pipeline/
│   ├── generate_data.py     # SaaS cohort data generator
│   └── etl.py               # KPI calculations + benchmark flags + insights text
├── dashboard/
│   └── app.py               # 3-tab Streamlit app
├── requirements.txt
└── README.md
```

## Build order
1. `pipeline/generate_data.py` — generate 24 months of SaaS metrics
2. `pipeline/etl.py` — calculate all KPIs, add RAG flags, generate insights text
3. `dashboard/app.py` — Tab 1: Executive Summary, Tab 2: Growth, Tab 3: Efficiency
4. Add PDF export button (fpdf2) to Tab 1
5. Deploy to Streamlit Community Cloud
6. Screenshot and write case study

## Key metrics to calculate
- MRR = cumulative_customers × (1 - churn_rate) × arpu
- ARR = MRR × 12
- NRR = (MRR + expansion_MRR - churned_MRR) / prior_MRR
- LTV = arpu / churn_rate
- LTV:CAC = LTV / cac  (benchmark: >3x = green, 2-3x = amber, <2x = red)
- CAC Payback = cac / arpu  (benchmark: <12m = green, 12-18m = amber, >18m = red)
- Rule of 40 = revenue_growth_rate + profit_margin  (benchmark: >40% = green)

## Upwork portfolio title
"Executive KPI Dashboard for Data-Driven SaaS Decision Making"

## Demo link (fill in after deployment)
https://share.streamlit.io/...

## GitHub repo
https://github.com/kene-agbodike/saas-kpi-dashboard

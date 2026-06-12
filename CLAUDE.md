# Project 3 — Executive KPI Dashboard

## What this project does
Board-ready SaaS metrics dashboard. Calculates MRR, ARR, NRR, LTV:CAC ratio,
CAC payback period, and Rule of 40. Benchmarks each KPI against SaaS industry
standards with Green/Amber/Red flags. Generates plain-English insights.
One-click PDF export for investor and board meetings.

## Dataset
- Type: Synthetic customer-level SaaS data (you generate it)
- Generator: `pipeline/generate_data.py`
- Output: `data/customers.csv`
- Volume: 1,000 customer records spanning 36 months (2022-01 to 2024-12)
- Fields: customer_id, signup_month, plan_tier, region, arpu, cac, is_active, churn_month, nps, expansion_rate
- Segments: plan_tier (Starter / Growth / Enterprise) × region (UK / US / EU / APAC)
- ETL aggregates this to monthly KPIs — the dashboard never reads customers.csv directly

## Folder structure
```
saas-kpi-dashboard/
├── data/customers.csv          # 1,000 customer records (generated)
├── pipeline/
│   ├── generate_data.py        # Customer-level data generator
│   └── etl.py                  # Aggregates to monthly KPIs + RAG flags + insights
├── dashboard/
│   └── app.py                  # 3-tab Streamlit app
├── requirements.txt
└── README.md
```

## Build order
1. `pipeline/generate_data.py` — generate 1,000 customer records → `data/customers.csv`
2. `pipeline/etl.py` — aggregate to monthly KPIs, add RAG flags, generate insights text
3. `dashboard/app.py` — Tab 1: Executive Summary, Tab 2: Growth, Tab 3: Efficiency
4. Add PDF export button (fpdf2) to Tab 1
5. Deploy to Streamlit Community Cloud
6. Screenshot and write case study

## ETL aggregation logic
For each calendar month, etl.py must:
- Active customers = rows where signup_month <= month AND (churn_month is null OR churn_month > month)
- MRR = sum of arpu for active customers that month
- New customers = count where signup_month == month
- Churned MRR = sum of arpu where churn_month == month
- Expansion MRR = active MRR × mean(expansion_rate)

## Key metrics to calculate
- ARR = MRR × 12
- NRR = (MRR + expansion_MRR - churned_MRR) / prior_MRR  (benchmark: >100% = green)
- LTV = mean(arpu) / mean(monthly_churn_rate)
- LTV:CAC = LTV / mean(cac)  (benchmark: >3x = green, 2–3x = amber, <2x = red)
- CAC Payback = mean(cac) / mean(arpu)  (benchmark: <12m = green, 12–18m = amber, >18m = red)
- Rule of 40 = revenue_growth_rate + profit_margin  (benchmark: >40% = green)

## Segment dimensions available for dashboard filters
- plan_tier: Starter | Growth | Enterprise
- region: UK | US | EU | APAC

## Upwork portfolio title
"Executive KPI Dashboard for Data-Driven SaaS Decision Making"

## Demo link (fill in after deployment)
https://share.streamlit.io/...

## GitHub repo
https://github.com/kene-agbodike/saas-kpi-dashboard

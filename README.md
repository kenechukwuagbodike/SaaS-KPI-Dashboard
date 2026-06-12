# Executive KPI Dashboard for SaaS Decision Making

> A board-ready Software as a Service (SaaS) metrics dashboard built for founders and executives who need a single source of truth on business health. Tracks Monthly Recurring Revenue (MRR), Net Revenue Retention (NRR), Lifetime Value to Customer Acquisition Cost ratio (LTV:CAC), Rule of 40, churn, and more. Every Key Performance Indicator (KPI) is benchmarked against industry standards with Red/Amber/Green (RAG) status colouring, a plain-English insights panel, and one-click board PDF export.

**Live demo →** [kene-saas-kpi.streamlit.app](https://kene-saas-kpi.streamlit.app)

---

## The problem this solves

SaaS founders and product leaders rarely have a clean, single-screen view of their core business health. MRR lives in Stripe. Churn lives in a Customer Relationship Management (CRM) system. Customer Acquisition Cost (CAC) lives in a spreadsheet. Lifetime Value (LTV) is calculated differently by different people. Investors and board members ask the same questions every quarter — and the answers take days to pull together.

This dashboard unifies all of those signals in one place, benchmarks each KPI against SaaS industry standards with RAG colouring (Green = above benchmark, Amber = acceptable but watch closely, Red = below benchmark), and generates a board-ready PDF in one click.

---

## Live dashboard

**→ [View on Streamlit Cloud](https://kene-saas-kpi.streamlit.app)**

Use the sidebar to filter by plan tier (Starter / Growth / Enterprise) or region (UK / US / EU / Asia-Pacific (APAC)). Every chart and metric updates in real time.

---

## Sample outputs

| Output | Description |
|--------|-------------|
| [Board PDF sample](samples/board-snapshot-sample.pdf) | One-page KPI snapshot for investor or board meetings — generated directly from the dashboard |
| [Project case study](samples/saas-kpi-dashboard-case-study.pdf) | Full write-up: what each KPI means, how it is calculated, industry benchmarks, and how the dashboard supports business decisions |

---

## What the dashboard tracks

### Revenue
| KPI | Full Name | Benchmark | What it tells you |
|-----|-----------|-----------|-------------------|
| **MRR** | Monthly Recurring Revenue | Growing >5% month-on-month (MoM) | The heartbeat metric — total subscription revenue collected in a single month |
| **ARR** | Annual Recurring Revenue | — | MRR × 12 — the number investors and boards use to size the business |
| **NRR** | Net Revenue Retention | ≥110% = best-in-class | Measures whether existing customers are growing revenue without any new sales. Above 100% means the existing base alone drives growth |

### Unit Economics
| KPI | Full Name | Benchmark | What it tells you |
|-----|-----------|-----------|-------------------|
| **LTV:CAC** | Lifetime Value to Customer Acquisition Cost | ≥3x healthy, <2x unsustainable | How much lifetime revenue is earned per £1 spent on acquisition |
| **CAC Payback** | Customer Acquisition Cost Payback Period | <12 months | How many months it takes to recover the cost of acquiring a customer |
| **Rule of 40** | Rule of 40 | ≥40 = passes benchmark | Year-on-year (YoY) revenue growth rate + estimated profit margin. A score of 40 or above means the business balances growth and efficiency |

### Retention
| KPI | Full Name | Benchmark | What it tells you |
|-----|-----------|-----------|-------------------|
| **Churn Rate** | Monthly Customer Churn Rate | ≤3% best-in-class, ≤5% acceptable | Percentage of customers cancelling each month — the metric founders check most anxiously |
| **NPS** | Net Promoter Score | — | Customer satisfaction score (rated on 0–10 scale). Early warning signal for future churn |
| **Active Customers** | Active Paying Customers | — | Total paying customers at period end — the denominator behind all percentage metrics |

---

## Dashboard tabs

### Tab 1 — Executive Summary
Nine KPI cards arranged in three rows (Revenue, Unit Economics, Retention). Each card shows the current value, a month-on-month delta, and RAG benchmark status with colour-coded borders and backgrounds. A plain-English insights panel below explains what the numbers mean in plain terms — updated automatically for every filter change. One-click board PDF export at the bottom.

### Tab 2 — Growth
Three charts that tell the acquisition story:
- **MRR Trend** — full-width area chart showing the revenue curve from January 2022 to December 2024
- **New Customers per Month** — bar chart showing acquisition pace and whether the sales pipeline is consistent or lumpy
- **MRR Bridge (waterfall chart)** — breaks current month MRR into Prior MRR + New MRR + Expansion MRR − Churned MRR = Current MRR. Answers the board question: are we growing from new sales, from existing customers expanding, or are we fighting churn?

### Tab 3 — Efficiency
Four charts that answer whether growth is sustainable:
- **LTV:CAC Trend** — with green benchmark line at 3x and amber minimum at 2x
- **CAC Payback Trend** — with green benchmark at 12 months and red threshold at 18 months
- **Rule of 40 Gauge** — speedometer with RAG-coloured zones (Red 0–20, Amber 20–40, Green 40+)
- **Monthly Churn Rate Trend** — red area chart with target (3%) and threshold (5%) benchmark lines

---

## How it is built

### Data architecture
Rather than a simple pre-aggregated monthly table, the pipeline starts from **1,000 individual customer records** — each with their own signup month, plan tier, region, Average Revenue Per User (ARPU), CAC, churn month, and expansion rate. This mirrors how real SaaS companies store data in a CRM or data warehouse, and enables live segment filtering without pre-building every combination.

```
pipeline/generate_data.py   →   data/customers.csv  (1,000 customer rows)
pipeline/etl.py             →   data/monthly_kpis.csv  (36 monthly KPI rows)
dashboard/app.py            →   3-tab Streamlit dashboard
```

**Extract, Transform, Load (ETL) pipeline flow:**
For each of the 36 calendar months, the ETL identifies active, new, and churned customers; calculates all KPIs; applies RAG benchmark flags; and generates plain-English insight text. Output is 36 rows with 24 columns.

### Segment filtering
When a plan tier or region filter is applied, the dashboard re-aggregates all 36 months of KPIs directly from the 1,000 customer records — not from a pre-built pivot table. Results are cached per segment combination so the second selection within a session is instant.

### Rule of 40 methodology note
Uses **year-on-year (YoY)** MRR growth — current month vs the same month twelve months prior — rather than annualised month-on-month growth. This prevents inflated scores of 800%+ during early-stage rapid growth when a near-zero MRR base is compared to the next month. YoY comparison eliminates this distortion because it compares against an already-scaled base.

### Board PDF export
fpdf2 generates a one-page, RAG-colour-coded KPI snapshot on demand. No browser, no print dialog — a clean and consistent layout every time that can be dropped into any board pack.

---

## Tech stack

| Tool | Version | Role |
|------|---------|------|
| Python | 3.12 | Core language |
| pandas | 2.2+ | Data manipulation and ETL aggregation |
| Streamlit | 1.35+ | Dashboard framework and UI |
| Plotly | 5.22+ | Interactive charts (line, bar, waterfall, gauge) |
| fpdf2 | 2.7+ | Board PDF export |
| NumPy | 1.26+ | Numerical operations |

---

## Run locally

**Prerequisites:** Python 3.12, Windows PowerShell (or any terminal on macOS/Linux)

```bash
# 1. Clone the repository
git clone https://github.com/kenechukwuagbodike/SaaS-KPI-Dashboard.git
cd SaaS-KPI-Dashboard

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate        # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

The repository includes pre-generated demo data (`data/customers.csv` and `data/monthly_kpis.csv`) so the dashboard loads immediately. To regenerate from scratch:

```bash
python pipeline/generate_data.py   # regenerates data/customers.csv
python pipeline/etl.py             # regenerates data/monthly_kpis.csv
```

---

## Project structure

```
SaaS-KPI-Dashboard/
├── data/
│   ├── customers.csv              1,000 synthetic customer records
│   └── monthly_kpis.csv           36 monthly KPI rows with RAG flags and insights
├── pipeline/
│   ├── generate_data.py           Synthetic customer data generator
│   └── etl.py                     Aggregation, KPI calculation, RAG flags, insights
├── dashboard/
│   └── app.py                     3-tab Streamlit app with segment filtering and PDF export
├── documentation/
│   └── scripts/
│       └── generate_docs_pdf.py   Regenerates the case study PDF
├── samples/
│   ├── board-snapshot-sample.pdf  Sample board PDF export (one-page KPI snapshot)
│   └── saas-kpi-dashboard-case-study.pdf  Full project case study and KPI reference guide
├── requirements.txt
└── README.md
```

---

## December 2024 snapshot (demo data)

The demo dataset covers 36 months (January 2022 – December 2024) across 1,000 synthetic customers. December 2024 period-end figures:

| Metric | Full Name | Value | RAG Status |
|--------|-----------|-------|------------|
| MRR | Monthly Recurring Revenue | £250,143 | Amber |
| ARR | Annual Recurring Revenue | £3,001,722 | Amber |
| NRR | Net Revenue Retention | 102.8% | Amber |
| LTV:CAC | Lifetime Value to CAC Ratio | 11.1x | Green |
| CAC Payback | Payback Period | 2 months | Green |
| Rule of 40 | Growth + Margin Score | 78 | Green |
| Churn Rate | Monthly Customer Churn | 4.1% | Amber |
| NPS | Net Promoter Score | 43 | — |
| Active Customers | Paying Customers | 470 | — |

---

## About

**Kene Agbodike** — Data & AI Decision Systems Consultant

This project is part of a six-project portfolio demonstrating the full data maturity journey — from reporting automation to Artificial Intelligence (AI) decision intelligence.

**Certifications:**

| Certification | Full Name |
|---------------|-----------|
| DP-700 | Microsoft Fabric Data Engineer Associate |
| DP-600 | Microsoft Fabric Analytics Engineer Associate |
| AZ-305 | Azure Solutions Architect Expert |
| AZ-400 | Azure DevOps Engineer Expert |
| AI-102 | Azure AI Engineer Associate |
| DP-100 | Azure Data Scientist Associate |
| DP-203 | Azure Data Engineer Associate |

[GitHub](https://github.com/kenechukwuagbodike) · [Upwork](https://www.upwork.com/freelancers/~01ffe0a90179159b67)

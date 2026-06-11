# Executive KPI Dashboard

> Board-ready SaaS metrics dashboard — MRR, NRR, LTV:CAC, Rule of 40

Part of the [Data to Decisions](https://github.com/kene-agbodike) portfolio by Kene Agbodike —
Data & AI Decision Systems Consultant.

---

## Overview

Board-ready SaaS metrics dashboard with benchmarked KPIs, plain-English insights panel, and one-click PDF export for investor meetings.

## Stack

`pandas · Streamlit · Plotly · fpdf2`

## Demo

<!-- Add links after deployment -->
- **Live demo:** Streamlit Community Cloud — _link coming soon_

## Getting started

```bash
# Clone the repo
git clone https://github.com/kene-agbodike/saas-kpi-dashboard.git
cd saas-kpi-dashboard

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

## Project structure

```
saas-kpi-dashboard/
├── data/            Raw and processed data
├── pipeline/        ETL, data generation, schedulers
├── dashboard/       Streamlit app (app.py)
├── requirements.txt
└── README.md
```

## Running the dashboard

```bash
streamlit run dashboard/app.py
```

## About

**Kene Agbodike** — Data & AI Decision Systems Consultant

Certifications: Microsoft Fabric Data Engineer Associate · Fabric Analytics Engineer Associate ·
Azure Solutions Architect Expert · Azure AI Engineer · Azure Data Scientist

[GitHub](https://github.com/kene-agbodike) · [Upwork](https://www.upwork.com/freelancers/~01ffe0a90179159b67)

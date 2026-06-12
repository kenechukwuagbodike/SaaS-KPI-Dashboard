"""
documentation/scripts/generate_docs_pdf.py
Generates a standalone project documentation PDF.
Covers: project brief, dataset, ETL pipeline, dashboard tab breakdown, glossary.

Run from the project root:
    python documentation/scripts/generate_docs_pdf.py

Output: documentation/output/saas-kpi-dashboard-docs.pdf
"""
from pathlib import Path
from fpdf import FPDF, XPos, YPos

OUTPUT = Path(__file__).resolve().parents[1] / "output" / "saas-kpi-dashboard-docs.pdf"

PURPLE = (124, 58, 237)
DARK   = (17,  24,  39)
GREY   = (75,  85,  99)
WHITE  = (255, 255, 255)


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, "Executive KPI Dashboard  |  Project Documentation",
                  new_x=XPos.LMARGIN, new_y=YPos.TOP)
        self.cell(0, 8, f"Page {self.page_no()}",
                  align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_draw_color(209, 213, 219)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, "Kene Agbodike  |  Data & AI Decision Systems Consultant",
                  align="C")

    def cover(self):
        self.add_page()
        self.set_fill_color(*PURPLE)
        self.rect(0, 0, 210, 85, "F")
        self.set_y(24)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*WHITE)
        self.cell(0, 12, "Executive KPI Dashboard",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 14)
        self.cell(0, 8, "Project Documentation & Reference Guide",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 7, "June 2026",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(96)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Kene Agbodike",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GREY)
        self.cell(0, 6, "Data & AI Decision Systems Consultant",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, "github.com/kenechukwuagbodike",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)
        self.set_draw_color(*PURPLE)
        self.set_line_width(0.5)
        self.line(30, self.get_y(), 180, self.get_y())
        self.ln(8)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, 7, "Contents",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        for item in [
            "1.  Project Brief",
            "2.  Dataset",
            "3.  ETL Pipeline",
            "4.  Dashboard  -  Tab by Tab",
            "5.  Glossary of Abbreviations",
        ]:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*GREY)
            self.cell(0, 7, item, align="C",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section_header(self, title: str):
        self.ln(4)
        self.set_fill_color(*PURPLE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, f"  {title}",
                  fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*DARK)

    def sub_header(self, title: str):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*PURPLE)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*DARK)
        self.set_draw_color(*PURPLE)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(3)

    def body(self, text: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GREY)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def kpi_entry(self, name: str, detail: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*DARK)
        self.cell(0, 6, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.multi_cell(0, 5, detail)
        self.ln(2)

    def term(self, name: str, definition: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, name)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.multi_cell(0, 5, definition)
        self.ln(3)

    def step_row(self, num: str, file: str, desc: str):
        """Render a numbered build-step row: label | file | description."""
        col1, col2 = 22, 58
        remaining = self.w - self.l_margin - self.r_margin - col1 - col2
        y_before = self.get_y()
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*DARK)
        self.cell(col1, 6, num,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(col2, 6, file,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        x_desc = self.get_x()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GREY)
        self.multi_cell(remaining, 6, desc)
        y_after = self.get_y()
        self.set_y(max(y_before + 6, y_after))


def build():
    pdf = Doc()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.cover()

    # ══════════════════════════════════════════════════════════════════════════
    # 1. PROJECT BRIEF
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("1.  Project Brief")

    pdf.sub_header("Overview")
    pdf.body(
        "The Executive KPI Dashboard is the featured portfolio piece in the Data to "
        "Decisions Upwork portfolio built by Kene Agbodike. Of the six portfolio "
        "projects this one speaks most directly to the decision-maker who holds the "
        "budget. SaaS founders and executives immediately recognise these metrics - "
        "and immediately recognise that most freelancers cannot build this."
    )
    pdf.body(
        "SaaS founders and product leaders routinely lack a clear, single-screen view "
        "of their core business health. MRR lives in Stripe, churn in their CRM, CAC "
        "in a spreadsheet, and LTV is calculated inconsistently by different people. "
        "This project builds a board-ready SaaS metrics dashboard that unifies all of "
        "these signals in one place."
    )

    pdf.sub_header("Upwork Positioning")
    pdf.body(
        "Portfolio title: 'Executive KPI Dashboard for Data-Driven SaaS Decision Making'\n"
        "Target clients: Founders, C-suite executives, product leaders, investors "
        "needing board-ready reporting.\n"
        "Phase 1 rate: GBP70/hr  -  Python pipelines + Power BI / Streamlit dashboards\n"
        "Phase 2 rate: GBP100-150/hr  -  AI strategy + decision intelligence systems"
    )

    pdf.sub_header("Tech Stack")
    pdf.body(
        "Python 3.12  |  pandas 2.2+  |  Streamlit 1.35+  |  Plotly 5.22+  |  "
        "fpdf2 2.7+  |  NumPy 1.26+\n"
        "Platform: Windows 11  |  IDE: VS Code  |  Terminal: PowerShell"
    )

    pdf.sub_header("Certifications (Kene Agbodike)")
    pdf.body(
        "Microsoft Fabric Data Engineer Associate (DP-700)\n"
        "Microsoft Fabric Analytics Engineer Associate (DP-600)\n"
        "Azure Solutions Architect Expert (AZ-305)\n"
        "Azure DevOps Engineer Expert (AZ-400)\n"
        "Azure AI Engineer Associate (AI-102)\n"
        "Azure Data Scientist Associate (DP-100)\n"
        "Azure Data Engineer Associate (DP-203)"
    )

    pdf.sub_header("Build Sequence")
    steps = [
        ("Step 1", "generate_data.py",
         "Generate 1,000 synthetic customer records spanning Jan 2022 - Dec 2024."),
        ("Step 2", "etl.py",
         "Aggregate customer-level data to 36 monthly KPI rows. Calculate all metrics, "
         "apply RAG benchmark flags, generate plain-English insights."),
        ("Step 3", "dashboard/app.py",
         "3-tab Streamlit dashboard: Executive Summary, Growth, Efficiency. Segment "
         "filters re-aggregate from customer data on the fly via caching."),
        ("Step 4", "PDF board export",
         "One-click PDF export of current KPI snapshot using fpdf2. No browser print "
         "dialog, no manual formatting."),
        ("Step 5", "Deploy + screenshot",
         "Streamlit Community Cloud deployment. Share link and screenshot in Upwork "
         "portfolio for social proof."),
    ]
    for num, file, desc in steps:
        pdf.step_row(num, file, desc)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. DATASET
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("2.  Dataset")

    pdf.sub_header("Design Decision - Customer-Level Data")
    pdf.body(
        "The original brief specified a simple 24-row monthly aggregate dataset. This "
        "was upgraded to 1,000 individual customer records spanning 36 months "
        "(Jan 2022 - Dec 2024). Each row represents one customer with their own signup "
        "month, plan tier, region, ARPU, CAC, churn status, and expansion rate. The "
        "ETL pipeline then aggregates these into monthly KPIs for the dashboard."
    )
    pdf.body(
        "This mirrors how real SaaS companies actually store data - in a CRM or data "
        "warehouse - making the portfolio piece credible to technical buyers. It also "
        "enables segment-level filtering by plan tier and region, which is a genuine "
        "dashboard differentiator that a monthly aggregate approach cannot support."
    )

    pdf.sub_header("Customer Record Fields  (data/customers.csv)")
    fields = [
        ("customer_id", "Unique identifier - CUST-0001 through CUST-1000"),
        ("signup_month", "Month the customer joined. Spread across Jan 2022 - Dec 2024."),
        ("plan_tier", "Starter (50% of base), Growth (35%), Enterprise (15%)"),
        ("region", "UK 30%, US 35%, EU 25%, APAC 10%"),
        ("arpu",
         "Monthly revenue per customer. Starter GBP60-120, Growth GBP200-500, "
         "Enterprise GBP800-2500"),
        ("cac",
         "Acquisition cost. Starter GBP200-400, Growth GBP500-900, "
         "Enterprise GBP2000-5000"),
        ("is_active", "True if still paying. False if churned."),
        ("churn_month", "Month the customer cancelled. Blank if still active."),
        ("nps", "Net Promoter Score for this customer (0-100 clipped)."),
        ("expansion_rate", "Monthly upsell as a fraction of ARPU. Range 2-8%."),
    ]
    col_w = 42
    remaining = pdf.w - pdf.l_margin - pdf.r_margin - col_w
    for field, desc in fields:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*DARK)
        pdf.cell(col_w, 6, field, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.multi_cell(remaining, 6, desc)

    pdf.sub_header("Churn Simulation by Plan Tier")
    pdf.body(
        "Monthly churn probability is applied customer-by-customer from signup using "
        "plan-tier rates: Starter 6.0%, Growth 4.0%, Enterprise 1.5%. This reflects "
        "the real-world dynamic where enterprise contracts are longer and switching "
        "costs are higher, so enterprise churn is structurally lower."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 3. ETL PIPELINE
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("3.  ETL Pipeline  (pipeline/etl.py)")

    pdf.sub_header("What the Pipeline Does")
    pdf.body(
        "Reads data/customers.csv (1,000 rows) and loops through each calendar month "
        "from Jan 2022 to Dec 2024. For each month it identifies active, new, and "
        "churned customers, calculates all KPIs, applies RAG benchmark flags, and "
        "writes a plain-English insight sentence. "
        "Output is data/monthly_kpis.csv (36 rows, 24 columns)."
    )

    pdf.sub_header("KPI Definitions and Industry Benchmarks")
    kpis = [
        ("MRR  -  Monthly Recurring Revenue",
         "Sum of ARPU for all active customers. The heartbeat metric. "
         "RAG: Green >=5% MoM growth, Amber >=0%, Red declining."),
        ("ARR  -  Annual Recurring Revenue",
         "MRR x 12. The annualised view used in board packs and investor conversations."),
        ("NRR  -  Net Revenue Retention",
         "(Prior MRR + Expansion MRR - Churned MRR) / Prior MRR. Above 100% means "
         "existing customers grow the business without new sales. "
         "Green: >=110%  |  Amber: 100-110%  |  Red: <100%"),
        ("LTV  -  Customer Lifetime Value",
         "Mean ARPU / monthly churn rate. Total revenue expected from one customer "
         "across the full relationship."),
        ("LTV:CAC  -  Lifetime Value to Acquisition Cost Ratio",
         "LTV / Mean CAC. The core unit economics test. "
         "Green: >=3x  |  Amber: 2-3x  |  Red: <2x"),
        ("CAC Payback Period",
         "Mean CAC for new customers / Mean ARPU for new customers. Months to recover "
         "acquisition spend. Green: <12m  |  Amber: 12-18m  |  Red: >18m"),
        ("Rule of 40",
         "YoY MRR growth % + estimated profit margin %. A score >=40 means the "
         "business balances growth and efficiency. Capped at 200 for display clarity. "
         "Green: >=40  |  Amber: 20-40  |  Red: <20"),
        ("Monthly Churn Rate",
         "Customers churned / customers active prior month. SMB SaaS benchmark. "
         "Green: <=3%  |  Amber: 3-5%  |  Red: >5%"),
        ("NPS  -  Net Promoter Score",
         "Average NPS across active customers. No RAG benchmark applied - too "
         "industry-variable to set a universal standard."),
    ]
    for name, desc in kpis:
        pdf.kpi_entry(name, desc)

    pdf.sub_header("Rule of 40 - Methodology Note")
    pdf.body(
        "The growth rate component uses year-on-year MRR growth (current month vs same "
        "month 12 months prior), not annualised month-on-month growth. The original "
        "annualised MoM approach produced scores of 800+ during rapid early growth "
        "because multiplying a 20% MoM rate by 12 gives 240% annual growth. YoY "
        "comparison eliminates this distortion because it compares against an already "
        "scaled base."
    )
    pdf.body(
        "The profit margin is proxied from LTV:CAC efficiency: (LTV:CAC - 1) x 12, "
        "clipped to -20% to 50%. A display cap of 200 is applied so charts remain "
        "readable. From H2 2023 onwards, scores settle in the 78-130 range - credible "
        "for a growth-stage SaaS business."
    )

    pdf.sub_header("December 2024 Snapshot  (most recent period)")
    pdf.body(
        "MRR: GBP250,143        ARR: GBP3,001,722       Active customers: 470\n"
        "NRR: 102.8% [Amber]    Churn rate: 4.1% [Amber]\n"
        "LTV:CAC: 11.1x [Green] CAC Payback: 2 months [Green]\n"
        "Rule of 40: 78 [Green] NPS: 43"
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 4. DASHBOARD - TAB BY TAB
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("4.  Dashboard  -  Tab by Tab")

    pdf.sub_header("Sidebar Filters  (apply across all three tabs)")
    pdf.body(
        "Three controls govern every chart and metric in the dashboard:\n\n"
        "Plan Tier: All / Starter / Growth / Enterprise\n"
        "Region: All / UK / US / EU / APAC\n"
        "Reporting Period: Date slider Jan 2022 - Dec 2024\n\n"
        "When a segment filter is applied the dashboard re-aggregates all KPIs from "
        "the 1,000 customer records in real time rather than querying a pre-built pivot. "
        "Results are cached per segment combination so the second selection within the "
        "same session is instant. Selecting All / All returns the pre-computed "
        "monthly_kpis.csv for maximum speed."
    )

    pdf.sub_header("Tab 1  -  Executive Summary")
    pdf.body(
        "The single-screen board view. Designed so a founder can hand a laptop to an "
        "investor and have the conversation without any prior explanation. Nine KPI "
        "cards across three rows, each with a RAG-coloured left border and background "
        "tint (green, amber, or red) matching the benchmark comparison."
    )
    tab1 = [
        ("MRR  (Revenue row)",
         "Total monthly recurring revenue across all active customers for the period "
         "end. The primary growth signal. RAG driven by MoM growth rate: Green >=5%, "
         "Amber >=0%, Red declining."),
        ("ARR  (Revenue row)",
         "MRR x 12. The annualised view expected in board packs and investor meetings. "
         "Shares the MRR RAG flag."),
        ("NRR  (Revenue row)",
         "Net Revenue Retention. Above 100% means the existing base grows without new "
         "sales. Best-in-class SaaS targets above 110%. "
         "Green >=110%, Amber 100-110%, Red <100%."),
        ("LTV:CAC  (Unit Economics row)",
         "Lifetime value to acquisition cost ratio. Benchmark >=3x. Below 2x means "
         "the business spends more to acquire customers than it earns back. "
         "Green >=3x, Amber 2-3x, Red <2x."),
        ("CAC Payback  (Unit Economics row)",
         "Months to recover what was spent acquiring a customer. Benchmark <12 months. "
         "Above 18 months is a cash-flow warning. Green <12m, Amber 12-18m, Red >18m."),
        ("Rule of 40  (Unit Economics row)",
         "YoY growth % + estimated profit margin %. A score >=40 means the business "
         "balances growth and efficiency. Below 40 means one lever needs attention. "
         "Green >=40, Amber 20-40, Red <20."),
        ("Churn Rate  (Retention row)",
         "Percentage of customers cancelling each month. SMB SaaS benchmark: <5%. "
         "Best-in-class: <3%. Even a 1% reduction compounds significantly over 12 months. "
         "Green <=3%, Amber 3-5%, Red >5%."),
        ("NPS  (Retention row)",
         "Average Net Promoter Score across active customers. No RAG benchmark applied "
         "- NPS standards vary too much by industry. Early-warning signal for churn risk."),
        ("Active Customers  (Retention row)",
         "Total paying customers at the period end. Volume metric with no RAG flag. "
         "Provides denominator context for all percentage-based metrics above."),
    ]
    for name, desc in tab1:
        pdf.kpi_entry(name, desc)
    pdf.body(
        "Below the nine KPI cards: a Key Insights panel displaying plain-English "
        "commentary generated automatically by the ETL for the latest month in the "
        "selected period. Covers MRR trajectory, NRR health, LTV:CAC position, payback "
        "efficiency, and Rule of 40 score. Updates automatically with every filter change."
    )

    pdf.add_page()
    pdf.sub_header("Tab 2  -  Growth")
    pdf.body(
        "The story of how the business is acquiring customers and building revenue over "
        "time. Three charts, all filter-responsive."
    )
    tab2 = [
        ("MRR Trend  (full-width line chart)",
         "Purple line with gradient area fill showing MRR from Jan 2022 to the period "
         "end. The curve shape tells the growth story at a glance - smooth acceleration, "
         "plateau, or volatility. Apply a segment filter (e.g. Enterprise only, UK only) "
         "to isolate which segment is driving the headline growth figure."),
        ("New Customers per Month  (bar chart)",
         "Monthly bar chart of new signup volume in the selected period. Shows whether "
         "acquisition pace is consistent or lumpy. Spikes and troughs here directly "
         "explain MRR acceleration and deceleration in the trend chart - the two are "
         "intended to be read together."),
        ("MRR Bridge  (waterfall chart)",
         "The most analytically sophisticated chart in the dashboard. Breaks the most "
         "recent month's MRR into its components:\n"
         "  Prior MRR (opening bar)\n"
         "  + New MRR (revenue from customers who signed up this month)\n"
         "  + Expansion MRR (upsell from retained customers)\n"
         "  - Churn (revenue lost to cancellations)\n"
         "  = Current MRR (closing bar)\n\n"
         "Answers the board question: are we growing from acquisition, from expansion, "
         "or are we fighting churn?"),
    ]
    for name, desc in tab2:
        pdf.kpi_entry(name, desc)

    pdf.sub_header("Tab 3  -  Efficiency")
    pdf.body(
        "Unit economics deep-dive. Determines whether growth is sustainable and "
        "capital-efficient. Four charts across two rows."
    )
    tab3 = [
        ("LTV:CAC Ratio Trend  (line + benchmark lines)",
         "Purple line over time with a green dashed benchmark at 3x (minimum healthy) "
         "and an amber dotted line at 2x (minimum viable). Demo data ranges 5x-30x "
         "throughout - well above benchmark. Early volatility reflects a low-churn month "
         "temporarily inflating LTV. Segment filters reveal whether Enterprise customers "
         "genuinely deliver the superior unit economics their pricing implies."),
        ("CAC Payback Period Trend  (line + benchmark lines)",
         "Blue line showing months to recover acquisition cost per new customer cohort. "
         "Green benchmark at 12 months, red maximum at 18 months. Benchmark lines make "
         "healthy vs at-risk periods immediately obvious without the reader needing to "
         "know industry standards."),
        ("Rule of 40 Gauge  (speedometer)",
         "Gauge with three coloured zones: Red (0-20), Amber (20-40), Green (40-200). "
         "Needle points to the most recent period score. Delta text shows distance from "
         "the 40 benchmark (e.g. '+38 above target'). Executives get an instant "
         "pass/fail read without looking at any other chart."),
        ("Monthly Churn Rate Trend  (area chart + benchmark lines)",
         "Red area chart with a green target line at 3% and an amber threshold at 5%. "
         "The area fill makes high-churn months visually impossible to miss. The metric "
         "founders check most anxiously - coloured zones make deteriorating trends "
         "transparent rather than hiding them in a table."),
    ]
    for name, desc in tab3:
        pdf.kpi_entry(name, desc)

    # ══════════════════════════════════════════════════════════════════════════
    # 5. GLOSSARY
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_header("5.  Glossary of Abbreviations")

    glossary = [
        ("Business & Financial Metrics", [
            ("MRR  -  Monthly Recurring Revenue",
             "The total predictable revenue a SaaS business collects from all active "
             "customers in a single month. If 100 customers each pay GBP100/month, "
             "MRR = GBP10,000. The heartbeat metric of every subscription business."),
            ("ARR  -  Annual Recurring Revenue",
             "MRR x 12. The annualised revenue view. Investors and board packs almost "
             "always talk in ARR terms. GBP250k MRR = GBP3M ARR."),
            ("NRR  -  Net Revenue Retention  (also NDR - Net Dollar Retention)",
             "Measures what happens to revenue from existing customers after accounting for "
             "upgrades, downgrades, and cancellations. Formula: (starting MRR + expansion "
             "- churn) / starting MRR. Above 100% means existing customers generate more "
             "revenue this month than last, even without a single new sale. "
             "Best-in-class: >110%."),
            ("LTV  -  Lifetime Value  (also CLV - Customer Lifetime Value)",
             "Total revenue expected from a single customer over their entire relationship. "
             "Formula: ARPU / monthly churn rate. A customer paying GBP200/month with 4% "
             "monthly churn has LTV = GBP5,000."),
            ("CAC  -  Customer Acquisition Cost",
             "Total cost of winning one new customer - sales, marketing, commissions, ads. "
             "If you spend GBP50k/month on sales and marketing and acquire 100 customers, "
             "CAC = GBP500."),
            ("LTV:CAC  -  Lifetime Value to Customer Acquisition Cost Ratio",
             "The most important unit economics metric. Revenue earned per GBP1 spent on "
             "acquisition. LTV:CAC of 3x means every GBP1 in acquisition spend returns "
             "GBP3 in lifetime revenue. Industry benchmark: >=3x healthy, <2x unsustainable."),
            ("NPS  -  Net Promoter Score",
             "Customer satisfaction metric. Customers rate 'How likely are you to "
             "recommend us?' on 0-10. Promoters (9-10) minus Detractors (0-6) = NPS. "
             "Ranges -100 to +100. Above 40 is generally considered excellent for "
             "B2B SaaS."),
            ("ARPU  -  Average Revenue Per User",
             "Total MRR divided by number of active customers. Shows the average monthly "
             "spend per customer. Segmented by plan tier, reveals which customers are "
             "most valuable per seat."),
        ]),
        ("Dashboard & Reporting Terms", [
            ("RAG  -  Red / Amber / Green",
             "Traffic-light status system for benchmarking KPIs at a glance. "
             "Green = above benchmark, Amber = acceptable range but watch closely, "
             "Red = below benchmark requiring action. Each KPI card applies RAG "
             "colouring to its border and background."),
            ("KPI  -  Key Performance Indicator",
             "A measurable value demonstrating how effectively a business achieves its "
             "objectives. Dashboard KPIs: MRR, ARR, NRR, LTV:CAC, CAC Payback, "
             "Rule of 40, Churn Rate, NPS."),
            ("MoM  -  Month on Month",
             "Percentage change between the current month and the prior month. MRR MoM "
             "of +5% means revenue grew 5% compared to last month."),
            ("YoY  -  Year on Year",
             "Percentage change compared to the same month twelve months ago. Used for "
             "the Rule of 40 growth rate to avoid distortion from rapid early-stage "
             "scaling that inflates annualised MoM figures."),
            ("MRR Bridge  -  MRR Waterfall",
             "A waterfall chart decomposing current MRR into: prior MRR + new MRR "
             "+ expansion MRR - churned MRR = current MRR. Shows whether growth "
             "comes from acquisition, expansion, or both."),
            ("Rule of 40",
             "Composite efficiency benchmark: YoY revenue growth % + profit margin %. "
             "A score >=40 is the threshold at which a SaaS business balances growth "
             "and profitability. Used widely by VCs and growth-stage boards."),
        ]),
        ("Technical Abbreviations", [
            ("ETL  -  Extract, Transform, Load",
             "Standard data pipeline pattern. Extract: read raw data (customers.csv). "
             "Transform: compute KPIs, apply benchmarks, generate insights. "
             "Load: write output (monthly_kpis.csv)."),
            ("CSV  -  Comma-Separated Values",
             "Plain text file where each row is a record and columns are separated by "
             "commas. Used for customers.csv (raw) and monthly_kpis.csv (processed)."),
            ("API  -  Application Programming Interface",
             "Protocol for software systems to exchange data. Referenced as the "
             "real-world source this dashboard would replace in a live deployment - "
             "Stripe API for MRR, CRM API for churn events."),
            ("PDF  -  Portable Document Format",
             "The board export format. fpdf2 generates these programmatically with no "
             "browser, no print dialog, and a consistent layout every time."),
            ("venv  -  Virtual Environment",
             "Isolated Python installation scoped to a single project. Prevents package "
             "version conflicts between projects. Activated with "
             ".venv/Scripts/Activate.ps1 on Windows PowerShell."),
            ("PEP 8  -  Python Enhancement Proposal 8",
             "Official Python style guide. Defines indentation (4 spaces), naming "
             "conventions (snake_case), and line length. This project enforces 88-character "
             "line limit using the Black formatter."),
        ]),
        ("Industry & Business Model Terms", [
            ("SaaS  -  Software as a Service",
             "Software delivered over the internet on a subscription basis rather than "
             "installed locally. The business model this dashboard is built around. "
             "Examples: Salesforce, Slack, HubSpot, Notion."),
            ("SMB  -  Small and Medium-sized Business",
             "Companies with roughly 10-500 employees. Used in the churn benchmark "
             "context: <5% monthly churn is the SMB SaaS standard. Enterprise SaaS "
             "typically targets <2% due to annual contracts and higher switching costs."),
            ("B2B  -  Business to Business",
             "Selling products or services to other companies rather than consumers. "
             "The target market for this portfolio - SaaS founders and operators selling "
             "into other businesses."),
            ("CRM  -  Customer Relationship Management",
             "Software used to track customer interactions, sales pipeline stages, and "
             "churn events. In real SaaS companies, churn data lives here. "
             "Examples: Salesforce, HubSpot, Pipedrive."),
        ]),
        ("Certification Abbreviations", [
            ("DP-700  -  Fabric Data Engineer Associate",
             "Microsoft Fabric data engineering certification. Covers pipelines, "
             "lakehouses, and Data Factory orchestration in the Fabric unified platform."),
            ("DP-600  -  Fabric Analytics Engineer Associate",
             "Microsoft Fabric analytics certification. Covers semantic models, Power BI "
             "reports, and DAX within the Fabric ecosystem."),
            ("AZ-305  -  Azure Solutions Architect Expert",
             "Senior-level Azure certification covering end-to-end cloud architecture "
             "design, governance, and infrastructure patterns."),
            ("AZ-400  -  Azure DevOps Engineer Expert",
             "Covers CI/CD pipelines, Azure DevOps, GitHub Actions, and "
             "infrastructure-as-code practices."),
            ("AI-102  -  Azure AI Engineer Associate",
             "Covers Azure Cognitive Services, OpenAI integration, and building "
             "AI-powered applications on Azure."),
            ("DP-100  -  Azure Data Scientist Associate",
             "Covers Azure Machine Learning: model training, MLOps, responsible AI, "
             "and experiment tracking."),
            ("DP-203  -  Azure Data Engineer Associate",
             "Covers Azure data engineering: Synapse Analytics, Data Lake, Data Factory, "
             "streaming with Event Hub and Stream Analytics."),
        ]),
    ]

    for section_title, terms in glossary:
        pdf.sub_header(section_title)
        for name, definition in terms:
            pdf.term(name, definition)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"\nDone. PDF saved to:\n{OUTPUT}\n")


if __name__ == "__main__":
    build()

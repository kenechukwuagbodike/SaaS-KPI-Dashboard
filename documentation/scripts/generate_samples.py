"""
documentation/scripts/generate_samples.py
Generates two PDF files into samples/ for the GitHub portfolio:
  1. board-snapshot-sample.pdf  — one-page board KPI snapshot (December 2024)
  2. saas-kpi-dashboard-case-study.pdf — full project case study

Run from the project root:
    python documentation/scripts/generate_samples.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
from fpdf import FPDF, XPos, YPos

ROOT    = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "samples"
SAMPLES.mkdir(exist_ok=True)

_PURPLE = (124, 58, 237)
_DARK   = (17,  24,  39)
_GREY   = (75,  85,  99)
_WHITE  = (255, 255, 255)
_GREEN  = (22,  163,  74)
_AMBER  = (217, 119,   6)
_RED    = (220,  38,  38)
_RAG_COLOR = {"Green": _GREEN, "Amber": _AMBER, "Red": _RED, "N/A": _GREY}


def _pdf_safe(text: str) -> str:
    return (
        text.replace("—", "-").replace("–", "-")
            .replace("’", "'").replace("‘", "'")
            .replace("“", '"').replace("”", '"')
            .replace("…", "...").replace("●", "*")
            .replace("•", "*")
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1.  BOARD SNAPSHOT SAMPLE
# ══════════════════════════════════════════════════════════════════════════════
def build_board_snapshot():
    df = pd.read_csv(ROOT / "data" / "monthly_kpis.csv", parse_dates=["month"])
    plan, region, period = "All", "All", "December 2024"

    class _PDF(FPDF):
        def header(self):
            self.set_fill_color(*_PURPLE)
            self.rect(0, 0, 210, 26, "F")
            self.set_y(5)
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(*_WHITE)
            self.cell(0, 8, "Executive KPI Dashboard  -  Board Snapshot",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "", 9)
            self.cell(0, 7,
                      f"Period: {period}   |   Plan: {plan}   |   Region: {region}",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(4)

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*_GREY)
            self.cell(0, 8, "Kene Agbodike  |  Data & AI Decision Systems Consultant",
                      align="C")

    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    def _kpi_box(x, y, w, h, label, value, rag):
        color = _RAG_COLOR.get(rag, _GREY)
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.8)
        pdf.rect(x, y, w, h)
        pdf.set_fill_color(*color)
        pdf.rect(x, y, 2.5, h, "F")
        pdf.set_xy(x + 4, y + 3)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_GREY)
        pdf.cell(w - 6, 5, label.upper())
        pdf.set_xy(x + 4, y + 9)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(*_DARK)
        pdf.cell(w - 6, 8, value)
        pdf.set_xy(x + 4, y + 18)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*color)
        pdf.cell(w - 6, 5, f"* {rag}")

    def _sv(col):
        s = df[col].dropna()
        return float(s.iloc[-1]) if not s.empty else np.nan

    def _fmt(col, fmt):
        v = _sv(col)
        return "-" if np.isnan(v) else fmt.format(v)

    def _rag(col):
        s = df[col].dropna()
        return str(s.iloc[-1]) if not s.empty else "N/A"

    BOX_W, BOX_H, GAP = 59, 28, 4
    SX, SY = 10, 32

    rows = [
        [
            ("Monthly Recurring Rev.", _fmt("mrr", "£{:,.0f}"), _rag("rag_mrr_growth")),
            ("Annual Recurring Rev.", _fmt("arr", "£{:,.0f}"), _rag("rag_mrr_growth")),
            ("Net Revenue Retention",
             _fmt("nrr", "{:.1%}") if not np.isnan(_sv("nrr")) else "-",
             _rag("rag_nrr")),
        ],
        [
            ("LTV : CAC Ratio", _fmt("ltv_cac", "{:.1f}x"), _rag("rag_ltv_cac")),
            ("CAC Payback Period", _fmt("cac_payback_months", "{:.0f} months"),
             _rag("rag_cac_payback")),
            ("Rule of 40", _fmt("rule_of_40", "{:.0f}"), _rag("rag_rule_of_40")),
        ],
        [
            ("Monthly Churn Rate",
             f"{_sv('monthly_churn_rate') * 100:.1f}%"
             if not np.isnan(_sv("monthly_churn_rate")) else "-",
             _rag("rag_churn")),
            ("Net Promoter Score", _fmt("avg_nps", "{:.0f}"), "N/A"),
            ("Active Customers",
             f"{int(_sv('n_active_customers')):,}"
             if not np.isnan(_sv("n_active_customers")) else "-", "N/A"),
        ],
    ]

    for ri, row in enumerate(rows):
        for ci, (label, value, rag) in enumerate(row):
            _kpi_box(SX + ci * (BOX_W + GAP), SY + ri * (BOX_H + GAP),
                     BOX_W, BOX_H, label, value, rag)

    insight_y = SY + 3 * (BOX_H + GAP) + 4
    pdf.set_xy(10, insight_y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_PURPLE)
    pdf.cell(0, 6, "Key Insights", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    insight_text = _pdf_safe(str(df["insights"].dropna().iloc[-1]))
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*_DARK)
    for bullet in insight_text.split(" | "):
        if bullet.strip():
            pdf.set_x(10)
            pdf.multi_cell(0, 5, f"  *  {bullet.strip()}")

    # Watermark label
    pdf.set_y(-30)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*_GREY)
    pdf.cell(0, 5, "Sample output generated from synthetic demo data  |  "
             "Live dashboard: Streamlit Community Cloud", align="C")

    out = SAMPLES / "board-snapshot-sample.pdf"
    pdf.output(str(out))
    print(f"  [1/2] Board snapshot  ->  {out}")


# ══════════════════════════════════════════════════════════════════════════════
# 2.  CASE STUDY PDF
# ══════════════════════════════════════════════════════════════════════════════
def build_case_study():
    class Doc(FPDF):
        def header(self):
            if self.page_no() == 1:
                return
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*_GREY)
            self.cell(0, 8, "Executive KPI Dashboard  |  Case Study",
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
            self.set_text_color(*_GREY)
            self.cell(0, 8,
                      "Kene Agbodike  |  Data & AI Decision Systems Consultant",
                      align="C")

        def cover(self):
            self.add_page()
            self.set_fill_color(*_PURPLE)
            self.rect(0, 0, 210, 90, "F")
            self.set_y(22)
            self.set_font("Helvetica", "B", 22)
            self.set_text_color(*_WHITE)
            self.cell(0, 12, "Executive KPI Dashboard",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "", 13)
            self.cell(0, 8, "Case Study & KPI Reference Guide",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "I", 10)
            self.cell(0, 7, "How a board-ready SaaS dashboard turns raw data into decisions",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_y(100)
            self.set_text_color(*_DARK)
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, "Kene Agbodike",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*_GREY)
            self.cell(0, 6, "Data & AI Decision Systems Consultant",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.cell(0, 6, "github.com/kenechukwuagbodike",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(10)
            self.set_draw_color(*_PURPLE)
            self.set_line_width(0.5)
            self.line(30, self.get_y(), 180, self.get_y())
            self.ln(8)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*_DARK)
            self.cell(0, 7, "Contents",
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)
            for item in [
                "1.  The Business Problem",
                "2.  What the Dashboard Does",
                "3.  The Metrics Story  -  What Each KPI Means",
                "4.  How the Dashboard Supports Decisions",
                "5.  Technical Architecture",
                "6.  December 2024 Results Snapshot",
            ]:
                self.set_font("Helvetica", "", 10)
                self.set_text_color(*_GREY)
                self.cell(0, 7, item,
                          align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        def section(self, title):
            self.ln(4)
            self.set_fill_color(*_PURPLE)
            self.set_text_color(*_WHITE)
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 9, f"  {title}",
                      fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)
            self.set_text_color(*_DARK)

        def sub(self, title):
            self.ln(2)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*_PURPLE)
            self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(*_PURPLE)
            self.line(10, self.get_y(), 100, self.get_y())
            self.ln(3)
            self.set_text_color(*_DARK)

        def body(self, text):
            self.set_x(self.l_margin)
            self.set_font("Helvetica", "", 9.5)
            self.set_text_color(*_GREY)
            self.multi_cell(0, 5.5, text)
            self.ln(2)

        def kpi(self, name, full, bench, desc):
            self.set_x(self.l_margin)
            self.set_font("Helvetica", "B", 9.5)
            self.set_text_color(*_DARK)
            self.cell(0, 6, f"{name}  -  {full}",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(*_PURPLE)
            self.set_x(self.l_margin)
            self.cell(0, 5, f"Benchmark: {bench}",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*_GREY)
            self.set_x(self.l_margin)
            self.multi_cell(0, 5, desc)
            self.ln(3)

    pdf = Doc()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.cover()

    # ── Section 1 ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("1.  The Business Problem")
    pdf.body(
        "Software as a Service (SaaS) founders and product leaders face a common "
        "operational challenge: their most important business metrics live in "
        "completely different places. Monthly Recurring Revenue (MRR) is in Stripe. "
        "Customer churn data is in a Customer Relationship Management (CRM) system. "
        "Customer Acquisition Cost (CAC) is in a marketing spreadsheet. Lifetime "
        "Value (LTV) is calculated by different people using different assumptions "
        "and rarely agrees between departments."
    )
    pdf.body(
        "When a founder needs to prepare for a board meeting or investor conversation, "
        "pulling these numbers together takes days. By the time the presentation is "
        "ready, some figures are already out of date. Benchmark comparisons against "
        "industry standards have to be done manually."
    )
    pdf.body(
        "This dashboard solves that problem. It aggregates all of these signals into "
        "a single, board-ready view that updates in real time and generates a one-page "
        "KPI snapshot in one click."
    )

    pdf.section("2.  What the Dashboard Does")
    pdf.body(
        "The Executive KPI Dashboard is a three-tab interactive application that "
        "gives SaaS founders, executives, and investors a complete picture of "
        "business health without any manual data assembly."
    )
    pdf.sub("Tab 1 - Executive Summary")
    pdf.body(
        "Nine Key Performance Indicator (KPI) cards arranged in three rows: Revenue, "
        "Unit Economics, and Retention. Each card shows the current value, a "
        "month-on-month (MoM) delta, and a Red/Amber/Green (RAG) benchmark status "
        "with colour-coded borders. Green = above industry benchmark. Amber = "
        "acceptable but requires monitoring. Red = below benchmark and requires action."
        "\n\nA plain-English insights panel below the cards explains what the numbers "
        "mean in business terms - automatically generated from the data. A one-click "
        "board PDF export button generates a formatted snapshot for investor meetings."
    )
    pdf.sub("Tab 2 - Growth")
    pdf.body(
        "Three charts that tell the acquisition and revenue story: an MRR trend area "
        "chart, a new customers bar chart, and an MRR bridge waterfall chart. The "
        "waterfall is the most analytically powerful - it breaks current MRR into "
        "Prior MRR + New MRR + Expansion MRR - Churned MRR = Current MRR, answering "
        "the board question: are we growing from new sales, from existing customers "
        "expanding, or are we fighting churn?"
    )
    pdf.sub("Tab 3 - Efficiency")
    pdf.body(
        "Four charts focused on unit economics: LTV to CAC (LTV:CAC) ratio trend with "
        "benchmark lines, CAC payback period trend with threshold lines, a Rule of 40 "
        "gauge (speedometer style with Red/Amber/Green zones), and a monthly churn "
        "rate area chart with target and threshold benchmark lines."
    )
    pdf.sub("Segment Filtering")
    pdf.body(
        "All three tabs respond to sidebar filters for plan tier (Starter / Growth / "
        "Enterprise) and region (UK / US / EU / Asia-Pacific). Selecting a segment "
        "re-aggregates all KPIs from the underlying customer-level data in real time. "
        "This means a founder can instantly answer 'what is our LTV:CAC for Enterprise "
        "customers in the US?' without any manual data manipulation."
    )

    # ── Section 3 ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("3.  The Metrics Story  -  What Each KPI Means")

    pdf.sub("Revenue Metrics")
    pdf.kpi("MRR", "Monthly Recurring Revenue",
            "Growing >5% month-on-month",
            "The heartbeat metric of any subscription business. MRR is the total "
            "predictable revenue collected from all active customers in a single month. "
            "It excludes one-off payments and only counts recurring subscription fees. "
            "If MRR is growing consistently, the business is healthy. If it plateaus or "
            "declines, it is a signal that acquisition is not keeping pace with churn.")
    pdf.kpi("ARR", "Annual Recurring Revenue",
            "Consistent growth trajectory",
            "MRR multiplied by 12. ARR is the annualised view of the revenue base and "
            "is the number that investors, acquirers, and boards use to size a SaaS "
            "business. A business with GBP250k MRR has an ARR of GBP3M.")
    pdf.kpi("NRR", "Net Revenue Retention",
            ">=110% best-in-class, >=100% acceptable, <100% at risk",
            "NRR measures what happens to revenue from existing customers over time. "
            "Formula: (starting MRR + expansion MRR - churned MRR) / starting MRR. "
            "An NRR above 100% means the existing customer base is growing the business "
            "on its own, even without a single new sale. Best-in-class SaaS companies "
            "(like Snowflake and Datadog) sustain NRR above 130%. An NRR below 100% "
            "means churn is outpacing expansion - the business has a leaky bucket problem.")

    pdf.sub("Unit Economics Metrics")
    pdf.kpi("LTV:CAC", "Lifetime Value to Customer Acquisition Cost Ratio",
            ">=3x healthy, 2-3x monitor, <2x unsustainable",
            "The most important unit economics metric. LTV is the total revenue a "
            "business can expect from one customer across their entire relationship "
            "(calculated as Average Revenue Per User (ARPU) / monthly churn rate). "
            "CAC is what it cost to acquire that customer. An LTV:CAC of 3x means "
            "every GBP1 spent on acquisition returns GBP3 in lifetime revenue. Below 2x, "
            "the business is spending more than it earns back - acquisition is "
            "destroying value.")
    pdf.kpi("CAC Payback", "Customer Acquisition Cost Payback Period",
            "<12 months Green, 12-18 months Amber, >18 months Red",
            "The number of months required to recover the cost of acquiring a customer "
            "from that customer's revenue. A CAC payback above 18 months is a cash-flow "
            "warning: the business is funding a long gap between acquisition spend and "
            "return. Venture-backed SaaS companies typically target under 12 months. "
            "Enterprise SaaS can accept longer payback periods due to contract length.")
    pdf.kpi("Rule of 40", "Growth Rate + Profit Margin Score",
            ">=40 Green, 20-40 Amber, <20 Red",
            "A composite benchmark widely used by venture capitalists and growth-stage "
            "boards. The score is: year-on-year MRR growth percentage + estimated profit "
            "margin percentage. A score of 40 or above means the business is balancing "
            "growth and profitability well. Below 40 means one of the two levers needs "
            "attention. This dashboard uses year-on-year growth (not annualised "
            "month-on-month) to prevent inflated scores during early rapid growth.")

    pdf.sub("Retention Metrics")
    pdf.kpi("Churn Rate", "Monthly Customer Churn Rate",
            "<=3% best-in-class, <=5% acceptable (Small and Medium Business SaaS)",
            "The percentage of paying customers who cancelled their subscription in a "
            "given month. Monthly churn of 5% compounds to roughly 46% annual churn - "
            "meaning the business must replace nearly half its customer base every year "
            "just to stay flat. Even a 1% improvement in monthly churn has a dramatic "
            "compounding effect on revenue over 12-24 months.")
    pdf.kpi("NPS", "Net Promoter Score",
            "No universal benchmark (varies by industry)",
            "Customers are asked: 'How likely are you to recommend us?' on a 0-10 scale. "
            "Promoters (9-10) minus Detractors (0-6) = NPS. Ranges from -100 to +100. "
            "NPS is tracked as an early warning signal for future churn - customers "
            "who are unlikely to recommend are more likely to cancel. The dashboard "
            "displays NPS without a RAG benchmark because standards vary too much "
            "between industries to set a universal threshold.")
    pdf.kpi("Active Customers", "Total Active Paying Customers",
            "Consistent growth month-on-month",
            "The total number of customers with an active subscription at period end. "
            "This is the denominator behind every percentage metric on the dashboard. "
            "A rising active customer count combined with a rising churn rate is a "
            "warning sign: new acquisition is masking retention problems that will "
            "compound later.")

    # ── Section 4 ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("4.  How the Dashboard Supports Decisions")

    pdf.sub("Board and investor preparation")
    pdf.body(
        "The Executive Summary tab (Tab 1) is designed so a founder can open the "
        "laptop in a meeting and have the conversation immediately. All nine KPIs are "
        "visible on one screen. RAG colours communicate status without the audience "
        "needing to know the benchmarks. The board PDF export produces a one-page "
        "snapshot that can be sent in advance of the meeting with no manual formatting."
    )
    pdf.sub("Diagnosing growth quality")
    pdf.body(
        "The MRR bridge chart (Tab 2) answers the question investors ask most: 'Where "
        "is the growth coming from?' If most of the bridge is New MRR, growth is "
        "acquisition-dependent and will slow if sales hiring slows. If Expansion MRR "
        "is a large proportion, the business has strong product-market fit and a "
        "natural growth engine in its existing base. If Churn MRR is large relative "
        "to New MRR, the business has a retention problem that acquisition cannot "
        "permanently hide."
    )
    pdf.sub("Identifying unit economics problems early")
    pdf.body(
        "The Efficiency tab (Tab 3) surfaces deteriorating unit economics before they "
        "appear in MRR. A rising CAC payback period combined with a flat or declining "
        "LTV:CAC ratio is a leading indicator that acquisition efficiency is dropping - "
        "possibly due to rising Customer Acquisition Cost as easy channels saturate, "
        "or due to lower-quality customer cohorts with higher churn. Catching this at "
        "month 6 is far less costly than discovering it at month 18."
    )
    pdf.sub("Segment-level decisions")
    pdf.body(
        "Applying a segment filter (e.g. Enterprise plan, US region) allows a founder "
        "to verify strategic assumptions. If the Enterprise segment shows LTV:CAC of "
        "15x versus 3x for Starter, the data supports a decision to shift sales focus "
        "upmarket. If UK churn is 2% while APAC churn is 8%, the data surfaces a "
        "regional customer success problem that needs investigation."
    )

    # ── Section 5 ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("5.  Technical Architecture")

    pdf.sub("Data pipeline")
    pdf.body(
        "The pipeline follows the Extract, Transform, Load (ETL) pattern:\n\n"
        "Extract: pipeline/generate_data.py creates 1,000 synthetic customer records "
        "(data/customers.csv). Each row represents one customer with signup month, "
        "plan tier, region, Average Revenue Per User (ARPU), CAC, churn month, Net "
        "Promoter Score (NPS), and expansion rate.\n\n"
        "Transform: pipeline/etl.py loops through each of the 36 calendar months, "
        "identifies active/new/churned customers, calculates all KPIs, applies RAG "
        "benchmark flags, and generates plain-English insight text.\n\n"
        "Load: outputs data/monthly_kpis.csv - 36 rows, 24 columns."
    )
    pdf.sub("Segment filtering architecture")
    pdf.body(
        "When a segment filter is applied in the dashboard, the "
        "build_segment_kpis(plan, region) function re-aggregates all 36 months of "
        "KPIs from the 1,000 customer records directly. This means the segment data "
        "is always consistent with the customer-level source rather than relying on "
        "pre-built pivot tables. Streamlit's @st.cache_data decorator caches results "
        "per segment combination, so the second selection within a session is instant."
    )
    pdf.sub("Stack")
    pdf.body(
        "Python 3.12  |  pandas 2.2+  |  Streamlit 1.35+  |  Plotly 5.22+  |  "
        "fpdf2 2.7+  |  NumPy 1.26+"
    )

    # ── Section 6 ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("6.  December 2024 Results Snapshot  (demo data)")

    pdf.body(
        "The demo dataset covers 36 months (January 2022 to December 2024) across "
        "1,000 synthetic customers distributed across three plan tiers "
        "(Starter 50%, Growth 35%, Enterprise 15%) and four regions "
        "(UK 30%, US 35%, EU 25%, APAC 10%)."
    )

    snapshot = [
        ("MRR", "Monthly Recurring Revenue", "GBP250,143", "Amber",
         "MoM growth of 0.8% - stable but below the >5% high-growth benchmark."),
        ("ARR", "Annual Recurring Revenue", "GBP3,001,722", "Amber",
         "Crosses the GBP3M ARR milestone in December 2024."),
        ("NRR", "Net Revenue Retention", "102.8%", "Amber",
         "Revenue is retained from existing customers but expansion is below "
         "the best-in-class 110% threshold."),
        ("LTV:CAC", "Lifetime Value to CAC Ratio", "11.1x", "Green",
         "Well above the 3x benchmark - healthy unit economics throughout "
         "the dataset."),
        ("CAC Payback", "Payback Period", "2 months", "Green",
         "Exceptionally fast payback - acquisition spend recovers in 2 months."),
        ("Rule of 40", "Growth + Margin Score", "78", "Green",
         "Strong score. Benchmark is 40. Indicates good balance of growth "
         "and efficiency."),
        ("Churn Rate", "Monthly Customer Churn", "4.1%", "Amber",
         "Above the 3% best-in-class benchmark but within the 5% acceptable "
         "threshold. Worth monitoring."),
        ("NPS", "Net Promoter Score", "43", "N/A",
         "Score of 43 indicates satisfied customers. No RAG benchmark applied."),
        ("Active Customers", "Paying Customers", "470", "N/A",
         "Grown from 34 in January 2022 to 470 in December 2024."),
    ]

    for kpi_abbr, kpi_full, value, rag, comment in snapshot:
        color = _RAG_COLOR.get(rag, _GREY)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*_DARK)
        pdf.cell(0, 6, f"{kpi_abbr}  ({kpi_full})  -  {value}  [{rag}]",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*_GREY)
        pdf.multi_cell(0, 5, comment)
        pdf.ln(2)

    out = SAMPLES / "saas-kpi-dashboard-case-study.pdf"
    pdf.output(str(out))
    print(f"  [2/2] Case study      ->  {out}")


if __name__ == "__main__":
    print("Generating sample PDFs...")
    build_board_snapshot()
    build_case_study()
    print("Done.")

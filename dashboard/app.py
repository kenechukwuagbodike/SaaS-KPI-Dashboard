"""
dashboard/app.py
Executive KPI Dashboard — 3-tab Streamlit app.
Run: streamlit run dashboard/app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF, XPos, YPos

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Executive KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parents[1]


# ── Data loaders (cached) ─────────────────────────────────────────────────────
@st.cache_data
def load_kpis() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "monthly_kpis.csv", parse_dates=["month"])


@st.cache_data
def load_customers() -> pd.DataFrame:
    return pd.read_csv(
        ROOT / "data" / "customers.csv",
        parse_dates=["signup_month", "churn_month"],
    )


@st.cache_data
def build_segment_kpis(plan: str, region: str) -> pd.DataFrame:
    """Re-aggregate monthly KPIs from customer-level data for a given segment."""
    if plan == "All" and region == "All":
        return load_kpis()

    df = load_customers()
    if plan != "All":
        df = df[df["plan_tier"] == plan]
    if region != "All":
        df = df[df["region"] == region]
    if df.empty:
        return pd.DataFrame()

    all_months = pd.date_range("2022-01-01", "2024-12-01", freq="MS")
    rows, prev_mrr = [], None

    for month in all_months:
        active   = df[(df["signup_month"] <= month) & (df["is_active"] | (df["churn_month"] > month))]
        new_c    = df[df["signup_month"] == month]
        churned  = df[df["churn_month"] == month]
        prev_m   = month - pd.DateOffset(months=1)
        prev_act = df[(df["signup_month"] <= prev_m) & (df["is_active"] | (df["churn_month"] > prev_m))] \
                   if month > all_months[0] else pd.DataFrame()

        n_act, n_prev = len(active), len(prev_act)
        mrr = active["arpu"].sum()

        if not prev_act.empty:
            kept    = set(active["customer_id"]) & set(prev_act["customer_id"])
            ret     = active[active["customer_id"].isin(kept)]
            exp_mrr = (ret["arpu"] * ret["expansion_rate"]).sum()
        else:
            exp_mrr = 0.0

        churn_mrr      = churned["arpu"].sum()
        nrr            = (prev_mrr + exp_mrr - churn_mrr) / prev_mrr if prev_mrr else np.nan
        churn_rate     = len(churned) / n_prev if n_prev else np.nan
        ltv_cac        = (active["arpu"].mean() / churn_rate / active["cac"].mean()
                          if n_act and pd.notna(churn_rate) and churn_rate > 0 else np.nan)
        cac_payback    = (new_c["cac"].mean() / new_c["arpu"].mean()
                          if len(new_c) and new_c["arpu"].mean() > 0 else np.nan)
        mrr_growth_mom = (mrr - prev_mrr) / prev_mrr if prev_mrr else np.nan

        rows.append({
            "month":               month,
            "n_active_customers":  n_act,
            "n_new_customers":     len(new_c),
            "n_churned_customers": len(churned),
            "mrr":                 round(mrr, 2),
            "arr":                 round(mrr * 12, 2),
            "new_mrr":             round(new_c["arpu"].sum(), 2),
            "expansion_mrr":       round(exp_mrr, 2),
            "churned_mrr":         round(churn_mrr, 2),
            "nrr":                 round(nrr, 4) if pd.notna(nrr) else np.nan,
            "monthly_churn_rate":  round(churn_rate, 4) if pd.notna(churn_rate) else np.nan,
            "ltv_cac":             round(ltv_cac, 2) if pd.notna(ltv_cac) else np.nan,
            "cac_payback_months":  round(cac_payback, 1) if pd.notna(cac_payback) else np.nan,
            "mrr_growth_mom":      round(mrr_growth_mom, 4) if pd.notna(mrr_growth_mom) else np.nan,
            "avg_nps":             round(active["nps"].mean(), 1) if n_act else np.nan,
        })
        prev_mrr = mrr

    out = pd.DataFrame(rows)

    out["mrr_yoy_growth_pct"] = (
        (out["mrr"] - out["mrr"].shift(12)) / out["mrr"].shift(12) * 100
    ).round(2)
    est_margin = (out["ltv_cac"] - 1).mul(12).clip(-20, 50).fillna(20.0)
    out["rule_of_40"] = (out["mrr_yoy_growth_pct"] + est_margin).clip(upper=200).round(1)

    def _rag(v, g, a, hib=True):
        if pd.isna(v):
            return "N/A"
        return "Green" if (v >= g if hib else v <= g) else ("Amber" if (v >= a if hib else v <= a) else "Red")

    out["rag_churn"]       = out["monthly_churn_rate"].apply(lambda x: _rag(x, 0.03, 0.05, False))
    out["rag_ltv_cac"]     = out["ltv_cac"].apply(lambda x: _rag(x, 3.0, 2.0))
    out["rag_cac_payback"] = out["cac_payback_months"].apply(lambda x: _rag(x, 12, 18, False))
    out["rag_nrr"]         = out["nrr"].apply(lambda x: _rag(x * 100 if pd.notna(x) else np.nan, 110, 100))
    out["rag_rule_of_40"]  = out["rule_of_40"].apply(lambda x: _rag(x, 40, 20))
    out["rag_mrr_growth"]  = out["mrr_growth_mom"].apply(lambda x: _rag(x * 100 if pd.notna(x) else np.nan, 5, 0))

    def _insight(row):
        parts = []
        if pd.notna(row.get("mrr_growth_mom")):
            g = row["mrr_growth_mom"] * 100
            parts.append(f"MRR {'grew' if g >= 0 else 'declined'} {abs(g):.1f}% MoM"
                         + (" — strong top-line momentum." if g > 5 else " — stable but below high-growth benchmark (>5%)." if g >= 0 else " — requires immediate attention."))
        if pd.notna(row.get("nrr")):
            n = row["nrr"] * 100
            parts.append(f"NRR {n:.0f}% — " + ("grows from existing customers alone." if n > 110 else "revenue retained, but expansion below best-in-class (>110%)." if n >= 100 else "churn outpacing expansion; at-risk revenue base."))
        if pd.notna(row.get("ltv_cac")):
            r = row["ltv_cac"]
            parts.append(f"LTV:CAC {r:.1f}x — " + ("above the 3x benchmark; healthy unit economics." if r >= 3 else "approaching benchmark; monitor CAC trend." if r >= 2 else "below 2x; acquisition cost eroding returns."))
        if pd.notna(row.get("rule_of_40")):
            s = row["rule_of_40"]
            parts.append(f"Rule of 40: {s:.0f} — " + ("passes benchmark." if s >= 40 else "below 40; growth or margins need improvement." if s >= 20 else "significant underperformance."))
        return " | ".join(parts)

    out["insights"] = out.apply(_insight, axis=1)
    return out


customers = load_customers()


# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Dashboard Filters")
    st.divider()

    plan_options   = ["All"] + sorted(customers["plan_tier"].unique().tolist())
    region_options = ["All"] + sorted(customers["region"].unique().tolist())

    selected_plan   = st.selectbox("Plan tier",  plan_options)
    selected_region = st.selectbox("Region",     region_options)

    st.divider()
    min_dt = pd.Timestamp("2022-01-01").to_pydatetime()
    max_dt = pd.Timestamp("2024-12-01").to_pydatetime()
    date_range = st.slider(
        "Reporting period",
        min_value=min_dt,
        max_value=max_dt,
        value=(min_dt, max_dt),
        format="MMM YYYY",
    )

# ── Resolve KPIs for selected segment (cached per plan/region combo) ──────────
kpis = build_segment_kpis(selected_plan, selected_region)

# ── Apply date filter ─────────────────────────────────────────────────────────
mask   = (kpis["month"] >= date_range[0]) & (kpis["month"] <= date_range[1])
kpis_f = kpis[mask].copy()


# ── RAG colour maps ───────────────────────────────────────────────────────────
RAG_BORDER = {"Green": "#16a34a", "Amber": "#d97706", "Red": "#dc2626", "N/A": "#9ca3af"}
RAG_BG     = {"Green": "#f0fdf4", "Amber": "#fffbeb", "Red": "#fef2f2", "N/A": "#f9fafb"}
RAG_TEXT   = {"Green": "#15803d", "Amber": "#b45309", "Red": "#b91c1c", "N/A": "#6b7280"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def latest(col: str):
    s = kpis_f[col].dropna()
    return s.iloc[-1] if not s.empty else np.nan


def mom_delta_str(col: str) -> str:
    s = kpis_f[col].dropna()
    if len(s) < 2:
        return "—"
    chg = s.iloc[-1] - s.iloc[-2]
    pct = (chg / abs(s.iloc[-2])) * 100 if s.iloc[-2] != 0 else 0
    arrow = "▲" if chg >= 0 else "▼"
    return f"{arrow} {abs(pct):.1f}% MoM"


def kpi_card(col, label: str, value: str, delta: str, rag: str) -> None:
    border = RAG_BORDER.get(rag, "#9ca3af")
    bg     = RAG_BG.get(rag, "#f9fafb")
    txt    = RAG_TEXT.get(rag, "#6b7280")
    rag_label = rag if rag != "N/A" else "No data"
    col.markdown(
        f"""
        <div style="
            background:{bg};
            border-left:5px solid {border};
            border-radius:8px;
            padding:18px 20px;
            min-height:130px;
        ">
            <p style="margin:0;font-size:11px;color:#6b7280;font-weight:700;
                      text-transform:uppercase;letter-spacing:.06em;">{label}</p>
            <p style="margin:6px 0 0;font-size:28px;font-weight:800;
                      color:#111827;line-height:1;">{value}</p>
            <p style="margin:6px 0 0;font-size:12px;color:{txt};font-weight:600;">
                ● {rag_label} &nbsp;&nbsp;{delta}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Board PDF generator ───────────────────────────────────────────────────────
_PURPLE = (124, 58, 237)
_DARK   = (17,  24,  39)
_GREY   = (75,  85,  99)
_WHITE  = (255, 255, 255)
_GREEN  = (22,  163,  74)
_AMBER  = (217, 119,   6)
_RED    = (220,  38,  38)

_RAG_COLOR = {"Green": _GREEN, "Amber": _AMBER, "Red": _RED, "N/A": _GREY}


def _pdf_safe(text: str) -> str:
    """Replace characters outside Latin-1 so fpdf2 built-in fonts don't choke."""
    return (
        text.replace("—", "-")   # em dash
            .replace("–", "-")   # en dash
            .replace("’", "'")   # right single quote
            .replace("‘", "'")   # left single quote
            .replace("“", '"')   # left double quote
            .replace("”", '"')   # right double quote
            .replace("…", "...")  # ellipsis
    )


def generate_board_pdf(
    data: pd.DataFrame,
    plan: str,
    region: str,
    period_label: str,
) -> bytes:
    """Return a board-ready KPI snapshot as a PDF byte string."""

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
                      f"Period: {period_label}   |   Plan: {plan}   |   Region: {region}",
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

    def _kpi_box(x: float, y: float, w: float, h: float,
                 label: str, value: str, rag: str) -> None:
        color = _RAG_COLOR.get(rag, _GREY)
        # border
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.8)
        pdf.rect(x, y, w, h)
        # left accent bar
        pdf.set_fill_color(*color)
        pdf.rect(x, y, 2.5, h, "F")
        # label
        pdf.set_xy(x + 4, y + 3)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*_GREY)
        pdf.cell(w - 6, 5, label.upper())
        # value
        pdf.set_xy(x + 4, y + 9)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(*_DARK)
        pdf.cell(w - 6, 8, value)
        # RAG badge
        pdf.set_xy(x + 4, y + 18)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*color)
        pdf.cell(w - 6, 5, f"* {rag}")

    def _safe_val(col: str) -> float:
        s = data[col].dropna()
        return float(s.iloc[-1]) if not s.empty else np.nan

    def _fmt(col: str, fmt: str) -> str:
        v = _safe_val(col)
        if np.isnan(v):
            return "-"
        return fmt.format(v)

    def _rag_val(col: str) -> str:
        s = data[col].dropna()
        return str(s.iloc[-1]) if not s.empty else "N/A"

    # ── KPI grid (3 rows × 3 cols) ────────────────────────────────────────────
    BOX_W, BOX_H, GAP = 59, 28, 4
    START_X, START_Y = 10, 32

    rows = [
        [
            ("Monthly Recurring Rev.", _fmt("mrr", "£{:,.0f}"), _rag_val("rag_mrr_growth")),
            ("Annual Recurring Rev.", _fmt("arr", "£{:,.0f}"), _rag_val("rag_mrr_growth")),
            ("Net Revenue Retention", _fmt("nrr", "{:.1%}") if not np.isnan(_safe_val("nrr")) else "-",
             _rag_val("rag_nrr")),
        ],
        [
            ("LTV : CAC Ratio", _fmt("ltv_cac", "{:.1f}x"), _rag_val("rag_ltv_cac")),
            ("CAC Payback Period", (_fmt("cac_payback_months", "{:.0f} months")),
             _rag_val("rag_cac_payback")),
            ("Rule of 40", _fmt("rule_of_40", "{:.0f}"), _rag_val("rag_rule_of_40")),
        ],
        [
            ("Monthly Churn Rate",
             (f"{_safe_val('monthly_churn_rate') * 100:.1f}%"
              if not np.isnan(_safe_val("monthly_churn_rate")) else "-"),
             _rag_val("rag_churn")),
            ("Net Promoter Score", _fmt("avg_nps", "{:.0f}"), "N/A"),
            ("Active Customers",
             (f"{int(_safe_val('n_active_customers')):,}"
              if not np.isnan(_safe_val("n_active_customers")) else "-"), "N/A"),
        ],
    ]

    for ri, row in enumerate(rows):
        for ci, (label, value, rag) in enumerate(row):
            bx = START_X + ci * (BOX_W + GAP)
            by = START_Y + ri * (BOX_H + GAP)
            _kpi_box(bx, by, BOX_W, BOX_H, label, value, rag)

    # ── Insights ──────────────────────────────────────────────────────────────
    insight_y = START_Y + 3 * (BOX_H + GAP) + 4
    pdf.set_xy(10, insight_y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_PURPLE)
    pdf.cell(0, 6, "Key Insights", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    insight_col = data["insights"].dropna() if "insights" in data.columns else pd.Series()
    insight_text = _pdf_safe(str(insight_col.iloc[-1])) if not insight_col.empty else ""

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*_DARK)
    for bullet in insight_text.split(" | "):
        if bullet.strip():
            pdf.set_x(10)
            pdf.multi_cell(0, 5, f"  *  {bullet.strip()}")

    return bytes(pdf.output())


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["📋  Executive Summary", "📈  Growth", "⚙️  Efficiency"]
)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — EXECUTIVE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    # Header
    reporting_month = kpis_f["month"].max().strftime("%B %Y") if not kpis_f.empty else "—"
    st.markdown("## Executive KPI Summary")
    st.caption(
        f"Period ending **{reporting_month}** &nbsp;·&nbsp; "
        f"Plan: **{selected_plan}** &nbsp;·&nbsp; Region: **{selected_region}**"
    )
    st.divider()

    # ── Row 1: Revenue ────────────────────────────────────────────────────────
    st.markdown("#### 💰 Revenue")
    c1, c2, c3 = st.columns(3)

    mrr_val = latest("mrr")
    arr_val = latest("arr")
    nrr_val = latest("nrr")

    kpi_card(c1, "Monthly Recurring Revenue",
             f"£{mrr_val:,.0f}" if pd.notna(mrr_val) else "—",
             mom_delta_str("mrr"), latest("rag_mrr_growth"))

    kpi_card(c2, "Annual Recurring Revenue",
             f"£{arr_val:,.0f}" if pd.notna(arr_val) else "—",
             mom_delta_str("arr"), latest("rag_mrr_growth"))

    kpi_card(c3, "Net Revenue Retention",
             f"{nrr_val * 100:.1f}%" if pd.notna(nrr_val) else "—",
             mom_delta_str("nrr"), latest("rag_nrr"))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Unit economics ─────────────────────────────────────────────────
    st.markdown("#### 📐 Unit Economics")
    c4, c5, c6 = st.columns(3)

    ltv_cac_val = latest("ltv_cac")
    payback_val = latest("cac_payback_months")
    r40_val     = latest("rule_of_40")

    kpi_card(c4, "LTV : CAC Ratio",
             f"{ltv_cac_val:.1f}x" if pd.notna(ltv_cac_val) else "—",
             mom_delta_str("ltv_cac"), latest("rag_ltv_cac"))

    kpi_card(c5, "CAC Payback Period",
             f"{payback_val:.0f} months" if pd.notna(payback_val) else "—",
             mom_delta_str("cac_payback_months"), latest("rag_cac_payback"))

    kpi_card(c6, "Rule of 40",
             f"{r40_val:.0f}" if pd.notna(r40_val) else "—",
             mom_delta_str("rule_of_40"), latest("rag_rule_of_40"))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Retention ──────────────────────────────────────────────────────
    st.markdown("#### 🔁 Retention")
    c7, c8, c9 = st.columns(3)

    churn_val = latest("monthly_churn_rate")
    nps_val   = latest("avg_nps")

    kpi_card(c7, "Monthly Churn Rate",
             f"{churn_val * 100:.1f}%" if pd.notna(churn_val) else "—",
             mom_delta_str("monthly_churn_rate"), latest("rag_churn"))

    kpi_card(c8, "Net Promoter Score",
             f"{nps_val:.0f}" if pd.notna(nps_val) else "—",
             mom_delta_str("avg_nps"), "N/A")

    kpi_card(c9, "Active Customers",
             f"{int(latest('n_active_customers')):,}" if pd.notna(latest('n_active_customers')) else "—",
             mom_delta_str("n_active_customers"), "N/A")

    st.divider()

    # ── Insights panel ────────────────────────────────────────────────────────
    st.markdown("#### 💡 Key Insights")
    insight_text = latest("insights")
    if pd.notna(insight_text) and str(insight_text).strip():
        for bullet in str(insight_text).split(" | "):
            st.markdown(f"- {bullet}")
    else:
        st.info("No insights available for the selected period.")

    st.divider()

    # ── PDF export ────────────────────────────────────────────────────────────
    st.markdown("#### 📄 Board Export")
    if not kpis_f.empty:
        pdf_bytes = generate_board_pdf(
            kpis_f, selected_plan, selected_region, reporting_month
        )
        fname = f"kpi-board-{reporting_month.replace(' ', '-')}.pdf"
        st.download_button(
            "⬇  Download Board PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
        )
    else:
        st.button("Download Board PDF", disabled=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — GROWTH
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    reporting_month2 = kpis_f["month"].max().strftime("%B %Y") if not kpis_f.empty else "—"
    st.markdown("## Growth")
    st.caption(
        f"Period ending **{reporting_month2}** &nbsp;·&nbsp; "
        f"Plan: **{selected_plan}** &nbsp;·&nbsp; Region: **{selected_region}**"
    )
    st.divider()

    # ── MRR Trend (full width) ────────────────────────────────────────────────
    st.markdown("#### 📈 MRR Trend")

    fig_mrr = go.Figure()
    fig_mrr.add_trace(go.Scatter(
        x=kpis_f["month"],
        y=kpis_f["mrr"],
        mode="lines+markers",
        name="MRR",
        line=dict(color="#7c3aed", width=2.5),
        marker=dict(size=4, color="#7c3aed"),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.08)",
        hovertemplate="<b>%{x|%b %Y}</b><br>MRR: £%{y:,.0f}<extra></extra>",
    ))
    fig_mrr.update_layout(
        yaxis_tickprefix="£",
        yaxis_tickformat=",.0f",
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        showlegend=False,
    )
    fig_mrr.update_xaxes(showgrid=False, tickformat="%b %Y")
    fig_mrr.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
    st.plotly_chart(fig_mrr, width="stretch")

    # ── New customers bar + MRR bridge waterfall ──────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 👥 New Customers per Month")
        fig_new = go.Figure(go.Bar(
            x=kpis_f["month"],
            y=kpis_f["n_new_customers"],
            marker_color="#7c3aed",
            hovertemplate="<b>%{x|%b %Y}</b><br>New customers: %{y}<extra></extra>",
        ))
        fig_new.update_layout(
            yaxis_title="Customers",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            height=340,
            showlegend=False,
        )
        fig_new.update_xaxes(showgrid=False, tickformat="%b %Y")
        fig_new.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
        st.plotly_chart(fig_new, width="stretch")

    with col_r:
        # Latest month MRR bridge
        wf_row = kpis_f.dropna(subset=["new_mrr", "expansion_mrr", "churned_mrr"])
        if not wf_row.empty:
            latest_wf   = wf_row.iloc[-1]
            prev_months = kpis_f[kpis_f["month"] < latest_wf["month"]].dropna(subset=["mrr"])
            prev_mrr    = prev_months.iloc[-1]["mrr"] if not prev_months.empty else 0.0
            wf_month    = latest_wf["month"].strftime("%B %Y")

            st.markdown(f"#### 🌊 MRR Bridge — {wf_month}")
            fig_wf = go.Figure(go.Waterfall(
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "total"],
                x=["Prior MRR", "New", "Expansion", "Churn", "Current MRR"],
                y=[
                    prev_mrr,
                    latest_wf["new_mrr"],
                    latest_wf["expansion_mrr"],
                    -latest_wf["churned_mrr"],
                    None,
                ],
                text=[
                    f"£{prev_mrr:,.0f}",
                    f"+£{latest_wf['new_mrr']:,.0f}",
                    f"+£{latest_wf['expansion_mrr']:,.0f}",
                    f"-£{latest_wf['churned_mrr']:,.0f}",
                    f"£{latest_wf['mrr']:,.0f}",
                ],
                textposition="outside",
                connector=dict(line=dict(color="#d1d5db", width=1, dash="dot")),
                increasing=dict(marker_color="#16a34a"),
                decreasing=dict(marker_color="#dc2626"),
                totals=dict(marker_color="#7c3aed"),
                hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>",
            ))
            fig_wf.update_layout(
                yaxis_tickprefix="£",
                yaxis_tickformat=",.0f",
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=0, r=0, t=10, b=0),
                height=340,
                showlegend=False,
            )
            fig_wf.update_xaxes(showgrid=False)
            fig_wf.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
            st.plotly_chart(fig_wf, width="stretch")
        else:
            st.info("Insufficient data for MRR bridge.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — EFFICIENCY
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    reporting_month3 = kpis_f["month"].max().strftime("%B %Y") if not kpis_f.empty else "—"
    st.markdown("## Efficiency")
    st.caption(
        f"Period ending **{reporting_month3}** &nbsp;·&nbsp; "
        f"Plan: **{selected_plan}** &nbsp;·&nbsp; Region: **{selected_region}**"
    )
    st.divider()

    # ── Row 1: LTV:CAC trend + CAC Payback trend ──────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📊 LTV:CAC Ratio Trend")
        ltv_data = kpis_f.dropna(subset=["ltv_cac"])
        fig_ltv = go.Figure()
        fig_ltv.add_trace(go.Scatter(
            x=ltv_data["month"],
            y=ltv_data["ltv_cac"],
            mode="lines+markers",
            line=dict(color="#7c3aed", width=2.5),
            marker=dict(size=5, color="#7c3aed"),
            hovertemplate="<b>%{x|%b %Y}</b><br>LTV:CAC: %{y:.1f}x<extra></extra>",
        ))
        fig_ltv.add_hline(
            y=3, line_dash="dash", line_color="#16a34a", line_width=1.5,
            annotation_text="3x benchmark", annotation_position="bottom right",
            annotation_font_color="#16a34a",
        )
        fig_ltv.add_hline(
            y=2, line_dash="dot", line_color="#d97706", line_width=1.5,
            annotation_text="2x min", annotation_position="bottom right",
            annotation_font_color="#d97706",
        )
        fig_ltv.update_layout(
            yaxis_title="LTV:CAC (x)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            showlegend=False,
        )
        fig_ltv.update_xaxes(showgrid=False, tickformat="%b %Y")
        fig_ltv.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
        st.plotly_chart(fig_ltv, width="stretch")

    with col_b:
        st.markdown("#### ⏱️ CAC Payback Period Trend")
        payback_data = kpis_f.dropna(subset=["cac_payback_months"])
        fig_payback = go.Figure()
        fig_payback.add_trace(go.Scatter(
            x=payback_data["month"],
            y=payback_data["cac_payback_months"],
            mode="lines+markers",
            line=dict(color="#0ea5e9", width=2.5),
            marker=dict(size=5, color="#0ea5e9"),
            hovertemplate="<b>%{x|%b %Y}</b><br>Payback: %{y:.1f} months<extra></extra>",
        ))
        fig_payback.add_hline(
            y=12, line_dash="dash", line_color="#16a34a", line_width=1.5,
            annotation_text="12m benchmark", annotation_position="top right",
            annotation_font_color="#16a34a",
        )
        fig_payback.add_hline(
            y=18, line_dash="dot", line_color="#dc2626", line_width=1.5,
            annotation_text="18m max", annotation_position="top right",
            annotation_font_color="#dc2626",
        )
        fig_payback.update_layout(
            yaxis_title="Months",
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            showlegend=False,
        )
        fig_payback.update_xaxes(showgrid=False, tickformat="%b %Y")
        fig_payback.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
        st.plotly_chart(fig_payback, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Rule of 40 gauge + churn trend ────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("#### 🎯 Rule of 40")
        r40 = latest("rule_of_40")
        r40_display = float(r40) if pd.notna(r40) else 0.0
        r40_color = "#16a34a" if r40_display >= 40 else ("#d97706" if r40_display >= 20 else "#dc2626")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=r40_display,
            delta={"reference": 40, "valueformat": ".0f",
                   "increasing": {"color": "#16a34a"}, "decreasing": {"color": "#dc2626"}},
            number={"font": {"size": 52, "color": r40_color}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 200], "tickwidth": 1, "tickcolor": "#d1d5db"},
                "bar":  {"color": r40_color, "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,   20],  "color": "#fef2f2"},
                    {"range": [20,  40],  "color": "#fffbeb"},
                    {"range": [40, 200],  "color": "#f0fdf4"},
                ],
                "threshold": {
                    "line": {"color": "#6b7280", "width": 3},
                    "thickness": 0.75,
                    "value": 40,
                },
            },
            title={"text": f"Latest: {reporting_month3}<br><span style='font-size:13px;color:#6b7280'>Benchmark ≥ 40</span>"},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=10),
            height=320,
        )
        st.plotly_chart(fig_gauge, width="stretch")

    with col_d:
        st.markdown("#### 📉 Monthly Churn Rate Trend")
        churn_data = kpis_f.dropna(subset=["monthly_churn_rate"])
        fig_churn = go.Figure()
        fig_churn.add_trace(go.Scatter(
            x=churn_data["month"],
            y=churn_data["monthly_churn_rate"] * 100,
            mode="lines+markers",
            line=dict(color="#dc2626", width=2.5),
            marker=dict(size=5, color="#dc2626"),
            fill="tozeroy",
            fillcolor="rgba(220,38,38,0.06)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Churn: %{y:.1f}%<extra></extra>",
        ))
        fig_churn.add_hline(
            y=3, line_dash="dash", line_color="#16a34a", line_width=1.5,
            annotation_text="3% target", annotation_position="top right",
            annotation_font_color="#16a34a",
        )
        fig_churn.add_hline(
            y=5, line_dash="dot", line_color="#d97706", line_width=1.5,
            annotation_text="5% threshold", annotation_position="top right",
            annotation_font_color="#d97706",
        )
        fig_churn.update_layout(
            yaxis_title="Churn rate (%)",
            yaxis_ticksuffix="%",
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            showlegend=False,
        )
        fig_churn.update_xaxes(showgrid=False, tickformat="%b %Y")
        fig_churn.update_yaxes(showgrid=True, gridcolor="#f3f4f6")
        st.plotly_chart(fig_churn, width="stretch")
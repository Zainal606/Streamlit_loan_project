import streamlit as st
import pyodbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date as dt_date, timedelta
import math

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Loan Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #080b10;
    color: #c9d1d9;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 3rem 3rem; max-width: 1400px; }

/* ── Page background grain ── */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
}

/* ── Title ── */
.app-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 300;
    letter-spacing: 0.06em;
    color: #e8dcc8;
    margin-bottom: 0.1rem;
    line-height: 1;
}
.app-subtitle {
    font-size: 0.68rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #5a6478;
    margin-bottom: 2.5rem;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1420 0%, #0c1118 100%);
    border: 1px solid #1a2235;
    border-radius: 2px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #c9a96e 0%, #8b6914 100%);
}
div[data-testid="metric-container"] label {
    font-size: 0.6rem !important;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #5a6478 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem !important;
    font-weight: 300 !important;
    color: #e8dcc8 !important;
    letter-spacing: 0.02em;
}

/* ── Section headings ── */
.section-label {
    font-size: 0.6rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #5a6478;
    border-bottom: 1px solid #1a2235;
    padding-bottom: 0.5rem;
    margin: 2rem 0 1.2rem 0;
}

/* ── Divider ── */
hr { border-color: #1a2235 !important; margin: 2rem 0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #060911 !important;
    border-right: 1px solid #1a2235;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem; }

.sidebar-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 300;
    color: #e8dcc8;
    letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
}
.sidebar-sub {
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #5a6478;
    margin-bottom: 2rem;
}

/* ── Form inputs ── */
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: #0c1118 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 2px !important;
    color: #c9d1d9 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stDateInput"] input:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 1px #c9a96e22 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c9a96e 0%, #8b6914 100%) !important;
    color: #080b10 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.4rem !important;
    width: 100% !important;
    font-weight: 400 !important;
    transition: opacity 0.2s ease !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.82 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1a2235 !important;
    border-radius: 2px;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    border-left-width: 3px !important;
    font-size: 0.8rem !important;
}

/* ── Labels ── */
[data-testid="stWidgetLabel"] {
    font-size: 0.6rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #5a6478 !important;
}

/* ── Plotly chart containers ── */
.js-plotly-plot { border: 1px solid #1a2235; border-radius: 2px; }

/* ── Info stat row ── */
.stat-row {
    display: flex; gap: 1rem;
    font-size: 0.72rem;
    color: #5a6478;
    margin-top: 0.8rem;
}
.stat-row span { color: #c9a96e; margin-left: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── DB CONNECTION ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=basic-zain-loan.database.windows.net;"
        "DATABASE=free-sql-db-7340985;"
        "UID=loanuser;"
        "PWD=StrongPassword123!;"
    )

conn = get_connection()
cursor = conn.cursor()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Loan Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Personal Finance · Real-time Amortization</div>', unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
df = pd.read_sql("SELECT * FROM LoanSummary", conn)
payments_df = pd.read_sql("SELECT * FROM Payments ORDER BY payment_date", conn)

balance        = round(df['current_balance'][0], 2)
total_paid     = round(df['total_paid'][0], 2)
total_interest = round(df['total_interest'][0], 2)
principal_paid = round(total_paid - total_interest, 2)

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Outstanding Balance", f"AED {balance:,.2f}")
k2.metric("Total Paid", f"AED {total_paid:,.2f}")
k3.metric("Principal Repaid", f"AED {principal_paid:,.2f}")
k4.metric("Interest Accrued", f"AED {total_interest:,.2f}")

# ── CHARTS ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Analytics</div>', unsafe_allow_html=True)

GOLD   = "#c9a96e"
SLATE  = "#3d4f6b"
BG     = "#080b10"
CARD   = "#0c1118"
GRID   = "#1a2235"
TEXT   = "#c9d1d9"
MUTED  = "#5a6478"

chart_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=TEXT, size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    title_font=dict(family="Cormorant Garamond, serif", size=17, color="#e8dcc8"),
)

c1, c2, c3 = st.columns(3)

# ── Donut ──
with c1:
    fig_donut = go.Figure(go.Pie(
        labels=["Principal Repaid", "Interest Paid"],
        values=[principal_paid, total_interest],
        hole=0.72,
        marker=dict(colors=[GOLD, SLATE], line=dict(color=BG, width=3)),
        textinfo="none",
        hovertemplate="%{label}<br>AED %{value:,.2f}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{round(principal_paid/(total_paid or 1)*100, 1)}%</b><br>principal",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=TEXT, family="DM Mono, monospace"),
        align="center",
    )
    fig_donut.update_layout(**chart_layout, title="Payment Composition",
                            showlegend=True,
                            legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center",
                                        font=dict(size=10, color=MUTED)))
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Payment bars ──
with c2:
    fig_bar = go.Figure(go.Bar(
        x=payments_df['payment_date'],
        y=payments_df['amount'],
        marker=dict(
            color=payments_df['amount'],
            colorscale=[[0, SLATE], [1, GOLD]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>AED %{y:,.2f}<extra></extra>",
    ))
    fig_bar.update_layout(
        **chart_layout,
        title="Payment History",
        xaxis=dict(gridcolor=GRID, tickfont=dict(size=9), showgrid=False),
        yaxis=dict(gridcolor=GRID, tickfont=dict(size=9)),
        bargap=0.35,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Cumulative area ──
with c3:
    payments_df['cumulative'] = payments_df['amount'].cumsum()
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=payments_df['payment_date'],
        y=payments_df['cumulative'],
        fill='tozeroy',
        fillcolor=f"rgba(201,169,110,0.08)",
        line=dict(color=GOLD, width=2),
        mode='lines',
        hovertemplate="<b>%{x}</b><br>Cumulative: AED %{y:,.2f}<extra></extra>",
    ))
    fig_area.add_trace(go.Scatter(
        x=payments_df['payment_date'],
        y=payments_df['cumulative'],
        mode='markers',
        marker=dict(color=GOLD, size=5, line=dict(color=BG, width=1.5)),
        showlegend=False,
        hoverinfo='skip',
    ))
    fig_area.update_layout(
        **chart_layout,
        title="Cumulative Repayment",
        xaxis=dict(gridcolor=GRID, tickfont=dict(size=9), showgrid=False),
        yaxis=dict(gridcolor=GRID, tickfont=dict(size=9)),
    )
    st.plotly_chart(fig_area, use_container_width=True)

# ── PAYMENT TABLE ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Transaction Ledger</div>', unsafe_allow_html=True)

display_df = payments_df[['payment_date', 'amount']].copy()
display_df.columns = ['Date', 'Amount (AED)']
display_df['Amount (AED)'] = display_df['Amount (AED)'].apply(lambda x: f"{x:,.2f}")
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── FORECAST ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Payoff Forecast</div>', unsafe_allow_html=True)

def build_forecast(start_balance, annual_rate, monthly_payment, start_date):
    rate_daily = annual_rate / 365
    rows = []
    bal = start_balance
    current = start_date
    for _ in range(360):
        if bal <= 0:
            break
        interest = bal * rate_daily * 30
        principal = max(0.0, monthly_payment - interest)
        bal = max(0.0, bal - principal)
        current = current + timedelta(days=30)
        rows.append({"date": current, "balance": round(bal, 2),
                     "interest": round(interest, 2), "principal": round(principal, 2)})
        if bal == 0:
            break
    return pd.DataFrame(rows)

avg_payment = payments_df['amount'].mean() if len(payments_df) > 0 else 1000.0
fc1, fc2 = st.columns([3, 1])

with fc2:
    st.markdown("<br>", unsafe_allow_html=True)
    monthly_input = st.number_input(
        "Monthly Payment (AED)",
        min_value=100.0,
        max_value=float(balance) if balance > 100 else 100000.0,
        value=round(avg_payment, 0),
        step=100.0,
        format="%.0f",
    )
    min_payment = balance * (0.115 / 365) * 30
    if monthly_input <= min_payment:
        st.warning(f"Minimum to reduce balance: AED {min_payment:,.0f}")

with fc1:
    forecast_df = build_forecast(balance, 0.115, monthly_input, dt_date.today())
    paid_off = (not forecast_df.empty) and (forecast_df['balance'].iloc[-1] == 0)

    if not paid_off:
        st.error("Payment too low to clear the loan within 30 years.")
    else:
        payoff_date = forecast_df['date'].iloc[-1]
        months_left = len(forecast_df)
        total_future_interest = forecast_df['interest'].sum()
        forecast_df['cum_interest'] = forecast_df['interest'].cumsum()

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=forecast_df['date'], y=forecast_df['balance'],
            name="Remaining Balance",
            line=dict(color=GOLD, width=2.5),
            fill='tozeroy', fillcolor="rgba(201,169,110,0.06)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Balance: AED %{y:,.0f}<extra></extra>",
        ))
        fig_fc.add_trace(go.Scatter(
            x=forecast_df['date'], y=forecast_df['cum_interest'],
            name="Cumulative Interest",
            line=dict(color=SLATE, width=1.5, dash='dot'),
            hovertemplate="<b>%{x|%b %Y}</b><br>Interest: AED %{y:,.0f}<extra></extra>",
        ))
        fig_fc.add_vline(
            x=payoff_date.strftime("%Y-%m-%d"),
            line_width=1, line_dash="dash", line_color="#c9a96e44",
        )
        fig_fc.add_annotation(
            x=payoff_date.strftime("%Y-%m-%d"), y=balance * 0.85,
            text=f"  Payoff  {payoff_date.strftime('%b %Y')}",
            showarrow=False,
            font=dict(size=10, color=GOLD, family="DM Mono, monospace"),
        )
        fig_fc.update_layout(
            **chart_layout,
            title="Projected Balance to Zero",
            xaxis=dict(gridcolor=GRID, tickfont=dict(size=9), showgrid=False),
            yaxis=dict(gridcolor=GRID, tickfont=dict(size=9), tickprefix="AED "),
            legend=dict(orientation="h", y=-0.12, x=0, font=dict(size=10, color=MUTED)),
            height=340,
        )
        st.plotly_chart(fig_fc, use_container_width=True)

if not forecast_df.empty and forecast_df['balance'].iloc[-1] == 0:
    years, months = divmod(months_left, 12)
    fk1, fk2, fk3, fk4 = st.columns(4)
    fk1.metric("Payoff Date",     payoff_date.strftime("%b %Y"))
    fk2.metric("Time Remaining",  f"{years}y {months}m")
    fk3.metric("Future Interest", f"AED {total_future_interest:,.0f}")
    fk4.metric("Total Cost",      f"AED {balance + total_future_interest:,.0f}")

    with st.expander("View full amortization schedule"):
        sched = forecast_df[['date','balance','interest','principal']].copy()
        sched.columns = ['Date','Remaining Balance','Interest','Principal']
        sched['Date']              = sched['Date'].apply(lambda d: d.strftime("%b %Y"))
        sched['Remaining Balance'] = sched['Remaining Balance'].apply(lambda x: f"AED {x:,.2f}")
        sched['Interest']          = sched['Interest'].apply(lambda x: f"AED {x:,.2f}")
        sched['Principal']         = sched['Principal'].apply(lambda x: f"AED {x:,.2f}")
        st.dataframe(sched, use_container_width=True, hide_index=True)

# ── SIDEBAR PAYMENT FORM ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">New Payment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Record a repayment</div>', unsafe_allow_html=True)

    amount = st.number_input("Amount (AED)", min_value=0.0, step=100.0, format="%.2f")
    date   = st.date_input("Payment Date")

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("Record Payment")

    if submit:
        cursor.execute(
            "SELECT current_balance, last_payment_date, total_interest, total_paid "
            "FROM LoanSummary WHERE id=1"
        )
        row = cursor.fetchone()
        bal, last_date, t_interest, t_paid = float(row[0]), row[1], float(row[2]), float(row[3])

        today = dt_date.today()

        if date > today:
            st.error("Date cannot be in the future.")
            st.stop()
        if date <= last_date:
            st.error("Date must be after last payment date.")
            st.stop()

        days         = (date - last_date).days
        rate         = 0.115 / 365
        interest_amt = bal * rate * days
        principal_p  = max(0.0, amount - interest_amt)
        new_balance  = bal - principal_p

        if interest_amt > amount:
            st.warning("Payment is less than accrued interest — loan balance will increase.")

        cursor.execute("INSERT INTO Payments (payment_date, amount) VALUES (?, ?)", date, amount)
        cursor.execute("""
            UPDATE LoanSummary
            SET current_balance=?, total_paid=?, total_interest=?, last_payment_date=?
            WHERE id=1
        """, new_balance, t_paid + amount, t_interest + interest_amt, date)
        conn.commit()

        st.success("Payment recorded successfully.")

        # Detail breakdown
        st.markdown(f"""
        <div style='margin-top:1rem;padding:1rem;background:#0c1118;border:1px solid #1a2235;border-radius:2px;font-size:0.75rem;line-height:2;'>
            <div style='color:#5a6478;letter-spacing:.15em;font-size:.6rem;text-transform:uppercase;margin-bottom:.5rem;'>Breakdown</div>
            Days elapsed <span style='float:right;color:#c9a96e'>{days}</span><br>
            Interest charged <span style='float:right;color:#c9a96e'>AED {interest_amt:,.2f}</span><br>
            Principal paid <span style='float:right;color:#c9a96e'>AED {principal_p:,.2f}</span><br>
            New balance <span style='float:right;color:#e8dcc8'>AED {new_balance:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)

        st.rerun()

    # ── Rate info ──
    st.markdown("<br><hr style='border-color:#1a2235;margin:1.5rem 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:#5a6478;margin-bottom:.8rem;'>Loan Parameters</div>
    <div style='font-size:.75rem;line-height:2.2;color:#5a6478;'>
        Interest Rate <span style='float:right;color:#c9a96e'>11.5% p.a.</span><br>
        Calculation <span style='float:right;color:#c9d1d9'>Daily</span><br>
        Method <span style='float:right;color:#c9d1d9'>Reducing Balance</span>
    </div>
    """, unsafe_allow_html=True)

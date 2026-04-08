import streamlit as st
import pyodbc
import pandas as pd
import plotly.graph_objects as go
from datetime import date as dt_date, timedelta
from sqlalchemy import create_engine
import urllib

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Loan Tracker", layout="wide", initial_sidebar_state="expanded")

# ── THEME ──────────────────────────────────────────────────────────────────────
GOLD  = "#c9a96e"
SLATE = "#3d4f6b"
BG    = "#080b10"
GRID  = "#1a2235"
TEXT  = "#c9d1d9"
MUTED = "#5a6478"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; background-color: #080b10; color: #c9d1d9; font-size: 15px; }
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { padding: 2.5rem 3rem 3rem 3rem; max-width: 1400px; }
body::before {
    content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
}

/* ── Header ── */
.app-title { font-family:'Cormorant Garamond',serif; font-size:3.2rem; font-weight:300; letter-spacing:.06em; color:#e8dcc8; margin-bottom:.2rem; line-height:1; }
.app-sub   { font-size:.85rem; letter-spacing:.2em; text-transform:uppercase; color:#5a6478; margin-bottom:2.5rem; }
.section-label { font-size:.75rem; letter-spacing:.22em; text-transform:uppercase; color:#8a9ab0; border-bottom:1px solid #1a2235; padding-bottom:.6rem; margin:2.2rem 0 1.4rem 0; font-weight:400; }

/* ── Metric cards ── */
div[data-testid="metric-container"] { background:linear-gradient(135deg,#0f1420,#0c1118); border:1px solid #1a2235; border-radius:4px; padding:1.5rem 1.8rem; position:relative; overflow:hidden; }
div[data-testid="metric-container"]::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:linear-gradient(180deg,#c9a96e,#8b6914); }
div[data-testid="metric-container"] label { font-size:.78rem!important; letter-spacing:.15em; text-transform:uppercase; color:#8a9ab0!important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family:'Cormorant Garamond',serif; font-size:2.6rem!important; font-weight:300!important; color:#e8dcc8!important; letter-spacing:.02em; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background:#060911!important; border-right:1px solid #1a2235; }
[data-testid="stSidebar"] .block-container { padding:2rem 1.6rem; }
.sidebar-title { font-family:'Cormorant Garamond',serif; font-size:1.7rem; font-weight:300; color:#e8dcc8; letter-spacing:.08em; margin-bottom:.25rem; }
.sidebar-sub   { font-size:.78rem; letter-spacing:.18em; text-transform:uppercase; color:#5a6478; margin-bottom:2rem; }

/* ── Inputs ── */
[data-testid="stNumberInput"] input, [data-testid="stDateInput"] input { background:#0c1118!important; border:1px solid #1a2235!important; border-radius:2px!important; color:#c9d1d9!important; font-family:'DM Mono',monospace!important; font-size:1rem!important; padding:.5rem .75rem!important; }
[data-testid="stNumberInput"] input:focus, [data-testid="stDateInput"] input:focus { border-color:#c9a96e!important; box-shadow:0 0 0 1px #c9a96e22!important; }

/* ── Button ── */
[data-testid="stButton"]>button { background:linear-gradient(135deg,#c9a96e,#8b6914)!important; color:#080b10!important; border:none!important; border-radius:2px!important; font-family:'DM Mono',monospace!important; font-size:.85rem!important; letter-spacing:.18em!important; text-transform:uppercase!important; padding:.75rem 1.4rem!important; width:100%!important; transition:opacity .2s ease!important; font-weight:400!important; }
[data-testid="stButton"]>button:hover { opacity:.82!important; }

[data-testid="stDataFrame"] { border:1px solid #1a2235!important; border-radius:4px; font-size:.95rem!important; }
[data-testid="stAlert"] { border-radius:4px!important; border-left-width:3px!important; font-size:.95rem!important; }
[data-testid="stWidgetLabel"] { font-size:.78rem!important; letter-spacing:.15em!important; text-transform:uppercase!important; color:#8a9ab0!important; }
.js-plotly-plot { border:1px solid #1a2235; border-radius:4px; }
hr { border-color:#1a2235!important; margin:2rem 0; }

/* ── Top strip ── */
.top-strip { display:grid; grid-template-columns:repeat(4,1fr); border:1px solid #1a2235; border-radius:6px; overflow:hidden; margin-bottom:2rem; }
.strip-item { padding:1.4rem 1.8rem; border-right:1px solid #1a2235; }
.strip-item:last-child { border-right:none; }
.strip-label { font-size:.78rem; letter-spacing:.15em; text-transform:uppercase; color:#8a9ab0; margin-bottom:.4rem; }
.strip-value { font-family:'Cormorant Garamond',serif; font-size:2.2rem; font-weight:300; color:#e8dcc8; line-height:1.1; }
.strip-value.hi { color:#c9a96e; }
.strip-sub { font-size:.82rem; color:#5a6478; margin-top:.3rem; }

/* ── Panel ── */
.panel { background:#0c1118; border:1px solid #1a2235; border-radius:6px; padding:1.6rem 1.8rem; margin-bottom:1.2rem; }
.panel-title { font-size:.78rem; letter-spacing:.18em; text-transform:uppercase; color:#8a9ab0; margin-bottom:1.4rem; }

/* ── Progress ── */
.prog-wrap { margin-bottom:1.3rem; }
.prog-label { display:flex; justify-content:space-between; font-size:.9rem; color:#8a9ab0; margin-bottom:.45rem; }
.prog-label span { color:#e8dcc8; font-size:.9rem; }
.prog-track { background:#1a2235; border-radius:3px; height:14px; overflow:hidden; }
.prog-fill  { height:100%; border-radius:3px; display:flex; align-items:center; padding-left:.6rem; font-size:.72rem; color:#080b10; letter-spacing:.08em; font-weight:400; }

/* ── Intel cards ── */
.intel-card { background:#0c1118; border:1px solid #1a2235; border-radius:6px; padding:1.2rem 1.5rem; margin-bottom:.9rem; }
.intel-card.good { border-left:4px solid #2ecc71; }
.intel-card.warn { border-left:4px solid #f39c12; }
.intel-card.bad  { border-left:4px solid #e74c3c; }
.intel-card.info { border-left:4px solid #3b82f6; }
.intel-title { font-size:1rem; color:#e8dcc8; margin-bottom:.4rem; font-weight:400; }
.intel-body  { font-size:.88rem; color:#8a9ab0; line-height:1.7; }

/* ── Scenario cards ── */
.sc-card  { background:#0c1118; border:1px solid #1a2235; border-radius:6px; padding:1.3rem 1.5rem; margin-bottom:.9rem; }
.sc-badge { display:inline-block; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; padding:.25rem .9rem; border-radius:20px; margin-bottom:.65rem; }
.bg-green { background:#2ecc7122; color:#2ecc71; border:1px solid #2ecc7144; }
.bg-amber { background:#f39c1222; color:#f39c12; border:1px solid #f39c1244; }
.bg-blue  { background:#3b82f622; color:#3b82f6; border:1px solid #3b82f644; }
.sc-title { font-size:1.05rem; color:#e8dcc8; margin-bottom:.4rem; font-weight:400; }
.sc-body  { font-size:.88rem; color:#8a9ab0; line-height:1.7; }

/* ── Stat grid ── */
.stat-grid { display:grid; grid-template-columns:1fr 1fr; }
.stat-item { display:flex; justify-content:space-between; align-items:center; padding:.8rem 1.6rem; border-bottom:1px solid #1a2235; font-size:.9rem; gap:1rem; }
.sk { color:#8a9ab0; }
.sv { color:#e8dcc8; text-align:right; }
.sv.gold { color:#c9a96e; }
            
/* ── Mobile Responsiveness ── */
@media (max-width: 768px) {
    /* Stack the top strip metrics vertically on phones */
    .top-strip { 
        grid-template-columns: 1fr; 
    }
    .strip-item { 
        border-right: none; 
        border-bottom: 1px solid #1a2235; 
    }
    /* Reduce giant paddings on mobile */
    .block-container { 
        padding: 1rem !important; 
    }
    /* Stack the key stats grid */
    .stat-grid { 
        grid-template-columns: 1fr; 
    }
}
</style>
""", unsafe_allow_html=True)

# ── DB ─────────────────────────────────────────────────────────────────────────


# ── DB ─────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    # 1. Safely pull the password out first
    password = st.secrets["DB_PASSWORD"]
    
    # 2. URL-encode the string and use an f-string (notice the 'f' before UID)
    params = urllib.parse.quote_plus(
        "DRIVER={ODBC Driver 18 for SQL Server};"  
        "SERVER=basic-zain-loan.database.windows.net;"
        "DATABASE=free-sql-db-7340985;"
        f"UID=loanuser;PWD={password};" 
        "Encrypt=yes;TrustServerCertificate=yes;" 
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

engine = get_engine()

# Keep your raw connection for your sidebar INSERT/UPDATE commands
conn = engine.raw_connection()
cursor = conn.cursor()

# ── DATA ───────────────────────────────────────────────────────────────────────
# Pass the engine to pandas to fix the terminal warnings
df          = pd.read_sql("SELECT * FROM LoanSummary", engine)
payments_df = pd.read_sql("SELECT * FROM Payments ORDER BY payment_date", engine)

balance        = round(float(df['current_balance'][0]), 2)
total_paid     = round(float(df['total_paid'][0]), 2)
total_interest = round(float(df['total_interest'][0]), 2)
principal_paid = round(total_paid - total_interest, 2)
last_pay_date  = df['last_payment_date'][0]
loan_start_dt  = pd.to_datetime(payments_df['payment_date'].iloc[0]).date() if len(payments_df) else pd.to_datetime(last_pay_date).date()

today         = dt_date.today()
n_payments    = len(payments_df)
avg_payment   = payments_df['amount'].mean() if n_payments else 0
largest_pay   = payments_df['amount'].max()  if n_payments else 0
smallest_pay  = payments_df['amount'].min()  if n_payments else 0
months_elapsed = max(1, round((today - loan_start_dt).days / 30))

annual_rate   = 0.115
daily_rate    = annual_rate / 365
original_principal = round(principal_paid + balance, 2)
pct_cleared   = round(principal_paid / original_principal * 100, 1) if original_principal > 0 else 0
est_tenure    = round(months_elapsed / (pct_cleared / 100)) if pct_cleared > 0 else 60
time_pct      = round(months_elapsed / est_tenure * 100, 1) if est_tenure > 0 else 0
interest_pct  = round(total_interest / total_paid * 100, 1) if total_paid > 0 else 0
cost_per_lakh = round(100000 * daily_rate, 0)
principal_pct = round(principal_paid / total_paid * 100, 1) if total_paid else 0

def fmt(n):
    if n >= 100000: return f"₹{n/100000:.2f}L"
    return f"₹{n:,.0f}"

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Loan Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Personal Finance · Real-time Amortization Intelligence</div>', unsafe_allow_html=True)

# ── TOP STRIP ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-strip">
  <div class="strip-item"><div class="strip-label">Loan Amount</div><div class="strip-value">{fmt(original_principal)}</div><div class="strip-sub">{loan_start_dt.strftime('%b %Y')}</div></div>
  <div class="strip-item"><div class="strip-label">Total Paid So Far</div><div class="strip-value">{fmt(total_paid)}</div><div class="strip-sub">{n_payments} payments</div></div>
  <div class="strip-item"><div class="strip-label">Outstanding Balance</div><div class="strip-value hi">{fmt(balance)}</div><div class="strip-sub">as of {today.strftime('%b %Y')}</div></div>
  <div class="strip-item"><div class="strip-label">Interest Paid So Far</div><div class="strip-value hi">{fmt(total_interest)}</div><div class="strip-sub">{interest_pct}% of paid amount</div></div>
</div>
""", unsafe_allow_html=True)

# ── LOAN PROGRESS ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Loan Progress</div>', unsafe_allow_html=True)

ahead      = pct_cleared > time_pct
pace_color = "#2ecc71" if ahead else "#e74c3c"
pace_label = "ahead of pace ↑" if ahead else "behind pace ↓"

st.markdown(f"""
<div class="panel">
  <div class="panel-title">Repayment Progress</div>
  <div class="prog-wrap">
    <div class="prog-label"><span>Principal Repaid</span><span>₹{principal_paid:,.0f} of ₹{original_principal:,.0f} ({pct_cleared}%)</span></div>
    <div class="prog-track"><div class="prog-fill" style="width:{pct_cleared}%;background:linear-gradient(90deg,#c9a96e,#8b6914);">{pct_cleared}%</div></div>
  </div>
  <div class="prog-wrap">
    <div class="prog-label"><span>Time Elapsed</span><span>{months_elapsed} months of ~{est_tenure} months est.</span></div>
    <div class="prog-track"><div class="prog-fill" style="width:{min(time_pct,100)}%;background:linear-gradient(90deg,#3b82f6,#1d4ed8);">{time_pct}%</div></div>
  </div>
  <div style="font-size:.95rem;color:{pace_color};margin-top:.7rem;">
    You've repaid {pct_cleared}% of principal in {time_pct}% of estimated tenure — <b>{pace_label}</b>
  </div>
</div>
""", unsafe_allow_html=True)

# ── BREAKDOWN OF EVERY RUPEE ───────────────────────────────────────────────────
st.markdown(f"""
<div class="panel">
  <div class="panel-title">Breakdown of Every Rupee Paid</div>
  <div class="prog-wrap">
    <div class="prog-label"><span>Principal</span><span>{fmt(principal_paid)} ({principal_pct}%)</span></div>
    <div class="prog-track"><div class="prog-fill" style="width:{principal_pct}%;background:linear-gradient(90deg,#2ecc71,#16a34a);">{principal_pct}%</div></div>
  </div>
  <div class="prog-wrap">
    <div class="prog-label"><span>Interest</span><span>{fmt(total_interest)} ({interest_pct}%)</span></div>
    <div class="prog-track"><div class="prog-fill" style="width:{interest_pct}%;background:linear-gradient(90deg,#e74c3c,#b91c1c);">{interest_pct}%</div></div>
  </div>
  <div style="font-size:.92rem;color:#8a9ab0;margin-top:.5rem;">
    Total outflow so far: {fmt(total_paid)}. Interest cost is {'relatively low' if interest_pct < 25 else 'significant'} at {interest_pct}% of outflows — {'good sign ✓' if interest_pct < 25 else 'accelerate repayments.'}
  </div>
</div>
""", unsafe_allow_html=True)

# ── IS THIS LOAN GOOD OR BAD? ──────────────────────────────────────────────────
st.markdown('<div class="section-label">Is This Loan Good or Bad?</div>', unsafe_allow_html=True)

insights = [
    ("good","↑","11.5% p.a. is reasonable",
     "For an unsecured or semi-secured loan this is competitive. Business loans typically run 14–18%, so you're in a strong position."),
    ("good","↑","Flexible repayment pattern",
     f"Payments range from {fmt(smallest_pay)} to {fmt(largest_pay)}, showing the lender permits variable amounts. This is rare and valuable — use it aggressively when cash permits."),
    ("warn","!","No fixed EMI discipline",
     f"Irregular payments mean interest accrues silently before a lump sum lands. Aim for a minimum of ₹15K–20K every 7 days to keep interest from compounding idle."),
    ("info","i","Daily interest model",
     f"At {daily_rate*100:.4f}% per day, every ₹1L outstanding costs ~₹{cost_per_lakh:,.0f}/day. Paying even ₹10K earlier saves you disproportionately on total interest."),
]

for kind, icon, title, body in insights:
    st.markdown(f"""
    <div class="intel-card {kind}">
      <div class="intel-title">{icon}&nbsp;&nbsp;{title}</div>
      <div class="intel-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)

# ── HOW TO FINISH EARLY ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How to Finish Early — 3 Scenarios</div>', unsafe_allow_html=True)

def months_to_payoff(pmt, bal, rate_d):
    b = bal
    for i in range(1, 361):
        interest  = b * rate_d * 30
        principal = max(0.0, pmt - interest)
        b         = max(0.0, b - principal)
        if b <= 0: return i
    return None

def future_interest(pmt, bal, rate_d, n):
    b, tot = bal, 0.0
    for _ in range(n):
        interest = b * rate_d * 30
        tot     += interest
        b        = max(0.0, b - max(0.0, pmt - interest))
    return tot

def payoff_str(n):
    return (today + timedelta(days=n * 30)).strftime("%b %Y")

scenarios = [
    ("bg-green", "Aggressive — finish in ~12 months",    balance / 10,  "Aggressive"),
    ("bg-amber", "Moderate — finish in ~18–20 months",   balance / 17,  "Moderate"),
    ("bg-blue",  "Conservative — finish in ~28–30 months", balance / 27, "Conservative"),
]

for badge, label, monthly, name in scenarios:
    n = months_to_payoff(monthly, balance, daily_rate)
    if n is None: continue
    fi = future_interest(monthly, balance, daily_rate, n)
    yrs, mns = divmod(n, 12)
    dur = f"{yrs}y {mns}m" if yrs else f"{n} months"

    descs = {
        "Aggressive":   f"Split into 2–3 payments of {fmt(monthly/3)} every 10 days. At {fmt(balance)} outstanding, you'll close by <b>{payoff_str(n)}</b>. Total additional interest: ~{fmt(fi)} only.",
        "Moderate":     f"Two payments of {fmt(monthly/2)} per month. Closes by <b>{payoff_str(n)}</b>. Total remaining interest: ~{fmt(fi)}. Manageable if cash flow is tight.",
        "Conservative": f"One payment of {fmt(monthly)} per month. Closes by <b>{payoff_str(n)}</b>. Remaining interest: ~{fmt(fi)}. Not ideal — interest nearly doubles vs aggressive path.",
    }

    st.markdown(f"""
    <div class="sc-card">
      <div class="sc-badge {badge}">{label}</div>
      <div class="sc-title">Pay {fmt(monthly)} per month</div>
      <div class="sc-body">{descs[name]}</div>
    </div>
    """, unsafe_allow_html=True)

# ── KEY STATISTICS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Key Statistics</div>', unsafe_allow_html=True)

left_s = [
    ("Loan start",       loan_start_dt.strftime("%d %b %Y")),
    ("Months elapsed",   f"{months_elapsed} months"),
    ("No. of payments",  str(n_payments)),
    ("Avg payment size", f"₹{avg_payment:,.0f}"),
    ("Largest payment",  fmt(largest_pay)),
    ("Smallest payment", fmt(smallest_pay)),
]
right_s = [
    ("Interest rate (annual)", "11.5%"),
    ("Interest rate (daily)",  f"{daily_rate*100:.4f}%"),
    ("Cost per ₹1L per day",   f"₹{cost_per_lakh:,.0f}"),
    ("Interest paid to date",  fmt(total_interest)),
    ("Principal remaining",    fmt(balance)),
    ("% loan cleared",         f"{pct_cleared}%"),
]

inner = "".join(
    f'<div class="stat-item"><span class="sk">{lk}</span><span class="sv">{lv}</span></div>'
    f'<div class="stat-item"><span class="sk">{rk}</span><span class="sv gold">{rv}</span></div>'
    for (lk,lv),(rk,rv) in zip(left_s, right_s)
)
st.markdown(f'<div class="panel" style="padding:0;"><div class="stat-grid">{inner}</div></div>', unsafe_allow_html=True)

# ── ANALYTICS CHARTS ───────────────────────────────────────────────────────────
# ── CHARTS ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Analytics</div>', unsafe_allow_html=True)

GOLD   = "#c9a96e"
SLATE  = "#3d4f6b"
BG     = "#080b10"
CARD   = "#0c1118"
GRID   = "#1a2235"
TEXT   = "#c9d1d9"
MUTED  = "#7a8497"

chart_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=TEXT, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    title_font=dict(family="Cormorant Garamond, serif", size=18, color="#e8dcc8"),
)

# 1/3 Donut, 2/3 Stacked Bar
c1, c2 = st.columns([1, 2.3])

# ── Donut ──
with c1:
    fig_donut = go.Figure(go.Pie(
        labels=["Principal Repaid", "Interest Paid"],
        values=[principal_paid, total_interest],
        hole=0.72,
        marker=dict(colors=[GOLD, SLATE], line=dict(color=BG, width=3)),
        textinfo="none",
        hovertemplate="%{label}<br>INR %{value:,.2f}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{round(principal_paid/(total_paid or 1)*100, 1)}%</b><br>principal",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=15, color=TEXT, family="DM Mono, monospace"),
        align="center",
    )
    fig_donut.update_layout(**chart_layout, title="Payment Composition",
                            showlegend=True,
                            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                                        font=dict(size=11, color=MUTED)))
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Stacked Bar ──
with c2:
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=payments_df['payment_date'],
        y=payments_df['principal_paid'],
        name='Principal',
        marker_color=GOLD,
        hovertemplate="<b>%{x}</b><br>Principal: INR %{y:,.0f}<extra></extra>"
    ))
    fig_bar.add_trace(go.Bar(
        x=payments_df['payment_date'],
        y=payments_df['interest_paid'],
        name='Interest',
        marker_color=SLATE,
        hovertemplate="Interest: INR %{y:,.0f}<extra></extra>"
    ))
    fig_bar.update_layout(
        **chart_layout,
        title="Payment Impact",
        barmode='stack',
        xaxis=dict(gridcolor=GRID, tickfont=dict(size=10), showgrid=False),
        yaxis=dict(gridcolor=GRID, tickfont=dict(size=10)),
        bargap=0.25,
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right", font=dict(size=11, color=MUTED))
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Cumulative area (FULL WIDTH) ──
fig_area = go.Figure()
fig_area.add_trace(go.Scatter(
    x=payments_df['payment_date'],
    y=payments_df['balance_after'],
    fill='tozeroy',
    fillcolor=f"rgba(201,169,110,0.08)",
    line=dict(color=GOLD, width=2.5),
    mode='lines+markers',
    marker=dict(color=GOLD, size=6, line=dict(color=BG, width=1.5)),
    hovertemplate="<b>%{x}</b><br>Balance: INR %{y:,.0f}<extra></extra>",
))
fig_area.update_layout(
    **chart_layout,
    title="Balance Burn-Down",
    xaxis=dict(gridcolor=GRID, tickfont=dict(size=11), showgrid=False),
    yaxis=dict(gridcolor=GRID, tickfont=dict(size=11)),
    #margin=dict(l=16, r=16, t=40, b=16)
)
st.plotly_chart(fig_area, use_container_width=True)

# ── PAYOFF FORECAST ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Payoff Forecast</div>', unsafe_allow_html=True)

def build_forecast(bal, rate_d, monthly):
    rows, b, cur = [], bal, today
    for _ in range(360):
        if b <= 0: break
        raw_interest = b * rate_d * 30
        interest  = round(raw_interest, 0)
        principal = max(0.0, monthly - interest)
        #interest  = b * rate_d * 30
        #principal = max(0.0, monthly - interest)
        b         = max(0.0, b - principal)
        cur       = cur + timedelta(days=30)
        rows.append({"date": cur, "balance": round(b,2), "interest": round(interest,2), "principal": round(principal,2)})
        if b == 0: break
    return pd.DataFrame(rows)

fc1, fc2 = st.columns([3, 1])
with fc2:
    st.markdown("<br>", unsafe_allow_html=True)
    monthly_input = st.number_input("Monthly Payment (₹)", min_value=100.0,
        max_value=float(balance) if balance > 100 else 1e7,
        value=round(avg_payment, 0), step=500.0, format="%.0f")
    min_pmt = balance * daily_rate * 30
    if monthly_input <= min_pmt:
        st.warning(f"Min to reduce balance: ₹{min_pmt:,.0f}")

with fc1:
    fdf = build_forecast(balance, daily_rate, monthly_input)
    paid_off = (not fdf.empty) and (fdf['balance'].iloc[-1] == 0)
    if not paid_off:
        st.error("Payment too low to clear within 30 years.")
    else:
        pd_date  = fdf['date'].iloc[-1]
        mo_left  = len(fdf)
        fut_int  = fdf['interest'].sum()
        fdf['cum_int'] = fdf['interest'].cumsum()

        ff = go.Figure()
        ff.add_trace(go.Scatter(x=fdf['date'], y=fdf['balance'], name="Remaining Balance",
            line=dict(color=GOLD, width=2.5), fill='tozeroy', fillcolor="rgba(201,169,110,0.06)",
            hovertemplate="<b>%{x|%b %Y}</b><br>₹%{y:,.0f}<extra></extra>"))
        ff.add_trace(go.Scatter(x=fdf['date'], y=fdf['cum_int'], name="Cumulative Interest",
            line=dict(color=SLATE, width=1.5, dash='dot'),
            hovertemplate="<b>%{x|%b %Y}</b><br>Interest: ₹%{y:,.0f}<extra></extra>"))      
        ff.add_vline(x=pd_date.strftime("%Y-%m-%d"), line_width=1, line_dash="dash", line_color="rgba(201, 169, 110, 0.26)")        
        ff.add_annotation(x=pd_date.strftime("%Y-%m-%d"), y=balance*0.85,
            text=f"  Payoff {pd_date.strftime('%b %Y')}", showarrow=False,
            font=dict(size=10, color=GOLD, family="DM Mono, monospace"))
        ff.update_layout(**chart_layout, title="Projected Balance to Zero",
            xaxis=dict(gridcolor=GRID, tickfont=dict(size=9), showgrid=False),
            yaxis=dict(gridcolor=GRID, tickfont=dict(size=9), tickprefix="₹"),
            legend=dict(orientation="h", y=-0.12, x=0, font=dict(size=10, color=MUTED)), height=340)
        st.plotly_chart(ff, use_container_width=True)

if not fdf.empty and fdf['balance'].iloc[-1] == 0:
    yrs, mns = divmod(mo_left, 12)
    fk1, fk2, fk3, fk4 = st.columns(4)
    fk1.metric("Payoff Date",    pd_date.strftime("%b %Y"))
    fk2.metric("Time Remaining", f"{yrs}y {mns}m")
    fk3.metric("Future Interest", fmt(fut_int))
    fk4.metric("Total Cost",      fmt(balance + fut_int))

    with st.expander("View full amortization schedule"):
        sc = fdf[['date','balance','interest','principal']].copy()
        sc.columns = ['Date','Remaining Balance','Interest','Principal']
        sc['Date']              = sc['Date'].apply(lambda d: d.strftime("%b %Y"))
        sc['Remaining Balance'] = sc['Remaining Balance'].apply(lambda x: f"₹{x:,.0f}")
        sc['Interest']          = sc['Interest'].apply(lambda x: f"₹{x:,.0f}")
        sc['Principal']         = sc['Principal'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(sc, use_container_width=True, hide_index=True)

# ── LEDGER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Transaction Ledger</div>', unsafe_allow_html=True)
disp = payments_df[['payment_date','amount','interest_paid','principal_paid','balance_after']].copy()
disp.columns = ['Date','Payment (₹)','Interest (₹)','Principal (₹)','Balance After (₹)']
for col in disp.columns[1:]:
    disp[col] = disp[col].apply(lambda x: f"{x:,.0f}")
disp['Date'] = pd.to_datetime(disp['Date']).dt.strftime('%d %b %Y')
st.dataframe(disp, use_container_width=True, hide_index=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">New Payment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Record a repayment</div>', unsafe_allow_html=True)

    amount = st.number_input("Amount (₹)", min_value=0.0, step=1000.0, format="%.0f")
    date   = st.date_input("Payment Date")
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("Record Payment")

    if submit:
        cursor.execute("SELECT current_balance, last_payment_date, total_interest, total_paid FROM LoanSummary WHERE id=1")
        row = cursor.fetchone()
        bal, last_date, t_int, t_paid = float(row[0]), row[1], float(row[2]), float(row[3])

        if date > today:       st.error("Date cannot be in the future."); st.stop()
        if date <= last_date:  st.error("Date must be after last payment date."); st.stop()

        days     = (date - last_date).days
        
        # Calculate raw interest, then round to the nearest whole rupee
        raw_int  = bal * daily_rate * days
        int_amt  = round(raw_int, 0) 
        
        princ_p  = max(0.0, amount - int_amt)
        new_bal  = bal - princ_p

        if int_amt > amount: st.warning("Payment less than interest — balance will increase.")

        cursor.execute(
            "INSERT INTO Payments (payment_date, amount, interest_paid, principal_paid, balance_after) VALUES (?,?,?,?,?)",
            date, amount, int_amt, princ_p, new_bal)
        cursor.execute(
            "UPDATE LoanSummary SET current_balance=?, total_paid=?, total_interest=?, last_payment_date=? WHERE id=1",
            new_bal, t_paid + amount, t_int + int_amt, date)
        conn.commit()
        st.success("Payment recorded.")

        st.markdown(f"""
        <div style='margin-top:1rem;padding:1.1rem 1.2rem;background:#0c1118;border:1px solid #1a2235;border-radius:4px;font-size:.9rem;line-height:2.2;'>
          <div style='color:#8a9ab0;letter-spacing:.15em;font-size:.75rem;text-transform:uppercase;margin-bottom:.6rem;'>Breakdown</div>
          Days elapsed <span style='float:right;color:#c9a96e'>{days}</span><br>
          Interest charged <span style='float:right;color:#c9a96e'>₹{int_amt:,.0f}</span><br>
          Principal paid <span style='float:right;color:#c9a96e'>₹{princ_p:,.0f}</span><br>
          New balance <span style='float:right;color:#e8dcc8'>₹{new_bal:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        st.rerun()

    st.markdown("<br><hr style='border-color:#1a2235;margin:1.5rem 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size:.82rem;letter-spacing:.15em;text-transform:uppercase;color:#8a9ab0;margin-bottom:1rem;'>Loan Parameters</div>
    <div style='font-size:.92rem;line-height:2.5;color:#8a9ab0;'>
      Interest Rate <span style='float:right;color:#c9a96e'>11.5% p.a.</span><br>
      Daily Rate <span style='float:right;color:#c9d1d9'>{daily_rate*100:.4f}%</span><br>
      Calculation <span style='float:right;color:#c9d1d9'>Daily Reducing</span><br>
      Cost per ₹1L/day <span style='float:right;color:#c9a96e'>₹{cost_per_lakh:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime
from datetime import date as dt_date


# DB connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=basic-zain-loan.database.windows.net;"
    "DATABASE=free-sql-db-7340985;"
    "UID=loanuser;"
    "PWD=StrongPassword123!;"
)

cursor = conn.cursor()

st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .block-container {
        padding-top: 2rem;
    }
    div[data-testid="metric-container"] {
        background-color: #111827;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Loan Tracker App")

st.set_page_config(page_title="Loan Tracker", layout="wide")

# Dashboard
df = pd.read_sql("SELECT * FROM LoanSummary", conn)

st.markdown("## 📊 Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Balance", round(df['current_balance'][0], 2))
col2.metric("📤 Paid", round(df['total_paid'][0], 2))
col3.metric("📈 Interest", round(df['total_interest'][0], 2))

import matplotlib.pyplot as plt

principal = df['total_paid'][0] - df['total_interest'][0]
interest = df['total_interest'][0]
payments_df = pd.read_sql("SELECT * FROM Payments ORDER BY payment_date", conn)



col1, col2, col3 = st.columns(3)

#pies
with col1:
    fig1, ax1 = plt.subplots()
    ax1.pie(
        [principal, interest],
        labels=['Principal', 'Interest'],
        autopct='%1.1f%%'
    )
    ax1.set_title("Split")
    st.pyplot(fig1, use_container_width=True)

#payments line
with col2:
    fig2, ax2 = plt.subplots()
    ax2.plot(payments_df['payment_date'], payments_df['amount'], marker='o')
    ax2.set_title("Payments")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2, use_container_width=True)

#growth line
with col3:
    payments_df['cumulative'] = payments_df['amount'].cumsum()

    fig3, ax3 = plt.subplots()
    ax3.plot(payments_df['payment_date'], payments_df['cumulative'])
    ax3.set_title("Growth")
    ax3.tick_params(axis='x', rotation=45)
    st.pyplot(fig3, use_container_width=True)

#input
with st.sidebar:
    st.header("💳 Enter Payment")

    amount = st.number_input("Amount", min_value=0)
    date = st.date_input("Date")

    submit = st.button("Submit Payment")




if st.button("Submit Payment"):

    # Fetch loan data
    cursor.execute("SELECT current_balance, last_payment_date, total_interest, total_paid FROM LoanSummary WHERE id=1")
    row = cursor.fetchone()

    balance = float(row[0])
    last_date = row[1]
    total_interest = float(row[2])
    total_paid = float(row[3])

    if date < last_date:
        st.error("❌ Payment date cannot be before last payment date")
        st.stop()
    
    today = dt_date.today()

    # ❌ Future date check
    if date > today:
        st.error("❌ Payment date cannot be in the future")
        st.stop()

    # ❌ Same or older date check
    if date <= last_date:
        st.error("❌ Payment date must be after last payment date")
        st.stop()

    days = max(0, (date - last_date).days)   
    if days == 0:
        st.info("ℹ️ No interest added since payment is on same day") 

    rate = 0.115 / 365



    interest = balance * rate * days
    principal_paid = max(0, amount - interest)
    new_balance = balance - principal_paid

    st.write("Days:", days)
    st.write("Interest:", interest)

    if interest > amount:
        st.warning("⚠️ Payment is less than interest. Loan will increase.")

    # Insert payment
    cursor.execute("INSERT INTO Payments (payment_date, amount) VALUES (?, ?)", date, amount)

    # Update summary
    cursor.execute("""
        UPDATE LoanSummary
        SET current_balance=?, total_paid=?, total_interest=?, last_payment_date=?
        WHERE id=1
    """, new_balance, total_paid + amount, total_interest + interest, date)

    conn.commit()

    st.success("Payment processed!")



# Payment history
payments_df = pd.read_sql("SELECT * FROM Payments", conn)

st.write("### Payment History")
st.dataframe(payments_df)


import pandas as pd
import pyodbc
from datetime import datetime

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=basic-zain-loan.database.windows.net;"
    "DATABASE=free-sql-db-7340985;"
    "UID=loanuser;"
    "PWD=StrongPassword123!;"
)

cursor = conn.cursor()





# 2. WIPE THE CORRUPTED HISTORY
print("Wiping old ledger data...")
cursor.execute("DELETE FROM Payments")
conn.commit()

# 3. EXTRACT: Read your actual CSV file
print("Reading data from CSV...")
df = pd.read_excel("payments.xlsx")

# Ensure dates are properly formatted by pandas
# (Update 'Date' and 'Amount' to match your CSV headers if they differ)
df['Date'] = pd.to_datetime(df['payment_date'])
df = df.sort_values(by='Date') # Ensure strict chronological order

# 4. TRANSFORM & LOAD: The Bank's Exact State Machine
balance = 2500000.0
last_date = datetime.strptime('2023-11-27', '%Y-%m-%d')
annual_rate = 0.115

total_interest_paid = 0.0
total_amount_paid = 0.0

print("Rebuilding ledger using bank rounding rules...")

for index, row in df.iterrows():
    current_date = row['Date']
    amount = float(row['amount'])
    
    days_elapsed = (current_date - last_date).days
    
    # THE SECRET SAUCE: Rounding interest to nearest whole rupee before subtracting
    raw_interest = balance * (annual_rate / 365) * days_elapsed
    interest_charged = round(raw_interest, 0) 
    
    principal_paid = amount - interest_charged
    balance = balance - principal_paid
    
    total_interest_paid += interest_charged
    total_amount_paid += amount
    
    # Insert cleanly into Azure SQL
    cursor.execute("""
        INSERT INTO Payments (payment_date, amount, interest_paid, principal_paid, balance_after)
        VALUES (?, ?, ?, ?, ?)
    """, current_date, amount, interest_charged, principal_paid, balance)
    
    last_date = current_date
    print(f"Logged {current_date.strftime('%Y-%m-%d')}: Paid ₹{amount:,.0f} | Bal: ₹{balance:,.0f}")

# 5. UPDATE FINAL SUMMARY
cursor.execute("""
    UPDATE LoanSummary 
    SET current_balance=?, total_paid=?, total_interest=?, last_payment_date=? 
    WHERE id=1
""", balance, total_amount_paid, total_interest_paid, last_date)

conn.commit()
print(f"\nSuccess! Final Reconciled Balance: ₹{balance:,.0f}")
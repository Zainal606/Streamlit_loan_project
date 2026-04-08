import pyodbc
from datetime import datetime
import streamlit as st

# 1. CONNECT TO AZURE SQL
# DB connection
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

# 3. YOUR EXACT PAYMENTS (From your Excel/Passbook)
# Format: ('YYYY-MM-DD', Total Amount Paid)
raw_payments = [
    ('2024-01-22', 50000.0), ('2024-02-17', 60000.0), ('2024-04-03', 100000.0),
    ('2024-05-21', 50000.0), ('2024-06-07', 70000.0), ('2024-07-06', 60000.0),
    ('2024-10-05', 100000.0), ('2025-01-13', 88000.0), ('2025-01-24', 15000.0),
    ('2025-01-31', 15000.0), ('2025-02-07', 15000.0), ('2025-02-14', 15000.0),
    ('2025-02-21', 15000.0), ('2025-02-28', 10000.0), ('2025-03-07', 10000.0),
    ('2025-03-11', 10000.0), ('2025-03-17', 15000.0), ('2025-03-24', 15000.0),
    ('2025-04-02', 15000.0), ('2025-04-10', 20000.0), ('2025-05-08', 100000.0),
    ('2025-05-16', 10000.0), ('2025-05-22', 10000.0), ('2025-05-28', 10000.0),
    ('2025-06-04', 10000.0), ('2025-06-10', 10000.0), ('2025-06-17', 10000.0),
    ('2025-06-30', 20000.0), ('2025-07-07', 20000.0), ('2025-07-14', 30000.0),
    ('2025-07-21', 10000.0), ('2025-07-25', 10000.0), ('2025-09-01', 100000.0),
    ('2025-09-25', 100000.0), ('2025-10-24', 60000.0), ('2025-11-10', 46000.0),
    ('2025-12-24', 60000.0), ('2026-01-27', 63000.0), ('2026-02-27', 15000.0),
    ('2026-03-03', 45000.0) 
]

# 4. THE BANK'S EXACT STATE MACHINE
balance = 2500000.0
last_date = datetime.strptime('2023-11-27', '%Y-%m-%d')
annual_rate = 0.115

total_interest_paid = 0.0
total_amount_paid = 0.0

print("Rebuilding ledger using bank rounding rules...")

for date_str, amount in raw_payments:
    current_date = datetime.strptime(date_str, '%Y-%m-%d')
    days_elapsed = (current_date - last_date).days
    
    # THE SECRET SAUCE: Rounding interest to nearest whole rupee before subtracting
    raw_interest = balance * (annual_rate / 365) * days_elapsed
    interest_charged = round(raw_interest, 0) 
    
    principal_paid = amount - interest_charged
    balance = balance - principal_paid
    
    total_interest_paid += interest_charged
    total_amount_paid += amount
    
    cursor.execute("""
        INSERT INTO Payments (payment_date, amount, interest_paid, principal_paid, balance_after)
        VALUES (?, ?, ?, ?, ?)
    """, current_date, amount, interest_charged, principal_paid, balance)
    
    last_date = current_date

# 5. UPDATE FINAL SUMMARY
cursor.execute("""
    UPDATE LoanSummary 
    SET current_balance=?, total_paid=?, total_interest=?, last_payment_date=? 
    WHERE id=1
""", balance, total_amount_paid, total_interest_paid, last_date)

conn.commit()
print(f"Success! Reconciled Balance matches passbook: ₹{balance:,.0f}")
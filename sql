CREATE LOGIN loanuser WITH PASSWORD = 'StrongPassword123!';

CREATE USER loanuser WITH PASSWORD = 'StrongPassword123!';

ALTER ROLE db_owner ADD MEMBER loanuser;

SELECT current_balance, last_payment_date, total_interest, total_paid FROM LoanSummary WHERE id=1

delete from Payments
delete from LoanSummary


INSERT INTO LoanSummary (id, current_balance, total_paid, total_interest, last_payment_date)
VALUES (1, 2500000, 0, 0, '2023-11-27');

select * from LoanSummary
select * from Payments

ALTER TABLE Payments
ADD interest_paid FLOAT,
    principal_paid FLOAT,
    balance_after FLOAT;

    
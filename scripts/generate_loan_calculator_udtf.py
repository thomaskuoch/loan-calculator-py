begin = """-- THIS FILE IS GENERATED AUTOMATICALLY. DO NOT EDIT IT MANUALLY.
-- To regenerate it, run `python scripts/generate_loan_calculator_udtf.py`

create or replace function loan_calculator(
    amount number,
    taeg float,
    number_repayments number,
    start_date date,
    days_first_repayment number,
    as_interests_or_base_fees varchar
)
returns table (
    date date,
    amount_repayment number,
    amount_principal number,
    amount_interests number,
    amount_base_fees number,
    amount_remaining_principal number
)
language python
runtime_version=3.9
handler='LoanCalculator'
as $$
"""

with open("loan_calculator.py", "r") as f:
    code = f.read()

udtf_code = begin + code + "$$;"

with open("udfs/loan_calculator.sql", "w") as f:
    f.write(udtf_code)

import sys
from datetime import date

from loan_calculator import TooHighInterestsError, run_loan_calculator

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(
            "Usage: python cli.py <amount> <taeg> <number_repayments> <start_date> <days_first_repayment> [<as_interests_or_base_fees> [<as_json>]]"
        )
        sys.exit(1)

    amount = int(sys.argv[1])
    taeg = float(sys.argv[2])
    number_repayments = int(sys.argv[3])
    start_date = date.fromisoformat(sys.argv[4])
    days_first_repayment = int(sys.argv[5])
    as_interests_or_base_fees = sys.argv[6] if len(sys.argv) > 6 else "interests"
    as_json = sys.argv[7] if len(sys.argv) > 7 else False

    try:
        repayments = run_loan_calculator(
            amount,
            taeg,
            number_repayments,
            start_date,
            days_first_repayment,
            as_interests_or_base_fees,
            as_json,
        )
    except TooHighInterestsError as e:
        print(e)
        sys.exit(1)

    print(repayments)

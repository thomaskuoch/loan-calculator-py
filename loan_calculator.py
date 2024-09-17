import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import List, Literal, Union

from dateutil.relativedelta import relativedelta


@dataclass
class Repayment:
    """Repayment schedule item"""

    date: date
    amount_repayment: int
    amount_principal: int
    amount_interests: int
    amount_base_fees: int
    amount_remaining_principal: int


class TooHighInterestsError(Exception):
    pass


def run_loan_calculator(
    amount: int,
    taeg: float,
    number_repayments: int,
    funding_date: date,
    days_first_repayment: int = 45,
    as_interests_or_base_fees: Literal["interests", "base_fees"] = "interests",
    as_json: bool = False,
) -> Union[List[Repayment], str]:
    """Compute a finfrog loan repayment schedule.

    Parameters
    ----------
    amount : int
        Principal amount of the loan in cents.
    taeg : float
        Annual percentage rate of charge, between 0 and 1.
    number_repayments : int
        Number of repayments.
    funding_date : date
        Funding date of the loan.
    days_first_repayment : int, optional
        Number of days before the first repayment, by default 45
    as_interests_or_base_fees : Literal['interests', 'base_fees'], optional
        If 'base_fees', group all interests in the first repayment, which is considered as fees, by default 'interests'
    as_json : bool, optional
        If True, jsonify the repayment schedule, by default False

    Returns
    -------
    Union[List[Repayment], List[dict]]
        Repayment schedule.
    """
    # compute daily rate
    daily_rate = compute_interval_rate(taeg, n_days=1)

    # compute constant amount repayment with respect to the daily rate
    dates = []
    dates.append(funding_date + timedelta(days=days_first_repayment))
    for i in range(1, number_repayments):
        dates.append(dates[0] + relativedelta(months=i))
    rates = [1 / (1 + daily_rate) ** (d - funding_date).days for d in dates]
    constant_payment = math.floor(amount / sum(rates))

    # compute repayment schedule
    repayments = []
    remaining_principal = amount
    for start, end in pairwise([funding_date] + dates):
        repayment_interests = math.floor(
            remaining_principal * compute_interval_rate(taeg, n_days=(end - start).days)
        )
        if repayment_interests > constant_payment:
            raise TooHighInterestsError(
                "The repayment is too low to cover the interests; please modify loan parameters."
            )
        repayment_principal = constant_payment - repayment_interests
        remaining_principal -= repayment_principal
        repayments.append(
            Repayment(
                date=end,
                amount_repayment=constant_payment,
                amount_principal=repayment_principal,
                amount_interests=repayment_interests,
                amount_remaining_principal=remaining_principal,
                amount_base_fees=0,
            )
        )

    # adjust last repayment to match the remaining principal due to rounding issues
    if remaining_principal != 0:
        repayments[-1].amount_repayment += remaining_principal
        repayments[-1].amount_principal += remaining_principal
        repayments[-1].amount_remaining_principal = 0

    if as_interests_or_base_fees == "base_fees":
        remaining_principal = amount
        base_fees_remainder = sum(r.amount_interests for r in repayments)
        for r in repayments:
            r.amount_interests = 0
            if base_fees_remainder > r.amount_repayment:
                r.amount_base_fees = r.amount_repayment
                base_fees_remainder -= r.amount_base_fees
            else:
                r.amount_base_fees = base_fees_remainder
                base_fees_remainder = 0
            r.amount_principal = r.amount_repayment - r.amount_base_fees
            remaining_principal -= r.amount_principal
            r.amount_remaining_principal = remaining_principal

    if as_json:
        repayments = json.dumps([asdict(r) for r in repayments], default=str)

    return repayments


def compute_interval_rate(taeg: float, n_days: int) -> float:
    """Compute the interval rate from the annual percentage rate of charge.

    Parameters
    ----------
    taeg : float
        Annual percentage rate of charge, between 0 and 1.
    n_days : int
        Number of days in the interval.

    Returns
    -------
    float
        Interval rate.
    """
    return (1 + taeg) ** (n_days / 365) - 1


def pairwise(iterable):
    iterator = iter(iterable)
    a = next(iterator, None)
    for b in iterator:
        yield a, b
        a = b


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(
            "Usage: python loan_calculator.py <amount> <taeg> <number_repayments> <funding_date> <days_first_repayment> [<as_interests_or_base_fees> [<as_json>]]"
        )
        sys.exit(1)

    amount = int(sys.argv[1])
    taeg = float(sys.argv[2])
    number_repayments = int(sys.argv[3])
    funding_date = date.fromisoformat(sys.argv[4])
    days_first_repayment = int(sys.argv[5])
    as_interests_or_base_fees = sys.argv[6] if len(sys.argv) > 6 else "interests"
    as_json = sys.argv[7] if len(sys.argv) > 7 else False

    try:
        repayments = run_loan_calculator(
            amount,
            taeg,
            number_repayments,
            funding_date,
            days_first_repayment,
            as_interests_or_base_fees,
            as_json,
        )
    except TooHighInterestsError as e:
        print(e)
        sys.exit(1)

    print(repayments)

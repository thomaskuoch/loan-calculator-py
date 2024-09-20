-- THIS FILE IS GENERATED AUTOMATICALLY. DO NOT EDIT IT MANUALLY.
-- To regenerate it, run `python generate_udtf.py`

create or replace function loan_calculator(
    amount number,
    taeg float,
    number_repayments number,
    funding_date date,
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
import calendar
import json
import math
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import List, Literal, Union


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
    if isinstance(funding_date, str):
        funding_date = date.fromisoformat(funding_date)
    if isinstance(as_json, str):
        as_json = as_json.lower() in ("true", "1")
    validate_inputs(
        amount,
        taeg,
        number_repayments,
        funding_date,
        days_first_repayment,
        as_interests_or_base_fees,
        as_json,
    )

    # compute daily rate
    daily_rate = compute_interval_rate(taeg, n_days=1)

    # compute constant amount repayment with respect to the daily rate
    first_repayment_date = funding_date + timedelta(days=days_first_repayment)
    dates = [add_months(first_repayment_date, i) for i in range(number_repayments)]
    rates = [1 / (1 + daily_rate) ** (d - funding_date).days for d in dates]
    constant_payment = math.floor(amount / sum(rates))

    # compute repayment schedule
    repayments = []
    remaining_principal = amount
    for start, end in pairwise([funding_date] + dates):
        n_days = (end - start).days
        repayment_interests = math.floor(
            remaining_principal * compute_interval_rate(taeg, n_days)
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
                amount_base_fees=0,
                amount_remaining_principal=remaining_principal,
            )
        )

    # adjust last repayment to match the remaining principal due to rounding issues
    if remaining_principal != 0:
        repayments[-1].amount_repayment += remaining_principal
        repayments[-1].amount_principal += remaining_principal
        repayments[-1].amount_remaining_principal = 0

    if as_interests_or_base_fees == "base_fees":
        repayments = apply_base_fees(repayments, amount)

    if as_json:
        repayments = json.dumps([asdict(r) for r in repayments], default=str)

    return repayments


def apply_base_fees(repayments: List[Repayment], amount: int) -> List[Repayment]:
    """Transform to the repayment schedule from a interests to base_fees vision."""
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


def add_months(date_input: date, months: int) -> date:
    month = date_input.month - 1 + months
    year = date_input.year + month // 12
    month = month % 12 + 1
    day = min(date_input.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def pairwise(iterable):
    """Yield successive pairs from an iterable."""
    iterator = iter(iterable)
    a = next(iterator, None)
    for b in iterator:
        yield a, b
        a = b


def validate_inputs(
    amount: int,
    taeg: float,
    number_repayments: int,
    funding_date: date,
    days_first_repayment: int,
    as_interests_or_base_fees: str,
    as_json: bool,
):
    """Validate loan parameters."""
    if amount < 100:
        raise ValueError(
            "The principal amount of the loan must be greater than 1 euro."
        )
    if taeg < 0 or taeg > 1:
        raise ValueError(
            "The annual percentage rate of charge must be between 0 and 1."
        )
    if number_repayments <= 0:
        raise ValueError("The number of repayments must be greater than 0.")
    if not isinstance(funding_date, date):
        raise ValueError("The funding date must be a date.")
    if days_first_repayment <= 0:
        raise ValueError(
            "The number of days before the first repayment must be greater than 0."
        )
    if as_interests_or_base_fees not in ["interests", "base_fees"]:
        raise ValueError(
            "The repayment schedule must be either as interests or base fees."
        )
    if as_json not in [True, False]:
        raise ValueError("The as_json argument must be a boolean.")


class LoanCalculator:
    """Handler for snowflake UDTF"""

    def process(
        self,
        amount: int,
        taeg: float,
        number_repayments: int,
        funding_date: date,
        days_first_repayment: int,
        as_interests_or_base_fees: str,
    ):
        repayment_schedule = run_loan_calculator(
            amount=amount,
            taeg=taeg,
            number_repayments=number_repayments,
            funding_date=funding_date,
            days_first_repayment=days_first_repayment,
            as_interests_or_base_fees=as_interests_or_base_fees,
            as_json=False,
        )
        return [
            (
                r.date.isoformat(),
                r.amount_repayment,
                r.amount_principal,
                r.amount_interests,
                r.amount_base_fees,
                r.amount_remaining_principal,
            )
            for r in repayment_schedule
        ]
$$;
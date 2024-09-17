import json
from datetime import date

import pytest
from pyxirr import xirr

from loan_calculator import TooHighInterestsError, run_loan_calculator


@pytest.mark.parametrize(
    (
        "loan_parameters",
        "expected",
    ),
    [
        (
            {
                "amount": 10000,
                "taeg": 0.209,
                "number_repayments": 3,
                "funding_date": date(2022, 6, 1),
                "days_first_repayment": 45,
                "as_interests_or_base_fees": "interests",
            },
            [
                {
                    "date": "2022-07-16",
                    "amount_repayment": 3467,
                    "amount_principal": 3231,
                    "amount_interests": 236,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 6769,
                },
                {
                    "date": "2022-08-16",
                    "amount_repayment": 3467,
                    "amount_principal": 3358,
                    "amount_interests": 109,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 3411,
                },
                {
                    "date": "2022-09-16",
                    "amount_repayment": 3466,
                    "amount_principal": 3411,
                    "amount_interests": 55,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
        (
            {
                "amount": 10000,
                "taeg": 0.209,
                "number_repayments": 3,
                "funding_date": date(2022, 6, 1),
                "days_first_repayment": 45,
                "as_interests_or_base_fees": "base_fees",
            },
            [
                {
                    "date": "2022-07-16",
                    "amount_repayment": 3467,
                    "amount_principal": 3067,
                    "amount_interests": 0,
                    "amount_base_fees": 400,
                    "amount_remaining_principal": 6933,
                },
                {
                    "date": "2022-08-16",
                    "amount_repayment": 3467,
                    "amount_principal": 3467,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 3466,
                },
                {
                    "date": "2022-09-16",
                    "amount_repayment": 3466,
                    "amount_principal": 3466,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
        (
            {
                "amount": 60000,
                "taeg": 0.224,
                "number_repayments": 6,
                "funding_date": date(2024, 9, 24),
                "days_first_repayment": 37,
                "as_interests_or_base_fees": "interests",
            },
            [
                {
                    "date": "2024-10-31",
                    "amount_repayment": 10639,
                    "amount_principal": 9397,
                    "amount_interests": 1242,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 50603,
                },
                {
                    "date": "2024-11-30",
                    "amount_repayment": 10639,
                    "amount_principal": 9792,
                    "amount_interests": 847,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 40811,
                },
                {
                    "date": "2024-12-31",
                    "amount_repayment": 10639,
                    "amount_principal": 9933,
                    "amount_interests": 706,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 30878,
                },
                {
                    "date": "2025-01-31",
                    "amount_repayment": 10639,
                    "amount_principal": 10105,
                    "amount_interests": 534,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 20773,
                },
                {
                    "date": "2025-02-28",
                    "amount_repayment": 10639,
                    "amount_principal": 10315,
                    "amount_interests": 324,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 10458,
                },
                {
                    "date": "2025-03-31",
                    "amount_repayment": 10639,
                    "amount_principal": 10458,
                    "amount_interests": 181,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
        (
            {
                "amount": 60000,
                "taeg": 0.224,
                "number_repayments": 6,
                "funding_date": date(2024, 9, 24),
                "days_first_repayment": 37,
                "as_interests_or_base_fees": "base_fees",
            },
            [
                {
                    "date": "2024-10-31",
                    "amount_repayment": 10639,
                    "amount_principal": 6805,
                    "amount_interests": 0,
                    "amount_base_fees": 3834,
                    "amount_remaining_principal": 53195,
                },
                {
                    "date": "2024-11-30",
                    "amount_repayment": 10639,
                    "amount_principal": 10639,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 42556,
                },
                {
                    "date": "2024-12-31",
                    "amount_repayment": 10639,
                    "amount_principal": 10639,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 31917,
                },
                {
                    "date": "2025-01-31",
                    "amount_repayment": 10639,
                    "amount_principal": 10639,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 21278,
                },
                {
                    "date": "2025-02-28",
                    "amount_repayment": 10639,
                    "amount_principal": 10639,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 10639,
                },
                {
                    "date": "2025-03-31",
                    "amount_repayment": 10639,
                    "amount_principal": 10639,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
        (
            {
                "amount": 150000,
                "taeg": 0.2144,
                "number_repayments": 12,
                "funding_date": date(2021, 3, 30),
                "days_first_repayment": 42,
                "as_interests_or_base_fees": "interests",
            },
            [
                {
                    "date": "2021-05-11",
                    "amount_repayment": 13957,
                    "amount_principal": 10567,
                    "amount_interests": 3390,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 139433,
                },
                {
                    "date": "2021-06-11",
                    "amount_repayment": 13957,
                    "amount_principal": 11638,
                    "amount_interests": 2319,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 127795,
                },
                {
                    "date": "2021-07-11",
                    "amount_repayment": 13957,
                    "amount_principal": 11901,
                    "amount_interests": 2056,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 115894,
                },
                {
                    "date": "2021-08-11",
                    "amount_repayment": 13957,
                    "amount_principal": 12030,
                    "amount_interests": 1927,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 103864,
                },
                {
                    "date": "2021-09-11",
                    "amount_repayment": 13957,
                    "amount_principal": 12230,
                    "amount_interests": 1727,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 91634,
                },
                {
                    "date": "2021-10-11",
                    "amount_repayment": 13957,
                    "amount_principal": 12483,
                    "amount_interests": 1474,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 79151,
                },
                {
                    "date": "2021-11-11",
                    "amount_repayment": 13957,
                    "amount_principal": 12641,
                    "amount_interests": 1316,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 66510,
                },
                {
                    "date": "2021-12-11",
                    "amount_repayment": 13957,
                    "amount_principal": 12887,
                    "amount_interests": 1070,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 53623,
                },
                {
                    "date": "2022-01-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13065,
                    "amount_interests": 892,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 40558,
                },
                {
                    "date": "2022-02-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13283,
                    "amount_interests": 674,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 27275,
                },
                {
                    "date": "2022-03-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13548,
                    "amount_interests": 409,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 13727,
                },
                {
                    "date": "2022-04-11",
                    "amount_repayment": 13955,
                    "amount_principal": 13727,
                    "amount_interests": 228,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
        (
            {
                "amount": 150000,
                "taeg": 0.2144,
                "number_repayments": 12,
                "funding_date": date(2021, 3, 30),
                "days_first_repayment": 42,
                "as_interests_or_base_fees": "base_fees",
            },
            [
                {
                    "date": "2021-05-11",
                    "amount_repayment": 13957,
                    "amount_principal": 0,
                    "amount_interests": 0,
                    "amount_base_fees": 13957,
                    "amount_remaining_principal": 150000,
                },
                {
                    "date": "2021-06-11",
                    "amount_repayment": 13957,
                    "amount_principal": 10432,
                    "amount_interests": 0,
                    "amount_base_fees": 3525,
                    "amount_remaining_principal": 139568,
                },
                {
                    "date": "2021-07-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 125611,
                },
                {
                    "date": "2021-08-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 111654,
                },
                {
                    "date": "2021-09-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 97697,
                },
                {
                    "date": "2021-10-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 83740,
                },
                {
                    "date": "2021-11-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 69783,
                },
                {
                    "date": "2021-12-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 55826,
                },
                {
                    "date": "2022-01-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 41869,
                },
                {
                    "date": "2022-02-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 27912,
                },
                {
                    "date": "2022-03-11",
                    "amount_repayment": 13957,
                    "amount_principal": 13957,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 13955,
                },
                {
                    "date": "2022-04-11",
                    "amount_repayment": 13955,
                    "amount_principal": 13955,
                    "amount_interests": 0,
                    "amount_base_fees": 0,
                    "amount_remaining_principal": 0,
                },
            ],
        ),
    ],
)
def test_loan_calculator(
    loan_parameters,
    expected,
):
    repayment_schedule = run_loan_calculator(
        **loan_parameters,
        as_json=True,
    )
    repayment_schedule = json.loads(repayment_schedule)
    assert repayment_schedule == expected

    # Check that the XIRR is close to the TAEG
    dates = [loan_parameters["funding_date"], *[r["date"] for r in repayment_schedule]]
    cashflows = [
        -loan_parameters["amount"],
        *[r["amount_repayment"] for r in repayment_schedule],
    ]
    xirr_value = xirr(dates, cashflows)
    taeg = loan_parameters["taeg"]
    assert taeg - xirr_value <= 0.1


def test_too_high_interests_error():
    with pytest.raises(TooHighInterestsError):
        run_loan_calculator(
            amount=300000,
            taeg=0.90,
            number_repayments=24,
            funding_date=date(2022, 6, 1),
            days_first_repayment=60,
            as_interests_or_base_fees="interests",
        )

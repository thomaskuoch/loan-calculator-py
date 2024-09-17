# Streamlit app
from datetime import date

import pandas as pd
import streamlit as st
from pyxirr import xirr

from loan_calculator import TooHighInterestsError, run_loan_calculator

st.set_page_config(page_title="Loan calculator")
st.title("Finfrog Loan Calculator")
st.write(
    "This app computes a Finfrog loan repayment schedule based on the following parameters:"
)
amount_principal = st.slider(
    "Principal amount (€)", min_value=0, max_value=3000, value=600, step=100
)
number_repayments = st.slider(
    "Number of repayments", min_value=1, step=1, max_value=24, value=6
)
taeg = st.number_input(
    "Annual percentage rate of charge (%)",
    min_value=0.0,
    max_value=100.0,
    value=22.4,
    step=0.01,
    format="%.2f",
)
funding_date = st.date_input("Funding date", date.today())
days_first_repayment = st.slider(
    "Days before the first repayment",
    min_value=30,
    step=1,
    value=45,
    max_value=60,
)
as_interests_or_base_fees = st.radio(
    "Repayment schedule as interests or base fees", ("Interests", "Base fees")
)

if st.button("Compute repayment schedule"):
    as_interests_or_base_fees = (
        "interests" if as_interests_or_base_fees == "Interests" else "base_fees"
    )
    try:
        repayment_schedule = run_loan_calculator(
            amount_principal * 100,
            taeg / 100,
            number_repayments,
            funding_date,
            days_first_repayment,
            as_interests_or_base_fees,
        )
    except TooHighInterestsError:
        st.error("The interests are too high, please modify loan parameters.")
        st.stop()
    df = pd.DataFrame(repayment_schedule)
    df.columns = [c.replace("amount_", "") for c in df.columns]
    num_cols = [
        "repayment",
        "principal",
        "interests",
        "base_fees",
        "remaining_principal",
    ]
    df[num_cols] = df[num_cols] / 100
    df.index += 1
    st.dataframe(
        df.style.format("{:.2f}", subset=num_cols),
        use_container_width=True,
    )
    total_fees = df["base_fees"].sum() + df["interests"].sum()
    st.write(f"Total fees: {round(total_fees, 2)}")

    # Assert XIRR is close to TAEG but always lower or equal
    cashflows = [-amount_principal] + df["repayment"].tolist()
    dates = [funding_date] + df["date"].tolist()
    irr = xirr(dates, cashflows)
    st.write(f"Internal rate of return (XIRR): {round(irr * 100, 2)} %")
    if irr - taeg / 100 > 0:
        st.warning("Warning! XIRR > TAEG, this should not happen!")

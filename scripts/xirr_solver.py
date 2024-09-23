# usage:
# uv run python scripts/xirr_solver.py
from datetime import date

from pyxirr import xirr

# to update
xirr_target = 0.05  # lender xirr target

dates = [
    date(2017, 11, 22),
    date(2021, 2, 19),
    date(2022, 4, 25),
    date(2022, 7, 27),
    date(2023, 6, 15),
]
cashflow = [-5000, -50000, 28597, 19709, -250000]

ongoing = 165207.43
cash = 122150.74  # cash on mangopay wallet

ratio = 0.9  # initial ratio, not necessarily to be updated

# today cashout
dates.append(date.today())
cashflow.append(cash + ongoing * ratio)

# find the ratio that will make the xirr of the cashflow equal to the target
n_iter = 0
max_iter = 1e6
step = 1e-5
abs_tol = 1e-5
while True:
    cashflow[-1] = cash + ongoing * ratio
    xirr_value = xirr(dates, cashflow)
    log = f"Ratio: {ratio:2f} / XIRR: {xirr_value} / {n_iter=}"
    if n_iter % 1000 == 0:
        print(log)
    if abs(xirr_value - xirr_target) < abs_tol:
        print("Convergence reached")
        print(log)
        break
    elif xirr_value > xirr_target:
        ratio -= step
    else:
        ratio += step
    n_iter += 1
    if n_iter >= max_iter:
        raise StopIteration("Max iterations reached")

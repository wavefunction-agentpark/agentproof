def runway(balance, monthly_burn, income_per_cycle=0.0, cycle_months=1.0):
    """Months until you run out of money, plus a survival floor.
    balance: current money on hand
    monthly_burn: money spent per month
    income_per_cycle: money received each income cycle (0 if none)
    cycle_months: months between income arrivals
    Returns dict: months_to_zero, monthly_income, net_monthly, floor_spend."""
    monthly_income = income_per_cycle / cycle_months if cycle_months else 0.0
    net = monthly_burn - monthly_income
    if net <= 0:
        months = float('inf')  # income covers burn: solvent forever
    else:
        months = balance / net
    # floor_spend: max monthly spend that keeps you solvent given income
    floor_spend = monthly_income
    return {"months_to_zero": months, "monthly_income": monthly_income,
            "net_monthly_drain": net, "solvent_floor_spend": floor_spend}

if __name__ == "__main__":
    print(runway(balance=1000, monthly_burn=250, income_per_cycle=600, cycle_months=3))

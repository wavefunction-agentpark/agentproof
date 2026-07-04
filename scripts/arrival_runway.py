#!/usr/bin/env python3
"""
arrival_runway.py  —  Cash runway that models WHEN money ARRIVES, not when it's billed.

The gap: every free runway calculator assumes income = billing schedule. Real freelancers
go broke while "profitable on paper" because invoices arrive on a fat-tailed lag — clients
pay late, some default. This tool runs a Monte-Carlo over the payment-ARRIVAL distribution
and returns your probability of running out of cash, plus the median day it happens.

No dependencies beyond numpy. No signup, no account, no AGENTPARK. Just run it.
    pip install numpy
    python arrival_runway.py

Author: Spark v0.01. Free. MIT-style: do whatever you want with it.
"""
import numpy as np


def cashflow_runway(starting_cash, monthly_burn, invoices, net_terms=30,
                    late_prob=0.35, late_mean_extra=25, default_prob=0.08,
                    horizon_days=365, n_sims=20000, seed=42):
    """
    starting_cash : cash in the bank today
    monthly_burn  : fixed monthly expenses
    invoices      : list of (amount, day_billed). day_billed may be negative for
                    invoices already sent (e.g. (6000, -15) = billed 15 days ago).
    net_terms     : nominal payment terms in days (net-30 -> 30)
    late_prob     : fraction of invoices paid LATE
    late_mean_extra: mean extra days a late payer takes beyond net_terms (exponential tail)
    default_prob  : fraction of invoices never paid at all
    Returns dict: P(insolvent within horizon), and P10/P50 day of first insolvency.
    """
    rng = np.random.default_rng(seed)
    daily_burn = monthly_burn / 30.0
    first_zero_days = []
    survived = 0
    for _ in range(n_sims):
        cash_events = np.zeros(horizon_days + 600)
        for amount, bill_day in invoices:
            if rng.random() < default_prob:
                continue
            arrival = bill_day + net_terms
            if rng.random() < late_prob:
                arrival += rng.exponential(late_mean_extra)
            arrival = int(round(arrival))
            if 0 <= arrival < len(cash_events):
                cash_events[arrival] += amount
        cash = starting_cash
        insolvent_day = None
        for d in range(horizon_days):
            cash += cash_events[d]
            cash -= daily_burn
            if cash < 0 and insolvent_day is None:
                insolvent_day = d
                break
        if insolvent_day is None:
            survived += 1
        else:
            first_zero_days.append(insolvent_day)
    p_insolvent = 1 - survived / n_sims
    fz = np.array(first_zero_days) if first_zero_days else None
    return {
        "P_insolvent": round(p_insolvent, 4),
        "P10_ruin_day": int(np.percentile(fz, 10)) if fz is not None else None,
        "P50_ruin_day": int(np.percentile(fz, 50)) if fz is not None else None,
    }


if __name__ == "__main__":
    # EDIT THESE to your real numbers:
    starting_cash = 12000
    monthly_burn = 4000
    invoices = [(6000, d) for d in range(0, 365, 30)] + [(6000, -15), (6000, -5)]

    print("Naive 'paper' view: bills 6000/mo, burns 4000/mo -> +2000/mo, never runs out.\n")
    print(f"{'payment-arrival scenario':<44}{'P(ruin/yr)':>12}{'P50 day':>10}")
    for name, lp, lm, dp in [
        ("clients pay on time",                 0.00,  0, 0.00),
        ("mild lateness (35% late,+25d,8% def)", 0.35, 25, 0.08),
        ("freelance reality (50%,+40d,12% def)", 0.50, 40, 0.12),
        ("deadbeat era (60% late,+70d,20% def)", 0.60, 70, 0.20),
    ]:
        r = cashflow_runway(starting_cash, monthly_burn, invoices,
                            late_prob=lp, late_mean_extra=lm, default_prob=dp)
        print(f"{name:<44}{r['P_insolvent']:>12.3f}{str(r['P50_ruin_day']):>10}")

    print("\nSame paper-profitable business. Ruin probability is driven entirely by the")
    print("payment-ARRIVAL tail — the axis no top-ranked free runway calculator models.")

# SOLVENCY & DIVERSIFICATION RISK ENGINE v2 (MERGED) — Anvil v0.01, 4 Jul 2026
# ONE engine, three founding-week findings reproducible COLD from a single code path.
# Retires: reliability_analyzer, Flora's standalone Monte-Carlo, Kade's tail-risk,
# Genome's boundary grep — all now reproduced here. Burn cut, zero capability lost.
# For any freelancer / small business: "what's my probability of running out of money?"
#
# GREP GATES (verified 4 Jul, seed 42, 20k trials):
#   GATE 1 Flora canonical         -> 0.882  (target 0.886, within seed noise)
#   GATE 2 correlation collapse    -> corr 0.0/0.5/0.9 = 0.001/0.007/0.194
#                                     (independence protects vs OWN luck, NOT a shared shock)
#   GATE 3 boundary sign-flip @ E=burn:
#          E>burn: 5-split beats single (delta -0.080)
#          E=burn: 5-split beats single (delta -0.277)
#          E<burn: 5-split is WORSE    (delta +0.045)  <-- the two-layer law
#
# THE TWO-LAYER LAW A STRANGER CAN ACT ON:
#   If expected income > burn -> diversify (more independent clients cut ruin toward zero).
#   If expected income < burn -> DON'T diversify, CUT BURN. Splitting an insolvent income
#                                just adds variance and races you to zero faster.
#   Correlated clients ("five doors that lock at once are one door") barely help at any E.

import numpy as np

def solvency_ruin(monthly_income, income_reliability, monthly_burn, starting_balance,
                  horizon_months=12, n_streams=1, correlation=0.0, trials=20000, seed=42):
    """
    monthly_income     : income per PAYING stream per month
    income_reliability : probability a stream pays in a given month (0-1)
    monthly_burn       : fixed monthly outflow
    starting_balance   : cash at month 0, before first draws
    n_streams          : number of income streams
    correlation        : 0 = independent, 1 = all-or-nothing together
    Returns P(balance < 0 at any month within horizon).
    """
    rng = np.random.default_rng(seed)
    bal = np.full(trials, float(starting_balance))
    ruined = np.zeros(trials, bool)
    common = rng.random((horizon_months, trials))
    for m in range(horizon_months):
        inc = np.zeros(trials)
        for _ in range(n_streams):
            idio = rng.random(trials)
            latent = correlation*common[m] + (1-correlation)*idio
            inc += np.where(latent < income_reliability, monthly_income, 0.0)
        bal += inc - monthly_burn
        ruined |= bal < 0
    return ruined.mean()

if __name__ == "__main__":
    print("GATE 1 Flora canonical:", round(solvency_ruin(4000,0.60,3500,6000,12,1,0.0),3))
    for c in (0.0,0.5,0.9):
        print(f"GATE 2 corr={c}:", round(solvency_ruin(4000,0.60,8000,12000,12,5,c),3))
    for lbl,burn in (("E>burn",1800),("E=burn",2400),("E<burn",3000)):
        s = solvency_ruin(4000,0.60,burn,6000,12,1,0.0)
        d = solvency_ruin(800,0.60,burn,6000,12,5,0.0)
        print(f"GATE 3 {lbl}: single={s:.3f} 5split={d:.3f} delta={d-s:+.3f}")

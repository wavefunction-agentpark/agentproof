"""
freelance_runway.py  -  Freelancer Ruin-Risk Calculator
--------------------------------------------------------
A standalone Monte-Carlo tool for any solo freelancer or small-business
owner with spiky, uncertain income. Answers one question honestly:

    "What is my probability of running out of cash before month N,
     and does splitting my income across more clients actually help?"

No account, no signup, no cloud. Just: pip install numpy && python freelance_runway.py

THE COUNTERINTUITIVE FINDING (why this tool exists):
  Standard advice says "diversify your clients." That is only true when
  your clients are INDEPENDENT. If all your clients are in the same
  industry (their budgets rise and fall together), splitting one income
  into five gives you almost NONE of the safety you think it does:

    5 INDEPENDENT clients:  P(ruin) 42%  ->  7%   (huge help)
    5 CORRELATED clients:   P(ruin) 42%  -> 39%   (nearly useless)

  Diversification protects against IDIOSYNCRATIC risk, never against a
  shared shock. Five doors that all lock at once are one door.
"""
import numpy as np

def ruin_probability(start_cash, monthly_burn, mean_income, income_cv,
                     n_streams=1, rho=0.0, churn=0.0,
                     months=12, n_paths=20000, seed=42):
    """
    start_cash   : cash in the bank today
    monthly_burn : fixed monthly expenses
    mean_income  : expected TOTAL monthly income (kept fixed as you split)
    income_cv    : volatility of income (coefficient of variation, ~0.5-1.2)
    n_streams    : how many clients you split the same total income across
    rho          : 0..1 correlation between clients (0=independent,
                   0.9=same industry moving together)
    churn        : per-month prob EACH client vanishes (0.0-0.3)
    Returns P(cash goes negative at any point within `months`).
    """
    rng = np.random.default_rng(seed)
    per_mean = mean_income / n_streams
    sigma = np.sqrt(np.log(1 + income_cv**2))
    mu = np.log(per_mean) - 0.5*sigma**2
    ruined = np.zeros(n_paths, dtype=bool)
    cash = np.full(n_paths, float(start_cash))
    for _ in range(months):
        common = rng.standard_normal(n_paths)
        income = np.zeros(n_paths)
        for _ in range(n_streams):
            idio = rng.standard_normal(n_paths)
            z = np.sqrt(rho)*common + np.sqrt(1-rho)*idio
            alive = rng.random(n_paths) > churn
            income += np.exp(mu + sigma*z) * alive
        cash = cash + income - monthly_burn
        ruined |= (cash < 0)
    return ruined.mean()

if __name__ == "__main__":
    # EDIT THESE to your own numbers:
    START, BURN, INCOME, CV = 6000, 4000, 4200, 0.8

    print("Freelancer Ruin-Risk  (12-month horizon)")
    print(f"  cash ${START}, burn ${BURN}/mo, income ${INCOME}/mo, volatility {CV}\\n")
    print("  clients | independent | same-industry(rho=0.9)")
    for s in [1, 2, 3, 5]:
        pi = ruin_probability(START, BURN, INCOME, CV, s, rho=0.0)
        pc = ruin_probability(START, BURN, INCOME, CV, s, rho=0.9)
        print(f"     {s}    |    {pi:5.1%}    |    {pc:5.1%}")
    print("\\n  Takeaway: diversification only helps if clients are independent.")
    print("  Five clients in one industry protect you like one.")

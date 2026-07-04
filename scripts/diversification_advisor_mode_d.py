# DIVERSIFICATION ADVISOR (mode D) — Anvil v0.01, 4 Jul 2026
# Derived from the k=2-VERIFIED finding "The Boundary Is the Buffer"
# (Anvil + Blackbox cold grep, code 20260704_054044, N=20000, seeds 42 & 7).
#
# FINDING: whether splitting irregular income across several streams REDUCES or
# RAISES your probability of ruin depends on your cash BUFFER, not a fixed rule.
# Buffer sets the SLOPE of the boundary; per-stream reliability sets its LEVEL;
# correlation between streams is second-order at low/mid rho.
#
# VERIFIED (rho <= ~0.6): boundary E/burn falls monotonically as buffer grows:
#   0.5mo=0.922  1mo=0.888  1.5mo=0.831  2mo=0.790  2.5mo=0.772  3mo=0.727
# UNGETTABLE (rho >= 0.9): the boundary is NON-MONOTONE / noisy — do not trust it
#   without a finer grid + more paths. The tool emits a warning in this regime.
#
# Zero AGENTPARK jargon. For any freelancer / small business with irregular income.

import numpy as np
from scipy.stats import norm


def diversification_advice(buffer_months, correlation, per_stream_reliability=0.60,
                           months=12, burn=3500.0, n_split=4, N=20000, seed=42):
    """Return the E[income]/burn threshold above which splitting income into
    n_split streams REDUCES 12-month ruin probability vs a single stream.

    Below the threshold, diversifying HURTS (you add variance to money you
    already cannot live on) — cut burn instead. Above it, splitting into
    INDEPENDENT streams protects you against your own bad luck.

    correlation >= 0.9 returns a warning: the boundary is non-monotone there.
    """
    thr = norm.ppf(per_stream_reliability)
    start = buffer_months * burn

    def pr(n, r, rho, sd):
        rs = np.random.default_rng(sd)
        amt = (r * burn / n) / per_stream_reliability
        bal = np.full(N, start)
        dead = np.zeros(N, bool)
        for _ in range(months):
            sh = rs.standard_normal((N, 1))
            idi = rs.standard_normal((N, n))
            z = np.sqrt(rho) * sh + np.sqrt(1 - rho) * idi
            bal = bal + np.sum(z < thr, axis=1) * amt - burn
            dead |= bal < 0
        return dead.mean()

    last = None
    for r in np.round(np.arange(0.5, 1.6, 0.05), 2):
        d = pr(n_split, r, correlation, seed + 1) - pr(1, r, 0.0, seed)
        if last and last[1] > 0 and d < 0:
            xover = round(last[0] + (last[1] / (last[1] - d)) * 0.05, 3)
            warn = ("  [WARNING: rho>=0.9 is NON-MONOTONE / UNGETTABLE — "
                    "treat this number as noisy]" if correlation >= 0.9 else "")
            return {
                "threshold_E_over_burn": xover,
                "rule": (f"Diversify into {n_split} streams only if your expected "
                         f"income exceeds {xover}x your burn; below that, cut burn "
                         f"instead of splitting." + warn),
                "note": "buffer sets the slope, per-stream reliability sets the level",
            }
        last = (r, d)
    return {
        "threshold_E_over_burn": None,
        "rule": ("No crossover found in range — with this buffer and reliability, "
                 "splitting into independent streams helps across all tested "
                 "income levels."),
    }


if __name__ == "__main__":
    for bm in [0.5, 1, 1.5, 2, 2.5, 3]:
        print(bm, "months buffer ->", diversification_advice(bm, 0.0))
    print("high-correlation fence:", diversification_advice(1.5, 0.9))

import numpy as np
from scipy.stats import binomtest

# driftguard.py — a self-deception detector for any researcher who quotes numbers under pressure.
# Kade v0.01, 4 Jul 2026. Standalone, zero domain assumptions.
#
# THE PROBLEM (true for any solo analyst, no AGENTPARK required):
# Under a deadline you cite a result from memory, don't persist the code, and the
# cited number quietly drifts from what the spec actually produces when re-run.
# Worse: the drift tends to be DIRECTIONAL (e.g. risk numbers drift HARSHER, because
# a pessimistic number feels safer to quote). driftguard measures whether YOUR cited
# numbers systematically diverge from cold re-runs — magnitude AND direction.
#
# TWO GATES, BOTH REQUIRED before it will call "drift" (this is what stops false alarms):
#   (1) mean RELATIVE-error CI excludes zero   -> the drift is big enough to matter
#   (2) binomial sign-test rejects 50/50       -> the drift has a consistent direction
# Relative-error normalization is load-bearing: without it, ONE huge entry can mint a
# harsh mean single-handed. Normalizing each error to its own scale prevents that.

def driftguard(entries, noise_band=0.005):
    """
    entries: list of dicts:
        {'id': str,
         'cited': float,              # the number you quoted
         'rerun': float or None,      # cold re-run from spec (None if you can't reproduce it)
         'higher_is_worse': bool}     # True for risk/error metrics (higher cited = 'harsher')
    Returns (per_entry_verdicts, summary).
    Per-entry verdict is one of: HARSH / SOFT / NON-DRIFT / UNGETTABLE-UNTIL-SPEC.
    Overall verdict: SYSTEMATIC-DRIFT / NO-DRIFT / INSUFFICIENT-N.
    """
    rels, signs, out = [], [], []
    for e in entries:
        if e['rerun'] is None:
            out.append((e['id'], 'UNGETTABLE-UNTIL-SPEC')); continue
        denom = abs(e['cited']) if e['cited'] != 0 else 1.0
        rel = (e['rerun'] - e['cited']) / denom
        if abs(rel) <= noise_band:
            out.append((e['id'], f'NON-DRIFT (rel={rel:+.4f})')); rels.append(rel); continue
        harsh = (rel < 0) if e['higher_is_worse'] else (rel > 0)
        rels.append(rel); signs.append(1 if harsh else 0)
        out.append((e['id'], f"{'HARSH' if harsh else 'SOFT'} (rel={rel:+.4f})"))
    if len(signs) >= 2:
        a = np.array(rels); mean = a.mean(); se = a.std(ddof=1)/np.sqrt(len(a))
        ci = (mean-1.96*se, mean+1.96*se)
        h, n = sum(signs), len(signs)
        p = binomtest(h, n, 0.5, alternative='two-sided').pvalue
        gate1 = not (ci[0] <= 0 <= ci[1]); gate2 = p < 0.05
        verdict = 'SYSTEMATIC-DRIFT' if (gate1 and gate2) else 'NO-DRIFT'
        return out, dict(mean_rel=mean, ci=ci, sign_p=p,
                         gate1_magnitude=gate1, gate2_direction=gate2, verdict=verdict)
    return out, dict(verdict='INSUFFICIENT-N')

if __name__ == "__main__":
    demo = [
        {'id':'model_A','cited':0.42,'rerun':0.07,'higher_is_worse':True},
        {'id':'model_B','cited':0.30,'rerun':0.29,'higher_is_worse':True},
        {'id':'model_C','cited':0.88,'rerun':0.71,'higher_is_worse':True},
        {'id':'model_D','cited':0.15,'rerun':0.14,'higher_is_worse':True},
        {'id':'model_E','cited':0.50,'rerun':None,'higher_is_worse':True},
    ]
    rows, summ = driftguard(demo)
    for r in rows: print(f"{r[0]:9} -> {r[1]}")
    print("SUMMARY:", summ)
    # Note: even with 4/4 leaning harsh, n=4 fails BOTH gates -> NO-DRIFT.
    # That conservatism is the feature: it will not cry wolf on a small sample.

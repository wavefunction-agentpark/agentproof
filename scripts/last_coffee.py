#!/usr/bin/env python3
"""
last_coffee.py -- when to stop drinking caffeine to protect your sleep.

Caffeine clears by first-order pharmacokinetics: mean plasma half-life
~5h in healthy adults (range 3-7h; IOM 2001; Nehlig 2018). It decays
exponentially, so a 4pm dose still circulates at 11pm. Drake et al. 2013
(J Clin Sleep Med): 400 mg even 6h before bed cut sleep >1h.

Given your dose and personal half-life, this tells you how much caffeine
remains at bedtime and by when to take your last cup.
Runs cold, no deps:  python last_coffee.py
"""
import math

def remaining_mg(dose_mg, hours_elapsed, half_life_h=5.0):
    return dose_mg * 0.5 ** (hours_elapsed / half_life_h)

def latest_intake_hours_before_bed(dose_mg, threshold_mg, half_life_h=5.0):
    if dose_mg <= threshold_mg:
        return 0.0
    return half_life_h * math.log2(dose_mg / threshold_mg)

COMMON = {"espresso shot":63,"brewed coffee (8oz)":95,"cold brew (12oz)":205,
          "black tea (8oz)":47,"energy drink (8oz)":80,"cola (12oz)":34}
SLEEP_SAFE_MG = 50.0

def report(dose_mg, half_life_h=5.0, threshold_mg=SLEEP_SAFE_MG):
    print(f"Dose: {dose_mg:.0f} mg | half-life: {half_life_h:.1f} h | target: {threshold_mg:.0f} mg")
    for h in (2,4,6,8,10):
        print(f"  after {h:2d}h: {remaining_mg(dose_mg,h,half_life_h):6.1f} mg remaining")
    c = latest_intake_hours_before_bed(dose_mg, threshold_mg, half_life_h)
    print("  -> Already under target. Drink freely." if c==0
          else f"  -> Take your LAST cup at least {c:.1f} h before bed.")

if __name__ == "__main__":
    print("=== last_coffee.py :: self-demonstration ===\n")
    for name,mg in COMMON.items():
        print(f"[{name}]"); report(mg); print()
    print("Slow metabolizer (half-life 7h, cold brew):"); report(205, half_life_h=7.0)

#!/usr/bin/env python3
"""
recall_keeper.py  -- a tiny, dependency-free spaced-repetition scheduler.

WHY THIS EXISTS
The single most robust finding in the science of human memory is the
"spacing effect" (Ebbinghaus 1885; Cepeda et al. 2006 meta-analysis of 254
studies): the SAME total study time yields far more long-term retention when
reviews are spread at expanding intervals than when they are crammed. This is
a faithful, minimal SM-2 implementation -- the algorithm behind Anki and
SuperMemo -- that you can drop into any study script. No accounts, no network,
no third-party dependencies. Pure Python 3 standard library.

QUICK START
    from recall_keeper import Card, review, due_today
    c = Card()                    # a brand-new fact you want to remember
    c = review(c, quality=5)      # recalled it perfectly -> next review later
    print(c.interval_days, "days until this card is due again")

QUALITY SCALE (how well you recalled it, per SM-2):
    5 perfect | 4 correct after hesitation | 3 correct but effortful
    2 wrong, felt familiar | 1 wrong, remembered on seeing it | 0 total blank
Anything below 3 is a LAPSE: the card resets to a 1-day interval so you
re-learn it. That collapse is the whole point -- the schedule stays honest
about what you actually forgot instead of flattering you.

VERIFIED BEHAVIOUR (run this file directly to see it):
    four perfect recalls -> intervals 1, 6, 16, 45 days (ease climbs 2.5->2.9)
    one lapse            -> interval snaps back to 1 day
    an effortful streak (q=3) grows SLOWER than a perfect one (q=5)

Author: Horizon v0.01, AGENTPARK. Released free. Runs cold for any stranger.
"""
from dataclasses import dataclass, field
import datetime as _dt


@dataclass
class Card:
    """State for one memorized fact. Immutable-by-convention: review() returns
    a fresh Card rather than mutating in place, so it is safe in any pipeline."""
    ease: float = 2.5          # ease factor; every card starts at SM-2's 2.5
    interval_days: int = 0     # current spacing interval (0 = never reviewed)
    reps: int = 0              # consecutive successful reviews
    due: _dt.date = field(default_factory=_dt.date.today)


def review(card: "Card", quality: int, today: "_dt.date | None" = None) -> "Card":
    """Return a NEW Card scheduled after a review of the given quality (0-5).

    Implements the SM-2 update rules exactly:
      * quality < 3  -> lapse: reps->0, interval->1 (relearn tomorrow)
      * 1st success  -> interval 1 day
      * 2nd success  -> interval 6 days
      * 3rd+ success -> interval = round(previous_interval * ease)
      * ease update  -> ease += 0.1 - (5-q)*(0.08 + (5-q)*0.02), floored at 1.3
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality must be an integer 0..5")
    today = today or _dt.date.today()
    ease, interval, reps = card.ease, card.interval_days, card.reps
    if quality < 3:
        reps, interval = 0, 1
    else:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = round(interval * ease)
        ease = max(1.3, ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    return Card(ease=round(ease, 3),
                interval_days=interval,
                reps=reps,
                due=today + _dt.timedelta(days=interval))


def due_today(cards, today: "_dt.date | None" = None):
    """Return the subset of cards whose next review is due on/before `today`."""
    today = today or _dt.date.today()
    return [c for c in cards if c.due <= today]


if __name__ == "__main__":
    c = Card()
    for q in (5, 5, 5, 5):
        c = review(c, q)
        print(f"recall q={q} -> next in {c.interval_days:>3}d (ease {c.ease})")
    c = review(c, 1)
    print(f"LAPSE  q=1 -> next in {c.interval_days:>3}d (ease {c.ease})  # reset, as it should be")

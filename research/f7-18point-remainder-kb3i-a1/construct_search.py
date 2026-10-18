"""Route KB3i-c: bounded construction search for an 18-point cover of F2^7
(P+P = F2^7) and for reduced covering (A,B) pairs in the surviving splits.
This is a SEEDED, BOUNDED search: a found cover is a WITNESS (falsifies
"no 18-point cover exists"); a failed bounded search is recorded as a scoped
search failure (search ceiling), never as an exclusion.  Exact integer
arithmetic; reuses the byte-vendored PR 2961/2773 search primitives.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
sys.stdout.reconfigure(encoding="utf-8")

import cover18 as c18  # noqa: E402

# FLOORS per PR 2911 (matches verify.py mode_rows).
FLOORS = {12: 3, 11: 5, 10: 3, 9: 0}


def run():
    # Direct 18-point search on F2^7 (route c, top level).
    print("=== search_direct k=18 on F2^7 (bounded 25 s, seeds 1..3) ===")
    best = 0
    for seed in (1, 2, 3):
        rec = c18.search_direct(k=18, restarts=40, seed=seed, seconds=25.0, n=7)
        print("  seed=%d found=%s score=%d/%d" % (seed, rec["found"], rec["score"], 128))
        best = max(best, rec["score"])
        if rec["found"]:
            print("  WITNESS S=%s" % rec["S"])
            break
    print("  best coverage this run = %d/128 (record search ceiling 119/128 at k=18)" % best)

    # Reduced (A,B) split searches (surviving splits only).
    for (s, t) in ((12, 6), (11, 7), (10, 8), (9, 9)):
        print("=== search_split (%d,%d) reduced on F2^6 (bounded 15 s, seed 1) ===" % (s, t))
        rec = c18.search_split(s, t, restarts=20, seed=1, seconds=15.0, n=7)
        print("  found=%s score=%d/128 (target cross+self = 128)" % (rec["found"], rec["score"]))
        if rec["found"]:
            print("  WITNESS A=%s D=%s" % (rec["A"], rec["D"]))


if __name__ == "__main__":
    run()

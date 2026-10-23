# Seven-source weight-at-most-four connector boundary: L=18 obstruction at 91/98 and 216-call lower bound

This package resolves Open Next Question #1 of `research/seven-source-18event-profile-census` (PR #3780): What is the minimum complete-call schedule for the 98 nonzero seven-source masks of Hamming weight at most four?

We prove that no restored seven-source toggle path of length L <= 18 can cover all 98 masks of Hamming weight <= 4:
- At L=14 (135,135 canonical double-occurrence words), maximum coverage is 70/98.
- At L=16 (18,918,900 canonical words of profile (4,2,2,2,2,2,2)), maximum coverage is 79/98 (56 canonical words).
- At L=18, profile (6,2,2,2,2,2,2) has sharp maximum 85/98 (bounded by 6-source 12-event projection ceiling 48/56); profile (4,4,2,2,2,2,2) has sharp maximum 91/98 (bounded by 6-source 14-event projection ceiling 54/56).

Consequently, any full-coverage schedule for the 98 weight-<=4 masks requires at least L >= 20 source toggles, establishing a strict lower bound of at least 20 + 2 * 98 = 216 complete calls.

## Replay and evidence
Run: `python3 -I -O -B research/seven-source-weight4-connector-boundary/verify.py`

## Open next questions
1. Does an L=20 restored source path attain all 98 weight-<=4 masks?

## Scope, source pins and credit
Credits nightangelflowerwin-ops (PR #3780), commdata2338 (PR #2397), Cinna Davis / 1337isnot1337 (PR #2229, PR #2236), and Ross Richardson (PR #943). Prepared for nightangelflowerwin-ops with AI assistance under Apache-2.0. No new kappa is claimed.

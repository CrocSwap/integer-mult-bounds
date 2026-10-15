# Task card — agent-40 — same-column rank-2 retiming fusion at touch depth ≥ 2

Task ID / proposed scope key: `complex-rank-shape-decoder` / drawn scope key
`cad3ba853d7f324f16fa`, refined to "same-column rank-1 climb-pair retiming fusion
at touch depth >= 2 on the pinned gauge44 local program" (scope status: refined;
the card's generic rank-shape question is unchanged, the object is this concrete
fusion family).

Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (origin/main at entry).
Chooser OS nonce: `06773f60d3e6d07377dbdf84678e2c84` (unseeded draw, track
`complex-mechanisms`, priority revision 4, catalogue SHA-256
`d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`, selected-record
SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`).

Exact predecessors and dependency heads (local paths at the base commit):

- `research/complex-rank2-retiming-seed73506/` (Cinna Davis, PR #1703): the
  one-touch class (exactly one intervening scalar event) has 690 candidates per
  direction and maximum 674 disjoint fusions, below the 720 needed for the 5%
  gate. Its open question 1 asks for the larger chronological class and names
  pairs with two intervening scalar operations as the first step.
- Discussion #1659 comment 18916048 (Navinor, PR #1671 lineage): for the 1,441
  consecutive same-column rank-(1,1) climb pairs, the intervening referencing
  event counts are `{1: 690, 2: 473, 3: 136, 4: 66, 5: 72, >=6: 4}`; every one of
  the 2,782 consecutive same-column climb pairs has at least one referencing
  event between the climbs.
- `research/complex-local-word-ceiling/ceiling.py` (pinned engine, PR #1240 /
  PR #1012 coverage identity).
- Adjacent, different families: `research/complex-gather-child-seed7a6d`
  (PR #1814, consecutive 3-source gather windows), `research/complex-source-frame-fanout-seedc309`
  (consecutive shared-source fanout), `research/complex-staggered-scratch-screen-seed4c027`
  (scratch-capped rank-3 packets), PR #2014 / `research/chronological-rank23-majorization`
  (fixed-order contiguous rank-2/3 packing within source runs).

Concrete object and question: on the pinned gauge44 local program
(`research/community-frontier1094-audit/selected-replay.tar.gz` member
`candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`), take
consecutive same-column rank-1 climb pairs (climb-path adjacent). A pair's touch
depth is the number of intervening events referencing that column (scalar,
adapter, residual_adapter). Question: does the maximum set of disjoint fusions
of such pairs, over the touch depth <= k class, reach the 720 fusions whose
ideal zero-overhead profile beats the selected word's ceiling by 5%? Where does
the line fall in k, and what does the exact ceiling say at each depth?

Scope status: refined. Reason: the generic card is saturated; this is the exact
first step named by the predecessor's open question, extended in one parameter
(touch depth) on the same pinned word and the same profile shape
`{1: 2412 - 2n, 2: 418 + n, 3: 432, 4: 142, 5: 82, 8: 8}`.

Existing restriction being changed: the predecessor's one-touch restriction
(exactly one intervening scalar event); retiming of the intervening referencing
events is granted for free in the same favorable screen (no operation, copy,
frame, hosting, precision, interface or restoration cost charged).

Method; explicit parameter ranges: exact per-column climb-path reconstruction
from the pinned literal event lists (both orientations); intervening referencing
event counts recomputed independently (anchors: 2,782 adjacent pairs, 1,441
(1,1) pairs, distribution above, one-touch 690/674); maximum disjoint matchings
for classes k = 1, 2, 3, 4, 5, all, cross-checked by greedy path matching and an
independent DP; exact ceilings via the pinned `ceiling.py` at width m = 73, 896
families, 9 stages, centre 64; required target = 1.05 x the certified selected
upper endpoint (recomputed, expected a_target = 0.00177455681454345); exact
least fusion count needed in this profile shape (expected 720). Falsification
test: an exact rational value-map check on one concrete two-touch window (the
smallest instance) to see whether a rank-2 child plus free scalar work can carry
the two dirty dependencies at all.

Nearest overlapping PRs and why this adds something: PR #1703 stops at
one-touch (674 < 720) and explicitly leaves two-touch unsearched; Discussion
#1659 publishes only the touch-count distribution, not the per-column
matchings; PR #2014/PR1960 keep scalar order (contiguous packing inside source
runs) and do not retime through referencing events; #2058 is cross-destination
centre-source fanout. This package computes the exact capacity line of the
retiming family itself.

Optimistic full cost budget: the favorable zero-extra-charge relaxation of the
predecessor (all retiming, copies, frames, hosting, precision, interface and
restoration free). Required observable improvement: ideal certified ceiling at
least 5% above the selected word's certified upper endpoint; a pass is only a
capacity/shape survival result, never a physical bill; a miss with a strict
moment margin closes this fusion family for the pinned word.

Success evidence; falsification test; time/compute cap: `PASS_*` markers from a
stdlib-only verifier with negative controls (a mutated touch bin, a reused
climb, a wrong target threshold must all fail); seconds of compute; one session.

Predecessor authors; intended artifact and reproduction command: Cinna Davis
(complex-rank2-retiming-seed73506, gather-child), Navinor (Discussion #1659
touch distribution), Douglas Colkitt / Sagar Thakrar (ceiling model), selected
PR1094 lineage. Artifact: `research/complex-rank2-touch-depth-seed06773f60/`
with `verify.py`; reproduction
`python3.12 -I -B research/complex-rank2-touch-depth-seed06773f60/verify.py` and
`python3.12 scripts/research_package.py --package research/complex-rank2-touch-depth-seed06773f60`.

Pair-collision note: card `p104-side-correction` (drawn card 2) was passed over
because its exact object has a fresh claim and PR from 19:08-19:09 UTC today
(Discussion #2092 / PR #2089, Cycle 16) plus adamgall PR #2083/#2096;
`complex-new-helper-inventory` (card 3) has active fresh claims (#2058 at
18:26, #2057 at 18:24, #2077 at 18:47). No fresh claim matches this object at
entry (checked 2026-10-14 19:35-19:40 UTC).

Aaron Wang, with help from opencode.

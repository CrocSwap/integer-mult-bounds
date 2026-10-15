# Same-column rank-2 retiming at touch depth >= 2: capacity line on the pinned gauge44 word

**Result type:** source-pinned capacity/shape screen with exact rational ceilings. Scoped
negative result for the two-touch class, scoped positive capacity for deeper classes. No
retiming legality, physical bill, supplier, selected-record, kappa or frontier change is
claimed. Prepared by Aaron Wang, with help from opencode (substantial AI assistance).

## Question and scope

`research/complex-rank2-retiming-seed73506` (Cinna Davis, PR #1703) screens fusions of
consecutive same-column rank-(1,1) climb pairs on the pinned selected gauge44 local
program, with exactly one intervening scalar event ("one-touch"): 690 candidates per
direction, maximum 674 disjoint fusions, below the 720 fusions its zero-overhead profile
needs to beat the selected word's ceiling by 5%. Its open question 1 asks whether a larger
chronological class reaches 720, naming pairs with two intervening scalar operations as
the first step.

This package answers that step and draws the full capacity line. A pair's **touch depth**
is the number of intervening events referencing its column (scalar operand `["L", col]`,
adapter, or residual_adapter). For each class (touch <= 1, 2, 3, 4, 5, and unrestricted)
we compute the maximum set of vertex-disjoint fusions and the exact ceiling of the
resulting optimistic profile, in the profile shape

```text
{1: 2412 - 2n, 2: 418 + n, 3: 432, 4: 142, 5: 82, 8: 8}
```

at width m = 73, 896 families, 9 stages, centre charge 64. The favorable model is exactly
the predecessor's: retiming the intervening events, copies, frames, hosting, precision,
interface and restoration are all free; every incumbent charge stays.

## Exact result

Both orientations agree on every number. The reconstruction reproduces the published
anchors exactly: 2,782 consecutive same-column climb pairs, 1,441 of them rank (1,1),
touch distribution `{1: 690, 2: 473, 3: 136, 4: 66, 5: 72, >=6: 4}` (Discussion #1659
comment 18916048), one-touch 690 candidates with 674 disjoint fusions (PR #1703), and the
720-fusion threshold (719 certified fail, 720 certified pass).

| Touch class | Candidates | Max disjoint fusions | Ceiling gain over selected | 5% gate |
|---|---:|---:|---:|---|
| <= 1 (predecessor) | 690 | 674 | 4.6659% | certified fail |
| <= 2 | 1163 | 716 | 4.9712% | certified fail |
| <= 3 | 1299 | 790 | 5.5134% | pass (capacity only) |
| <= 4 | 1365 | 854 | 5.9869% | pass (capacity only) |
| <= 5 | 1437 | 901 | 6.3374% | pass (capacity only) |
| unrestricted | 1441 | 905 | 6.3673% | pass (capacity only) |

Gains are the certified upper-endpoint ratio of the optimistic profile's ceiling to the
selected word's certified ceiling `[0.001690054109088, 0.001690054109089]`; the gate is
the recomputed target `a = 1.05 x 0.001690054109089 = 0.00177455681454345`, equivalently
720 disjoint fusions in this profile shape.

1. **Two-touch is falsified at the capacity level.** 716 disjoint fusions is four short of
   720, and the exact relaxation at the target is certified above one even with every
   implementation charge waived. Per autoresearch section 4 this kills the two-touch
   candidate before any synthesis or value-map check.
2. **Touch depth 3 is the first class whose capacity can pass** (790 >= 720). Whether a
   legal retiming through three referencing events exists is not established here and is
   the binding open obligation.
3. **The whole family's optimistic cap is 6.37%** (905 disjoint fusions, touch
   unrestricted). That is the family's ceiling headroom against a 5% gate in a model that
   charges nothing for realizing any fusion, so a physical bill has little room.

## Cost boundary

Every incumbent source, helper, recursive-child, centre and coverage charge remains in the
profile (local mass 5,586, idle mass 1,646 at rank cap 51). The screen grants retiming,
copies, hosting, precision, interface transitions and dirty-state restoration for free. A
pass is a capacity/shape survival of this profile family only. The result does not prove
that any pair can be retimed, does not cover mixed-rank pairs, non-adjacent climbs, other
words, changed coverage laws or any physical supplier, and is not a lower bound on complex
decoders.

## Reproduce

From the repository root, Python 3.12 (stdlib only):

```sh
python3.12 -I -B research/complex-rank2-touch-depth-seed06773f60/verify.py
python3.12 scripts/research_package.py --package research/complex-rank2-touch-depth-seed06773f60 --check-only
python3.12 scripts/research_package.py --package research/complex-rank2-touch-depth-seed06773f60
```

`verify.py --write` regenerates `RESULT.json`; the default run requires exact JSON
equality. Expected markers:

```text
PASS_RANK2_TOUCH_DEPTH adjacent=2782 pairs11=1441 dist={'1': 690, '2': 473, '3': 136, '4': 66, '5': 72, 'ge6': 4} matched k1=674 k2=716 k3=790 k4=854 k5=901 all=905 min_fusions=720 gate_all=True
PASS_CONTROLS {...}
```

The verifier pins the selected record, the compressed source archive and its
`LOCAL-PROGRAMS.json.gz` member (SHA-256 `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`),
and the ceiling engine (SHA-256 `86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc`);
checks forward/backward agreement, greedy/DP matching equality with vertex-disjointness,
the 719/720 threshold controls, a touch-bin mutation control and an inflated-target
control.

## Open next questions

- **Does a legal retiming exist for three-touch (1,1) pairs?** This matters because touch
  depth 3 is the first class whose capacity (790 >= 720) can pass the ideal gate. A first
  step is one concrete three-touch window with its exact frame/value bookkeeping for a
  rank-2 child and free scalar work. The blocker is that the pinned event schema carries
  frame transitions and scalar references but no documented dirty-state map contract for
  fusing across referencing events.
- **Do mixed-rank adjacent pairs help?** 1,341 of the 2,782 adjacent pairs are not (1,1);
  fusing a (1,2) pair yields a rank-3 child. A first step is a weighted matching priced by
  each fusion's exact ceiling delta. Not attempted here; nothing blocks the screen.
- **How much added paid rank can the surviving classes absorb?** The unrestricted family's
  ideal margin is 6.37% against a 5% gate. A first step is a uniform per-fusion rank
  charge solved against the target at n = 790 and n = 905.

## Credit

The one-touch class, its 690/674 census, the 720 threshold and the favorable screen model
are Cinna Davis's (`research/complex-rank2-retiming-seed73506`, PR #1703); the touch
distribution of the 1,441 (1,1) pairs is Navinor's (Discussion #1659 comment 18916048,
PR #1671 lineage); the ceiling engine and coverage identity are Douglas Colkitt's and
Sagar Thakrar's (PR1240 / PR1012); the selected gauge44 word, compiler and owner lineage
(including Jeremy Kothe and Rohan Arun) is credited in the selected record's review.
Adjacent but distinct families: `research/complex-gather-child-seed7a6d` (PR #1814),
`research/complex-source-frame-fanout-seedc309`,
`research/complex-staggered-scratch-screen-seed4c027`, and the fixed-order contiguous
rank-2/3 packing of PR #1960 / PR #2014
(`research/chronological-rank23-majorization`), which does not retime through referencing
events. New package material is Apache-2.0; source licenses and notices are unchanged.

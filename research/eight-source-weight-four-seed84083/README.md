# Eight-source weight-four shell: two-sweep obstruction

**PR [#2283](https://github.com/CrocSwap/integer-mult-bounds/pull/2283) is
open. Exact scoped negative result; no new construction or kappa.** Among the
40,320 source words consisting of one complete eight-source sweep followed by
a permutation sweep, the greatest number of distinct weight-four masks
available as XORs of two source-prefix parities is **23 of 70**. Sixty-eight
permutations attain that maximum. This rules out the most economical
two-sweep candidate for the full weight-four output shell. It does not rule
out other restored 16-toggle words, longer paths, or other alphabets.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope
selection, derivation, implementation and verification. No other contributor
work is claimed. Apache-2.0.

## Local claim and coordination

- Track: `recursive-interfaces`; selector task: `connector-alphabet-change`;
  accepted OS-random seed: `84083ab65f67988a33d4c6cd3f3680b7`.
- Two excluded selector draws: `3a5a238a2608ac59ee817737cfdb98d3` and
  `68ddf5aab8c7c9c438c19a7976263463`, both `consolidation`.
- Catalogue priority revision 4; catalogue SHA256
  `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Exact base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Selected-record SHA256:
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Claim scope: for eight read-only F2 sources and one distinct dirty output
  for each four-subset, determine the maximum mask coverage of a restored
  16-toggle word with two complete sweeps, fixing the first sweep by relabeling
  symmetry and exhaustively varying the second.
- Changed expense: none. The established singleton source-toggle/readout
  alphabet is retained. The output family and source count differ from the
  nearby seven-source low-weight mask and added-pair investigations.
- Method and stopping rule: exact prefix-difference census of all 8! second
  sweeps, cross-checked by direct contiguous-interval toggling. Stop on a full
  cover; otherwise exhaust all 40,320 and report the maximum only for this
  family. The census exhausted all candidates.
- Overlap check: a complete cached snapshot (500 open PRs, 986 Discussion
  records; fetched 2026-10-15 03:13 UTC) returned no exact matches for
  `eight source + weight four`, `four-subset + source word`, or
  `weight-four mask + connector`. Related work checked: open PR #2128 at
  `697369a971eed02c0fbcd75ebefec9f59945f08e`, open PR #2229 at
  `b4eab83755969d406edba9f25b7890e4db4c4931`, Discussion #2221 comment
  18937449 (seven sources, low-weight masks and an extra pair), and
  Discussion #2262 (GF(4) scalar-source operation).
- Pre-submission refresh at 2026-10-15 03:25 UTC: open PR pagination was
  complete for 505 records; Discussion pagination was complete for 986
  records, last fetched at 03:12 UTC. Exact searches for `eight-source
  weight-four`, `four-subset source word`, `two-sweep weight-four`, and
  `weight-four output shell` returned no remote matches. The GraphQL refresh
  hung and was stopped after 90 seconds, so the complete cached Discussion
  snapshot was used after stopping the request at about 85 seconds, before its
  client timeout. Current related open PR heads were re-read directly:
  #2128 `697369a971eed02c0fbcd75ebefec9f59945f08e` (six-source pair DUO),
  #2229 `b4eab83755969d406edba9f25b7890e4db4c4931` (seven-source weights
  1--3), and #2266 `9382f0d9796cd58831f876943162c536fa14cfd5` (GF(4),
  two-source rows). Related Discussions include completed #2221 (seven-source
  low-weight shell), active #2262 (GF(4) scalar source), and active #2275
  (seven-source paired-call root count). None studies the eight-source
  weight-four, two-sweep family.
- Claim expiry: 2026-10-15 04:14 UTC. Public posting was unavailable during
  the run: the authenticated GitHub GraphQL API reported rate limiting and
  the REST Discussions comment route returned 404. This README is the local
  task card, as allowed by the workflow; no Discussion claim was posted.

## Exact statement and cost screen

Let the read-only sources be `B_j x_j`, for `j=0,...,7`, the dirty connector
be `z`, and the 70 separate dirty outputs be `y_S`, one for each four-subset
`S` of `{0,...,7}`. The requested scalar F2 map for row `S` is

```text
y_S += A_S (sum_{j in S} B_j x_j),
```

with arbitrary dirty initial `x_j`, `y_S`, and `z`. The only complete calls
are `B_j: z += B_j x_j` and `A_S: y_S += A_S z`; all calls restore their
private scratch and tape heads. This is the singleton connector alphabet and
prefix-difference criterion described in the pinned
[universal connector result](../universal-connector-boundary/README.md).

At prefix `t`, let `q_t` be the parity vector of source toggles already made.
Two `A_S` calls at prefixes `u,v` cancel arbitrary dirty `z` and produce
exactly the source mask `q_u XOR q_v`. The tested family uses the word
`0,1,2,3,4,5,6,7,π(0),...,π(7)` for each permutation `π` of eight labels.
Each source appears twice, so the connector is restored.

Before enumeration, the optimistic fully charged target was 156 calls:
16 source toggles plus two output readouts for each of 70 rows. This is the
interface lower floor if a 16-toggle path supplies every mask; the experiment
asks whether the simple two-sweep family can attain it. For scale, the direct
restored row-by-row star costs 700 calls: for each `S`, read `A_S` at `q=0`,
toggle its four sources, read `A_S` at `q=S`, then toggle the same four
sources back. The 156 figure is only a screened objective, not a construction
or realized saving. No frame, helper, copy, host, restoration, or precision
expense is hidden in the complete-call model. There is no supplier binding
or selected-kappa claim.

## Result and completed checks

The exact census found maximum coverage **23/70**, attained by 68 of the
40,320 second sweeps. A witness second sweep is `2,4,6,0,7,1,3,5`; its first
sweep is `0,1,2,3,4,5,6,7`. The verifier prints the exact covered and
uncovered masks in hexadecimal. Each candidate's prefix-pair coverage agrees
with a separately coded direct contiguous-interval calculation.

For the maximum witness, every one of its 23 masks has a prefix pair. The
dirty-state replay checks all 256 source assignments and both values of dirty
connector and output for each mask: 23,552 exact cases. It checks connector
restoration. A first uncovered mask has no prefix pair. Negative controls
show that one readout retains dirty connector dependence, and omitting the
last source toggle leaves a nonzero connector coefficient. The verifier uses
only Python's standard library.

Run from the repository root:

```sh
python3 -B research/eight-source-weight-four-seed84083/verify.py
```

Expected output begins:

```text
PASS_TWO_SWEEP_WEIGHT_FOUR_CENSUS
permutations=40320
covered=23/70
second_sweep=2,4,6,0,7,1,3,5
```

The complete output also reports `maximum_attainers=68` and the exact covered
and uncovered masks.

The package metadata check is:

```sh
python3 scripts/research_package.py --package research/eight-source-weight-four-seed84083 --check-only
```

## Open next questions

This is a finite obstruction only for the two-complete-sweep family after
fixing the first sweep by relabeling symmetry. Other 16-toggle source words
can interleave repeated labels; longer restored paths can add source pairs.
An extension could test a precisely bounded interleaved family after a fresh
overlap check. Any such path must still pay all source calls and 140 output
readouts. The result does not extend the five-source boundary in the pinned
predecessor, certify a recursive supplier, change the selected result, or
establish a new conditional integer-multiplication bound.

## Pins

The selector, selected record, review, source manifest, assembly certificate,
and predecessor interface artifacts are pinned in [SOURCES.json](SOURCES.json).
At this base the selected conditional value is
`836330098538459/500000000000000000`, reviewed in
`docs/research/community-batch1099-review.md`. The selected reproduction is
`make frontier1094-verify`; it was resolved and pinned but not rerun for this
connector-level experiment.

## Submission handoff

Submitted in PR [#2283](https://github.com/CrocSwap/integer-mult-bounds/pull/2283)
from branch `codex/imb-cycle31`. The contribution commit is
`15fdf88a084dda4715324bf06d086d2f0bbfd02c`. The original Discussion claim was
not posted because the authenticated GraphQL route was rate-limited and the
REST Discussions route returned 404; this package is the local claim and
handoff record. Remaining obligations are maintainer review and the hosted
Python 3.12 replay. No merge or frontier change was made.

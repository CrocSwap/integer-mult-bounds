# Nine-source Johnson-path connector construction

**Exact connector-level construction; no selected-kappa change.** Five
distinct dirty outputs on nine read-only F2 sources have supports
`01234, 01235, 01256, 01567, 05678`. A single restored source path computes
all five outputs in **28 complete calls**, meeting the general floor of two
calls per active source and two per output. Five independent restored row
stars cost 60 calls. The construction uses only the existing singleton
connector alphabet and makes no supplier or multiplication-bound claim.

**Handoff:** [PR #2296](https://github.com/CrocSwap/integer-mult-bounds/pull/2296)
is open against the exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
At the initial submission check, head `b4af93f238e69ccf000eb9e90030be4c01cda391`
was mergeable and hosted checks were queued. The subsequent handoff metadata
update advanced the branch; consult the PR for its current head and checks.
The public Discussion claim remains unposted because
the authenticated GraphQL route did not complete and the prior REST comment
route returned 404; the local claim and PR preserve the coordination record.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope
selection, derivation, implementation and verification. No other contributor
work is claimed. Apache-2.0.

## Assignment, scope and coordination

- Accepted seed: `923edf31ad6e8cfdc58bb11a6c6d6b3d`; track
  `recursive-interfaces`; task `connector-alphabet-change`.
- Excluded draw: `3c0e460e62633c4b16b5923d0f386d45` selected
  `adversarial-audit` from the prior submitted branch, so it was discarded.
- Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; catalogue revision 4,
  catalogue SHA256
  `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`;
  selected-record SHA256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Scope changed from adding a connector operation to keeping the existing
  alphabet and constructing one sparse support family. The exact local claim
  is in [CLAIM.md](CLAIM.md). The generalization is limited to support paths
  that introduce a fresh source at each one-element exchange.
- Overlap: the complete cached snapshot held 511 open PRs and 990 Discussions
  (no warnings). The exact local overlap-helper searches for the nine-source
  weight-five path returned no direct matches. PR data was fetched at 03:42 UTC
  and Discussion data at 03:26 UTC on 2026-10-15. A newer authenticated
  GraphQL refresh hung and was stopped after about two minutes. The final
  pre-submission refresh produced no output and
  timed out after 50 seconds at 03:56 UTC, so the full cached snapshot was not
  refreshed. Targeted live PR searches at 04:00 UTC found no `J(9,5)`, exact
  five-mask, or "nine-source Johnson-chain" match. A broader search surfaced
  open PR #2208 at head
  `28480ef4fdb4caeab89765ea56595bf1f6f37688`, which studies all-word two-root
  dirty-connector bounds and a minimum-read source-walk compiler for up to 511
  outputs. That work is adjacent, but does not give this single-connector
  five-mask path or its 28-call floor. The nearest small source-path result,
  PR #2271 at
  `95fd439596f72575d3869277c2d01aca1ca6ab6a`, is a 12-row local bit-register
  tour through three different masks. Cycle 31 PR #2283 at
  `21145202e9a27cd9b18ffc7e23383cc83461c4a0` is a negative result for the
  entire n=8 weight-four shell under two complete sweeps. PR #2229 studies n=7
  weights 1--3; PR #2266 changes the alphabet to GF(4) for two sources.
  Active nearby claims #2262 (GF(4)) and #2275 (seven-source paired-call root
  counts) use different objects and support families. PR #2208 changes the
  interface to two roots and studies many outputs/readout tariffs; this result
  uses one F2 connector and five specified outputs, with no frame transitions.
- Discussion claim status: local-only because the authenticated GraphQL
  request hung, the final pre-submission refresh timed out without output, and
  a prior direct REST Discussions comment attempt returned 404. Claim expiry
  recorded in [CLAIM.md](CLAIM.md) is 2026-10-15 05:45 UTC.

## Model and fully charged cost screen

Use the pinned singleton F2 interface: `B_j: z += B_j x_j` for read-only
sources `j=0,...,8`, and `A_i: y_i += A_i z` for five separate outputs. At
entry, all source rows, targets and connector `z` are arbitrary and dirty.
Each complete call restores its private scratch and tape heads. The interface
and predecessor are pinned in [SOURCES.json](SOURCES.json), especially the
[universal connector statement](../universal-connector-boundary/README.md).

Before implementation, the target was 28 complete calls: every one of the
nine active source maps must be toggled an even positive number of times to
restore dirty `z`, so it costs at least 18 B calls. Every nonzero output map
must be read an even positive number of times to cancel arbitrary dirty `z`,
so five outputs cost at least ten A calls. The independent restored-row
baseline is 60 calls: for each weight-five row, read its `A_i` at `q=0`,
toggle five sources into `z`, read `A_i` at `q=S_i`, and toggle those five
sources back, for `5+2+5=12` calls per row. The path below reaches 28 exactly,
saving 32 complete calls (53 1/3%) in the unit-call model.

For the lower bound, specialize every operator to scalar identity maps and
vary one source and the dirty connector independently. Restoring `z` forces
each active `B_j` count even, while producing every nonzero output and
cancelling arbitrary `z` forces each `A_i` count even and positive. This
gives `2*9 + 2*5` for any correct schedule in the stated alphabet.

The same comparison holds with unequal **per-call** prices. Let `c_j > 0` be
the complete price of `B_j`, `a_i > 0` the complete price of `A_i`, and
`d_j` the number of outputs containing source `j`. Here
`d=(5,4,3,2,1,4,3,2,1)`. The shared path costs
`2 sum_j c_j + 2 sum_i a_i`; independent row stars cost
`2 sum_j d_j c_j + 2 sum_i a_i`. Thus the exact saving is
`2 sum_j (d_j-1)c_j > 0`. Readout prices cancel; the saving comes from
source maps that occur in multiple rows. This weighted invoice charges each
complete B/A call, including its recursive child bill when such a bill is
assigned. It assumes a call's price is stable across positions in the word.

The path adds no clean rows, copies, helper operations or separate frames, and
returns `z` to its dirty entry value. The abstract connector model has no
position-dependent frame-transition charge. A concrete supplier would still
need its actual child prices, any schedule-dependent transition or host cost,
precision and tape bill, and a placement proof. This local cost reduction is
not a kappa claim.

## Construction

Let the five supports be

```text
S1 = {0,1,2,3,4}
S2 = {0,1,2,3,5}
S3 = {0,1,2,5,6}
S4 = {0,1,5,6,7}
S5 = {0,5,6,7,8}.
```

They form a path in `J(9,5)`: each next support removes one current source
and introduces a source not used before. Their union is all nine sources, and
only source 0 is common to all five outputs; the route does not rely on a
large shared core.
The source word follows the parity states

```text
0 -> S1 -> S2 -> S3 -> S4 -> S5 -> 0
```

by toggling each symmetric difference:

```text
B0 B1 B2 B3 B4 | B4 B5 | B3 B6 | B2 B7 | B1 B8 | B0 B5 B6 B7 B8
```

At the initial `q=0` prefix, call each `A_i` once. At the later prefix
`q=S_i`, call that same `A_i` once more. The resulting full schedule uses 18
source calls and ten output readouts. Each `B_j` appears exactly twice, so
arbitrary connector contents are restored.

For each output, the two `A_i` calls contribute

```text
A_i z_initial + A_i(z_initial + sum_{j in S_i} B_j x_j)
= sum_{j in S_i} A_i B_j x_j,
```

because the interface is over F2 and `A_i` is linear. Thus arbitrary initial
target and connector contents cancel in the update, while every source input
remains unchanged. The scalar verifier exhausts all source values and dirty
bits; this algebraic identity establishes the same schedule for arbitrary
compatible linear maps.

More generally, take `p` distinct supports `S_1,...,S_p` of size `r`, where
each transition replaces one current source by a fresh source and
`n=r+p-1`. The same closed path `0,S_1,...,S_p,0` uses
`r+2(p-1)+r=2n` source calls; each source appears twice. Two A readouts per
output give `2n+2p`, the complete-call lower floor. Separate row stars cost
`p(2r+2)`. In the recorded instance `n=9`, `r=p=5`, these are 28 and 60.

## Verification

Run from repository root with Python 3.10 or later and the standard library:

```sh
python3 -B research/nine-source-johnson-chain-seed923edf/verify.py
python3 scripts/research_package.py --package research/nine-source-johnson-chain-seed923edf --check-only
```

The exact verifier checks the five supports, all nine source labels, every
Johnson-path transition, the 18-toggle word, the ten readouts and the 28-call
floor. For each of 512 source assignments, both dirty connector bits and all
32 dirty-output vectors (32,768 cases), it replays both the shared path and an
independent 60-call row-star schedule. Negative controls expose single-readout
connector leakage, a wrong output boundary, and a missing restoration call.
The verifier also checks the weighted formula at the nonuniform prices
`c_B=(1,...,9)` and `a=(1,...,5)`, where the saving is 120 price units.

Expected output starts with:

```text
PASS_NINE_SOURCE_WEIGHT_FIVE_JOHNSON_CHAIN
supports=01f,02f,067,0e3,1e1
common_sources=0
source_calls=18
readout_calls=10
total_complete_calls=28
independent_row_stars=60
saved_calls=32
weighted_price_control_saving=120
dirty_state_cases=32768
```

The registered package replay uses Python 3.12. This host has Python 3.14.7
and no `python3.12`; the direct verifier and package metadata/pin check were
run locally. Hosted replay remains an obligation.

## Selected context

The selected conditional result remains
`836330098538459/500000000000000000`, reviewed in
`docs/research/community-batch1099-review.md`. Its source manifest,
`ASSEMBLY.json`, reproduction `make frontier1094-verify`, Makefile rule and
actual verifier are pinned in [SOURCES.json](SOURCES.json). That reproduction
was resolved but not rerun: this contribution changes no selected source,
certificate, supplier or frontier record.

## Open next questions

The next useful question is whether nonuniform B/A call prices preserve a net
saving over separate row stars for this fresh-source Johnson-path family. That
requires assigning actual recursive child prices before claiming any effect
on the selected bound.

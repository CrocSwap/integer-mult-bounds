# Three-source gather child: a scoped negative result

**Result type:** source-pinned finite screen of one hypothetical rank-shape mechanism. No physical supplier, selected-frontier change, or new \(\kappa\) is claimed. Review: [PR #1814](https://github.com/CrocSwap/integer-mult-bounds/pull/1814). The original coordination claim is [Discussion #1167, comment 18921596](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18921596).

## Question and scope

Can three consecutive ADD gates that update one destination from three distinct sources be replaced by one four-register gather child, so several low-rank frame climbs become one larger-rank child? The sources are not the destination; their *values* stay unchanged, although their represented frames may grow. The child rank is the sum of every positive destination and source frame increment across the three gates. This preserves rank mass and charges the source-frame growth in full.

The exact finite domain is every length-three consecutive window in A or B of the pinned width-73 local word satisfying that gate pattern. Schedules may choose any non-overlapping subset. The interval screen ignores further register, adapter, hosting, and physical-interface conflicts, making it deliberately favorable to the gather mechanism.

The initial subcase required all source frames to stay fixed and yielded no candidates. One evidence-driven refinement allowed those frames to grow and included their full rank increments in the merged child. No further arity, nonconsecutive-window, alternate-word, or physical-synthesis search was made.

## Exact result

The pinned word has 112 ports, 480 helpers, 704 registers, and operation lists of 3,451 ADD gates in A and 1,846 in B. The verifier independently reconstructs the complete reported local profile

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
```

with rank mass 5,586. The exhaustive scan finds 32 windows in A and none in B:

| Number | Per-gate `(destination climb, source climb)` | Gather rank |
|---:|---|---:|
| 24 | `(0,4), (0,4), (0,4)` | 12 |
| 8 | `(4,4), (0,4), (0,4)` | 16 |

Exact weighted interval scheduling chooses 16 disjoint windows: eight of each pattern. Replacing their positive climbs by one rank-sum child gives

```text
{1:2412, 2:418, 3:432, 4:86, 5:82, 8:8, 12:8, 16:8}
```

Rank mass remains 5,586. Under the pinned local ceiling routine, this max-saving schedule has ceiling `171310859037/100000000000000` = `0.00171310859037`; the baseline ceiling is `1690054109089/1000000000000000` = `0.001690054109089`. The gain is exactly `2305448128100/1690054109089` percent, about **1.3641268145%**, below the task's five-percent gate.

There is a stronger obstruction within this domain. At `a = 1.05` times the baseline ceiling, the verifier assigns each candidate its certified upper bound on moment savings, then maximizes those bounds over all non-overlapping schedules. Subtracting that maximum from the certified baseline moment lower bound still leaves the moment above one by the positive exact rational in `CERTIFICATE.json` (`strict_margin_above_one`, approximately `0.000176054645830535`). Thus no schedule in this consecutive C3 gather family reaches the five-percent screen, even when the full gather, source reads, copies, adapters, extra helpers, frame conversions, restoration, precision and hosting overheads are all set to zero.

## Map and cost accounting

For an admitted window with exact rational coefficients \(c_1,c_2,c_3\), the value map on arbitrary dirty inputs is

```text
(D,S1,S2,S3) -> (D+c1*S1+c2*S2+c3*S3, S1, S2, S3).
```

Its inverse subtracts those three source multiples. For every scanned window, the verifier checks the exact rational 4-by-4 matrices multiply to the identity in both orders. This establishes invertibility of the value map; it does not show that one recursive child implements the four endpoint-frame transitions.

The favorable model charges one child of rank \(R\), the sum of all positive destination and source frame increments. That keeps total rank mass exactly fixed. It assigns zero cost to implementing the four-register gather, collecting three source values, adapters or extra copies, helper capacity, extra frame transitions, restoration, precision/phase conversion, and whole-call hosting/owner changes. The strict screen failure therefore rejects the proposed ideal rank profile against the five-percent gate; it does not prove that other gather schedules or decoder families fail.

## Reproduction

From the repository root, use Python 3.12 for the registered package replay:

```sh
python3.12 scripts/research_package.py --package research/complex-gather-child-seed7a6d --check-only
python3.12 scripts/research_package.py --package research/complex-gather-child-seed7a6d
```

The first command checks metadata and base-commit Git blob/SHA pins only. The second performs the exact replay and focused controls. Direct commands are:

```sh
python3 -B research/complex-gather-child-seed7a6d/verify.py --write
python3 -B research/complex-gather-child-seed7a6d/verify.py
python3 -B -m unittest discover -s research/complex-gather-child-seed7a6d -p 'test_verify.py'
```

`--write` creates the deterministic certificate; the default command recomputes it and requires exact JSON equality. The verifier checks the selected-record/certificate binding, selected source manifest, local-word compressed and decompressed hashes, slot pin, ceiling source hash, complete local frame replay, and profile reconstruction. `SOURCES.json` records every Git blob at base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. `SELECTOR.json`, `CLAIM.md`, `OVERLAP.json`, and `OVERLAP-GATHER.json` record the assignment and coordination evidence.

Expected markers include `PASS_C3_GATHER_CENSUS windows=32 max_nonoverlap=16`, `PASS_C3_GATHER_MAPS count=32`, and `SCREEN_C3_GATHER ... five_percent_pass=False`.

## Predecessors and limits

The selected incumbent is PR1094 as resolved by its selected record and maintainer review. The pinned ceiling uses PR1012's coverage identity and the selected local word. The nearby cycle-6 PR1799 studies the opposite orientation: one unchanged source updates three distinct destinations. Discussion #1167 comment 18920760 claims a diagonal rank-16 batch across distinct destinations; it does not merge three inputs into one destination. PR1605/Discussion #1596 address integer reblocking thresholds and chronological delivery. Discussion #1622/PR1633 classify all-pairs overcomplete E8 factor ranks, while `complex-coefficient-reuse` shares coefficient preparation for same-source scalar runs without changing the paid frame profile. `complex-block-rank-optimum` proves its fixed eight-array interface and explicitly leaves changed interfaces out of scope.

The result does not cover nonconsecutive or reordered gates, other gather arities, other words, changed coverage laws, or a physical four-register child. The underlying local-word source remains marked not admitted for arbitrary-dirt/global obligations; this package does not promote it or replay the full selected construction.

## Open next questions

Could a nonconsecutive same-destination gather beat this ceiling if intervening ADDs commute with all source/destination shears? A first step is to build a dependency graph for source-version intervals in the pinned word, admit only gate pairs with disjoint touched registers, and account for all endpoint frames before synthesis. The blocker is preserving frame histories and values through the commuting interval; no such search was attempted here.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in selecting the scope, deriving the rank-sum screen, implementing the exact verifier and controls, and preparing the write-up. The selected PR1094 lineage, PR1012 coverage identity, pinned word authors, PR1605/#1596, PR1633/#1622, the cycle-6 PR1799 package, and `complex-coefficient-reuse` retain their respective attribution. New package material is Apache-2.0; source licenses and notices are unchanged.

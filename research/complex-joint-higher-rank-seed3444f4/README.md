# Higher-rank two-lane boundary at a single ADD gate

This package gives a finite, source-pinned extension of the conditional rank-two joint-boundary proposal in PR #1764. It covers only one binary ADD gate whose two operands both climb to a common frame and whose two quotient ranks are not both one. It does **not** admit a recursive supplier, change the selected construction, or claim a new `κ`.

## Exact boundary mechanism

At one gate, let the common target frame be `F` and the two old dirty frames be `U` and `V`, with quotient dimensions

```text
r = dim(F) - dim(U)
s = dim(F) - dim(V).
```

The exact scalar gate is the shear `T_c(x,y) = (x + c y, y)` for a recorded nonzero rational `c`. Its matrix is `[[1,c],[0,1]]`, its determinant is one, and its inverse is `T_-c`. The old dirty input space `U × V` has codimension `r+s` in `F × F`. Since `T_c` is invertible on `F × F`, its image has the same dimension and the joint boundary also has codimension `r+s`.

This proves the linear boundary and its exact cost rank. The conditional step is separate: one recursive `J_{r,s}` child must implement that whole two-lane boundary at the ordinary rank-`r+s` price. That supplier and its adapters are not supplied here.

## Complete finite census

The verifier reads the selected local word pinned by the current main source chain. It replays every A, B, and scheduled cleanup-tail operation in both orientations, checks all frame inclusions and old/new endpoints, and extracts only single ADD gates with two positive climbs and `max(r,s) > 1`.

It finds 359 gates:

| Quotient ranks `(r,s)` | Gates | Joint rank `r+s` |
| --- | ---: | ---: |
| `(1,2)` | 72 | 3 |
| `(1,3)` | 52 | 4 |
| `(1,4)` | 35 | 5 |
| `(1,5)` | 26 | 6 |
| `(2,2)` | 14 | 4 |
| `(2,3)` | 5 | 5 |
| `(2,4)` | 19 | 6 |
| `(3,3)` | 122 | 6 |
| `(3,4)` | 6 | 7 |
| `(4,4)` | 8 | 8 |

For a conditional like-for-like comparison, the starting profile includes the 753 rank-one pairs from PR #1764: 590 same-gate `(1,1)` pairs and 163 terminal `(1,1)` pairs. The 359 higher-rank gates are then replaced by one rank-sum child each. The resulting profile is

```text
selected:  {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
PR #1764:  {1:906, 2:1171, 3:432, 4:142, 5:82, 8:8}
extended:  {1:721, 2:1047, 3:197, 4:132, 5:96, 6:167, 7:6, 8:16}
```

All three profiles have rank mass 5,586. The conditional child-call counts are 3,494, 2,741, and 2,382 per local word. Under the retained selected-word packing model and a certified `10^-12` grid, the extension raises the fixed-word ceiling by **at least 5.956346700% over the PR #1764 candidate profile**, and by at least 11.510179694% over the selected baseline profile. This is a conditional local ceiling comparison only.

## Overhead screen

At `1.05` times the upper endpoint of the PR #1764 candidate ceiling, the extended profile permits at most **43 added rank-one-equivalent child costs per local call** if each extra unit is paid by displacing fractional rank-51 idle mass. Forty-four fail. Charging one rank-one-equivalent adapter for each of the 359 joint boundaries gives a relaxation moment above one at that target, so that overhead would erase the 5% incremental margin.

The 43-unit budget is not an estimate of the physical adapter cost. It is a strict allowance in the retained fixed-word model. The ledger below states the remaining costs explicitly.

| Cost category | Optimistic screen | Remaining obligation |
| --- | --- | --- |
| Source access | No added scalar reads | Show how the joint child receives both lanes without extra reads or copies. |
| Native helper operations | No added scalar gates; original gate and frame word stay fixed | Price any gather, packing, or local adapter operations. |
| Recursive children | Replace ranks `r` and `s` by one `J_{r,s}` child of rank `r+s` | Construct and admit a supplier for every listed shape. |
| Frame changes | None beyond the two recorded climbs | Verify a supplier supports both dirty frames and the common target frame. |
| Copies and hosting | Zero added cost in the favorable screen | Rebuild physical copy inventory and complete-call hosting. |
| Restoration | The local shear has exact inverse `T_-c` | Prove the recursive joint child restores both lanes and arbitrary dirty spectators. |
| Precision and phases | No added transfer cost assumed | Price coefficient representation, phase transfer, and precision conversion. |
| Interface transitions | At most 43 rank-one-equivalent costs fit the 5% increment | Provide the actual `J_{r,s}` input/output contract and all adapters. |

## Reproduction

From the repository root:

```sh
python3 -B research/complex-joint-higher-rank-seed3444f4/verify.py
python3 -I -O -B research/complex-joint-higher-rank-seed3444f4/verify.py
python3 scripts/research_package.py --package research/complex-joint-higher-rank-seed3444f4 --check-only
python3.12 -B scripts/research_package.py --package research/complex-joint-higher-rank-seed3444f4
```

The direct verifier checks the selected-record and word pins, all source gate and frame endpoints in both orientations, the exact shape census, rank-mass conservation, exact fixed-word ceilings, the overhead budget, and four negative controls. `CENSUS.tsv` stores one compact row per gate; `RESULT.json` stores the exact profiles and rational ceiling brackets. `--check-only` checks package metadata and source pins, not the mathematics.

The assignment is recorded in `TASK.json`, its input and provenance pins in `SOURCES.json`, and the registered commands in `VERIFY.json`. The claim is on [Discussion #1167, comment #18922740](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18922740). The final overlap snapshots cover all open PRs and Discussions with complete pagination and no warnings; see `OVERLAP.json` and `OVERLAP-RELATED.json`.

## Predecessors and limits

PR #1764 / Discussion #1765 covers same-gate `(1,1)` transitions and terminal `(1,1)` pairings under a proposed `J2` boundary. PR #1814 covers consecutive three-source, one-destination gather windows. PR #1817 / Discussion #1596 studies diagonal batches of rank-one climbs across different destinations. This package does not combine their profiles or supersede their open supplier, overhead, or hosting questions.

The result is limited to the pinned word, the listed 359 two-operand gates, the retained coverage law, and zero-extra-cost joint interfaces before the separate overhead screen. It does not prove that any `J_{r,s}` interface is implementable by the selected recursive supplier, establish an all-size construction, close inherited precision or analytic obligations, or improve the selected `κ`.

## Open next questions

- Can an admitted recursive supplier realize `J_{r,s}` for every listed shape with one child at the ordinary rank-`r+s` cost?
- Can its actual gathering, copies, precision, restoration, and whole-call hosting bill fit within the 43 rank-one-equivalent per-call budget?
- Can a source-pinned all-size assembly integrate those boundaries while retaining every arbitrary-dirt column and terminal frame?

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No independent human review is claimed.

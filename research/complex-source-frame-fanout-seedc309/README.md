# Three-output shared-source fanout: a scoped negative result

**Result type:** exact finite obstruction for one C3 family on the selected word. This does not add a supplier, change the selected construction, or establish a new \(\kappa\).

Review handoff: [PR #1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799); original research claim: [Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18921204).

## Question and scope

On the selected width-73 local word, can three consecutive ADD gates that read the same unchanged source and write three distinct destinations be compressed into one tagged child whose rank is the sum of the three destination-frame climbs? We considered every length-three window wholly inside section A or section B with zero source-frame increment at each gate and at least two positive target climbs. The schedules considered are all non-overlapping subsets of those windows.

This is one refinement of `complex-new-helper-inventory`. The initial source-frame-deferral subcase had no qualifying positive source climbs, so the bounded experiment pivoted once to the output-side C3 fanout described here. The separate four-lane J2 composition idea was rejected at its optimistic capacity screen: at most 176 disjoint groups fit among 704 registers, below the 181 groups needed for its five-percent threshold.

## Exact result

The pinned word has \(m=73\), 112 ports, 480 helpers, and 704 registers. Replaying its A and B operations and all terminal charges reconstructs the reported profile

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
```

The scan covers all 3,451 A operations and 1,846 B operations. It finds 32 qualifying windows (2 in A and 30 in B). Exact weighted interval scheduling selects 25 non-overlapping groups (2 in A and 23 in B). Their replacement profile is

```text
{1:2382, 2:421, 3:416, 4:124, 5:82, 8:8, 9:8, 12:6}
```

Both profiles have rank mass 5,586. Under the pinned local ceiling, the selected maximum-weight schedule has ceiling `42634383521/25000000000000` = `0.00170537534084`, a `0.9065527351%` gain over the baseline ceiling `1690054109089/1000000000000000` = `0.001690054109089`.

The stronger five-percent screen prices each candidate by a certified upper bound on its moment saving at `a = 1.05` times the baseline ceiling. Exact weighted interval scheduling maximizes the sum of those upper bounds over every allowed non-overlapping schedule. Even after dividing by the family/stage factor and subtracting that maximum saving from the certified baseline moment lower bound, the resulting moment lower bound remains greater than one by the exact positive rational recorded as `strict_margin_above_one` in `CERTIFICATE.json` (about `0.000199109206397236`). Thus no schedule in this finite C3 family reaches the five-percent target under the pinned model.

### Map and cost accounting

For arbitrary dirty values `(S,D1,D2,D3)`, each qualifying window has the exact map

```text
(S,D1,D2,D3) -> (S,D1+c1*S,D2+c2*S,D3+c3*S).
```

Its inverse subtracts the same three rational multiples of `S`; the verifier multiplies both exact rational 4-by-4 matrices in both orders and checks the identity. This establishes invertibility of the algebraic map, not admission of a physical recursive supplier.

The screen charges the replacement child rank \(R=t_1+t_2+t_3\), preserving rank mass. To make the bound favorable to C3, it assigns zero cost to extra source copies, fanout adapters, new helper capacity or operations, extra source reads, additional frame transitions, restoration, precision conversion, hosting, and owner changes. The result therefore rejects this particular zero-overhead profile against the five-percent acceptance gate; it is not a physical implementation result or a general impossibility theorem.

## Reproduction

From the repository root, using Python 3.12 for the registered package replay:

```sh
python3.12 scripts/research_package.py --package research/complex-source-frame-fanout-seedc309 --check-only
python3.12 scripts/research_package.py --package research/complex-source-frame-fanout-seedc309
```

The first command checks package metadata and exact base-commit Git blob/SHA pins only. The second runs the exact replay and focused positive/negative controls. Direct commands are:

```sh
python3 -B research/complex-source-frame-fanout-seedc309/verify.py --write
python3 -B research/complex-source-frame-fanout-seedc309/verify.py
python3 -B -m unittest discover -s research/complex-source-frame-fanout-seedc309 -p 'test_verify.py'
```

The first verifier invocation writes the deterministic `CERTIFICATE.json`; the second checks byte-decoded JSON equality against exact recomputation. `SOURCES.json` pins the original task catalogue, selected-record provenance, reviewed selected-construction inputs, and local-word input to base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The verifier also checks the compressed and decompressed word digests, slot pin, selected-record/certificate binding, and reconstructed full local profile.

Expected replay markers include `PASS_SCOPED_C3_FANOUT_OBSTRUCTION windows=32 max_nonoverlap=25`, `PASS_C3_ARBITRARY_DIRTY_MAPS count=32`, and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.

## Predecessors and limits

The incumbent is the selected PR1094 construction as resolved by `certificates/selected-result.json` and its maintainer review. The local ceiling and coverage identity are PR1240 and PR1012. Adjacent work includes PR1756's abstract two-output clean-cache obstruction and three-output control, PR1764/Discussion 1765's tagged J2 boundary, and Discussion 1693's rank-one-to-rank-two retiming. This package contributes the selected-word three-gate census and exact schedule bound for a stable shared source.

The result does not cover nonconsecutive or reordered gates, other fanout arities, other words, changed coverage laws, or any physical C3 supplier. The inherited selected construction remains conditional on its reviewed model and source/interface obligations.

## Open next questions

1. Nonconsecutive shared-source outputs might allow more compatible fanout blocks. A follow-up should enumerate source-version intervals with exact intervening-write, destination-dependency, and frame checks, then optimize compatible blocks. The added dependency graph must preserve endpoint commutation.
2. A physical C3 child may require source copies or adapter resources. A follow-up can start from one pinned window and account for the exact four-register rational map, helper inventory, restoration, and terminal frames. No reviewed C3 supplier contract currently supplies those costs.

## Credit

Prepared by Cinna Davis. The selected construction, word, ceiling, and task-card sources retain their original attribution and notices. Substantial AI assistance: OpenAI Codex helped develop the bounded search, exact verifier, tests, and package prose; the stated scope and evidence are tied to the pinned artifacts and reproducible replay. New package work is offered under Apache-2.0.

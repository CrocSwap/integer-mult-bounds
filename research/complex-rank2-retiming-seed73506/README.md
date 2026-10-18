# One-touch rank-2 retiming cannot meet the 5% ceiling gate

**Scoped negative result; no construction and no new κ.** On the selected PR1094 gauge44 local program, the complete class of same-column rank-1 climb pairs with exactly one intervening scalar event has 690 candidates in each direction. The maximum set that can be fused without reusing a climb has **674 pairs**. Even if every one becomes a rank-2 child at zero additional operation, copy, frame, hosting, precision, interface, or restoration cost, the exact selected-word ceiling rises only **4.6659458%**, below the predeclared 5% target.

## Exact object and result

The source is `research/community-frontier1094-audit/selected-replay.tar.gz`, SHA-256 `f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`. The program member is `candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`, SHA-256 `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`. The verifier extracts and checks these bytes; it does not modify the frozen source.

For each direction, climbs are grouped by column in program order. A candidate is a consecutive `(rank 1, rank 1)` pair with exactly one intervening event that references the column; all 690 such intervening events are scalar operations. Forward and backward candidate sets agree. On each column, the climb events form a path and candidate fusions are edges between adjacent rank-1 vertices. A greedy path matching and a separate dynamic-programming recurrence both give the maximum compatible set: **674**.

The selected local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` at width `m=73`, 896 families, 9 stages, and centre charge 64. For `n` disjoint fusions, the optimistic profile is

```text
{1: 2412 - 2n, 2: 418 + n, 3: 432, 4: 142, 5: 82, 8: 8}
```

It preserves all 5,586 local rank units and the incumbent 1,646 idle units, which the relaxation fills at rank 51 under the halving guard. The exact interval engine in `research/complex-local-word-ceiling/ceiling.py` gives:

| Case | Certified ceiling bracket for `a` |
|---|---:|
| Selected profile | `[0.001690054109088, 0.001690054109089]` |
| All 674 one-touch fusions, with zero added cost | `[0.001768911117731, 0.001768911117732]` |
| Required target, 5% above the selected upper endpoint | `0.00177455681454345` |

At that target, the exact relaxation for 674 fusions is already greater than 1. The least number of zero-overhead rank-2 fusions that passes is **720**: 719 fails and 720 passes. Thus this one-touch candidate family misses the gate by at least 46 fusions even before any physical implementation bill is added.

## Cost boundary

Every incumbent source, helper, recursive-child, centre, and coverage charge remains in the selected profile. The screen grants the proposed scalar/frame retiming, copies, hosting, precision, interface transitions, and dirty-state restoration for free. This is deliberately favorable. Any additional paid child rank would consume rank-51 idle mass and lower the ceiling; all other implementation costs are waived here, so a real construction would still have to account for their effect. The screen rules out reaching the 5% target **through this complete one-touch fusion family under the unchanged coverage law**.

It does not prove that any pair can actually be retimed. It does not rule out pairs with two or more intervening operations, a different block rank, a changed word or coverage law, or another helper inventory. It is not a universal lower bound on complex decoders and supplies no physical supplier or κ.

## Relation to prior work

Arham Tahir's [PR1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605) gives the rank-2 cost threshold but no physical realization. Josie Elliston's [finding in Discussion 1596](https://github.com/CrocSwap/integer-mult-bounds/discussions/1596#discussioncomment-18915212) gives the 5% κ threshold for unrestricted rank-1 pair fusion and leaves its frame/dirty-state contract open. Navinor's [source event count in Discussion 1659](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659#discussioncomment-18916048) identifies the one-touch candidates syntactically without frame or dirty-state semantics. This package intersects that exact chronological class with the exact disjoint-pair budget and stops before an unpromising physical synthesis.

The active [frame-reassignment claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659) fixes the paid profile. The active [nested-endpoint claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1674) fixes scalar order. This screen changes both local schedule and paid rank profile, but makes no claim about their results. The current selected record is `836330098538459/500000000000000000`; its review is `docs/research/community-batch1099-review.md`, source manifest is `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate is `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and selected replay instruction is `make frontier1094-verify`. This package does not rerun or alter that replay.

## Reproduce

From the repository root:

```sh
python3.12 scripts/research_package.py --package research/complex-rank2-retiming-seed73506 --check-only
python3.12 scripts/research_package.py --package research/complex-rank2-retiming-seed73506
```

The package verifier rechecks archive/member pins, both event directions, the 674-edge maximum matching by two algorithms, the selected baseline ceiling, the optimistic profile, and the exact 719/720 target boundary. Expected marker:

```text
PASS_ONE_TOUCH_RANK2_RETIMING_SCREEN candidates=690 matched=674 a_gain_pct<4.666 target_min=720
```

## Open next questions

- **Can a larger chronological class reach 720 disjoint fusions?** This matters because the one-touch class is too small even under the free-retiming relaxation. A feasible first step is to enumerate pairs with two intervening scalar operations and test whether a common rank-2 frame can preserve their exact map. The blocker is a transformation that carries both dirty-state dependencies through those operations without adding a paid rank-1 child.

## Credit

Retain the selected PR1094 lineage credited in the selected review; Douglas Colkitt/PR1240 and Sagar Thakrar/PR1012 for the ceiling model; Arham Tahir/PR1605 for integer block budgets; Josie Elliston/Discussion 1596 for rank-2 fusion thresholds; and Navinor/Discussion 1659 for the source-bound event classification. The exact ceiling engine is reused and pinned; the event parsing and matching certificate are new. Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

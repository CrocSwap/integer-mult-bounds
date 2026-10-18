# Mixed-rank diagonal blocks miss the five-percent screen

**Construction-focused exact screen and scoped negative result. No physical supplier or new \(\kappa\) is claimed.**

The construction replaces consecutive independent rank-2/rank-3 child products by one child of rank equal to their sum. For square matrices (A_i,B_i), the exact identity is

\[
\operatorname{diag}(A_1,\ldots,A_t)\operatorname{diag}(B_1,\ldots,B_t)
=\operatorname{diag}(A_1B_1,\ldots,A_tB_t).
\]

The verifier checks the full symbolic product for a mixed (2,2,3,3,3,3) partition of side 16. This gives an exact block decoder; its input gathering, output routing, frames, interfaces, hosting, precision, and dirty restoration are then all waived to form a favorable screen.

The pinned gauge44 provider has 641 uninterrupted runs and 850 rank-2/rank-3 calls in each orientation. There are 1,191 contiguous windows of total rank at most 16 if singleton calls are included; 341 are nontrivial merge candidates. A weighted interval dynamic program selects 162 disjoint blocks covering 365 calls (rank mass 1,039) and replaces them by one child each. Both orientations produce the same schedule and profile:

| Per-call profile | Rank mass | Exact relaxed ceiling upper endpoint |
|---|---:|---:|
| Selected `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` | 5,586 | 0.001690054109089 |
| Best strict-chronology zero-charge profile `{1:2412, 2:362, 3:123, 4:158, 5:87, 6:127, 8:9, 9:1, 12:4, 15:5, 16:3}` | 5,586 | 0.001764844128533 |

The resulting ceiling gain is **4.425303%**, below the card's 5% gate. More strongly, at 1.05 times the selected ceiling the verifier maximizes an outward-rounded upper bound on savings over every admissible disjoint interval packing. Even that best possible zero-charge packing leaves the relaxed moment at least `1.0000270103`, so no packing in this strict chronological rank-2/rank-3 block family reaches 5%. Adding physical costs can only reduce the gain.

The bound is deliberately scoped. It does not cover moving calls across non-phase events, rank-one commutations, nonconsecutive buffering, larger child sides, changed local words, or a changed coverage law. The event trace does not provide the physical operand lifetime and mutable-output restoration contract needed to price those variants.

## Reproduce

Python 3.12 and the standard library are sufficient:

```sh
python3 scripts/research_package.py --package research/complex-mixed-rank-diagonal-seed8433 --check-only
python3.12 scripts/research_package.py --package research/complex-mixed-rank-diagonal-seed8433
```

Expected verifier line starts `PASS_COMPLEX_MIXED_RANK_DIAGONAL_BLOCKS` and reports 641 runs, 341 nontrivial intervals, 162 selected blocks, exact rank-mass preservation, the ceiling gain, and four negative controls. The dynamic program compares exact rational enclosures from the pinned ceiling implementation.

The selected provider archive and member, selected record, source manifest, task catalogue, and ceiling model are pinned in [SOURCES.json](SOURCES.json). The active research claim is [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926727). PR #1779 tests contiguous rank-one batches, PR #1817 adds register commutations to that rank-one object, and draft PR #1836 studies two higher-rank operand climbs at one ADD gate. PR #1866 constructs a different heterogeneous five-output rank-six tensor. This package uses direct sums of ordinary rank-2/rank-3 matrix products in the selected word's uninterrupted trace and a complete bounded interval optimizer; it claims no new local tensor identity beyond that direct-sum construction.

## Open next questions

- Can a nonconsecutive mixed-rank block schedule be realized with complete operand lifetime, source/copy, output, frame, hosting, precision, and arbitrary-dirty restoration charges? A useful next step is to recover those lifetimes from a source that records mutable-state ownership, then price one candidate block end to end. The selected event archive alone lacks that physical state contract.

**Attribution.** The selected gauge44 word and its source lineage remain credited to their original authors (see the pinned selected record and source manifest). This bounded diagonal-block construction, exact interval optimizer, and package were prepared by Cinna Davis with substantial OpenAI Codex assistance; no subagents were used. No independent human review is claimed.

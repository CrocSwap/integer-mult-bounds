# Diagonal rank-16 batches are not limited by the selected chronology

**Audit of one implication in open PR #1779. No new κ; the selected record is unchanged.**

[PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) (1337isnot1337, head `1e3128bf`) batches
sixteen rank-1 climbs on distinct destinations into one rank-16 diagonal child. In the selected gauge44 provider it
finds 8 such batches (128 rank-1 climbs). That raises the zero-charge ceiling by 1.72%, below the card's 5% gate.
Its count uses only **contiguous** runs: any computational event breaks a run, and chunks are 16-aligned.

That restriction, not the provider, makes the count small. A rank-1 climb on `L r` reads and writes only `L r`.
Inside its own phase it can move past any event that touches no `L r`. Allowing that move, and nothing else,
gives this:

| | per orientation |
|---|---:|
| Disjoint 16-batches on distinct destinations (earliest-deadline greedy) | **134** (2,144 of 2,412 rank-1 climbs) |
| Per-phase cap ⌊rank-1 count / 16⌋ | 149 |
| By phase: A / B / cleanup_tail / final | 58/58, 52/67, 4/4, 20/20 |
| PR #1779's contiguous rule, re-implemented: original → reordered programs | 8 → 134 |

**The retained checker accepts the reordered programs unchanged.** Only rank-1 climbs move; every other event
keeps its relative order. The [independent local checker](../complex-571-cold14-k492b/code/hpe_audit_local.py)
replays scalars, frames and wrappers literally and runs 25 mutation controls. It passes both reordered
orientations with a receipt (`local` block and paid profiles) equal to the original programs'. The original's
receipt equals the pinned selected `INDEPENDENT-LOCAL-REPLAY.json`. Two added mutations are rejected: a climb
moved past a scalar on its own register, and a climb moved into the next phase.

## Exact ceilings (#1779's convention)

Rank mass is preserved and every interface charge is waived. Ceilings come from
[`ceiling.py`](../complex-local-word-ceiling/ceiling.py) with 73 columns, 896 families, nine stages, centre 64 and
grid 10⁻¹⁵. The gate is `1.05 × 0.001690054109089`.

| rank-16 batches | a ceiling (upper) | gain | +5% gate |
|---:|---:|---:|---|
| 8 (#1779) | 0.001719107428154 | +1.72% | fails |
| 22 | 0.001772433845132 | +4.87% | fails |
| 23 | 0.001776370006187 | +5.11% | passes |
| 134 (legal here) | 0.002358018698467 | +39.5% | passes |
| 149 (phase cap) | 0.002467305908467 | +46.0% | passes |

**Charge headroom.** With 134 batches, at most **1,258 extra rank-1 children per call** keep the gate (1,259
fail; sharp). That is about 9.4 per batch, under the idle-displacing convention of discussion 1596: extra paid
work replaces equal idle mass. Charging overhead on top of the idle bill instead, as #1605 does, would give less;
that convention is not computed here.

## What this does and does not show

- It removes one stated reason the diagonal-batch route fails. The source chronology allows 134 batches, so the
  zero-charge screen clears the 5% gate by a wide margin.
- The route is decided by what #1779 waived. Gathering 16 registers at *different* frames into one diagonal
  rank-16 child needs copies, frames, hosting, output storage, precision and arbitrary-dirty restoration. This
  package inherits #1779's premise that a diagonal rank-16 child realizes 16 independent rank-1 climbs, and
  does not examine it.
- The reorder is checked only at the local level. Every register's frame at each phase marker is unchanged
  because climbs stay inside their phase. The check does not establish that global hosting and the idle-remainder
  frame audit (`global/hosted`, `global/audit` in the replay archive) are insensitive to positions inside a phase.
- Batch counts are a greedy lower bound. 149 is the trivial phase cap, not an attained value.
- The bit supplier binds well before +39% (#1605), so the complex ceiling alone does not set κ.

## Reproduce

```sh
python3 -I -B research/diagonal-batch-commutation/verify.py          # ~12 s, PASS_DIAGONAL_BATCH_COMMUTATION
python3 scripts/research_package.py --package research/diagonal-batch-commutation
```

`verify.py --write` regenerates `RESULT.json`. `batch.py PROGRAMS CANONICAL-WORD [OUT]` runs the reorder on
extracted members and can write the reordered programs. Both use the standard library only. Checked on Python
3.10 and 3.12.

## Open next questions

- **What can a diagonal rank-16 child of frame climbs cost?** Its gathering and restoration charge now decides
  the route. The first step is to specify the contract for 16 registers at different frames `a_i → b_i`, then
  price it against the 1,258-unit headroom above. The blocker is that no such contract is written down; #1779's
  diagonal identity is the only premise.
- **On-top charge convention.** The same headroom with overhead added on top of the idle bill (#1605's
  convention) needs a moment term outside `ceiling()`'s local-profile interface.
- **Exact phase-B maximum (52 ≤ max ≤ 67).** This only moves the zero-charge ceiling between +39.5% and +46%.
  It is low priority next to the charge question. The windows are already computed by `batch.py`, so it is an
  interval-stabbing integer program.

## Credit

The diagonal batching premise and the contiguous count are 1337isnot1337's (#1779). The rank-shape budgets are
Arham Tahir's (#1605, discussion 1596). The packing ceiling is Douglas Colkitt's (#1240), and the coverage law
is PR1012's. The local checker is from the icekylinx / PR514 / PR433 lineage, retained in
`complex-571-cold14-k492b`. Selected construction credits are in its review. Prepared for Josie Elliston by
Claude Code (Claude Opus 5.5) in one donated session, without independent review. Apache-2.0.

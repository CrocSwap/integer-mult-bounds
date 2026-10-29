# Block-climb complete profile: the charged realization of rank-one reblocking (no new κ)

**Scoped exact obstruction for one declared realization family of the drawn
`complex-rank-shape-decoder` card. No κ claim; the selected record is unchanged.**
Agent: Aaron Wang, with help from opencode (substantial AI assistance; no model
named; no independent human review). Base commit
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.

The card asks for one exact small decoding identity whose frame path climbs in
blocks, priced with its complete per-call profile. This package builds the
smallest such identity (`k = 2`), prices its complete invoice, and records where
the construction dies and what remains open.

## What this establishes

1. **Exact identity classification at the smallest block (`k = 2`).**
   A rank-`k` block child delivers `k` products of linear forms, so its outputs
   are rank-1 tensors. For two payload products `x_p1 y_q1`, `x_p2 y_q2`:

   - If the pair pattern is a *matching* (`p1 != p2`, `q1 != q2`), the rank-1
     tensors inside the required span `span(x_p1 y_q1, x_p2 y_q2)` are exactly
     the two coordinate ones (the determinant conic of `aA + bB` is `ab`).
     Only coordinate-aligned child outputs can deliver the two products.
   - If the pattern shares a row or a column, mixed rank-1 outputs exist
     (e.g. `x_1(y_1 + y_2)`) and decode back with exact integer additions
     (`x_1 y_2 = f_1 - f_2`), but mixing never reduces the number of charged
     transports: the block operands are length-`k` vectors at the block frame
     in every exact realization.

   The `k = 3` fixture (all 0/1 diagonal matrices) witnesses coordinate
   alignment in a finite alphabet; the general argument is the two-line
   rank-1-support observation recorded in `RESULT.json` and is not
   machine-checked.

2. **Dirty gather-slot restoration forces paid work.** Writing a gathered
   operand over a dirty slot is non-injective in the slot's prior content
   (exact witness: states 0 and 1 collide), so restoring arbitrary dirty state
   needs a paid save per overwritten slot — a rank-1 child in the retained
   cost alphabet. This turns [PR 1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605)'s
   "one added rank-one call per output block" tax from an assumption into a
   lower bound for every realization that cannot use owned temporaries.

3. **The transport obstruction, in closed form.** A climb group of `k` payload
   units delivered by one rank-`k` child with `alpha` charged transports (each
   rank-`r` transport charged as a rank-`r` recursive child,
   [PR 1429](https://github.com/CrocSwap/integer-mult-bounds/pull/1429)'s contract) has net
   saving `k c(1) - (1 + alpha) c(k)` over the `k` rank-1 children it replaces.
   The group pays only when `k^a > alpha + 1`, that is `a > ln(1+alpha)/ln k`.
   With exact enclosures, `ln 2 / ln 51 = 0.17629143...`, so **every group with
   at least one charged transport is strictly dearer than its payload children
   for every `a <= 1/99` (indeed every `a < 0.17629`), every `k = 2..51`**.
   Both the retained `ceiling.py` enclosure and an independent binomial-tail
   enclosure agree on all 150 grid points per `a`.

4. **Complete per-call screens at the acceptance target**
   `a* = 21/20 * 1690054109089/10^15 = 0.001774556814543` (the card's +5%
   ceiling margin). All signs exact:

   | Realization (rank-1 payload reblocked at cap 16) | Moment at `a*` | Ceiling vs baseline |
   |---|---|---|
   | Selected word (no reblock) | fails (control) | 1.00x |
   | `k = 362`, zero charge | fails | — |
   | `k = 363`, zero charge | passes (PR 1605 threshold) | — |
   | `k = 363`, one transport per group | fails | +2.8% (with idle credit) |
   | `k = 363`, two transports per group | fails | +0.8% (with idle credit) |
   | `k = 363`, one rank-1 save per block | fails | +4.5% (with idle credit) |
   | Full reblock (`k = 2412`), zero charge | passes | 1.47x |
   | Full reblock + one shared rank-16 transport | fails | — |
   | Full reblock + 10 rank-1 units (the call budget) | passes | 1.47x |

   The +5% gate is missed by every per-group charged realization screened; it
   stays open for call-level invoices inside PR 1605's reproduced budget of
   **10 added rank-1 units per call** at full reblock (zero at `k = 363`),
   which is under 0.07 units per group for 151 groups. Since the cheapest
   charged item in the frame contract is one rank-1 call, **any surviving
   realization must be per-group zero-charge** (both operand vectors already at
   the block frame, owned gather slots) with all its charged work shared across
   the call.

So the answer to the card's question for this family: a decoder cannot deliver
the local paid mass in fewer, larger-rank children through *charged* block
frame climbs at any saving below `a = ln 2 / ln 51`; the entire lever now rests
on whether zero-charge co-frame groups exist inside the selected word.

## Reproduce

Python 3.12, standard library only, exact rational arithmetic throughout
(about 2 minutes):

```sh
python3.12 -I -B research/block-climb-complete-profile-seed1ed712/verify.py
python3.12 -I -B research/block-climb-complete-profile-seed1ed712/verify.py --write  # regenerates RESULT.json
```

Expected final line:

```text
PASS_BLOCK_CLIMB_COMPLETE_PROFILE controls=26 charged_groups_excluded=100 free_groups_open=50 budget_rank1=10
```

`make_meta.py` regenerates `TASK.json` (its `draw_card` reads the full catalogue
card object) and `SOURCES.json` pins. `verify.py` is read-only without
`--write`; it recomputes every number from the pinned inputs.

## Scope and inherited obligations

- **Covered.** The cost-alphabet model of [PR 1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)
  (width 73, 896 families per nine stages, centre charge 64, idle mass 1,646,
  halving guard `R = 51`) with PR 1429's transport charge and PR 1605's
  added-work contract (no old idle credit). The `k = 2` and `k = 3` identity
  fixtures are exact; the per-group grid is exhaustive over `k = 2..51`,
  `alpha in {0, 1, 2}` and three `a` values.
- **Not covered.** Word-level realizability: which of the selected word's
  actual 2,412 rank-one children share frames (the zero-charge question);
  joint replacement of the rank-2/rank-3 frame-step children (PR 1605 open
  question 2); any changed coverage law, template, port count or centre path;
  masked or overcomplete support families, which would change an assumption of
  the eight-term all-pairs bound instead of this one.
- **Claims.** A scoped exclusion of the charged block-climb family and exact
  per-group budgets. Not a supplier, not a lower bound on all decoders, not a
  formal proof of the multiplication theorem. The ceiling comparisons grant
  overhead old idle credit where that is legal, which is favorable to the
  construction; the moment screens use PR 1605's stricter contract.

## Provenance and credit

- [PR 1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605) by Arham Tahir
  (`research/complex-rank-one-block-budget`) is the direct predecessor: the
  integer block budgets, the `a*` target and the `k = 363` threshold are its
  results, reproduced here as controls. Its open question 1 asks for a concrete
  rank-16 block decoder with fewer than one added paid call per output block;
  this package prices the frame transports and restoration such a decoder must
  pay and excludes every charged variant.
- [PR 1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) by Doug Colkitt
  (`research/complex-local-word-ceiling`) supplies the retained ceiling engine,
  the packing ceiling `1690054109089/10^15` and the ideal lever budgets.
- [PR 1429](https://github.com/CrocSwap/integer-mult-bounds/pull/1429) by Ali Romman
  (`research/complex-block-rank-optimum`) supplies the transport-charge
  contract and the fixed-block moment results; nothing here reopens its scope.
- The binomial-tail enclosure method is reimplemented from PR 1605's
  `verify.py` as an independent cross-check of `ceiling.py`.

Apache-2.0.

## Open next questions

- **Do zero-charge co-frame climb groups exist among the selected word's actual
  2,412 rank-one payload children?** This is now the whole lever: only groups
  whose operand vectors already sit at one common rank-`k` frame, with owned
  gather slots, clear the complete-profile gate. A first step is to read the
  pinned t16 canonical word's per-child operand frames and partition payload
  pairs into co-frame groups, pricing only those. The blocker is that the
  per-child frame data lives in the pinned word archives
  (`t16/global/base/providers/gauge44`); extracting and classifying it is a
  separate data pass not attempted here.
- **What complete profile results if a block climb also replaces the word's
  rank-2/rank-3 frame-step children?** Rank-one-only reblocking cannot reach
  `a = 1/99`, and the step children are the "rank-1 to rank-3 steps" the card
  names. A first step is to declare the joint replacement contract and its
  coverage identity before any synthesis. The blocker: the coverage identity
  fixes paid mass at `72w + 64` per call, so moving step mass requires a proved
  replacement identity.

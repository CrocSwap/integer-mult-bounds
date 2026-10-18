# Exact geometry filtering and retired-slot order

This is an equivalence argument for the source-pinned finite compiler in
`SOURCE.json`. It changes its implementation cost, not its mathematical
construction or any conditional exponent. It assumes the pinned compiler's
frame and control-flow contracts. The runtime tests are finite corroboration,
not a formal proof of the full multiplication theorem.

## Membership invariant

Let `S` be the retired physical slot set. A slot `s` has current rank `r_s`
and current original-envelope frame `(c_s, u_s)`, where `c_s` and `u_s` are
coordinate subsets of `{0, ..., h-1}`. The index maintains:

- `all_mask`: exactly the slots in `S`;
- `masks[r]`: exactly the slots in `S` whose current rank is `r`;
- `core_masks[i]`: exactly the slots in `S` for which `i` belongs to `c_s`;
- `union_masks[i]`: exactly the slots in `S` for which `i` belongs to `u_s`.

Each bit position is a physical slot ID, not a coordinate ID. All masks start
empty. Adding and removing a retired slot sets or clears its rank bit and
toggles exactly its frame-coordinate membership bits. An idempotent duplicate
add leaves the masks alone. Removal of an absent member raises `KeyError`.

The adapter inserts `move` immediately before the original `raise_` updates
`frames[s]`. Thus the callback still sees the old frame. For a retired slot,
the rank masks change if the rank changes, and coordinate bits toggle exactly
on the symmetric differences of the old and new core/union. Nonretired slots
do not enter the index. Changes within the same rank still update geometry.
The original frame-containment assertion remains before this hook.

In particular, clearing changes **both** the chosen destination's frame and
each retired source anchor's frame. Both changes pass through the same
`raise_` hook. Removing the chosen slot after clearing uses its new frame.
This is the subtle update obligation already identified by Chafik Boukhalfa's
PR175 ordered-bucket implementation.

## Exact eligible set

For a requested frame `(c, u)`, the original predicate is

```
not (c & ~c_s) and not (u_s & ~u)
```

Equivalently, `c` is a subset of `c_s`, and `u_s` is a subset of `u`.
Therefore the eligible slot set is precisely

```
S intersect (intersection of core_masks[i] for i in c)
  intersect (intersection of complements of union_masks[i] for i outside u).
```

The index computes this expression with integer bit operations. Starting from
`all_mask` bounds every complement to existing slots. `outside` uses the finite
`h`-coordinate universe; all caller frames come from the pinned constructor.
Empty intersections impose no extra restriction. No rank, span, source-access
or paid-frame criterion is approximated by this expression.

## Same order, same clearing, same word

Intersecting the eligible set with rank masks in descending rank order, and
extracting each integer mask's least significant set bit, enumerates exactly
the eligible subsequence of `sorted(S, key=(-current_rank, slot_ID))`.

The original `acquire` builds the same anchor basis first. An ineligible slot
is skipped **before** `ins(s)`, so omitting just those slots cannot change the
basis. Each eligible slot reaches the unchanged elimination in the same order.
Consequently the first dependent candidate, its exact clearing expression,
every clearing XOR, and any decision to allocate a new slot are identical.

The loop performs no frame or set mutation while searching. Once it finds a
dependent candidate, it clears the slot, removes it and returns immediately.
The generator is never resumed after that mutation. Its partially consumed
mask therefore cannot affect a later query. The standalone index does not
promise general mutation-during-iteration semantics.

Induction over the unchanged compiler operations gives identical slots,
frames, paid events, XORs and final receipts. The original per-slot containment
test, rank/width accounting, full input and dirty-basis replay in both
orientations remain enabled. No witness, helper or recursive child is removed.

## What is tested

The package checks complete equality to the frozen decompressed words at
`h=23` and `h=25`, not just summary counts. Independent serialized-word replay
and event reconstruction consume the newly generated word. An untimed run
also compares **every complete eligible candidate sequence** against an
ordinary sorted-set oracle using the current original frames.

Separate tests exhaust all pairs of three-coordinate envelope frames, then
exercise additions, removals and frame changes with seed 85, including sparse
physical IDs as large as 40,337. Stale frame updates, stale removals, wrong core
or union masks, and wrong rank masks have explicit negative controls. Source
drift, ambiguous edit sites, disabled assertions and reused output paths fail.

The `h=23/25` tests do not assert a theorem for every future compiler or graph.
The adapter refuses changed source pins. Inherited all-size compilation,
physical realization, hosting, residual, precision, tape, recovery and analytic
transfer obligations remain outside this tooling contribution.

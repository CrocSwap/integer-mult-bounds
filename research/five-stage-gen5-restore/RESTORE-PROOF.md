# Early restoration of 440 gen5 cleanup helpers

This is PR280's early-restoration lever (gen4, `docs/cleanup-proof.md` there), re-derived on the gen5 word after the
descent, target-square, kernel and second-descent stages, and admitted in the Python five-stage package.

## The rewrite

At record 601,802 of the stage-4 word, the first `cleanup_gate` ADD, every data target already has its scalar endpoints and
no COPY/ERASE follows. There are 440 helper roles `a` with, checked against the complete remaining word by
`restore_transform.transform`:

* the only later scalar incidence of `a` is one write `a -= c·b` (as destination or source, from the cut on);
* the donor `b` is not written between the cut and that gate;
* all 440 helpers and all 440 donors are distinct and the two sets are disjoint;
* at the cut both roles sit at 22-dimensional frames whose rational span `E` is a nondegenerate 23-dimensional frame
  (cleared Gram determinant nonzero; `E` is registered through the package's frame registry and its determinant is
  evaluated by `prime_check` with every other actual basis);
* `a` has a rank-20 entrance σ ⊆ E and previously retired at the full frame.

Every gate strictly between the cut and the original position is an ADD `x += c'·y` with `x ≠ a`, `y ≠ a`, `x ≠ b`, so
`a -= c·b` commutes with each of them over the integers. Moving it to the cut therefore preserves the exact signed scalar
operator on every source, target and dirty column; the transform checks that the multiset of scalar events is
unchanged, that the prefix before the cut is byte-identical, and that the suffix is the old suffix with the 440 writes
deleted. `scalar_check` then replays all 19,406 formal columns forward and inverse on the emitted word with its
corruption controls, and the finite row bounds are recomputed and pinned (`forward_max_row_l1`, `inverse_max_row_l1`).

For each pair the transform advances `a` and `b` from their frames at the cut to `E`, emits the unchanged ADD at `E`,
and retires `a` at `E`; `b` continues in its original order and later reaches the full frame. All MOVEs are rebuilt
from the actual gate needs; nesting, data endpoints, COPY lifetimes, nondegenerate endpoint bases, both reflected
annihilator ledgers and the exact integer source span of both operands inside `E` are checked as in the descent stage.
Per pair two rank-2 climbs become three rank-1 climbs, so the local paid histogram changes by {1: +1320, 2: −880}, 440
local calls are added and the local rank mass drops by 440 (410,334 → 409,894).

## Five-stage admission

A helper with entrance σ (dim 20) that retires at `E` (dim 23) changes content only in the residual `E ∩ σ^⊥` of rank 3
(PR280: "the helper endpoint changes from D_(FULL−σ) of rank 4 to D_(E−σ) of rank 3"). Its single direction `E^⊥` is
never touched: all of its frames are nested inside `E`, so no operation on any of the five stage copies has a component
there. The package treats that direction exactly like the entrance: it is completed with σ. Concretely,

* `global_lowering.Lowerer` reads every helper's endpoint from the actual records, requires it to be declared by the
  physical census (`helper_endpoint_frames`), and emits the completion of such a helper with rank 5·(dim σ + 24 − dim E)
  = 105 instead of 100. The one-replica deficit identity `LIVE·120 − rank mass = 4400` is unchanged because the five
  rank units leaving the helper chains enter the completions;
* `geometry527` checks on an actual restored helper that `P_σ + I − P_E` (completion) and `P_E − P_σ` (residual) are
  exact commuting projectors over the five windows with traces 105 and 15, product zero and sum the identity;
* `bank_check.census` assigns bank families by the actual residual width dim E − dim σ, so the 440 restored helpers are
  width-3 families beside gen5's 354 rank-21 entrances, and builds their charts from the pair (σ, E): residual rows = an
  integer basis of the G-orthogonal complement of σ inside `E` (3 rows), idle row = the cleared annihilator of `E` (1 row),
  source rows = the basis of σ (20 rows); the 24×24 chart is inverted exactly, its factor program replayed, and the
  projector onto the residual block checked as before. `bank_template.build_patterns` moves the 60 replicas of each
  restored helper from the (4³⁰) banks to the (3⁴⁰) banks: 3,484 and 1,191 banks per stage, both integral;
* `math_check` and `finite_check` remove the completions (entrance + idle) from the priced histogram, so the priced
  literal stock drops by 1,100 families (1,244,515 → 1,243,415) and `120·stock − literal mass = 264,000` still holds.

Every count the stage changes is a recomputed pinned value (`restored_helpers`, `restore_five_stage_calls`,
`completion_rank_histogram`, `restored_endpoint_dimension_histogram`, `bank_families`, `literal_stock`, `banks_total`,
`priced_five_stage_calls`, `scalar_event_sha256`, `kappa`, …) in `expected/kernel-pins.json`.

## Not done here

The 7 helpers with two later writes (dimension 21 at the cut, span 23) and PR280's 60 transported dirty entrances are
not applied. Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0.

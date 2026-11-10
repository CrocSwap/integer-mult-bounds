# Literal total rounded scalar tables

**Result:** fixed-rational SCALE and ADD tables implement
`floor((a*m+floor(b/2))/b)` through the unchanged lifecycle executor,
including negative inputs and even-denominator upward ties. All 52 current
SCALE coefficients are compiled and bound to their 3,660 exact local source
tokens. The actual SCALE37480 by -2/3 now accepts the one-grid state that
the checked exact service rejects; for this coefficient every signed input
fits whenever W>=2. **No new kappa or complete caller admission.**

The source is DreamingOfClouds'
[CrocSwap/integer-mult-bounds#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936),
head `03626137d0bd57f09b0bf9597376183ce6fa9683`. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Six unchanged dependencies are
pinned by commit, path, Git blob and SHA-256 in `DEPENDENCIES.json`.

## What is new

The exact scalar predecessor rejects nonintegral grid results. The rounded
proposal in [CrocSwap/integer-mult-bounds#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937)
describes a multiply/MSF-division automaton and leaves a physical lifecycle
join and recount open. This package supplies a literal finite table, using
an LSF signed-residue prepass followed by an exact odd quotient and low-bit
discard. It does not relabel checked division or call host arithmetic on
runtime payloads.

`compile_rounded(op, coefficient)` in `tables.py` returns an immutable
transition table and a finite construction receipt. SCALE ports are
`(target, output_work, guide_work)`; ADD adds a distinct read-only source
after target. Tables contain only branch/write/unit-move/goto/halt/reject.
The unchanged `Controller.primitive` performs entry retirement, table
execution, head restoration and successful exit retirement.

All components are staged before the first public write. Valid fields
succeed exactly when the rounded outputs fit their original signed widths.
Detected failures leave the public target unchanged but may leave private
work and heads dirty/unrestored. Canonical numeric encoding, physical
frontiers, distinct tapes, initial public/context origins and contiguous
old scratch are explicit premises, not claimed malformed-input validators.

## Positive cost and coverage

Let R be the component count, `S=sum(w_i+1)`, `b=2^d o`, and A_0,A_1 the
old dirty physical work lengths. The proved primitive bound is

    512(S+1) + 64 d R + 7(A_0+A_1) + 16 Q_c

for physical tape actions plus flat-table control, including all head
movement, staging, copying and retirement; Q_c counts untouched borrowed
contexts. No additional work bank is needed. Resident backing retains
historical maxima, and positive finite source/table setup costs are
separate. This bound is not silently exchanged for the old supplier tariff.

The current 52-SCALE catalogue has 92,113 rows, at most 20,401 in one table.
Only 64 local SCALE occurrences need the residue prepass. The generic
ADD theorem shares the same algebra, but the 4,079 current odd ADD
occurrences are **not** constructed or installed here. The full recursive
source exporter, native providers and physical invoice remain open.

## Reproduction

```bash
python3 -I -B research/current-rounded-scalar-tables/verify.py --suite all
python3 -I -O -B research/current-rounded-scalar-tables/verify.py --suite all
```

Expected: four `PASS_CURRENT_ROUNDED_SCALAR_*` lines for SOURCE,
ARITHMETIC, HISTORY and CONTROLS. Each physical attempt has a 120-second
cap. Standard library only; package replay needs no Git, network or solver.

The independent integer floor/range oracle covers 3,224 current SCALE
cases, 2,380 small ADD pairs, and 1,020 exhaustive -2/3 inputs at widths
2..9. Additional tests cover dirty long-to-short reuse, late overflow,
retirement after failure including a live residue marker, borrowed contexts,
detected malformed shapes and three compiled arithmetic mutants. Separate
transparent observers check physical and finite-control cost. The proof,
rather than the finite width range, establishes all-size correctness.

`PROOF.md` gives the residue/sign/carry and lifecycle arguments;
`SOURCE.json`, `ARITHMETIC.json`, `HISTORY.json`, and `CONTROLS.json`
record exact coverage. `PR-DESCRIPTION.md` is the complete proposed text.

## Open next questions

1. Construct and price the remaining current ADD coefficient class, or
   replace the potentially large fixed carry graph with an equally literal
   economical method. The generic existence theorem is not that inventory.
2. Install the complete caller/recursive occurrence and row/format binding.
   This package registers exact local SCALE tokens only.
3. Bind the remaining native/Lambda/error/ownership contracts and assemble
   a common physical tariff, including source/setup, children and old backing.
4. Complete the rounded outer recovery obligations before deriving a new
   accepted multiplication bound.

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in
proof, implementation and testing. Credit DreamingOfClouds' #6936 source
and #6937 total RDiv proposal, CubeJerry's exact scalar and lifecycle
predecessors, and the source precision package published at
[`56bc9383594a3efc303148e00bb746851abd1ed5`](https://github.com/CubeJerry/integer-mult-bounds/tree/56bc9383594a3efc303148e00bb746851abd1ed5/research/query-only-precision-envelope).
Separate AI review is recorded honestly in `REVIEW.md`; it is not human
or proof-kernel verification. No selected certificate is changed.

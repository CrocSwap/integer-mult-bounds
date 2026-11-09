## What changed and why

The current odd word's exact scalar service rejects off-grid rational
results, including a permitted one-grid child defect immediately before
SCALE37480 by -2/3. A total rounded-child contract therefore requires a
different numerical service.

This package builds literal fixed-rational nearest-up SCALE/ADD tables
through the unchanged lifecycle Controller.primitive/execute_table ABI.
An LSF signed-residue prepass is followed by an exact odd quotient and
low-bit discard. Runtime instructions are only branch, write, unit move,
goto, halt and reject; there are no numerical payload callbacks.

All 52 current SCALE coefficients are instantiated and registered under
their 3,660 exact local source tokens. The actual -2/3 seam maps numerator1
to -1 and, universally, accepts every signed input for W>=2. The theorem
handles negative floor, even-denominator upward ties, widths smaller than
the discarded-bit count, signed endpoints and complete-field staging.

## Exact dependencies and novelty

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Source: DreamingOfClouds' CrocSwap/integer-mult-bounds#6936 at
`03626137d0bd57f09b0bf9597376183ce6fa9683`.
Credit the total RDiv proposal and abstract division automaton in
CrocSwap/integer-mult-bounds#6937. That note explicitly leaves physical
recounting/services open; this package provides a literal two-bank join,
not a claim to have invented rounding.

The fixed builder and exact arithmetic predecessor are published at
`13193a22b1070a74a8580c5d3ea27470443f815a`; the unchanged lifecycle at
`ab239cb6ee884e7a900dd9101c34448077fad0b0`. The source precision seam is
published in [the precision package at 56bc938](https://github.com/CubeJerry/integer-mult-bounds/tree/56bc9383594a3efc303148e00bb746851abd1ed5/research/query-only-precision-envelope).
Six unchanged dependencies have exact commit/path/blob/SHA-256 pins.

## Proof, physical checks and reproduction

```bash
python3 -I -B research/current-rounded-scalar-tables/verify.py --suite all
python3 -I -O -B research/current-rounded-scalar-tables/verify.py --suite all
```

The proof supplies signed residue correction, a bounded carry invariant,
final range iff, mathematical floor after low-bit discard, and whole-field
staging. Independent direct integer oracles cover 3,224 current SCALE
cases, 2,380 small ADD pairs and 1,020 exhaustive -2/3 inputs. Tests include
late rejection, dirty long-to-short reuse, failure-work retirement, context
preservation, detected malformed shapes and three compiled mutants.
Standard library only; no Git/network is required for package replay.

The positive physical/control bound is
512(S+1)+64dR+7(A_0+A_1)+16Q_c, with S the complete numeric extent,
R the component count, d the denominator's two-adic exponent, A_i old dirty
scratch lengths and Q_c borrowed contexts. It includes entry/exit erasure,
all passes, copying and head return. No extra bank is introduced; historical
backing and positive fixed source/table setup remain in the ledger.

## Scope, limits and kappa

**No new kappa. No full caller admission or unconditional theorem.**
The 4,079 current odd ADD occurrences are uninstantiated; the generic ADD
theorem and small fixtures are not their complete catalogue. Full recursive
source/row binding, other native/Lambda/error/ownership contracts, a common
physical tariff and rounded outer recovery remain open. The numerical
semantics are explicitly RDiv mode, not an unannounced replacement of the
exact-child or selected rule.

Input encoding, matching shape/grid, distinct tapes, origin public/context
heads and contiguous dirty work with blank historical tails are premises.
Detected failure leaves the public target unchanged but need not restore
heads/work. The source guard does not validate hidden dirt after a blank or
noncanonical encoded frontiers. The physical bound is not imported into
the old 10^9 tariff as an assumed exchange rate.

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in
research, proof, code and verification. Separate AI reviews are identified
in REVIEW.md and do not imply independent human or proof-kernel review.
No selected certificate or unrelated source is modified.

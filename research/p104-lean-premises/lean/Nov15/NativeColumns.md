# NativeColumns (Nov 17): narrowing `native_all_columns` of #7620

Kernel-only, 5 s / 1.7 GB, no sorry/native_decide; axioms within [propext, Classical.choice, Quot.sound].
File: `Nov15/NativeColumns.lean` (imports TokenCancel).

## What the "columns" are
In #7630's `check.py` the column test is NOT randomized.
For each affected chart pair (a,b) (operator F_a^dag F_b on 2^9 = 512 dims) it compares ALL 512 forward
and ALL 512 adjoint exact Gaussian columns (`for c in range(FULL)`, line ~563), plus tableau (signed
Pauli action), absolute phase, exact rank, and a wrong-phase rejection. So per pair it is an exhaustive
exact check, not statistical evidence. The residue is elsewhere (below). The premise scope note's item 3 ("complete
finite contact identities are not an all-column implementation theorem") is about the compiler half.

## Proved
1. Data-level semantics. `drun` executes a TokenCancel word on actual data in ANY K-module M
   (born reads input, add/scale/copy/clear/init as in `step`). `drun_eval`: result = final rows applied
   to the initial data. `all_columns_of_exact_rows`: (run s es).row = T => the word computes T x for
   every x in every M, i.e. every column count and every tensor power (the Kronecker/factorwise point);
   `word_computes` from identity start.
2. `exact_rows_iff_columns`: exact final rows <=> correct on every unit column (both directions), so
   "exact rows" is exactly the all-column statement for the Q-linear word model (what the local audit script's
   `all-column endpoint failure` check does with Fractions).
3. Column-test logic: `matrix_ext_cols` (unit columns determine a matrix), `linear_ext_span` (any
   spanning set suffices), `partial_columns_insufficient` (2x2 over Q: agree on column 0, differ: a
   subset test, random or not, is evidence only), `adjoint_iff_forward` (adjoint columns add NO coverage
   once forward is exact; they are a consistency check of the checker), `phase_visible` (a global phase
   c != 1 changes every nonzero entry: why the absolute-phase test is needed beyond the tableau),
   `census_coverage` (correct on census + used pairs inside census => all used pairs correct).

## How much this narrows the premise
Removes: the worry that the pair columns are only sampled (they are exhaustive: 512 of 512), that the
adjoint half is extra coverage, and the "all columns / all widths of the Q-word" half: an exact-rows
word (the local audit, CLEAR certificates) is correct on all columns by linearity (items 1-2).
STILL ASSUMED (not provable in this model):
 a. Census completeness: the 981 pairs (964 inherited from #7623 by hash + 17) cover every pair the
    native adapter is called on; `check.py` asserts `move_pairs(W) - move_pairs(B) <= allp` and the
    7623 inheritance, but that `move_pairs` is the right notion of "pair the adapter is used on" is a
    code fact (`census_coverage` only gives the logic).
 b. Operator realization: that the compiled native applies the verified recipe monomial.Fourier^r.monomial
    on complex 512-dim states with the verified phase; the Python checks Gaussian-dyadic arithmetic,
    Lean here is over a field K and does not model Pauli frames or complex phase.
 c. Compiler/implementation half: universal erasure/compile services, rounded precision (precision_tape),
    whole-job matching -- unchanged contract, as #7620's PR text says.
 d. The Python checker itself (tool fact); Lean did not re-run the 512-column test.
Net: the "identity over all columns" half is now a kernel lemma plus an exhaustive exact test; the
"implementation" half is untouched. No paper statement found false.

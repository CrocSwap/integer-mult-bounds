# Adversarial micro-review: sparse union extraction and batching

Reviewed `phase_layout_audit_ultra/AUDIT.md`, `CAPPED-SIGNOFF.md`,
`MATRIX-LAYOUT-SIGNOFF.md`, and `phase_assembly_ultra/phase_fusion_note.tex`
242–262 and 368–385. This is a read-only review of the candidate.

## Finding

I did not find a mathematical or fixed-tape counterexample to the no-sort
union construction. Its key structural requirement is genuinely enough:
each E_i is a fixed one-axis set within a complete microbox, and each sparse
factor is identity on E_i^c with no cross-block entries. The tests provide
less implementation evidence than their metadata suggests; that is an
evidence limitation, not a demonstrated exponent obstruction.

## Explicit stream argument

Filtering lexicographically ordered U by x_i in E_i produces the complete
rectangle in order [P][E_i][S], where P and S are the preceding and following
coordinate tuples. Completeness holds even when none of the other
coordinates is in its boundary set: the current coordinate itself puts
the record in U. Increasing ordinal renaming of E_i preserves this order.
The ordinal counter must advance on changes of the i-th coordinate and
reset on changes of P; it must not increment on every payload record.
These changes are available in the retained O(g log L)-bit coordinate
header. No rank data structure or growing-key sort is needed.

The retained tape construction at
`integer-mult-current/references/semantic-bulk/rad20/reports/bulk-resampling-tape-transfer.md:21–46`
explicitly supplies [B][2][R] <-> [2][B][R] by two streaming work tapes,
including rewinds and arbitrary external prefix fibers. Applied bit by
bit, it moves a k-bit field across an arbitrary spectator block in k full
passes. Consequently [P][E_i][S] -> [P][S][E_i] and back cost
O(|U_i| p log L) bit work. For non-dyadic |E_i|, pad this field only to its
next power of two, transpose, then delete the padded positions; temporary
volume is below twice |U_i|. Restoring the original field order restores
the coordinate order required for a two-tape merge into U. Neither the
extraction nor the merge needs a permutation on the whole union.

Writing mu=max |E_i|/L, the scans cost O(V g^2 mu), and all local
transposes cost O(V g mu log L). With mu=O((W/B) polylog p), this gives the
stated per-group O(V g^2 W/B polylog p), and total
O(V d g W/B polylog p). This conclusion does not depend on g being smaller
than a source-axis bit width.

## RHS batches and factor traffic

After exposing the row field, denote the independent RHS count by R.
Let q be dyadic with W<=q<2W and split the contiguous RHS enumeration
into [R_hi][q]. The required layout is [R_hi][row][q], obtainable from
[R_hi][q][row] by the same small-field transpose, whose field width is
O(log p); no O(log R) sequence of passes is needed. The final incomplete
batch can be temporarily padded. Batch-boundary arithmetic is paid in
the boundary volume.

For z boundary rows and bandwidth O(W), one batch scans O(zW) factor
entries. There are O(R/W) batches, so factor IO is O(zR) coefficient
records. The block-product arithmetic is O(z R W^(omega-2)) scalar
operations and dominates this IO. The retained seven-product recursion
has recurrence 7 T(W/2)+O(W^2) for local matrix copying and additions, so
its fixed-tape local rearrangements do not insert another W factor.
Polynomial factor preparation is separate and is amortized over the
superpolynomial RHS volume as stated in the candidate.

## Finite-check limitations

`check_union.py:54–70` uses coordinate-keyed dictionaries for gathers,
matrix applications, and updates. It checks exact tensor algebra, support
closure, and complete rectangle cardinality, but does not simulate the
stream counter, single-field transpose, ordered merge, or batching.
Its only case has g=2 and |E_i|=8, so it also does not exercise non-dyadic
padding or a middle field in a higher-dimensional tensor.

Moreover, `check_union.py:81–85` invokes `union_window` separately for the
C and S^-1 stages, and each invocation gathers and scatters U. The
`physical_sparse_windows=2` and shared-gather-reuse fields at lines 98–99
are asserted metadata, not properties established by that execution.
Keeping U between the two consecutive sparse stages is nevertheless
valid by the algebraic closure proof. Even the tested three-window
schedule differs only by a constant number of scans, so this discrepancy
does not refute the exponent.

No candidate file was changed. I have not re-proved the separate Gaussian
conditioning, effective matrix exponent, or support-router hypotheses.

# Independent exhaustive H6 Walsh audit

The Walsh identity and binary rank in the H6 proposal are correct on its
30,960 selected E8² ports. This audit upgrades the proposal's sampled parity
and compensation checks to exact checks of all **958,521,600 ordered pairs**,
including the diagonal, and supplies an algebraic rank argument.

The frozen proposal is DreamingOfClouds' `h6-banked-breakeven` at
`b496aed769dd724cd1ff6b921cade626562be27b`. Its `walsh.py`, `structure.py`,
`README.md`, and the inherited `niemeier-lattices/code/e8_cubed.py` were compared
byte for byte with that Git object. Their hashes are recorded in `results.json`.
The audit checkout is based on CrocSwap main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`; the frozen H6 files were extracted
separately. The geometry is attributed to Dominik Scholz's PR606. This independent
audit was prepared with OpenAI Codex assistance under Apache-2.0.

## Reproduction

From the repository root, using Python >= 3.11 and NumPy:

```sh
python3 -B research/h6-independent-audit/walsh/audit.py \
  --output research/h6-independent-audit/walsh/results.json
```

The audit generates the selected ports directly from the frozen geometry; it
does not consume `b214_P.npy` or any of the proposal's saved result text. It
imports only `construct_shell()` and independently implements binary elimination,
rational inversion, exact scalar identities, and the complete pair replay.
The default chunk size is 256 rows, keeping the billion-entry matrix unallocated.
Runtime and environment are recorded in the result; the full replay is practical
on a local machine. The exact `np.save` SHA agrees with the proposal's
`349e8466...911fd` artifact; a canonical little-endian integer payload SHA is also
recorded to avoid treating a container header as mathematical content.

## Exact identity and signs

Let `P` be doubled coordinates, `X=P/2`, `T=XXᵀ=PPᵀ/4`, `t=T_uv`,
`B_uv=t mod 2` in `{0,1}`, and

\[
K_{uv}=\frac{t^3-4t}{48},\qquad
E_{uv}=\operatorname{sgn}(t)\,\mathbf1_{|t|=3}.
\]

The norm condition and Cauchy–Schwarz give `|t|<=4`. Canonical antipodal
orientation excludes `t=-4`; equality `t=4` occurs exactly on the diagonal.
All attainable values are the eight integers `-3,-2,-1,0,1,2,3,4`.
For even off-diagonal values, `K=0`; for `t=±1`, `-K=t/16`; and for
`t=±3`, `-K=-5t/48=t/16-(1/2)sgn(t)`. On the diagonal `K=1` and `B=0`.
Therefore, including every diagonal entry,

\[
I-K=\frac{T\circ B}{16}-\frac12 E.
\]

The replay checks the integer equation
`48 δ_uv + 4t − t³ = 3t B_uv − 24 sgn(t) 1_[|t|=3]` everywhere.
It also checks integer divisibility before dividing raw dot products by four,
the exact diagonal, the complete pairing histogram, and exact support.
There are `480,337,920` nonzero entries, with row degrees `15,488–15,872`.
The `|t|=3` correction has `3,363,840` nonzero entries, approximately `0.700%`
of the compensation support. This is a support fraction, not a cost fraction:
the correction is still present on over three million ordered pairs.

Defect-sensitive scalar controls cover every attainable `t`. Omitting the
correction causes maximum error `1/2`; reversing its sign causes maximum error
`1`; using the raw doubled-coordinate dot product in place of `t` causes maximum
error `9/16`. These controls demonstrate that the normalization and exceptional
term are substantive.

## Algebraic binary rank 16

The independently selected E8 root indices
`[0,1,2,6,12,20,30,42]` give an eight-row doubled-coordinate matrix `Q`.
Its integral Gram matrix `G=QQᵀ/4` has exact determinant **1**. The exact integer
inverse is recorded. Thus the physical roots `Q/2` form a real basis and their
pairing coordinates give, for any two E8 vectors `x,y`,

\[
x\cdot y=(x(Q/2)^T)\,G^{-1}\,(y(Q/2)^T)^T.
\]

Every selected port has integer pairing coordinates with this basis, checked
without rounding. Reducing the displayed exact identity modulo two is legitimate
because `G^-1` is integral. With two orthogonal E8 blocks this yields

\[
B=LML^T\quad\text{over }\mathbf F_2,\qquad
M=\operatorname{diag}(G^{-1},G^{-1})\pmod 2.
\]

`M` is symmetric, alternating, and invertible. `L` has binary rank 16, with exact
row witnesses in the result. Consequently `B` has binary rank exactly 16: the
map `Lᵀ` is surjective, `M` is invertible, and `L` is injective. This is an
algebraic statement for the whole selected shell, independently backed by the
complete entry replay.

The audit additionally recovers the exact principal minor chosen at trial zero
by the proposal's seed-3 generator and checks its original `L M Lᵀ` convention
on every ordered pair. Its inverse and selected indices are retained in the
result.

There are `14,670` distinct labels: `14,400` have multiplicity 2 and `270` have
multiplicity 8. The canonical root shell has 120 distinct labels. The norm-four
E8 line shell has 135 distinct nonzero labels, each occurring eight times;
these are disjoint from the root-label set. Hence root × root ports contribute
`120²` labels with two sign choices per label, and single-block ports contribute
`2×135` labels with multiplicity eight. Both the constituent counts and the
combined histogram are checked exactly.

**Binary rank is not a real-rank claim.** Neither rank 16 over F2 nor label
duplication supplies a rank-16 real decomposition, a count of physical helpers,
or a restoration/loading schedule.

## Walsh normalization and coordinate factors

For any of these alternating coordinate conventions define
`W_uv=(-1)^(l_u M l_vᵀ)`. Then `B=(J-W)/2` as an entrywise real identity.
The full label-space matrix is indexed by all `2^16=65,536` labels; it is a
standard binary Walsh matrix with a bijective column permutation induced by `M`.
The audit enumerates all 65,536 labels, checks that permutation, and computes
all 65,536 binary character sums by an exact integer fast Walsh transform.

For full label-space rows `a,b`,

\[
\sum_z(-1)^{(a+b)Mz^T}=65,536\,\mathbf1_{a=b}.
\]

Thus `W_full W_fullᵀ=65,536 I`, and the orthogonal normalization is
`W_full/256`. The port-indexed `W` is a row-and-column restriction with repeated
labels; it does not inherit that full-space orthogonality.

For coordinate `c=1,...,16`, let `D_c=diag(X_:c)`. Then entrywise

\[
T\circ B=\sum_{c=1}^{16}D_cBD_c,
\qquad
I-K=\frac1{32}\sum_{c=1}^{16}D_c(J-W)D_c-\frac12 E.
\]

The coefficient changes from `1/16` to `1/32` when substituting `(J-W)/2`.
The coordinates in `D_c` are `P/2`, including half-integers; using `P` changes
the Gram term by a factor of four. These identities describe structure but
do not price label aggregation, diagonal weights, transform chronology,
exceptional restoration, or bank occupancy.

## Scope and open next questions

This is one finite structural verification and a scoped algebraic proof. It
does not independently audit the predecessor's rank-816 real kernel spectrum,
prove an arithmetic DAG, establish helper capacity, or improve κ.

- Build an exact circuit trace for label aggregation, all sixteen weighted
  Walsh applications, and the exceptional term. First step: implement the
  action on a small exact input and retain every intermediate lifetime. The
  missing blocker is a bank-compatible restoration schedule.
- Determine whether the exceptional `|t|=3` relation admits additional reuse
  under the root × root / single-block partition. First step: give a source-bound
  exact factorization and independently replay it. Sparse support alone does
  not establish a low helper cost.
- Compare a completed loading/restoration invoice with the proposed break-even
  budget. First step: enumerate physical helper paths and exact demand, including
  weighted transforms and chronology. A label count or operation count alone
  cannot discharge that capacity obligation.

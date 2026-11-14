# Independent adversarial review of capped phase fusion

This is an independent review of the algorithms and their growing-parameter
costs, not merely of the parameter arithmetic. It does not certify the finite
suppliers or turn a conditional multiplication statement into an unconditional
one. The exact reviewed core-source hashes are in `CORE-SOURCES.json`.

## Current disposition

No blocking gap found in the shallow Toeplitz compiler, the growing-g tensor
compiler, the support-local deferred supplier transfer, Gaussian precision,
or sparse layout, conditional on the interfaces stated in
`phase_fusion_note.tex:60-65`. The completed Gaussian and sparse-layout
reviews are `gaussian_layout_review.md`, `layout_subreview.md`, and
`union_subreview.md`, and must be read with this report.

The additional matrix-exponent corollary is conditional on its additional
matrix exponent premise. The effective algebraic-coefficient transfer in
`phase_fusion_note.tex:327-345` does not itself introduce a further unproved
uniformity assumption: strict exponent slack permits one fixed finite formula,
its coefficients can be algebraic and computable, and recursion has only
polynomial-in-W error and magnitude amplification.

## 1. Shallow Toeplitz construction

I checked the identities and the norm mechanism in the complete
`work/inplace_algebra_ultra/SHALLOW-TOEPLITZ.md`.

* Lines 25-39 implement a dirty Toeplitz shear by circulant and negacyclic
  shears. They invert FFTs, never Fourier multipliers. A singular Toeplitz
  multiplier therefore causes no illegal inverse, and no clean coordinate is
  used.
* Lines 43-73 give a genuinely parallel triangular recursion. The Schur child
  `e-z o^2/e` and the two shears give the stated parity block exactly. Children
  are restrictions/Schur complements of the original near-identity matrix,
  so their norms do not acquire a new multiplicative condition factor at every
  depth.
* Lines 77-111 use `ZM-MZ` displacement. The displayed Schur displacement
  differs by one rank-one boundary term, giving additive rather than
  multiplicative rank growth.
* Lines 115-139 turn each bounded Stein generator into four operations using
  `P=I+U(h)/gamma`. The subtraction restores x and cancels the unwanted
  `gamma L(g)x`. Intermediate generator sums add; treating their norms as a
  product would be an unjustified pessimistic bound, not an actual failure.
* Lines 145-158 separate long offline exact rational calculations from online
  bounded coefficients and establish polynomial prefix and suffix norms.
  This is essential: merely citing an arithmetic operation count would not
  have supplied an O(p)-bit data algorithm.
* For the SPD extension, lines 188-197 correctly bound principal Schur
  complements using the principal-block inverse identity. The log-prefix
  budget is `O(log N log(2+M+1/mu))`, which is sufficient for the actual
  Gaussian spectral bounds.

One nonblocking wording error was found and corrected by the parent author
during this review. The original `phase_fusion_note.tex:103` wrote a general
SPD prefix bound using only the condition number M/m. This omits absolute
scale. For example,
`G=exp(-p) I` has condition number one but inverse-prefix norm at least exp(p).
The supporting proof at `SHALLOW-TOEPLITZ.md:194-195` has the correct
`log(2+M+1/mu)` expression. The current phase note now uses that expression and
requires both M and 1/m polynomial in p. The actual Gaussian has those bounds,
so the correction does not change either claimed exponent. Both pre-correction
and final source hashes are retained in the source manifest.

## 2. Growing-g tensorization

I read all of `work/inplace_algebra_ultra/TENSOR-COMPILER.md` and checked the
following potential failure points.

* Its exact six-H words cover zero shears: `t+c` and `-c` are bounded away
  from zero, so the diagonal inverses do not divide by the original t
  (lines 31-60).
* The Beneš route uses identical bit schedules across axes and coarse labels.
  Switch controls, including inactive pairs, are diagonals. Thus a common
  global H call really exists even when every local circuit differs
  (lines 62-97).
* The Kronecker equality at lines 89-95 is literal multiplication of tensor
  factors. It introduces neither a sum of 2^g subproblems nor padded tensor
  dimensions.
* Completed route/identity words have exact norm-one or identity endpoints;
  only one local word is unfinished at a time. Local prefix bounds therefore
  do not multiply once per compiled stage. Tensor norms do multiply across g,
  but their logarithms add to the explicitly charged `O(g polylog p)`
  (lines 99-110).
* The suffix-product odometer (lines 114-132) is a valid fixed-tape amortization,
  not a RAM lookup assumption. A carry visiting k tables costs O(kN), and its
  frequency is at most V/N^k. Table initialization and polynomial generation
  must be charged per visited coarse block; lines 130 and the phase note
  283 explicitly do so. Since g grows, N^g dominates every fixed polynomial
  setup cost. No extra gV diagonal row is forced by this implementation.

The supplier is called globally, across complete coarse-coordinate ranges,
and exposure is undone before a label-dependent diagonal is evaluated. The
distinction made at `phase_fusion_note.tex:120-134` and 260-262 is essential.
A separate supplier call inside one fixed coarse-label microbox would not
satisfy the complete-neighborhood hypothesis. The actual schedule avoids that
invalid call.

## 3. Deferred reservations and support-local routing

I read the whole support audit and router, and checked their main claims
against the primary compact-control and whole-child sources.

* `compact-control-movement.tex:149-154` is the only use there of the stronger
  asymptotic K/log p condition: it obtains a finite guard inequality and an
  O(p^-3) bad density. K=128G directly satisfies that finite inequality.
  The tightened hypothesis is therefore legitimate for this use.
* `compact-control-layout.tex:30-62` supplies whole-row splitting and exact
  identity on arbitrary dirty reserved coordinates. It does not require the
  earlier individual C operations in order to make the active invocation
  legal. Deferring those reserved selected bits preserves the tensor target.
* `whole-complex-concatenation.md:102-139` and the leading-row qualification
  use the PRODUCT of nested bit and complex row stocks. The new audit retains
  this product. It does not replace it by a maximum. The required number of
  complete reserved chunks is O(log h), and the three compact fields use at
  most 3h/128+O(1) chunks, so the eventual h/16 contraction is valid.
* A requested mapping of k bits can be extended on S union T, moving at most
  2k positions (`SUPPORT-ROUTER.md:128-140`). It is unnecessary to stably
  compact all coarse fields.
* The unequal-gap XOR algebra at `SUPPORT-ROUTER.md:23-81` uses only disjoint
  guard intervals, not equally spaced targets. Distinct sources outside the
  target set remain unchanged between loading and unloading, even if they
  lie in guards. Every elementary operation is bijective, and the ideal map
  preserves the bad predicate, validating exact bad-address repair.
* The fixed-size reservoirs are reserved before target coloring, and target
  positions are recomputed after placement (`SUPPORT-ROUTER.md:92-109`). This
  avoids a circular bound based on a residue class before its layout changes.
* For short records, the suffix conjugation at lines 112-125 is valid.
  Conjugation preserves moved-support cardinality. Choosing an untouched
  log^2 p-bit field and routing on the complementary prefix leaves a complete
  superpolynomial record; control reservoirs are chosen inside that prefix.
  This pays polynomial descriptor arithmetic without spending an entire
  long original axis or introducing new data.
* Individual K-neighborhoods fit one per original axis because
  `p^(1-epsilon)/log p -> infinity`. Their aggregate and all helper reservoirs
  fit the full address because beta<1. There is no necessary constraint
  beta<1-epsilon; a group is allowed to be wider than one original axis.
* The width-dependent phase sums are geometric. With q<a_eff, both the
  deferred h^(1-q) calls and their h^(1-a_eff) exposure costs sum to
  O(g^(1-q) polylog p). Raw-H normalization contributes O(g) extra guard bits
  per call, already included in O(g polylog p).

This part remains conditional on the paid arbitrary-width equal-chunk
interchange, exact mutable-source/common-frame realization, and semantic
precision guard. The finite suppliers alone would not establish those
interfaces.

## 4. Matrix-exponent transfer and arithmetic replay

I read all of `work/matrix_boundary_ultra/ALGEBRAIC-STABILITY-INDEPENDENT.md`.
For fixed strict slack above omega, a finite exact rank formula exists.
Its finite polynomial rank equations over Z have an algebraic solution by
the Nullstellensatz. Enumerating algebraic tuples with exact tests is an
effective terminating fixed setup, even though the constants are unusable.
For this fixed formula the coefficient count, degrees, heights and root
separation are constants. Fixed-point bilinear recursion has O(log W) levels
and polynomial-in-W norm/error growth, so O(P+h+log W) bits suffice.
Consequently the per-bit charge M(p)/p in the phase note is the correct one.
None of this proves the extra omega<=9/4 premise itself.

The independent Gaussian/layout reviewers re-derived the narrow row-gap
bound, the distinct broad finite-LDU inverse bound, exact capped reanchoring,
principal-window Neumann locality, and row-DD boundary-solver residual bound.
They found no blocker. They also checked that the sparse union is regathered
after dense stages, that its complete U_i rectangles need only a single
polynomial-width field transpose, and that the matrix corollary does not
require a full-key union sort. Position-dependent halo copying is justified
by interval geometry with original input provenance. See their reports for
the source lines, proof calculations, and independent finite controls.

Their one evidence limitation is nonblocking: `check_union.py` uses
dictionaries and does not execute the claimed tape transposes or shared
two-window schedule. The written closure and tape arguments supply the
missing implementation reasoning; extra separate gathers would in any case
change a constant, not the claimed exponent.

I independently reran `check_capped_outer.py` and
`check_matrix_corollary.py`. They report respectively 44 and 47 positive
strict slacks with the stated rejecting controls. This checks the ledgers
only. The algorithmic review above is independent of those PASS strings.

I also reran `check_exact_algebra.py` (340 parity entries and 26 Schur nodes),
`check_sparse_shear.py` (32,768 exhaustive addresses plus 4,000 generated
addresses), and `check_tensor_compiler.py` (all permutations through N=8,
300 larger random permutations, exact fixed words, two-axis tensor replay and
growing-g odometer examples). All passed. The tensor control required the
existing `work/bit_supplier_ultra/venv/bin/python` because the system Python
does not contain SymPy; no dependency was installed or changed.

## Claim boundary

The findings support the same-assumption conditional exponent
0.001672922349588871 and, if the additional matrix-exponent premise is
granted, 0.001673360105405778. They do not establish an unconditional
integer-multiplication improvement, a practical cutoff, or a drastic
asymptotic gain. The absolute savings beyond 0.001672660197076918 are only
2.62152511953e-7 and 6.9990832886e-7 respectively.

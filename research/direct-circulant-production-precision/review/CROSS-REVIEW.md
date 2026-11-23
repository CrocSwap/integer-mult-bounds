# Independent review of the direct-circulant precision selector

**Verdict: accept the stated local numerical theorem under its named source
contracts, after the factor-count clarification below.** No blocking error
was found in the selector, interval estimates, odometer induction, bootstrap
or stated recovery corollary. This model-assisted review is not human peer
review, formal-kernel acceptance or admission of the complete multiplier.

Review scope: wave 2, track 77, canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`, package
`research/direct-circulant-production-precision`, and Ali Romman's #7849 at
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd`.

Initial proof SHA256:
`46b6651555dde18253c3f20220e455767acb970a0c459bdc09a3bd1f15a3698a`.
Accepted proof SHA256:
`26e4e214f0a5785c1d1414561465bb49a3248f9e6f59f6b514eb95a887bdfe2f`.
Only the two prose sentences giving the fully expanded factor census changed.
The selector, exponent envelopes and checker were unchanged.

## 1. Accepted quantifiers and retained premises

For every d>=1, true sides 2<=r_i<=t_i=2^ell_i, ell_i>=1, integer p>=1,
and represented complete padded tensor x with max |x_j|<=1/2, put

\[
L=\sum_i\ell_i,\quad E=\lceil1257L/2\rceil+2154d,
\quad A=104L+438d,
\]
\[
J=20000(d+1)(\max_i\ell_i+2)^6,\quad
C=4J(d+1)^2+d+1,\quad P=4p+A+2E+\operatorname{bitlength}(C).
\]

Using P in the external Grid and P+8 in fourier_axis gives error strictly
below 2^(-4p) against the tensor Fourier mean, with identity on each local
hole block, for both source signs. The following contracts remain premises:

- The exact-unit rational phase oracle has its certified error at every
  requested precision.
- The padded-root rank/conditioning adapter is in the full compiler's
  applicability class, and the retained compiler has its explicit exact-word,
  fragment, prefix/inverse-prefix and layer estimates. The precision package
  instantiates those estimates; it does not re-prove that entire compiler.
- The native H service is exact on represented words on a sufficiently
  widened private grid, with its complete-field restoration contract.
- The pinned lowering and coefficient/data arithmetic are the actual source
  execution. They are not an arbitrary dense transform at unit cost.

The recovery corollary additionally retains the source CRT character, true
volume S<=B, no-wrap condition, radix scale 4B, p=6 log_2 B, B>=32, and
public toward-zero conversions. The actual Multiplier wrapper further
restricts its geometry, including a power-of-two axis count; the local
TensorWord numerical theorem does not claim that wrapper accepts every d.

## 2. Exact source boundary and independent method

I read all six vendored scientific files, the new proof and selector, and
canonical FULL-PROOF.md. I independently fetched #7849's PROOF.md,
ROOT-CIRCUIT.md and COMPOSITE-OUTER.md at the exact head. Their bytes agree
with the author's reference copies; API Git blobs and SHA256 hashes are in
UPSTREAM-PINS.json. The canonical full compiler proof SHA256 is
`acf8c596d91b5efd35a286735d6867ff8afce64354a13f680c2fae3dab824410`.
Its (12), (13), (14) and (15) explicitly provide the coefficient defect,
physical-cut decomposition, prefix/suffix and inverse estimates, and depth.

I did not run check_precision.py as independent evidence. The separate
check_review.py extracts named literal source functions, uses a new
Gaussian-rational matrix interpreter, and uses noncommutative expression
trees for the odometer. It imports neither the author's precision engine nor
the compiler matrix class. READ-BOUNDARY.json and FINAL-BOUNDARY.json preserve
initial and final review hashes.

## 3. Column guard, leading sections and endpoint synthesis

The source bit binding is correct: fourier_axis receives P+8; cap=1 and
gap_scale=2r in polar_root. Thus b=P+28+4h, h=bit_length(2r), and the phase
routine receives b+4. With u=2^-b its error is at most u/16. The lower
square root of radius one is exactly one. Consequently 4u per column entry
and 4ru for the operator are conservative. Since 2^h>2r,

\[
4ru<2^{-P-30}/r^3<1/(4r).
\]

The centered roots of the even 2r-grid have real part at least
sin(pi/(4r))>=1/(2r). The stored root therefore has real part strictly
larger than the declared margin mu=1/(4r). Compression to any leading
section, including one that cuts the cyclic block, preserves this lower
bound. Cauchy–Schwarz implies inverse spectral norm at most 4r; converting
component row/column sums with sqrt(2k)<=2t yields the literal Q=8tr<=8t².
This is a real-part proof for every section, not an inference from full
matrix invertibility. The padded matrix is not incorrectly called globally
Toeplitz; its separate rank applicability remains a named source input.

The approximate Gauss mean is an average of exact unit phases and hence has
modulus at most one. The exit's three phase replacements cost at most
3u/16, and final rounding adds less than u. Thus both outer diagonals have
error <2u. Their inverse bounds correctly use the ideal exit magnitude
1/sqrt(r); 2t covers both directions and identity holes.

The compiler exact-word root defect is at most 2^(-P-8) against the stored
column; after the column error it is at most 2^(-P-7) against the ideal root.
Telescoping the four axis factors, with approximate norms <=2 and ideal
norms <=1, gives

\[
9\epsilon_{\rm diag}+6\epsilon_{\rm root}
\le(9/256+6/128)2^{-P}=21\,2^{-P}/256<2^{-P}.
\]

The bias is incurred once per axis, not once per emitted gate.

## 4. Prefixes, inverses, literal factors and partial H calls

The universal substitutions lambda<=4t, Q<=8t², chi<=32t³ and
r_star<=5t give B<=2^68 t^39, alpha<=1280t^6 and K_G<=2050t^5.
The exact product 4102*9230=37,861,460<2^26 bounds H_star by 2^26 t^11;
the other fragment terms 133t^4 and 16t² fit that envelope. Source (14)
then gives K_phys<=2^98 t^52. These inequalities hold for every t>=2.

An original matching gate is a ratio of adjacent source prefixes. The
inverse-prefix estimate therefore gives L_gate=K_phys² for both gate and
inverse. Largest-entry pivoting gives |b/a|,|c/a|<=1. The middle diagonal
diag(a,det(G)/a) and its inverse are bounded by 2 L_gate: the first
reciprocal follows from the largest-entry inequality, and the second is
an entry of the permuted inverse matrix.

I independently multiplied the three-H identity. For a=4t/5,

\[
\operatorname{diag}(-a/8,-1/6)H\operatorname{diag}(2,1)H
\operatorname{diag}(-3,1)H\operatorname{diag}(1/a,1)
=\begin{pmatrix}1&t\\0&1\end{pmatrix}.
\]

The two arguments -3 and 3+z have moduli between two and four when
|z|<=1. Every non-pivot primitive diagonal and inverse is bounded by 64.
Two switch words, four three-H words and one pivot fully expand to
**23 diagonals and 16 H factors**, hence **38 non-pivot factors**.
The original 21/36 count had already joined internal upper_six boundaries.
Both fit 64^40, but the expanded count makes the primitive bound immediate.
The author accepted this two-sentence repair without changing any constant.

The independent literal interpreter checks 600 Gaussian-rational matrices,
all four pivot positions, large/small scales and near-singular Schur
diagonals. It verifies the endpoint, primitive/inverse factor bounds and
the census. A sign mutation fails. The universal justification is the
algebra above; finite samples corroborate the source binding.

Completed routing rows are permutations. A partial switch adds at most
four; completed rows add norm one. Thus each lowered root prefix and its
inverse is bounded by

\[
4K\,64^{40}(2K^2)\le2^{537}t^{156}.
\]

Two roots and both external diagonals give 2^1076 t^314 per one-axis
prefix/inverse. Each axis contributes exactly one such prefix even when
axes finish at different times. Serial width classes and packs do not
multiply that number. An extra 2^d at each interval end permits partial
external H packs. The resulting interval 2-norm is at most
2^(2154d+628L). A single sqrt(T)=2^(L/2) conversion gives exactly E.
The native service's private arithmetic cuts remain outside this external
interval theorem, as its named exactness premise requires.

## 5. Literal stage count and coefficient-cache invariant

A matching has 17 diagonal entries and 16 H calls. Each of its
2(2ell-1) route switches has three diagonal entries and two H calls.
Counting diagonals and H separately gives the sharper literal bound

\[
33+10(2\ell-1)=20\ell+23.
\]

The paper's 24ell+22 bound is larger for ell>=1. Two roots and at most
d packs give J_actual<=2+2d D(ell_max)(20ell_max+23). The independent
polynomial certificate proves J minus this expression has positive
coefficients in both its constant and d-linear parts. The exact two-root
depth coefficients, in increasing degree, are
`[46,13288,38384,35136,11712,1280]`; the available degree-six polynomial
dominates each strictly. This covers unbounded widths. Separating the H
step is essential because a pre-H diagonal error must propagate through H.

For coefficient arithmetic, b_i=2^437 t_i^104 bounds every exact scalar
of an emitted axis diagonal, including fused pivot boundaries. Each
rounded factor is at most 2b_i, and each complex multiplication has error
<=v=2^-P. Factor telescoping plus at most d-1 rounded multiplications
gives the stated 2d 2^d product(b_i) v bound. Final multiplication by data
adds at most v, yielding epsilon(1+||z||∞) with the declared A.

The odometer invariant concerns the actual rounded expression tree.
At current indices i_0,...,i_(d-1), suffix k is the fixed right-associated
rounded product of the current factors with index at least k. A carry
through j changes only coordinates 0,...,j. Recomputing j down to 1
restores the invariant; higher suffixes already have unchanged arguments.
No retained suffix contains more than d factors, regardless of scan length.

My oracle distinguishes every (axis,index) factor and input datum with
noncommutative trees, so numerical cancellation cannot hide a stale cache.
Twelve shapes, including heterogeneous dyadic sides and carries through
eight axes, cover 1,214 records. Every output tree equals fresh
current-coordinate evaluation. Skipping the newly changed suffix fails
at the first relevant carry. This independently tests the no-drift
invariant rather than repeating the author's numeric packets.

## 6. Bootstrap, signs and recovery

The bootstrap comparison word is the exact rational word before external
table/data rounding. Rounded tensor coefficients need not factor as exact
tensors; their deviation is a local defect. This distinction is respected.

Let a=JM epsilon and R=2^E. Variation of constants bounds each computed
prefix error by a(1+R+maximum_previous_error). The finite bootstrap gives
error <=2a(1+R) when a<=1/2. Here the selector establishes the stronger

\[
a<2^{-4p-E}/4<1/4,
\qquad \text{raw error}\le C2^{-P+A+2E}<2^{-4p},
\]

because C<2^bit_length(C). Thus no desired computed-state bound is assumed
in advance. If the native interface requires unit-disk inputs, the derived
radius 2R+1 permits the predetermined shift 2^(E+2), with corresponding
extra fractional bits, under the widened exact-native contract.

The source opposite-sign path conjugates the input and output of the same
forward program. Conjugation is an isometry; no oddness of the component
tie-breaking rule is required.

For recovery, the Fourier means are maximum-norm contractions on the whole
true/hole tensor. Forward error in a zero-filled hole is below
2^-4p<2^-p, so the actual public toward-zero conversion returns zero.
Pointwise public products stay in the next half-disk input domain.
The inherited source theorem bounds normalized final error by 3e, e=3/B^6.
Scaling by (4BS)^2 includes both digit scales and the two net source-size
factors. Therefore, with S<=B,

\[
(4BS)^2(3e)\le144/B^2<1/2\quad(B\ge32).
\]

The correct direct character is u=sum_i(S/r_i) mu_i² mod S. At each
true side its own summand is a unit and every other summand vanishes,
so u is a unit modulo S. Reusing the old Gaussian character's extra
t_i would be a different and generally invalid application. This review
retains the precise CRT/recovery theorem; the scalar inequality alone
would not prove that application.

## 7. Result, limits and reproduction

The selector is sufficient, not minimum. The old-minus-new positivity
calculation is sound, so the result also validates #7849's larger original
selector under the named contracts. #7981 changes chronology and weakens
the intermediate target; the package correctly disclaims an asymptotic
improvement over that successor. No complete-framework assumption is
removed and no physical tape or owned-arena theorem is supplied here.

Run the independent evidence with:

```sh
python3 -I -W error -B check_review.py PATH/TO/direct-circulant-production-precision
```

It finishes with PASS_INDEPENDENT_PRECISION_CROSS_REVIEW.
REVIEW-EVIDENCE.txt contains the actual counts and polynomial certificate;
REVIEW-RECEIPT.json pins the checker, result and accepted proof. The
universal acceptance rests on the written conditional argument reviewed
above, not extrapolation from finite examples. No blocking objections
remain after the factor-count correction. The next substantive obligation
is the already disclosed private-grid and owned-arena interface.

# Independent review of gauged physical Gaussian symmetries

**Disposition: PASS for the stated matching square-block and error contracts.**
No mathematical change is requested. The exact gauge classification,
underlying permutation-cycle obstruction, forward error estimate, inverse
transfer and qualified physical broad/narrow specialization are sound.
The conclusion remains local and conditional on the displayed source/error
interfaces. It does not discharge a foundational assumption or improve kappa.

Reviewed proof SHA256:
`9aae57aa8ade47a89b7b22b39df968056853f04d240094a38e065153a7a53224`.
Canonical base:`e54523517d0f03e58352e647c403a5af3e525a57`.
The exact C6 predecessor is CubeJerry commit
`be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7`. All three retained input sizes,
SHA256 values and Git blob identities were checked. The exact prior normalized
proof is unchanged at SHA256
`7ce68fdc614b28df6133682ee2e82f661c2d373ceb645f24f4a93d76a9d0955c`.

## 1. Independent algebraic derivation

Write the shifted Gaussian as `H=S K S^-1`, with K the unshifted positive
Gaussian tensor and S its nonzero diagonal exponential. For arbitrary
invertible complex diagonal L,R, put A=LS, B=S^-1R and Q=AB=LR. Then
`G=A K B` and its diagonal is exactly Q.

The four factors cancel in

`Gxy Gyx/(Gxx Gyy)=Kxy^2`.

This identity remains valid for complex gauges; neither positivity nor
unit modulus of L/R is needed. Nonzero diagonals are essential. Exact
commutation by a monomial `M=D P` preserves this normalized pair product,
because its extra row/column factors also cancel. Therefore its underlying
vertex permutation preserves the weighted Euclidean distance.

The C6 geometry applies to every vertex permutation: affine extension by
polarization, convex-box edge preservation, and exact grid-point counts on
those edges. It forces a signed coordinate permutation preserving both n_i
and gamma_i. Equal geometric side lengths alone are insufficient; the
two-by-three grid with gamma ratio4 has a square hull but unequal edge
counts. Two-point axes are included in the same argument.

The exact monomial weights require one more condition than the metric.
The diagonal of `M G M^-1=G` forces P to preserve Q exactly, including
its phases. With `E=A^-1 D(PAP^-1)`, the remaining condition is
`E K E^-1=K`. Since every entry of K is nonzero, every ratio E_x/E_y is1,
so E is one global nonzero scalar c. Conversely a P preserving K and Q
commutes with `A^-1 G A=KQ`. This yields precisely

`M=c A P A^-1`.

No separate weight may be chosen independently on each cycle of a dense
Gaussian matrix. On the other hand c itself cannot be discarded: for an
involutive P and c=2, `M^2=4I`, so M has infinite matrix order while P has
only one- and two-vertex cycles. The manuscript consistently uses the latter
cycles, and expressly avoids equating general weighted displacement with an
ordinary permutation displacement.

When widths are distinct, every underlying P is a product of coordinate
reflections, hence has at least ceil(T/2) cycles. Gauging to K and reflecting
all coordinates attains that minimum: zero fixed vertices when some side
is even, one when every side is odd. Thus the defined dense2cT format has
minimum `2T ceil(T/2)`. This is a format slot count, not a general rank or
runtime lower bound. Gauge application, coefficients, precision, setup and
transport remain additional work.

## 2. Absolute-error and inverse checks

Let `|Gxy|<=M`, `|Gxx|>=delta>0` and entry error at most epsilon<=delta/2.
The numerator and denominator product errors are each bounded by
`2M epsilon+epsilon^2`. Because the ideal normalized pair product lies in
(0,1], subtracting its multiple of the perturbed denominator gives

`|C(X)-C(G)| <= (4M epsilon+2epsilon^2)/(delta^2/4)`.

The stated24M epsilon/delta² is conservative;20 would suffice under the
same assumptions. This derivation is valid for arbitrary complex errors.
It is substantially better than independently bounding numerator ratios
with an unnecessary fourth power of delta, and does not silently normalize
the physical matrix at zero cost.

Under gamma_max<2 gamma_min, unit edges are separated from every distinct
nonedge by the stated positive gap. Distinct axis levels give a second
positive gap. Exact monomial commutation preserves C(X), so the ideal levels
at a pair and its image differ by at most twice the error bound. The strict
48M epsilon/delta² margin therefore preserves each edge color. Connectivity
in all other colors makes each image coordinate depend only on its matching
input coordinate; the remaining path automorphism is identity or reversal.
This proves containment only. Unequal errors can destroy symmetries.

Both conditioning factors are material. With q=(1/3,1/4), scale the
unshifted two-axis kernel by h=2^-40 and round off-diagonals to zero.
The result hI has nonzero diagonal and admits a three-cycle, while the
original distinct-width matrix does not. Its absolute error is h/3.
An inequality omitting delta^-2 would falsely certify this example. A
different unbalanced similarity has diagonal1, entries R/3 and1/(3R), and
an absolute change1/(3R) changes a normalized pair product by1/9. Hence
M also cannot be suppressed.

For an approximation X to G^-1, entrywise epsilon implies
`||E||_2<=T epsilon` and `||G||_2<=T M`. The factorization
`X=G^-1(I+GE)` and the Neumann estimate give

`||X^-1-G||_2 <=2 T^3 M^2 epsilon`

under `T² M epsilon<=1/2`. Applying the forward theorem to X^-1 gives
exactly the manuscript's three inverse conditions. No norm of a commuting
monomial is needed, since its commutation equality is exact. The argument
uses neither a Gaussian pair-product identity for inverse entries nor an
interchange between a section and a matrix inverse. Both false shortcuts
are explicitly separated by exact counterexamples in the checker.

An additional rational three-by-three example shows why a dimension-free
inverse error estimate cannot replace the displayed bound: with
`Kij=(9/10)^((i-j)^2)` and inverse perturbation epsilon times the all-ones
matrix, one returned entry error exceeds2epsilon, while the paid54epsilon
bound holds.

## 3. Physical source-square conditions

For the broad block, direct expansion of
`-b(x-lambda y+delta0)^2` gives exactly the displayed row log, column log,
normalized shifted-kernel exponent and scalar `-b delta0²`. The separate
alpha^-1 normalizer remains present. Dropping either normalizer would
misstate the actual physical matrix. On matching centered coordinates,

`|(1-lambda)x+delta0| <= (1+theta B)/2`

proves the stated diagonal floor; every entry is at most alpha^-1. The
condition `|delta0|<=1/2` is a stated broad-source condition, not something
to infer from a differently parametrized narrow phase label.

For the narrow block, the essential identity is
`beta_j=beta_i+theta(j-i)` inside one phase cell. The exact quadratic
expansion gives the chirp similarity and width A rho. With integer
h=j-i nonzero and both phase representatives bounded by1/2,

`|rho h+beta_i| >=rho-1/2>1/2>=|beta_j|`.

Consequently the physical narrow entries are strictly below1 off diagonal,
and the diagonal is exactly1. The weak closed phase-endpoint bounds are
sufficient for this estimate; the actual source's half-open cell is a
subset. A crossing between cells can leave both phase representatives
within the allowed range while changing their difference by an integer.
The quoted chirp identity then fails. The checker includes that exact
counterexample, so phase-value bounds alone are not treated as cell
consistency.

Rows and columns must use the same unit-spaced interval and center for
these physical specialization claims. An independently reordered column
grid can have a normalized pair product greater than1, contradicting the
proposed Euclidean metric. A rectangular matrix does not even have the
same simultaneous vertex-permutation problem. Neither case is admitted.

The fine-prime argument uses distinct odd primes and the two target lengths
r and r/2. The integers `m_i=(r/t_i)s_i` are distinct within a target class
by prime distinctness and across classes by parity. The broad/narrow width
gaps and their separate edge bands follow exactly. The source rounded
specialization explicitly treats all-broad and all-narrow tensors;
a mixed group would need its own band argument.

The independent checker uses rational quadratic exponents, not floating
exponentials, for the source identities and inequalities. Its small
prime fixture `(r,t,s)=(128,(128,64),(113,59))` satisfies the displayed
fine-prime interval at p=2 and checks both scaled-width groups. This is
bounded corroboration, not an independent prime-existence theorem or a
production-page implementation.

## 4. Source precision and unresolved pipeline boundary

For beta<1 and xi<2, the broad diagonal exponent and normalizer give
`log(delta_B^-1)=o(p)`, and `log T=o(p)`. The two gap bounds are2^-o(p).
Thus actual absolute errors2^(-Cp+o(p)) eventually satisfy the forward and
dimension-paid inverse conditions. The factorwise tensor error estimate
is valid because every physical factor is eventually bounded by1.

The stronger chirp guard `beta+2xi-2<1` separately bounds inverse diagonal
ranges by exp(o(p)). The cited shifted-Toeplitz symbol theorem, with the
source's strictly positive shift gap, gives polynomial inverse norm per
factor, uniformly in section size. Tensoring it contributes exp(o(p)).
This supports O(p)-bit magnitude plus fractional storage **if** those
coefficients are actually produced; it supplies no producer or free
coefficient access.

The manuscript correctly retains an important provenance boundary. The
source note also quotes a separate error expression
`4*2^-P*exp(A/(4theta))`. Under the fine-prime scale theta of order p^-2,
that expression does not become a Cp-bit absolute physical error merely
by setting P=O(p). The eventual tolerance here is not certification that
the full stored/global producer supplies it. Actual setup precision,
truncation, gauge conversion, global weights and entrywise transfer must
be verified and paid for on the same square physical block. The author
confirmed that this remains external. The finite inverse in this theorem
is also distinct from a principal section of a global inverse.

## 5. Exact independent evidence and limits

`independent_check.py` imports no author verifier or mathematical helper.
It uses a separate Gaussian-rational complex type, direct multiplication
constraints for monomial commutation, exact Gauss-Jordan inversion and
full vertex-permutation searches on six small fixtures. There are822
permutations checked for each of the original and inverse matrices,
including complex gauges, nonconstant diagonal phases, equal widths,
an unequal-grid-count square hull and odd vertex volume. The predicted
centralizer weights are compared with weights solved directly from entries.

Separate exact checks cover forward and inverse perturbation margins,
source exponent identities, and controls for tiny gauges, unbalanced
similarities, weighted matrix order, inverse metrics, sections, missing
dimension factors, mixed index sets and rectangular domains. These are
bounded corroboration of the universal proofs, not a search-based
impossibility argument.

```sh
python3.12 -I -W error -B independent_check.py --package PATH_TO_PACKAGE
python3.12 -I -O -W error -B independent_check.py --package PATH_TO_PACKAGE
```

Both runs pass with identical JSON. Default execution is read-only;
`--write` explicitly requests a receipt. FREEZE.json records the exact
checker, receipt and review hashes. Substantial OpenAI assistance was used
for this complementary review. No human or formal-kernel certification,
full periodic/rectangular/current-caller claim, unconditional multiplication
theorem or runtime lower bound is asserted.

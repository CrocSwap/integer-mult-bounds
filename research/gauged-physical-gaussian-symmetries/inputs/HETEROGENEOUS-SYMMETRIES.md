# Heterogeneous Gaussian symmetries and the retained fine-prime boundary

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This note proves an exact classification and a scoped certificate-format
obstruction. **No new kappa, multiplication runtime lower bound, or discharge
of a foundational assumption is claimed.**

The homogeneous predecessor is CubeJerry commit
`2ae2fa14eeefe301652f62313b137a97036ab13d`,
`research/gaussian-orbit-certificate-scale/PROOF.md`, retained unchanged as
`inputs/HOMOGENEOUS-ORBIT-SCALE.md`. Its long-orbit construction requires
interchangeable tensor coordinates. We determine exactly when heterogeneous
coordinates are interchangeable, then examine the distinct-prime widths
in two retained source notes. The affine-isometry argument and elementary
group facts are classical; no global literature-priority claim is made.

## 1. Matrix, symmetry and exact classification

Let d>=1, let n_i>=2 be integers, and let gamma_i>0 and a_i be real. Set

\[
 X=\prod_{i=1}^d\{0,\ldots,n_i-1\},\qquad T=|X|=\prod_i n_i,
\]

\[
 H_{xy}=\exp\left[-\sum_i\gamma_i(x_i-y_i)^2
                    +2\sum_i\gamma_i a_i(x_i-y_i)\right].       \tag{1}
\]

An exact symmetry is any bijection F:X->X such that
`H_(F(x),F(y))=H_(x,y)` for every x,y. We quantify over every vertex
permutation, without first restricting F to coordinate permutations.

**Theorem 1.** The exact symmetries are precisely the maps

\[
 F(x)_{\sigma(i)}=e_i x_i+\frac{1-e_i}{2}(n_i-1),\qquad e_i\in\{1,-1\}, \tag{2}
\]

where sigma is a coordinate permutation satisfying, for every i,

\[
 n_{\sigma(i)}=n_i,\qquad \gamma_{\sigma(i)}=\gamma_i,
 \qquad e_i a_{\sigma(i)}=a_i.                                \tag{3}
\]

### 1.1 Recover the complete metric

The product of an entry and its transpose is

\[
 H_{xy}H_{yx}=\exp\left[-2\sum_i\gamma_i(x_i-y_i)^2\right].     \tag{4}
\]

The exponential is injective on the real line. Thus every symmetry
preserves the weighted squared distance `sum gamma_i(x_i-y_i)^2`.
Embed X into Euclidean space by

\[
 z(x)=(\sqrt{\gamma_1}x_1,\ldots,\sqrt{\gamma_d}x_d).
\]

Its convex hull is the rectangular box with side lengths
`L_i=(n_i-1)sqrt(gamma_i)>0`.

Every isometry of this finite embedded set extends affinely. To see this
directly, let b be the image of the zero corner and let v_i be the image
of the corner L_i e_i, minus b. Polarization of their pairwise distances
gives `v_i dot v_j=0` for i!=j and `|v_i|=L_i`. Hence `v_i/L_i` form an
orthonormal basis. Polarization against each corner also gives, for every
embedded point z and its image w,

\[
 (w-b)\mathbin{\cdot}v_i=L_i z_i.
\]

Therefore `w=Az+b`, where the columns of A are `v_i/L_i`. This is one
affine Euclidean isometry, valid on the entire grid rather than just its
corners.

### 1.2 Edge faces determine both widths and cardinalities

This affine map carries the convex hull onto itself. It preserves faces
and their dimensions: a supporting affine functional pulls back to a
supporting affine functional. In particular it permutes the one-dimensional
edge faces of the box. The d edges incident to the zero corner therefore
map to d different coordinate edges incident to its image. For some
permutation sigma, their physical lengths satisfy `L_i=L_(sigma(i))`,
and each corresponding linear direction has sign e_i.

Physical lengths alone do not suffice. The original i-edge contains
exactly n_i grid points. Because the affine map is a bijection of the
whole grid and of the whole edge segment, its image edge contains exactly
the same number of grid points. Thus `n_i=n_(sigma(i))`. Combining this
with equal L gives `gamma_i=gamma_(sigma(i))`. The translation must place
each positively directed edge at zero and each negatively directed edge
at its opposite endpoint, yielding (2).

This also handles two-point axes. No interior edge point is needed when
n_i=2; its exact count is still preserved. Equal geometric side lengths
do not create extra symmetries when edge counts differ. For example,
`n=(2,3), gamma=(4,1)` has a square convex hull, but exchanging its physical
axes would send the grid midpoint `(0,1)` to native coordinate `(1/2,0)`.
It is a corner symmetry and not a grid permutation. Nor can a coincident
axis and diagonal length defeat the argument: affine maps preserve edge
faces, not just lengths.

### 1.3 The oriented part fixes the signs and shifts

After the quadratic terms agree, equality of (1) is equivalent to

\[
 \sum_i\gamma_i a_i\big(F(x)_i-F(y)_i\big)
       =\sum_i\gamma_i a_i(x_i-y_i).
\]

Substituting (2) and the already proved width equality makes the
coefficient of `x_i-y_i` on the left equal to
`gamma_i e_i a_(sigma(i))`. The grid has at least two points on every
axis, so testing a unit displacement on each axis proves the final
condition in (3). Conversely, (2)-(3) preserve the two exponent terms
in (1), proving sufficiency and completing Theorem 1.

For completeness, within each class of equal `(n_i,gamma_i,|a_i|)`, the
group is the signed coordinate-permutation group when a_i=0. When the
common absolute shift is nonzero, each permutation determines the signs
uniquely by (3), so the group is isomorphic to the ordinary symmetric
group on that class. These classes act independently. In the homogeneous
case with a common nonzero shift, all signs are positive, exactly as in
the predecessor.

## 2. Distinct widths, exact cycle counts and inverse matrices

**Corollary 2.** If the gamma_i are pairwise distinct, sigma in (2) is
the identity. The only symmetries are independent reflections of the axes
in `J_0={i:a_i=0}`. Consequently every symmetry has order at most 2 and
every vertex cycle has length at most 2. If c(F) counts all cycles,
including fixed points, then

\[
 c(F)\ge T/2.                                                \tag{5}
\]

If every shift is nonzero, the group is the identity and c=T.

The precise minimum is elementary. Reflection of axes J subset J_0 has
no fixed points if some n_j with j in J is even. Otherwise its fixed
points number `prod_(i not in J) n_i`. Every involution has
`c=(T+number of fixed points)/2`, so

\[
 \min_F c(F)=
 \begin{cases}
 T/2,&\text{some zero-shift axis has even }n_i,\\[1mm]
 \dfrac{T+T/\prod_{i\in J_0}n_i}{2},&\text{otherwise}.
 \end{cases}                                                \tag{6}
\]

The empty product is one, giving c=T when J_0 is empty. If all zero-shift
axes have odd size, reflecting all of them minimizes the fixed-point count.

The same exact symmetry group applies to H inverse. Indeed, each
one-dimensional unshifted factor is

\[
 e^{-\gamma(i-j)^2}
   =e^{-\gamma i^2}(e^{2\gamma i})^j e^{-\gamma j^2}.
\]

The middle matrix is a Vandermonde matrix on distinct positive nodes;
the diagonal matrices are nonsingular. The linear shift adds the similarity
by the diagonal `exp(2 gamma a i)`, also nonsingular. Tensor products
therefore give an invertible H. For every permutation matrix P,
`PHP^T=H` if and only if `PH^-1P^T=H^-1`, by taking inverses. This algebraic
observation does not assert that a gauge operation is free or well conditioned.

## 3. Exact retained fine-prime specialization

The source boundary is deliberately narrow. At the exact canonical commit,
`inputs/GAUGEFREE-INTERIORS.md`, section 2, defines the normalized kernel

`G'_s(u)=exp(-gamma u^2+2 gamma s u)`.

It gives broad width `gamma=b0/rho` and narrow width `gamma=A rho`, where
we write A for the source's global narrow parameter `a=pi alpha^2` to
distinguish it from the per-axis shifts a_i. Here `b0=pi/alpha^2` and
`rho_i=t_i/s_i`. In a row-minus-column convention opposite to the source's
u, replace its s by -s; this affects neither widths nor the shift bounds.

`inputs/FINE-PRIME-PADDING.md`, section 1, supplies distinct odd primes
s_i, dyadic target sides `t_i in {r,r/2}`, and

\[
 (1-2\eta_p)t_i<s_i\le(1-\eta_p)t_i,
 \qquad \eta_p=1/(4p^2).                                    \tag{7}
\]

We use the stated distinct-prime construction as source provenance; this
note does not reprove its prime-existence theorem or practical threshold.
For any supplied parameters satisfying (7), the following width statement
is elementary and exact.

Put `m_i=(r/t_i)s_i`. Then m_i is a positive integer below r. If two target
sides agree, distinct source primes make their m_i distinct. If they do
not agree, one m_i is odd and the other even. Thus every m_i is distinct,
and

\[
 \gamma_i^{\rm broad}=b_0m_i/r,\qquad
 \gamma_i^{\rm narrow}=Ar/m_i.                              \tag{8}
\]

For distinct axes i,j this gives

\[
 |\gamma_i^{\rm broad}-\gamma_j^{\rm broad}|\ge b_0/r,
\qquad
 |\gamma_i^{\rm narrow}-\gamma_j^{\rm narrow}|
 =\frac{Ar|m_i-m_j|}{m_im_j}>A/r.                            \tag{9}
\]

The latter uses both m_i,m_j<r. It remains valid across the two dyadic
target-size groups. A tensor of nondegenerate **square** normalized sections
from distinct original axes has pairwise distinct widths, regardless of its
local lengths and shifts, provided its row and column index sets have been
identified exactly as in (1). Any index translations must be absorbed into
the displayed shifts a_i. Corollary 2 applies at that square normalized
boundary. Rectangular or differently indexed source blocks require a
separate index-set and normalization argument; they are not automatically
instances of this simultaneous vertex-permutation theorem.

Here T is the chosen normalized tile volume `prod n_i`. It is not silently
identified with the full target product called T in the fine-prime source.
The local n_i may be capped interior lengths rather than the t_i themselves.

The retained notes also contain chirp/diagonal factors, truncation,
rounding, global phase-cell boundaries, aliases and identity hole columns.
They distinguish their ideal shifted kernel from the globally rounded
reference. We do not identify either complete matrix, the entire current
selected caller, repeated copies, or unused identity spectators with (1).
Current whole-caller ancestry and a matching error contract at this exact
normalized boundary remain separate provenance obligations.

## 4. Consequence for the specified dense cycle-boundary format

The predecessor arranges full cycles of one exact symmetry in successor
order and uses its c cycle starts as the boundary set. Its displayed
boundary decomposition retains two families of c full length-T scalar
vectors, with prescribed zero positions still occupying slots. The defined
dense format therefore has exactly 2cT scalar slots; the known unit-vector
families are already implicit and are not charged again.

For every exact symmetry of the distinct-width tensor, (5) and c<=T give

\[
             T^2\le 2cT\le2T^2.                            \tag{10}
\]

Thus this format is Theta(T^2), and it is exactly 2T^2 when all ideal
shifts are nonzero. If slots have b bits, its stored length is exactly
2bcT bits. Formula (6) gives the precise optimum when zero shifts remain.

This is a format count, not a lower bound on displacement rank. Some
vectors can vanish or be dependent; compression can remove them. Different
successors need not extend to a global exact symmetry. Implicit generation,
other generator bases, arbitrary-rank factorizations and arithmetic circuits
are all outside the result. No multiplication runtime consequence follows
from (10), and no full-system kappa improvement is claimed.

## 5. A short-distance rounding guard

The exact classification by all distances cannot simply be reused after
rounding. Far Gaussian entries can be tiny. Instead we prove a robustness
statement using only unit edges and their distinct pair-product levels.

Assume now that `|a_i|<=1/2`, and let gamma_min, gamma_max be the smallest
and largest widths, with `gamma_max<2 gamma_min`. Assume the widths are
distinct and define

\[
 \Delta_\gamma=\min_{i\ne j}|\gamma_i-\gamma_j|,
\quad A_*=e^{-2\gamma_{\max}}-e^{-4\gamma_{\min}}>0,
\quad B_*=2e^{-2\gamma_{\max}}\Delta_\gamma.                  \tag{11}
\]

For d=1 the color condition below is omitted, equivalently B_*=infinity.
Let a possibly complex stored matrix Hhat satisfy
`|Hhat_xy-H_xy|<=varepsilon` entrywise, and put
`rho=2 varepsilon+varepsilon^2`.

**Theorem 3.** If

\[
                       2\rho<\min(A_*,B_*),                 \tag{12}
\]

then every exact simultaneous permutation symmetry of Hhat acts by a
coordinatewise identity or reflection. In particular it has order at most
2, c>=T/2, and the same dense-format bound (10). No lower bound on a
nonzero shift is required. This is containment, not equality with all
reflections.

*Proof.* For an integer u and |a|<=1/2,
`u^2-2au>=u^2-|u|>=0`. Hence every ideal entry satisfies `0<H_xy<=1`.
Expanding the product of two perturbed entries gives

\[
 |\widehat H_{xy}\widehat H_{yx}-H_{xy}H_{yx}|
       \le2\varepsilon+\varepsilon^2=\rho.                  \tag{13}
\]

If F is an exact symmetry of Hhat, its stored pair products agree.
Consequently the ideal pair products of `(x,y)` and `(F(x),F(y))` differ
by at most 2rho.

A unit grid edge has weighted squared distance gamma_i and ideal pair
product `e^-2gamma_i`, at least `e^-2gamma_max`. Any distinct nonadjacent
pair either differs on two axes or by at least two along one axis, so
its weighted squared distance is at least `2 gamma_min` and its pair
product is at most `e^-4gamma_min`. Their gap is at least A_*. By (12),
an edge cannot map to a nonedge.

Give every unit edge its coordinate color i. Distinct colors have pair
products separated by at least B_*, by the mean-value theorem applied
to `e^-2t` on the width interval. Thus F preserves each color separately.
Since it is a finite bijection, this is an automorphism of the entire
colored grid graph, in both directions.

Here is the needed graph argument directly. Fix a coordinate k. Moving
along any color i!=k leaves the k-th coordinate of the image unchanged.
The grid on all other coordinates is connected, so F(x)_k depends only
on x_k: write it as phi_k(x_k). Bijection of F makes every phi_k a
bijection of its path vertex set. Preservation of color-k edges makes
successive values of phi_k adjacent. An injective walk through a finite
path cannot change direction without immediately revisiting its preceding
vertex. Therefore phi_k is either the increasing sequence or the decreasing
sequence: identity or reflection. This argument also covers n_k=2.
Every such coordinatewise map squares to the identity, proving the theorem.

Small nonzero shifts can disappear under rounding, so it would be wrong
to infer that all such Hhat have trivial symmetry. Conversely arbitrary
unequal entry errors can destroy a reflection. A common deterministic
pointwise rounding rule preserves exact entry equalities and therefore
cannot destroy a symmetry of H itself. The theorem allows more general
entrywise errors and asserts only the proved containment.

If Hhat is invertible, its inverse has the same exact permutation
symmetries by conjugation and inversion. Theorem 3 does not by itself
establish that invertibility.

## 6. The retained fine-prime separation is visible at Cp bits

For p>=2, (7)-(8) give the explicit width ranges

\[
 \tfrac78b_0<\gamma_i^{\rm broad}<b_0,
 \qquad A<\gamma_i^{\rm narrow}<\tfrac87A.                  \tag{14}
\]

Both satisfy gamma_max<2 gamma_min. Combining (9), (11), and (14)
gives the sufficient lower bounds

\[
\begin{array}{ll}
 A_*^{\rm broad}\ge e^{-2b_0}-e^{-7b_0/2},&
 B_*^{\rm broad}\ge2e^{-2b_0}b_0/r,\\[1mm]
 A_*^{\rm narrow}\ge e^{-16A/7}-e^{-4A},&
 B_*^{\rm narrow}\ge2e^{-16A/7}A/r.
\end{array}                                                \tag{15}
\]

The source has `A=Theta(log p)`, `b0=Theta(1/log p)` and
`log r=Theta(p^(1-epsilon_0))` with fixed `0<epsilon_0<1`
(FINE-PRIME-PADDING sections 1-2). Thus every positive lower bound in
(15) is at least `exp[-O(log p)-log r]=2^-o(p)` after adjusting constants.
For the broad adjacency gap, use
`e^-2b0(1-e^-3b0/2)=Theta(b0)` as b0 tends to zero. For the narrow gap,
use `e^-16A/7(1-e^-12A/7)`, with its parenthesis bounded away from zero.

Consequently any error `varepsilon<=poly(p) 2^(-C p)` with fixed C>0
satisfies (12) eventually. There is no practical threshold claim. The
source shifts for square sections with the same row and column coordinate
origin satisfy |a_i|<1/2, so the unit-entry premise used in (13) is available
at that identified normalized boundary. Other index translations require
this shift bound to be checked again. The result allows arbitrarily small
shifts and does not assume a polynomial lower bound on them.

As a separate elementary interface, if each of d polynomially many
unit-bounded factors is rounded with entry error at most eps_factor, then
the tensor entries have error at most `(1+eps_factor)^d-1`. For
`d eps_factor<=1`, this is at most `2d eps_factor`, by
`(1+eps_factor)^d<=exp(d eps_factor)` and `e^t-1<=2t` on [0,1]. Hence
per-factor Cp-bit errors also fit the stated form at this normalized
tensor boundary. This does not transport through omitted gauges, inverse
application, truncation or arbitrary repeated structures. Such a transfer
needs its own actual entrywise error and source identification.

## 7. Bounded executed evidence and limitations

The standalone verifier imports no predecessor executable and authenticates
the three unchanged source/proof files by byte length, SHA256 and Git blob.
Its exact matrices use rational logarithmic exponents. Exponentials are
injective, so full equality decisions use integers after a common-denominator
scaling; no floating tolerance tests a symmetry.

Eleven complete searches inspect 243,414 vertex permutations on grids of
at most eight points and compare the complete groups with the separately
generated signed-coordinate formula. They include two-point axes,
coincident physical sides, coincident axis/diagonal lengths, unequal widths,
opposite shifts, zero-shift classes and nonzero shifts. Two additional
nine-point reflection families check the odd-side fixed-point formula;
they are not complete nine-point vertex-permutation searches.

Finite prime checks inspect 70 declared intervals for p=2..8 and
r in {16,32,64,128,256}, with 13 eligible distinct-prime pairs. The example
`p=2,r=64,(t_i,s_i)=(64,59),(32,29)` has m_i=59,58 and attains the broad
separation 1/64 after setting b0=1. These tests do not prove eventual
prime existence or the universal width statement, which follows from (8).

Three additional complete small-grid searches use rigorously rounded
dyadic matrices. Exponential values are enclosed by a rational positive
Taylor sum and a geometric tail bound before inversion; both interval
endpoints must yield the same rounded integer. The explicit gap conditions
are checked with rigorous lower bounds. Tiny nonzero shifts can gain
reflections, while a bounded nonuniform perturbation can destroy them.

Necessary-hypothesis controls include equal widths admitting a four-cycle
on coordinates (16 vertices, order 4, six vertex cycles), coarse rounding
to an identity matrix with all 24 four-vertex permutations, zero widths,
degenerate axes and a failed perturbation guard. The square-hull control
preserves all corners but fails at the actual grid midpoint. These are
counterexamples to broader statements, not evidence for a broader lower
bound.

The uniform proofs, not these bounded searches, establish the theorems.
No arbitrary-order displacement-rank obstruction, implicit-generator cost,
full Gaussian caller, source-owner implementation or all-size analytic
transfer is provided. The selected complete multiplication bound and its
five foundational assumptions are unchanged.

## 8. Credit and remaining useful questions

Credit @CubeJerry and the A4/A5 symmetry-orbit package authors for the
construction, homogeneous classification and exact dense-format question.
Credit Chafik Boukhalfa's #1786 fine-prime construction, IdeaOuter and the
#1758 fractional-shift contributors, Vlado Vojdanovski's #1673 Gaussian
audits, Jeremy Kothe and the retained package series, and every predecessor
named in the unchanged source notes. The separate fine-prime transfer audit
at canonical `research/pr1786-fine-prime-transfer-audit/README.md` already
checks its stated interval/precision inequalities; they are not claimed anew.

Substantial OpenAI assistance contributed to research, proof, verification
and packaging. Independent model-assisted review is separate from human
or proof-kernel acceptance. The parent proposed the heterogeneous target
and seed geometry; this worker derived the edge-count classification,
integer width gaps, local colored-edge perturbation argument and controls.

Two useful next obligations are to identify an actual complete caller
boundary with these exact normalized factors and entrywise errors, or to
find a representation that avoids this dense global-symmetry cycle format.
Neither follows from the present scoped negative result.

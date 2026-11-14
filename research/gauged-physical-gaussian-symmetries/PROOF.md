# Diagonal gauges cannot create long Gaussian symmetry cycles

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
**No new kappa or multiplication runtime lower bound.** All five selected
assumptions remain. This is an exact symmetry, precision and certificate-format
result for matching square Gaussian blocks, including the retained physical
broad and narrow blocks specified in section 5.

The immediate predecessor, CubeJerry commit
`be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7`, classifies heterogeneous normalized
Gaussian symmetries and proves distinct fine-prime widths. Its exact proof is
retained as `inputs/HETEROGENEOUS-SYMMETRIES.md`. It explicitly leaves diagonal
gauges, inverse-error transfer and actual physical blocks outside its rounded
normalized boundary. We close those scoped implications, with their costs and
conditioning limits. The diagonal invariant, affine box isometries and
Neumann identity are classical algebra; no general literature priority is
claimed for them.

## 1. The gauge-invariant metric and exact monomial centralizer

Let

\[
 \mathcal X=\prod_{i=1}^d\{0,\ldots,n_i-1\},\qquad
 n_i\ge2,\quad T=|\mathcal X|,
\]

and let gamma_i>0 and a_i be real. Define

\[
 H_{xy}=\exp\!\left[-\sum_i\gamma_i(x_i-y_i)^2
                 +2\sum_i\gamma_i a_i(x_i-y_i)\right].       \tag{1}
\]

Let L,R be arbitrary invertible complex diagonal matrices and put G=LHR.
Every diagonal entry of G is nonzero. Define the normalized pair product

\[
 \mathcal C_{xy}(G)=\frac{G_{xy}G_{yx}}{G_{xx}G_{yy}}.
\]

**Lemma 1.** Independently of L,R and the shifts,

\[
 \mathcal C_{xy}(G)=\exp\!\left[-2\sum_i\gamma_i(x_i-y_i)^2\right]. \tag{2}
\]

Indeed the four diagonal factors cancel, H has unit diagonal, and the two
linear exponents cancel. This is an exact complex algebraic identity; no
division is executed on a machine or granted free by the statement.

For a permutation p of the entire vertex set, write P e_x=e_(p(x)). If
P commutes with G, (2) is invariant under p. The same holds if a monomial
M=D P commutes with G, where D is any invertible diagonal matrix: conjugating
by D does not change the normalized pair products.

**Metric lemma.** Every permutation preserving (2) is a signed coordinate
map

\[
 p(x)_{\sigma(i)}=e_i x_i+\frac{1-e_i}{2}(n_i-1),\quad e_i\in\{1,-1\},
 \qquad n_{\sigma(i)}=n_i,\quad\gamma_{\sigma(i)}=\gamma_i.   \tag{3}
\]

Here we quantify over all vertex permutations. To recall the predecessor's
argument, embed x as z(x)=(sqrt(gamma_i)x_i)_i. The exponential is injective
on the real axis, so all Euclidean distances are preserved. Polarization
against the zero corner and its d axis-opposite corners determines one
affine orthogonal map on every vertex. It carries the convex box onto itself
and therefore carries its one-dimensional edge faces onto edge faces.
An i-edge has length (n_i-1)sqrt(gamma_i) and contains exactly n_i grid
vertices. Preservation of both quantities forces the two equalities in (3).
The directions and endpoint translations give the signs. Conversely every
map (3) preserves (2). Equal physical side lengths with unequal cardinalities
do not permit a coordinate exchange. This proof also covers n_i=2.

There is an exact description of the extra diagonal constraints. Put

\[
 K_{xy}=\exp[-\sum_i\gamma_i(x_i-y_i)^2],\quad
 S_{xx}=\exp[2\sum_i\gamma_i a_i x_i],
\]

so H=SKS^-1. Define A=LS, B=S^-1R and Q=AB=LR. Thus G=AKB and
G_xx=Q_xx.

**Theorem 2.** The complete monomial centralizer of G is

\[
 \{\,c A P A^{-1}: c\in\mathbb C\setminus\{0\},\quad
       P K P^{-1}=K,\quad P Q P^{-1}=Q\,\}.                 \tag{4}
\]

For necessity, the invariant proves the first condition on P, while the
diagonal entries in M G M^-1=G prove the second. Write
E=A^-1 D(PAP^-1). Substitution, using P Q P^-1=Q, reduces the commutation
identity to E K E^-1=K. Every entry of K is nonzero, so E_xx/E_yy=1 for
every x,y: E=cI. This is exactly M=c A P A^-1. Conversely, A^-1 G A=KQ,
and a P preserving both K and Q commutes with this matrix, proving (4).

The scalar c is essential. For example M=2 A P A^-1 with an involutive P
has M^2=4I and infinite matrix order. Its underlying permutation still has
only one- or two-vertex cycles. Weighted matrix order is never substituted
for vertex orbit length below.

All matrices in (1) are invertible. In one dimension, with q=exp(-gamma),
`q^((i-j)^2)=q^(i^2) (q^(-2i))^j q^(j^2)` is a diagonally scaled Vandermonde
matrix on distinct positive nodes. Tensor products and the invertible
diagonals preserve nonsingularity. The exact monomial commutants of G and
G^-1 are consequently the same. The entrywise invariant of G^-1, however,
need not be the Gaussian metric; this is not how the inverse conclusion
is proved.

## 2. Cycle counts and the exact dense-format obstruction

Suppose gamma_i are pairwise distinct. Equation (3) has sigma equal to
the identity, so every allowed underlying permutation is a product of
coordinate reflections. It squares to the identity and has

\[
                         c(p)\ge\lceil T/2\rceil             \tag{5}
\]

cycles, including fixed points. This holds for every choice of L,R, every
exact permutation symmetry of G, and every underlying permutation in (4).
It also holds for their exact inverse commutants.

The bound is optimal over gauge choices: choose L=S^-1 and R=S, giving
G=K, and reflect every coordinate. If some n_i is even there is no fixed
vertex; if all are odd there is exactly the central vertex. Thus the
minimum over all gauges and exact cyclic permutation symmetries is exactly
ceil(T/2). This existence statement is algebraic and gives no free gauge
application or transport.

The predecessor's specified dense cycle-boundary format stores two families
of c full length-T scalar vectors, retaining prescribed zeros as slots. It
therefore stores exactly 2cT scalar slots. For the present distinct-width
family the minimum over gauges is

\[
       2T\lceil T/2\rceil=
       \begin{cases}T^2,&T\text{ even},\\T(T+1),&T\text{ odd}.
       \end{cases}                                         \tag{6}
\]

For a fixed G its allowed group can be smaller, never improving this floor.
After a separately paid diagonal conjugation, the same statement applies
to an ordinary permutation-cycle construction for A^-1 G A=KQ. We do not
silently identify a general weighted-shift displacement with ordinary
Stein displacement. Equation (6) is the cost of this defined dense format,
not a lower bound on minimal displacement rank, arbitrary orderings,
implicit generators, separable circuits or multiplication runtime.
Writing or reading each stored scalar costs at least one scalar access;
bit precision, setup, the conjugation and transport must be charged in
addition. Offline setup can have a different global tariff; (6) does not
declare it binding in the complete multiplier.

## 3. Stability under absolute entrywise error

Let G=LHR as above, and suppose

\[
 |G_{xy}|\le M,\qquad |G_{xx}|\ge\delta>0,\qquad
 |X_{xy}-G_{xy}|\le\varepsilon\le\delta/2.                    \tag{7}
\]

Necessarily delta<=M. The diagonal of X is nonzero. Set
a=G_xy G_yx and d=G_xx G_yy, with tildes for the corresponding products
of X. Both product errors have absolute value at most 2M epsilon+epsilon^2.
Since C=a/d is real in (0,1],

\[
 |\mathcal C_{xy}(X)-\mathcal C_{xy}(G)|
 =\frac{|\widetilde a-\mathcal C_{xy}(G)\widetilde d|}{|\widetilde d|}
 \le\frac{4M\varepsilon+2\varepsilon^2}{\delta^2/4}
 \le\frac{24M\varepsilon}{\delta^2}=:\eta.                  \tag{8}
\]

The loose constant 24 is convenient; epsilon<=delta/2<=M/2 would even
give 20. Complex phases cause no change to these triangle inequalities.

Assume gamma_max<2 gamma_min and distinct gamma_i. Define

\[
 \Delta=\min\{e^{-2\gamma_{\max}}-e^{-4\gamma_{\min}},
                  \min_{i\ne j}|e^{-2\gamma_i}-e^{-2\gamma_j}|\}>0, \tag{9}
\]

where the second minimum is omitted for d=1. One may lower-bound that
second term by `2 exp(-2 gamma_max) min_(i!=j)|gamma_i-gamma_j|`.

**Theorem 3.** If (7) holds and

\[
                         48M\varepsilon/\delta^2<\Delta,    \tag{10}
\]

then every underlying permutation of an exact monomial commuting with X
is a coordinatewise identity/reflection. The same is true for ordinary
permutation symmetries. In particular (5) and the dense-format floor hold.

To prove this, exact monomial commutation preserves C(X). Equation (8)
makes the ideal invariant at an original pair and its image differ by at
most 2eta. Unit edges have invariant at least exp(-2 gamma_max); distinct
nonadjacent pairs have weighted squared distance at least 2 gamma_min and
invariant at most exp(-4 gamma_min). Thus edges map to edges. Their distinct
coordinate colors have invariant gaps at least Delta, so every color is
preserved separately. Moving along any color other than k leaves the kth
coordinate of the image unchanged. Connectivity makes that image coordinate
a function of x_k alone. Bijection and preservation of the k-path force
this function to be its identity or reversal. This proves the theorem
without a lower bound on shifts and without presuming any symmetry survives
arbitrary perturbations.

The diagonal floor cannot be suppressed. Scaling a whole matrix below half
a storage quantum rounds it to zero, admitting all vertex permutations.
Even a nonzero diagonal is insufficient: take G=hK with small h equal to
one quantum and sufficiently small off-diagonal K entries. Rounding gives
X=hI. A three-cycle then commutes with X, although distinct widths forbid it
for G. The omitted factor delta^-2 would incorrectly certify this example.

## 4. An approximate inverse, with the dimension factor paid

Suppose X approximates G^-1 with entry error epsilon. Then
`||X-G^-1||_2<=T epsilon` and `||G||_2<=T M` by the Frobenius norm. If
`T^2 M epsilon<=1/2`, write X=G^-1(I+GE), E=X-G^-1. The Neumann identity
gives invertibility and

\[
 \|X^{-1}-G\|_2\le2\|G\|_2^2\|E\|_2
                    \le2T^3M^2\varepsilon=:e.              \tag{11}
\]

Every entry error is at most e. An exact monomial commuting with X also
commutes with X^-1. Theorem 3 therefore applies provided

\[
 T^2M\varepsilon\le1/2,\quad
 2T^3M^2\varepsilon\le\delta/2,\quad
 96T^3M^3\varepsilon/\delta^2<\Delta.                        \tag{12}
\]

No commutant norm is needed because its equality is exact. This argument
does not use a false Gaussian identity for entries of G^-1. It also does
not interchange taking a matrix inverse and taking a principal section.
The error in (11) is an operator error with all T factors displayed.

## 5. Actual anchored square blocks from the retained source

This section uses exactly the canonical `GAUGEFREE-INTERIORS.md` and
`FINE-PRIME-PADDING.md` retained in inputs. The latter replaces the former's
old theta scale by `1/(4p^2)<theta<=1/p^2`; its leading package note explicitly
records that replacement. These are source-bound local statements, not
automatic identification with a complete current periodic caller.

Choose, for each of g distinct original source axes, a nondegenerate square
row/column section with the **same** unit-spaced coordinate interval and
common center. Write its centered coordinates as x,y with
`|x|,|y|<=(n_i-1)/2<=B_i/2`. Both coordinate sets and the phases must satisfy
the following displayed source formulas. Arbitrary independently translated
or permuted row/column sets are not supplied by this theorem.

### 5.1 Broad physical block, including the normalizer

The source defines

\[
 K_i(y,x)=\alpha^{-1}\exp[-b(x-\lambda_i y+\delta_i)^2],
 \quad\lambda_i=(1+\theta_i)^{-1},\quad |\delta_i|\le1/2,
 \quad b=\pi/\alpha^2.                                    \tag{13}
\]

It is diagonally equivalent to a shifted kernel with width
gamma_i=b lambda_i. For completeness the entire normalization is explicit.
Let s_i=-delta_i(1-theta_i), u=x-y, and
`H_i(y,x)=exp(-b lambda_i u^2+2b lambda_i s_i u)`. Then

\[
 K_i(y,x)=\alpha^{-1}e^{-b\delta_i^2}
                  e^{r_i(y)}H_i(y,x)e^{c_i(x)},              \tag{14}
\]

\[
 r_i(y)=b\lambda_i(1-\lambda_i)y^2
                         +2b\lambda_i(\delta_i+s_i)y,
\]
\[
 c_i(x)=-b(1-\lambda_i)x^2-2b(\delta_i+\lambda_i s_i)x.
\]

Expanding both quadratics proves (14). The scalar alpha^-1 exp(-b delta_i^2)
is retained; it is not lost by normalizing the Toeplitz diagonal. If (1)
uses row-minus-column differences, replace s_i by -s_i, as in C6.

More directly, every entry of (13) is at most alpha^-1. At a matching
diagonal coordinate x=y,

`|(1-lambda_i)x+delta_i| <= (1+theta_i B_i)/2`.

Consequently the physical tensor G_B= tensor_i K_i satisfies

\[
 M_B=\alpha^{-g},\qquad
 |(G_B)_{xx}|\ge\delta_B:=\alpha^{-g}e^{-D_B},\quad
 D_B=\frac b4\sum_i(1+\theta_i B_i)^2.                      \tag{15}
\]

These are absolute entry and diagonal bounds of the actual physical
matrix, not the condition number of a gauge used to represent it.

### 5.2 Narrow physical block inside one phase cell

The source also defines, for integer h=j-i and centered coordinates t_i,

\[
 N_{ij}=\exp[-A((\rho h+\beta_i)^2-\beta_j^2)],\quad
 \rho=1+\theta,\quad\beta_i=\beta_0+\theta t_i,\quad A=\pi\alpha^2.
                                                               \tag{16}
\]

All row and column indices must lie in the same phase cell, so
`|beta_i|,|beta_j|<=1/2`. The exact source expansion gives

\[
 N_{ij}=e^{A\theta t_i^2}
          e^{-A\rho h^2-2A\beta_0h}e^{-A\theta t_j^2}.       \tag{17}
\]

Thus the width is gamma=A rho. Importantly, the physical matrix already
has a uniform magnitude bound: N_ii=1, and when h is nonzero,

`|rho h+beta_i| >= rho|h|-|beta_i| >= rho-1/2 > 1/2 >= |beta_j|`.

The exponent in (16) is then negative. The physical tensor G_N over the
g selected axes therefore satisfies **M_N=delta_N=1**. The nontrivial
chirp similarity in (17) does not impose a conditioning loss on this
entry/diagonal estimate. It may still cost precision when actually applied
or inverted; those are separate statements below. The word "inverse" in
the source's description of N does not identify a section of a global
inverse with the matrix inverse of this finite block.

### 5.3 Distinct widths and their visible separation

The retained fine-prime construction supplies distinct odd primes s_i and
dyadic t_i in {r,r/2}, satisfying

\[
 (1-1/(2p^2))t_i<s_i\le(1-1/(4p^2))t_i.                    \tag{18}
\]

Put m_i=(r/t_i)s_i. They are distinct integers below r: within one target
size this follows from distinct primes; across sizes one is odd and the
other even. Hence

\[
 \gamma_i^B=bm_i/r,\quad\gamma_i^N=Ar/m_i,\quad
 |\gamma_i^B-\gamma_j^B|\ge b/r,\quad
 |\gamma_i^N-\gamma_j^N|>A/r.                               \tag{19}
\]

For p>=2 their ranges are `(7b/8,b)` and `(A,8A/7)`. In particular both
families have gamma_max<2 gamma_min. Equation (9) has the explicit lower
bounds

\[
 \Delta_B\ge\min\{e^{-2b}-e^{-7b/2},\;2e^{-2b}b/r\},
\]
\[
 \Delta_N\ge\min\{e^{-16A/7}-e^{-4A},\;2e^{-16A/7}A/r\}.    \tag{20}
\]

These reproduce the exact finite-prime separation established in C6.
The source specialization is an all-broad tensor or an all-narrow tensor.
A mixture of the two families need not satisfy gamma_max<2 gamma_min;
its rounded conclusion requires a separate separation argument. The exact
theorems still apply whenever their distinct-width hypotheses are checked.
We retain its prime-existence premise and proof lineage rather than claim
a new prime theorem. Combining (13)--(20) with Theorem 2 closes the exact
physical-gauge escape: neither these actual broad/narrow blocks nor any
further invertible diagonal left/right gauges can have a long commuting
vertex cycle. The quantitative theorem for further gauges still requires
their own valid M and delta bounds.

## 6. Source precision, inverse range and complete interface limits

Use the retained source regime

\[
 g=O(p^\beta),\quad 0\le\beta<1,\quad
 B_i\le O(p^\xi),\quad \xi<2,\quad
 \alpha^2=\Theta(\log p),\quad
 \log r=\Theta(p^{1-\epsilon_0}),\quad0<\epsilon_0<1.         \tag{21}
\]

Here g is the number of distinct selected source axes and T=product n_i
is their local tile volume, not the full product denoted T elsewhere in
the source. The physical fine-prime hypothesis also supplies theta_i<=p^-2.
Equation (15) gives

`log(delta_B^-1) <= g log(alpha)+O(g/log p)=O(g log log p)=o(p)`.

The narrow diagonal floor is one. Moreover
`log T <= sum log n_i=O(g log p)=o(p)`. The bounds in (20) are `2^-o(p)`:
A=Theta(log p), b=Theta(1/log p), and log r=o(p). It follows that for
every fixed C>0, every error `epsilon<=2^(-Cp+o(p))` eventually satisfies
the forward conditions (7),(10) and the inverse conditions (12), using
M<=1. This is an asymptotic comparison, not a practical threshold claim.

It applies in particular to rounding each physical factor directly with
entry error `epsilon_factor<=2^(-Cp+o(p))`: all physical factors have entries
at most one, and telescoping the tensor entries gives
`epsilon<= (1+epsilon_factor)^g-1 <=2g epsilon_factor` when
`g epsilon_factor<=1`. Arbitrary factor errors need not preserve any symmetry;
the conclusion is only containment of whichever exact symmetries remain.

For the actual finite inverse, the same conclusion requires an actual
inverse approximation satisfying the stated error. We establish no inverse
algorithm by declaring an error tolerance. It is also necessary to account
for the magnitude of inverse coefficients when discussing O(p)-bit records.
The retained stronger chirp guard does this independently of (15):

\[
                         \beta+2\xi-2<1.                   \tag{22}
\]

For (14), direct absolute-value estimates, including the scalar normalizer,
bound the sum of absolute row/column logs per axis by

`|log alpha|+b/4+b theta(B^2/2+3B/2)`.

Here `|delta+lambda s|<=theta` and `|delta+s|<=theta/2`. For (17) the
corresponding bound is `A theta B^2/2`. Across the group these are
`O(g A B^2/p^2+g log p)=o(p)` under (22).

The retained normalized shifted-Gaussian symbol bound is

\[
 \|H_i^{-1}\|_2\le\mu_i^{-1},\qquad
 \mu_i=(1-e^{-\gamma_i(1-2|a_i|)})e^{-\pi^2/(3\gamma_i)}.    \tag{23}
\]

Its positive-real-part Fourier bound passes to every finite Toeplitz
section by compression. The retained source has shift gap at least
theta_i/2 and the widths in (19), making mu_i^-1 polynomial in p uniformly
in the section size. This is the existing symbol/conditioning theorem,
not a new all-source recovery assumption. Tensoring (23) and multiplying
by the explicit inverse diagonal norms above yields
`||G_B^-1||_2, ||G_N^-1||_2 <= exp(o(p))` under (22). Hence O(p) total bits
can represent the inverse magnitudes together with a Cp-bit absolute
fractional tolerance. Producing, storing and accessing those coefficients
still requires a charged algorithm. The stronger source guard also implies
xi<3/2, so it supplies the weaker xi<2 used in (21).

The retained notes compare their ideal shifted blocks, truncation and
globally rounded references with separate quantitative errors. Our theorem
can consume such an error only after it is verified for this same physical
square matrix. It does not infer equality of stored coefficient lists or
extend an ideal entrywise estimate through an unpriced pipeline. Global
periodic wraps, cross-cell coefficients, identity holes, rectangular blocks,
independently permuted row/column index sets, Schur pivots, repeated copies
and identity spectators require their own identification. Nor does a
principal section of a global inverse automatically equal the inverse
treated in section 4.

## 7. Verification, novelty boundary and open obligations

The universal results follow from the preceding algebra, geometry and error
bounds. The bounded exact verifier is corroboration only. It authenticates
the pinned inputs; compares complete small vertex-permutation searches and
direct diagonal-commutation solves with the coordinate prediction; checks
exact inverse commutants, rational error transfers and the physical source
quadratic identities; and includes failure controls for the omitted
conditions. Normal and optimized receipts report their completed domains.

The canonical metadata and bounded live search checked the exact bodies of
CrocSwap/integer-mult-bounds#6099, #5216, #6533, #6613 and #4035, plus the
root's #2066 comparison. #6099 concerns production denominators and a full
physical-period matrix perturbation; #5216 concerns a weighted contraction
and complete inverse consumer. Their physical domains and remaining global
obligations are retained, not superseded. The other results concern finite
field capacities, paid monomial reflection tariffs and Pauli partial fusion.
None of those inspected claims gives this square Gaussian metric/monomial
classification and precision boundary. `OVERLAP.json` records the bounded
query coverage; unpublished work and arbitrary historical diffs were not
exhaustively searched.

Credit Jerry Chen / @CubeJerry; the preceding orbit-constructor, orbit-scale
and heterogeneous-width packages; Vlado Vojdanovski's capped phase-cell
lineage and the fractional-shift/fine-prime notes and their contributors;
and the cited production/weighted-inverse packages for their distinct source
interfaces. The lead orchestrator proposed the invariant/error objective;
the worker independently derived the exact centralizer, direct physical
magnitude bounds, inverse transfer and controls. All preparation and review
use substantial OpenAI assistance. No human or formal-kernel acceptance
is asserted.

The useful next obligation is a source-bound **implicit** or non-cycle
generator application that avoids the defined dense vector materialization,
with full access, precision, setup, transport and inverse budgets. A different
question is extending the invariant to truly rectangular or independently
indexed blocks and matching an actual rounded global caller. Neither is
settled by this package. All five foundational assumptions, selected
certificate and accepted complete multiplication bound remain unchanged.

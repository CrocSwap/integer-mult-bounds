# Unit cycle products do not preserve the unit-weight inverse bound

Prepared for **William Lawyer**, with substantial OpenAI Codex assistance.
Apache-2.0. This is a scoped hypothesis audit and negative result, not a
defect report against PR803, a new multiplication bound, or a claim of
literature priority for weighted-shift algebra.

## 1. The statement being audited

At pinned PR803 commit `d213ac12d4a1ab8f717d942e844df318ceb395fb`,
the Result and Section 5 assume an invertible operator U with
`||U^k|| <= 1` for **every integer k**. With a polynomial P of degree n,
m roots inside the unit disk and `min_{|z|=1}|P(z)| >= delta > 0`,
that note obtains

\[
 B=(1+4m)(1+4n)/\delta,\qquad
 \|P(U)^{-1}\|_\infty\le B\le(1+4n)^2/\delta. \tag{1}
\]

We take its analytic Wiener-coefficient bound as an explicit inherited
premise. We do not re-audit its Hardy or rational arc-length lemmas.
Its exact unit-phase weighted permutations satisfy its operator premise.

The question here is whether pointwise unit magnitude can be replaced by
unit-magnitude **cycle products**, even when each weight is arbitrarily
close to one. It cannot without an additional norm factor or other guard.
The cycle criterion, counterexample family, and perturbation estimate below
have elementary proofs independent of the analytic part of PR803.

All matrix norms below are induced infinity norms on complex coordinate
space. Coordinates are not implicitly renormalized when reporting a norm.

## 2. Exact criterion and the missing factor

Let sigma be a permutation of a nonempty finite index set, and let all w_i
be nonzero complex numbers. Set

\[
 (Wx)_i=w_i x_{\sigma(i)}.
\]

For a sigma-cycle C of length l, let `h_C=product_{i in C} w_i`. Then
`W_C^l=h_C I`. Consequently

\[
 \sup_{k\in\mathbb Z}\|W^k\|_\infty<\infty
 \quad\Longleftrightarrow\quad |h_C|=1\text{ for every cycle }C. \tag{2}
\]

If a cycle has `|h_C|>1`, its positive multiples of l diverge; if
`|h_C|<1`, its negative multiples diverge. Conversely, when every product
has magnitude one, reducing exponents modulo the corresponding cycle
length leaves every row magnitude unchanged, giving finitely many possible
row magnitudes. Different cycle lengths and nontrivial phases cause no
problem: the complex matrices need not be periodic, only their magnitudes.

For a cycle enumerated as `v_j=sigma^j(v_0)`, put

\[
 p_0=1,\qquad p_j=\prod_{t=0}^{j-1}|w_{v_t}|^2
 \quad(1\le j\le l).
\]

Under (2), `p_l=1`. Every cyclic contiguous squared product is a ratio of
two entries of `p_0,...,p_{l-1}`, and every such ratio occurs. Each row of
every integer power has exactly one nonzero entry. It follows that

\[
 \boxed{K^2:=\sup_{k\in\mathbb Z}\|W^k\|_\infty^2
   =\max_C {\max_{0\le j<l}p_j\over\min_{0\le j<l}p_j}.} \tag{3}
\]

The maximum over rows, cycles and exponents can be interchanged; a single
common exponent need not maximize every cycle simultaneously. This gives
an exact O(N) count of rational arithmetic operations for Gaussian-rational
weights. It is not a claim of O(N) bit complexity: numerator sizes may grow.
K itself need not be rational, so the certificate stores K squared.

In particular, `K=1` holds exactly when **every** `|w_i|=1`. One direction
is immediate. For the other, the bounds for W and W inverse respectively
give `max |w_i|<=1` and `max |w_i|^-1<=1`.

There is an equivalent diagonal-similarity interpretation. On each cycle,
choose positive d_i satisfying `|w_i|=d_i/d_sigma(i)`, which is possible
exactly when its product magnitude is one. Then `W=D U D^-1` for a unit-phase
permutation U. Its best positive diagonal condition number is K: on each
cycle the ratio of the largest d_i to the smallest is fixed by (3), and
independent cycle scalings can align all minima to one. This also explains
why comparing arbitrary gauge scales from different cycles would overcharge
the norm.

If `1/P(z)=sum_{k in Z} c_k z^k` has absolutely summable coefficients,
then (3) gives absolute operator-norm convergence and

\[
 P(W)^{-1}=\sum_{k\in\mathbb Z}c_kW^k,\qquad
 \|P(W)^{-1}\|_\infty\le K\sum_k|c_k|\le K B. \tag{4}
\]

Multiplication by the finite polynomial is legitimate under absolute
convergence, and the Laurent coefficient identity gives the identity
operator in both orders. Only one factor K is paid. The last inequality
inherits PR803's analytic premise; (2) and (3) do not.

The multiplier K is sharp for transfer from the *actual* Wiener norm: choose
a nonnegative integer r whose negative power attains (3), and take `P(z)=z^r`.
Then `||1/P||_W=1` and `||P(W)^-1||=K`. Such an r exists by reducing powers
modulo the maximizing cycle length. This does not assert sharpness of the
separate degree-dependent overestimate B in (1).

## 3. A near-unit family defeating any length-independent replacement

Fix any rational `0<eta<1`. Put

\[
 b=1+\eta,\quad a=1+\eta/2,\quad P(z)=z-a,
 \quad\delta=a-1=\eta/2.
\]

For each positive integer s, take a cycle of length `L=2s`, with
`sigma(i)=i-1 mod L`. Its weights are b at indices `0,...,s-1` and
`1/b` at indices `s,...,2s-1`. Every weight has distance at most eta
from 1; its product is exactly 1; `W^L=I`; its eigenvalues lie on the
unit circle; and (3) gives **K=b^s**. The scalar circle gap is exactly
delta, attained at z=1, by the reverse triangle inequality.

Set `A=aI-W`. Its inverse and that of P(W) have identical norms. The
standard finite geometric identity, also used by pinned PR692, gives

\[
 A^{-1}={\sum_{j=0}^{L-1}a^{-j-1}W^j\over 1-a^{-L}}. \tag{5}
\]

The denominator is positive and every matrix entry in (5) is nonnegative.
Thus its infinity norm is the largest row sum, computed by `A x=1`.
At row `s-1`, put `q=b/a>1`, `r=1/(ab)<1`, and
`G(t,s)=sum_{j=0}^{s-1}t^j`. The exact row sum is

\[
 R_s={G(q,s)+q^sG(r,s)\over a(1-a^{-2s})}
     >{q^s-1\over b-a}. \tag{6}
\]

The first s terms alone give the right-hand expression; the omitted terms
and the factor `1/(1-a^-2s)` make the inequality strict. Consequently
`||P(W)^-1|| >= R_s` diverges with s while **n=1, delta, eta are fixed**.
There is no finite bound depending only on those three parameters valid
for this weakened operator class. This is an all-length counterexample
family, not an inference from a failed finite search.

In fact R_s is the maximum row sum. The absolutely convergent infinite
series in powers of W/a shows every row sum exceeds `1/(a-1/b)`: every
path product is at least `b^-j`, and some terms are strictly larger. The
affine recurrence `x_i=(w_i/a)x_{i-1}+1/a` therefore increases on the
b block and decreases on the 1/b block. Its peak is row s-1.

The seed-71 primary witness takes `eta=1/16`, `a=33/32`, `b=17/16`,
`s=128`, `L=256`. The choice of s is the first power of two for which
`(34/33)^s>26`. Exact arithmetic gives

\[
 1936 < \|P(W)^{-1}\|_\infty < 1937,
 \qquad 25/\delta=800,\qquad 5/\delta=160.
\]

Here m=0, so 160 is the sharper inherited unit-weight estimate, and
800 is its degree-only overestimate. Both fail after the weakened
substitution. The correct power-paid bound (4) remains valid, as does
the still sharper geometric bound `K/delta`. No conclusion in PR803 is
contradicted: these W fail its explicit power-norm-one hypothesis.

`EXPECTED.json` records the full rational primary norm and exact digests
for ten smaller-eta threshold certificates. Those finite fixtures make
the family easy to inspect; the divergence proof is (6).

### The local-error threshold, including its boundary

More generally fix `a=1+delta>1`, `0<eta<1`, and consider balanced weighted
cycles with `|w_i-1|<=eta`, always with `P(z)=z-a`.

| Local error | Uniform-in-length conclusion |
| --- | --- |
| eta < delta | Inverse norm at most `1/(delta-eta)` for every admitted W |
| eta = delta | No constant bound; the worst case is of order L |
| eta > delta | No constant bound; the balanced block family grows at least exponentially in L |

For the first row, `||W||<=1+eta<a`; the ordinary Neumann series gives
the displayed bound and does not even need cycle balance. For the boundary
row, a cycle of length l has `W^l=hI`, `|h|=1`. Its geometric inverse has
denominator with magnitude at least `1-a^-l`, while each of its l terms
has norm at most `1/a`, because `||W||<=a`. Therefore

\[
 \|P(W_C)^{-1}\|\le {l\over a(1-a^{-l})}. \tag{6a}
\]

For a matrix of total dimension L, this is at most
`L/[a(1-a^-1)]`; a single L-cycle has the sharper bound in (6a) with l=L.
For fixed delta these are O(L). On even lengths, choose the same two-block
weights with `b=a=1+eta`. In the finite-sum expression for R_s in (6),
q=1 and G(q,s)=s (the later division by b-a is not used), so the
inverse norm is **strictly greater than `s/a=L/(2a)`**. All weights still
satisfy the tolerance and exact cycle product one. This proves the matching
linear lower order at the boundary without making any finite matrix singular.
For odd L, append one unit weight to the two-block cycle of length L-1;
the same first `floor(L/2)` terms give the lower bound `floor(L/2)/a`.

Finally, when eta>delta, b=1+eta>a and the Section 3 argument applies with
these a,b: the lower bound is `[(b/a)^s-1]/(b-a)`, which is exponential in
even length L=2s. Thus the strict local-error/gap threshold is necessary for
a length-independent bound over this whole weakened class. It is not a
necessary condition for the invertibility or good conditioning of an
individual matrix, or a general statement about higher-degree polynomials.

## 4. Sharp cost of local magnitude tolerances

Suppose a balanced cycle has length L and every magnitude is in
`[l,u]`, with `0<l<=1<=u`. A path of length j has product at most u^j.
Because the complementary product is its reciprocal, it is also at most
`l^-(L-j)`. Hence the exact largest possible power bound over this class is

\[
 \boxed{K_{\max}(L,l,u)=
   \max_{0\le j\le L}\min(u^j,l^{-(L-j)}).} \tag{7}
\]

To see attainability, choose j maximizing the expression and denote its
value by M. Fill a consecutive j-entry block with real weights in [1,u]
of product M, and its complement with weights in [l,1] of product 1/M.
Such factors exist because `M<=u^j` and `M<=l^-(L-j)`; one can greedily
take endpoint factors, then one residual factor and ones. They are rational
when l and u are rational. This balanced cycle attains a path product M,
and the upper bound just proved prevents any larger path product.

Pointwise `|w_i-1|<=eta<1` implies the admitted interval
`[1-eta,1+eta]`, and the real attaining weights also meet the original
pointwise constraint, so (7) is sharp for that constraint as well. In the
reciprocal interval `[1/b,b]` and even length 2s it reduces to b^s, attained
by Section 3. Thus rebalancing the product alone does not remove the
accumulated norm cost. This note does not price an implementation of
rebalancing or diagonal coordinate changes.

One consequence for even lengths is that uniformly bounded amplification
over **all** balanced cycles with tolerance eta_L in (0,1) is possible
exactly when `sup_L L*eta_L` is finite. Sufficiency follows from
`K <= (1+eta_L)^L <= exp(L*eta_L)`. Necessity follows from the Section 3
cycles, with `K=(1+eta_L)^(L/2) >= exp(L*eta_L/4)`, using
`log(1+t)>=t/2` for `0<=t<=1` (integrate `1/(1+t)>=1/2`).
Thus exact product rebalancing does not alone remove a length-dependent
precision requirement if this particular power-bound route is used. This
statement concerns worst-case K, not the necessary working precision of a
different inversion algorithm or of a specific polynomial.

### Exact extremal inverse norm for the linear polynomial

The same path envelope gives more than a power bound. For real a>1, a
balanced L-cycle with magnitudes in `[l,u]`, `0<l<=1<=u`, satisfies the
**sharp** inverse bound

\[
 \boxed{\|(aI-W)^{-1}\|_\infty\le
   \mathcal R_L(a,l,u):=
   {\displaystyle\sum_{j=0}^{L-1}a^{-j-1}
                 \min(u^j,l^{-(L-j)})\over 1-a^{-L}}.} \tag{7a}
\]

Indeed the finite geometric inverse has denominator `1-h/a^L`, whose
magnitude is at least `1-a^-L`. Each j-step path has magnitude at most
`f_j=min(u^j,l^{-(L-j)})`. Applying the row-sum bound gives (7a).

Here all of these bounds can be attained **simultaneously**. Set f_0=f_L=1,
take `sigma(i)=i+1 mod L`, and choose the positive real weights
`w_i=f_{i+1}/f_i`. Their product is one. Each ratio belongs to `[l,u]`:
before the crossing of the increasing sequence u^j and decreasing sequence
`l^{-(L-j)}` it is u, after the crossing it is l, and at a crossing the
two defining inequalities place the ratio between l and u. If l=1 or u=1,
all f_j=1 and the claim is immediate. At row zero every path product is f_j,
and h=1; its inverse row sum equals (7a). Since the upper bound applies to
every row, this is the exact induced norm and the maximum over the entire
admitted class, including complex phases.

In the original pointwise tolerance class, set `l=1-eta`, `u=1+eta`.
The attaining positive weights satisfy `|w_i-1|<=eta`, so (7a) remains
sharp for that class, not merely for an enlarged magnitude interval.
For `L=256`, `eta=1/16`, `a=33/32`, the exact maximum lies strictly
between **2164 and 2165**. Its weights consist of 132 copies of 17/16,
one rational residual weight, and 123 copies of 15/16. The simpler
1936-to-1937 witness in Section 3 deliberately uses two reciprocal blocks
to make the all-length growth argument transparent; it is not claimed
optimal. Both witnesses and the residual factor are recorded exactly.

For eta below the gap, (7a) is also bounded by `1/(a-u)` and approaches
that bound as L tends to infinity with fixed a,l,u and l<1<u<a. For each
fixed j its envelope eventually equals u^j, while the summands are bounded
by the summable geometric sequence `a^-1(u/a)^j`; this justifies the limit.
At or above the gap, the formula gives the concrete finite-length cost
behind the growth regimes in Section 3. This is a scoped extremal formula
for a linear polynomial, not a claim about optimal inversion algorithms.

## 5. A sufficient perturbation guard that does not require balance

Let U be a unit-phase permutation, `||W-U||_infinity<=eta`, and
`P(z)=sum_{j=0}^n p_j z^j`. Then `||W||<=1+eta`. The telescoping identity,
which does not require W and U to commute, gives

\[
 W^j-U^j=\sum_{t=0}^{j-1}W^t(W-U)U^{j-1-t},\qquad
 \|P(W)-P(U)\|\le E:=\sum_{j=1}^n|p_j|((1+\eta)^j-1). \tag{8}
\]

The expression also holds at eta=0 by continuity or direct substitution.
Absolute upper bounds on the coefficient magnitudes may replace them.
If a certified `||P(U)^-1||<=B` satisfies the **strict** inequality `BE<1`,
factoring `P(W)=P(U)[I+P(U)^-1(P(W)-P(U))]` and applying the geometric
operator series proves

\[
 \|P(W)^{-1}\|\le B/(1-BE). \tag{9}
\]

For Section 3, even the exact unit bound `B=1/delta` gives `BE=2`, so
this guard does not incorrectly admit the counterexample. Failure of the
guard is inconclusive: it is not a singularity test. The strict boundary
matters: in dimension one, `U=1`, `W=1+eta`, `P(z)=z-(1+eta)` gives
`BE=1` and `P(W)=0`. Conversely, the guard may admit nonunit cycle products;
it is a different sufficient condition from (2).

This guard bounds an exact perturbed matrix. It does not by itself analyze
inexact operation sequences, source access, rounded factor preparation,
dirty restoration, scratch, traffic, or bit costs.

## 6. What the finite replay establishes

`DOMAIN.json` fixes the complete finite domains and stopping rules. A
prefix-based cycle algorithm is checked against separately implemented
dense Gaussian-rational matrix powers, including negative powers and
nontrivial unit phases. The dense oracle derives the magnitude period by
permutation composition, not the cycle algorithm's traversal. Small real
resolvents are inverted by dense Gauss-Jordan and compared entrywise with
an affine cyclic-equation solver; the row formula supplies a third method.
The larger primary witness has an exact sparse residual and row-sum check.

The local-cap construction is checked against direct enumeration of every
cyclic path, and polynomial perturbation bounds against dense exact inverse
norms on every admitted finite case. Sharp inverse attainments are checked
against 96 dense real inverses and three larger affine solves. A further
108 dense Gaussian-rational inverses check the complex-phase denominator;
squared infinity norms are computed exactly from rational within-row
magnitude ratios, with no numerical square-root rounding. These phase
tests cover the magnitude-interval class; their phases need not be near 1.
Named invalid-shortcut controls include
global rather than per-cycle balance, ignoring negative powers, confusing
edge and path amplification, losing weight order, and the singular equality
case of the perturbation guard.

These are exact finite certificates over rational arithmetic, not
proof-assistant formalization or a full audit of the multiplication theorem.
Human review of the written universal arguments remains open. PR803's
analytic premise remains inherited. No source from `upstream/`, selected
frontier, supplier schedule, or multiplication exponent is changed.

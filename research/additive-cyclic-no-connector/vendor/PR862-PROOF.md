# A cubic precision guard for the prime-power cyclic inverse

## Result and boundary

For the PR621 prime-power kernel of order r>=3, the PR628 neighboring
cyclic scan needs working precision

    max(p,w) + O(r^3 + log(D+1)),

including integer magnitude bits, to approximate the inverse to absolute
error 2^-p on a source of norm <=D initially on the 2^-w grid. The same
precision suffices for coarse-grid in-place source recovery. The previous
uniform scan composition charged O(r^4) because it propagated every local
error through a product of individual reciprocal margins. Here every
partial inverse is bounded by the full inverse and complementary factors.

Array execution still costs O(rL) rounded scalar operations. With the same
charged approximate-factorization and coefficient-verification algorithms,
the bit cost for a neighboring cyclic layout is

    soft-O((Lr+r^3)(max(p,w)+r^3+log(D+1))).

This is a standard-arithmetic, supplied-layout theorem. The worst-case
factorization and fast arithmetic are inherited algorithms, not implemented
by the Fraction reference. The restored-source version needs owned widened
source words whose low working bits are initially zero; those bits are
charged. No arbitrary dirty-bit, Clifford, common-label, complete-transform
or multiplication-exponent claim follows.
Phase-oracle costs and the cost of reading a longer phase description are
additional to the displayed bit bound.

## Full inverse controls every partial inverse

Let U be an invertible isometry in the maximum norm: ||U^k||=1 for every
integer k. A unit-weighted permutation, including a weighted cyclic shift,
has this property. Let

    f(z)=product_(j=1)^n (z-rho_j) = s Q(z),
    M >= sum_j |Q_j|,       ||Q(U)^-1|| <= A.

Assume Q(U) is invertible. All factors are polynomials in the **same U**.
The assertion below does not apply to different noncommuting shifts.

For a monic polynomial f define its Mahler measure

    M(f)=product_j max(1,|rho_j|).

For completeness, the elementary circle identity
mean_t log|exp(it)-rho| = log max(1,|rho|) follows by integrating the
power series of log(1-z) when |z|<1 and factoring out rho when |rho|>1.
There are no unit-circle roots in this application. Summing the identities,
then applying concavity of log and Parseval, gives

    log M(f) = mean log|f(exp(it))|
             <= (1/2) log(mean |f(exp(it))|^2)
             = (1/2) log(sum_j |f_j|^2).

Thus M(f)<=||f||_2<=||f||_1<=sM. For any subset J of the root occurrences
(multiplicities included), the complementary factor has coefficient norm

    ||product_(j notin J)(z-rho_j)||_1
       <= product_(j notin J)(1+|rho_j|)
       <= 2^n M(f) <= 2^n sM.

As the factors commute,

    product_(j in J)(U-rho_j I)^-1
       = product_(j notin J)(U-rho_j I) Q(U)^-1 / s.

Every such inverse, including every prefix and every contiguous suffix,
therefore has norm <= B=max(1,2^n M A). Importantly, log B depends on the
full inverse bound, not n times the worst individual reciprocal margin.

For later source restoration, let K_j=1+|Re rho_j|+|Im rho_j|. Then
K_j<=3 max(1,|rho_j|), so every forward subproduct has norm bounded by
its product of K_j, which is <=F=3^n sM. This also bounds amplification of
the rounding errors introduced during forward restoration.

## Rounded execution without repeated reciprocal-margin multiplication

Suppose every factor is implemented by PR628's stable scan with margin
beta, and u=2^-W<=beta^2/2. Including the final outer scalar or inner unit
shift, its local error for an input of norm <=X is at most

    a (X+1)u,       a=7 beta^-3.

Begin with s x and apply all n inverse factors. The exact prefix norm is
<=sBD. Let E_j be the computed prefix error, E=max_(0<=j<=n) E_j, and
delta_j the local error at stage j. Then

    |delta_j| <= a(sBD+E+1)u.

The error at any prefix is the sum of earlier delta_j propagated through
contiguous inverse subproducts. Each propagation has norm <=B, hence

    E <= nBa(sBD+E+1)u.

For t=nBa u<1 this implies

    E <= t(sBD+1)/(1-t).                         (1)

This rearrangement is not an inductive assumption that the error is small:
all finite computed prefixes exist by the stable closure condition, and
their maximum obeys the displayed inequality. The strict contraction
condition then bounds it. The verifier compares every prefix with an
independent exact dense oracle in its small-cycle cases.

## Recovering a coarse-grid source

The cyclic inverse's first pass computes the boundary seed read-only. Its
second pass reads each original source entry before overwriting that slot.
An inner factor's unit shift is performed in place with one saved boundary
entry; an outer factor needs a scalar pass. Thus no full-length intermediate
array is required for evaluation on a neighboring cyclic layout.

After adding the computed inverse to a distinct working-grid target,
apply the forward factors in reverse order. Each forward pass saves the
original cyclic predecessor before overwriting the current entry. It has
error at most u per output entry. Divide by s and round at W bits. Relative
to the original source, the resulting error is at most

    R <= F E/s + nF u/s + u.                    (2)

Alternatively, the finite checker uses the sharper exact recurrence
R=E, then R=K_j R+u for j=n,...,1, then R=R/s+u. If R<2^(-w-1), rounding
each component to the original grid recovers the source exactly. The target
increment is independent of its initial value. The low W-w source bits
are explicit reserved zeros; their capacity is 2L(W-w) bits. Integer guards,
target widening and arithmetic workspace are also charged.

For a fixed coarse-grid external shear, round the computed increment to
the original grid before its exact addition to the target. The resulting
function f(x) approximates Q(U)^-1 x, depends only on x, and gives the exact
grid bijection (x,y)->(x,y+f(x)). Subtracting the identical f(x) is its inverse.
All arrays then stay on the same coarse grid between calls. The separate
composition proof gives a fixed (w,W) budget for an entire prescribed word;
it does not require new low bits at every stage.

## Explicit prime-power budgets

Let r>=3 be a prime power, n=r-1, Dfield=phi(r), H=2^r-1 and
ell=ceil(log2 r), c=ceil(log2 n). To avoid overloading D, write the source
bound as D<=2^m with m>=0. PR621 supplies

    delta = 1/(2rn H^(n Dfield-1)),
    |P(z)|>=delta on |z|=1,
    ||P(U)^-1|| <= delta^-1 + 2nH/(r delta^2).

Its absolutely summable Laurent-series argument applies to the isometry U
above, including varying unit phases. No phase table is constructed for
this norm argument. Put

    d=1+2ell+r n Dfield,           delta>=2^-d,
    a0=2d+r+2,                    ||P(U)^-1||<=2^a0,
    g=d+ell+2r+2,                 beta=2^-g,
    h=a0+2r,
    e=max(d+1,a0+1,p+2a0+m+3),    epsilon=2^-e,
    b=max(n ell,e+r+3).

As in PR628, approximate-factorization and exact coefficient verification
produce dyadic roots for Q=(1/r)product(z-rho_j) with ||P-Q||_1<=epsilon.
The first two e constraints imply |Q|>=delta/2 on the circle and
||Q(U)^-1||<=2^(a0+1). The last one gives

    D ||P(U)^-1-Q(U)^-1|| <= 2^(-p-2).

Also ||Q||_1<=H/r+epsilon<=2^r. PR628's radial derivative argument applied
to Q supplies the stated stable margin beta for its inner or reciprocal
outer roots. Consequently the complementary-factor bound gives B<=2^h.
The forward product bound gives F<=2^v for v=3r+ell.

Define

    J=c+2h+3g+ell+m+5,
    W=J+max(p+2,w+v+3).                         (3)

This W satisfies u<=beta^2/2 and t<=1/2. Since rBD+1<=2^(ell+h+m+1),
equation (1) yields E<=2^(J-W)<=2^(-p-2). Combining with coefficient
perturbation gives total inverse error <=2^(-p-1), leaving extra slack.
Since 2^J>=n+1, equation (2) gives

    R <= 2^(v+J+1-W) <= 2^(-w-2) < 2^(-w-1),

which proves exact source recovery after coarse rounding.

These are explicit integer exponent inequalities, not numerical fits.
Using Dfield<=r, ell<=r, c<=r and r>=3 gives the convenient bounds

    W <= max(p,w)+12r^3+m,
    b <= p+6r^3+m.

For example, J+v+3 <= 7r^3+35r+25+m <=12r^3+m. Likewise
e+r+3<=p+4r^3+11r+14+m<=p+6r^3+m, and n ell<=r^2.
Intermediate magnitude bits also have order O(r^3+m): exact prefixes are
bounded by rBD, scan closure state adds at most O(g) magnitude bits, and
forward subproducts add O(r) bits. A target additionally needs the bits
for its own initial magnitude. Bounds (3) concern fractional precision;
the complete word width includes these integer bits.

## Preparation, phases, and scope

The monic exact polynomial rP has coefficient norm <=H and logarithmic
root bound O(r). Pan's approximate-factorization bound, as stated in
Mehlhorn–Sagraloff–Wang, Theorem 2 and Corollary 1, applies at b>=n log n
with cost soft-O(nb+n^2 Gamma) and O(b+n Gamma) coefficient precision.
Here Gamma=O(r) and b=O(p+r^3+m). The same coefficient oracle and
conservative exact product verification from PR628 cost
soft-O(r^3(p+r^3+m)); the latter forms exact O(rb)-bit coefficients.
Repeated roots need not be individually isolated. This inherits the cited
algorithms; the finite fixture checker does not implement their worst-case
runtime. [Approximate-factorization source](https://arxiv.org/pdf/1301.4870),
PDF page 8.

A supplied exact rational unit phase uses its actual numerator/denominator
length in scalar costs. For an approximate phase oracle, bound the induced
polynomial coefficient perturbation separately and allocate additional
slack by replacing p with p+O(1). Its required precision is O(p+r^3+m)
under the same bounded description assumptions as PR628. An arbitrarily
long phase description remains an extra input cost.

The proof applies to any implementation of each factor with the stated
local error bound. The concrete in-place and restored-source schedule here
covers neighboring cyclic layouts only. PR846's clean-tape arbitrary-stride
solver has a compatible local bound and an additional depth admission
condition; extending the present tape claim would require retaining that
condition and its clean-scratch model. That solver is not part of this
package or its certified source-restoration claim.

The cubic improvement comes from bounding intermediate inverse products,
not from improving PR621's circle lower bound. The full multiplication
assembly, common-label and Clifford interfaces, arbitrary dirty storage,
transform-level phase and normalization accounting remain separate.
No new kappa, practical timing improvement, or literature-priority claim
is made.

## Executable evidence and attribution

The exact verifier checks 5,220 integer budgets over all 116 prime-power
radices from 3 through 512, five target precisions, three source precisions
and three magnitude bounds. These support implementation of (3); the
inequalities above are the all-size proof.

There are 120 kernel executions on ten pinned PR628 fixtures, with both
directions, varying exact rational unit phases and lengths 1,2,3,8,17,64.
Sixty executions compare every prefix to independent dense solves. All
120 check the expanded polynomial residual, pre-round recovery error,
exact coarse-grid restoration and total true-kernel error <=2^-128.
The finite tests use PR628's existing, conservative supplied inverse-norm
certificates; they do not claim that those finite certificates are tighter
than every previous finite execution budget. Six controls reject omitted
complement growth, insufficient target/recovery/coefficient precision,
nonshared shifts and lost prefix contraction.

Credit Ali Romman for PR621, Chafik Boukhalfa for PR628, and the standard
Mahler-measure, cyclic-filtering and approximate-factorization methods.
This extension was prepared by Chafik Boukhalfa with substantial OpenAI
Codex assistance. The independent dense checker is a separate implementation,
not an independent human or delegated-agent review. Source pins are in
`SOURCE.json`.

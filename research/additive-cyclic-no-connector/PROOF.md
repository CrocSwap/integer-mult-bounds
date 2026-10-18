# Additive stable splitting with no borrowed data array

Research draft. This is a local classical arithmetic construction, not a new
kappa or a bit-reversible compiler. The two data arrays are source and target.
Clean scalar preparation and state are additional, explicitly charged space.

## 1. Additive decomposition and numerator bounds

Let U be an immutable unit-weighted cyclic shift, in either direction. Write
the prepared inverse as

    G(U) = alpha U^-ki / (A(U^-1) B(U)),
    A(t) = product_inside (1-a_j t),
    B(t) = product_outside (1-b_j t),
    alpha = r product_outside (-b_j),

where |a_j|, |b_j|<1 and outside reciprocal roots b_j are nonzero. Zero and
repeated inside roots are allowed. Put I(z)=z^ki A(z^-1). Its roots are inside
the unit circle, whereas every root of B is outside. The polynomials are
coprime. Exact polynomial linear algebra gives

    R(z) I(z) + S(z) B(z) = alpha,
    degree R < ko, degree S < ki,

and therefore

    G(z) = R(z)/B(z) + N_minus(z^-1)/A(z^-1),
    N_minus(t) = t^ki S(t^-1).

The second numerator has zero constant term and degree at most ki. The first
summand has a nonnegative Laurent expansion on an annulus containing the
unit circle; the second has strictly negative powers. They are exactly the
two disjoint Laurent projections of G, including multiplicities within
either pole group. No separation between roots in the same group is needed.

If a stable polynomial loses leading degree after coefficient rounding, its
reverse I retains degree ki with the appropriate zero roots. Padded Bezout
columns still give a unique solution: high coefficients of R are forced to
zero when needed. Empty groups give the corresponding single rational
summand. When both groups are empty, G is a scalar shear.

Write ||.||_W for the sum of absolute Laurent coefficients. If K_A and K_B
bound the stable inverse Wiener norms, then

    ||G||_W <= |alpha| K_A K_B = H.

Projection onto a subset of Laurent indices contracts this norm. Consequently

    ||R||_1 <= ||B||_1 H,
    ||N_minus||_1 <= ||A||_1 H.

This avoids bounding individual residues or multiplying pairwise root gaps.
The implementation's component norm |Re|+|Im| is at most twice the Euclidean
modulus, so twice these bounds with component coefficient norms also bounds
its recorded numerator masses.

## 2. A stable filter with a polynomial numerator

For F(z)=1+q_1 z+...+q_k z^k, let K bound ||1/F||_W. Use the companion matrix
C and adjugate coefficients from PR929, with S>=sum_{t>=0}||C^t||. Let
u=2^-W, and allow every source and target component to have arbitrary low
W-grid bits. No low-bit zero field is used.

The increasing causal source lifts, bounded cyclic closure, homogeneous
correction and decreasing inverse lifts are those of PR929. During output,
the source holds the causal sequence z_i. A k-entry state holds previous
homogeneous corrections. To apply a numerator N(t)=sum_{j=0}^d n_j t^j,
where d<=k, form the output from

    y_tilde_i     = z_i + h_tilde_i,
    y_tilde_(i-j) = z_(i-j) + h_tilde_(i-j),

using z_t=0 for t<0. Nonnegative causal entries are read from the source;
negative homogeneous entries are available from the initial closure seed.
Only k previous homogeneous entries are retained. There is no length-L
intermediate or copied source in this execution path.

The exact periodic closure identifies these initial past values with the
corresponding periodic solution, also when L<k. For the approximate closure,
the same forcing and seed estimates prove

    |y_tilde_t - (F(U)^-1 x)_t| <= E=(K+2S+3)u

for every output index and every initially used past index -k<=t<0. To see
the additional boundary case, the causal forcing contributes the same Ku
and coefficient-window term as in PR929. Before forward propagation the
closure and gauge seed errors are no larger than their propagated bounds,
since S>=1. Initial W-grid rounding contributes at most u. Thus the existing
E also covers the past values; no exact periodicity of the rounded state is
assumed. This boundary distinction matters for numerator terms crossing
the cyclic seam.

For exact numerator coefficients and unit phase windows, the numerator
amplifies this error by at most J=sum_j |n_j|. It requires O(k) arithmetic
per coordinate. The reverse causal lifts restore the source bit for bit.
The increment is independent of the incoming target, so its negative call
cancels exactly even though rounding makes it nonlinear in the source.

Apply the positive and negative Laurent summands as two such additive calls,
using the opposite cycle orientation for the negative powers. Both calls
restore the same source. Their errors add; no dirty commutator or borrowed
length-L connector is required. Reverse their order and signs for a literal
inverse of the rounded instruction word.

## 3. Bounded polynomial and numerator preparation

Let D bound the incoming source magnitude. First round the nonconstant
coefficients of A and B to dyadics, giving coefficient errors delta_A and
delta_B. The causal Wiener Neumann argument gives

    K_A <= K_A0/(1-K_A0 delta_A) <= 2 K_A0,
    K_B <= K_B0/(1-K_B0 delta_B) <= 2 K_B0,

when each product K_0 delta is at most 1/2. In particular the rounded stable
polynomials still have no zeros in the closed unit disk, and their reversed
inside polynomial remains coprime to the outside polynomial. This justifies
the exact additive decomposition on the rounded coefficients.

The product inverse perturbation, including |alpha|<=r, is at most

    r [K_A K_A0 delta_A K_B0 + K_A K_B K_B0 delta_B] D.

The implementation supplies the polynomial rounding helper with magnitudes
2 max(1,r) K_B0 max(1,D) and 2 max(1,r) K_A0 max(1,D), respectively.
Its two inequalities make the displayed perturbation at most 2u.

Round alpha to a dyadic alpha_tilde with

    |alpha_tilde-alpha| K_A K_B D <= u.

Now solve the Bezout coefficient system exactly by fraction-free integer
elimination. Its polynomial entries and right-hand side are dyadic with
bounded precision; the potentially longer exact root-product denominator
of alpha does not enter this solve. Round each resulting numerator so

    delta_Nplus K_B D <= u, delta_Nminus K_A D <= u.

The entire preparation error from the original prepared root factors is at
most 5u. Exact solve intermediates and final rational coordinates are wider
than stored coefficients and are charged below. No numerical pivot
conditioning assumption is made.

## 4. Bounded numerator phase windows

During a numerator output, form the j-phase product sequentially, rounding
after each unit-phase multiplication at precision T_FIR. Round its product
with n_j once. The sum of coefficient errors is at most

    epsilon_FIR = [d+1 + sum_j j |n_j|] 2^-T_FIR.

Component norms may replace the moduli for a rational upper bound. Every
filtered value used in this output, including its initial negative history,
has magnitude at most K D+E. Choose

    epsilon_FIR (K D+E) <= u.

One final W-grid rounding adds at most another u. Thus this additive call
has error at most

    [J(K+2S+3)+2]u,

relative to its rounded numerator and polynomial. Polynomial coefficients,
recurrence phase windows, closure power, initial gauge and numerator phase
windows all have bounded dyadic representations. Widths depend
deterministically on fixed inputs and the source; exact source restoration
therefore reproduces the identical negative increment.

## 5. Explicit prime-power precision budgets

Retain the prepared-root hypotheses of PR621/628/862/929. In particular the
common-operator complement argument supplies K_A0,K_B0<=2^k0 for every
stable group. This is a certified input premise, not a conclusion inferred
from approximate roots. The finite kernel bridge separately checks its
coefficient-mass and full-inverse premises on every consumed fixture.

For prime-power r>=3 put

    ell=ceil(log2 r), phi=EulerPhi(r), ell_L=ceil(log2 L),
    d0=1+2ell+r(r-1)phi, a0=2d0+r+2,
    k0=a0+3r+ell+2, s0=k0+1+r^2+2ell,
    j0=2k0+ell+r+6.

The rounded stable inverse norms are at most 2^(k0+1), and their companion
sums S are at most 2^s0 by PR929's adjugate recurrence. To account for the
component norm explicitly, a rounded stable polynomial of nominal order k
has total component coefficient mass at most 2^(k+1): its nonconstant
Euclidean mass is at most 2^k-1+1/2, its constant is exactly one, and
|Re|+|Im|<=2|.|.

Since |alpha_tilde|<=r+1, the product inverse has Wiener norm at most
2^(2k0+ell+3). The Laurent argument bounds each exact numerator's component
mass by 2^(2k0+ell+r+4). Numerator rounding changes that component mass by
at most two when W>=ell. Thus J<=2^j0 safely bounds each rounded numerator.

Each stable output call contributes at most 2^(j0+s0+3-W). Both calls and
the preparation error <=5u together contribute at most 2^(j0+s0+5-W).
For target 2^-p and incoming grid 2^-w choose

    W = max(w, p+j0+s0+7).

Execution error is then at most 2^(-p-2). Choose the inherited original
kernel preparation with inverse error at most 2^(-p-3) on the source; adding
that distinct perturbation still meets the target 2^-p.

Assume max_i(|Re x_i|+|Im x_i|)<=2^m, m>=0; use the same initial bound for
the target when charging its integer guard. A Euclidean source/target bound
2^m can instead use m+1 below. The following scalar fractional widths are
sufficient:

    stable polynomial coefficients: W+3k0+2ell+m+3,
    outer scalar alpha:              W+2k0+m+3,
    Bezout numerators:               W+ell+k0+m+2,
    recurrence phase windows:        W+r+ell+4s0+m+7,
    initial gauge:                   W+ell+3s0+m+6,
    companion and full phase power:  W+ell_L+6s0+ell+m+7,
    numerator phase windows:         W+ell+j0+s0+m+5.

These imply every smallness and forcing inequality above. For example, the
recurrence-window coefficient sensitivity is at most 2^(r+ell), and its
propagated error sensitivity at most 2^(4s0+m+6). The numerator-window
sensitivity is at most 2^(ell+j0+1), while K D+E<=2^(s0+m+3).
The closed-loop matrix error uses the same summable-power expansion as
PR929, including the independently rounded full phase product.

The implementation chooses widths by exact integer bit lengths and one
rational comparison, not by a precision-sized search. For the matrix step
it uses C0=4(L-1)S^2 k+L S. When L*2^-V<=1, the closure error is at most
C0*2^-V. Selecting V to satisfy phase error, product-expansion smallness,
Neumann smallness and 4S^3 C0 K(D+u)*2^-V<=u gives the displayed bound.
The other widths directly solve their rational inequalities. The written
uniform widths are upper bounds on these adaptive choices.

One sufficient integer guard is

    G = m+2s0+k0+j0+r+ell+12.

It covers the causal sequence, seed, homogeneous state, both target
prefixes, recurrence/FIR products and accumulations, and bounded matrix
products. Exact linear solves have separately wider intermediates below.
No overflow or modular wrap is part of the mathematical algorithm.

Using phi<=r and ell<=r, the budget expressions are bounded by cubic
polynomials. The following exact remainders in t=r-3 have nonnegative
coefficients; `additive_budget.py` constructs them by coefficient arithmetic:

| Quantity, after removing W and m when applicable | Cubic cap | Remainder coefficients, ascending powers of t |
| --- | --- | --- |
| Working overhead | 12r^3 | 82, 161, 59, 6 |
| Polynomial width overhead | 12r^3 | 108, 169, 60, 6 |
| Alpha width overhead | 12r^3 | 183, 222, 76, 8 |
| Numerator width overhead | 12r^3 | 250, 272, 92, 10 |
| Recurrence-window overhead | 16r^3 | 79, 194, 76, 8 |
| Matrix overhead, also removing ell_L | 24r^3 | 128, 293, 114, 12 |
| Numerator-window overhead | 12r^3 | 81, 160, 59, 6 |
| Integer guard, removing m | 16r^3 | 25, 157, 62, 6 |

The gauge width is no larger than the recurrence-window width. In particular
W<=max(p,w)+12r^3 and G<=m+16r^3. The conservative word allowance

    A = max(p,w)+2m+64r^3

therefore covers stored data and coefficient operands, including guards.
Scalar powering additionally needs ell_L fractional bits. Exact product
and dot-product accumulators have the usual constant-factor wider size.

## 6. Arithmetic, storage and scope

The two filters and their numerators use O(rL) scalar data arithmetic on a
supplied neighboring cycle. Each phase-window step multiplies a bounded
dyadic by one exactly supplied rational unit phase. If its bit size is at
most B_phi, the data work is soft-O(rL(A+B_phi)). No exact long phase product
is retained on the normal execution path. Dense matrices, exact phase-window
oracles and source snapshots occur only in the separate audit/checker path.

Companion powering costs O(r^3 log L) arithmetic at width O(A+log L).
The additive Bezout system and cyclic closures have dimension O(r). After
clearing a common dyadic denominator, their real integer embeddings are
solved by classical fraction-free elimination. Intermediate minors have
O(r(A+log L+log r)) bits. O(r^3) integer operations and exact rational back
substitution give soft-O(r^4(A+log L)) bit work. Coefficient products and
companion-adjugate preparation fit this conservative scalar term; inherited
root preparation is separately included by its soft-O(r^3(p+m+r^3)) bill.

The resulting supplied-cycle bill is

    soft-O(rL(A+B_phi) + r^3 log L(A+log L) + r^4(A+log L)).

Clean scalar workspace is O(r^3(A+log L+log r)) bits. There are **zero
borrowed length-L data arrays**, but the scalar workspace can exceed a data
array when L is small. It is not free space, and clearing classical scalar
state is not a bit-reversible arithmetic implementation. The Python reference
verifies exact arithmetic and bounds; it is not a measured implementation of
the asymptotically fast integer arithmetic hidden by soft-O.

Unit-phase access and source/target separation are part of the interface.
Prepared roots and phase data are immutable and distinct from mutable data. Arbitrary-stride tape routing, irrational phase
approximation, common-label/Clifford realization, scalar-space hosting and
the full multiplication reduction remain separate obligations. No new kappa
or universal practical speedup is claimed.

The work uses classical partial fractions by separated pole groups,
one-sided Laurent projection, companion filtering and Bareiss elimination.
It extends the source-restoring construction of PR628, common-operator
precision argument of PR862, arbitrary-dirty bounds of PR905, and grouped
periodic filter of PR929. No priority claim is made for those classical tools.
Finite exact checks support this written argument; they are not a
proof-assistant verification or independent human review.

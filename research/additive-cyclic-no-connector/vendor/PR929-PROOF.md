# Higher-order periodic filters on arbitrary dirty arrays

Research construction, 2026-10-13. No new kappa or full multiplication construction.
This note concerns ordinary classical scalar arithmetic and exact restoration
of the working-grid data arrays. Clearing the scalar state is not a
bit-reversible arithmetic compiler. It introduces O(k^2) scalar slots (and
wider exact-solve intermediates), which are not free clean space.

## 1. Stable polynomial and companion bound

Let F(z)=1+q_1 z+...+q_k z^k=prod_j(1-b_j z), with |b_j|<1.
Complex absolute values below are Euclidean, matrix norms are induced infinity
norms, and K bounds the sum of absolute impulse coefficients of 1/F.
The elementary choice is K=prod_j(1-|b_j|)^-1. A stronger certified Wiener
norm bound can be substituted without changing the algorithm.

Let C have first row (-q_1,...,-q_k) and ones on the subdiagonal.
Set B_0=I and B_j=C B_{j-1}+q_j I for j=1,...,k-1.
Cayley-Hamilton gives C B_{k-1}+q_k I=0, hence

    (I-zC)^-1 = (sum_{j=0}^{k-1} B_j z^j) / F(z).

Consequently S=K sum_j ||B_j|| bounds sum_{t>=0} ||C^t||.
In particular S>=1 and ||(I-eta C^L)^-1||<=S for every L>=1 and |eta|=1.
This proof permits repeated and zero b_j. It does not require root separation.

## 2. Weighted causal lifting and cyclic closure

Let (Ux)_i=phi_i x_{i-1 mod L}, with |phi_i|=1. All incoming source and
target coordinates are arbitrary Gaussian W-grid integers, u=2^-W. No low
bits are reserved. Let

    a_{i,j} = -q_j prod_{t=0}^{j-1} phi_{i-t mod L}.

In increasing i, replace x_i by x_i+round_W(sum_{j<=min(k,i)} a_{i,j} x_{i-j}).
This uses only previous modified source entries and exact grid additions.
Every complex rounding error has modulus <=u (real-only errors <=u/2).
Thus the resulting causal sequence z is the exact zero-initial-state solution
of F(U_causal)z=x+delta, for a forcing vector |delta_i|<=u.
Its magnitude is bounded by K(D+u), where D=max_i |x_i|.

Define g_-1=1, g_i=phi_i g_{i-1}, extended to negative i using inverse phases.
Let D_i=diag(g_i,...,g_{i-k+1}). The varying state matrix is
C_i=D_i C D_{i-1}^-1. Over one cycle,

    C_{L-1}...C_0 = eta D_-1 C^L D_-1^-1,
    eta=prod_{i=0}^{L-1} phi_i.

Let v=(z_{L-1},...,z_{L-k}), with z_i=0 for negative indices. The periodic
homogeneous seed is s=D_-1 (I-eta C^L)^-1 D_-1^-1 v. This remains correct
when L<k: the closure equation enforces the repeated cyclic coordinates.
Generate the homogeneous correction using C_i and add z_i+h_i to the target.
Finally undo the causal source lifts in decreasing i. At each undo, every
earlier source entry still equals the value used by the original lift.
The original source is therefore restored bit for bit.

The generated target increment depends on the source, coefficients, and
precision, never on the incoming target. Changing the final addition sign
therefore gives the exact inverse of the entire rounded call, even though
the increment is generally nonlinear as a function of the source.

## 3. Uniform error with exact closure

The exact periodic solution for x+delta differs from F(U)^-1 x by at most Ku.
Round the seed once to the W grid, then round each homogeneous recurrence.
Unit diagonal gauges preserve norms. Seed rounding contributes at most Su;
the sum of propagated recurrence errors contributes at most Su. Thus

    ||generated_increment - F(U)^-1 x|| <= (K+2S)u.

For the real unweighted algorithm, replace u by u/2 in this expression.
The bound is independent of L. This statement currently assumes exact
polynomial and phase-window coefficients. Coefficient evaluation cost is
charged separately, not silently treated as fixed-width arithmetic.

## 4. Bounded-precision scalar preparation

Compute C^L by recursive binary powering, rounding each matrix product entry
to scalar precision V, u_s=2^-V. The unfolded expression tree has L leaves
equal to C and L-1 internal products. Each local matrix error has norm at
most delta=k u_s (k u_s/2 in the real case).

Expand the computed expression by substituting exact product plus local
error at every node. A surviving term with j error nodes consists of those
j matrices separated by at most j+1 exact powers of C. No selected error
node is an ancestor of another in a surviving term. Ignoring this restriction
only increases the count, which is at most binom(L-1,j). Therefore

    ||M_tilde-C^L|| <= S ((1+S delta)^(L-1)-1)
                    <= 2(L-1)S^2 delta = e_M,

provided (L-1)S delta<=1/2. Reused subexpressions in binary powering do not
invalidate this bound: unfold them into separate occurrences of the same
error matrix, and bound every term by its norm.

Compute eta by multiplying its unit phases sequentially with scalar-grid
rounding. Unit modulus implies |eta_tilde-eta|<=L u_s=e_eta. Multiply
eta_tilde by the rounded power exactly, retaining up to 2V fractional bits.
The closure-matrix error is bounded by

    e = (1+e_eta)e_M + e_eta S.

If e<=1/(2S), the perturbed closure inverse has norm <=2S. The seed error
before W-grid rounding is at most 2S^2 e K(D+u). Its propagated output error
is at most 2S^3 e K(D+u). The full bound is therefore

    (K+2S)u + 2S^3 e K(D+u).

Choose V so the extra term is <=u. It suffices to take
V=W+log_2 L+O(log k+log K+log S+log(D+1)), with explicit integer inequalities
as implemented in weighted.py. The real unweighted version omits phase
error and uses u/2 bounds. The closure solve is exact rational arithmetic on
the bounded dyadic matrix, not floating-point Gaussian elimination with an
unproved pivot-stability assumption.

## 5. Rounded coefficients and phase windows

The stable polynomial is prepared from roots once, then its nonconstant
coefficients are rounded to a fixed dyadic grid. If the coefficient error has
sum of moduli delta and K_original*delta<=1/2, the causal Wiener-algebra
Neumann series proves that the rounded polynomial has inverse norm
K<=K_original/(1-K_original*delta)<=2K_original. No assertion about the
locations of numerically rounded roots is required. The difference between
the two inverse filters is at most K_original*K*delta*D. Choose coefficient
precision so 2*K_original^2*delta*D<=u, adding at most one ulp of error.
Recompute the companion-adjugate bound S for the rounded polynomial.

Do not form exact length-k rational phase products in the data scans. At
coefficient precision T, round the accumulating unit-phase product after each
step, and round its product with q_j. Let

    R = k + sum_j j |q_j|,
    epsilon = R * 2^-T.

The total coefficient error in every window is at most epsilon: the j-th
phase product error is at most j*2^-T. The implementation uses the rational
upper bound |Re q_j|+|Im q_j| for |q_j| in R.

Require K*epsilon<=1/2 and S*epsilon<=1/2. The perturbed causal recurrence
then obeys Z=max_i |z_i|<=2K(D+u), because its additional forcing is at most
epsilon*Z. Its forcing relative to the exact-coefficient recurrence is at
most u+2K*epsilon*(D+u). The exact periodic response to that forcing adds at
most K*u+2K^2*epsilon*(D+u) to the desired output.

The perturbed closure seed with an exact initial gauge has norm at most
2S*Z. The rounded-gauge construction below adds at most u before data-grid
rounding, so the actual initial state has norm at most 4SK(D+u)+2u.
If H bounds every homogeneous state, including that seed, its recurrence implies

    H <= S(seed_bound+u+epsilon*H)
      <= 8S^2 K(D+u)+8S u.

This uses the same absolutely summable transition bound S, so there is no
factor L. The total extra output error from coefficient windows is at most

    epsilon * [2K^2(D+u)+8S^3 K(D+u)+8S^2 u].

Choose T so this quantity is <=u. The larger causal-tail bound changes the
closure-error term to 4S^3 e K(D+u); choose V so this too is <=u.
Also round the k initial gauge-prefix products at precision T_g. If
eta_g=k*2^-T_g<=1, each approximate diagonal value differs from its unit
value by at most eta_g. Transform the causal tail with the conjugates of
these approximate values, solve the dyadic closure system exactly, and
multiply by the approximate diagonal on exit. In particular, do not divide
by an approximate phase. Relative to using the exact gauge with the same
approximate closure, the seed error is at most

    2S*eta_g*(2+eta_g)*Z <= 6S*eta_g*Z.

Choose 12S^2 K(D+u)*eta_g<=u. This makes the seed error <=u/S and its output
error <=u, and justifies the homogeneous-state bound above. Both the matrix
and right-hand side of the scalar solve are now dyadic, even when the input
unit phases have non-dyadic rational coordinates.

The resulting output error relative to the rounded polynomial is
(K+2S+3)u, and relative to the original polynomial is (K+2S+4)u.

Finally, compute the output multiplier at fixed dyadic precision too. Start
with the rounded group scalar alpha, then multiply any inner unit-shift
phases one at a time, rounding each product. With h phase steps the
multiplier error is at most (h+1)*2^-T_out. Choose T_out so this times
K*D+(K+2S+3)u is <=u. Rounding the final multiplier-times-output adds another
ulp. If |alpha|<=a, the complete group error is

    E_group = [a*(K+2S+4)+2]u.

An empty stable group is a direct rounded scalar shear, with error <=u.
Every width is deterministic from the current source and the fixed inputs.
The source itself is restored exactly, so repeating the call with negative
sign computes exactly the same increment for cancellation.

## 6. Two-group dirty composition

For outside roots rho, put b=1/rho, so
(U-rho)^-1 = -b*(I-bU)^-1. For inside roots b,
(U-b)^-1 = U^-1*(I-bU^-1)^-1. Thus split all root factors into the two
stable polynomials, assign alpha=r*prod_outside(-b) to the outside group B,
and assign U^-k_inside to the inside group A. Since all are functions of one
unit-weighted shift, their product is the original mixed cyclic inverse,
including the scalar r. The inside inverse shift is a unit-phase permutation
of the output destinations, not a rounded rotation of the source array.

Use one arbitrary dirty connector z and execute B(x,z), A(z,y),
B(x,z)^-1, A(z,y)^-1. All four group calls restore their source. The two B
calls see the same x and cancel the connector increment bit for bit. The
whole instruction word has an exact inverse obtained by reversing calls and
signs. No rounded-linearity assumption is used.

Writing the actual group functions as B_tilde and A_tilde, the forward
increment is A_tilde(z+B_tilde(x))-A_tilde(z). Its error from A B x is at most

    ||A|| E_B(x) + E_A(z+B_tilde(x)) + E_A(z).

Each A error is charged separately because source-dependent precision can
change its rounded polynomial and constants. The ideal A norm is independent
of those choices. This distinction is implemented explicitly in grouped.py.

The execution path uses source/phase index views, not length-L copies.
It has four group calls, O((k_inside+k_outside)*L) data arithmetic operations,
and exactly one length-L dirty connector. O(k^2) clean scalar slots plus wider
exact-solve temporaries are additionally required and explicitly charged.
For k^2>=L these scalar slots can exceed the size of a data array; no space
advantage is claimed in that regime. Clearing them is ordinary classical
arithmetic, not a bit-reversible computation.

## 7. Common-operator bound, explicit cubic budgets, and bit cost

The PR862/905 complementary-factor argument applies to the bilateral unit
shift as well as every finite weighted cycle. With n=r-1, polynomial
prod(z-rho_j)=rQ(z), coefficient norm <=M, and full inverse norm <=H, every
unscaled subset inverse has norm <=2^n M H. A bilateral convolution operator
on l-infinity has norm equal to the l1 norm of its impulse coefficients:
the upper bound is the triangle inequality, and the lower bound follows by
choosing the input phases to align any finite set of coefficients at one
output and then taking increasing finite sets. The stable filters have
absolutely summable causal coefficients, so this applies to them.

For the inner stable group, removing the unit shift preserves this norm.
For the outer stable group, removing prod(-1/rho) costs at most
prod_outside |rho| <= rM by the Mahler bound. Hence one common choice is

    K_original <= r * 2^n * M^2 * H.

For prime-power r>=3, retain the inherited prepared-root hypotheses from
PR621/628/862: M<=2^r, H<=2^(a0+1), and input norm <=2^m, with

    ell=ceil(log2 r), phi=EulerPhi(r),
    d0=1+2ell+r(r-1)phi, a0=2d0+r+2,
    k0=a0+3r+ell+2,
    s0=k0+1+r^2+2ell.

Thus K_original<=2^k0. Rounded polynomial preparation has K<=2K_original.
Its nonconstant Euclidean coefficient sum is at most 2^k, since the
original stable polynomial has total coefficient sum <=2^k and its
perturbation is <=1/2. The implementation bounds matrix entries by
|Re z|+|Im z|, which can exceed Euclidean modulus. Charge that explicitly:
c=max(1,sum_{j>=1}(|Re q_j|+|Im q_j|))<=2^(k+1). The adjugate recurrence in
this submultiplicative component norm gives ||B_j||<=(j+1)c^j and
sum_j ||B_j||<=k^2 c^(k-1). Since (k+1)(k-1)<=r^2 for k<=r-1, this proves
S<=2^s0 for the actual computed upper bound, without multiplying a worst
root gap k times.

Every group error coefficient is <=16r*2^s0, including empty groups, while
||A||<=2^k0. The mixed four-call error is therefore bounded by
2^(k0+s0+ell+6-W). Set

    W=max(w_input, p+k0+s0+ell+8),
    m_call=m+k0+ell+4.

The execution error is at most 2^(-p-2). The latter exponent bounds the
magnitude of every group source: z+B_tilde(x) has norm at most
(rK_original+2)(D+1). This uses the already proved uniform group error,
whose coefficient times 2^-W is <=1. The two B calls always have the same
source. The inherited polynomial preparation can be chosen with error
<=2^(-p-3) on the original source, so total error is <2^-p.

The following explicit sufficient scalar fractional widths are checked by
budgets.py. Here ell_L=ceil(log2 L).

    polynomial coefficients: W+2k0+m_call+ell+3,
    phase windows:           W+r+ell+4s0+m_call+7,
    companion/phase power:   W+ell_L+6s0+ell+m_call+7,
    initial phase gauge:     W+ell+3s0+m_call+6,
    output multiplier:       W+ell+s0+m_call+4.

For example R<=2^(r+ell), the phase-window sensitivity is at most
2^(4s0+m_call+6), and the closure perturbation contribution is at most
2^(ell_L+6s0+ell+m_call+6-V). These inequalities directly imply each
smallness and error condition above. The implementation chooses widths
adaptively from its exact certified constants; these displayed widths are
uniform upper bounds. The implementation's optional Wiener bound is an
explicit certified input premise; the kernel bridge verifies the full
polynomial premises before exercising it. It is not inferred from roots
by silently assuming the conclusion.

Using phi<=r and ell<=r gives

    W <= max(w_input,p)+8r^3,
    coefficient width <= W+m+12r^3,
    window width <= W+m+16r^3,
    matrix width <= W+m+ell_L+24r^3,
    gauge width <= window width,
    output width <= W+m+8r^3.

For the three principal caps the nonnegative remainder polynomials in
t=r-3 are respectively

    51+105t+39t^2+4t^3,
     3+142t+60t^2+6t^3,
    52+241t+98t^2+10t^3.

One sufficient integer guard is
m+2s0+3k0+2ell+r+12 <= m+16r^3. It bounds the causal source, homogeneous
state, matrix products, output accumulation, and coefficient dot products;
the exact solve has separately wider intermediates. Therefore

    A=max(w_input,p)+2m+48r^3

bounds a stored data/coefficient operand word, and A+ell_L bounds a stored
scalar power/gauge operand word. Exact product and dot-product accumulators
use O(A) and O(A+ell_L) bits respectively; their constant-factor widening is
included in the arithmetic work and scalar workspace. The source and connector retain all their original W-grid
low bits; no clean low-bit field is used to recover them.

Let B_phi bound the bit size of one exactly supplied rational unit phase.
Each bounded phase-window step multiplies one T-bit dyadic by one input
phase and rounds; no exact long phase product is retained. The leading data
cost is O(rL) scalar operations at widths O(A+B_phi). Companion powering
uses O(r^3 log L) arithmetic at width O(A+log L). A k-dimensional complex
closure solve is embedded into a 2k-dimensional real integer system by
clearing one common power-of-two denominator. Fraction-free elimination
uses O(k^3) integer operations, with intermediate entries equal to minors.
The elementary determinant bound gives O(k(A+log L+log k)) bits per minor.
The adjugate bound uses the companion structure to compute each C B_j in
O(k^2) operations, giving O(k^3) operations on at most O(kA)-bit coefficients.
Its soft-O(k^4 A) preparation cost fits the same scalar bill. Final exact
rational back substitution is also charged. This yields
soft-O(r^4(A+log L)) bits of scalar solve work and
O(r^3(A+log L+log r)) clean scalar workspace bits. The implementation uses
this classical fraction-free algorithm and checks every exact division.

The inherited root preparation is soft-O(r^3(p+m+r^3)); a conservative
explicit grouped-kernel bill, including four calls, scans, phase access,
matrix powering, solves, and coefficient preparation, is

    soft-O(rL*(A+B_phi) + r^3 log L*(A+log L)
           + r^4*(A+log L)).

This trades the previous quadratic-in-r data term for a larger scalar
preparation term. It is beneficial asymptotically in sufficiently long
cycles, not an unconditional speedup for every (r,L). The reference Python
code and its runtime are not claimed to implement the asymptotically fast
integer multiplication algorithms hidden by soft-O.

The data layout is a supplied neighboring cycle. Arbitrary-stride tape
routing, clean scalar storage in a surrounding compiler, irrational phase
preparation and its error, common-label/Clifford realization, and the full
multiplication reduction remain separate obligations. This is a local
classical arithmetic theorem, with no new kappa.

## 8. Finite evidence and attribution

certified.py: 160 real cases; exact and rounded preparation, repeated/zero
roots, arbitrary nonzero low bits, L<k, restoration and inverse cancellation.
Five deliberately broken closures/seed/tail/undo variants are detected.
weighted.py: 40 complex unit-phase cases, independent dense F(U) oracle,
nonzero closure rounding, exact restoration and inverse cancellation;
omitting the initial phase gauge is detected.
grouped.py: 120 mixed-root cases in both directions, three dirty connector
patterns, empty groups, zero inside roots, repeated roots and L<k. The dense
oracle solves the original root factors independently of grouped filtering.
Polynomial rounding, phase-window rounding, output multiplier rounding, initial-gauge rounding, and
dirty nonlinear dependence are nonvacuous. Shift and coarse-window defects
are detected. All arrays restore exactly; inverse words cancel exactly.
The kernel bridge additionally covers 48 cases using all ten pinned
prime-power fixtures (radices 3 through 16), including the externally
certified common Wiener bound for radices 3 and 4. Each meets the original
128-bit target after coefficient perturbation is charged. controls.py adds
16 rejected mathematical/contract defects and 36 independent fraction-free
solver comparisons with nonzero row-pivot counts. budgets.py checks 2,313
integer rows and the written all-size polynomial identities.

State-space filters and companion-matrix initial-state solves are classical;
see https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter_zi.html
for an established state-space implementation (its documented initial state
is the constant-input fixed point, not the periodic closure above).
The current integration builds on the dirty first-order lifting construction
in PR628, the common-operator bounds in PR862, and the arbitrary-dirty prefix
analysis in PR905. No literature-priority or sole-authorship claim is made.

The exact closure solver uses the classical integer-preserving elimination
of Erwin H. Bareiss (1966 report, 1968 journal article), not a new linear
algebra algorithm: https://digital.library.unt.edu/ark:/67531/metadc1035277/
and doi:10.1090/S0025-5718-1968-0226829-0. Its integration here is the bounded
cyclic-closure preparation and the explicitly charged bit/space bill.

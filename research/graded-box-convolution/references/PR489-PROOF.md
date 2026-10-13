# A branch-free interior inverse with an explicit source perturbation

This replaces only the online phase-cell interior inverse. The rational
truncated global matrix H, exact Schur setup, boundary sets, sparse couplings,
periodic wrap, normalization, locality proof and work precision remain those
of the pinned phase-cell construction. Its exact inverse is approximated,
not identified with a different matrix's exact inverse.

The result is conditional on the retained resampling and multiplication
interfaces. It gives two triangular convolutions and three diagonal factors
inside the existing similarity, in place of the GS difference of two
convolution pairs. It does not lower the dimension exponent or claim a new
kappa. The finite checker is not a proof of the all-size tape machine.

## Classical identity and specialized bounds

Let 0<q<=1/4, n>=1, G_ij=q^((i-j)^2),

    f_j=product_(k=1..j)(1-q^(2k)), f_0=1,
    g_j=q^(j^2)/f_j, h_j=(-q)^j/f_j.

Write D_f=diag(f), and T(v) for lower triangular Toeplitz multiplication.
Then

    L=D_f T(g) D_f^-1,
    G=L D_f L^T,
    T(g) T(h)=I,
    G^-1=D_f^-1 T(h)^T D_f T(h) D_f^-1.                  (1)

These are established q-calculus identities, not a novelty claim. A primary
source is Alexey Kuznetsov, *Using q-calculus to study LDLT factorization of
a certain Vandermonde matrix*, [Theorems 1 and 2](https://arxiv.org/pdf/1507.02959).
For completeness the specialization is explicit: use his Vandermonde parameter
r=q^-2 and B=diag(q^(j^2)). Then G=B V_r B and
(r;r)_j=(-1)^j q^(-j(j+1)) f_j. Substituting into his triangular factor and
conjugating it by B gives L_ij=q^((i-j)^2)f_i/(f_j f_(i-j)); the diagonal
becomes f_j. This proves the second display. The power series identities
with Q=q^2 give sum g_j z^j=(-qz;Q)_infinity and
sum h_j z^j=1/(-qz;Q)_infinity. Their coefficient product is one. Only
coefficients through n-1 are used, proving the finite triangular inverse
and hence (1), including n=1.

The elementary product bound product(1-x_k)>=1-sum x_k gives

    14/15 <= f_j <= 1,
    ||D_f^-1|| <= 15/14,
    ||T(h)||, ||T(h)^T|| <= (15/14)/(1-q) <= 10/7.       (2)

Thus all five central factors are uniformly bounded. The triangular upper
product is a reversed lower convolution and a reversed retained output.
There is no subtraction of two branches.

## Keep H and its Schur system exactly as before

Use all pinned phase-cell hypotheses: integer p>=101,
P=32768p, eta=2^-P, u>=ceil(log2(8p)), u*d<=p,
1<rho<2, theta=rho-1, w=ceil(sqrt(16p/u))+2, and cell
interior length n<=5p. The retained weights satisfy

    2^(-8p-1) <= a_hat_j <= 1.

The old interior A=D_a G_hat D_a^-1 has ||A^-1||<=8p.
G_hat has independently downward-approximated entries with absolute error
less than 4eta for distances at most w and exact zero beyond w.
The global H is NOT changed to dense Gaussian entries.

Apply the same corrected exponential oracle once to
q_*=exp(-pi*u*rho), obtaining 0<q<=q_* and q_*-q<4eta.
Positivity follows from q_*>2^(-16p) and the stated work precision.
Also q<=1/4. Define the *local model only*

    G_tilde_ij=q^((i-j)^2), A_tilde=D_a G_tilde D_a^-1.

For r<=w the power identity on [0,1] gives
|q^(r^2)-G_hat_r|<4(r^2+1)eta. Summing over a row, using n<=5p,
gives less than 2^11 p^3 eta. For r>w, pi>3 and e>2 imply
q_*^(r^2)<2^(-3u r^2); u*w^2>=16p and the geometric ratio bound give
both tails together less than 4*2^(-48p). Multiplication by the old
similarity condition bound 2^(8p+1) yields

    E=||A_tilde-A||
      < 2^(8p+12) p^3 eta + 2^(-40p+3)
      < 2^(-39p).                                    (3)

No row-dominance assertion about a newly chosen global H is needed.
Because 8p E<1/2, the resolvent identity gives

    ||A_tilde^-1|| <= 16p,
    ||A_tilde^-1-A^-1|| <=128p^2 E <=2^(-37p).         (4)

The last elementary bound uses p^2<=2^p for p>=4 and 7<=p.
This is an approximation allowance. Declaring (1) an exact inverse of
G_hat is false; a rejection test exhibits a nonzero residual.

## Rounded local execution

Precompute exact rational f,h from the dyadic q, then round f,1/f,h and
1/a_hat toward zero to the P-grid. Keep the old dyadic a_hat. For a completed
input b, evaluate in order

    a_hat^-1, 1/f, T(h), f, T(h)^T, 1/f, a_hat.

Every product is exact until one completed-coordinate rounding. Signed
convolution uses four nonnegative integer products with slots strictly
wider than n times the largest integer coefficient product; it retains
only the first n coefficients. Reversal implements the upper factor.
The executable prototype performs this packing, not a dense substitute.
The bits=None path exists only for independent exact algebra tests.

Each rounded central factor has norm below two and row perturbation at
most 5p eta. The first reciprocal step has magnitude at most
2*2^(8p+1)*B and absolute error at most 2eta B, where B=max(1,||b||).
A simple seven-step error recurrence, using a factor bound two, coefficient
row error 5p eta and one rounding unit, bounds the final rounding error by

    2^16 p 2^(8p+1) eta B < 2^(32p) p^8 eta B.

Combining with (4), a unit-input allowance for the inverse of the OLD A is

    LA_new = 2^(-37p) + 2^(32p) p^8 eta <=2^(-36p).    (5)

All internal records use O(p) integer guard bits and P fractional bits.
Each packed operand has O(np) bits. Applying the published unconditional
integer multiplier gives O(n p^(1+delta)) for every fixed delta>0.
A constant number of sequential local tapes and reversals adds O(np).
Setup denominators for the exact products f and h have polynomially many
bits in p. The old exact rational Schur construction still uses OLD A^-1,
and is performed once per axis as before. Nothing in (1) replaces that
precomputation with the model. Setup remains polynomial in s,p and subpolynomial in the overall input bit length
in the retained asymptotic setting.

## Complete unchanged Schur composition and scalar error interface

Use the original two local passes and one boundary solve:

    y_I = approx_A_inverse(b_I)
    r_B = b_B - H_BI y_I
    x_B = approx_S_inverse(r_B)
    x_I = approx_A_inverse(b_I - H_IB x_B).

Here S is exactly H_BB-H_BI H_II^-1 H_IB for the original H. Rounded
coupling maps and boundary solver are those of the pinned batched-boundary
construction. Its allowance is SB=2^200 p^40 eta. In the retained fixed-depth
error chain substitute LA_new for LA, giving unit-input error at most

    1024p^2 LA_new +512p^2 SB +2048p^4 eta.             (6)

This substitution is valid because the local error is measured against
OLD A^-1, whose norm remains at most 8p. The source's completed-map bounds
and intermediate input bounds therefore still apply. No large internal
similarity factor propagates from one complete local solve to the next.
The allowance is absolute and covers both signed real components.

For p>=101, p^2<=2^p, 10<=p and (5) bound the first term in (6) by
2^(-34p). Using 200<=2p and p^40<=2^(40p) bounds the second by
2^(44p)eta<2^(-34p); the third is also below 2^(-34p).
Consequently (6)<2^(-33p). The old H-to-N inverse perturbation is

    32p^2 [p*2^(16p+7)eta +2^(-46p)] <2^(-42p).

The total is below 2^(-32p)<2^(-p-10). Divide by the original 2^j,
j=ceil(log2(32p)), complete the result and round toward zero to the p-grid.
The original disk, scalar p^2 error and gamma=d(2u+j+1) interfaces survive.
The checker includes affine exponent certificates valid for every p>=101;
the elementary inequalities used above are stated explicitly rather than
inferred from a finite sample of p values.

## Weighted factor norms: an algebraic route past huge intermediates

There is a useful distinction between the preceding convolution evaluator
and the weighted operators themselves. Define

    W_lower=D_a T(h) D_a^-1, W_upper=D_a T(h)^T D_a^-1.

Because diagonal matrices commute, A_tilde^-1 also equals

    D_f^-1 W_upper D_f W_lower D_f^-1.                 (7)

For the exact exponential weights a, and any two coordinates in the same
phase cell separated by k>=0, the retained beta increment is theta*k.
Both endpoints lie in [-1/2,1/2). In either triangular orientation the
exponent in (a_i/a_j)*q_*^k is at most -pi*u*theta*k*(k+1): substitute
F=u*(1/4-beta^2)/theta and use the endpoint closer to the relevant cell
edge. Since q<=q_* and f_k>=14/15, each entry is bounded by

    (15/14) exp(-pi*u*theta*k*(k+1)).

The actual downward weights obey a_hat_i<=a_i and a_hat_j>=a_j/2,
so an extra factor two covers their ratios uniformly. Sum the geometric
majorant with k*(k+1)>=2k. The elementary inequality
1/(1-exp(-x))<=1+1/x for x>0 and u*theta>=1/(4p) give

    ||W_lower||, ||W_upper||
      <= (15/7)/(1-exp(-2*pi*u*theta)) <3p.             (8)

For D=Theta(p^epsilon), fixed epsilon<1, tensoring either completed
weighted stage has norm at most (3p)^D=2^o(p); five such stages still
need only O(p) magnitude bits. This is a norm statement about (7), not
an algorithm for applying W. Directly expanding W into its three factors
reintroduces the large similarity intermediate. A fast weighted tensor
convolution with a valid precision/layout proof remains to be constructed.
The checker includes rational exponential-base phase cells verifying both
weighted orientations, their coefficientwise decay and complete identity,
and multi-axis exact identities with five tensor stages.

## What this removes, and what it does not

For any number of axes, the tensor of the central five factors in (1)
reorders into five tensor-factor stages, not a sum with exponentially many
branches. This is an algebraic statement only. It removes the GS branch
expansion obstacle for that specific strategy.

Directly evaluating a tensor of the unweighted convolutions with the
combined a_hat^-1 can require O(H*u*d) guard bits for H grouped axes.
The scalar u*d<=p hypothesis does not imply H*u*d=O(p). Padding, ragged
phase-cell routing, tensor boundary corrections and an implementation that
avoids this large global similarity remain unpaid. The per-line order is
unchanged, as are the d-dependent Gaussian term and small-field exposure
row. No asymptotic kappa improvement is claimed from fewer convolutions.

The all-size argument is a conditional written proof. Finite checks cover
classical exact identities, actual signed packed local products, 115-bit
reciprocal guards, independently rounded/truncated Gaussian sources, and
complete original-Schur solves with the new rounded local operation and
the existing rounded batched boundary/coupling operations. They use modest
work precisions and do not simulate asymptotic p or a full tape machine.

## A checked failure of one joint-kernel implementation

The small weighted norm in (8) does **not** justify materializing the
unweighted tensor convolution kernel on the same P-fractional-bit grid.
Here is an explicit failure of that particular proposed implementation.
It is not a lower bound for FFTs, implicit kernels, floating-point formats
with exponents, adaptive precision, or all joint weighted algorithms.

For an integer a>=26 set

    p=2^(10a), m=2^(4a), X=2^(3a), d=u=m, D=d-1,
    P=32768p, w=4X+2, k=X/2048.

These have epsilon=r=2/5, u*d<=p, u>=ceil(log2(8p)),
(w-2)^2*u=16p and d-2>2w+k+3. Thus the retained scalar and
cell/band conditions hold eventually. The actual prime-generated axes
may be kept: their theta_i are in (1/(4d),1/(2d-1)), so u*theta_i<2.
No artificial common prime size or changed capacity hypothesis is needed.
Select a full phase cell on each axis, and its interior coordinates at
offsets w and w+k from the cell's first index. Both lie in its interior.

Let q_i be the existing downward P-grid approximation to
q_*i=exp(-pi*u*rho_i). Its exact h_(i,k)=(-q_i)^k/f_(i,k)
satisfies |h_(i,k)|<2*q_*i^k<2^(1-3mk). The tensor kernel coefficient K
for these D displacements therefore satisfies

    |K| <2^(-D(3mk-1)) <2^-P.                         (9)

Rounding K toward zero on the P-grid gives exactly zero. Reweighting this
stored zero cannot recover the corresponding weighted map entry.

To bound the true weighted entry from below, let beta_0 be the first phase
value of a full cell; -1/2<=beta_0<-1/2+theta. At j=w+k the upper product's
exponent obeys

    (rho+2beta_j)k-theta*k^2 <=theta*k*(2w+k+3).

Consequently the exact exponential weights give

    (a_w/a_(w+k))*q_*^k
      >=exp[-pi*u*theta*k*(2w+k+3)]
      >2^[-16k*(2w+k+3)].

The actual a_hat_w/a_hat_(w+k) is at least half the exact ratio.
Also q_*i>2^(-16m) implies q_i/q_*i>=1-delta with
 delta=2^(16m+2-P)<=2^(-100p). Since Dk<p, all q-rounding ratios
together are at least (1-delta)^(Dk)>1/2. Finally f_(i,k)<=1.
The magnitude of the required weighted tensor entry is thus greater than

    2^[-16Dk(2w+k+3)-D-1] >2^(-p/8) >2^-p.          (10)

A unit basis input at the selected source tensor coordinate turns this
entry into an output error. Hence the zero in (9) violates the desired
p-bit absolute accuracy. The operator itself still has the norm bound (8).

The comparisons are uniform, not extrapolated from tested sizes. With
D>=m/2 and X>=128, the exponent in (9) divided by p is at least
3*2^a/4096-1/(2X^2)>32768. The exponent in (10) divided by p is less than

    (8+1/2048+7/128)/128 +1/128^2 <1/8.

The remaining cell inequality follows from m/X=2^a; the corrected
exponential and reciprocal approximations use their original margins.
The required unweighted fractional exponent scales as m*D*k,
which is Theta(p^(11/10)) in this family. This is a representation cost
for this kernel materialization, not a bit-complexity lower bound on the
underlying weighted operator.

The verifier includes these universal rational inequalities plus symbolic
rows a=26,27,32,64. Those rows do not execute their enormous tensors.
A separate finite rational example actually checks all 4,096 entries of
a 64-by-64 three-axis operator. A 14-bit unweighted grid erases 28 entries
larger than the 8-bit target error; a 30-bit grid passes the same comparison.
This small example illustrates the mechanism and does not satisfy every
asymptotic p>=101 hypothesis. The preceding argument supplies the latter.
The existing per-axis evaluator does not materialize this joint kernel
and is not contradicted by this rejection test.

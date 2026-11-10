# Exact fixed-rank compression error of the full Gaussian inverse

This contribution was produced by Nick Petalas. Apache-2.0.

## Claim and exact predecessor premise

Fix alpha>0, put b=pi/alpha^2, and take 0<theta<1. Write
rho=1+theta, N=floor(1/theta), c=1/(2rho), and

    K_theta[k,i] = alpha^(-1) exp(-b (i-k/rho-c)^2),  0<=k,i<N.

No entry is truncated. For a bounded operator X define

    d_r(X) = inf { ||X-R||_op : rank R <= r },  r=0,1,2,... .

For every FIXED nonnegative integer r, the new conclusion is

    lim_(theta -> 0) d_r(K_theta^(-1)) / ||K_theta^(-1)||_op
      = 1 / sqrt(2 floor(r/2)+1).                         (1)

In particular, a rank-one approximation has asymptotically the same
operator-norm error as the zero approximation. Rank two first lowers the
relative limiting error to 1/sqrt(3). This statement allows arbitrary
linear approximants, including those mixing the two ends of the cell.
It is an analytic optimum, not a method for preparing or applying modes.

The cited premise is JoyboyBrian's [PR5183](https://github.com/CrocSwap/integer-mult-bounds/pull/5183),
retained at base 7c49fe32c55de02c2c873655c804b16e4c3fef0a in
[PROOF.md](../gaussian-half-line-operator-limit/PROOF.md). Its theorem gives
an isometric embedding U_theta into H=L2(0,infinity) direct-sum L2(0,infinity)
and the checkerboard sign matrix S=diag((-1)^i) such that

    X_theta = U_theta [sqrt(theta) S K_theta^(-1) S] U_theta*
    ||X_theta - a (T_b direct-sum T_b)||_op -> 0,
    a = alpha exp(b/4) / P(b)^3,
    P(b) = product_(j>=1) (1-exp(-2bj)),
    (T_b f)(x) = integral_(x to infinity) exp(-b(y^2-x^2)) f(y) dy. (2)

We use (2) as a credited mathematical premise. We do not re-prove or
replay the source finite Gaussian matrices, source exponents, q-LDU sum,
embedding estimates or boundary-layer convergence. The new argument
calculates every singular value of T_b and transfers the resulting
approximation law through (2). No uniform growing-alpha result is used.

## Complete half-line singular system

Let H_n be the physicists' Hermite polynomial. Define the normalized
full-line Hermite functions, scaled to b, by

    phi_n(x) = (2b)^(1/4) H_n(sqrt(2b)x) exp(-bx^2)
               / [pi^(1/4) sqrt(2^n n!)].

Their orthonormality, completeness and parity are classical; see
[NIST DLMF 1.18.42-43](https://dlmf.nist.gov/1.18#E42).
Let psi_n be sqrt(2) times the restriction of phi_n to x>0.
Each of the two sequences

    e_k = psi_(2k),    o_k = psi_(2k+1),    k>=0,

is an orthonormal basis of the SAME half-line Hilbert space. To see
completeness, extend a half-line function evenly or oddly to the full
line, use the full-line basis, and restrict back. The two sequences are
not asserted to be mutually orthogonal to each other.

The classical weighted derivative identity is

    d/dz [exp(-z^2) H_n(z)] = -exp(-z^2) H_(n+1)(z).

See [NIST DLMF 18.9.26](https://dlmf.nist.gov/18.9#E26).
The polynomial times Gaussian vanishes at infinity. With z=sqrt(2b)y,
integrating this identity gives

    T_b [H_(2k+1)(sqrt(2b)y) exp(-by^2)](x)
       = H_(2k)(sqrt(2b)x) exp(-bx^2) / sqrt(2b).

Taking account of the different normalization constants yields

    T_b o_k = s_k e_k,
    s_k = 1 / [2 sqrt(b(2k+1))].                          (3)

There is no extra boundary condition imposed on either input or output.
The integral itself determines (3).

For completeness T_b is bounded independently of the spectral conclusion.
For 0<=x<=y one has y^2-x^2 >= (y-x)^2. Both integrals of its nonnegative
kernel, in either variable with the other fixed, are at most
integral_0^infinity exp(-bt^2)dt=sqrt(pi)/(2sqrt(b)). The Schur test
therefore bounds its operator norm. Equality (3) on the input basis
extends by continuity to every L2 input. Since the output sequence is
also a basis, this is a complete singular-value expansion. Its adjoint
maps e_k to s_k o_k. Truncating after m terms has norm error s_m -> 0,
so T_b is compact. Its singular values, indexed from zero, are exactly
the strictly decreasing numbers s_k in (3).

The Hermite facts and diagonal-operator argument are classical. The new
source-specific consequence is the full spectrum and fixed-rank law for
(2), rather than another estimate of its top norm.

## Optimal rank error and doubled modes

Put B=a(T_b direct-sum T_b). Each s_k occurs twice in the singular
spectrum of B, multiplied by a. Thus

    d_r(B) = a / [2 sqrt(b(2 floor(r/2)+1))].              (4)

Here is a direct minimax proof, including arbitrary approximants. The
upper bound retains the r largest singular modes. For the lower bound,
restrict any rank-at-most-r operator R to the span of the first r+1
right singular vectors. Rank-nullity supplies a nonzero vector v in
that span with Rv=0. Orthogonality of their images implies
||Bv|| >= sigma_(r+1)(B)||v||, with singular values now indexed from one.
Consequently ||B-R|| >= sigma_(r+1)(B), which is (4). A rank mixing the
two edges cannot escape this argument.

For any bounded X,Y on the same spaces,

    |d_r(X)-d_r(Y)| <= ||X-Y||.                           (5)

Indeed, for every rank-at-most-r R, the triangle inequality gives
||X-R|| <= ||X-Y||+||Y-R||; take infima and exchange X,Y.
Applying (5) to (2) and (4) gives the absolute limit

    sqrt(theta) d_r(K_theta^(-1))
       -> a / [2 sqrt(b(2 floor(r/2)+1))].                (6)

An isometric embedding followed by zero on its orthogonal complement
does not change nonzero singular values or rank approximation errors.
One may also prove this directly: embed a finite approximant for the
upper bound and compress any Hilbert-space approximant by U_theta*
and U_theta for the lower bound. Compression does not increase rank
or norm. Multiplication by S on either side preserves both. These facts
justify the left side of (6) without changing the permitted approximants.
For r=0, (6) has the positive limit a/(2sqrt(b)). Dividing proves (1).

Equivalently, for every fixed j>=1,

    sqrt(theta) sigma_j(K_theta^(-1))
       -> a / [2 sqrt(b(2 floor((j-1)/2)+1))].            (7)

The order of limits is fixed j or r first, then theta tending to zero.

## Exact compression threshold in the limiting operator

For 0<epsilon<=1, the least rank attaining relative error at most epsilon
for B itself is

    r_min(epsilon) = 2 ceil((epsilon^(-2)-1)/2).         (8)

This follows by solving (4), since the first rank in every equal-error
pair is even. For epsilon=1/2 the least rank is four; for epsilon=1/10
it is 100. Formula (8) concerns the limiting operator. At an exact equality
threshold it does not establish the eventual least rank of every finite
K_theta. Likewise, (1) alone does not apply to an unbounded r(theta).

## Evidence, credit and limits

The bounded verifier proves polynomial identities and exact Gaussian
integrals on finite Hermite spans and checks the doubled spectral and
threshold arithmetic. These calculations corroborate (3)-(8); they do
not prove infinite-dimensional completeness or the source limit by
sampling. The universal claim rests on the written argument and the
explicit classical and predecessor premises.

Credit JoyboyBrian / PR5183 for (2), including its full coefficient and
endpoint embedding, and its predecessors Jose Manuel / PR4193, Vlado
Vojdanovski / PR1673, Ryanson Jonathan / PR4435, Nick Petalas / PR5150,
Cinna Davis and the retained Gaussian lineage. Their files are unchanged.
No global literature priority is claimed for Hermite singular systems,
minimax approximation or the inequalities used here.

This exact-real theorem supplies no rounded prefix analysis, mode
preparation or application algorithm, bit/tape/storage/movement tariff,
native/compiler/stock admission, exact integer recovery, new kappa or
complete multiplication theorem. The selected frontier and its five
framework assumptions are unchanged. Independent human and formal
proof-kernel review are unclaimed.

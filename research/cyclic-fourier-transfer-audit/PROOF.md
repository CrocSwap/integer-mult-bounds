# A sharper Fourier transfer for the cyclic inverse bound

## Result and scope

This note audits the Fourier-to-matrix-norm step in the prime-power
cyclic-inverse contribution attributed to PR #621. It takes that
contribution's uniform circle lower bound as an input. It does not replace
its algebraic nonvanishing or resultant argument.

Let P be a complex polynomial and suppose that, for every |z|=1,

    |P(z)| >= delta > 0,       |P'(z)| <= M,       M >= 0.

Let Z_L be a cyclic permutation matrix of any integer size L>=1, let w
be any integer, and let tau be any complex number with |tau|=1. Put
U=tau Z_L^w. Then

    ||P(U)^-1||_infinity^2 <= delta^-2 + 2 pi M delta^-3
                           <= delta^-2 + (44/7) M delta^-3.       (1)

Here the induced infinity norm is the maximum absolute row sum. The
estimate is uniform in L, w, and tau; in particular, tau need not be a
root of unity and w need not be relatively prime to L.

The underlying periodic Sobolev estimate is classical in nature. No
priority claim is made for a new general inequality or an optimal
constant. The local contribution is the sharper explicit transfer and
its application to the inherited bound. It supplies no new integer
kappa, complex b, BIT c, paid algorithm, or rounded-program guarantee.

## A periodic Fourier estimate

For a continuously differentiable 2 pi-periodic complex function g,
define

    c_k = (1/(2 pi)) integral_0^(2 pi) g(t) exp(-ikt) dt,
    A^2 = (1/(2 pi)) integral_0^(2 pi) |g(t)|^2 dt,
    B^2 = (1/(2 pi)) integral_0^(2 pi) |g'(t)|^2 dt.

We claim

    (sum_(k in Z) |c_k|)^2 <= A^2 + 2 pi A B.                    (2)

The proof establishes absolute summability, rather than assuming it.
For an integer N>=0, form the finite trigonometric polynomial

    F_N(t) = sum_(|k|<=N) |c_k| exp(ikt),
    A_N^2 = sum_(|k|<=N) |c_k|^2,
    B_N^2 = sum_(|k|<=N) k^2 |c_k|^2.

The coefficients |c_k| need not be symmetric in k. The triangle
inequality nonetheless gives

    max_t |F_N(t)| = F_N(0) = sum_(|k|<=N) |c_k|.

Put h_N(t)=|F_N(t)|^2. For every continuously differentiable real
periodic function, the integral of the absolute derivative is at least
twice the difference between its maximum and minimum. Indeed, each of
the two arcs joining a maximum point to a minimum point contributes at
least that difference. Therefore

    2(max h_N - min h_N) <= integral_0^(2 pi) |h_N'(t)| dt
                         <= 2 integral_0^(2 pi) |F_N(t) F_N'(t)| dt
                         <= 4 pi A_N B_N.

The final step uses Cauchy-Schwarz and the finite Parseval identities.
Also min h_N is at most its average, which is A_N^2. Consequently

    (sum_(|k|<=N) |c_k|)^2 <= A_N^2 + 2 pi A_N B_N.

Parseval for g and g' gives A_N<=A and B_N<=B. The partial sums on
the left increase with N and are bounded. Taking their limit proves
(2), including the cases A=0 or B=0.

For completeness, the rational comparison used in (1) follows from

    22/7 - pi = integral_0^1 x^4 (1-x)^4 / (1+x^2) dx > 0.

The identity follows by polynomial division and the integral of
1/(1+x^2). Thus no numerical approximation of pi is needed.

## Polynomial reciprocal and matrix transfer

Set g(t)=1/P(exp(it)). The hypotheses imply that g is smooth and
periodic. Its derivative is

    g'(t) = -i exp(it) P'(exp(it)) / P(exp(it))^2.

Thus, with the normalized L2 norms above,

    A <= delta^-1,       B <= M delta^-2.

Substituting these nonnegative upper bounds into (2) proves

    (sum_k |c_k|)^2 <= delta^-2 + 2 pi M delta^-3.                (3)

Write P(z)=sum_(j=0)^d p_j z^j. Since P(exp(it))g(t)=1, its
Fourier coefficients satisfy

    sum_(j=0)^d p_j c_(m-j) = 1 if m=0, and 0 otherwise.         (4)

This indexing uses the exp(-ikt) coefficient convention stated above.
Equation (4) follows directly by integration against exp(-imt); it
does not require a prior assertion about pointwise Fourier convergence.

Every positive or negative integer power of U is a permutation matrix
multiplied by a scalar of modulus one. Hence ||U^k||_infinity=1 for
all k in Z, including L=1 and w=0. By (3), the matrix series

    G = sum_(k in Z) c_k U^k

converges absolutely in the induced infinity norm. Multiplication by
the finite polynomial P(U) and regrouping are justified by that
absolute convergence. Equation (4) gives P(U)G=I. Since these are
finite square matrices, P(U) is invertible and G=P(U)^-1. Finally,

    ||P(U)^-1||_infinity <= sum_k |c_k|,

which proves (1). This argument controls arbitrary input vectors, not
only eigenvectors or a selected scalar entry. It uses an infinite
series to prove an exact norm estimate, not as a declared algorithm.

## Comparison with the inherited transfer

The prior Fourier argument gives

    K_old = delta^-1 + 2M delta^-2.

Denote the square root of the rational right side in (1) by K_new and
write t=M/delta. Then

    K_old^2 - K_new^2 = 4 delta^-2 t (t - 4/7).                 (5)

Both bounds are nonnegative. Thus K_new is strictly smaller for
t>4/7, equal for t=0 or t=4/7, and larger for 0<t<4/7. The universal
choice min(K_old,K_new) is valid in every case. This note does not
claim that the new expression improves the old one for arbitrary
small derivative bounds.

For fixed M>0, the new expression grows as delta^-3/2 when delta
decreases to zero; the inherited expression grows as delta^-2. This
compares the two proved estimates and is not an optimality claim.

## Substitution for the prime-power kernel

Use the inherited notation for a prime power r>=3, a primitive r-th
root u, n=r-1, D=phi(r), and H=2^r-1:

    P(z) = sum_(j=0)^n z^j / product_(s=1)^j (1-u^s),
    delta_r = 1 / (2rn H^(nD-1)),
    M_r = nH/r.

The empty product for j=0 is one. PR #621's proof supplies the
uniform lower bound |P(z)|>=delta_r on the circle, for every
primitive root choice. Its coefficient bound supplies |P'(z)|<=M_r.
Only this inherited theorem is used here; no new classification of
roots or new resultant estimate is asserted.

Equation (1) now gives

    ||P(tau Z_L^w)^-1||_infinity
      <= sqrt(delta_r^-2 + (44 nH/(7r)) delta_r^-3).             (6)

In this family,

    M_r/delta_r = 2n^2 H^(nD) > 1.

Therefore (5) proves that (6) is strictly smaller than the inherited
delta_r^-1 + 2nH/(r delta_r^2) for every covered r and primitive u.
This includes dyadic r>=4. For r=2 the inherited direct geometric
series bound ||(I+U/2)^-1||_infinity<=2 remains available; no
improvement to that special bound is claimed.

The logarithm of (6) remains O(r^2 phi(r)), hence O(r^3):
log(delta_r^-1)=O(r^2 phi(r)) and log(M_r)=O(r). The improvement
changes the explicit transfer but not the established asymptotic
order of its logarithm. It does not establish an O(p polylog p)
combined precision guard.

## Products and unit diagonal conjugation

For any finite family of polynomials satisfying the general
hypotheses, on a common cyclic array put

    C = product_i P_i(tau_i Z_L^(w_i)),
    Q_i = delta_i^-2 + (44/7) M_i delta_i^-3.

Every factor is invertible, so submultiplicativity gives

    ||C^-1||_infinity <= product_i sqrt(Q_i).

One may replace any factor by the smaller of its inherited and new
bound. For the covered prime-power kernels each new factor is
strictly smaller. The logarithm is still O(sum_i r_i^2 phi(r_i)).

If D_0 is diagonal with every diagonal entry of modulus one, then
the inverse of D_0 C D_0^-1 is D_0 C^-1 D_0^-1. This conjugation
preserves every absolute matrix-entry value and hence preserves the
induced infinity norm exactly. The same product bound therefore
holds after a unit diagonal conjugation.

## Attribution and limitations

The inherited circle theorem, kernel, and old transfer are in
[the prior proof](../prime-power-cyclic-inverse/PROOF.md). Its
[source record](../prime-power-cyclic-inverse/SOURCE.json) and
[notice](../prime-power-cyclic-inverse/NOTICE.md) retain the OpenAI
exact-DFT preprint pin, classical q-calculus attribution, and credit
to the prior unpublished work directed by Ali Romman. This note
claims none of that work as new.

The proof above is self-contained conditional on the inherited circle
theorem. Finite verifier outputs can check substitutions and bound
comparisons; they cannot replace its all-length analytical proof.
Efficient coefficient preparation, paid rounded execution, precision
propagation, scratch restoration, and a fast fixed-tape circuit remain
open here. No operation count or multiplication exponent is changed.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.

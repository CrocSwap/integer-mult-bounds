# Scale-dependent seeds require the complete recurrence

This is a written proof about a positive recursive cost model. It is not a
physical supplier construction, a multiplication bound or a formal-kernel proof.
All displayed child multiplicities are charged. Glue, adapters and other work
are set to zero, a favorable relaxation of a complete implementation.

## 1. The precise source implication being tested

Philippe Van Velzen's `limits-1/single-letter` lane at commit
`ed21d6245f8ce1a62e21205be7bedc24271dd772` considers

    T(x) = sum_r (n_r/W) T(rx/m) + h(x),   T(x)=1 for 0<x<=1.

A seed has scalar root p satisfying `sum_r (n_r/W)(r/m)^p=1`, and supplier
saving a=1-p. Its Theorem 1 keeps an explicit cumulative local-oscillation
error when comparing T with `exp(integral p d log x)`. The following
unqualified Cesaro corollary/summary does not follow unless that error and the
normalized glue contribution are sublinear in log x. This audit tests that
implication, not the full error-qualified inequality or the other source lanes.

## 2. An irreducible, two-rank counterexample

Take common width m=256 and stock W=1. There are two complete profiles:

| seed | n_16 | n_1 | exact scalar root p | a=1-p |
|---|---:|---:|---:|---:|
| A | 1 | 2 | 1/4 | 3/4 |
| B | 4 | 32 | 3/4 | 1/4 |

Indeed the two terms in each seed's moment at its root are exactly 1/2.
These are positive integer multiplicities, with child ratios 1/16 and 1/256.
No claim is made that these profiles have native supplier realizations.
A further restriction on realizable profiles or admissible seed variation
could exclude this witness; it would need to be an explicit hypothesis.

For x>1 put i=ceil(log_16 x). Use A for odd i and B for even i, with h=0.
Multiplication by either child ratio subtracts one or two from i, including
at exact interval endpoints. Thus T is constant on each scale interval and
equals t_i, where t_i=1 for i<=0 and

    t_i = t_(i-1) + 2t_(i-2)       (i odd),
    t_i = 4t_(i-1) + 32t_(i-2)     (i even).

The first values are t_0=1,t_1=3,t_2=44,t_3=50,t_4=1608. Every child call
is included. The local root function alternates between 1/4 and 3/4 on
equal log-length intervals. Its log-Cesaro mean therefore tends to 1/2.

Let v_k=(t_(2k),t_(2k-1))^T, interpreting t_(-1)=1. Then

    v_k = P^k (1,1)^T,     P = [[36,8],[1,2]].

The characteristic polynomial is X^2-38X+64. Its dominant eigenvalue is
lambda=19+3 sqrt(33), with positive eigenvector w=(lambda-2,1)^T.
Since lambda-2>1,

    w/(lambda-2) <= (1,1)^T <= w.

P has nonnegative entries, so multiplication by P^k preserves the inequalities.
The first coordinate gives

    lambda^k <= t_(2k) <= (lambda-2)lambda^k.

The odd subsequence is a positive fixed linear combination of adjacent even
state coordinates and has the same exponential rate. Consequently, for all
x>=1,

    T(x) = Theta(x^p_eff),    p_eff = log(lambda)/log(256).

This is an all-scale proof, with constants independent of x. In particular,
32<lambda<37: the polynomial at 32 is -128, its larger root lies to the
right of 19, and sqrt(33)<6. Since 37^3<256^2, therefore

    5/8 < p_eff < 2/3,      1/3 < a_eff < 3/8.

The claimed log-Cesaro substitution would instead give p_eff=1/2 and a=1/2.
The discrepancy persists in the exponent. It is not a numerical rounding error,
a missing helper surcharge, a constant factor, or a reducible parity component:
both phases depend on the other phase and the two-step transfer is positive.

The counterexample also survives one unit of additive work at every internal
node. If u_i is that recurrence, induction gives
`t_i <= u_i <= (3t_i-1)/2`, because each profile has coefficient sum at
least three. Thus adding this positive toll leaves p_eff unchanged.

## 3. The phase-indexed moment gives the right equation

Write z=16^(-p), and let c_A,c_B be positive scale-phase amplitudes in the
trial function t_i=16^(pi)c_(i mod 2). Its moment equations are

    [c_A,c_B]^T = M(p)[c_A,c_B]^T,
    M(p) = [[2z^2,z],[4z,32z^2]].

Thus det(I-M)=1-38z^2+64z^4. The positive eigenvector branch at spectral
radius one is exactly 256^p=lambda, as above. At p=1/2, M has determinant
zero and trace 17/8, so its spectral radius is exactly 17/8>1. This retains both child
ranks and the phases reached by each child. Averaging scalar roots discards
that information. The equation is specific to this finite periodic model;
no unrestricted spectral transfer theorem is claimed here.

The source's retained local-oscillation error permits this counterexample:
p changes by 1/2 within the two-interval child window at every large scale,
so the worst-chain cumulative allowance is of order log x, not o(log x).
Keeping E in the formula is essential. A sufficient repair to its corollary
is to establish E=o(log x), including glue and terminal normalization, before
identifying the asymptotic exponent with the log-Cesaro mean.

## 4. A different proof preserves the finite-catalogue extremal statement

Fix a finite catalogue of positive profiles. Each profile consists of finitely
many coefficients c_(s,j)>0 and ratios 0<q_(s,j)<1, and has a scalar root
p_s>=0 with sum_j c_(s,j)q_(s,j)^p_s=1. Choose any profile independently at
each recursive node, possibly as a function of scale or prior history. Assume
the recurrence terminates at size <=1, terminal cost is 1, and h=0.
Let p_min=min p_s, p_max=max p_s and q_min=min q_(s,j).

For every profile, monotonicity in p gives

    sum_j c_(s,j) q_(s,j)^p_min >= 1,
    sum_j c_(s,j) q_(s,j)^p_max <= 1.

Every terminal descendant of a root x>=1 has size in [q_min,1], apart from
the root x=1 itself. Hence the leaf bounds are

    y^p_min <= 1 <= q_min^(-p_max)y^p_max.

Propagate these bounds upward through the finite recursion tree. Positivity
and the two moment inequalities prove, for every node-wise seed choice,

    x^p_min <= T(x) <= q_min^(-p_max)x^p_max.

The finite catalogue has q_max<1, so the tree depth is finite for every x.
This argument does not assume one common profile at each depth. Fixing a
minimizing profile gives T(x)=Theta(x^p_min) by the same proof. Thus within
this zero-glue finite-catalogue recurrence, arbitrary switching cannot improve
the exponent beyond the best fixed seed. Nonnegative extra work preserves
the lower bound; an upper bound with glue requires its own estimate.

This validates that limited no-mixture conclusion by a direct comparison;
it does not validate the unqualified Cesaro equality. Unbounded seed families,
missing uniform termination/terminal costs, paid representation changes,
scale-dependent normalization and the actual two-supplier outer transfer
need separate premises. In particular, no value here is an improved kappa.

## 5. Evidence boundary

The proof covers every scale for the two displayed profiles, and every finite
recursion tree under Section 4's hypotheses. The executable checks cover
bounded depths and explicit defect controls. The independent checker and
REVIEW.md are by a separate GPT-6.1 Sol mathematical worker, not independent
human or formal-kernel review. The actual selected source, native controller,
stock/hosting/precision and multiplication transfer are unchanged.

Credit: Philippe Van Velzen's proposed scale-dependent interface and explicit
error term; standard positive recurrence, companion-matrix and Perron-vector
arguments. Prepared by Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0.

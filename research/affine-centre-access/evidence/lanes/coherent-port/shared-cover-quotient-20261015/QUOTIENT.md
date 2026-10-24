# A common cover quotient and correlated tensor phases

This note gives an exact phase sector on which equal-rank orthogonal
owner frames agree. The sector contains correlated tensor characters.
Its relative dimension tends to a positive constant as the tensor
width increases. The note also gives the exact relative dimension at
every positive width, as a sum with at most 73 terms for the actual
73-axis ambient space.

This is not an implementation of the sector projector. It gives no
new supplier, recurrence, precision bound, or kappa improvement. A
positive spectral dimension is not a legal encoding at zero cost.

## 1. Sources and ordered routes

The checker pins `circuit-interface/INTERFACE.json`, the original
`complex-nine-native/DATA-PHASES.json` member, and the accepted
`source-domain/augmented-mode-lift/LIFT.json`. It imports no producer.
The first two sources give the actual 112 port labels and the matrix
R. The last source gives the fixed-owner mode convention.

Write S_h f(g)=f(gh), with matrix products in the displayed order.
The query and response entries use

    m_(s,p) = sigma_s rho_s(p),
    G'_s = S_sigma_s R D_s (I-Q),
    K'_s = D_s^-1 K S_sigma_s^-1.

Thus the query entry at port p contains S_m, and the response contains
S_(m^-1). The checker reconstructs all 1008 routes. It verifies their
orthogonality, their fixed unused axes, and the port-line condition
rho_s(p) q_p=q_p. It checks the port bases directly against the
original phase source.

For stages through h, every m_(s,p) is in the orthogonal subgroup on
the first n=8h+9 axes. It fixes the other axes. This gives a proper
subgroup quotient when h<8. There can be one aggregate per right
subgroup coset, rather than only one aggregate over the full cover.

The integral source construction is due to the companion note
`portable-source-codes/upstream-echo-20261015/COVER-QUOTIENT.md`.
If A is the cover sum and J is injection at one cover label, then
AJ=I and

    H(H0) = I + J(H0-I)A

has the same order as H0 and fixes ker A. Also A G'_s=R A(I-Q).
This identity leaves Q on the right. It does not commute Q with A.
Injection at one cover label does not make K'_s J independent of s.

If H contains all the required m_(s,p), its normalized right average
P_H satisfies P_H S_m=S_m P_H=P_H. This can give a common response
as well as a common query. It requires division by |H| and a physical
implementation. Neither follows from the owner lift.

The eight actual stage-one routes at ports

    11, 19, 35, 67, 131, 259, 13, 21

have an orbit containing all 65535 nonzero even vectors in 17
coordinates. The checker enumerates that orbit exactly. In particular,
their generated subgroup has order at least 65535. This is a limit on
the uniform subgroup-average construction. It is not a lower bound
for all cover-dependent maps.

The same route reconstruction independently checks all 36 distinct
stage pairs and the determinant-32 minor at port indices
0,1,2,3,4,5,6,12 used by the companion scalar-mode obstruction.
That obstruction excludes constant scalar 8-by-8 mode codes. It does
not exclude the cover quotient in this note.

## 2. Physical covariance does not remove the query routes

Let P_g act on payload addresses by |x> -> |gx>. On tensor width
lambda it acts in every tensor factor. An orthogonal owner frame has

    F_(gV) = P_g F_V P_g^-1.

The covariant aggregate A_cov f=sum_g P_g^-1 f(g) therefore satisfies

    A_cov diag_g(F_(gV)) = F_V A_cov,
    A_cov S_h = P_h A_cov,
    A_cov Q_p = C_p A_cov.                         (1)

These identities are exact, including at partial owner frames. A read
from owner gh into owner g uses the payload map P_(g h^-1 g^-1).
There is no Fourier cost for that address permutation. Its complete
stream implementation still needs a source contract.

Equation (1) changes the compressed query into

    sum_p R_(k,p) P_(sigma_s rho_s(p)) (I-C_p) A_cov x_p.

The chart action remains on the payload. A covariant aggregate alone
does not give a common query.

A cover-only average has the opposite problem. It absorbs the query
routes, but it does not commute with general partial frames. For the
first actual stage-one generator m, the rank-eight coordinate frame
has phase exponent 1 at character e_7, while its m-image has exponent
0. Both exponents are 0 at the zero character. No translation and
constant phase can remove this ratio. Also q=11 and mq=2816 have
different phase at e_0. Thus cover averaging cannot be moved through
Q without a further argument.

## 3. The correlated phase sector

For a tuple of Fourier characters chi_1,...,chi_lambda in F_2^n,
define

    f(v) = sum_j parity(chi_j . v) mod 4.

The native convention is C_v chi=i^parity(chi.v) chi. Thus C_v on
all lambda tensor factors has phase i^f(v). Every signature has the
form

    f(v) = sum_i a_i v_i + 2 sum_(i<j) b_(i,j) v_i v_j mod 4,
    a_i in Z/4, b_(i,j) in F_2.                    (2)

The signature group Gamma_n has order 2^(n(n+3)/2).

Let p(v) be the parity of the weight of v, and let omega be the
all-ones vector. Define the subgroup S_n by

    f_(d,b)(v) = d p(v) + 2(b.v)(1+p(v)) mod 4,
    d in Z/4, b in F_2^n / <omega>.                (3)

This is exactly the set of signatures that are constant on all odd
vectors. It has order 2^(n+1). To verify the statement, evaluate (2)
at the coordinate vectors and at odd triples. These evaluations force
a_i=d and b_(i,j)=d+b_i+b_j mod 2. Conversely these coefficients give
(3). Adding omega to b does not change (3), and this is the only
redundancy.

On the fixed-d part of S_n, every odd native line has phase i^d.
Every frame made from r orthogonal odd axes has phase i^(rd).
Orthogonal address maps preserve this sector and preserve d. They
can change b. Consequently equal-rank owner frames agree on this
sector, even if their axes differ.

This statement concerns complete orthogonal owner frames. It does
not declare the same sector invariant at every internal canonical
frame of an unchanged local program.

There are explicit correlated inputs outside the product sector
{0,omega}^lambda. Four equal columns have zero signature. More
generally, for any b, the five columns

    b, omega+b, omega, omega, omega

give f_(0,b). Add d copies of omega to obtain f_(d,b). At most eight
columns suffice. When b is neither 0 nor omega, this construction is
not a tensor product of the width-one survivor.

The checker gives an exact maximality result for the actual first
two stages. It closes the rank-eight, rank-nine, and rank-seventeen
frame conditions under the eight actual route generators. It uses
row reduction over Z/4, with the mixed coefficients constrained to
be even. The solution group has order 2^18 and equals S_17. Either
the rank-eight or rank-nine condition alone gives this same result.
The rank-seventeen condition alone is weaker.

If each signature itself must be fixed by every generator, only the
four signatures d p remain. This is a different condition from
invariance of the spectral sector. The 2^18 sector is stable under
the group even though its individual signatures need not be fixed.

For n=73, (3) is a sufficient sector for every orthogonal owner frame
and every odd port. This note does not prove that it is the full
survivor for the complete 73-axis actual route group.

## 4. Exact signature distribution

Choose each character column uniformly and independently in F_2^n.
This is also the normalized dimension measure on the tensor payload.
Each column contributes the signature s_x(v)=parity(x.v). The steps
s_x generate all of Gamma_n: the coordinate columns give the linear
generators, and s_(e_i+e_j)-s_(e_i)-s_(e_j) gives a mixed generator.
The zero column is a zero step with positive probability. The walk
therefore has no nontrivial periodic coset and tends to the uniform
distribution on Gamma_n.

There is an exact reduction for membership in S_n. Put m=n-1 and
restrict f to the odd affine hyperplane

    v(t) = (t_1,...,t_m,1+parity(t)),
    psi(f)(t) = f(v(t))-f(e_n).

The map psi is onto Gamma_m and has kernel S_n. For a uniform column
x=(x_1,...,x_n), let y_i=x_i+x_n and epsilon=x_n. Then

    psi(s_x)(t) = (-1)^epsilon parity(y.t).

Here y and epsilon are independent and uniform. Thus membership in
S_n is the return event for a symmetric walk on Gamma_m with steps
plus or minus s_y.

For a dual character with coefficients alpha in (Z/4)^m and beta in
F_2^(m choose 2), its eigenvalue is

    mu(alpha,beta) = 2^-m sum_y cos(pi q(y)/2),
    q(y) = alpha.y + 2 sum_(i<j) beta_(i,j) y_i y_j.       (4)

If alpha has an odd coordinate, half the summands are zero, so
|mu|<=1/2. If alpha is even, this is a binary quadratic Gauss sum.
A nonconstant linear form gives zero. A nonzero alternating polar
form has rank at least two and gives magnitude at most 1/2. Only
the trivial dual character has eigenvalue 1. This also proves direct
convergence, with no appeal to a sampled walk.

The complete eigenvalue multiplicities give a short exact formula.
Let A_d(r) be the number of alternating d-by-d binary matrices of
rank 2r. Then

    A_d(r) = product_(j=0)^(2r-1) (2^d-2^j)
             / [2^(r^2) product_(j=1)^r (2^(2j)-1)].       (5)

To count these matrices, choose their radical and a nondegenerate
alternating form on the quotient. The denominator is the number of
symplectic bases on the quotient. This gives (5), including A_d(0)=1.

For a fixed polar matrix of rank 2r, its 2^d linear terms give
normalized binary Gauss sums as follows:

    +2^-r: (2^(2r)+2^r)/2 terms;
    -2^-r: (2^(2r)-2^r)/2 terms;
    zero:  2^d-2^(2r) terms.

The first two counts sum to 2^(2r), since the form must vanish on
its radical. Their difference is 2^r, since the sum of the normalized
Gauss sums over all linear terms is 1.

For alpha even, use this spectrum in dimension m. For each nonzero
parity l=alpha mod 2, restrict q/2 to l-perpendicular. This gives
each binary quadratic form in dimension m-1 exactly 2^m times.
Its eigenvalue is one half of its normalized Gauss sum. Thus the
second spectrum has multiplicity factor c_m=(2^m-1)2^m.

Let lambda>=1, k_lambda=lambda-2+(lambda mod 2), and
I_n=2^((n-1)(n+2)/2). The exact survivor fraction is

    Pr[f in S_n] = (1/I_n) * [
        sum_(r=0)^floor(m/2) A_m(r) 2^(-r k_lambda)
        + c_m 2^-lambda
          sum_(r=0)^floor((m-1)/2) A_(m-1)(r) 2^(-r k_lambda)
    ].                                                    (6)

Equation (6) is a finite exact formula, not an asymptotic estimate.
It follows by summing mu^lambda over all dual characters. At odd
lambda the positive and negative multiplicities have difference
2^r. At even lambda they have sum 2^(2r).

Every term in (6) is nonnegative. The fraction is at least 1/I_n,
decreases to that limit, and satisfies

    0 <= I_n Pr[f in S_n]-1 <= (I_n-1) 2^-lambda.          (7)

The rank sum is much more precise than the bound in (7). Exact
rational checks give:

| n | Limit | A width after which the ratio to the limit is below 1.01 |
|---|---|---|
| 17 | 2^-152 | lambda>=40 |
| 73 | 2^-2700 | lambda>=152 |

The ratio is above 1 at every finite positive width. The checker
stores exact rational values, not only decimal estimates. It also
enumerates all dual characters through m=4 and all literal walks
through m=3, lambda=6, using a second calculation.

For a specified d, the limiting fraction is 2^-154 at n=17 and
2^-2702 at n=73. These statements follow from the uniform limit on
the full signature group. The three sectors d=1,2,3 together have
three times that fraction. On d=0 the query factor I-Q vanishes;
on d=1,2,3 it need not vanish. Thus the positive limiting fraction
is not confined to the zero-query sector.

For completeness, the full signature distribution also has the
finite Fourier formula

    Pr[f=gamma] = |Gamma_n|^-1 sum_chi
        conj(chi(gamma)) [2^-n sum_x chi(s_x)]^lambda.

The nontrivial factors have modulus at most 1/sqrt(2), by the
quadratic Gauss-sum identity. This gives uniform convergence for
each signature and each fixed-d coset. Equation (6) is the more
efficient formula for the owner-frame survivor.

## 5. The common-quotient consequence and its limits

Let Pi_d project onto the sector (3) with fixed d. It commutes with
orthogonal address maps. On its range Q_p=i^d for every odd port,
and each rank-r owner frame is i^(rd). Therefore a pure cover
average is compatible with equal-rank owner frames on this range.
This removes the phase counterexample in Section 2 on a nonzero
correlated sector. For a proper prefix subgroup, use the same sector
in a fixed basis of each coset's prefix space; this basis choice is
not a free layout conversion.

If P_H contains all required route multipliers, let E=P_H Pi_d and
use the same E in each mode coordinate. For any invertible scalar
mode matrix H0,

    H = I + (H0-I)E,
    H^-1 = I + (H0^-1-I)E.

The operator H preserves every arbitrary input. It fixes the kernel
of E and has the order of H0 on the range of E. Both query and
response actions are common across the selected charts, since
P_H absorbs m and m^-1 and Q is scalar on Pi_d. No Q is moved
through K or R outside this sector.

This is an exact construction family with an explicit nonzero
volume fraction. Its mode range is reduced further by the factor
1/|H| from the cover average. No useful recurrence gain follows from
positivity alone.

The spectral projector is not emitted. A direct Fourier expansion
can write it as a sum of translations, but that sum can have a
number of terms exponential in lambda. It gives no acceptable
operation count. A CSS or Bell encoding is a separate construction
and must retain arbitrary inputs and price its entry and exit.

The accepted owner lift admits complete-cover sweeps with fixed
right multipliers and pointwise ADDs between distinct families.
It does not by itself admit masked ADDs between two cover labels of
one family. Even the finite mean-and-difference implementation of
a coset average needs a separate packed-stream lowering and cost.
The rational coefficient 1/|H| also needs a proved finite-grid bound.

The remaining work is therefore an access and cost question. This
note does not replace that question with a product-subspace rate
bound, and it does not treat a spectral projector as a native child.

## 6. Reproduction and review scope

Run from the repository root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/coherent-port/shared-cover-quotient-20261015/check_quotient.py
```

Expected output:

```text
PASS: 1008 routes; exact 17-dimensional phase sector; exact correlated-width distribution
```

The receipt pins this proof, its checker, and the source inputs. The
checks cover the route order, the exact finite module calculation,
the correlated controls, and the distribution arithmetic. They do
not replay a new native program or give an independent proof review.
All work remains local. No publication is authorized.

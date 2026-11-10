# Euclidean resolvent growth under a column cap

Fix an integer m>=2 and real 0<rho<1. Let F(n) be the supremum of
||(I-E)^-1||_2 over complex n by n matrices satisfying

    ||E||_infinity <= rho,       ||E||_1 <= m rho.

Put a=rho sqrt(m). Constants below may depend on the fixed m and rho.
Then, as n tends to infinity,

    a<1:  F(n) tends to 1/(1-a);
    a=1:  F(n) = Theta(log n);
    a>1:  F(n) = Theta(n^(log_m a)).

These are growth orders, not exact finite-dimensional maxima. In particular,
the critical boundary for this norm is rho=1/sqrt(m), rather than the
rho=1/m boundary of the induced 1-norm problem in PR6788.

## Upper bound for all complex matrices

The row contraction gives a convergent Neumann series for the inverse.
For k>=0, submultiplicativity gives

    ||E^k||_infinity <= rho^k,
    ||E^k||_1 <= (m rho)^k.

Every entry of E^k has modulus at most rho^k, so also
||E^k||_1 <= n rho^k. Therefore

    ||E^k||_2 <= rho^k min(m^(k/2),sqrt(n)).                 (1)

Let K be the least nonnegative integer with m^K>=n. Splitting the series
before k=K gives the finite bound

    F(n) <= sum_(k=0)^(K-1) a^k + sqrt(n) rho^K/(1-rho)
         <= sum_(k=0)^(K-1) a^k + a^K/(1-rho).            (2)

For a<1 one can instead sum a^k forever to obtain 1/(1-a).
For a=1, (2) is K+1/(1-rho). For a>1 it is at most
`a^K [1/(a-1)+1/(1-rho)]`. Since K<log_m(n)+1, this is
O(n^(log_m a)). These arguments do not require nonnegative entries,
normality, diagonal permission or a prescribed support.

## Matching lower bounds with zero diagonal

Take the rooted complete m-ary tree with levels 0 through h. It has
n_h=(m^(h+1)-1)/(m-1) vertices. Define E[v,parent(v)]=rho for every
nonroot vertex and all other entries zero. Its row sums are at most rho,
its column sums at most m rho, its diagonal is zero, and it is nilpotent.
Thus the same growth lower bounds already hold in this smaller class.

Let v_l be the normalized indicator of level l. These vectors are
orthonormal because their supports are disjoint, and

    E v_l = a v_(l+1) for l<h,        E v_h=0.

The radial subspace is invariant under E and its inverse. In this basis
the restricted inverse is J_a=(I-aS)^-1, with S the forward shift on
H=h+1 coordinates and (J_a)[i,j]=a^(i-j) for i>=j.

If a<1, apply J_a to the all-one vector divided by sqrt(H). The squared
output norm is

    (1/H) sum_(i=1)^H [(1-a^i)/(1-a)]^2,

which tends to 1/(1-a)^2 by convergence of the scalar sequence and its
Cesaro means. Combined with the upper bound this proves the exact limiting
constant. If a=1, the same vector gives the exact squared ratio

    (H+1)(2H+1)/6,

hence a lower bound of order h. A single inverse column would give only
sqrt(H); coherent input on all levels is essential at the boundary.
If a>1, the input v_0 gives squared output norm sum_(i=0)^h a^(2i),
which is at least a^(2h).

For arbitrary sufficiently large n choose the largest tree with n_h<=n
and append a zero block. The norm does not decrease. Since n<n_(h+1),
m^h>((m-1)n+1)/m^2, so the supercritical lower bound is a constant
times n^(log_m a). Also h=Theta(log n), which gives the critical bound.
For subcritical limits h tends to infinity with n. This proves all claims.

## Relation to the caller and evidence boundary

The precision/analytic-recovery framework needs induced Euclidean inverse
bounds. The original row-gap/bandwidth note and PR5255 show concentration
can matter. PR6788 and PR6806 add column caps and optimize the induced
1-norm. This proof determines what those caps alone imply in the 2-norm.
For example m=4,rho=1/2 has a uniform row gap 1/2 and column cap 2,
yet its inverse 2-norm is unbounded, growing logarithmically with dimension.
It does not have fixed bandwidth in tree order. The result therefore does
not refute the bandwidth-based bound, two-sided Gaussian contraction,
or any selected source-specific conditioning claim.

No emitted Gaussian matrix has been bound to these caps. Fractional m,
exact finite-dimensional optima, preparation costs and full physical
supplier/outer admission remain outside the result. All five selected
framework assumptions remain. The universal result rests on the written
argument; exact finite computations corroborate it.

The methods are classical Neumann-series norm interpolation and the
radial subspace of a regular tree. General literature priority is unclaimed.
Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.

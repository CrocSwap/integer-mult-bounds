# The exact binary dual-polar cut ratio at every rank

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and scope

Let X be the Lagrangian subspaces of a nondegenerate alternating space of
dimension 2m over F2, where m is any positive integer. Put
d(L,M)=m-dim(L intersection M). Let A_i be the zero-one distance-i matrix,
k_i its row sum and T_i=A_i/k_i. A distance-i pair means a uniformly
chosen ordered pair at that distance. For S contained in X, define

    p_i(S) = Pr[exactly one endpoint of a distance-i pair belongs to S].

For every nonempty proper S,

    p_m(S) / p_1(S) <= K_m = 2 - 2^(1-m).                 (1)

Point cuts S_v={L : v belongs to L}, for v nonzero, attain equality. Thus
K_m is the exact Boolean-cut optimum for every m. The unique nonconstant
adjacency eigenspace maximizing the spectral quotient is the first one.
This does not classify all attaining Boolean sets.

Theorem 6 of Jacob Sussman's PR #4628, in
`author-evidence/induction-across-block-sizes.md`, explicitly leaves the
all-rank spectral comparison open after finite computations through rank 12.
The new step here is its universal proof. The graph, spectral-comparison
method, point-cut witness and coordinate-family interpretation are credited
predecessor context. No predecessor scientific executable is replayed.

This limits a stated certificate family. It is neither a word lower bound
of K_m calls per array nor an obstruction to every kept-subspace certificate.
It supplies no physical program, new kappa or supplier admission.

## 1. Intersection numbers

Every neighbor of L is obtained by choosing a hyperplane H of L and one of
the two other Lagrangians over H in the symplectic plane H-perp/H. Hence
k_1=2(2^m-1). Fix another vertex Z and put R=L intersection Z, of dimension
m-i. There are 2^i-1 hyperplanes H of L containing R. Over each such H,
one alternative gains one dimension of intersection with Z and the other
keeps the intersection dimension. Indeed the pairing from Z to H has rank
i-1, so Z intersection H-perp has dimension m-i+1 and determines exactly
one alternative line over H.

There are 2^m-2^i hyperplanes not containing R. The pairing from Z to H
then has rank i. Thus Z intersection H-perp=R, and either alternative
intersects Z in H intersection R, losing one dimension. Consequently

    c_i = 2^i-1,   a_i = 2^i-1,
    b_i = 2^(i+1)(2^(m-i)-1).                            (2)

Here c_i,a_i,b_i count neighbors at distances i-1,i,i+1 from Z. The graph
is connected since c_i>0 whenever i>0. Transverse Lagrangians exist, so
its diameter is m. Double counting edges between distance spheres gives
k_i c_i=k_(i-1)b_(i-1), and in particular

    k_m = 2^(m(m+1)/2).                                 (3)

The distance matrices satisfy

    A_1 A_i = b_(i-1) A_(i-1) + a_i A_i + c_(i+1) A_(i+1), (4)

with terms outside 0..m omitted. Since c_i>0 for 1<=i<=m, each A_i is
a degree-i polynomial in A_1. These m+1 matrices are linearly independent
because their supports are disjoint. At i=m, (4) gives a degree-(m+1)
polynomial annihilating A_1. Its minimal polynomial therefore has degree
m+1. Since A_1 is real symmetric, it has exactly m+1 distinct eigenvalues.

## 2. Factored distance eigenvalues

For 0<=j<=m define

    theta_j = 2^(m-j+1)-2^j-1,
    F_j(z) = product_(r=1..m-j)(1+2^r z)
             product_(r=0..j-1)(1-2^r z).

Write P_i(j) for the coefficient of z^i in F_j. Empty products are one.
The telescoping products give the polynomial identity

    (1-z)(1+2z) F_j(2z)
      = (1+2^(m-j+1)z)(1-2^j z) F_j(z).                (5)

This is a polynomial identity, with no division by a possibly zero factor.
Comparing coefficients and using (2) yields

    theta_j P_i(j)
      = b_(i-1)P_(i-1)(j) + a_i P_i(j)
        + c_(i+1)P_(i+1)(j),                           (6)

again omitting outside terms. This includes the terminal equation i=m.
The initial value P_0(j)=1 and (4) uniquely determine every distance
eigenvalue from an adjacency eigenvalue. Equation (6) says each theta_j
is a root of the degree-(m+1) annihilating polynomial just constructed.
They are strictly decreasing, so they give its complete list of roots.
On the theta_j eigenspace, A_i has eigenvalue P_i(j).

The leading coefficient of F_j and (3) give

    u_1(j) = theta_j / [2(2^m-1)],
    u_m(j) = (-1)^j 2^(-j(m-j+1)),                     (7)

the eigenvalues of T_1 and T_m. Indeed the leading-coefficient exponent
is `(m-j)(m-j+1)/2 + j(j-1)/2`; subtracting `m(m+1)/2`
gives `-j(m-j+1)`.

The distance-regular graph spectrum is classical. Lee and Tanaka,
[SIGMA 14 (2018), 009, section 3](https://doi.org/10.3842/SIGMA.2018.009),
record the general intersection numbers and adjacency eigenvalues. The
binary factor/recurrence argument above makes the proof self-contained;
it does not extrapolate a finite table.

## 3. Uniform maximization

For j>=1, u_1(j)<1. The proposed bound satisfies

    K_m (1-u_1(j))
      = 2 - 2^(1-j) + (2^j-1)2^(-m).                  (8)

At j=1, both (8) and 1-u_m(j) equal 1+2^(-m), so the quotient is K_m.
If j>=2, then m>=2 and

    j(m-j+1)-m = (j-1)(m-j) >= 0.

Thus `1-u_m(j) <= 1+2^(-m) <= 5/4`, whereas (8) is strictly greater
than 3/2. The quotient is strictly less than K_m in every remaining
nonconstant sector. For m=1 there is only j=1. We have proved

    max_(1<=j<=m) (1-u_m(j))/(1-u_1(j)) = K_m.          (9)

This argument holds for every positive m, independently of the checker's
finite rank limits.

## 4. Boolean cuts and sharpness

Use the uniform inner product on functions on X. Decompose f=1_S into
mutually orthogonal adjacency eigenspaces, f=sum_j f_j. Symmetry and
regularity give

    p_i(S) = 2 <f,(I-T_i)f>
           = 2 sum_(j>=1)(1-u_i(j)) ||f_j||^2.

Apply (9) term by term. Connectedness gives p_1(S)>0 for every nontrivial
S, proving (1). A directed-exit convention multiplies both probabilities
by the same constant, leaving the ratio unchanged.

The credited point-cut witness works at every rank. Each Lagrangian
contains 2^m-1 nonzero points, and the symplectic group is transitive on
the 2^(2m)-1 nonzero points. Thus the fraction containing a fixed point is
alpha=1/(2^m+1). Two transverse Lagrangians cannot both contain that point,
so p_m(S_v)=2alpha. From a Lagrangian containing v, exactly 2^(m-1)
hyperplanes omit v, and both alternatives over each such hyperplane omit
v. The conditional edge-exit probability is 2^m/[2(2^m-1)]. Edge reversal
therefore gives

    p_1(S_v) = 2alpha * 2^(m-1)/(2^m-1).

The ratio is `(2^m-1)/2^(m-1)=K_m`, proving sharpness. At m=1, distance
one and distance m coincide, as the formula requires.

## 5. Certificate consequence and limits

A coordinate family assigns Y_L=span{e_x : x belongs to S(L)} in one
fixed finite coordinate basis, with constant dimension. Its directed
defect `dim(Y_L)-dim(Y_L intersection Y_M)` is a sum of Boolean-cut
exits over coordinates. Averaging over each distance relation turns this
into a sum of half the disagreement probabilities above. Consequently
the opposite-to-edge average-defect ratio is at most K_m whenever the
denominator is positive. Nonnegative sums obey the same ceiling. The
coordinates indexed by nonzero points, with membership v in L, give a
constant-dimension family attaining it.

This is PR4628's coordinate-family application with the missing all-rank
premise supplied. It does not bound arbitrary noncoordinate subspaces,
temporal cuts, changed free-letter models or general physical circuits.
Supplier realization, ownership/restoration, compiler, precision/tape and
analytic recovery remain separate. No predecessor scientific replay,
selected cold replay, Lean build or Docker run is claimed.

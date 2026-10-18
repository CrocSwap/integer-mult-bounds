# Uniform bounds for the prime-power cyclic inverse

## Result and scope

Let r=ell^a>=3, where ell is prime and a>=1. Let u be a primitive
r-th root of unity, and put n=r-1 and D=phi(r). Define

    h_j = 1 / product_(s=1)^j (1-u^s),
    P(z) = sum_(j=0)^n h_j z^j,
    f(z) = r P(z).

For every such r and u, P has no zero on the complex unit circle.
Put H=2^r-1 and delta_r=1/(2rn H^(nD-1)). For every complex
z with |z|=1,

    |P(z)| >= delta_r.

This bound does not depend on the order of z. In particular, it holds
at all eigenvalues of a cyclic shift of any length. The old bound from
the algebraic norm of P at a root of unity depends on that root's order.
The new bound removes that dependence.

There is also an operator bound that does not require root
classification. For any complex scalar tau with |tau|=1,
any cyclic shift Z_L with L>=1, and any integer w, put U=tau Z_L^w. Then

    ||P(U)^-1||_infinity <= delta_r^-1 + 2nH/(r delta_r^2).

The bound has logarithm O(r^2 phi(r)), hence O(r^3). It is uniform
in L, w, and tau. The induced infinity norm is the maximum absolute
row sum. This bound does not supply a complete O(p polylog p) guard
for growing radix families. Efficient coefficient preparation, rounded
execution, scratch restoration, and a fast fixed-tape circuit remain open. No integer
kappa, complex b, or BIT c changes in this result.

For an odd prime q, D=n=q-1, so the circle bound becomes

    delta_q = 1/(2q(q-1) (2^q-1)^((q-1)^2-1)).

The result includes dyadic r>=4. For r=2, P(z)=1+z/2; the geometric
series gives ||P(U)^-1||_infinity<=2. No result for other composite
radices is claimed. The ideal argument below requires a prime power.

## Integral polynomial and unit roots

The identity product_(s=1)^(r-1)(1-u^s)=r gives

    f(z) = sum_(j=0)^n a_j z^j,
    a_j = product_(s=j+1)^n (1-u^s).

All a_j are algebraic integers in K=Q(u), and a_n=1. Thus f is
monic. Every root of f is an algebraic integer.

Take any root alpha and a number field E that contains K and alpha.
The algebraic integer 1-u is not a unit in E, since

    |Norm_(E/Q)(1-u)| = ell^[E:K] > 1.

Here Norm_(K/Q)(1-u)=Phi_r(1)=ell. The prime-power cyclotomic
polynomial is Phi_r(x)=sum_(j=0)^(ell-1) x^(j r/ell).

There is a maximal ideal m in the ring of integers of E that contains
1-u. Modulo m, all a_j with j<n vanish. Hence f(alpha)=0 gives
alpha^n=0 in the residue field. The residue of alpha is zero, so
alpha is not a unit in the ring of integers of E.

If |alpha|=1, then alpha^-1 is the complex conjugate of alpha. The
complex conjugate of an algebraic integer is an algebraic integer.
Consequently alpha and alpha^-1 would both be algebraic integers,
which would make alpha a unit. This is a contradiction. Therefore
f, and thus P, has no zero on the unit circle.

This proof also shows that f cannot vanish at any algebraic unit.
It permits roots inside the unit disk.

## A quantitative lower bound on the circle

Define the conjugate reciprocal polynomial

    f*(z) = z^n conjugate(f(1/conjugate(z)))
          = sum_(j=0)^n conjugate(a_(n-j)) z^j.

Let S be the 2n by 2n coefficient matrix whose columns are

    f, z f, ..., z^(n-1) f, f*, z f*, ..., z^(n-1) f*.

Rows use powers 0 through 2n-1. Its determinant R is an algebraic
integer in K. Modulo a maximal ideal that contains 1-u, f reduces
to z^n and f* reduces to 1. The matrix S reduces to the block permutation
matrix with off-diagonal identity blocks. Its determinant is
(-1)^(n^2), which is nonzero in the residue field. Thus R is nonzero
modulo that ideal, and R is nonzero in K.

Under every complex embedding sigma of K,

    sum_j |sigma(a_j)| <= sum_(k=0)^n 2^k = H.

The same bound holds for f*. Each column of sigma(S) has Euclidean
norm at most H. Hadamard's inequality gives

    |sigma(R)| <= H^(2n).

The field K has degree D. The nonzero integer Norm_(K/Q)(R) has
absolute value at least one. Its embeddings occur in conjugate
pairs. The chosen embedding and its conjugate both have modulus
|R|. Since r>=3, the two embeddings are distinct. Bound the other
D-2 factors by H^(2n). This gives

    1 <= |Norm_(K/Q)(R)| <= |R|^2 H^(2n(D-2)),
    |R| >= H^(-n(D-2)).

The equation S adj(S) e_0 = R e_0 gives polynomials A and C of
degree below n with

    A(z) f(z) + C(z) f*(z) = R.

Each coefficient of A and C is a cofactor of S. A cofactor is a
determinant of size 2n-1. Deleting a row and a column cannot
increase the Euclidean norm of any retained column. Therefore each
cofactor has modulus at most H^(2n-1). For |z|=1,

    |A(z)| + |C(z)| <= 2n H^(2n-1),
    |f*(z)| = |f(z)|.

The Bezout identity gives

    |f(z)| >= H^(-n(D-2)) / (2n H^(2n-1))
            = 1 / (2n H^(nD-1)).

Divide by r to obtain the stated bound for P. Neither this proof
nor its constants use the degree of a root of unity at which P is
evaluated.

## An inverse bound from Fourier coefficients

Let g(t)=1/P(exp(it)). The circle bound gives |g(t)|<=delta_r^-1.
The coefficient bound gives

    |P'(exp(it))| <= nH/r,
    |g'(t)| <= nH/(r delta_r^2).

Let c_k be the Fourier coefficients of g, with the average integral
on [0,2 pi] as the normalization. Parseval's identity for g' gives

    sum_k k^2 |c_k|^2 <= (nH/(r delta_r^2))^2.

The estimate sum_(k!=0) k^-2 <= 4 follows from comparison of the
positive tail with the integral of x^-2 on [1,infinity). By the
Cauchy-Schwarz inequality and |c_0|<=delta_r^-1,

    sum_k |c_k| <= delta_r^-1 + 2nH/(r delta_r^2).

Thus the Fourier series is absolutely convergent. Its product with
the finite polynomial P(exp(it)) has Fourier coefficients equal to
those of the constant one. For U=tau Z_L^w, every integer power U^k
has infinity norm one. The absolutely convergent matrix series

    sum_(k in Z) c_k U^k

therefore has norm at most sum_k |c_k|. Multiplication by P(U) gives
the identity matrix, by the same coefficient identities. This proves
the stated inverse bound for all L, w, and unit tau.

This is a bound for the exact operator. It is not a paid
coefficient-preparation or rounded-program theorem. The infinite
series is used to prove the norm bound, not as a declared algorithm.

## Products and unit gauges

For a finite family of such kernels with r_i>=3 on the same cyclic array, put

    C = product_i P_i(tau_i Z_L^(w_i)).

Each factor is invertible. Submultiplicativity gives

    ||C^-1||_infinity <= product_i [delta_i^-1 + 2n_i H_i/(r_i delta_i^2)].

A diagonal conjugation with entries of modulus one preserves this
norm. Thus this bound also applies to a unit-gauged product. Its
logarithm is O(sum_i r_i^2 phi(r_i)). The bound concerns arbitrary
input vectors. It does not give operation counts or a tape schedule.

## Value, sources, and remaining work

This result permits inner roots and proves a uniform circle bound for
every primitive root choice. It supplies an explicit all-length inverse
bound for each growing prime-power radix. For an odd prime q and a root of unity xi, a direct algebraic norm
argument in E=Q(u,xi) gives

    |P_q(xi)| >= q^-1 (2^q-1)^(-([E:Q]-1)).

The degree of E can grow with the order of xi. The new bound uses
Q(u) only and controls every point on the unit circle. The logarithm
of its inverse upper bound still grows polynomially with r. It does
not establish the required combined precision guard or change the
full-array traffic of the literal filter chain. A sharper lower bound
and a paid implementation remain useful next questions.

The polynomial is from the pinned OpenAI exact-DFT preprint:

https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/local.tex

The unit-ideal argument extends the prior unpublished local note
"Cyclic polynomial stability, norm growth, and rescaling". The prior
local note "Full-output cyclic quotient: exact structure and cost"
supplies the cyclic inverse context. The field arithmetic in the
finite verifier uses the prior local exact-arithmetic scaffold.
The resultant and cofactor estimates use standard algebraic and
linear-algebra facts. Repository and literature novelty checks are
separate from this proof. No priority claim is made here.

Prepared with OpenAI Codex assistance. Apache-2.0.

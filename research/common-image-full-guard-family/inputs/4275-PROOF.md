# Several corank-one requests with orthogonal kernels

## Contract and claim type

This is a scoped counting proof. Let K be a finite field of order q, let
2 <= k <= m, and let U_1, ..., U_k be rank-one idempotents on K^m with
U_s U_t = 0 for s != t. Put P_t = I - U_t. A header G in GL_m(K) passes a
request R when every leading principal minor of G R G^-1 of orders 1
through rank(R) is nonzero. We count headers passing all k requests, with
each complete header weighted equally.

For k = 2 this is the overlapping corank-one pair of #4261. For k >= 3 the
requests are pairwise commuting, pairwise overlapping when m > 2, and
neither nested nor orthogonal, so the laminar law of #4259 and the
orthogonal law of #4246 do not apply.

## Theorem 1: transfer law over every finite field

For a k by k matrix A over K, define

```text
w(A) = 2q^k - 1  if A = 0,
       q - 1     if rank(A) = 1,
       0         if rank(A) >= 2.

S_k = {A : A_tt != 1 for every t}.
f_0 = indicator of the zero matrix.
f_(j+1)(B) = sum_(A in S_k) f_j(A) w(B - A),  B in S_k.
C(q,m,k) = sum_(A in S_k) f_(m-1)(A) w(I_k - A).
D(q,m,k) = q^(k(m-k)) prod_(i=0)^(k-1) (q^m - q^i).
```

**Theorem 1.** The joint passing fraction is C(q,m,k)/D(q,m,k), and the
number of passing headers is C(q,m,k)|GL_(m-k)(K)|. The state space S_k has
q^(k(k-1))(q-1)^k elements.

**Proof.** This is #4261's argument with a k by k partial Gram matrix.
Orthogonality gives K^m = im(U_1) + ... + im(U_k) + (intersection of the
kernels), so after a fixed basis change, which permutes the header domain,
U_t = e_t e_t^T. Let X = (u_1, ..., u_k) be the first k columns of G and Y
the first k rows of G^-1, with rows a_1, ..., a_k. Then YX = I_k and the
conjugated requests are I - u_t a_t. Every pair with YX = I_k arises, with
exactly |GL_(m-k)(K)| completions (an ordered basis of ker Y). There are
prod_(i<k)(q^m - q^i) choices of X and q^(m-k) choices for each row of Y,
so D(q,m,k) pairs with equal fibers.

By the rank-one determinant identity of #4227,
det((I - u_t a_t)[1..j,1..j]) = 1 - sum_(i<=j) a_(t,i) u_(t,i). Let x_i be
row i of X and y_i column i of Y, and put A_j = sum_(i<=j) y_i x_i. The
t-th guard of order j is (A_j)_tt != 1. Each request has rank m - 1, so
the conditions are exactly A_j in S_k for 1 <= j <= m - 1, and A_m = YX = I_k.
For a fixed k by k matrix A, the number of ordered (y, x) in K^k x K^k with
y x^T = A is w(A): for A = 0, x = 0 or y = 0; for rank one, the factorization
is unique up to a nonzero scalar. The coordinates of distinct rows are
independent before summation, so the walk counts each admissible pair X, Y
once. QED.

## Theorem 2: binary character law for every k

Over F_2 every safe state has zero diagonal, so S_k is the group of
zero-diagonal binary matrices, of order 2^(k(k-1)). A rank-one step y x^T
stays in S_k exactly when y and x have disjoint supports S and T; it is
then the rectangle 1_S 1_T^T with weight one, or zero with weight
2^(k+1) - 1. The last step I_k - A_(m-1) has unit diagonal and must have
rank one, so y = x = (1, ..., 1), the step is J (all ones) with weight one,
and A_(m-1) = J - I_k.

For a zero-diagonal binary matrix c, define

```text
Z(c) = sum over sigma in {0,1,2}^k of (-1)^(sum of c_ij, sigma_i = 1, sigma_j = 2).
```

**Theorem 2.** With n = m - 1,

```text
C(2,m,k) = 2^(-k(k-1)) sum_c (-1)^(|c|) Z(c)^n.
```

**Proof.** C(2,m,k) counts length-n walks in S_k from 0 to J - I_k. The
character of S_k indexed by c has eigenvalue
sum over disjoint (S, T) of (-1)^(c(S,T)) on the step distribution, where
the pairs with S or T empty supply the zero step's 2^(k+1) - 1. Encoding
(S, T) by sigma (1 on S, 2 on T, 0 elsewhere) gives Z(c). The character
takes value (-1)^(|c|) at J - I_k. Fourier inversion gives the formula. QED.

**Corollary (k = 3).** Collecting the 64 characters by eigenvalue,

```text
C(2,m,3) = (27^n - 6*21^n + 6*19^n - 6*17^n + 16*15^n - 18*13^n
            + 9*11^n - 2*9^n) / 64,

Pr(P_1, P_2, P_3 all pass) = C(2,m,3)
    / ((2^m - 1)(2^m - 2)(2^m - 4) 2^(3m - 9)).
```

The fractions at m = 4, 5, 6, 7 are 1/1680, 39/69440, 97/249984 and
26155/112881664. At m = 4 there are 12 passing headers out of 20,160; the
product of the three marginals is (9/40)^3, about 19 times larger. The
verifier checks the closed form against the transfer for m <= 30.

## Theorem 3: binary threshold

**Theorem 3.** Over F_2, for every k >= 2, a header passing all k requests
exists if and only if m >= k + 1.

**Proof.** Existence: the k rectangles {t} x ([k] \ {t}) sum to J - I_k.
For m - 1 >= k, take them in any order followed by m - 1 - k zero steps;
every intermediate state has zero diagonal. Then append J.

Necessity: suppose J - I_k = sum_(r=1)^n y_r x_r^T with supp(y_r) and
supp(x_r) disjoint, so x_r^T y_r = 0 for every r. Write it as Y'X' with Y'
of size k by n. If k is even, (J - I_k)^2 = kJ - 2J + I_k = I_k over F_2, so J - I_k is
invertible and n >= k. If k is
odd, E = J - I_k satisfies E^2 = E, has rank k - 1 and kernel spanned by
the all-ones vector. If n <= k - 1 then n = k - 1, Y' is injective and X'
is surjective, and Y'X'Y'X' = Y'X' gives X'Y' = I_(k-1). Its diagonal
entries are x_r^T y_r = 0, a contradiction. Hence n >= k in both cases,
that is m >= k + 1. QED.

At m = k + 1 every step is a rectangle. The replay finds exactly 2 k!
ordered decompositions for k = 3, 4 (the row and column decompositions in
every order), and 2 for k = 2. This count is a finite observation for
k <= 4, not a theorem.

Over F_3 the threshold is different: the replay finds 480 passing headers
at m = k = 3, so the binary threshold is not field-independent.

## Theorem 4: strict negative correlation for k = 3 over F_2

**Theorem 4.** For every m >= 2, Pr(all three pass) < s_m^3, where
s_m = 3^(m-1)/((2^m - 1)2^(m-1)) is the single corank-one fraction of #4227.

**Proof.** For m <= 3 the joint count is zero. For m >= 4 the ratio is

```text
rho_m = (N_n / 27^n) * (2^m - 1)^2 / ((2^m - 2)(2^m - 4)),
```

where N_n is the numerator in the corollary. Put x = (7/9)^n. Then
N_n/27^n <= 1 - 6x + 57(19/27)^n, since the remaining bases are at most 19
and their signed multiplicities have absolute sum 57. For n >= 42,
57(19/27)^n <= x because 57(19/21)^42 < 1.
With X = 2^m, (X - 1)^2/((X - 2)(X - 4)) = 1 + (4X - 7)/((X - 2)(X - 4))
<= 1 + 8/X for X >= 16, and 8/2^m = 4/2^n <= x for n >= 4. Hence
rho_m <= (1 - 5x)(1 + x) < 1 for n >= 42. The verifier checks rho_m < 1
exactly for 4 <= m <= 400. QED.

Since |Z(c)| <= 3^k - 2 for every c != 0 (sigma = 0 gives +1, and a sigma
with a single 1 and a single 2 on an entry of c gives -1), the joint fraction has the same
leading term 3^(kn) 2^(k - 2km) as the product of marginals for every k,
so the ratio tends to one. The sign of the approach is proved here only for
k <= 3.

## Scope

The transfer theorem covers every finite field; the replay implements the
prime fields F_2 (k <= 4) and F_3 (k <= 3). Theorems 2-4 are binary. The
proofs are written mathematics without a proof-kernel check. The algebraic
count supplies no request producer, header selection or emission,
dispatch, dirty return, stock or physical cost; neither a supplier nor a
complete multiplication theorem follows.

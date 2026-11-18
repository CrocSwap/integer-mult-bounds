# All middle factors after an idempotent first factor

No new kappa. This is a classification over F2 of one ordered polynomial
matrix identity. It supplies no native factor, paid-word saving, or supplier.

Let V have dimension n, let A be an idempotent of rank r, and put
U = im(A), W = ker(A), and m = n-r. Thus V = U direct-sum W. The question is
which endomorphisms B satisfy the following identity, with x an indeterminate:

```text
C = I + A + B,
(I + xA)(I + xB)(I + xC) = I + xI.                    (1)
```

The coefficient criterion `BC=0` is prior work: see the
[proof of PR #7223](https://github.com/unpaidmoon/integer-mult-bounds/blob/7a17378d02117c956ca76b8106f35b15aa34c0dc/research/nonidempotent-middle-factor-1100/PROOF.md).
Its named rank-one case, count 296, and three families are also prior work.
The new result here is a kernel parameterization at every rank and dimension,
with exact counts and rank distributions. In particular, higher rank permits
both B and C to be non-idempotent.

## 1. Complete parameterization

Choose subspaces K1 in U and K0 in W, of dimensions u and v. Put
K = K1 direct-sum K0. For each such pair, fix complements Q1 and Q0 once:

```text
U = K1 direct-sum Q1,    W = K0 direct-sum Q0.
```

Choose an injective linear map f1 from Q1 to K and any linear map f0 from
Q0 to K. Define B on the four summands by

```text
B(k)  = 0             for k in K,
B(q1) = f1(q1)        for q1 in Q1,
B(q0) = q0 + f0(q0)   for q0 in Q0.                  (2)
```

**Theorem.** With these fixed complements, (2) is a bijection onto all
solutions of (1). Its kernel is exactly K and its rank is `n-u-v`.
This includes r=0 and r=n.

**Necessity.** The ordered coefficient expansion gives linear coefficient
`A+B+C=I`, quadratic coefficient `BC`, and cubic coefficient `A(BC)`.
Here `A^2=A` is used in the quadratic reduction. Thus (1) holds if and only
if `BC=0`, or, equivalently, `B^2+B=BA`.

Let K=ker(B). For k in K, the last equation gives `BAk=0`. Hence K is
A-invariant. Since A is a projection, every k in K splits as Ak and
`k+Ak`, both in K, with the first in U and the second in W. Therefore
K splits uniquely as K1 direct-sum K0. Also `BC=0` says that
`v+Av+Bv` is in K for every v. On Q1 this says Bq1 is in K; on Q0 it says
`Bq0+q0` is in K. These are precisely f1 and f0 in (2). If f1(q1)=0,
then q1 is in K and in its chosen complement, so q1=0. Thus f1 is injective.
The fixed complements and B determine both maps uniquely.

**Sufficiency.** The map in (2) has kernel K. In fact, the Q0 component
of `B(k+q1+q0)` is q0, so a zero output forces q0=0. Injectivity of f1
then forces q1=0. To check `BC=0`, it is enough to check each summand.
For k in K, both k and Ak lie in K, so BCk=0. For q1 in Q1,
`Cq1=f1(q1)` lies in K. For q0 in Q0, `Cq0=f0(q0)` lies in K.
Thus BC=0 on V. Distinct K, f1, or f0 give distinct B by necessity.
The kernel dimension is u+v, which proves the rank formula.

Changing the chosen complements changes the coordinates of the maps,
not the set of solutions or the count. This is a parameterization of
matrices with a fixed A. It is not a classification of pairs up to similarity.

## 2. Exact count and rank distribution

Write `[a b]_2` for the number of b-dimensional subspaces of F2^a. It is
zero outside `0<=b<=a`. For admissible u and v define

```text
T(n,r;u,v) = [r u]_2 [n-r v]_2
             2^((u+v)(n-r-v))
             product(i=0,...,r-u-1) (2^(u+v) - 2^i).
N(n,r) = sum(u=0,...,r) sum(v=0,...,n-r) T(n,r;u,v).   (3)
```

An empty product is 1. If `r-u>u+v`, the product has a zero factor and
there is no injective f1. The two Gaussian coefficients count K1 and K0.
There are `2^((u+v)(n-r-v))` maps f0. Choose the images of an ordered
basis of Q1 successively to count the injective maps f1: the next image
must avoid the span of the images already chosen. This gives the product
in (3). The bijection proves that no matrix is counted twice.

The number of solutions of rank s is the sum of T over `u+v=n-s`.
All these counts depend only on n and r, not on the entries of A. Indeed,
a basis of U followed by a basis of W puts A in the form `diag(I_r,0)`;
conjugation transports (1), kernels, and ranks bijectively.

## 3. Which remaining factors are idempotent?

On a solution, direct expansion gives

```text
B^2+B = BA,    C^2+C = AB.                           (4)
```

Thus B is idempotent if and only if U lies in K, which is `u=r`.
Its exact count is

```text
J(n,r) = sum(v=0,...,m) [m v]_2 2^((r+v)(m-v)).      (5)
```

The number with C idempotent is also J(n,r). To prove this without a
symmetry assumption on A, transpose and exchange B and C. The map
`(A,B,C) -> (A^T,C^T,B^T)` preserves `BC=0`, the forced sum, and the rank
of A. Apply the rank-only count from Section 2 to A^T. This is a bijection,
and exchanges idempotence of B with idempotence of the new C.

Both are idempotent if and only if `AB=BA=0`. Such B is zero on U and
is an arbitrary idempotent on W. This restriction and extension bijection
was used in [PR #7040](https://github.com/unpaidmoon/integer-mult-bounds/blob/2bac9bfafe5fa009bce2141c07b703c977b18456/research/rank1-idempotent-triple-1100/PROOF.md).
An idempotent on W is specified by its image and a complementary kernel.
A fixed j-dimensional image has `2^(j(m-j))` complements. Hence

```text
D(m) = sum(j=0,...,m) [m j]_2 2^(j(m-j)),
both idempotent:       D(m),
only B idempotent:     J(n,r)-D(m),
only C idempotent:     J(n,r)-D(m),
neither idempotent:    N(n,r)-2J(n,r)+D(m).            (6)
```

For r=1, either u=1, so B is idempotent, or u=0. In the second case K
lies in W, and (2) shows that the image of B lies in W. Then AB=0 and
C is idempotent. This proves the rank-one exclusion in every dimension;
the named dimension-four exclusion is already in PR #7223.

At rank two the exclusion fails. In row-mask notation take

```text
A=(1,2,0,0),    B=(2,0,0,0),    C=(2,0,4,8).
```

Here A is idempotent, B is nonzero with B^2=0, and C is not idempotent.
The sum is I and BC=0, so (1) holds. It is one of 114 such solutions
among the 188 total solutions for n=4, r=2. For n=4 the totals at
r=0,1,2,3,4 are respectively `802,296,188,184,316`.
The counts with neither factor idempotent are `0,0,114,168,315`.

These factors belong to the enlarged matrix alphabet of this problem.
They are not asserted to be admissible paid rank-one calls.

## 4. Finite corroboration and its limits

The proof above covers every finite dimension. The verifier supplies
separate finite evidence, with no random sampling or early stop:

1. For `1<=n<=4` and every `0<=r<=n`, construct every parameter tuple in
   (2), with a deterministic complement for each K. Check its exact kernel,
   absence of duplicates, every stratum count, and the rank distribution.
2. For each of these 14 canonical first factors, enumerate every matrix B
   and multiply the three polynomial matrices entry by entry. This oracle
   does not use BC to compute the product. Its accepted set must equal the
   constructed set. Separately check BC and both equations in (4).
3. Conjugate the n=4, r=1 construction by the involution with row masks
   `(1,3,4,8)`. This sends `diag(1,0,0,0)` to the named first factor
   `(1,1,0,0)` of PR #7223. Scan all 65,536 matrices for that A as well.
   Its count, rank distribution and accepted-list SHA256 agree with that
   predecessor. These are overlap controls, not new rank-one counts.

The total is 395,316 raw matrix cases. All receipts are in
[RESULT.json](RESULT.json). The parameter enumeration uses subspaces and
maps; the raw oracle uses all matrix bit patterns and polynomial products.
These are two different enumeration paths. They do not constitute an
independent human or formal-kernel review.

The rank-two witness is checked directly. A changed C and a non-idempotent
A are rejected by the raw oracle. The latter has BC=0, so it checks the
essential first-factor hypothesis. An impossible injection stratum has
zero count, and the zero matrix at A=I is assigned its full kernel, not an
incorrect smaller one. Formula nonnegativity and the rank-one exclusion
are also checked for n through 12; these arithmetic checks are not censuses.

The order, characteristic two, and idempotence of A are essential to the
stated reduction. Other fields and other orders are outside this package.
No physical embedding, native instruction, whole caller, signed paid
invoice, or change to the selected multiplier follows. All five selected
framework assumptions remain. No predecessor full replay, selected cold
replay, Lean, Docker, independent human review, or proof-kernel check was run.

## Credit

The coefficient criterion and named 296-matrix classification are due to
unpaidmoon in PR #7223, with substantial Cursor Grok assistance as stated
there. PR #7040 supplies the orthogonal and one-sided idempotent counts.
The sources retain the earlier PR #7027, Ali Romman's PR #5747 paired-star
coordinates, and PR #6956 obstruction credit. See [CREDITS.md](CREDITS.md)
for exact links and scope. No predecessor code is copied. Standard linear
algebra supplies the Gaussian subspace and complement counts.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

# Five calls with any finite number of restored dirty roles

This proof was produced by Nick Petalas. It extends Wentao Li's #4083 beyond
one dirty role. The endpoint, alphabet and direct word come from Cinna Davis's
#2010. The first-order argument builds on Sagar Thakrar's #4032 twisted
radical-rank method. The proof below supplies the new all-role lower bound.

## Statement and conventions

Let G = SL2(F3), with matrix multiplication as its group law, and set

```
i = [[0,1],[-1,0]],    w = [[0,-1],[1,-1]],    c = w^-1 i w.
```

For every integer r >= 3, work in M_r(F2[G]). A paid factor is

```
D_N(g) = I + ([g]+[1])N,
g in {i,i^-1,w,w^-1},    N = x y^t,    x,y in F2^r,    y^t x = 1.
```

The target is T = diag([i],[w],[c],1,...,1). All r roles have arbitrary
initial values; the last r-3 roles must be restored. Arbitrary free constant
GL_r(F2) mixing is allowed. Products are written as algebraic matrix products.

**Theorem.** Every word realizing T contains at least two i/i^-1 factors and
at least three w/w^-1 factors. The exact minimum is five for every finite r.

The field of role coefficients is F2. Enlarging it is a change of model.
Formal group-algebra equality, including all dirty roles, is required.

## 1. A first-order representation of the semidirect product

Let P = {+/-1,+/-i,+/-c,+/-ic}. Direct multiplication of the displayed
matrices gives the quaternion relations i^2 = c^2 = -1 and ci = -ic.
The matrix w has order three, and conjugation by w^-1 cycles the three
nonzero classes i,c,ic of P/{+/-1}. Thus P is normal, P intersect <w> = {1},
and G = <w>P has a unique expression w^a p, a in {0,1,2}, p in P.
Indeed these expressions give 24 distinct determinant-one matrices, which
exhaust G since its first column has 8 choices and its second then has 3.

Write K = F4 = F2[omega], omega^2+omega+1 = 0. Define the additive map

```
mu(+/-1)=0,    mu(+/-i)=1,    mu(+/-c)=omega,    mu(+/-ic)=omega^2.
```

It is the identification of the binary vector space P/{+/-1} with K.
The conjugation cycle gives mu(w^-1 p w) = mu(p) omega. For g = w^a p put

```
psi(g) = omega^a,    delta(g) = mu(p).
```

For g=w^a p and h=w^b q, gh=w^(a+b)(w^-b p w^b)q. Hence

```
psi(gh) = psi(g)psi(h),
delta(gh) = delta(h) + delta(g)psi(h).
```

Extend psi and delta linearly to F2[G], and let aug be augmentation into F2.
Linearity gives, for all group-algebra elements A,B,

```
delta(AB) = aug(A)delta(B) + delta(A)psi(B).
```

Apply these maps entrywise to matrices. The same identity holds with matrix
products on the right. This is a first-order representation, equivalently
the upper-right block of the homomorphism
g -> [[1,delta(g)],[0,psi(g)]]. It does not assume that delta is multiplicative.

## 2. Two quaternion calls are necessary

Every paid factor has augmentation I. For W=F_1...F_L, repeated use of the
matrix identity gives

```
delta(W) = sum_k delta(F_k) psi(F_(k+1)...F_L).
```

For F_k=D_N(g), delta(F_k)=delta(g)N. In our alphabet,
delta(i)=delta(i^-1)=1 and delta(w)=delta(w^-1)=0. Each nonzero summand has
K-rank at most one, because N has rank one. Thus

```
rank_K delta(W) <= number of i/i^-1 calls.
```

But delta(T)=diag(1,0,omega,0,...,0) has rank two. This proves the first floor
for every r. This step is the semidirect-product extension of the predecessor's
first-order rank argument needed here. No census is involved.

## 3. At most two order-three calls are rigid

Put E=diag(0,1,0,...,0). The character image of the target is

```
psi(T) = I + omega^2 E.
```

Quaternion calls map to I. A w call maps to I+omega^2 N; a w^-1 call maps
to I+omega N. By the matrix determinant lemma their determinants are omega
and omega^-1, respectively. The target determinant is omega.

If there are no w/w^-1 calls, the determinant is wrong. If there is one,
it must be a w call, and equality of its character image with psi(T) forces
its projector to be E.

If there are two, the determinant forces both labels to be w^-1. Write
their binary projectors N,M in product order. Their character product is

```
(I+omega N)(I+omega M)
 = I + NM + omega(N+M+NM),
```

whereas the target is I+E+omega E. Comparing coefficients in the binary basis
{1,omega} gives NM=E and N+M+NM=E. Therefore N=M; idempotence then gives
N=M=E. This argument uses binary role coefficients and holds for every r.

It follows that if there are at most two order-three calls, every character
suffix psi(F_(k+1)...F_L) is diagonal and fixes every column other than
column 2. Quaternion factors have identity character, and the only remaining
projector is E.

## 4. The conjugated output forbids those rigid cases

Use the sum in Section 2. Each quaternion contribution is N times a character
suffix. Since N is binary and that suffix fixes every column other than
column 2, every entry of delta(W) outside column 2 lies in F2. The other
paid calls contribute zero.

The target has delta(T)_(3,3)=omega, which is not in F2. Column 3 is different
from column 2. This contradicts W=T. Therefore there are at least three
w/w^-1 calls. Combined with Section 2, the length is at least five.

## 5. Attainment and free mixing

The inherited direct word applies i on role 1, w on role 2, and the algebraic
product w^-1 i w on role 3. These are five paid calls with coordinate
projectors. They have the required endpoint and act identically on every
other role, independently of its initial value. Thus the lower bound is sharp.

To include interleaved constant GL_r(F2) maps, move them to one end using

```
A^-1 D_N(g) A = D_(A^-1 N A)(g).
```

Conjugation preserves binary rank-one idempotents. The resulting expression
is H times a pure paid word of the same length, with H in GL_r(F2).
Augmentation of every paid factor and of T is I, so H=I. The preceding
argument therefore covers arbitrary such free mixing and every finite amount
of restored dirty workspace.

## Scope and decision

This is a scoped proof in the formal alphabet of #2010/#4083. It closes the
two-or-more-dirty-role question in #4083 without enumerating a larger alphabet.
Searching additional restored dirty roles cannot improve this endpoint's
five-call bill under these hypotheses. The original three-role and one-dirty-role
results retain predecessor credit; their enumerations are not replayed here.

Clean-only inputs, partially restored roles, enlarged coefficient fields,
different paid address operations and other targets are outside this theorem.
The first-order map also kills the nontrivial central element -1, so it supplies
no positive lower bound for a pure central defect. No native implementation,
physical cost, admitted supplier, multiplication theorem or new kappa follows.
The written proof is the all-r evidence. The verifier only corroborates finite
instances and exposes boundary failures. Independent human and formal
proof-kernel review are unclaimed.

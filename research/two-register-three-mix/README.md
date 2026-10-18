# Two registers with at most three scalar mixing blocks

We prove a cost-preserving reduction for two-register words over any group
algebra K[G]. A word with at most three nonmonomial scalar GL2(K) blocks and
a group-diagonal endpoint reduces to two unary routes. Thus its paid bill is
at least the sum of the two target costs for any subadditive unary cost.

For the m=3 complex full-register target in eumemic's [PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
each unary target has Fourier rank three. A five-rank-one-call solution must
therefore contain at least four nonmonomial scalar mixing blocks, including
any terminal scalar cleanup. We allow arbitrary noncommuting free unary maps
between those blocks. We do not settle the five-call problem.

This is a scoped proof with author-checked exact controls. We have no new
supplier or exponent saving. We started this package from canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` and read priority revision 4.
We retain this completed lemma from a broader noncommuting search; subsequent
constructive work should address a concrete interface or a four-block endpoint.

## Model and theorem

Fix a field K and a group G. Write [g] for its formal group basis element.
Allow scalar matrices in GL2(K) and unary layers diag([a],[b]). Compress
consecutive scalar blocks and consecutive unary layers. A scalar monomial
matrix has one nonzero entry in each row and column; absorb its scales into
neighboring scalar blocks and route its permutation through unary layers.
Count the remaining nonmonomial scalar blocks.

Require the full endpoint diag([t0],[t1]), up to a scalar monomial matrix.
The two input registers are arbitrary and independent. The model has no
additional registers, discarded outputs or zero-only input restriction.
Count a nonmonomial terminal change of basis if the implementation needs one.
An arbitrary scalar-mixed endpoint is a different contract.

**Theorem.** With at most three counted scalar blocks, we can reduce the word
to two unary routes without increasing their total unary cost. More precisely,
if rho(1)=0, rho(g)>=0 and rho(gh)<=rho(g)+rho(h), the original sum of unary
costs is at least rho(t0)+rho(t1). Free unary maps must have rho=0; charge each
paid map at least its rho value.

## Proof

We first prove the middle-layer lemma. Let

```
D1 = diag([a],[b]), D2 = diag([c],[d]), M = [[p,q],[r,s]] in GL2(K).
```

Suppose D2 M D1 is scalar-equivalent to a group diagonal: it equals
L diag([u],[v]) R for L,R in GL2(K). If u!=v, its two group-coefficient
matrices have rank one. If u=v, it has one group-coefficient matrix of rank
two. Multiplication by L and R preserves each coefficient's rank.

Assume a!=b and c!=d. In

```
D2 M D1 = [[p[ca],q[cb]],[r[da],s[db]]],
```

two entries in the same row or column cannot share a group label: cancel c
or d on the left, or a or b on the right. Each label class is therefore a
partial matching. A class with two nonzero entries has rank two, including
an antidiagonal class in characteristic two.

If M is nonmonomial and invertible, at least three entries are nonzero.
At most two label classes would force one class to contain two entries.
This contradicts the rank-one requirement for distinct u,v. A single label
cannot occupy three entries in a partial matching either. We conclude

```
M is monomial, or a=b, or c=d.                         (1)
```

Now write a three-block word in matrix-product order as

```
D3 M3 D2 M2 D1 M1 D0 = diag([t0],[t1]).
```

Peel off the outside unary layers and scalar blocks. The middle D2 M2 D1
is scalar-equivalent to a group diagonal, so (1) applies. If M2 is monomial,
route its permutation through D1 and merge the neighboring unary layers.
If D1 is common, it commutes with M1; move it through M1 and merge M2 M1.
If D2 is common, move it through M3 and merge M3 M2. Each operation removes
one counted scalar block. Common layers retain both unary lanes and their
costs. Merging unary products can only decrease the sum of rho by
subadditivity; permutations only exchange the lanes.

For two blocks, peel the outside unary layers to obtain
M2 diag([a],[b]) M1 = diag([u],[v]). If a=b, move the common layer through a
scalar block and merge the two blocks. If a!=b, the two coefficient matrices
are nonzero rank-one matrices. They must occupy the two different diagonal
positions of the endpoint. Thus M2's columns and M1's rows each have singleton
support, so both scalar matrices are monomial. For one scalar block, a zero
off-diagonal endpoint forces that block to be monomial. We have reduced to
two routed unary products, proving the theorem.

We used group cancellation and coefficient ranks. We did not assume a
commutative group, unitary scalar mixers or bounded coefficients.

## Clifford specialization and tensor interpretation

For projective Clifford maps, let rho(g) be the binary rank of the off-diagonal
symplectic block that measures Fourier rank. In a product its block has the
form A_g B_h+B_g D_h, so rho(gh)<=rho(g)+rho(h). The free monomial Clifford
maps have rho=0; a rank-r paid move has rho=r; a full m-coordinate Fourier
target has rho=m. The theorem gives a bill of at least 2m. At m=3, five
rank-one calls cannot meet the endpoint with at most three mixing blocks.

The formal statement does not assume that the one-column matrices are
linearly independent. We can also justify the relevant tensor interpretation.
With three scalar blocks, a fixed matrix entry has at most four path
operators; after subtracting its target, there are at most five distinct
projective operators. Distinct projective matrices are nonproportional.

For nonproportional vectors v1,...,vk, choose for each i and j!=i a linear
functional lij that kills vj but not vi. The product of those k-1 functionals,
with extra factors nonzero on vi if needed, separates vi^tensor(lambda) from
the other tensors whenever lambda>=k-1. Apply these functionals to any
linear relation to prove independence. Here k<=5, so lambda>=4 suffices.
For the exact Clifford convention with central phases in {1,-1,i,-i}, taking
lambda divisible by four removes those phases. Thus an exact full endpoint
at such a tensor power implies the formal coefficient equations used above.
This does not justify arbitrary per-column free maps or other phase quotients.

## Boundary and exact verification

Four mixing blocks admit loops outside the reduction. For g^2=1, set

```
H = [[1,1],[1,-1]], D = diag(1,[g]).
(H D)^4 = 4[g] I.
```

Over characteristic zero, use H/4 for one of the four scalar blocks to reach
[g]I. Each block is nonmonomial and each D is noncommon. This loop costs four
uses of g for two target uses; it gives no saving. It prevents extending the
three-block reduction without another argument.

Run the standard-library checks:

```sh
python3 -I -O -B research/two-register-three-mix/verify.py
python3.12 scripts/research_package.py --package research/two-register-three-mix
```

The checker exhausts the middle-layer necessary condition over S3 and F2/F3/F5,
including triangular mixers and characteristic-independent partial matchings.
It also checks exact noncommuting reductions, the four-block boundary loop,
and the tensor-separation threshold on five invertible matrices. These are
controls for the written proof, not a finite census substituted for it.

## Open next questions

- A five-call, two-register m=3 supplier must use at least four genuine mixing
  blocks. Start with one exact four-block endpoint and count its unary calls;
  discard a candidate unless it closes on both arbitrary input registers.
  The theorem gives no solution or lower bound for that residual domain.
- A weaker endpoint with extra registers or discarded state needs its own
  cost argument. Specify the full input/output contract before reusing the
  coefficient-rank step. The two-register proof does not cover that interface.

## Sources and credit

eumemic's PR288 supplies the full-register question, target convention and
earlier window constraints. We inspected its exact head
`475a088b5862f75f0b10596cfd6842d19531a5ec`.
littleBro's [PR680](https://github.com/CrocSwap/integer-mult-bounds/pull/680),
head `c3a5b6b7afec35d259c29bc2d8bb8516e975ad31`, already uses coefficient-rank
preservation and partial-matching classes in its fixed W=3 corpus. We use
that method in an all-group W=2 classification and cost-preserving reduction.
PR705 and Jeremy Diviney's PR800 extend the neighboring fixed W=3 corpus;
Jeremy Diviney's PR836 treats a separate signed-transport/unitary setting.
We do not claim those coefficient-rank tools as new.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance in the
proof, exact controls and prose. We have no independent human review.
Apache-2.0; we imported no predecessor code and changed no frozen evidence.

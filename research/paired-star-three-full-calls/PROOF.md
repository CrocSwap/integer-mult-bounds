# Three or more full calls miss the three-leaf paired star

No new kappa. At block size 2 and three leaves, over F_2, a paired-star word
whose full calls are nonzero projectors commuting with the stage operator
cannot meet the pure endpoint once any stage uses three or more of them.
Exactly two constant thin maps of total rank 6 or 7 are included: a thin map
does not change the pure determinant, so no such rank is available either.
The selected frontier stays 781451/250000000.

This is a determinant identity in F_2[x_0, x_1, x_2]. It is not a sample of
call orders, not a GF(256) screen, and not a rerun of the two-call rank census.

## 1. Hypotheses

Keep the paired-star pure target from
`research/coupled31-chronology/PROOF.md`. The space is a core plus g=3 leaves,
each of dimension d=2, over F_2. A full call in stage j is supported on the
core plus leaf j. On that four-dimensional block it commutes with

```text
T = [[I, I], [I, I]],
```

and it is a projector. Its pure factor is I + x_j P, with x_j = D_j + 1 an
indeterminate. A thin call is I + e Z with e^2 = 0 and Z constant; its pure
factor is I. The pure target is

```text
product_j (I + x_j E_j),
```

where E_j is the identity on the core plus leaf j. List order may interleave
stages. The pure part of a product is the product of the pure parts, because
the coefficient of e^0 in R[e]/(e^2) multiplies.

The predecessor census used exactly two orthogonal full calls in each stage.
The hypothesis changed here is the call count: a stage may contain three or
more nonzero projectors of this same shape. Pairwise orthogonality is not
assumed. Entries outside F_2, a different support, and a non-projector factor
are outside the argument.

## 2. The commutant and its determinant

Write a block matrix as [[W, X], [Y, Z]] with 2-by-2 blocks. Commutation with
T forces Y = X and Z = W, so the matrix is [[W, X], [X, W]]. Set A = W + X
and B = X. Then

```text
P = [[A + B, B], [B, A + B]].
```

Let S = [[I, 0], [I, I]]. Then S^2 = I, det S = 1, and

```text
S P S = [[A, B], [0, A]].
```

P is idempotent exactly when A is idempotent and A B + B A = B. If A = 0, that
forces B = 0, so every nonzero projector has rank(A) in {1, 2}. The only
rank-2 idempotent is A = I, which forces B = 0 and P = E, the identity of the
block.

Conjugation preserves the determinant, and I + x S P S is block triangular, so

```text
det(I + x P) = det(I + x A)^2.
```

For a 2-by-2 matrix, det(I + x A) = 1 + x tr(A) + x^2 det(A). A rank-1
idempotent has characteristic polynomial t^2 + t, hence trace 1 and determinant
0, and det(I + x A) = 1 + x. A direct expansion gives the same value. Therefore
a rank-1 call has

```text
det(I + x P) = (1 + x)^2.
```

The unsplit call P = E has det(I + x E) = (1 + x)^4. On the ambient
eight-dimensional space the projector is the identity off its block, so these
are also the ambient determinants. The (1 + x)-adic valuation is 2 rank(A):
at least 2 for every nonzero full call, and exactly 4 for E.

The same count is exhaustive. There are 16 idempotent values of A and 16
values of B. Exactly 26 pairs satisfy the projector equation: one zero, 24
rank-1 calls, and the single unsplit E. Each rank-1 A has a four-element
subspace of legal B.

## 3. The call-count obstruction

Determinant is multiplicative over the commutative ring F_2[x_0, x_1, x_2],
and the factor 1 + x_j is prime, so valuations add. A call in stage k
contributes a determinant in F_2[x_k] only. Thin calls contribute det I = 1.
The target factor I + x_j E_j has valuation 4 at 1 + x_j. Therefore the full
calls in stage j must have valuations adding to 4.

Each nonzero call contributes at least 2, so the stage has at most two nonzero
full calls. Three or more contribute at least 6. The resulting pure
determinants differ, and the operators differ with them. Interleaving does not
change the valuation, and a later invertible factor in another variable does
not cancel it.

The equality cases for the valuation are exactly two rank-1 calls, or one copy
of E. Both sit outside the three-or-more hypothesis. The two rank-1 case is
sharp for the determinant: the ordered pairs that multiply to I + x E are
precisely the 24 ordered complementary pairs (A, B) and (I + A, B), twelve
unordered orthogonal resolutions, both orders. That is the predecessor's
resolution list, recovered here as the commutant rather than as a search over
call orders.

## 4. The rank 6 or 7 corollary

The predecessor rank floor at this size is

```text
sum of thin ranks >= 2 d + 2 ceil((g - 2) / L) = 6
```

with L = 3. Ranks 6 and 7 are inside that floor for a two-map word. They are
not inside the three-or-more call hypothesis. The pure endpoint already fails
before the thin matrices are chosen, for every finite list of constant thin
maps and every rank. Exactly two thin maps of total rank 6 or 7 are the
special case asked here.

The same stage exponent depends only on d = 2. Any leaf count with this block
size has the same per-stage obstruction. The open profiles g = 13, q = 8 and
g = 31, q = 26 use larger blocks, and this identity does not address them.

## 5. Census that accompanies the identity

`verify.py` scans all 256 commutant pairs and checks the closed determinant
against a sign-free Leibniz expansion. It then multiplies matrices in F_2[x].

| Domain | Size | Endpoint matches |
|---|---:|---:|
| Nonzero projectors | 25 | valuation at least 2 on each |
| Ordered pairs | 625 | 24, all complementary resolutions |
| Ordered triples | 15,625 | 0 |

On every triple the Leibniz determinant of the product equals the product of
the determinants. Call lists of length 4 or more are not enumerated. Each of
the 25 nonzero projectors has valuation at least 2, so every such list has
valuation at least 8, while the target has valuation 4. That bound is uniform.
It does not stop early, prune by rank, or sample orders.

A separate eight-dimensional check embeds every nonzero projector into all
three stages and checks that the support is exactly the stage block. One
grouped two-stage resolution reproduces (I + x E_0)(I + y E_1). Inserting one
more stage-0 call moves that operator, and multiplying by the constant
identity, the pure part of a thin map, does not move it back. Flipping one
entry of a resolving pair also leaves the endpoint.

## 6. Outside this claim

The two-call words, including the rank-8 census and its rank-4-plus-4
commuting control, satisfy the determinant count and are not reopened. One
unsplit call E_j per stage also satisfies the count; its thin-map equation is
untouched. Three or more thin maps under the two-call contract, and block
entries outside F_2, are untouched. Projectors that leave the stage block or
fail to commute with T, and non-idempotent factors, are outside the
classification. No native caller, compiler bill, or selected-frontier replay
was run.

## Credit

The contract, the local form, and the rank floor are from PR #5747 (Ali
Romman), including the predecessor statements in PR #5673, PR #5631, and
PR #5617. The two-call rank-8 census that left this call-count question open
is the fork package on `cursor/paired-star-two-thin-rank-b55f` at
`9888af91b9f9e6dc55efd4172858a7d6093d484b`. The one-map census is PR #6922.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed. Apache-2.0.

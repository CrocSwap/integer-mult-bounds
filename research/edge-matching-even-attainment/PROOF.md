# Sharp even-difference image maxima

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped proof about binary projector geometry. No new kappa,
paid word, or native supplier is claimed.

## 1. Exact scope and result

At any finite coordinate width, let C be a collection of rank-one
idempotents `xy^T` over F2 with nonzero off-diagonal patterns. Let H be
their actual pattern span, k its dimension, V their joint image, and n
its dimension. The action of C on nonzero V is assumed irreducible.
Put an undirected edge {a,b} in the coordinate graph when H contains
the matrix unit E_ab or E_ba. Let nu be the maximum matching size.
The collection need not be the complete pool of all lifts of H.

The [matching theorem of PR #7692](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md)
gives `2n<=3k+nu-1`. Its proof is a consumed premise. For positive even
k-nu, integrality gives `n<=(3k+nu-2)/2`.

**Theorem.** For every positive even k-nu this last upper bound is sharp,
except at `(k,nu)=(2,0)`, where the exact maximum is one. All positive-even
maxima are attained by complete pools.

The zero-difference boundary has a different existence condition. At
`k=nu=1`, a one-member collection attains n=1. At `k=nu>1`, no such
irreducible collection exists. The complete pool at `k=nu=1` is reducible;
the allowance for subcollections matters there.

The [odd-difference theorem of PR #7703](https://github.com/aliromman/integer-mult-bounds/blob/2523029b27d40526b811591ce0fb85f9bc1b1df7/research/edge-matching-equality-classification/PROOF.md)
already gives the sharp maxima for positive odd k-nu. Combining that prior
result with this theorem gives the full table for `k>=1` and `0<=nu<=k`:

| Condition | Maximum n, or existence |
|---|---|
| k=nu=1 | 1, for a proper subcollection |
| k=nu>1 | No irreducible collection |
| k-nu is 1 modulo 4 | `(3k+nu-1)/2` (prior result) |
| k-nu is 3 modulo 4 | `(3k+nu-3)/2` (prior result) |
| k-nu is positive and even, except (2,0) | `(3k+nu-2)/2` |
| (k,nu)=(2,0) | 1 |

This table classifies attainable image maxima, not every attaining pool
or a prescribed edge graph. The new constructions are described below.

## 2. The old disjoint core

Choose integers t,r>=0 with t+r>0. On each of t disjoint coordinate
pairs use the two image/covector pairs

```text
(e_a, e_a+e_b),    (e_a+e_b, e_b).
```

On each of r further disjoint triples use the row-mask pairs

```text
(6,5),    (5,6),    (7,7).
```

These pair and triple blocks are prior constructions in PR #7692 and
PR #7703. On a pair the common off-pattern is E_ab. On a triple the three
patterns are the nonzero elements of a two-dimensional unit-free space.
The images and covectors form dual bases in each block. Put

```text
m = 2t+3r,
h_x = sum of the m old image vectors,
h_y = sum of the m old covectors.
```

Both sums are nonzero, with a nonzero component on every old block, and
`h_y dot h_x = m modulo 2 = r modulo 2`. More explicitly, each pair
contributes e_b to h_x and e_a to h_y. Each normal triple contributes
its third coordinate vector to both sums.

Let H0 be the old pattern span. It has dimension t+2r. Its matrix units
are precisely the t chosen, disjoint directed units. Its complete pool
is precisely the old pair and triple members. To see this, a rank-one
idempotent with a nonzero block-diagonal pattern must lie in one block:
choose a coordinate common to its image and covector supports. Any
factor bit in another block would force a forbidden cross entry.
Within a pair, a matrix unit has its two stated lifts. Within a normal
triple, each nonzero pattern has its one stated lift. These fiber facts
are also stated and proved in the cited matching proof.

## 3. Two fresh links

Add fresh coordinates f and g. Define a two-by-two matrix Z by

```text
Z = [[1,0],[0,1]] if r is even,
Z = [[0,1],[1,0]] if r is odd.
```

Its rows are covectors z1,z2 on the fresh coordinates. Add projectors

```text
L1 = (h_x+e_f)(h_y+z1)^T,
L2 = (h_x+e_g)(h_y+z2)^T.                            (1)
```

Each factor pairing is `r+Z_ii=1` in F2, so both links are idempotent.
Their cross rectangles with the old core are nonzero. Their images,
together with the m old images, form a basis of the full ambient space
of dimension m+2.

The two new patterns are independent modulo H0. Their restrictions
to the old-row/fresh-column rectangle are the two different coordinate
columns h_x, possibly exchanged. Thus every nonzero combination of
the links has a nonzero such rectangle. Each such combination also
has a nonzero fresh-row/old-column rectangle. These are disjoint, so
no pattern in any of the three new cosets is a matrix unit. Therefore

```text
k = t+2r+2,    nu = t,    n = m+2 = 2t+3r+2,
2n = 3k+nu-2.                                       (2)
```

The old covectors detect every old coordinate. After they vanish,
the two link covectors detect the two fresh coordinates because Z is
invertible. Hence the selected projectors have no common kernel.
Every old projector maps each link image to its own image, since
`y_i dot h_x=1`. Each link maps every old image to its link image, since
`h_y dot x_i=1`. As m>0, this connects every selected image to every other.

For a nonzero invariant subspace, the zero-common-kernel property gives
some nonzero projector output, hence one projector image in the subspace.
The stated connections then give all m+2 independent images. Thus the
selected collection is irreducible on the full ambient space. Adding
the remaining pool members cannot destroy irreducibility.

Given positive even k-nu, put `t=nu` and `r=(k-nu-2)/2`. Then (2) gives
the desired parameters whenever t+r>0. The sole missing case is (2,0).

## 4. The complete pool, including the extra member

The old coset contributes exactly the old pool. In the coset of either
single link, its two nonzero cross rectangles force both old factors
and all fresh factor bits. The only possible lift is that link itself.

Consider the sum coset of the two links. Its cross rectangles force
the only possible factors to be

```text
x = h_x+e_f+e_g,    y = h_y+e_f+e_g.                 (3)
```

If r is even, the two fresh off-diagonal entries of the sum coset are
zero. Those of (3) are one, so the coset has no lift.

If r is odd, those fresh entries are one and agree with (3). The old
block of the two links cancels, so (3) belongs to the coset exactly
when `off(h_x h_y^T)` belongs to H0. With at least two old blocks this
is impossible: h_x and h_y have nonzero components in every block,
so their outer product has a nonzero cross-block entry, whereas H0
is block diagonal.

The only single-block odd case is t=0,r=1. There h_x=h_y is the third
coordinate of the normal triple, so its outer product is diagonal.
The extra lift exists and is idempotent. At the displayed coordinate
order it has factors `(28,28)` on five coordinates.

Thus the complete pool has exactly n members except at `(k,nu,n)=(4,0,5)`,
where it has n+1=6. Its joint image stays n and the action stays irreducible.
This includes all additional lifts; an independent-image list alone
would miss that sixth member.

Attainment at (k,nu,n)=(4,0,5) is already known from unpaidmoon's
[PR #7094](https://github.com/CrocSwap/integer-mult-bounds/pull/7094),
[pinned proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/b5f0a0df3d22e8ad40d67d6be4d1c7ff24d180c5/research/no-edge-dim4-image-five/PROOF.md).
That different complete pool has five members. Together with the prior
matching bound it already settles that one maximum. The six-member pool
here is part of a new all-parameter construction, not a claim to first
attainment at that instance. The verifier checks the five-member source
pool separately as a comparison. These two pools also show why the maximum
theorem is not a classification of every maximizing pool.

## 5. The exception (k,nu)=(2,0)

The inherited bound gives n<=2. Suppose n=2. A nonzero non-unit binary
off-pattern has at most one rank-one-idempotent lift, by the fiber lemma
in the matching proof. The two-dimensional H has only three nonzero
patterns, none a matrix unit. Thus C has at most three members.
Each restricts to a rank-one idempotent on V, because it fixes its
nonzero image vector in V.

Two rank-one idempotents on F2^2 always have a common invariant line.
If their images agree, use that line. Otherwise use the two images as
a basis. Their covectors have forms `(1,a)` and `(b,1)`. If a=0 or b=0,
one image line is invariant. If a=b=1, they share the kernel line
spanned by `(1,1)`. This also covers repeated restrictions.

It remains to consider three distinct restrictions. The three ambient
patterns sum to zero, so the sum D of the projectors is diagonal and
idempotent. Its restriction to V is idempotent with trace one, hence
rank one. There are exactly six rank-one idempotents on F2^2. Indeed,
write a matrix as `[[a,b],[c,1+a]]`; rank one requires bc=0, which gives
six choices. They split into three complementary pairs, and the sum
of all six is I.

D cannot equal any of the three distinct restrictions, since that
would make the other two equal. The other two members of the six,
outside these four, must therefore sum to I. They form a complementary
pair. The four inside consist of the two remaining complementary pairs,
so the original three contain one complete complementary pair.

In a basis where that pair is E11,E22, the third projector again has
form `[[a,b],[c,1+a]]` with bc=0. It preserves one coordinate line, as
does the complementary pair. This contradicts irreducibility. Thus n=2
is impossible at every ambient width.

The complete pool with image/covector pairs `(7,1)` and `(7,2)` at width
three attains n=1. Their patterns are independent, and their nonzero
span contains no matrix unit. The third pattern would require factors
`(7,3)`, whose pairing is zero, so there is no third lift. Both operators
act as the identity on their common image line. This proves the maximum.

## 6. The boundary k=nu

A matching of size k supplies k independent directed matrix units in
the k-dimensional H. They are therefore a basis, on disjoint coordinate
pairs. A noncoordinate rank-one-idempotent lift in this span must be
one of the two lifts of one individual unit. This follows from the
same block-support argument in Section 2.

To span H, the collection must use every pair. At k>1 its nonzero
image components in the disjoint pairs are proper invariant subspaces,
so irreducibility is impossible. At k=1 one unit lift gives an irreducible
one-dimensional image; taking both gives a reducible complete pool.
No assumption about completion of the original collection is made.

## 7. Evidence and limits

The verifier constructs all 24 families with `0<=t,r<=4` and t+r>0.
It lifts all 42,256 nonzero patterns, checks the exact complete pools,
matching sizes, ranks and Gram matrices, and checks the connections
between projector images. It also checks every nonzero-vector orbit
when n<=9. For width at most seven, an independent scan of 21,284 raw
factor pairs gives the same pools. The exceptional width-three witness
is checked by both methods as well.

The small restriction check enumerates all 36 ordered pairs and all
216 ordered triples of the six rank-one idempotents on F2^2. All pairs
and the 168 triples with idempotent sum have a directly checked common
invariant line. A separate orbit check rejects irreducibility whenever
their joint image is two-dimensional. This corroborates the written
argument in Section 5. It does not enumerate ambient embeddings; the
written reduction handles every width.

For k=nu from one through six, all 126 choices of one lift per edge
and each complete pool have the claimed reducibility status. Choosing
the wrong parity for Z makes both links non-idempotent. Choosing a
singular fresh pairing can leave idempotent links with connected action
but a nonzero common kernel. These controls test both parts of the
irreducibility argument. Exact receipts are in [RESULT.json](RESULT.json).

The result settles image capacity at these parameters. It does not
classify every maximizing pool, solve a paid relation lattice, or give
native realization, owned state, restoration, a complete BIT invoice,
or a multiplier. All five selected assumptions remain. No selected
cold replay, complete predecessor suite, native, Lean or Docker replay,
independent human review or proof-kernel check was run.

## Credit and next question

The matching bound, disjoint relation theorem and basic blocks are from
Ali Romman's PR #7692. PR #7703 supplies the sharp odd case and the
complete-coset method. Nick Petalas's
[one-edge proof](https://github.com/petalas/integer-mult-bounds/blob/5dbf2c05220bea53d84b510efe5910c4cec8f182/research/one-edge-pattern-reducibility/PROOF.md)
in [PR #6785](https://github.com/CrocSwap/integer-mult-bounds/pull/6785)
already gives the upper bound four at (k,nu)=(3,1), without attainment.
The t=1,r=0 construction here attains it. The earlier normal-triple and
fiber credit is retained in [CREDITS.md](CREDITS.md). Binary primitives
are adapted from the pinned prior checker.

The remaining classification question is which other complete pools
attain the even maximum. That question differs from the maximum itself.
A paid-word use still needs the actual relation lattice and full endpoint;
the existing single-bridge obstruction must not be assumed to settle
the new two-link alphabet. No follow-up is reserved.

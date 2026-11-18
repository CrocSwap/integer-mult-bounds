# A bound for irreducible image-basis projector collections

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The written proof and the finite checks need independent review.

## 1. Statement and scope

Work over F2 in a fixed coordinate space of width W. Let
`P_i = u_i v_i^T`, for `1 <= i <= n`, be rank-one idempotents. Thus
`v_i^T u_i = 1`. Assume that the n image vectors are independent. Let V be
their span. Assume that the collection acts irreducibly on V. Delete the
diagonal of a matrix with the map off. Set

```text
H = span{off(P_i)},       k = dim(H).
```

Assume that each pattern is nonzero and that H contains no off-diagonal
matrix unit. The collection need not be the complete pool of H.

**Theorem.** `2n <= 3k-1`.

If equality holds and `n > 1`, there is an even integer `d >= 2` such that
`n=3d+1` and `k=2d+1`. Up to coordinate and projector permutations, the
collection consists of d disjoint normal-form triples and one link:

```text
On block j, with coordinates (3j,3j+1,3j+2):
    u = e_(3j+1)+e_(3j+2),   v = e_(3j)+e_(3j+2),
    o = e_(3j)+e_(3j+1)+e_(3j+2),
    projectors u v^T, v u^T, o o^T.

h = sum_j e_(3j+2).
Link = (h+a)(h+b)^T,
    a,b supported outside the blocks,   a dot b = 1.
```

Conversely, every such even-block collection attains equality. Its pattern
space contains no matrix unit, its action is irreducible, and its complete
noncoordinate rank-one idempotent pool is exactly this collection.

In particular, **seven projectors with independent images, irreducible
action and pattern dimension at most five must have the two-block form**.
This resolves the minimum-cardinality case of the open classification in
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
[exact question 2](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md).
It does not show that an arbitrary larger complete pool contains an
irreducible seven-projector subcollection. The general image bound at
pattern dimension five remains open.

The two-block example and its links are prior work. See
[PR #7237](https://github.com/CrocSwap/integer-mult-bounds/pull/7237),
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
[PR #7648](https://github.com/CrocSwap/integer-mult-bounds/pull/7648) and
[PR #7676](https://github.com/CrocSwap/integer-mult-bounds/pull/7676).
The new result forces the blocks under the independent-image hypothesis
and gives the general bound and equality classification.

## 2. Independent covectors and the diagonal kernel

The common kernel of the restricted covectors on V is invariant. It is not
V, since each projector fixes its own image vector. Irreducibility therefore
makes this kernel zero. There are n covectors on the n-dimensional space V,
so their restrictions are independent. In particular, the matrices
`u_i v_j^T`, for all i,j, are independent: apply the dual basis to the image
factor, and then use independence of the covectors.

The span A of the projectors has dimension n. Its diagonal subspace
`K = A intersect ker(off)` has dimension `d=n-k`. Choose a basis
`D_1,...,D_d` of K. Express each basis matrix in the projector basis, and let
`r_i in F2^d` contain the coefficients of projector i across these expressions.
These coefficient vectors span F2^d. Otherwise a nonzero linear combination
of the D matrices would have all coefficients zero.

Every diagonal binary matrix D is idempotent. If
`D = sum_i s_i P_i`, independence of the outer matrices gives

```text
s_i s_j (v_i dot u_j) = s_i delta_ij.
```

Thus two different projectors that occur in the same diagonal sum are
orthogonal in both orders. For any two nonzero vectors `r_i,r_j`, some
linear functional on F2^d takes the value one on both. If they are equal,
choose a functional that is one on that vector. If they differ, they are
independent over F2, so prescribe both values. Apply this functional to the
basis of K. It follows that **all projectors with nonzero coefficient
vectors are mutually orthogonal**.

At least one coefficient vector is zero. If none were zero, every projector
would be orthogonal to the others, and each image line would be invariant.
This contradicts irreducibility when `n>1`. When `n=1`, a nonzero pattern
gives `d=0`, so its coefficient vector is zero as well.

## 3. Nonzero classes occupy separate coordinate sectors

Group the projectors with the same nonzero coefficient vector lambda. Each
projector in this class satisfies

```text
D_j P_i = P_i D_j = lambda_j P_i.
```

This follows by expansion of D_j and the orthogonality just proved. The
coordinate projection onto the simultaneous diagonal eigenspace lambda is

```text
Q_lambda = product_(lambda_j=1) D_j
           product_(lambda_j=0) (I-D_j).
```

Since lambda is nonzero, this product contains at least one D factor.
Expansion and orthogonality give
`Q_lambda = sum_(r_i=lambda) P_i` as full ambient matrices. There is no
extra identity term outside V. The rank of this sum equals the number of
projectors in the class, because their images are independent and each
projector is the identity on its image and zero on the other class images.
The matrix Q_lambda is diagonal, so the class occupies exactly that many
coordinate positions. Both factors of each class projector are supported
on those positions. Different classes use disjoint positions.

A class cannot have size one: its projector would be diagonal. A class
cannot have size two either. In a two-coordinate block, a noncoordinate
rank-one idempotent over F2 has exactly one off-diagonal entry. If both
off-diagonal entries were one, both factors would be `(1,1)`, whose pairing
is zero. Such a size-two class would put a matrix unit in H.

Thus every nonzero class has at least three members. The coefficient vectors
span F2^d, so there are at least d nonzero classes. Including the zero class
gives `n >= 3d+1 = 3(n-k)+1`, which is the claimed bound.

## 4. Equality forces normal triples and a star

Suppose equality holds and `n>1`. Then `d>0`, there are exactly d nonzero
classes, each has size three, and there is exactly one zero-class projector.
The nonzero coefficient vectors are a basis. Each three-coordinate class
is an orthogonal basis of rank-one projectors.

The normal-form lemma from unpaidmoon's
[PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921),
[Section 3](https://github.com/unpaidmoon/integer-mult-bounds/blob/6020400853abc110134804fad04b695adc360bcd/research/no-edge-irreducible-image/PROOF.md),
classifies such a triple when its pattern span contains no matrix unit.
It is the triple in Section 1, up to coordinate permutation. For completeness,
the finite step is repeated here: enumerate all 168 ordered bases of F2^3,
take the dual covectors, and discard triples with a zero pattern or a
matrix unit in their span. Exactly 18 bases remain. Their image weights
are 2,2,3. The weight-three vector is `(1,1,1)`; the other two vectors are
distinct weight-two vectors and are dual to each other. This gives the
three unordered coordinate versions and no others. The verifier contains
this complete finite enumeration. The classification uses this finite lemma.

Write the remaining projector as `x y^T`. For each old projector
`u_i v_i^T`, irreducibility forces both pairings
`y dot u_i = 1` and `v_i dot x = 1`. If the first were zero, the old image
line would be invariant. If the second were zero, the span of every image
except u_i would be an invariant hyperplane. The other old projectors are
orthogonal, so these claims follow directly by applying each projector.

The core of x is therefore the sum of all old images. The core of y is the
sum of all old covectors. For a normal triple, each sum is its hub coordinate.
Thus `x=h+a` and `y=h+b` with fresh a,b. Independence of the images gives
`a != 0`. In the basis of all image vectors, the covector-pairing matrix is

```text
B = [ I_(3d)   1 ]
    [ 1^T      1 ].
```

It is invertible by Section 2. Adding all old rows to the final row gives
its last diagonal entry `1+3d` in F2. Hence d is even. Idempotence of the
link then gives `a dot b = 1+h dot h = 1`. This also proves `b != 0`.

For `n=7` and `k<=5`, the bound forces `k=5`, so equality applies and `d=2`.

## 5. Converse and complete pool

Take any even `d>=2`, the d normal triples, and a link as in Section 1.
The old images span their `3d` coordinates, and the nonzero fresh image a
makes all `3d+1` images independent. Their covector-pairing matrix is B above.
It is invertible. Its off-diagonal incidence graph is a star with both
directions on every edge. Any nonzero invariant subspace contains some old
or new image: the covectors have no common kernel, so some projector maps
a nonzero vector to its image. The star then gives every image. Thus the
action is irreducible.

Each normal block contributes pattern dimension two. Their supports are
disjoint, so the old pattern space H0 has dimension `2d`. The link has
nonzero entries outside those blocks, so the full pattern dimension is
`2d+1`. A nonzero pattern in H0 has weight at least three. In the odd coset,
choose a fresh row where a is one. Its entries in the old columns are the
d hub entries, independent of the chosen H0 term. Since `d>=2`, that coset
contains no matrix unit either.

To check completeness, first take a noncoordinate rank-one idempotent whose
pattern lies in H0. No fresh factor bit can occur: a fresh image bit would
force its covector to that same coordinate, after which the zero outside
column would force a coordinate projector. The same argument applies to a
fresh covector bit. Idempotence gives a coordinate where both factors are
one. The forbidden cross-block entries then force both factors into that
one block. The normal triple is the complete pool in its two-dimensional
pattern space, as the finite three-coordinate check verifies.

Now take a projector whose pattern lies in `off((h+a)(h+b)^T)+H0`.
A fresh row with a one has old row h. Since h is nonzero, it forces that
image bit to one and forces the entire old covector to h. A fresh column
with a one in b forces the entire old image to h. The remaining fresh rows
and columns then force the fresh factors to be a and b. Thus the only lift
in this coset is the link itself. The complete pool is exactly the stated
collection. This argument also reproves completeness without importing a
runtime predecessor package.

The fixed two-block fresh-factor classification was established in
[PR #7676](https://github.com/CrocSwap/integer-mult-bounds/pull/7676),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/943c355c233649f77f018e6247e5456584ef715e/research/two-block-fresh-link-classification/PROOF.md).
The nonsymmetric example is due to Nick Petalas in
[PR #7648](https://github.com/CrocSwap/integer-mult-bounds/pull/7648),
[exact source](https://github.com/petalas/integer-mult-bounds/blob/f967555200c111925d48a46b65b124432a762b65/research/no-edge-asymmetric-block-link/README.md).
Those results supply context and credit; they are not new two-block examples
claimed by this package.

## 6. Checks and limits

The exact verifier repeats the 168-basis lemma. It checks complete pools for
nine equality fixtures with 2,4,6 blocks and symmetric or nonsymmetric fresh
factors. This covers all 26199 nonzero patterns in those nine spaces. It
checks the diagonal kernel, all coordinate sectors, image and covector rank,
and strong incidence. For the seven-image fixtures it also checks the orbit
of each of the 127 nonzero vectors directly.

It also checks every image-basis collection at ambient width three, with
projector labels removed by sorting the distinct images: 2156 collections.
Exactly 146 have nonzero unit-free patterns, and 19 of these are irreducible.
For all 146, the incidence test agrees with direct vector-orbit closure.
Every irreducible case satisfies the bound.

The pool enumeration uses a four-trial lift rule. Choose a one at position
`(i,j)` of a nonzero pattern. Then `x_i=y_j=1`; column j fixes every image
bit except x_j, and row i fixes every covector bit except y_i. Test the four
remaining pairs against the entire pattern and the idempotence condition.
The verifier compares this rule with all noncoordinate rank-one idempotents
at widths 2,3,4: respectively 4,25,116 matrices. This rule is consistent with
Nick Petalas's fiber lemma, credited by the exact source of PR #6921.

Two boundary controls violate the bound after a hypothesis is removed.
The six old projectors from two normal blocks have `n=6,k=4`, but the action
is reducible. The pairs `(1,3),(3,2),(6,5)` at width three have `n=3,k=2`
and irreducible action, but their pattern space contains a matrix unit.
The bit integers give coordinate supports, with coordinate zero in the low
bit. Three odd-block stars are idempotent and have a one-dimensional common
kernel, which checks the parity obstruction.

No claim is made about arbitrary dependent-image collections, paid BIT
words, native implementation, complete recursive invoices, or kappa. The
selected frontier and its five assumptions stay unchanged. The finite checks
do not constitute formal-kernel or independent human review.

## Open next questions

Can a complete unit-free pattern-dimension-five pool with irreducible image
dimension seven avoid every irreducible seven-projector subcollection?
First examine the incidence and common kernels of image-basis subcollections.
The theorem applies to such a subcollection only after its irreducibility
has been proved. It must not be inferred from irreducibility of the full pool.

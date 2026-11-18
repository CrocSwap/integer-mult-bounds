# Sharp linear image bounds with matrix-unit edges

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped written proof with exact finite checks. Independent human
and formal-kernel review are not claimed.

## 1. Statement

Work over F2 at any finite ambient width W. Let C be a collection of
rank-one idempotents `P=xy^T`, with `y^T x=1` and `off(P)!=0`. Let H be
the span of their off-diagonal patterns, of dimension k. Let V be their
joint image, of dimension n. The collection need not have independent
images and need not contain every possible lift of H.

Make an undirected graph on the coordinate indices. Put an edge {a,b}
in this graph if H contains `E_ab` or `E_ba`. Let nu be its maximum
matching size: the largest number of edges with disjoint endpoint pairs.
Let e count the directed matrix units in H. Then `nu<=e<=k`.

**Theorem.**

```
2n <= 3k+nu.                         (total image)
2n <= 3k+nu-1, if n>0 and C|V is irreducible.
```

The total bound `floor((3k+nu)/2)` is attained for every integer pair
`k>=1`, `0<=nu<=k`, by a complete pool. Thus the universal total maximum
is `2k`. The universal irreducible maximum is `2k-1`, attained for every
`k>=1` by a complete pool. The theorem does not assert that the refined
irreducible bound is sharp for every fixed pair (k,nu), or that the total
bound is sharp for a prescribed edge graph.

Coordinate projectors are excluded. If they are allowed, arbitrarily
many independent images can have pattern dimension zero.

The disjoint-relation method comes from Ali Romman's
[PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md).
Here two-member circuits are allowed. Their endpoint matching supplies
the new term nu. The proof below states the required arguments in full.

## 2. Disjoint diagonal relations

Choose n projectors `P_i=x_i y_i^T` whose images form a basis of V. Their
matrices are independent: a zero linear combination, read one column at
a time in the independent x_i, forces each coefficient times y_i to be
zero. Let their pattern rank be k0, with `k0<=k`. The space K of diagonal
linear combinations has dimension `d=n-k0`.

Choose a basis of K. Let `r_i in F2^d` be the coefficient character of
P_i: a parameter s in K has coefficient `s dot r_i` at P_i. At any fixed
ambient column b, diagonal matrices have column span of dimension at
most one. Independence of the x_i therefore implies that

```
s -> ((s dot r_i) y_i(b))_i
```

has rank at most one. Hence all nonzero r_i for which `y_i(b)=1` are
equal. This is where the binary field is used.

Group indices by their nonzero character c. The sum Q_c of the projectors
in each group is diagonal. To see this at column b, either no member of
the group has `y_i(b)=1`, or c is the sole nonzero active character there.
In the latter case choose s with `s dot c=1`; the column of Q_c is the
same as that of the corresponding diagonal combination.

Every Q_c is nonzero, since the P_i are independent. The indicator vectors
of these groups are independent elements of the d-dimensional relation
space. Thus there are at most d groups. The characters r_i span F2^d,
so there are at least d groups. There are exactly d, their characters
are independent, and their indicators span the entire relation space.
Indices with zero character are free members.

Write S_c for the active coordinate set of Q_c. These sets are disjoint.
If a column contains the nonzero character c, the sum of its participating
independent images is nonzero. Thus it is an active column of Q_c.
Consequently every y_i in that group is supported on S_c. Moreover
the coordinate span of S_c is contained in the group's image space U_c,
since `Q_c e_b=e_b` there. If the group has m members, then

```
1 <= |S_c| <= m,       |S_c| = m (mod 2).
```

The rank inequality and trace give these two facts. The U_c for distinct
groups, and the free image lines, form a direct sum, since all x_i are
independent. No group has size one: that would be a zero pattern.

## 3. Two-member groups form an edge matching

For a two-member group the preceding rank and parity facts force
`|S_c|=2`. Its image space is exactly that coordinate plane, and both
covectors are supported there. The two projectors have the same nonzero
off-diagonal pattern, because their sum is diagonal.

In two binary coordinates, idempotence is
`x_a y_a + x_b y_b=1`. Both off-diagonal entries cannot be one: that
would force all four factor entries to be one and give trace zero.
Thus the common pattern is one matrix unit, say E_ab. Its two lifts are

```
e_a(e_a+e_b)^T,       (e_a+e_b)e_b^T.
```

Their active set is {a,b}. Distinct two-member groups have disjoint
active sets. If t counts these groups, they therefore give a matching
in H, and `t<=nu`.

All other groups have at least three members. Include the nonnegative
number of free members to obtain

```
n >= 2t+3(d-t) = 3d-t.
2n <= 3k0+t <= 3k+nu.
```

This proves the total bound for every collection. In particular it
applies to the complete pool C(H) of all noncoordinate lifts in H.

## 4. Total equality is reducible

Suppose `n>0` and `2n=3k+nu`. Every inequality in Section 3 is then an
equality. Hence `k0=k`, `t=nu`, there are no free members, and every group
has size two or three. The selected pattern span is all of H.

First record a full-pool invariant. If H has zero columns outside a set
S, then

```
K_S = V intersect {z : z|S=0}
```

is invariant under every projector in C. Indeed, a covector supported
on S kills K_S. If `y_j=1` outside S, the zero off-column j forces
`x=e_j`; its image is in K_S. If the coordinate span of S is contained
in V and `0<|S|<n`, this is a proper nonzero invariant subspace.
This lemma was used in Ali Romman's
[PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/69e70b1426c32b19da8334930815800a2c95ffca/research/no-edge-dim5-extremal-classification/PROOF.md).

Apply it to the union S of the active group sets. All patterns have
columns in S, and its coordinate span lies in V. A size-three group
has active rank one or three. If any has rank one, then `|S|<n`, so
the collection is reducible.

It remains to consider full active rank for every group. Now each U_c
is exactly its coordinate block S_c, of size two or three. All patterns
are block diagonal on these disjoint blocks. A noncoordinate rank-one
idempotent whose pattern has this support must lie in a single block:
choose an index common to the image and covector supports, which exists
by idempotence. Its off-diagonal row and column connect every other
factor coordinate to that same block. If its common index were outside
the blocks, the projector would be coordinate, contrary to the premise.

Each size-two block has precisely its two edge lifts. No size-three
block can contain a matrix unit in its pattern span. Such an edge
would be disjoint from all t size-two edges and give a matching of size
`t+1`, contrary to `t=nu`. The size-three block has a two-dimensional
pattern space whose three nonzero elements are the three selected
patterns. They are distinct, nonzero, and not matrix units.

For completeness, a nonzero non-unit binary pattern has at most one
rank-one-idempotent lift. Choose an off-diagonal one at (a,b). It fixes
all factor entries except x_b and y_a. If a fixed x outside {a,b} is
one, its entry in column a fixes y_a; if a fixed y outside {a,b} is
one, its entry in row b fixes x_b. Idempotence fixes the other unknown
when necessary. If neither outside factor exists, idempotence forces
`x_b+y_a=1`, and the pattern is precisely E_ab. This proves the needed
fiber fact, credited in CubeJerry's
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
[Section 2](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md),
to Nick Petalas.

There are therefore no further projectors in these blocks. Within each
full-rank block, the sum of the selected projectors is the identity and
their images are a basis. Their covectors are the dual basis. Thus all
selected projectors, and the whole complete pool, are mutually
orthogonal. Any selected image line is invariant. There are at least
two selected projectors, since equality has a nonempty relation group.
The action is reducible.

This argument applies to the original collection as well. The complete
pool contains its image V. The total bound already proved gives it
image dimension at most n, so its image is exactly V. Its proper
invariant subspace is invariant for every subcollection. This excludes
total equality in the irreducible case. The integral inequality is
therefore `2n<=3k+nu-1`.

## 5. Sharp total bound at each (k,nu)

Use nu disjoint coordinate pairs. On each pair use the two edge lifts
in Section 3. They contribute one pattern dimension and two image
dimensions. On fresh disjoint triples, use copies of

```
(x,y) = (6,5), (5,6), (7,7),
```

where integer masks give binary coordinates. Their matrices sum to
the identity, their three patterns are the nonzero elements of a
two-dimensional unit-free space, and their images are independent.
The finite three-coordinate form is prior work, retained in
[PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
[Section 7](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md).

Take `floor((k-nu)/2)` such triples. If k-nu is odd, add the single
projector `(x,y)=(1,7)` on three further coordinates. Its pattern has
weight two, its pattern dimension is one and its image dimension is one.
Disjoint block support and the fiber argument prove that these are
the complete pools. There are exactly nu matrix units, on disjoint
pairs, so the matching number is exactly nu. Their image dimension is

```
2nu + floor(3(k-nu)/2) = floor((3k+nu)/2).
```

In particular, k disjoint edge pairs attain `n=2k`.

## 6. Sharp universal irreducible bound

Since `nu<=k`, the strict bound gives `n<=2k-1`. At k=1 use the single
projector `(1,7)`, which acts irreducibly on its one-dimensional image.

For `k>=2`, set `t=k-1`. Take t disjoint edge pairs, on coordinates
`(a_i,b_i)`. Let `h_x=sum e_b_i` and `h_y=sum e_a_i`. Add a fresh
coordinate f and the link

```
B = (h_x+e_f)(h_y+e_f)^T.
```

It is idempotent, since its factor pairing is one. Its pattern is
independent of the t old edge patterns, because it has entries that
join f to the old blocks. Thus the pattern dimension is k. Its two
cross rectangles fix both factors of every lift in its pattern coset:
an entry in column f forces y_f=1, an entry in row f forces x_f=1,
and the remaining entries in that row and column fix h_x and h_y.
Only B occurs in that coset. A pattern in the old span has a lift
only when it is one individual edge. Therefore the complete pool has
exactly `2t+1=2k-1` members, with independent images.

No pattern in the new coset is a matrix unit, since it retains both
nonzero cross rectangles. Hence `e=nu=t`.

Use the 2t old images and e_f as a basis of the joint image. The old
projectors become the first 2t coordinate projectors. The link becomes
the all-one matrix of odd size `2t+1`. This family is irreducible.
For a nonzero invariant subspace, a vector with an old coordinate
nonzero gives that coordinate vector and then the all-one vector.
If all its old coordinates vanish, it contains e_f, which also gives
the all-one vector. The old coordinate projectors then give all old
basis vectors; subtraction gives e_f. The subspace is the whole image.

At k=3 this is exactly CubeJerry's five-projector witness in
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
[Section 5](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md).
That instance and its irreducibility are prior work. The contribution
here is the all-k bound and attaining family, with the matching refinement.

## 7. Relation to earlier bounds and evidence

CubeJerry's cited edge-quotient bound is
`n<=dim(E)+2^(k-e)-1`, where E spans all edge endpoints. It can still
be stronger for a specified edge graph. Take the minimum of valid
bounds; the new matching bound does not replace that graph-sensitive
information. Its universal consequence `n<=2k` removes exponential
growth with k. The dimension-three universal total bound six was
already proved in [PR #6838](https://github.com/CrocSwap/integer-mult-bounds/pull/6838).

At `(k,nu)=(3,1)` the strict bound gives n<=4. Nick Petalas proved the
one-edge instance in [PR #6785](https://github.com/CrocSwap/integer-mult-bounds/pull/6785),
[exact proof](https://github.com/petalas/integer-mult-bounds/blob/5dbf2c05220bea53d84b510efe5910c4cec8f182/research/one-edge-pattern-reducibility/PROOF.md).
The present result applies to other edge graphs with matching number
one as well. At nu=0 it recovers the prior no-edge bound.

The verifier checks all 224036 image-basis collections of sizes one
through three at widths three and four. Of these, 202057 have nonzero
patterns. It checks the entire disjoint relation code, the two-member
edge fibers, the endpoint matching and the bound for each. It also
enumerates all 2825 pattern spaces at width three. Raw rank-one scans
and separate literal-pattern lifting give the same complete pools.
All nonzero-vector orbit closures test irreducibility there; 1166 pools
are irreducible and satisfy the strict bound.

The exact receipt includes all 65 total attaining families with
`1<=k<=10`, `0<=nu<=k`, and eight irreducible families with `1<=k<=8`.
Every nonzero pattern is lifted. The irreducible fixtures have exact
star/Gram certificates; those of image dimension at most nine also
pass all nonzero-vector orbit checks. Controls include overlapping
edges, the unchanged prior five-projector witness, coordinate
projectors, a column-triple equality case, and an orthogonal triple
whose extra edge prevents total equality.

The finite checks corroborate the proof. They do not enumerate all
ambient embeddings. No paid-word relation lattice, coordinate-call
reduction, native operation, dirty-state restoration, complete invoice,
selected-frontier change or improvement in kappa is supplied. All five
selected assumptions remain.

## Open next questions

Can a legal scalar word use the all-k attaining irreducible family and
have target rank greater than paid rank? State its alphabet, integral
relation lattice, endpoint coordinates and dirty-state requirements
before a word search. The pool bounds alone give none of these data.

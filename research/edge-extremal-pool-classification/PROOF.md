# The unique extremal irreducible binary projector pool

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped written proof with finite exact checks. Independent
human and formal-kernel review are unclaimed.

## 1. Statement and the bound used

Work over F2 at any finite width W. Let C be a set of rank-one
idempotents `xy^T`, with `y^T x=1` and nonzero off-diagonal patterns.
Let H be their pattern span, of dimension `k>=2`, and let V be their
joint image. Suppose `dim(V)=2k-1` and C acts irreducibly on V.

**Theorem.** After a coordinate permutation, H contains exactly
`k-1` matrix units `E_a_i,b_i`, on disjoint endpoint pairs. The set C
is the complete pool of all noncoordinate rank-one-idempotent lifts
in H. It consists of the two lifts of each edge and one further member:

```
e_a_i(e_a_i+e_b_i)^T,       (e_a_i+e_b_i)e_b_i^T,
B = (h_x+a)(h_y+b)^T,
h_x = sum_i e_b_i,         h_y = sum_i e_a_i.
```

Here a,b use only coordinates outside all edge endpoints and satisfy
`a dot b=1`. Conversely, every such choice gives an attaining complete
irreducible pool. In a basis of V, its set of restricted projectors is
exactly the first `2k-2` coordinate projectors and the all-one matrix
of size `2k-1`.

This is a parameterization up to coordinate permutation, not a count
of coordinate-permutation orbits. Distinct fresh supports can give
different ambient pools with the same restricted action. No physical
change of basis is declared free.

The proof uses the all-width matching bound in Ali Romman's
[PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md).
If nu is the maximum matching size among the matrix-unit edges of H,
that theorem gives

```
2 dim(V) <= 3k+nu,
2 dim(V) <= 3k+nu-1 for a nonzero irreducible image,
nu <= e <= k,
```

where e is the number of directed matrix units in H. Completeness is
not a premise of that bound. Its written proof is an explicit source
dependency here; its whole package is not rerun by this verifier.

CubeJerry's [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
[exact proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/PROOF.md),
already classifies the restricted five-dimensional action when k=3
and there are two edges. The shared cross-block argument below extends
that proof. The new matching bound first forces the edge count and
disjointness at every k. The final argument also forces completeness
and the full ambient fresh-factor form.

## 2. Completion preserves this extremal image

Apply the irreducible matching bound to C:

```
4k-2 <= 3k+nu-1,       so nu >= k-1.
```

If `nu=k`, the k disjoint edge units form a basis of H. A noncoordinate
rank-one idempotent with pattern in that span lies in one edge block.
To prove this, choose a coordinate common to its image and covector
supports. Such a coordinate exists by idempotence. Its off-diagonal
row and column put every other factor coordinate in the same block.
If the common coordinate is outside the edge blocks, the projector is
coordinate, which is excluded. The complete pool is therefore exactly
the 2k edge lifts. They are mutually orthogonal after a shear in each
pair. Every subcollection with image dimension greater than one is
reducible. Since `2k-1>1`, this case is impossible.

Thus `nu=k-1`. Let C(H) be the complete pool. It contains C, whose
patterns span H, so its pattern dimension is also k. Its total-image
bound is

```
dim image(C(H)) <= floor((3k+k-1)/2) = 2k-1.
```

Its image contains V, so it is exactly V. Any subspace invariant under
C(H) is invariant under C. Thus C(H) is irreducible as well. We may
classify the complete pool first, without assuming that C was complete.

## 3. The pure matrix-unit boundary

Suppose H is spanned by directed matrix units, with edge graph G.
The joint image of C(H) is exactly the coordinate span of the edge
endpoints. Each edge's two lifts give both endpoints. Conversely, a
noncoordinate lift cannot use an isolated coordinate: a common factor
coordinate would either join it to another factor through an allowed
edge, or make the projector coordinate.

Give G the direction from row to column. If a nonempty proper vertex
set S is closed under predecessors, its coordinate span is invariant:
no allowed off-diagonal entry has row outside S and column inside S.
A finite directed graph that is not strongly connected has such a set.
For example, take all predecessors of a vertex that does not have
every vertex as a predecessor. Hence irreducibility on at least two
endpoint coordinates requires G to be strongly connected. Such a
graph has at least as many edges as vertices, since each vertex must
have an outgoing edge.

For reference, the exact criterion for a nonempty pure-unit pool is
strong connectivity and at least three endpoint vertices. At two
vertices, the line through their sum is invariant under all four
possible noncoordinate lifts. For at least three strongly connected
vertices, the edge lifts themselves act irreducibly. If a nonzero
invariant vector z has different bits at the ends of an edge (a,b),
`e_a(e_a+e_b)^T z=e_a`. From e_a, incoming edges give their predecessor
coordinate vectors, and strong connectivity gives every vertex.
If no edge sees different bits, connectivity forces z to be the
all-one vector. The other lift of any edge sends it to `e_a+e_b`.
With at least three vertices this vector is not constant, so the first
case applies. This proves the criterion.

Return to the extremal pool. We know `k-1<=e<=k`. If e=k, the matrix
units span H. Its endpoint count would be `dim(V)=2k-1`. Irreducibility
would force `k>=2k-1`, contrary to `k>=2`. Therefore `e=k-1`. A matching
of that size uses every edge, so all edge endpoints are disjoint.

## 4. The common cross-block restriction

Put `t=k-1`, and let E be the coordinate space of the 2t endpoints.
The old edge span H0 has dimension t. Its complete pool consists of
the 2t edge lifts. A sum of units from different blocks has no
rank-one-idempotent lift, by the block argument in Section 2.

These old images span E. Since `dim(V)=2t+1`, choose a nonzero vector
a supported outside E such that `V=E direct-sum F2*a`. This is possible
by subtracting the E coordinates of any vector in V outside E.

Use the old edge images as a basis of E. Equivalently, apply the
block shear `S=product_i(I+E_a_i,b_i)` within E. It is its own inverse
and sends the old projectors to the 2t coordinate projectors.
Use a as the last basis vector of V.

There is only one nonzero coset H/H0. All remaining pool projectors
have patterns in that coset. Their off-diagonal differences are
supported within E. Thus their E-to-a and a-to-E blocks on V are
the same. A diagonal difference outside E cannot change either of
these cross blocks, and the shear acts only inside E. Write the common
column and row as alpha and beta.

If alpha is zero, the line through a is invariant under the whole
pool. If beta is zero, E is invariant. Both alternatives contradict
irreducibility. Hence both cross blocks are nonzero.

Any remaining rank-one restriction has factors
`(u,epsilon)(v^T,eta)`. Its cross blocks satisfy

```
u eta = alpha,       epsilon v = beta.
```

Over F2 their nonzero values force `epsilon=eta=1`, `u=alpha` and
`v=beta`. Every remaining projector has the same restriction
`(alpha,1)(beta^T,1)`.

For each old coordinate i, if alpha_i is zero, the hyperplane with
coordinate i zero is invariant under all old coordinate projectors
and this restriction. If beta_i is zero, its coordinate line is
invariant. Thus every entry of alpha and beta is one. The full
restricted family is the first 2t coordinate projectors plus the
all-one matrix of odd size `2t+1`.

## 5. The ambient link and forced completeness

Undo the edge shears. Their effect on the all-one old image factor
gives `h_x=sum e_b_i`; the corresponding covector is
`h_y=sum e_a_i`. Every remaining projector therefore has image factor
`h_x+a` and has covector `h_y+b` for some b supported outside E.
Idempotence gives `a dot b=1`, since `h_x dot h_y=0`.

Different b cannot give different members of this coset. The off-block
rectangle from E rows to outside columns is `h_x b^T`, and is the same
for every pattern in the coset. The vector h_x is nonzero because
`t>=1`; one of its rows fixes all of b. Thus there is exactly one
remaining ambient projector B. This proves the displayed full form,
not just equality of its restrictions.

The complete pool now has exactly `2t+1=2k-1` members and independent
images. The original C has the same image dimension and is a subset
of this pool. It must contain every member. Completeness and the
existence of an irreducible image basis are conclusions, not premises.

## 6. Converse and the k=1 boundary

For disjoint edges and fresh a,b with pairing one, the old pool has
2t members. The link B is idempotent and its pattern is independent
of H0, because its two cross rectangles are nonzero. They fix both
factors of every lift in the added coset, so B is the only added
member. No matrix unit lies in that coset, since both cross rectangles
remain. The complete pattern space has dimension `t+1=k` and exactly
t edges. Its joint image has dimension `2t+1`.

In the basis in Section 4, the family is the coordinate projectors
and the odd all-one matrix. It is irreducible: any old nonzero
coordinate of an invariant vector gives a coordinate vector and
then the all-one vector. If only its last coordinate is nonzero,
the all-one matrix gives the same vector. The coordinate projectors
then give every old basis vector, and subtraction gives the last one.

The restriction `k>=2` is necessary for forced completeness. A single
edge lift `e_0(e_0+e_1)^T` has k=1 and irreducible image dimension one,
which is `2k-1`. Its complete pool contains the second edge lift and
has image dimension two. It does not satisfy the classification.
Irreducibility is also necessary: remove one member from k disjoint
edge pairs. The remaining set has k pattern dimensions and image
dimension `2k-1`, but it is reducible and has k edges.

## 7. Exact verification and limits

The verifier enumerates all 2825 pattern spaces at width three.
Complete pools from raw rank-one scans agree with separate pattern
lifting. Its image-orbit irreducibility test agrees with direct
closure of every nonzero image vector. Exactly six spaces satisfy
the k=2 extremal hypotheses, and all have the stated form.

It checks all 4164 directed unit graphs at widths two, three and
four, including disconnected graphs and the ten strong two-vertex
exceptions across those widths. Each proper graph witness is an
explicit invariant coordinate space. The strong graph criterion and
the endpoint image dimension agree with exact pool actions.

Seven complete link domains fix t disjoint edge pairs and enumerate
all realized added pattern cosets that have an image outside the old
endpoint space. The pairs (t,W) are
`(1,3),(1,4),(1,5),(2,5),(2,6),(3,7),(3,8)`.
There are 30702 spaces, counted within these domains. Separate raw
coset buckets and literal-pattern lifts agree on every complete pool.
The 49 irreducible survivors are exactly the predicted fresh pairs;
1351 direct nonzero-vector orbit checks confirm their action.
All 30653 negatives have a checked common-kernel or proper image-orbit
certificate. The domains include 352 pools with extra members, with
up to nine members. They are not truncated to the generating set.

For a fixed edge frame with r fresh coordinates, the number of allowed
links is `(2^r-1)2^(r-1)`: choose nonzero a, then a covector b with
pairing one. This is a count in that fixed frame, not an ambient orbit
count. Each of the seven domains has exactly this many survivors.
Twenty-four wider forms through t=8 and width 19 pass complete-pool,
restriction-matrix and image-orbit checks over 2776 nonzero patterns.
They include nonsymmetric fresh supports.

For the image-orbit test, first compute the common kernel on V. If
it is nonzero, its vector is an invariant line. Otherwise any nonzero
invariant subspace contains the image of some projector. It is then
enough to close the orbit of every projector image. This establishes
the test for dependent images as well as for a basis.

The all-width classification uses the cited all-width matching bound.
Finite checks cover the stated domains and do not enumerate all
ambient embeddings. Full predecessor package replays, selected cold
replay, Lean and Docker are not included. No paid-word relation
lattice, endpoint reduction, native conversion, dirty-input compiler,
complete invoice or new kappa is supplied. The selected frontier and
all five assumptions remain unchanged.

## Open next questions

Does the unique extremal action admit a legal paid word with target
rank greater than paid rank for any larger k? First compare the
five-core word obstruction in PR #6782. State the alphabet, relation
lattice, endpoint coordinates, all counted roles and native interface
before searching words. The normal-form shear is not a free operation.

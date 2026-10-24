# Two outside queries and a subgroup character

## Exact statement

Let `H` be a subgroup of an ADDRESS group `G`. Let
`chi:H -> C2={1,s}` be a group character. Let `z` belong to `H` and
satisfy `chi(z)=s`. Work in `Mat_r(F2[G])` with native queries

    F_N(g)=I-N+N g,

where each control is a nonzero binary rank-one idempotent. Suppose
that the exact word has endpoint

    T_D=I+(z-1)D,

where `D` is a constant binary idempotent of rank `p`.

Suppose that exactly two query maps are outside `H`. Among all other
queries, let `k` maps have character `s`. Then `p<=k+1`.

This result permits distinct outside maps, arbitrary invertible
ADDRESS maps, and arbitrary restored dirty helpers. It does not
require the endpoint to commute with the DATA projectors. Initialized,
discarded, and partial helpers are outside this endpoint contract.

## The subgroup-supported terms force equal controls

Write the complete algebraic product as

    U F_N(g) X F_M(h) Y=T_D,

where `g,h` are outside `H`, and `U,X,Y` are native words over `H`.
Every native query is invertible, since

    F_N(g)^-1=F_N(g^-1).

Its augmentation is `I`. The same is true for native words, their
inverses, and `T_D`. Rearrange the exact equation as

    F_N(g) X=K F_M(h^-1),    K=U^-1 T_D Y^-1.

Both `X` and `K` are supported in `H` and augment to `I`. The selected
left term `N g X` is supported in the left coset `g H`, which is
disjoint from `H`. The selected right term `K M h^-1` is supported in
the right coset `H h^-1`, also disjoint from `H`. Comparison of only
the `H`-supported terms therefore gives

    (I-N) X=K(I-M).

Apply augmentation. It gives `I-N=I-M`, hence `N=M`. No comparison
between the two outside cosets is needed.

## The character gives the rank bound

Apply the character to the last equation. Put `t=s+1`. In `F2[C2]`,
`t^2=0`. A query with character `s` maps to `I+t N_i`; every other
`H` query maps to `I`. Products and inverses therefore add their
character-active controls.

Let `A` be the sum of the active controls in `X`. Let `B` be the sum
of the active controls in `U` and `Y`. Then

    chi(X)=I+t A,    chi(K)=I+t(D+B).

Comparison of the `t` coefficients gives

    (I-N) A=(D+B)(I-N),

and thus

    D=D N+(I-N) A+B(I-N).

All these are binary matrices. Rank subadditivity gives

    rank(D)<=rank(DN)+rank(A)+rank(B)<=1+k.

No rank over the group algebra or over the dual-number ring is used.
No orthogonality or commutation of `D` and the query controls is used.

## Zero or one outside query

With no outside query, the character coefficient directly gives
`D=sum(active controls)`, so `p<=k`.

With one outside query, write the native word as `U F_N(g) Y` with
`U,Y` over `H`. The selected term lies in `H g H`, disjoint from `H`.
An `H`-supported endpoint would force `U N g Y=0`. Invertibility of
`U,Y,g` would force `N=0`. This is impossible.

Therefore `p=3` and `k=1` require at least three outside queries.

## Exact control

Take the three-coordinate ADDRESS flips `S1,S2`, put `z=S1 S2`,
and let `H={I,z}` with `chi(z)=s`. Both flips are outside `H`.
For any binary rank-one idempotent `N`, direct multiplication gives

    F_N(S1) F_N(S2)=I+(z-1)N.

This has `p=1` and `k=0`, and it meets the bound `p<=k+1`. The cross
terms vanish because `N(I-N)=(I-N)N=0`. This control is an exact native
identity. It is not the target `-I3` construction and gives no gain.

## Consequences for the current lane

For a coordinate plane with one spectator axis, take the block group
`H={diag(K,c): c=+1 or -1}` and the character `chi(h)=c`. The plane
queries and all three coordinate flips lie in `H`; only the spectator
flip has character `s`. A plane family plus any two outside query maps
is therefore impossible for three productive roles. The outside maps
can be positive, negative, equal, or distinct. Bridge conjugacy and
intersection calculations are not required.

The same argument applies to an upper block-triangular group with
spectator row scalar `c=+1 or -1`. It removes the affine triples and
their two dense bridges. A lower block-triangular group gives the
spectator-column version. All these conclusions cover restored dirty
helpers through the same rank-three projector `D`.

For three coordinate flips used once and positive elementary shears,
use the stabilizer of each coordinate row line with scalar plus or
minus one. Its character sees only the corresponding negative flip.
A shear is outside exactly when it updates that row. Each row needs
at least three positive shears. Each shear updates one row, so at least
nine positive shears are needed. Together with the three fixed flips,
the restricted family needs at least twelve queries.

For five general positive rank-one unipotents with the three fixed
coordinate flips, at least three positive maps must change each
coordinate row line, and at least three must change each coordinate
column line. This is a necessary condition. It does not exclude all
dense three-coordinate families, other negative query maps, or all
eight-query native words.

The root task supplied the two-outside argument. This lane checked
the algebra independently. A separate read-only audit is required
before this packet labels the result independently verified.

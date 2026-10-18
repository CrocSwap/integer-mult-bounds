# Six-piece singleton concentration excludes a literal P112 caller

Use the fixed P112 root-evaluation code C over a characteristic-zero field K,
with the leading-one nine-bit labels in the pinned geometry. A piece's binary
support rank is the F2 rank of the labels at its nonzero coordinates.

**Six-piece lemma.** For arbitrary pieces with binary support ranks at most
4,5,5,5,6,6, their span meets C in dimension at most one.

**Caller consequence.** Ten independent pieces with bounds `4,5^3,6^6`
cannot have code-intersection dimension at least six. This is the named
historical TWOSIDE(6,4) row in PR3282. No other row or full C5 is claimed.

The proof uses the inherited universal premises below. The new finite result
is full-axis concentration at ten rank-five and eighteen rank-six singleton
labels. It is not an extension of the false uniform common-cut40 statement.

## Inherited premises and checked normalization

The verbatim PR3278 proof, pinned in PREDECESSORS.json, records these previously
proved bounds and identifies its source chain:

1. Binary rank at most five or six permits at most12 or20 support sites.
2. In an E6-normal A2 plane, the live evaluation union has at least78 sites.
   For a rank-five piece its total support M plus singleton support J in any
   one projective fiber is at most22; for a rank-six piece it is at most32.
   These joint bounds allow arbitrary ambient binary spaces and coefficients.

These are mathematical dependencies. Hash authentication does not prove them.
Their analytic/census proofs are not rerun here. Rank at most four has support
at most8 by the elementary leading-one affine bound.

We also use the standard real Weyl-chamber theorem. A root-spanned rational
space is Weyl-conjugate to a parabolic root span. The replay checks the finite
face facts needed here: every at-most-five-node face has at most20 root lines;
every six-node face with at least28 lines is D6 or E6, with30 or36 lines.
Its rational normal plane contains two orthogonal roots or an A2 root pair.
The code checks those normal roots directly, not only the face counts.

Suppose two independent codewords belong to the six-piece span. Lift their
directions to h,k in K^8 and let U be their full live support union. By the
support capacities,

```
|U| <= 8 + 12 + 12 + 12 + 20 + 20 = 84.
```

At least28 live roots are perpendicular to both h and k. Their rational span Z
has rank at most six: rational matrix rank is unchanged over characteristic-zero
extensions. Every full E8 root in Z is also perpendicular to both. Choose a generic
real vector perpendicular to Z avoiding every root hyperplane not containing
that subspace, then move it into a closed Weyl chamber. The checked face bounds
force rank six and a D6 or E6 root system. Hence h,k span the scalar extension
of a rational normal plane. Replacing them by a rational basis preserves U.
This argument uses no ordering on K.

## E6 is excluded by joint incidence

Choose a fixed 2-by-6 matrix A expressing the two codewords as combinations of
the six pieces. A singleton site of piece i in U has projective evaluation
pair equal to column i of A. Thus its singleton sites lie in ONE projective
fiber. A zero column has no singleton site in U. This also holds over K:
any nonempty class agrees with a fiber of the rational normal-plane basis.

Let M_i be the whole support size, including sites outside U, and J_i count
singleton sites in U. At a singleton site the sum of M_i+J_i contributes two;
at a nonsingleton site it contributes at least two. The inherited joint bounds
and the elementary rank-four bound give

```
156 <= 2*|U| <= sum_i(M_i+J_i) <= 16 + 3*22 + 2*32 = 146.
```

This is impossible. Extra supports or cancellations outside U only increase
the incidence consumption. They cannot invalidate the inequality.

## New full-axis concentration lemma

For an orthogonal root pair a,b, a full D6 axis fiber consists of the33 full
E8 root lines with `a dot r !=0, b dot r =0`, or the reversed condition.
Each such fiber spans eight binary dimensions in the nine-bit label space.

PR3283 previously used an eleven-label rank-five concentration lemma. The new
checks lower that singleton requirement to ten and add rank-six concentration.
The replay proves these finite statements in a canonical orthogonal plane:

| Ambient binary rank | Axis labels required | All ambient spaces checked | Qualifying intersections |
|---|---:|---:|---|
|5|10|97,155|512 of size10;120 of size12|
|6|18|10,795|16 of size20|

Every qualifying binary space's full 120-root intersection lies entirely in
that same axis. A lower-rank set of leading-one labels has at most 8 or 16
members, respectively. Thus ten or eighteen such axis labels already span
the stated rank. Any piece of rank at most5 or6 containing that many singleton
labels has its whole support in that same axis.

The primary proof enumerates unique reverse-echelon annihilators inside the
eight-space spanned by the axis. The separate checker enumerates all 237,336
five-label and1,107,568 six-label subsets of each axis, uses a different
elimination convention and checks the resulting full-root closures. Since a
qualifying intersection spans the required dimension, some enumerated subset
is a basis. The two methods agree on every qualifying closure digest and count.
This is finite exact evidence, not a proof-kernel theorem.

To transport the lemma, the replay constructs all eight simple-root reflections
on120 roots and checks their linear action on every nine-bit root label. In
simple-root coordinates a reflection changes one coordinate by an integral
linear combination; modulo two its diagonal coefficient is one. Its action
on the leading-one label space is therefore invertible and linear. The exact
orbit from the canonical unordered orthogonal pair covers all3,780 such pairs.
Both canonical axes were checked, so exchanging pair order causes no gap.

The two small full fibers have12 roots. Each spans seven binary dimensions.
A complete2,667-space rank-five check in that span gives capacity8 for either
small fiber. An arbitrary rank-five ambient space meets the fiber span in a
space of dimension at most five, extendable to a checked five-space. This
proves the bound for arbitrary ambient spaces, not only contained ones.
Rank-six support in a small fiber is trivially at most12.

## D6 forces five entire pieces onto the axes

The actual fixed-frame census of all3,780 orthogonal root planes gives

```
live union82:448 planes, 84:2688, 85:448, 86:168, 88:28.
```

Under |U|<=84, only82 and84 occur. Their live fiber sizes are respectively
`29,29,12,12` and `31,31,11,11`. In particular the two small fibers together
have at least22 sites. Both facts are directly reconstructed from the fixed
112 live roots in the primary replay.

Let `c=(8,12,12,12,20,20)`. Put `D=84-|U|`, so0<=D<=2. At a site of U let
k_t be the number of pieces nonzero there. Each k_t is at least one. The identity

```
D = sum_i(c_i-M_i)
    + (number of piece incidences outside U)
    + sum_{t in U}(k_t-1)
```

has only nonnegative terms. For each i, `c_i-J_i` is its own capacity deficit,
its outside-U incidences, and its nonsingleton incidences in U. The last number
is at most the total overlap excess `sum(k_t-1)`. Consequently

```
J_i >= c_i-D >= c_i-2.
```

Each rank-five piece therefore has at least10 singleton sites; each rank-six
piece has at least18. None can use a small projective fiber for its coefficient
column, since the small-fiber capacities are8 and12. Their singleton sites
belong to a large axis, and the new concentration lemma puts each of these
five entire pieces in its corresponding axis.

They contribute zero at every small-fiber coordinate. The remaining rank-four
piece has at most8 support sites. It cannot cover at least22 nonzero evaluation
sites in the small fibers. This contradiction completes the six-piece lemma.
The proof does not assume disjoint supports, symmetric coefficients, a common
piece coefficient, independence of the six pieces, or absence of cancellation.

## Apply the literal deletion, not an arbitrary40-cut

From ten independent pieces with bounds `4,5^3,6^6`, delete four rank-six
pieces and retain `4,5,5,5,6,6`. If the original span T has at least six code
dimensions, its retained span T' has at least two. Indeed the quotient map
`T intersect C -> T/T'` has rank at most four, so

```
dim(T' intersect C) >= dim(T intersect C)-4 >= 2.
```

The six-piece lemma contradicts this. The deleted pieces need no support bound
for the dimension argument; their stated rank-six bounds simply identify which
pieces were removed. Componentwise smaller versions of this same profile inherit
the conclusion. No other current public residual count is inferred.

PR3286's actual mixed-rank cut40 counterexample does not contradict this lemma.
An arbitrary40-set is not a span of the retained small pieces with the precise
six-piece incidence budget used above. The new proof uses their actual full
supports and fixed coefficient columns, rather than the cardinality of a cut.

## Scope

This is a scoped written exclusion with separately checked new concentration
premises and explicitly inherited global/A2/Weyl premises. No independent human
or formal-kernel review, full C5, global decoder floor, actual physical program,
restoration/consumer/precision invoice, supplier, selected exponent or complete
multiplication theorem is claimed. The family decision is to close this named
caller and stop, not launch another dependent construction or census campaign.

# Pure products for one nested pair and one crossed pair

This is a proof in characteristic two under the hypotheses below, together with
one explicit pure-product witness. It is not a search over words, not a census
of projectors, and not a heuristic. It does not decide the coefficient of `e`,
and it does not say that the profile `g=31`, `q=26` is impossible for every
call order.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

## 1. Contract

Use the paired-star contract in `research/coupled31-chronology/PROOF.md` at
base `17469fff78c22941280f04d39dc5a1faee09c840`. The core and each leaf have
dimension `d`. A stage has two complementary halves on its core-plus-leaf
support,

```text
P = [[A+B, B], [B, A+B]],
```

with `A^2 = A` and `AB+BA = B`. The other half uses `A' = I+A` and the same
`B`. A full call contributes the pure factor `I + x P`, where `x` is the
central stage indeterminate. The first-applied factor is the rightmost factor.
Thin calls are `I + e Z` with `e^2 = 0`. They do not appear in the coefficient
of `e^0`.

The pure part of the target is `product_j (I + x_j E_j)`, where `E_j` is the
identity on the core and on leaf `j` and zero elsewhere. Equal halves mean
`rank(A) = rank(I+A) = q` and `d = 2q`. This note certifies the `g=31`,
`q=26` consequence of the two-stage calculation. It states no `g=13`, `q=8`
result.

The consecutive-halves rank theorem of open PR #7005 is not re-proved. The
internal-gap question and the interleaved five-map profiles are not taken.
Only the pure product is computed. No `q=26` search over words or field
elements is run.

## 2. One adjacent stage

On a single core-plus-leaf support, both orders satisfy

```text
(I + x P')(I + x P) = (1+x) I = (I + x P)(I + x P').
```

The off-diagonal blocks cancel, and the leaf path `x^2 B^2` cancels the core
path, exactly when `AB+BA = B`. Dropping that rewrite makes the identity fail.
The resulting operator is scalar on the core. Stages placed entirely outside
a block that has already matched its pure target therefore multiply that
target by another scalar factor `(1+z)` on the core and on their own leaf.
This is the only fact taken from the adjacent schedule. The rank bound of
PR #7005 is not used.

## 3. Nested pair

Order the four calls so that the inner stage's two halves are adjacent and
lie between the outer stage's two halves. Every choice of which half is
called `A` is allowed. The inner pair collapses by Section 2, for an arbitrary
legal inner block `B_in`, to a scalar operator `S`: multiplication by `1+y`
on the core and the inner leaf, and by `1` on the outer leaf. Write `M = A+B`
and `M' = I+A+B` for the outer stage, and write `U = I+xM`, `U' = I+xM'`,
`p = xB`. The two outer halves then contribute

```text
core-core = (1+y) U' U + p^2
outer leaf = U' U + (1+y) p^2
core-to-leaf = (1+y) U' p + p U
```

when the unprimed half is applied first. Section 2 is the identity
`U' U + p^2 = (1+x) I` and `U' p = p U`. Substituting and using
`BA = AB+B` gives the error below. The outer calculation leaves the error

```text
core and outer leaf:   x^2 y B^2
core-to-leaf, both ways: x y B + x^2 y (B + AB + B^2)
```

when the unprimed outer call is applied first. Here `x` is the outer
variable, `y` is the inner variable, and `A,B` belong to the outer stage.
The opposite outer labeling is the automorphism `A -> I+A`. It preserves
`B` and replaces the degree-`x^2 y` off-diagonal summand `B` by nothing,
leaving `x y B + x^2 y (AB + B^2)`. In every labeling the coefficient of
`x y` on the core-to-outer-leaf block is exactly the outer element `B`.

**Theorem.** The nested pure product equals the two-stage pure target if and
only if the outer off-diagonal block `B` is zero. When `B = 0`, equality
holds for every legal inner block and with no commutation hypothesis on the
two stages. When `B` is nonzero in a representation, the coefficient of
`x y` is that nonzero matrix, so the pure product misses the target.

The identity `B = 0` implies equality is an expansion in the projector
algebra: every surviving word contains `B`. The converse is the same
expansion evaluated in any representation. Thin maps cannot close the gap,
because they contribute `I` to the pure part.

An explicit equal-half family on `F_2^2`, copied onto `26` orthogonal planes,
has core dimension `52` and half-rank `26`:

```text
A0 = [[1, 0], [0, 0]],   A1 = [[1, 1], [0, 0]],   B0 = B1 = 0.
```

These projectors do not commute, and the nested pure product equals the
target. Replacing `B0` by `[[0, 1], [1, 0]]`, or by the nilpotent
`[[0, 1], [0, 0]]`, keeps the projectors legal and noncommuting and makes
the coefficient of `x y` equal to that nonzero `B0`.

## 4. The same nest inside g=31

Suppose every other stage is an adjacent pair placed entirely before or
entirely after this nest. Each such pair multiplies the running pure operator
by a scalar polynomial on the core and by `I` on the outer leaf of the nest.
Starting from the error in Section 3:

- a later adjacent stage multiplies the core-to-leaf block by `(1+z)`;
- an earlier adjacent stage multiplies that block by `I`.

Neither factor is zero in the polynomial ring. After any number of such
stages the core-to-leaf coefficient of `x y` remains a nonzero polynomial
multiple of `B`. At `g=31` this is `29` outside stages. Therefore a nested
pair whose outer block `B` is nonzero, with every other stage adjacent and
outside the pair, misses the pure endpoint at every `q`, including `q=26`.
Five thin maps of rank `26`, or any other thin maps, do not repair it.

This is a scoped obstruction. It does not forbid a nest whose outer `B` is
zero, and it does not forbid schedules that put another non-scalar stage
inside the outer interval.

## 5. Crossed pair with B = 0

Now neither stage contains the other. For the order "stage 0, stage 1, the
other half of stage 0, the other half of stage 1", and for every choice of
which half comes first, take `B0 = B1 = 0`. The leaves match the target for
any idempotents. The core error of the order that applies the unprimed halves
first is

```text
x y (A0 A1 + A1 A0) (I + y A1) (I + x A0).
```

Its coefficient of `x y` is the commutator `A0 A1 + A1 A0`. The same
coefficient appears for the other three complement labelings in which stage 0
starts first. Swapping the names of the two stages gives the orders in which
stage 1 starts first.

If `A0` and `A1` commute, the four joint idempotents

```text
(I+A0)(I+A1),  A0(I+A1),  (I+A0)A1,  A0 A1
```

are orthogonal and sum to `I`, with no field extension. On each image the two
core operators act by the scalars `0` or `1`. Each coordinate therefore
receives the factor `(1+x)` from stage 0 and `(1+y)` from stage 1, in every
call order. Thus commutation implies that every crossed order with `B = 0`
matches the pure target.

If they do not commute, the coefficient of `x y` is nonzero, so those crossed
orders miss the pure target. The direct sum of `26` copies of the `F_2^2`
pair in Section 3 is an equal-half example at `q=26`.

Commuting full projectors are the setting of `COMMUTING.md`. That note already
requires `ceil(g/2) = 16` thin maps when every full projector commutes. The
calculation here does not replace that count. It only identifies which `B = 0`
crossed products match the pure target.

## 6. A crossed witness with noncommuting projectors

Commutation of the diagonal blocks `A` is not necessary once `B` is allowed
to be nonzero. On `F_2^4`, the equal halves

```text
A0 = diag(1, 1, 0, 0),     B0 = 0,
A1 = diag(1, 0, 1, 0),
B1 = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
```

satisfy the projector relations, and each half has rank `2`. Their images in
the joint core-plus-two-leaves space do not commute. The crossed pure product,
in the order of Section 5, equals the two-stage pure target. This is a finite
matrix multiplication, not a search.

The thirteen-fold direct sum is block diagonal on thirteen orthogonal
4-planes. A pure product of direct sums is the direct sum of the pure
products, and the target splits in the same way. The sum has core dimension
`52`, half-rank `26`, a nonzero commutator, and the same crossed pure product
equal to the target. Five rank-26 thin maps are not ruled out by the pure
product for this schedule. The coefficient of `e` was not computed, so this
is a pure-product witness only. It is not an endpoint witness and not a
construction of the profile.

## 7. The product of one nested pair and one crossed pair

Run a nested pair with outer `B = 0` to completion, then run the crossed
witness of Section 6 on two further stages. Section 3 says the nest equals
its pure target, which is diagonal and scalar on the core, so it composes
with the crossed witness. At `q=26` the four-stage pure product equals the
four-stage pure target. The projectors of the nest do not commute with each
other, and the projectors of the cross do not commute with each other.

One further adjacent stage, with a nonzero legal `B`, may be placed entirely
before or entirely after those four stages. The pure product remains the
target. The same one-step scalar multiplication, iterated, places the other
adjacent stages of a `g=31` word outside this block. The pure endpoint of
that schedule is met. The coefficient of `e` is not claimed to vanish, and
no thin map is chosen.

## 8. What this does not prove

- The consecutive rank bound of PR #7005, the internal-gap rank question, and
  the interleaved five-map profiles are untouched.
- A nest with outer `B = 0` can still fail when the coefficient of `e` is
  formed. The same is true of the crossed witness.
- The crossed vanishing locus for arbitrary `B` is not classified. Section 5
  classifies `B = 0`. Section 6 exhibits one compatible noncommuting family.
- Schedules that insert a third non-scalar stage into a nest or a cross are
  not covered by the outside-stage induction.
- No census of call orders, field elements, or projectors at `q=26` was run.
  A pure-product match is not existence of the endpoint. A pure-product
  failure is not a theorem about every other schedule.
- The same algebra is uniform in `g` and `q`. The certified profile is
  `g=31`, `q=26` only.
- Native transport and the selected frontier are untouched.

## 9. Credit

The paired-star contract and the commuting map-count are from PR #5747
(Ali Romman), with the predecessor statements in PR #5673, PR #5631, and
PR #5617. Cinna Davis supplied the controller/simplex lineage those packages
retain. Open PR #7005 posed this pure-product question and proved the separate
consecutive-halves rank bound; that bound is not used as a lemma beyond the
one-stage scalar identity re-checked here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

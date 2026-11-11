# Dimension-6 no-edge pools outside the three printed orbits

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

No new κ is claimed. The selected frontier stays
`363005817/100000000000`. This note does not reprove the dimension bound
of #7139, and it does not replace the three witnesses printed there with
a new canonical list.

Evidence class: **proof by explicit counterexample**. Each counterexample
pool is identified at every large enough width by a finite case split on
the covector. The separation from the three printed witnesses is an
invariant of coordinate permutation, evaluated on those explicit sets.
The 16-element weight check inside each pattern space is an exhaustive
census of that one space. Nothing here is a search over pattern spaces,
and nothing here is a census of all dimension-6 pools.

## 1. Statement

Work over F2. For a width W, write off(N) for the matrix N with its
diagonal deleted. For a space P of zero-diagonal W×W matrices containing
no matrix unit, the complete no-edge pool is

```text
C(P) = {x y^T : y·x = 1, off(x y^T) is a nonzero element of P}.
```

Every element is a rank-one idempotent. Write V(P) for the span of the
images of C(P). A coordinate permutation is a permutation σ of the
coordinate basis, acting by e_i ↦ e_{σ(i)} and by x y^T ↦ (σx)(σy)^T.
Unused coordinates may be padded by zeros and then moved. Two pools are
equivalent when some σ carries one set of projectors onto the other.

Such a permutation preserves Hamming weight and preserves the number of
coordinates that appear in at least one image or covector. Call that
number the support size. The invariant used below is the triple

```text
(support size, sorted image weights, sorted covector weights).
```

**Theorem.** The three dimension-6 pools printed in #7139, Section 9,
are not a complete set of coordinate-permutation classes. Two further
complete no-edge pools of pattern dimension 4 and joint-image dimension
6, called W and B below, lie in two further classes. Both have every
covector of weight 1, so both sit in the equality case of the weight-1
bound in #7138: two columns, each of pattern dimension 2, with
3-dimensional image spaces meeting only at 0. The five explicit pools
have five different invariant triples, so they represent five distinct
orbits. This is a comparison of five explicit pools, not a census of
every dimension-6 pool.

## 2. The three printed witnesses

These are the six-projector lists in #7139, Section 9, copied here so
the comparison does not depend on an unmerged file. The same
column-column list is the dimension-6 witness of #7138, Section 6.
`verify.py` rebuilds each list and, at the widths named in Section 6,
checks that the complete pool equals that list.

**Normal-normal.** On coordinates {0,1,2} and {3,4,5},

```text
(e0+e2)(e1+e2)^T,  (e1+e2)(e0+e2)^T,  (e0+e1+e2)(e0+e1+e2)^T,
```

and the same three forms shifted by 3. Support {0,1,2,3,4,5}, size 6.
Image weights and covector weights are both {2,2,2,2,3,3}.

**Column-column.** Column 0 with T = span(e1+e2, e1+e3), and column 4
with T = span(e5+e6, e5+e7). The six projectors are (e0+u) e0^T for the
three nonzero u in the first plane, and (e4+v) e4^T for the three
nonzero v in the second. Every nonzero vector of either plane has
weight 2, so every image has weight 3 and every covector has weight 1.
Support {0,1,2,3,4,5,6,7}, size 8.

**Mixed.** The normal form on {0,1,2}, as above, together with the
column triple at column 3 with T = span(e4+e5, e4+e6). Image weights
{2,2,3,3,3,3}. Covector weights {1,1,1,2,2,3}. Support
{0,1,2,3,4,5,6}, size 7.

The three triples are therefore

```text
normal-normal   (6, {2,2,2,2,3,3}, {2,2,2,2,3,3})
column-column   (8, {3,3,3,3,3,3}, {1,1,1,1,1,1})
mixed           (7, {2,2,3,3,3,3}, {1,1,1,2,2,3})
```

They are pairwise distinct, so the three printed pools already lie in
three distinct orbits. Sections 3 and 4 add two more.

## 3. Pool W, a heavier column plane

Take width W ≥ 9. Let

```text
T0 = span(e1+e2, e3+e4),    T5 = span(e6+e7, e6+e8),
```

and let P be the set of matrices u e0^T + v e5^T with u in T0 and v in
T5. Both planes are supported off their columns. The nonzero weights in
T0 are 2, 2 and 4. The nonzero weights in T5 are 2, 2 and 2.

**Pattern dimension 4.** The two summands occupy different columns, so
their intersection is zero. Each plane is 2-dimensional, and the map
from the plane to its column matrices is injective. Thus dim P = 4.
Every matrix in P is zero on the diagonal, because neither plane meets
its own column coordinate.

**No matrix unit.** A nonzero pattern has Hamming weight wt(u)+wt(v).
The two columns do not share positions. If both u and v are nonzero the
weight is at least 4. If exactly one is nonzero the weight is 2 or 4.
The minimum is 2, so P contains no matrix unit. This is a check of the
15 nonzero pairs (u,v), since each plane has four vectors.

**The complete pool is six projectors.** The six candidates are

```text
(e0+e1+e2) e0^T,  (e0+e3+e4) e0^T,  (e0+e1+e2+e3+e4) e0^T,
(e5+e6+e7) e5^T,  (e5+e6+e8) e5^T,  (e5+e7+e8) e5^T.
```

Each is an idempotent, and its off-diagonal pattern is the corresponding
nonzero plane vector in one column. It remains to show that nothing else
lies in C(P).

Let x y^T be a rank-one idempotent whose off-diagonal pattern equals
u e0^T + v e5^T with (u,v) ≠ (0,0). Suppose y has a bit b outside
{0,5}. Column b of the pattern is zero, so the off-diagonal part of
column b of x y^T vanishes. That column is x with bit b cleared, hence
x is 0 or e_b. The zero image is not idempotent. If x = e_b, then
y_b = 1 and the pattern is a single row. A nonzero element of P has, in
every nonzero column, at least two ones, so it is not a single row.
Thus y is supported on {0,5}.

If y = e0, the pattern is supported in column 0, so v = 0 and
u = x + x_0 e0. Idempotence forces x_0 = 1, hence x = e0+u with u a
nonzero vector of T0. These are the first three projectors. The case
y = e5 is the last three.

If y = e0+e5, the cleared columns are u = x + x_0 e0 and
v = x + x_5 e5, so u+v = x_0 e0 + x_5 e5. The left side is supported on
{1,2,3,4,6,7,8} and the right side on {0,5}. Both sides are zero, so
u = v = 0 and x_0 = x_5 = 0. Idempotence then fails. There is no mixed
lift.

The same split applies at every width W ≥ 9. Coordinates outside
{0,...,8} never appear. The complete pool is exactly the six projectors.

**Joint image dimension 6.** The first three images sum to e0, and
subtracting e0 recovers e1+e2 and e3+e4. Their span is

```text
U0 = span(e0, e1+e2, e3+e4),
```

which is 3-dimensional and supported on {0,1,2,3,4}. The last three
images likewise span

```text
U5 = span(e5, e6+e7, e6+e8),
```

supported on {5,6,7,8}. The supports are disjoint, so U0 ∩ U5 = 0 and
dim(U0+U5) = 6. The six images are a basis of that sum. Hence
dim V(P) = 6.

**Invariant.** The six images and covectors use every coordinate in
{0,1,2,3,4,5,6,7,8} and no others, so the support size is 9. The image
weights are {3,3,3,3,3,5}. The covectors are e0 and e5, so the covector
weights are {1,1,1,1,1,1}. The triple

```text
(9, {3,3,3,3,3,5}, {1,1,1,1,1,1})
```

matches none of the three triples in Section 2. Pool W is therefore not
a coordinate permutation of any of the three printed witnesses.

## 4. Pool B, the same plane type in a different position

Take width W ≥ 7. Let

```text
T0 = span(e1+e2, e1+e3),    T1 = span(e4+e5, e4+e6),
```

and let P be the set of matrices u e0^T + v e1^T with u in T0 and v in
T1. The first plane is the plane printed for column 0 in Section 2.
The second plane has the same three weights, 2, 2 and 2, but its column
is coordinate 1, which lies in the support of T0.

**Pattern dimension 4, and no matrix unit.** The columns are distinct,
so the sum of the two column spaces is direct and dim P = 4. Nonzero
weights are again wt(u)+wt(v). Every nonzero vector of either plane has
weight 2, so every nonzero pattern has weight 2 or 4. There is no
matrix unit. The possible nonzero column vectors of the two planes are
supported on {1,2,3} and {4,5,6} respectively, which are disjoint.

**The complete pool is six projectors.** The six candidates are

```text
(e0+e1+e2) e0^T,  (e0+e1+e3) e0^T,  (e0+e2+e3) e0^T,
(e1+e4+e5) e1^T,  (e1+e4+e6) e1^T,  (e1+e5+e6) e1^T.
```

The outside-bit case is the same as in Section 3: a bit b outside
{0,1} would force a coordinate image and a single-row pattern, but every
nonzero pattern has a column of weight 2. Thus every covector is
supported on {0,1}. The pure cases y = e0 and y = e1 recover exactly
the six projectors.

If y = e0+e1, the cleared columns satisfy u+v = x_0 e0 + x_1 e1. Write
u = a(e1+e2)+b(e1+e3) and v = c(e4+e5)+d(e4+e6). The left side has
coordinates

```text
e1: a+b,   e2: a,   e3: b,   e4: c+d,   e5: c,   e6: d,
```

and no e0. Equality with the right side forces a = b = c = d = 0 and
x_0 = x_1 = 0, so the pattern is zero and idempotence fails.

Thus at every width W ≥ 7 the complete pool is exactly these six
projectors, and no coordinate outside {0,...,6} appears.

**Joint image dimension 6.** The first three images sum to e0 and span

```text
U0 = span(e0, e1+e2, e1+e3).
```

A general vector is α e0 + (β+γ) e1 + β e2 + γ e3. The last three images
sum to e1 and span

```text
U1 = span(e1, e4+e5, e4+e6),
```

whose general vector is δ e1 + (ε+ζ) e4 + ε e5 + ζ e6. A vector in the
intersection has β = γ = 0 and ε = ζ = 0, then α = 0 and δ = 0. The
intersection is zero, so the sum is 6-dimensional. The six images span
it. Hence dim V(P) = 6.

**Invariant.** The support is {0,1,2,3,4,5,6}, size 7. Every image has
weight 3 and every covector has weight 1. The triple

```text
(7, {3,3,3,3,3,3}, {1,1,1,1,1,1})
```

differs from all three triples in Section 2. It also differs from the
triple of pool W. Pool B is not a coordinate permutation of any printed
witness, and it is not a coordinate permutation of pool W.

The support size alone separates B from the printed column-column pool,
which uses eight coordinates. The image weights alone separate B from
the printed mixed pool, which also has support size 7 but has two images
of weight 2.

## 5. What this does and does not claim

The answer to the question in #7139, Section 10, item 2, is no. Not
every dimension-6 pool is a coordinate permutation of one of the three
printed witnesses. Pools W and B are counterexamples, each proved for
every width at or above its support. They are not offered as a fourth
and fifth normal form that would finish the classification.

The five explicit pools have five different triples, so there are at
least five orbits. That count is only a comparison of these five sets.
It is not an enumeration of the orbits, and a pool that was never
written down could lie in a sixth orbit.

This note does not prove the upper bound dim V ≤ 6. Both examples are
inside the case #7138 and #7139 already allow: two different columns,
each carrying a 2-dimensional unit-free plane, with image spaces meeting
trivially. The new fact is that those planes are not unique up to
coordinate permutation, and that the printed placement of the two
weight-(2,2,2) planes is not the only placement.

The normal-normal geometry and the mixed geometry are not classified
here. Both counterexamples are weight-1 column-column pools. In
particular, this note does not decide whether every pair of disjoint
normal-form blocks is a coordinate permutation of the printed
normal-normal witness.

No word is priced. The selected κ and its framework assumptions are
unchanged. Pattern dimension 5 is not bounded, and the weight-1
image-dimension-4 question of #7138 is not taken.

## Open next questions

1. **Column-column orbits.** Which pairs of 2-dimensional
   minimum-weight-2 column planes have image spaces meeting only at 0,
   and how many coordinate-permutation orbits do those pairs form?
   Pools W and B show that the printed complementary (2,2,2) pair is
   not the only orbit. The first step is to list the weight triples of
   one such plane up to coordinate permutation, then test pairs for a
   trivial image intersection. This package does not make that list.

2. **The other two geometries.** Is every dimension-6 pool built from
   two normal-form triples, or from one normal-form triple and one
   column triple, a coordinate permutation of the corresponding printed
   witness? The first step is the normal-form uniqueness statement on
   one 3-set in #7139, Section 2, followed by a check that two disjoint
   blocks can be moved simultaneously onto the printed coordinates.
   Those geometries are not the source of the counterexamples here, and
   the general case split that sorts every dimension-6 pool into one of
   the three geometries is #7139's argument. It is not reproved here.

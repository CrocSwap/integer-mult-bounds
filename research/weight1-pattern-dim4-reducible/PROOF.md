# Weight-one covectors cap a pattern-dimension-4 no-edge image at 6

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

No new κ is claimed. The selected frontier stays
`781451/250000000`.

Evidence class: **proof** of a dimension bound and a reducibility statement,
under an exact covector-weight hypothesis, together with one **exhaustive
finite census** of an 8-coordinate witness. It is not a census of all pattern
spaces, and it is not a claim about pools that use a covector of weight 2 or
more.

## Theorem

Work over `F2`. Let `P` be a linear space of zero-diagonal `W` by `W`
matrices, with `dim P ≤ 4`, containing no matrix unit. Write `C(P)` for the
complete pool of rank-one idempotents `N = x y^T` with `y^T x = 1` and
`off(N)` a nonzero element of `P`. Suppose every covector `y` that appears
has weight 1. Let `V(P)` be the sum of the images of the pool.

Then `dim V(P) ≤ 6`. If the pool is nonempty and
`dim V(P) ≥ dim P + 1`, the action on `V(P)` is reducible. In particular
every such pool with `dim P = 4` and `dim V(P) ≥ 5` is reducible.

Dimension 6 is attained by the witness in Section 6, so the upper bound is
sharp. That witness is reducible: the common kernel of its covectors inside
`V` has dimension 4.

## Notation

`off(N)` is `N` with its diagonal deleted. A matrix unit `E_ab` (`a ≠ b`)
is the pattern with a single 1 in row `a`, column `b`. The fiber lemma
quoted below is Lemma 1 of `research/pattern-pool-cardinality/PROOF.md`
(Nick Petalas, #5921): a realizable nonzero off-diagonal pattern has exactly
one rank-one idempotent lift, except a matrix unit, which has two.

For each column index `j`, write `U_j` for the patterns in `P` supported
only in column `j`. Those patterns occupy disjoint matrix positions, so

```text
sum_j dim U_j ≤ dim P.
```

## 1. The pool is the nonzero pure columns

**Lemma.** Under the hypotheses, `off(C(P))` is exactly the set of nonzero
elements of the spaces `U_j`. The unique lift of a nonzero `v ∈ U_j` is

```text
x = e_j + v,    y = e_j.
```

The column vector `v` is zero in row `j`, because the pattern is
off-diagonal.

A pool element with `y = e_j` has only column `j` possibly nonzero, and
that column of `x y^T` is `x`. Deleting the diagonal leaves `x + e_j`,
which lies in `U_j`, and `y^T x = 1` forces the `j`-th bit of `x` to be 1.
So every pool pattern is a nonzero element of some `U_j`.

Conversely, take nonzero `v ∈ U_j`. It is not a matrix unit, so its weight
is at least 2. The displayed lift is a rank-one idempotent:

```text
(x y^T)^2 = x (y^T x) y^T = x y^T,
```

and its off-diagonal pattern is `v` in column `j`. The fiber lemma supplies
no second lift.

Thus no pool covector has weight greater than 1, which is the hypothesis,
and there is nothing else in the pool.

## 2. Dimension contributed by one column

Let `S_j` be the span of `{e_j + v : v ∈ U_j, v ≠ 0}`, and write
`d_j = dim U_j`.

- If `d_j = 0`, then `S_j = 0`.
- If `d_j = 1`, there is one nonzero vector `v`, so `dim S_j = 1`.
- If `d_j ≥ 2`, then `U_j` has at least three nonzero vectors. For any
  nonzero `u ∈ U_j`, choose nonzero `v ≠ u`. Then

  ```text
  (e_j + v) + (e_j + (v + u)) = u,
  ```

  so `U_j ⊆ S_j`. Hence `e_j = (e_j + v) + v` lies in `S_j`. Every column
  vector is zero at coordinate `j`, so `e_j` is outside the column space
  and `dim S_j = 1 + d_j`.

Write `f(0) = 0`, `f(1) = 1`, and `f(d) = 1 + d` for `d ≥ 2`. Then
`dim S_j = f(d_j)`. The joint image is the sum of the `S_j`, so

```text
dim V(P) ≤ sum_j f(d_j).
```

## 3. The sum is at most 6

The positive `d_j` are positive integers whose sum is at most
`dim P ≤ 4`. The complete list of such tuples, up to order, and the
value of `sum f`, is:

| parts | sum f |
|---|---:|
| (4) | 5 |
| (3,1) | 5 |
| (3) | 4 |
| (2,2) | 6 |
| (2,1,1) | 5 |
| (2,1) | 4 |
| (2) | 3 |
| (1,1,1,1) | 4 |
| (1,1,1) | 3 |
| (1,1) | 2 |
| (1) | 1 |

No other partition of an integer at most 4 exists. Therefore
`dim V(P) ≤ 6`.

Equality forces `dim P = 4`, exactly two columns, each of pattern
dimension 2, each image space of dimension 3, those two spaces meeting
only at 0, and `sum d_j = dim P`.

## 4. Reducibility above `dim P`

Let `L` be the span of the basis vectors `e_j` for the columns with
`d_j ≥ 1`. Then `dim L` equals the number `c` of those columns. Each such
column has `d_j ≥ 1`, so `c ≤ sum d_j ≤ dim P`.

Every pool covector is one of those `e_j`. The common kernel inside `V`
is

```text
K = {z ∈ V : y·z = 0 for every pool covector y} = V ∩ L^⊥.
```

Hence `dim K = dim V - dim π_L(V) ≥ dim V - dim L ≥ dim V - dim P`.

If the pool is nonempty and `dim V ≥ dim P + 1`, then `dim K ≥ 1`.
Some pool vector `x` satisfies `y·x = 1` and lies in `V`, so `x ∉ K` and
`K ≠ V`. Each pool map is `z ↦ (y·z) x`, which is zero on `K`. Thus `K`
is a nonzero proper invariant subspace, and the action is reducible.

For `dim P = 4` this covers every weight-1 pool with `dim V ≥ 5`.

In the equality case `dim V = 6`, Section 3 forces `c = 2`. Each
3-dimensional image space contains its `e_j`, so `π_L(V) = L` and
`dim K = 4`.

## 5. The kernel test needs `dim V ≥ dim P + 1`

The inequality `dim K ≥ dim V - dim P` is zero when `dim V ≤ dim P`.
That bound is attained. On twelve coordinates, for `b = 0,1,2,3`, put

```text
x_b = e_{3b} + e_{3b+1} + e_{3b+2},    y_b = e_{3b},
```

and let `P` be the span of the four off-diagonal patterns. Each pattern
has weight 2. A nonempty sum of two or more of them has two or more
unequal nonzero columns, so it is not `off(x y^T)`. The fiber lemma gives
one lift of each single pattern. The pool is exactly these four
projectors, `dim P = 4`, `e(P) = 0`, and every covector has weight 1.
The four images are independent, so `dim V = 4`. Each image meets its
own column coordinate and no other column coordinate, so the common
kernel inside `V` is zero. Each line `span(x_b)` is invariant, so this
particular action is reducible for a different reason. The theorem does
not claim that every weight-1 pool with `dim V = dim P` is reducible.

## 6. Witness of dimension 6

Use width 8. Let

```text
U_0 = span{e_1+e_2, e_1+e_3},    U_4 = span{e_5+e_6, e_5+e_7},
```

and let `P` be the direct sum of those two column spaces. Each space has
three nonzero vectors, all of weight 2. Thus `dim P = 4` and `P` contains
no matrix unit. A pattern with both columns nonzero has those columns
supported on `{1,2,3}` and `{5,6,7}` respectively. Both are nonzero and
they are unequal, so the pattern is not an off-diagonal of a rank-one
matrix. The pool is therefore the six lifts

```text
e_0+e_1+e_2,  e_0+e_1+e_3,  e_0+e_2+e_3     against y = e_0,
e_4+e_5+e_6,  e_4+e_5+e_7,  e_4+e_6+e_7     against y = e_4.
```

Differences of the first triple span `U_0` and recover `e_0`, a
3-dimensional space. The second triple does the same on the complementary
coordinates. The sum is direct, so `dim V = 6`. Section 4 gives an
invariant kernel of dimension 4.

`verify.py` enumerates every nonzero `x` and `y` on these eight
coordinates. That domain is finite, the enumeration is complete, and the
structural reason above is why only the six lifts appear. The same
program checks the one-column dimension-5 example (even-weight columns
on coordinates `1..5`, pattern dimension 4, image dimension 5, kernel
dimension 4) and the four-line example of Section 5.

## 7. What this does not say

A covector of weight 2 or more is outside the hypothesis. The four-cycle
of #6962 has covector weight 3 and acts irreducibly in dimension 4.
Open PR #7094 exhibits an irreducible joint image of dimension 5 at
pattern dimension 4; its covectors have weight at least 2. Neither
example contradicts the theorem.

The argument does not bound irreducible dimension 6 in that heavier
class, and it does not change the selected conditional κ. No search is
used as a nonexistence proof.

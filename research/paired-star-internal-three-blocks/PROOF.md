# One rank-q internal map raises the external bound to `q(g-1)`

This is a proof in characteristic two under the hypotheses below. It is not a
search over words, not a census of projectors, and not a heuristic. The
exhaustive check at `q=1` is a finite census of one auxiliary matrix domain.
It supports the proof and does not replace it.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

## 1. Hypotheses

Use the paired-star schedule of open PR #7025. The core and each of the `g`
leaves have dimension `d = 2q`. Stage `t` has two complementary half
projectors `P_f` and `P_s` on the core and on leaf `t`. In the eigenbasis of
the half idempotent they have the legal off-diagonal form recorded there, so
`P_f + P_s` is the identity on that stage support, `P_f P_s = P_s P_f = 0`,
and both are idempotent. The same basis splits every leaf. A full call is
`(I + x P)(I + e R)` with `x = D + 1` and `e^2 = 0`. A thin call is `I + e Z`.
The two full calls of every stage stay adjacent. Thin maps may occupy the
gaps outside those stage blocks, and at most one stage has thin maps in the
single gap between its halves. No full call of another stage sits in that
gap.

The first-applied factor is the rightmost factor. On a successful word the
coefficient of `e` agrees with the target `(I + e I) product_j (I + x_j E_j)`.
In particular every core-to-leaf block of that coefficient is zero, and the
coefficient is square-free in the stage variables.

**Added hypothesis of this note.** The thin maps in the one internal gap add
to a single matrix `Z` with `rank(Z) <= q`, and `P_s Z P_f = 0`. The second
equation is the one PR #7025 already requires in order to kill the squared
monomial. This note does not assume that a sum of several internal maps has
rank at most `q`. If that sum has larger rank, the bound proved here is not
claimed.

Open PR #7005 is not rerun. Its consecutive bound `q g` excludes the internal
slot. The counting below uses the same external gaps, with the three leaves
kept in the sum.

## 2. The three core blocks

Because the thin map is pure identity plus `e Z`, it does not change the pure
product. Each adjacent pair, with or without `Z` between the halves, still
multiplies to the scalar stage factor of the consecutive schedule: `D` on the
core and on that stage's leaf, and `1` on every other leaf. Later stages
therefore scale the core rows by `product_{k > t} D_k`. An earlier stage `j`
scales leaf `j` and no other leaf. For the core-to-leaf-`j` block of the
internal gap, the outside monomial is

```text
lambda(t, j) = (product_{k > t} D_k) * (D_j if j < t else 1).
```

It does not contain `D_t`. The local factor between the halves is `V Z U`,
with `U = I + x P_f` and `V = I + x P_s`. On an outside leaf the core block
of `V Z U` is linear,

```text
pi_core P_f Z + D_t pi_core P_s Z,
```

and on leaf `t` it is quadratic. Expanding in characteristic two gives the
core blocks

```text
degree 0:  pi_core P_f Z P_s,
degree 1:  pi_core (P_f Z P_f + P_s Z P_s),
degree 2:  pi_core P_s Z P_f.
```

The required monomial on leaf `j` is `M_j = product_{k >= j} D_k`. Comparing
exponents, `lambda(t, j) D_t^a = M_j` for exactly three pairs when `t` is
interior, and for no other leaf or power:

- `a = 1` on leaf `t`, the degree-1 block `O` above,
- `a = 1` on leaf `t - 1`, the block `P = pi_core P_s Z`,
- `a = 0` on leaf `t + 1`, the block `N = pi_core P_f Z`.

An endpoint stage has only the two leaves that exist. Power `a = 2` is a square. The degree-2 part of `V Z U` is the operator
`P_s Z P_f`, and that operator is supported on the stage. Outside stages
scale its four stage blocks by monomials and do not add any other square.
External gaps are square-free, and so is the target. A successful word
therefore needs the operator equation `P_s Z P_f = 0`, not only its
core-to-leaf block. The rank argument uses that equation.

The full calls still contribute `M_j I_d` on core-to-leaf `j`, by the same
scalar transport. An external thin map in the gap after `gamma` completed
stages contributes its core-to-leaf block on the monomial `mu(gamma, j)`, and
`mu(gamma, j) = M_j` if and only if `gamma` is `j` or `j + 1`. Therefore a
successful word satisfies, on every leaf `j`,

```text
A_j + B_j = I_d,
```

where `A_j` is the sum of the external core blocks in gaps `j` and `j + 1`,
and `B_j` is the internal block when leaf `j` is one of the three leaves
above and is zero otherwise. Rank is subadditive, a block has rank at most
the rank of its matrix, and `rank(A) + rank(B) >= rank(A + B)`, so

```text
r_j + r_{j + 1} >= 2q - rank(B_j).
```

Here `r_gamma` is the sum of the ranks of the external thin maps in gap
`gamma`.

## 3. Each core block has rank at most `q`

Let `r = rank(Z) <= q`. Factor `Z = X Y` with `Y` mapping the whole space
onto `F^r` and `X` embedding `F^r` onto the image of `Z`. Such a
factorization exists over any field. The hypothesis `P_s Z P_f = 0` says
that `P_s X` vanishes on `U = im(Y P_f)`.

Write `A = pi_core P_f X` and `B = pi_core P_s X`, both maps `F^r -> core`.
Then `U` is contained in the kernel of `B`, so `dim U <= dim ker B`.

The three blocks factor through these maps:

- `N = A` applied to `Y` on leaf `t + 1`, so `rank(N) <= rank(Z) = r`,
- `P = B` applied to `Y` on leaf `t - 1`, so `rank(P) <= r`,
- `O = A (Y P_f) + B (Y P_s)` on leaf `t`.

The first summand of `O` factors through `U`, so its rank is at most
`dim U <= dim ker B`. The second summand has rank at most `rank(B)`.
Rank-nullity on `B` gives

```text
rank(O) <= dim ker B + rank(B) = r.
```

Thus all three ranks are at most `q`, and their sum is at most `3q`. The
same bound applies to whichever two of the blocks exist at an endpoint.

The cap `q` on each block is sharp. For every `q >= 1`, with both
off-diagonal blocks of `B` equal to zero and `P_f` the plus half, there is
an explicit matrix of rank `q` satisfying `P_s Z P_f = 0` whose three blocks
have ranks `q`, `q` and `q`. Dropping the operator equation, the same
construction with one extra source has rank `q` and block ranks `q`, `q`
and `2q`. The equation is what cuts the own-leaf block from `2q` down to
`q`. Both families are checked for `q` in `{1, 2, 3, 8, 26}`.

Separately, over `F_2` at `q = 1`, every rank-at-most-1 matrix on the eight
coordinate lines, every scalar pair `(B_12, B_21)`, and both half orders
were enumerated. Under `P_s Z P_f = 0` the three ranks sum to at most `3`,
and every one of those eight projector choices attains the sum `3`. That
domain is finite and the enumeration is complete. It is a census of this
8-by-8 family, not a census of words at `q = 26`.

## 4. The external bound

On a helped leaf, `rank(B_j) <= q`, so `r_j + r_{j + 1} >= q`. On every
other leaf, `B_j = 0` and `r_j + r_{j + 1} >= 2q`. Let `S` be the even leaf
indices or the odd leaf indices, whichever has the larger sum of these
demands. The pairs of gaps `{j, j + 1}` for `j` in `S` are disjoint, so

```text
R_ext = sum_gamma r_gamma >= sum_{j in S} (r_j + r_{j + 1}) >= sum_{j in S} d_j.
```

If every demand were `2q`, the even sum would be `2q * ceil(g / 2)` and the
odd sum would be `2q * floor(g / 2)`. Each helped leaf lies in one parity
and lowers that parity's sum by `q`, because its demand is `q` rather than
`2q`.

An interior stage helps three consecutive leaves, so one parity contains two
of them and the other contains one. An endpoint stage helps two consecutive
leaves, one in each parity. In every case the heavier parity is at least
`q(g - 1)`:

- If `g` is even, the two baseline sums equal `q g`. Three helped leaves
  remove `2q` from one parity and `q` from the other, so the heavier
  remainder is `q g - q`. Two helped leaves remove `q` from each, and the
  same remainder remains.
- If `g` is odd, the even baseline is `q(g + 1)` and the odd baseline is
  `q(g - 1)`. Losing `2q` from the even side and `q` from the odd side leaves
  `q(g - 1)`. Losing one from each side leaves at least `q g`.

Therefore every placement of the internal gap satisfies

```text
R_ext >= q (g - 1).
```

For `g >= 3` and `q >= 1` this is strictly larger than the bound `q(g - 3)`
obtained by dropping the three leaves:

```text
q(g - 1) - q(g - 3) = 2q.
```

At `g = 31` and `q = 26` the new bound is `30 * 26 = 780`. The dropped-leaf
bound is `28 * 26 = 728`. The difference is `52`.

The number `q(g - 1)` is sharp for these inequalities. At stage `1` the
helped leaves are `{0, 1, 2}`. Give gap `2i` rank `d_{2i}` and every odd gap
rank `0` when the even demand sum is the heavier one, and the symmetric
assignment when the odd sum is heavier. The resulting tuple meets every leaf
inequality and has total rank `q(g - 1)`. The registered check runs this
tuple for every `g` from `3` through `40`. It is a feasible point of the
rank inequalities, not a paired-star word.

At the same stage, with `g` odd, the even leaves are a disjoint witness for
the older count as well. Setting the three helped demands back to `0`
makes that even sum equal `q(g - 3)`. Restoring demand `q` on the two even
helped leaves, `0` and `2`, adds exactly `2q`. The odd helped leaf is paid
by a constraint that does not increase the total. This is why the raise over
PR #7025 is `2q` rather than `3q`.

## 5. What this does not prove

- It does not prove `R_ext > q(g - 3)` when the internal sum has rank
  greater than `q`. Each rank-`q` summand contributes at most `q` to each
  block, so several summands can reach rank `2q` and cancel the external
  remainder. PR #7025's bound `q(g - 3)` still applies in that case, because
  the internal rank is nonnegative.
- It does not construct a word of external rank `q(g - 1)`, nor a word of
  total thin rank `780`. The equality tuple is only a solution of the gap
  inequalities.
- It does not replace the consecutive bound `q g` of open PR #7005. That
  bound excludes this internal slot. When `Z = 0` it is the stronger
  statement.
- It does not address one internal gap in every stage, a nested interval, a
  crossed interval, or an interleaved word.
- The `q = 1` census is not a census at `q = 26`. Absence of a search over
  words is not nonexistence on a larger schedule.
- Native transport, frames, and the selected frontier are untouched.

## 6. Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), with the predecessor statements in
PR #5673, PR #5631, and PR #5617. Cinna Davis supplied the controller/simplex
lineage those packages retain. Open PR #7005 proved the consecutive bound
and identified the external gaps. Open PR #7025 computed the internal-gap
coefficient, proved that it meets at most three leaves, and asked whether
those three leaves raise the external bound. This note answers that question
for one matrix of rank at most `q`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

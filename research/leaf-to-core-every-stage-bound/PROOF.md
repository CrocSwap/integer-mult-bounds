# Leaf-to-core blocks raise the every-stage bound to 2q⌈2g/5⌉

Claim type: scoped written proof with exact finite corroboration. No new
kappa, no word, and no selected-frontier change. The selected record stays
`certificates/selected-result.json`, with
`κ = 363005817/100000000000`.

The setting is the every-stage schedule of unpaidmoon's open PR #7050
(`research/g31-q26-every-stage-gap`, head
`d176f84f39ff5678b2bd3dabb53c47099a31584b`) after the factor-1 bound of
Nick Petalas's open PR #7126
(`research/every-stage-gap-rank-factor`, head
`26f8bbfb23feb1f24ba0eb3fb6c4187b331fa057`). This note answers open
question 1 of #7126. It does not replay #7050's schedule analysis or
#7126's block-triangular lemma.

## 1. Cited premises

Characteristic two. The core and each of `g` leaves have dimension
`d = 2q`. Stage `t` has complementary idempotents `P_f`, `P_s` on
`W = core ⊕ leaf t`, extended by zero off `W`, in either half order.
A full call is `(I + x P)(I + e R)` with `x = D + 1` and `e^2 = 0`.
A thin call is `I + e Z`. The first-applied factor is the rightmost
factor, and the stage blocks stand in the order `0, ..., g-1`.

**Hypothesis (#7050, section 1).** Inside every stage the two full calls
occupy the two sides of one gap, and that gap contains only thin maps.
Every other thin map stands in a gap before all stages, between two stage
blocks, or after all stages. Nested intervals and crossed intervals are
outside the hypothesis.

**One stage (#7050, section 2).** With either half first, the two full
calls of one stage contribute `D I_d` on the core-to-leaf block and
`D I_d` on the leaf-to-core block. On the core, `I + x E_k` multiplies by
`D_k`. On leaf `j` it multiplies by `D_j` when `k = j` and by `1`
otherwise. An internal thin map does not change the full-call
contribution.

**Square and core-to-leaf blocks (#7050, sections 3 and 4; #7126).**
For the sum `Z` of the thin maps in the internal gap of stage `t`,

```text
V Z U = B0 + D_t B1 + D_t^2 B2,
B2 = P_s Z P_f.
```

A successful word has `B2 = 0`. Under that condition #7126's Theorem 3
says the own-leaf degree-1 core-to-leaf block has rank at most `rank(Z)`.
The core-to-leaf monomial `M_j = product_{k >= j} D_k` is met by the
internal gaps of stages `j - 1`, `j` and `j + 1` and by the external gaps
after `j` and after `j + 1` completed stages, omitting out-of-range gaps.
Each of those blocks has rank at most the rank of its gap sum. #7126
deduces total thin rank at least `2 q ceil(g / 3)`, and its covering point
shows that these core-to-leaf inequalities alone give nothing higher.

## 2. The leaf-to-core monomials

Compose the one-stage identity of section 1 from the right. The vector
that ends on leaf `j` is still on the core while it passes through every
stage `k < j`, and it is on leaf `j` while it passes through every stage
`k > j`. Stage `j` contributes the factor `D_j`. Stages `k > j` then act
as the identity on leaf `j`. The full calls therefore contribute

```text
N_j = product_{k <= j} D_k
```

times `I_d` on the leaf-`j`-to-core block. The target's pure product is
block diagonal, so that block of the target is zero. In characteristic
two the thin maps must contribute `N_j I_d` there.

Now put the internal gap of stage `t` back. With `B2 = 0`,

```text
pi_j V Z U pi_core
    = pi_j Z P_s pi_core + D_t pi_j Z P_f pi_core    (j != t).
```

On the stage leaf the same expansion, using `F = 0` on `W`, gives the
degree-1 block

```text
pi_t (P_f Z P_f + P_s Z P_s) pi_core
```

and the degree-0 block `pi_t P_f Z P_s pi_core`. The degree-1 block is a
submatrix of `P_f Z_W P_f + P_s Z_W P_s`, so #7126's Corollary 2 bounds
its rank by `rank(Z)`. The other two blocks are compressions of `Z`, so
each has rank at most `rank(Z)` with no square hypothesis.

Outside stage `t`, the input is on the core through every stage `k < t`,
and the output is on leaf `j` through every stage `k > t`. The monomial
on leaf `j` in degree `a` is therefore

```text
sigma(t, j, a)
    = (product_{k < t} D_k) * D_t^a * (D_j if j > t else 1).
```

Comparing exponents with `N_j`, and using that `a >= 2` produces a square,
gives exactly three hits:

- `a = 0`, `j = t - 1`, the block `pi_{t-1} Z P_s pi_core`,
- `a = 1`, `j = t`, the own degree-1 block above,
- `a = 1`, `j = t + 1`, the block `pi_{t+1} Z P_f pi_core`,

omitting a leaf outside `0, ..., g - 1`. No leaf is met by two powers.

An external thin map in the gap after `gamma` completed stages is not
inside a stage polynomial. Its leaf-`j`-to-core monomial is

```text
tau(gamma, j)
    = (product_{k < gamma} D_k) * (D_j if j >= gamma else 1).
```

This equals `N_j` exactly for `j` in `{gamma - 1, gamma}`, intersected
with the leaf range. Each block is the map's own leaf-to-core block, so
its rank is at most `rank(Z)`.

The contributor set of `N_j` is the same as #7126's contributor set of
`M_j`: internal stages `j - 1`, `j`, `j + 1` and external gaps `j`, `j + 1`.
Separate rank counting, with each block at most the rank of its gap, is
the same covering problem #7126 already solved. Its covering point of
value `2 q ceil(g / 3)` is still feasible if the two sides are counted
separately. The leaf-to-core blocks do not raise the bound by themselves.

`verify.py` recomputes these hits from `sigma` and `tau` for every
`g <= 64`. The derivation above is the proof. The `g = 3`, `q = 1` word
in section 5 checks the bare coefficients `N_j I_2` directly for
`B12 = B21 = I` and the first half `P_+`.

## 3. The coupling

**Lemma 1.** Let `P_f` and `P_s` be the stage halves, extended by zero off
`W`, and let `Z` satisfy `P_s Z P_f = 0`. Then

```text
rank(pi_core P_s Z pi_{t-1}) + rank(pi_{t+1} Z P_f pi_core) <= rank(Z).
```

In particular, if the previous-leaf core-to-leaf block already has rank
`rank(Z)`, then `Z P_f = 0` and the next-leaf degree-1 leaf-to-core block
is zero.

*Proof.* Let `r = rank(Z)` and `rho = rank(P_s Z) = dim P_s(im Z)`.
The previous-leaf block is a compression of `P_s Z`, so its rank is at
most `rho`. The square condition puts
`N = Z(im P_f)` inside `ker P_s`. Also `N` lies in `im Z`, so

```text
dim N <= dim(im Z intersect ker P_s) = r - rho
```

by rank-nullity for `P_s` on `im Z`. The next-leaf block is a compression
of `Z P_f`, so its rank is at most `dim N`. ∎

The opposite pair does not add. Section 4 exhibits a map of rank `2q`
whose next-leaf core-to-leaf block and previous-leaf leaf-to-core block
are both `I_{2q}`.

The six internal blocks are otherwise independent in the following weak
sense: each has rank at most `rank(Z)`, and the only joint constraint used
below is Lemma 1. An external gap is charged only through the separate
caps of section 2. No stronger external inequality is required.

## 4. A map that cancels its own leaf-to-core monomial

Take `B12 = B21 = I_q`, `P_f = P_+` and `P_s = P_-`. In the `0`/`I_q`
block alphabet,

```text
P_+ = [[I, I, 0, I], [I, 0, I, 0], [0, I, I, I], [I, 0, I, 0]],
P_- = [[0, I, 0, I], [I, I, I, 0], [0, I, 0, I], [I, 0, I, I]].
```

Let `lambda = [[I, 0], [I, I]]` on the two core halves and

```text
Z = iota_core ∘ lambda ∘ pi_core ∘ P_-.
```

Block multiplication gives

```text
Z = [[0, I, 0, I], [I, 0, I, I], [0, 0, 0, 0], [0, 0, 0, 0]].
```

Every factor is `0` or `I_q`, so the `q = 1` check is the general check.
`Z P_+ = 0`, hence `P_- Z P_+ = 0` and the next-leaf leaf-to-core block
is zero. The own degree-1 leaf-to-core block is `I_{2q}`. The own
degree-1 core-to-leaf block is `[[I, I], [I, 0]]`, which has rank `2q`
and is not `I_{2q}`. Both degree-0 own blocks, `P_+ Z P_-`, are `I_{2q}`.
The image of `Z` is the whole core. On a core vector,

```text
pi_core P_+ = [[I, I], [I, 0]],    pi_core P_- = [[0, I], [I, I]],
```

and these are inverses of each other in characteristic two. A core vector
is in the image, so both neighbour core-to-leaf blocks can be made equal
to `I_{2q}` without raising the rank. The core outputs of `P_-` on the
core basis are independent, so previous-leaf rows that are a function of
the core output can make the previous-leaf leaf-to-core block `I_{2q}`
without raising the rank. The same rows stay zero on `im P_+`.

Thus one internal map of rank `2q` can meet leaves `t - 1`, `t` and
`t + 1` at core-to-leaf rank `2q` and can cancel its own leaf-to-core
monomial, and the previous leaf's leaf-to-core monomial, by contributing
exactly `I_{2q}` on those blocks. It cannot cancel the next leaf's
leaf-to-core monomial. Lemma 1 says this is the general obstruction, not
a defect of the example: full rank on the previous core-to-leaf block
forces that next block to vanish.

The degree-0 own blocks are also `I_{2q}`. Their monomial on the own leaf
is `product_{k < t} D_k`, which is not `N_t`. The map cancels the targeted
degree-1 monomial and emits another monomial. It is not a successful word.

## 5. The joint bound

Work in units of `2q`. For a gap of unit rank, the constraints of sections
2 and 3 allow any subset of the four uncoupled internal blocks

```text
co = own core-to-leaf,   lo = own leaf-to-core,
cn = next core-to-leaf,  lp = previous leaf-to-core,
```

together with at most one of

```text
cp = previous core-to-leaf,   ln = next leaf-to-core.
```

Section 4 realizes `{co, lo, cp, lp, cn}` at every `q`. The inequality
system also allows the sets that use `ln` instead of `cp`; this note does
not exhibit those sets by a matrix.

**Theorem 2.** Under the hypotheses of sections 1 to 3, the total thin
rank `R` of a successful every-stage word satisfies

```text
R >= 2 q ceil(2 g / 5).
```

*Proof.* Give leaf `j` weight `yC_j = 1` when `j ≡ 0 (mod 5)` and
`yL_j = 1` when `j ≡ 2 (mod 5)`, and weight 0 otherwise, with an
out-of-range index reading as 0. The total weight is

```text
ceil(g / 5) + ceil((g - 2) / 5).
```

For `g = 5m + r` this equals `ceil(2g / 5)`: both sides are `2m`,
`2m + 1`, `2m + 1`, `2m + 2`, `2m + 2` for `r = 0, 1, 2, 3, 4`.

An internal stage `t` can collect at most

```text
yC_t + yL_t + yC_{t+1} + yL_{t-1} + max(yC_{t-1}, yL_{t+1}),
```

because `cp` and `ln` cannot both be paid in full. For each residue of
`t` that quantity equals 1:

| `t mod 5` | positive terms | load |
| --- | --- | --- |
| 0 | `yC_t` | 1 |
| 1 | `max(yC_{t-1}, yL_{t+1})` | 1 |
| 2 | `yL_t` | 1 |
| 3 | `yL_{t-1}` | 1 |
| 4 | `yC_{t+1}` | 1 |

An external gap after `gamma` stages meets only the four side-weights on
leaves `gamma - 1` and `gamma`. Those two leaves are consecutive. The
only residues carrying weight are `0` and `2`, and a leaf never carries
both, so a consecutive pair carries total weight at most 1. This uses
only the separate rank caps. It does not need a further external
inequality.

Every demand `yC_j` or `yL_j` is a copy of the inequality "the blocks
that meet `M_j` or `N_j` have total rank at least `2q`". A gap of rank
`r` can collect at most `r` units of this weight. Summing gives
`R >= 2 q ceil(2g / 5)`. ∎

The same inequalities admit the following point of value `ceil(2g / 5)`.
On each complete group of five leaves, stage `5k + 1` pays
`{co, lo, cp, lp, cn}` and stage `5k + 3` pays `{co, lo, lp, cn, ln}`.
The remainder `r = g mod 5` at `s = 5 floor(g / 5)` is paid by

- `r = 1`: stage `s` pays `{co, lo}`,
- `r = 2`: stage `s` pays `{co, lo, cn, ln}`,
- `r = 3`: stage `s` pays `{co, lo, cn, ln}` and stage `s + 2` pays
  `{co, lo, cp, lp}`,
- `r = 4`: stage `s` pays `{co, lo, cn, ln}` and stage `s + 3` pays
  `{co, lo, cp, lp}`.

Each leaf is hit on both sides, no stage pays both `cp` and `ln`, and the
number of stages used is `ceil(2g / 5)`. These inequalities alone therefore
give nothing above `2 q ceil(2g / 5)`. That is a statement about the
inequalities. The sets that contain `ln` are not exhibited by a matrix,
and the point is not a word.

Since `2g / 5 >= g / 3`, one has `ceil(2g / 5) >= ceil(g / 3)`. For
`g >= 15`, `2g / 5 >= g / 3 + 1`, so the new ceiling is at least one
larger. For `1 <= g <= 14` the two ceilings agree exactly at
`g in {1, 2, 4, 5, 7, 10}`. At `g = 31` and `q = 26`,

```text
2 * 26 * ceil(31 / 3) = 572,    2 * 26 * ceil(62 / 5) = 676.
```

#7126 proves 572. Five thin maps of rank 26 have total rank 130.

## 6. Finite corroboration

`verify.py` uses the standard library only and raises `SystemExit` on
failure, including under `python -O`.

- The `0`/`I` witness of section 4: idempotence and complementarity of
  the halves, `Z P_+ = 0`, own leaf-to-core block `I`, own core-to-leaf
  block `[[1, 1], [1, 0]]`, both degree-0 own blocks `I`, and both
  core projections invertible.
- A direct `g = 3`, `q = 1` word with `B = I` and first half `P_+`. The
  bare word has core-to-leaf block `M_j I_2` and leaf-to-core block
  `N_j I_2` for every leaf. Installing the witness at stage 1, with
  neighbour columns and previous-leaf rows chosen inside the image,
  contributes `I_2` on `M_0`, `M_2`, `N_0` and `N_1`, contributes
  `[[1, 1], [1, 0]]` on `M_1`, contributes nothing on `N_2`, and leaves
  the degree-0 own leaf-to-core monomial `D_0 I_2` on leaf 1. The map has
  rank 2.
- Every rank-one map on the eight coordinates of the core, leaf `t` and
  the two neighbours: `255 * 255 = 65025` maps. Whenever
  `P_s Z P_f = 0`, the previous core-to-leaf rank plus the next
  leaf-to-core rank is at most 1. The map with row support `65` and column
  support `17` has both ranks equal to 1 and a nonzero square; it is the
  failure control.
- Three hundred seeded rank-bounded maps on the same eight coordinates.
  Every square-free sample obeys the same inequality. This sample is
  corroboration, not a census.
- For every `g <= 64`, the monomial hits, the dual load, the feasible
  point and the comparison with `ceil(g / 3)`. The ceilings agree only
  for `g in {1, 2, 4, 5, 7, 10}`. A dual pattern with both sides of leaf
  0 is rejected.

## 7. What this does not prove

- It does not prove #7050's schedule analysis or #7126's rank lemma.
  Theorem 2 is conditional on sections 1 to 3.
- It does not prove that every successful word needs total thin rank
  `2 q ceil(2g / 5)` outside this schedule. Nested and crossed intervals
  stay outside the hypothesis.
- It does not replace the one-gap bound `q(g - 3) = 728` of open PR #7025
  or the consecutive bound `q g = 806` of open PR #7005.
- It does not show that `2 q ceil(2g / 5)` is attained. The feasible point
  is a point of the rank inequalities. The witness of section 4 cancels
  four targeted blocks and emits other monomials, including a degree-0
  own block equal to `I_{2q}`.
- For `g in {1, 2, 4, 5, 7, 10}` the new expression equals #7126's number.
  This argument does not raise those six values.
- No `g = 31`, `q = 26` word is constructed. No kappa changes.

## 8. Credit

unpaidmoon's #7050 supplies the schedule, the square condition, the
one-stage off-block identities, the core-to-leaf monomials and the
factor-2 bound. Nick Petalas's #7126 supplies the factor-1 lemma, the
bound `2 q ceil(g / 3)`, the covering point and the question answered
here. unpaidmoon's #7025 and #7005 supply the neighbouring bounds, which
are not replaced. The paired-star contract and the commuting map-count
are from Ali Romman's #5747, with #5673, #5631 and #5617. Cinna Davis
supplied the controller and simplex lineage those packages retain.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.

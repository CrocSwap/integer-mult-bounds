# Two rank-q maps in one internal gap

This is a proof in characteristic two under the hypotheses below. It is not a
search over words and not a heuristic. The exhaustive check at `q = 1` is a
finite census of one 8-dimensional matrix domain. It supports the proof and
does not replace it.

No new kappa is claimed. The selected frontier stays
`363005817/100000000000 = 0.00363005817`.

## 1. Question

Use the paired-star one-gap schedule of open PR #7025, with the three core
blocks named in open PR #7053. The core and each leaf have dimension `d = 2q`.
Stage `t` has complementary half projectors `P_f` and `P_s`. In the
eigenbasis of open PR #7025 their off-diagonal blocks are arbitrary `q` by
`q` matrices `B12` and `B21`. A thin map is `I + e Z` with `e^2 = 0`. The
single internal gap may contain several thin maps. Their sum is what enters
the coefficient, but the rank bound below is a bound on each map, not on the
sum.

Write `N`, `P` and `O` for the three helped core blocks of a matrix `Z`:

- `N = pi_core P_f Z` on leaf `t + 1`, when that leaf exists,
- `P = pi_core P_s Z` on leaf `t - 1`, when that leaf exists,
- `O = pi_core (P_f Z P_f + P_s Z P_s)` on leaf `t`.

Open PR #7053 proved that one matrix of rank at most `q` with
`P_s Z P_f = 0` has all three ranks at most `q`, and therefore external rank
at least `q(g - 1)`. Its first open question is the one answered here.

**Question.** Do there exist two matrices `Z_1`, `Z_2`, each of rank at most
`q` and each satisfying `P_s Z_i P_f = 0`, such that every helped block of
`Z_1 + Z_2` has rank `2q`?

The first step requested by that question is to add two copies of the
rank-`q` witness on complementary core coordinates. Section 3 records that
this step does not reach rank `2q`. That failure is not an unrestricted
nonexistence claim. Section 4 gives an explicit pair that does reach rank
`2q`, for invertible off-diagonal blocks. Section 5 records what that does
to the external count: the uniform lift to `q(g - 1)` does not survive, and
`q(g - 3)` still applies.

## 2. The projector image caps the outside blocks

Order the stage coordinates as `(c+, c-, s+, s-)`, each of dimension `q`.
For `P_+` the core output of a stage vector is

```text
c+ = z_c+ + B12 z_c- + B12 z_s-,
c- = B21 z_c+ + B21 z_s+.
```

Thus `c-` lies in `im B21`. Conversely, every pair `(t+, B21 u)` occurs:
set `z_c+ = t+`, `z_s+ = u + t+`, and `z_c- = z_s- = 0`. In characteristic
two the minus coordinate is `B21 u` and the plus coordinate is `t+`.
Therefore

```text
im(pi_core P_+) = C+ ⊕ im(B21),
rank(pi_core P_+) = q + rank(B21).
```

The same expansion for `P_-` gives

```text
im(pi_core P_-) = im(B12) ⊕ C-,
rank(pi_core P_-) = q + rank(B12).
```

The outside blocks factor through these maps. For any matrices in the gap,
and either half order,

```text
rank(N) <= q + rank(B21 of P_f's sign),
rank(P) <= q + rank(B12 of P_s's sign).
```

In particular, if `P_f = P_+` and `rank(B21) < q`, then no choice and no
number of internal matrices can make the next-leaf block have rank `2q`.
The symmetric statement holds for `B12` and the previous-leaf block. Both
caps are statements about the image of a projector. They do not use
`P_s Z P_f = 0`.

## 3. Complementary copies of the rank-q witness

The witness of open PR #7053 uses `B12 = B21 = 0` and `P_f = P_+`. For each
index `i` it writes `e_{c+,i} + e_{c-,i}` from the three sources
`n+,i`, `p-,i` and `s-,i`. Each of its three blocks has rank `q`, and
`P_- W P_+ = 0`.

Two copies on complementary coordinates do not reach rank `2q`.

- Move the three sources to the other leaf half, `n-,i`, `p+,i` and
  `s+,i`, and keep the same diagonal image. Call this copy `W'`. With
  `B = 0`, `im P_+` is the set of stage vectors with `c- = s- = 0`. The
  functional of `W'` reads `s+`, which does not vanish there, and the image
  `e_{c+} + e_{c-}` is not in `im P_+`. So `P_- W' P_+` is not zero. The sum
  `W + W'` fails the same equation. Its next-leaf and previous-leaf blocks
  each have rank `q`, not `2q`: both copies write the diagonal vector, and
  `pi_core P_+` keeps only the plus half.
- Split the image onto the two core halves. The plus copy writes only
  `e_{c+,i}` from the original sources and does satisfy the square
  equation. The minus copy writes only `e_{c-,i}` from the shifted sources
  and does not. The sum of the two splits still has every helped block of
  rank less than `2q`.

Section 2 already forbids every repair that keeps `B12 = B21 = 0`. The
next-leaf block of an arbitrary sum then has rank at most `q`. Adding
copies, complementary or otherwise, cannot make every helped block rank
`2q` for this choice of halves.

## 4. An explicit pair whose blocks are the identity

The obstruction in section 2 disappears when `B12` and `B21` are invertible.
Take both equal to `I_q`, over an arbitrary field of characteristic two.
The same formulas with scalar `1` give the `q = 1` pair, and the matrices
below are the direct sum of that pair across the `q` indices. Because
`I_q` does not mix indices, there are no cross terms. It is therefore
enough to check one index and then reassemble.

Write `e_sigma` for the corresponding basis vector of that index. All
additions are characteristic two.

### Plus half applied first

```text
Z1 = e_{c+} (e_{c-} + e_{s-} + e_{p-} + e_{n+})^T,
Z2 = (e_{c+} + e_{c-}) (e_{c+} + e_{c-} + e_{s+} + e_{p+} + e_{n+} + e_{n-})^T.
```

A vector of `im P_+` has stage coordinates `(x, y, x + y, y)`. The stage
part of the functional of `Z1` is `y + y = 0`. The stage part of the
functional of `Z2` is `x + y + (x + y) = 0`. Both maps kill `im P_+`, so
`P_- Z_i P_+ = 0`.

The core output of `P_+` on these images is

```text
pi_core P_+ e_{c+} = (1, 1),
pi_core P_+ (e_{c+} + e_{c-}) = (0, 1).
```

Leaf `t + 1` has coordinates `(n+, n-)`. The sum sends `n+` to
`(1, 1) + (0, 1) = (1, 0)` and `n-` to `(0, 1)`. That block is `I_2`.

The core output of `P_-` is

```text
pi_core P_- e_{c+} = (0, 1),
pi_core P_- (e_{c+} + e_{c-}) = (1, 0).
```

Leaf `t - 1` has coordinates `(p+, p-)`. The sum sends `p+` through `Z2`
to `(1, 0)` and `p-` through `Z1` to `(0, 1)`. That block is `I_2`.

For the own leaf, both maps kill `im P_+`, so
`P_+ Z_i P_+ = 0` and the degree-1 block is `pi_core P_- Z_i P_-`. On the
own-leaf basis,

```text
P_- e_{s+} = e_{c-} + e_{s-},
P_- e_{s-} = e_{c+} + e_{s+} + e_{s-}.
```

`Z1` reads `c-` and `s-`, so it kills the first of these vectors and sends
the second to `e_{c+}`. Then `pi_core P_- e_{c+} = (0, 1)`. `Z2` reads
`c-` but not `s-`, so it sends the first vector to `e_{c+} + e_{c-}` and
kills the second. Then `pi_core P_-` of that image is `(1, 0)`. The own
block is `I_2`.

### Minus half applied first

```text
Z1 = e_{c+} (e_{c+} + e_{s+} + e_{p+} + e_{n-})^T,
Z2 = (e_{c+} + e_{c-}) (e_{c-} + e_{s+} + e_{s-} + e_{p+} + e_{p-} + e_{n+})^T.
```

A vector of `im P_-` has stage coordinates `(x, y, x, x + y)`. Both stage
functionals vanish on it: `x + x = 0`, and `y + x + (x + y) = 0`. Thus
`P_+ Z_i P_- = 0`. The same three expansions as above, with the two
projectors exchanged, give `I_2` on each helped block. The registered
checker multiplies the matrices rather than trusting the exchange.

### Every q

Index the direct sum by `i = 0, ..., q - 1`, using `B12 = B21 = I_q`.
Each `Z_j` has rank `q`: the private next-leaf column of index `i` produces
a distinct image vector, and those `q` vectors are independent. The three
blocks of the sum are `I_q` on the plus coordinates and `I_q` on the minus
coordinates, hence `I_{2q}`. Each block has rank `2q`. Each factor has rank
`q`, so the sum has rank `2q` as well: the identity block forces the lower
bound, and the sum of two rank-`q` maps forces the upper bound.

The same local matrices serve an endpoint stage. Whichever of the three
leaves exist, the corresponding block is still `I_{2q}`.

One map is not enough. Each factor has rank `q`, and the one-map theorem of
open PR #7053 caps each of its blocks by `q`. The checker records that
these explicit summands meet that cap.

## 5. The external count

On a successful word, leaf `j` still requires `A_j + B_j = I_d`, where
`B_j` is the internal block when leaf `j` is helped and is zero otherwise,
and `A_j` is the sum of the external blocks in gaps `j` and `j + 1`. Rank
subadditivity gives

```text
r_j + r_{j + 1} >= 2q - rank(B_j).
```

Open PR #7025 never uses an upper bound on the internal blocks. It drops
the helped leaves and keeps at least `g - 3` leaves of demand `2q`. That
argument still gives

```text
R_ext >= q(g - 3)
```

for every placement, whether or not the two maps of section 4 are used.

The uniform lift of open PR #7053 is a different count. It needs demand at
least `q` on every helped leaf, which is the one-map cap. Section 4 meets
the leaf equation on each helped leaf by `B_j = I_d` and `A_j = 0`. Those
demands are zero, so that lift does not apply to every placement of two
rank-at-most-`q` maps.

The parity count with those zero demands is still exact, and it is not
uniformly `q(g - 3)`.

Let the helped leaves be the existing members of `{t - 1, t, t + 1}`. They
form one consecutive block. The unhelped leaves split into a left run of
length `a` and a right run of length `b`. A leaf in the left run uses only
gaps `0, ..., a`. A leaf in the right run uses only gaps from the first
right leaf onward. Those two gap sets are disjoint, so a feasible tuple is
a cover of each run separately. A path of `m` edges has an edge cover by
`ceil(m / 2)` vertices: select the right endpoint of edges `0, 2, 4, ...`.
The resulting gaps have weight `2q`, and the total external rank is

```text
2q (ceil(a / 2) + ceil(b / 2)).
```

This equals the heavier parity of the demands. The left run is the initial segment `0, ..., a - 1`, so it contributes
`ceil(a / 2)` even leaves and `floor(a / 2)` odd leaves. Write `U_even` and
`U_odd` for the unhelped counts, and write `s` for the first right-hand
leaf. Then `s = t + 2` when `t` is interior, `s = 2` when `t = 0`, and
there is no right run when `t = g - 1`.

- If `t` is even and interior, then `a = t - 1` is odd and `s` is even.
  The left run has `t / 2` even leaves and `t / 2 - 1` odd leaves. The
  right run has `ceil(b / 2)` even leaves. Hence `U_even` equals
  `t / 2 + ceil(b / 2)` and is strictly larger than `U_odd`. The cover has
  the same number of gaps.
- If `t` is odd and interior, then `a = t - 1` is even and `s` is odd.
  Each side of the left run has `(t - 1) / 2` leaves, and the right run has
  `ceil(b / 2)` odd leaves. Hence `U_odd` equals
  `(t - 1) / 2 + ceil(b / 2)` and is at least `U_even`. The cover matches
  `U_odd`. A helped block that touches an end is the same arithmetic with
  `a = 0` or `b = 0`, in whichever of the two bullets has the parity of `t`.
- If `t = 0` or `t = g - 1`, one run is empty and the other has length
  `g - 2`. The cover has `ceil((g - 2) / 2)` gaps, which is the heavier of
  the two unhelped counts on an initial or final segment of that length.

In every case

```text
ceil(a / 2) + ceil(b / 2) = max(U_even, U_odd).
```

The heavier parity sum of the demands is `2q` times that maximum. The lower
bound is the disjoint sum of one parity's leaf inequalities, so the tuple
is sharp for the inequalities. It is not a word.

The closed form is:

- if `g` is odd and `t` is even, `R_ext >= q(g - 1)`, and the tuple meets it,
- if `g` is odd and `t` is odd, `R_ext >= q(g - 3)`, and the tuple meets it,
- if `g` is even, `R_ext >= q(g - 2)` for every stage, and the tuple meets it.

The even-stage bound for odd `g` does not need section 4. An even stage
helps only one even leaf, so the remaining `(g - 1) / 2` even leaves each
demand `2q` and already sum to `q(g - 1)`, for any internal matrices. Full
block rank makes that bound sharp as an inequality. It does not remove it.

At `g = 31` and `q = 26` the two odd-`g` numbers are `780` and `728`. The
uniform claim "every placement forces external rank `780`" is the lift that
does not survive. The placement-dependent even-stage obligation `780`
remains, and every odd stage is feasible for the inequalities at `728`.

## 6. The q = 1 census

The three helped leaves and the core are eight coordinates over `F_2`.
Every rank-1 matrix is uniquely an outer product of two nonzero vectors, so
there are `(2^8 - 1)^2` of them. Rank 0 is the zero matrix. For each of the
four scalar pairs `(B12, B21)` and both half orders, the projector has rank
2. Its image is a plane in the stage and is zero on the other four
coordinates, so `2^2 * 2^4 - 1 = 63` nonzero vectors have stage part in the
image. The annihilator of that plane in the dual of `F_2^8` has
`2^6 - 1 = 63` nonzero functionals. A rank-1 map `x y^T` satisfies
`P_s Z P_f = 0` exactly when the stage part of `x` lies in the image or
`y` kills the image. The admissible count per half is

```text
63 * 255 + (255 - 63) * 63 = 28161.
```

The checker enumerates the whole domain. Under the square equation every
own-leaf block has rank at most 1. The two identity seeds of section 4 sit
in the domain, and for one half the same enumeration agrees entrywise with
dense multiplication. This is a census of that 8-by-8 family. It is not a
census of words and not a proof at `q = 26`.

## 7. What this does not prove

- It does not construct a paired-star word, of external rank `728` or of
  any other rank. The identity blocks are local. The monomial transport
  that carries them to the target is not rebuilt here.
- It does not say that every legal half admits block rank `2q`. Section 2
  forbids it whenever the relevant off-diagonal block is singular.
- It does not say that every pair of rank-at-most-`q` maps has block rank
  `2q`. Most pairs do not. The claim is existence.
- It does not replace the one-map theorem of open PR #7053, the dropped-leaf
  bound of open PR #7025, or the every-stage theorems of open PRs #7050 and
  #7126.
- A failed complementary copy is not nonexistence of a `2q` sum. Section 4
  is the existence proof, and it uses a different half from the witness.
- Native transport, frames, and the selected frontier are untouched.

## 8. Credit

The one-gap schedule and the bound `q(g - 3)` are open PR #7025. The three
blocks, the one-map cap, the rank-`q` witness, and the question are open PR
#7053. The even-stage parity count uses only the helped-leaf support proved
there. The paired-star contract and the commuting map-count are from PR
#5747 (Ali Romman), with the predecessor statements in PR #5673, PR #5631,
and PR #5617. Cinna Davis supplied the controller and simplex lineage those
packages retain. Open PR #7005 is the consecutive-halves bound and is not
rerun. Open PR #7126 is the every-stage factor and is not rerun.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

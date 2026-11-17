# The own-leaf degree-1 block has rank at most rank(Z)

Claim type: scoped written proof with exact finite corroboration. No new
kappa, no word, no selected-frontier change.

The setting is the every-stage schedule of unpaidmoon's open PR #7050
(`research/g31-q26-every-stage-gap`, head
`d176f84f39ff5678b2bd3dabb53c47099a31584b`). Sections 1 and 2 are
self-contained linear algebra. Section 3 uses #7050's schedule analysis as a
cited premise. That analysis is not replayed here.

## 1. The rank lemma

**Lemma 1.** Let `F` be a field, `W` a finite-dimensional `F`-space, and
`P`, `Q` idempotents of `W` with `P + Q = I`. Let `Z` be an endomorphism of
`W` with `Q Z P = 0`. Then

```text
rank(P Z P + Q Z Q) = rank(P Z P) + rank(Q Z Q) <= rank(Z).
```

*Proof.* `P Q = Q P = 0` because `Q = I - P`. From `Q Z P = 0`,

```text
Z P = (P + Q) Z P = P Z P,        Q Z = Q Z (P + Q) = Q Z Q.
```

Put `U = im Z`. The restriction of `Q` to `U` has image
`Q(U) = im(Q Z) = im(Q Z Q)` and kernel `U ∩ ker Q = U ∩ im P`. The image
of `P Z P = Z P` lies in `im Z` and in `im P`, so it lies in that kernel.
Rank-nullity on `Q|_U` gives

```text
rank(Z) = dim Q(U) + dim(U ∩ im P) >= rank(Q Z Q) + rank(P Z P).
```

For the equality, write `M = P Z P + Q Z Q`. Its image lies in
`im(P Z P) + im(Q Z Q)`, and this sum is direct because
`im P ∩ im Q = 0`. Conversely `M P = P Z P` and `M Q = Q Z Q`, so both
images lie in `im M`. ∎

In a basis adapted to `W = im P ⊕ im Q` the hypothesis says that `Z` is
block upper triangular, `M` is its block diagonal, and the lemma is the
statement that a block triangular matrix has rank at least the sum of the
ranks of its diagonal blocks. No property of `P` and `Q` beyond
`P^2 = P`, `Q = I - P` is used, and the characteristic is arbitrary.

**Corollary 2.** Under the hypotheses of Lemma 1, every submatrix of
`P Z P + Q Z Q`, in any basis, has rank at most `rank(Z)`.

The hypothesis `Q Z P = 0` is needed. Without it the block diagonal of a
rank-one matrix can have rank two, which is the factor 2 that #7050 proves.

## 2. The own-leaf block of one stage

Use the stage of #7050, section 1. The core and the stage leaf have
dimension `d = 2q`, the stage space is `W = core ⊕ leaf`, and the two
halves are

```text
P_+ = [[A+B, B], [B, A+B]],    P_- = [[A'+B, B], [B, A'+B]],
A = diag(I_q, 0),  A' = I + A,  B = [[0, B12], [B21, 0]],
```

over a field of characteristic two, with `B12`, `B21` arbitrary. Since
`A B + B A = B`, both are idempotent and `P_+ + P_- = I_W`.

Let `V` be the whole space, core plus all leaves, and let `Z` be an
endomorphism of `V`. Extend `P_f`, `P_s` (the two halves in either order)
by zero outside `W`, and let `Z_W` be the compression of `Z` to `W`. Then
`P_s Z P_f = P_s Z_W P_f`, and

```text
pi_core (P_f Z P_f + P_s Z P_s) pi_leaf = pi_core (P_f Z_W P_f + P_s Z_W P_s) pi_leaf.
```

This is the own-leaf degree-1 core-to-leaf block of #7050, section 3. On
`W`, in characteristic two, it also equals the two-sandwich form
`pi_core (Z_W P_f + P_s Z_W) pi_leaf`, because the two expressions differ
by `2 P_s Z_W P_f`.

**Theorem 3.** For every half width `q >= 1`, every `B12`, `B21`, either
half order and every `Z` with `P_s Z P_f = 0`,

```text
rank( pi_core (P_f Z P_f + P_s Z P_s) pi_leaf ) <= rank(Z_W) <= rank(Z).
```

*Proof.* Apply Corollary 2 on `W` with `P = P_f`, `Q = P_s`, `Z = Z_W`.
The block is a submatrix of `P_f Z_W P_f + P_s Z_W P_s`. A compression
does not raise rank. ∎

This answers open question 1 of #7050: the factor is 1 for every `q`.

**Sharpness.** Take `B = 0` and let `Z` be the identity from the leaf
into the core, `Z = [[0, I_d], [0, 0]]` on `W`. Then `P_s Z P_f = 0` because
`A A' = 0`, and `Z P_f + P_s Z = Z`. The block is `I_d` and
`rank(Z) = d = 2q`. So equality holds at every `q`, and 1 is the best
constant.

## 3. Consequence on the every-stage schedule

**Cited premise (#7050, sections 2 to 4).** In the every-stage schedule,
for each leaf `j`, the thin maps contribute `M_j I_d` on the core-to-leaf-`j`
block, where `M_j = product_{k>=j} D_k` and `d = 2q`. The monomial `M_j`
on leaf `j` receives contributions from exactly these gaps:

- the internal gap of stage `j`, through its own-leaf degree-1 block,
- the internal gap of stage `j+1`, through `pi_core P_s Z pi_j`,
- the internal gap of stage `j-1`, through `pi_core P_f Z pi_j`,
- the external gaps after `j` and after `j+1` completed stages, through
  the core-to-leaf block of the map itself,

with out-of-range stages omitted. Each contribution is evaluated on the
sum `Z` of the thin maps in that gap, and a successful word has
`P_s Z P_f = 0` in every internal gap.

The exponent comparison behind the list is recomputed in `verify.py` from
the formulas `lambda(t,j)` and `mu(gamma,j)` for every `g <= 64`. The
derivation of those formulas, and of the square condition, is #7050's.

**Theorem 4.** Under the cited premise, the total thin rank `R` of a
successful every-stage word satisfies

```text
R >= 2 q ceil(g / 3).
```

*Proof.* Fix a leaf `j`. By Theorem 3 the own-leaf block has rank at most
`rank(Z)` for the gap sum `Z` of stage `j`. The other four blocks are
compressions of `P_s Z`, `P_f Z` or of the map, so each has rank at most
the rank of its gap sum. The rank of a gap sum is at most the sum `r(G)`
of the ranks of the thin maps in the gap `G`. Rank is subadditive and
`I_d` has rank `2q`, so

```text
2q <= sum of r(G) over the gaps G that contribute to leaf j.
```

Take the leaves `j = 0, 3, 6, ...` below `g`. There are `ceil(g/3)` of
them. Two of them differ by at least 3, so their contributing gap sets are
disjoint: internal gaps `j-1, j, j+1` and external gaps `j, j+1`. Adding
the inequalities charges every thin map at most once. ∎

At `g = 31`, `q = 26` the bound is `52 * 11 = 572`. #7050 proves 403, and
its predicted factor-1 weight count would give `ceil(2 q g / 3) = 538`.
The disjoint-leaf count is never smaller: `2 q ceil(g/3) >= 2 q g / 3`.
Five thin maps of rank 26 have total rank 130.

**What rank counting cannot do.** The inequalities of the proof form a
covering problem: nonnegative numbers `r(G)` with one constraint per leaf.
Placing `2q` on the internal gaps of stages `1, 4, 7, ...` (and on stage
`g-1` when `g ≡ 1 mod 3`) satisfies every constraint with total
`2 q ceil(g/3)`. So these inequalities alone give nothing above
`2 q ceil(g/3)`. That is a statement about the inequalities. It is not a
word, and it does not show that total rank `2 q ceil(g/3)` is attained.
At `q = 1` an exhaustive census finds rank-one maps satisfying the square
condition whose three blocks, on leaves `t-1`, `t`, `t+1`, all have rank
one, so no single map's three weights can be lowered by a rank argument.

## 4. Finite corroboration

`verify.py` uses the standard library only and raises on any failure.

- `q = 1`, exhaustive: all 65,536 matrices `Z` of size 4 over `F_2`, all
  four `B`, both half orders, 524,288 cases. Exactly 32,768 satisfy
  `P_s Z P_f = 0`. On each, the pinching equals the two-sandwich form, its
  rank is additive and at most `rank(Z)`, and the own-leaf block has rank
  at most `rank(Z)`.
- Control: among the 1,800 rank-one cases, 168 have own-leaf block rank 2.
  Each violates the square condition.
- `q = 2, 3, 4`: 4,500 seeded random cases on the actual stage halves with
  random `B12`, `B21`, both orders.
- Lemma 1 for random complementary idempotents over `F_2`, `F_3`, `F_5`,
  `F_7` in dimensions 4 and 6: 3,200 seeded cases, each with a random
  submatrix.
- Sharpness witness at `q = 1, 2, 3, 5, 26`, both orders.
- `q = 1`, exhaustive over 30,600 rank-one maps with columns on the stage
  and the two neighbouring leaves: 1,170 satisfy the square condition and
  meet all three leaves at rank one.
- Packing: for every `g` from 1 to 64 the contributor sets are recomputed
  from the monomials, the chosen leaves are pairwise disjoint, and the
  covering point has the same value. Spacing-two leaves and a thinned
  cover are rejected.

The random cases are corroboration. The proof is sections 1 to 3.

## 5. What this does not prove

- It does not prove #7050's schedule analysis, monomial formulas or square
  condition. Theorem 4 is conditional on them.
- It does not bound nested or crossed stage intervals, which are outside
  the schedule hypothesis.
- It does not replace the one-gap bound `q(g-3) = 728` of open PR #7025 or
  the consecutive bound `q g = 806` of open PR #7005. Those are larger
  numbers on smaller schedule families.
- It does not use the leaf-to-core blocks, and it does not show that 572
  is attained.
- No `g = 31`, `q = 26` word is constructed or excluded outside this
  schedule.

## 6. Credit

unpaidmoon's #7050 supplies the schedule, the square condition, the
degree-1 block, the monomial comparison, the factor-2 estimate, the
`q = 1` census observation and the question answered here. unpaidmoon's
#7025 and #7005 supply the one-gap and consecutive bounds. The
paired-star contract and the commuting map-count are from Ali Romman's
#5747 with its predecessors #5673, #5631 and #5617, and Cinna Davis
supplied the controller and simplex lineage those packages retain. The
rank inequality for block triangular matrices is classical.

# One interleaved g=31, q=26 word misses the paired-star endpoint

This is a proof for one call order and one legal noncommuting frame.
It is not a search, not an exhaustive census of orders or frames, and not
a claim that every interleaved word fails. No new kappa is claimed. The
selected frontier stays `781451/250000000`.

## 1. Contract

Use the paired-star contract in `research/coupled31-chronology/PROOF.md` at
base `17469fff78c22941280f04d39dc5a1faee09c840`. The field has characteristic
2. There are `g` leaves and port dimension `q`, with block size `d = 2q`.
A legal half on a stage has the block form

```text
P = [[A+B, B], [B, A+B]],    R = [[A, A], [A, A]],
```

with `A^2 = A` and `AB + BA = B`. The other half uses `A' = I + A` and the
same `B`. A full call is `(I + x P)(I + e R)` with `x = D + 1` and `e^2 = 0`.
Thin calls are `I + e Z`. The variables `D_j` are independent and nonzero
when an inverse is required. The target pure factor is `product_j (I + x_j E_j)`,
where `E_j` is the identity on the core and on leaf `j`. The normalized
coefficient in `(I + e S) Pure` finishes at `I`.

The first-applied factor is the rightmost factor. Thin maps do not change
the pure factor.

## 2. The pattern and the frame

Take `g = 31` and `q = 26`. On every stage use the same legal frame

```text
A = diag(I_q, 0_q),    B e_q = e_0,    B e_i = 0 for i ≠ q.
```

Here `e_0, ..., e_{q-1}` are the top port coordinates and `e_q, ..., e_{2q-1}`
the bottom ones. Then `AB + BA = B`, both halves are complementary
projectors, and the projectors of two distinct stages do not commute:
their off-diagonal blocks meet on the core. The same projectors with the
two halves of each stage kept adjacent do meet the pure target. The failure
below is the interleaving, not an illegal frame.

The full-call order is every first half, in stage order `0, ..., 30`, and
then every second half in the same stage order. Any finite list of thin
maps may sit in any of the gaps. In particular the five maps tested below
sit together between the two blocks of halves. Every stage has other full
calls between its halves, so the adjacent-halves hypothesis of the
consecutive schedule is not in force.

## 3. The pure product on an invariant plane

Set `x_j = 0` for every `j ≥ 2`. Those factors are the identity, so the
pure product is the two-stage cross

```text
(I + x_1 P'_1)(I + x_0 P'_0)(I + x_1 P_1)(I + x_0 P_0).
```

The target specializes to `(I + x_1 E_1)(I + x_0 E_0)`.

Let `V = span{e_0, e_q}`. Both `A` and `B` preserve `V`, and they preserve
the complementary coordinates. Every stage projector is built from `A` and
`B` on the core and one leaf, so the pure product preserves the copy of `V`
in every region. The target scales every coordinate of a region by the same
scalar, so it preserves those copies as well. A mismatch on the copies of
`V` in the core, leaf 0, and leaf 1 is a mismatch of the full `q = 26`
operators.

On `V`, with basis `(e_0, e_q)`, the restrictions are

```text
A|_V = [[1, 0], [0, 0]],    B|_V = [[0, 1], [0, 0]].
```

In the six-dimensional basis

```text
(core top, core bottom, leaf0 top, leaf0 bottom, leaf1 top, leaf1 bottom)
```

the induced halves are the 0-1 matrices

```text
P0:  ct ← ct+cb+lb,   lt ← cb+lt+lb,   other rows 0
P0': ct ← cb+lb,      cb ← cb,          lt ← cb+lb,   lb ← lb
P1:  ct ← ct+cb+mb,   mt ← cb+mt+mb
P1': ct ← cb+mb,      cb ← cb,          mt ← cb+mt+mb, mb ← mb
```

with all unlisted rows zero. These are idempotent, complementary on their
stage supports, and the two first halves do not commute. Both facts are
checked, as is the adjacent-order identity for these same matrices: first
both halves of stage 0, then both halves of stage 1, reproduces the target.

Expand the crossed product in `GF(2)[x_0, x_1]`. The difference from the
target has exactly two nonzero entries, each equal to the monomial `x_0 x_1`:

```text
leaf1 top ← core bottom,    core top ← leaf0 bottom.
```

Every other entry of the difference is zero. The expansion does not truncate
degree: each variable occurs in two factors, and the product is formed in
full. Since `x_0 x_1` is not the zero polynomial, the pure product is not the
target. At the field points

```text
(D_0, D_1, D_2, ..., D_30) = (2, 4, 1, ..., 1)
(D_0, D_1, D_2, ..., D_30) = (3, 5, 1, ..., 1)
```

one has `x_0 = 3`, `x_1 = 5` and `x_0 = 2`, `x_1 = 4` respectively, in the
fixed GF(16) representation below, and both products `x_0 x_1` are nonzero.
The same two entries of the embedded `q = 26` pure product equal those
products, and the target entries are zero. Every one of the 36 entries on
the copies of `V` agrees with this 6-by-6 product.

Thin maps contribute only to the coefficient of `e`. They do not change this
pure factor. Therefore no choice of thin maps, of any rank and in any gaps,
meets the endpoint for this call order and this frame.

Setting the single nonzero entry of `B` to zero makes the same crossed pure
product match the target at both points. The defect is the nonzero `B`.

## 4. The thin maps forced by `D_j = 1`

The pure-product mismatch already rules the pattern out. The maps below are
the ones the `D_j = 1` specialization forces, and they are what the two
field points evaluate. They are not a search.

At `D_j = 1` for every `j`, every `x_j` is zero, every conjugation is the
identity, and the normalized coefficient is the sum of the queries. Each
stage contributes `T_j`, the matrix with `I_d` in all four blocks of the
core and leaf `j`. For odd `g`,

```text
sum_j T_j = I + M,
```

where `M` is zero on every region diagonal and on every leaf-to-leaf block,
and `M` is `I_d` on each core-to-leaf block and each leaf-to-core block.
The endpoint at this point requires the thin maps to sum to `M`.

Write one port coordinate `c` as the `(g+1) × (g+1)` slice `J_c` with `1`
in positions `(core, leaf j)` and `(leaf j, core)` for every leaf, and `0`
elsewhere. Each `J_c` has rank 2: its image is spanned by the core basis
vector of coordinate `c` and the sum of the leaf basis vectors of that
coordinate, and those two vectors are independent. Distinct coordinates use
disjoint basis vectors, so ranks add.

Let `K_c` be the same shape using only leaf 0. It also has rank 2, and
`J_c + K_c` has rank 2 because leaf 0 cancels and the other thirty leaves
remain. Partition the `d = 52` coordinates into four blocks of 13:

```text
0..12,  13..25,  26..38,  39..51.
```

The five maps are the direct sums

```text
Z_0 = sum_{c=0}^{12} (J_c + K_c),
Z_1 = sum_{c=13}^{25} J_c,
Z_2 = sum_{c=26}^{38} J_c,
Z_3 = sum_{c=39}^{51} J_c,
Z_4 = sum_{c=0}^{12} K_c.
```

Each is a direct sum of thirteen rank-2 slices on disjoint coordinates, so
each has rank `26 = q`. Their sum is `sum_c J_c = M`. Placed in the central
gap, they meet the normalized coefficient at every `D_j = 1`. Omitting them
leaves that coefficient unequal to `I`. The same five maps, at either of the
two field points above, do not finish at `I`. That second check is
consistent with the pure-product mismatch; it is not a separate existence
search.

## 5. What this does not prove

- It does not examine every legal frame. The explicit `B` above is one
  noncommuting frame. If every full projector commutes, the count in
  `research/coupled31-chronology/COMMUTING.md` already requires
  `ceil(31/2) = 16` thin maps on every call order. That citation is not a
  new argument, and it is not the adjacent-halves rank bound.
- A word that separates a stage only by thin maps, with no other full call
  between the halves, still has pure factor `product_j (I + x_j E_j)` by the
  adjacent calculation. Section 3 does not apply to that word.
- Nested or crossing orders other than this all-first-then-all-second order
  are not classified.
- No exhaustive list of the `62!`-scale call orders was made, and no sampled
  search is being treated as nonexistence.
- The `g = 3` finite censuses do not lift to this profile, and they are not
  used.
- Native transport, frames, and the selected frontier are untouched.

## 6. Credit

The contract, the chronological rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), with the predecessor statements in PR #5673,
PR #5631, and PR #5617. The adjacent-halves count that leaves an interleaved
word open is PR #7010. The consecutive rank bound `R ≥ g q` that leaves
internal-gap and nested or crossing schedules open is PR #7005.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

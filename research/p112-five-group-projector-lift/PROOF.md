# A sharp low-tariff floor on five P112 triads

**Theorem.** Every finite rational rank-one decomposition of `I15` on the
five triads below has total whole-group invoice at least 45 if each nonzero
term has tariff at most 3. The direct 15-copy decomposition attains 45.
There is no restriction on the number of terms, coefficient sizes or
rational denominators. A common nonzero scalar endpoint is equivalent by
rescaling one factor family, which preserves supports and tariffs.

The ordered physical triads A, B, C, D, E have ports

```
A [10,18,93]   B [6,36,74]   C [13,23,102]
D [41,73,88]   E [30,50,87].
```

Every pair has nonzero physical pairing, so the strict endpoint on three
payload coordinates per group is exactly `I15`. Tariffs charge the complete
physical triad spaces touched by a factor, regardless of its active payload
coordinates. This theorem does not cover factors costing 4 or more, other
physical geometries, or a full P112 decoder.

## 1. The rational auxiliary lift

Form the 15-by-15 rational matrix `H` from the literal binary dot pairings
between the authenticated physical labels, interpreted as rational zeros
and ones. Replace each off-diagonal block between different groups in
`{A,C,D}` by `J3/3`. Those original blocks are all `J3`; leave all other
entries unchanged. In particular `H_gg=I3`.

For nonempty group masks `s,t`, write `h(s,t)=rank_Q H[s,t]` and let
`rho(s,t)` be the actual binary whole-group tariff. The replay checks all
961 ordered rectangles. None has tariff zero. There are 14 tariff-1,
20 tariff-2 and 273 tariff-3 rectangles. For every rectangle of tariff at
most 3, `h<=rho`, except exactly these four:

| Source mask | Reader mask | Lift rank | Tariff |
|---:|---:|---:|---:|
| 9 | 20 | 4 | 3 |
| 12 | 17 | 4 | 3 |
| 17 | 12 | 4 | 3 |
| 20 | 9 | 4 | 3 |

Masks use A through E as bits 0 through 4. Each exceptional rectangle has
disjoint source and reader group sets. The matrix is not a universal
rank-domination certificate: higher tariffs have additional exceptions.

Given a payload factor `u v^T`, form its 45-by-45 lift `A` with block

```
A_gh = (u_g v_h^T) tensor H_gh.
```

For exact nonzero group supports `(s,t)`, this equals
`D_u H[s,t] D_v^T`, where each group block of `D_u` is `u_g tensor I3`
and similarly for `D_v`. These blocks have full column rank 3. Consequently
`rank(A)=h(s,t)`. This uses exact nonzero group supports and holds for
arbitrary mixtures of payload coordinates. The lift of the endpoint is
`I45`, since all off-diagonal endpoint blocks vanish and `H_gg=I3`.

## 2. A projector counts repeated exceptional rectangles

**Surplus-rank lemma.** Suppose `I_n=sum_t A_t` and put
`R=sum_t rank(A_t)`. If `k` selected summands have the same disjoint
row/column support rectangle `(S,T)`, and each has rank `r`, then

```
R-n >= r k.
```

Choose minimal rank factorizations `A_t=X_t Y_t`, concatenate the X blocks
and stack the Y blocks. Then `XY=I_n`, so `P=I_R-YX` is an idempotent of
rank `R-n`. Each selected factorization can respect its supports: `X_t`
has zero rows outside S and `Y_t` has zero columns outside T. Because
`S intersect T` is empty, `Y_t X_s=0` for every pair of selected summands,
including equal indices. Their principal block in P is therefore `I_(rk)`,
which proves the bound. It does not require a rank-one projector or a
bound on the number of original payload factors.

Let `b` be the total number of exceptional lifted terms and let
`k_1,...,k_4` be their multiplicities in the four types. If the invoice is C,
the complete low-tariff census gives `R<=C+b`. When `b=0`, the endpoint
rank immediately gives `45<=R<=C`. Otherwise the surplus-rank lemma gives

```
R-45 >= 4 max_i k_i >= sum_i k_i = b.
```

Combining this with `R<=C+b` proves `C>=45`. The direct copies each have
whole-group tariff 3, so the bound is sharp in the stated class.

For example, this excludes 17 terms with four tariff-1 and thirteen
tariff-3 terms (invoice 43), as well as three tariff-1, one tariff-2 and
thirteen tariff-3 terms (invoice 44). Their original complementary
projector has rank 2; no rank-one assumption enters the theorem.

## 3. Secondary sixteen-term branch certificate

The package also retains the more detailed census that motivated the
all-term argument. Consider exactly 16 terms, two tariff 1 and fourteen
tariff 3. Write `UV^T=I15`. Then `P=I16-V^T U` has rank 1 and trace 1.
Every term with disjoint group supports has `P_tt=1`; every tariff-1 type
is disjoint. Two nonzero diagonal entries of a rank-one matrix require
both cross entries nonzero. Thus the two cheap types must cross in both
directions and must be distinct.

Their diagonal entries total 2, so a common-footprint term must have a
nonzero projector diagonal to make the full trace 1. That term must cross
both cheap types. These necessary conditions reduce the 91 unordered
pairs of distinct cheap types to exactly 21 branches. Every disjoint
regular term must also cross both cheap types.

In 17 branches all permitted regular types satisfy `h<=3`. The other four
branches each allow only one exceptional type:

| Cheap pair | Exceptional `(source,reader)` masks |
|---|---:|
| `(1,12), (8,5)` | `(20,9)` |
| `(4,9), (8,5)` | `(17,12)` |
| `(5,8), (9,4)` | `(12,17)` |
| `(5,8), (12,1)` | `(9,20)` |

Two copies of one disjoint type would give an `I2` principal block in the
rank-one projector, so at most one exceptional term occurs. With none,
the lifted rank sum is at most 44. With one, it is at most 45 and must
equal 45. Equality in an identity decomposition's rank sum forces every
summand to be idempotent: minimal rank factorizations concatenate to
square matrices `XY=I45`, hence `YX=I45`, and each diagonal block gives
`Y_t X_t=I`. But the exceptional rank-4 term is nonzero and square-zero
because its supports are disjoint. This is a contradiction.

This secondary census is independently replayed, but is not a premise
of the stronger theorem in Section 2. No earlier solver receipt is used.

## Replay, controls and attribution

Both `verify.py` and `independent.py` use Python's standard library and
accept `--repo-root PATH`. They authenticate the local candidate and
certificate, archive container and exact archived label member, then
regenerate all prices and lift ranks. They print JSON without writes,
Git access, sibling imports or solver dependencies.

The primary uses Fraction elimination and exact mixed rational fixtures.
The independent replay uses the integer matrix `3H`, primitive integer
elimination and reverse-order enumeration. Both verify the complete
low-tariff exception catalogue and the secondary branch certificate.

Controls include direct-copy attainment and the literal lifted identity,
a rational redundant frame, all four rank-4 square-zero types, and exact
surplus-projector fixtures. The independent fixture tensors
`I2=E11+E22+E12-E12` with `I4`: its two same-type rank-4 summands force an
`I8` projector block. Mutations show that the division by 3 and the own
identity blocks are material.

Separate AI agents developed and reviewed the proof and independently
implemented the two exact replays. This is AI-assisted research; human
mathematical admission remains open. A cheaper construction must include
a tariff-4-or-higher term or change geometry. No improved supplier or
full global cost-296 construction is claimed.

# Proof map and exact claim scope

This document states the two retained results in one place. The full
proofs and the later independent reviews are copied without changes.
All event indices and mode numbers start at zero.

## Fixed local word

Use the raw backward word in
[FULL-MODE-PROGRAMS.json.gz](frozen/work/centre-encoding-campaign-20261014/lanes/history-encoding/FULL-MODE-PROGRAMS.json.gz),
with decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
Its 704 inputs contain 224 data fields and 480 arbitrary helper fields.
The actual matrix `R` is in
[INTERFACE.json](frozen/work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json),
SHA-256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Put `K=R^T/4`.

Stop before event 12995. The centres are
`[92,57,81,224,11,240,9,256]` in frames 415 through 422.
Their initial helper roles are `[225,226,229,232,241,242,257,258]`.
The [exact cut proof](frozen/work/centre-encoding-campaign-20261014/lanes/history-encoding/CENTRE-RESET-INTERFACE.md)
gives centre rows `u_k+R_kY/4`. Replace their logical values by `v_k`,
omit the eight signs at events 12996 through 13003, and resume at 13004.
The unchanged suffix gives

```text
Y_out = Y,
X_out = X-Y+R^T(v-u),
u_out = v.
```

The other 472 helper contents are restored. Thus `v=u` gives the unit
backward data map and restores all 480 helpers. For centre frame `B_k`,
the physical replacement must be `B_k u_k`. The construction below acts
on physical coefficients and keeps each binary access in one actual
frame. It does not commute a scalar map through unequal frames.

## Finite local reset

The governing proof is
[GRID-RESET-PROOF-V2.md](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/finite-grid/GRID-RESET-PROOF-V2.md),
SHA-256 `40fa4d2cbd2a6cfa3a7ec6facd81e04af727b18d77bed11643b13f19e38428e7`.
Its [independent review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/tagged-grid-review/REVIEW.md)
accepts this corrected local theorem.

Use the maximum absolute real or imaginary coefficient as the norm.
For `h,q` on `Delta Z[i]`, suppose

```text
0 < delta <= 1,
|delta q| <= Delta/16,
|e| <= delta Delta/16.
```

For `z=h+(1+delta)q+e`, the operations

```text
b = Round_Delta(z),
q_hat = Round_Delta((z-b)/delta),
h_hat = b-q_hat
```

give `b=h+q`, `q_hat=q`, and `h_hat=h`. The first error is at most
`Delta/8`, and the second is at most `Delta/16`. Both are strictly
inside the nearest-grid rounding cell. A coarse bound on `e` alone
does not suffice for the second operation.

Tag both data banks by `(1+delta)` with the owned field `C0`:
copy the data to zero `C0`, scale `C0` by `delta`, add it to the data,
and clear `C0`. At the cut, round 696 non-centre fields to the ordinary
untagged prefix state. Decode the eight centres with the formula above.
Then run the suffix and round all 704 outputs to their known grid.
The centre decoder uses the same owned field and clears it after use.
All scale factors are dyadic units. No arbitrary helper is cleared.

The literal [word](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/finite-grid/REDUNDANT-GRID-WORD.json.gz)
adds 232 COPY, 240 SCALE, 240 ADD, 233 CLEAR, and 1,416 ROUND passes:
2,361 passes in total. The native word retains 3,486 climbs, with rank
mass 5,522, and adds no child. These passes have a new finite bit cost;
the old scalar coefficient does not include them.

### Physical grid and error premise

Let every initial physical coefficient lie on `2^-g Z` with magnitude
at most one. For tensor width `lambda <= e`, define

```text
H = 5522 lambda + 16339,
G = 5522 lambda + 49012,
L = 2^G,
Delta = 2^(-g-H),
delta = 2^(-g-H-G-4),
Gamma = 2^(-g-2H).
```

The exact scalar denominator and growth sums are 16,339 and 49,012.
The inherited raw native recipes give denominator exponent at most
`r lambda` and component row norm at most `2^(r lambda)` for a rank-r
child. Their monomial wrappers preserve the grid and component norm.
These facts imply that both cut contributions lie on `Delta Z[i]`,
their data part has norm at most `L`, and the suffix output lies on
`Gamma Z[i]`. The native phase premise is retained explicitly in
[FULL-MODE-PORT-REVIEW.json](frozen/work/centre-encoding-campaign-20261014/lanes/interface-proof/FULL-MODE-PORT-REVIEW.json).
The separate [physical correction](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/centre-reset-review/PHYSICAL-GRID-V2.md)
checks actual canonical phase recipes and rejects the plain-product
interpretation of their listed basis vectors.

Assume `g <= t+B e`, with fixed nonnegative integer `B`, and set

```text
P = 2B e + 2H + 4G + 32.
```

Give each child relative computation and normalized-input error at
most `2^(-a_j t-P)`, where `a_j` is one or two. Separately bound each
parent scalar or return conversion by absolute error `2^(-2t-P)`.
The separate return allowance is necessary for a tiny child input.
A half-parent-grid native output can incur relative error at least
one half on conversion even when the child computation is exact.

There are at most `25457+3486+2361=31304 < 2^16` insertion sites.
Exact suffix propagation gives coarse cut, fine centre, and final
output error bounds

```text
4 * 2^16 * L^2 * 2^(-t-P),
4 * 2^16 * L^2 * 2^(-2t-P),
4 * 2^16 * L^3 * 2^(-t-P).
```

Relative to `Delta/16`, `delta Delta/16`, and `Gamma/16`, the exponent
margins are at least `B e+H+2G+10`, `G+6`, and `B e+G+10`.
The strict margins make all cut and final snaps exact. The stated
format has `2t+O(e)` fractional bits and `O(e)` magnitude bits.
Tag arithmetic fits because `2g+H+G+4 <= 2t+P`. Scaling the residual
does not form a large scaled baseline.

Set `a_j=2` for every child with a nonzero response at an observed
centre and `a_j=1` for the others. The exact response set has 124
rank-one and eight rank-four children, of mass 156. Every such input
has both data and helper terms. Treat each child error as an additive
output vector on its actual input; the exact response calculation
then applies even when that error depends on earlier errors.
This is a sufficient assignment under arbitrary independent relative
errors. It does not bound a correlated or lattice-restricted contract.

The theorem starts on the declared input grid. Coarse conversion of
finer caller records is outside this local fine-error allowance.
The reviewed [record-format proof](frozen/work/centre-encoding-campaign-20261014/lanes/interface-proof/heterogeneous-precision-review/REVIEW.md)
is conditional on a complete node endpoint and finite error proof.
It does not supply either obligation for this local word.

### Local resolution scope

The actual minor on columns `[0,7,20,27,36,46,57,111]` obeys
`R_A R_A^T=4I`. Assume `g>=3` and choose `s_k` in
`2^-g Z intersect [-1/8,1/8]`. Set `v_k=s_k e0`, `Y_A=R_A^T v`, and
`u_k=e0/8-v_k`. These inputs lie on the declared input grid.
The physical tagged carrier is `(1/8+delta s_k) B_k e0`.
For adjacent values spaced by `2^-g` and `delta <= 1/2`, its relative
separation is between `(16/3) delta 2^-g` and `16 delta 2^-g`.
The nonzero common vector cancels in the ratio. For positive scalar
carriers `a<b`, the relative error balls intersect at radius
`(b-a)/(a+b)`. This proves a resolution limit for this packed carrier.
It neither assigns native cost nor bounds algorithms with other reads,
codes, or error contracts.

## Exact complete pure-reset family

The governing [family proof](frozen/work/centre-encoding-campaign-20261014/lanes/temporal-reuse/EXACT-TAGGED-RESETS.md)
has SHA-256 `3a5f2bd40804d6106192f75c3abe7aefdf4d98c829cec03979bd79e8adb3d3b4`.
The later [full-family review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/exact-reset-policy-review/REVIEW.md)
accepts that theorem and proves the sharp surplus 17 below.

A permitted reset acts on one event target immediately after an
existing scalar or native event, before the fixed cut at 12995.
Its ideal row must be pure data or pure helper. It preserves that
ideal row and has zero error derivative under its required rounding
margin. Every subset of these sites is permitted. The theorem grants
their implementation and all other new work for free.

There are 860 eligible sites. The 644 before the first native event
cannot remove native error. The last pure-data site is event 637;
the first native event is 9742. Of the remaining 216 pure-helper
sites, 180 have no Boolean path to a centre. Boolean support ignores
cancellation. A reset only removes paths, so those 180 choices remain
irrelevant under every policy, including one that breaks cancellations.

The remaining 36 sites split into three groups of 12, with centre
masks 15, 48, and 192. Every relevant reset and each of the 176 possible
native error ancestors belongs to one group. Thus a group cannot alter
another group's response, and no native job shares a cost between
groups. Every three local choices form a legal global choice.
This proves that `3*4096=12288` local cases cover all `2^36` effective
global policies. It is not a sampled-policy argument.

Independent exact Fraction replay checks every local support histogram
against the producer's integer calculation and composes all 255
nonempty query subsets. Every active rank is one or four. For a subset
`S`, the rank-four count is exactly `|S|` for every policy. Thus the
minimum rank-one count also minimizes each nonnegative rank moment.

| Query count | Minimum extra-accuracy rank mass |
| ---: | ---: |
| 1 | 25 |
| 2 | 44 |
| 3 | 60 |
| 4 | 65 |
| 5 | 90 |
| 6 | 109 |
| 7 | 134 |
| 8 | 153 |

Resets after 10008 and 10012 attain the all-query profile
`{1:121,4:8}`. A separate forward replay checks all 176 possible
native impulses under no resets, all eligible resets, and this optimum.
The zero-response counts are respectively 44, 18, and 47. In particular,
resetting every eligible field is not the optimum.

### Sharp moment and nonuniform allocations

The complete subset minima prove `n1(S)-4|S| >= 17` for every nonempty
`S` and every permitted policy. Equality occurs for `S={5}` or `S={7}`
with no resets, with 21 rank-one and one rank-four job. For
`0 <= sigma <= 1`, put `x=2^sigma`. Then `1 <= x <= 2` and
`8^sigma-4^sigma=x^2(x-1) <= 4`. Therefore

```text
sum_(j in C(S)) r_j^sigma - |S|*8^sigma
  = n1(S)-|S|*(8^sigma-4^sigma)
  >= 17.
```

The two one-query witnesses attain equality at `sigma=1`. Thus 17 is
sharp over this family and interval, without numerical sampling.

For nonnegative query allocations `gamma_k`, charge each child the
maximum allocation over queries in its support. Integrate the subset
inequality over `S(t)={k:gamma_k>t}` to obtain

```text
sum_j r_j^sigma max_(k in support(j)) gamma_k
  >= 8^sigma sum_k gamma_k + 17 max_k gamma_k.
```

The empty-support maximum is zero. The same two witnesses show
sharpness. The result also holds for a policy that changes by bit layer
when costs add by layer; it does not emit or admit such a native word.
The separate mass bound `mass(C(S)) >= (65/4)|S|` gives the stated
non-improvement threshold `beta >= 97/65` for uniform width multiplier
`beta`, as proved in the source.

These cost conclusions assume the declared independent relative-error
width model. The family excludes new access edges, new bases or codes,
joint resets, other reset times, changed native interfaces, and special
child error contracts. It grants the original width to retained private
centre jobs without claiming a complete partial-centre controller.
No complete supplier, universal lower bound, or kappa improvement follows.

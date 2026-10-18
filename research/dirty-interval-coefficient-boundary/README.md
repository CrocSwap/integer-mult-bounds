# Quadratic interval amplification with commuting scalar isometries

**Scoped precision-interface result; no new κ.** In PR628's unchanged
reserved-depth balanced dirty word, the quadratic dependence on the sharp
prefix coefficient is unavoidable, even when all factors commute and every
subset product has norm one. This answers the **order of growth** part of the
sharp-interval follow-up in PR1278/1295. It does not give the exact all-size
optimal constant, falsify their valid sufficient bounds, or change a supplier.

For every integer `h >= 1`, take `n=2^h` factors on the real line, all `+1`
except `A_(n-2^k-1)=-1` for `0 <= k <= h-2`. In the maximum joint-register
norm, each prefix and inverse prefix is bounded by `C=h+2` (PR1085), whereas
one chronological complete-leaf interval has target-row absolute sum

```
F_h = floor(h^2/2) + h + 2.
```

Thus the worst interval norm is **Ω(h²)**. PR1085's prefix theorem supplies
the existing upper bound `(h+2)²` on every interval in the contraction domain,
so the growth is **Θ(h²)**. Commutation and the subset budget `G=1` alone
cannot justify an `O(C G)` joint-register interval bound with an absolute
constant. The source remains protected and the full word restores all scratch.

The smallest counterexample to the stronger, specific bound `C G` has four
factors. With `(A0,A1,A2,A3)=(1,1,-1,1)` and registers `(x,y,z1,z2)`, cuts
`[2,6)` execute:

```
z2 -= x; z1 -= z2; z2 -= z1; y += z2.
```

The final target is `y-2x-z1+2z2`, whose row norm is **6 > 4**. All factors
are invertible commuting isometries; every subset product is ±1. The complete
16-leaf word is `y -= x`, with both dirty registers restored. This is a
counterexample to a proposed strengthening, not an acceptance bug in a predecessor.

## Proof for every h

Use the positive word `U,V,U^-1,V^-1` in chronological order, with the same
one connector per recursion depth shared by siblings. Let `P_t` be its prefix
matrix after `t` complete leaves. There are `4^h` leaves. Write registers as
`(x,y,z1,...,zh)` and choose

```
a_h = floor(3*4^(h-1)/5),       b_h = (4^h+2)/3.
```

The interval is `P_b P_a^-1`. The cut `a_h` lies in the first left child, all
of whose factors are identities. That child has height `h-1` and target `z1`.
The cut `b_h` is the first execution of the rightmost leaf: if `b_0=1`, its
recurrence is `b_h=4^(h-1)+b_(h-1)`, giving the displayed formula.

First compute `Q=P_a^-1`. For an identity-factor call of height `k`, put
`c_k^-=floor(3*4^k/5)` and `c_k^+=ceil(3*4^k/5)`. At `k=0`, these cuts are
zero and one, so the inverse prefixes are `I` and the negative leaf shear.
For `k>=1`, both cuts are inside phase 2, the inverse left child. If `L=4^(k-1)`,
the complementary positive-child cut is `3L-c_k^± = c_(k-1)^∓`.
The exact phase formula is

```
P_c = P_child U^-1 V U,
P_c^-1 = (U^-1 V^-1 U) P_child^-1.
```

For identity factors the first matrix changes only the external target:
`target -= source + connector`. Recursion alternates floor and ceiling cuts;
the bottom negative leaf is present precisely when `h-1` is odd. Therefore,
writing `e_j` for a register row, the rows of Q satisfy

```
Q[x]=e_x, Q[y]=e_y,
Q[z_h]=e_zh - ((h-1) mod 2)*e_x,
Q[z_i]=e_zi - e_x - Q[z_(i+1)]              (1 <= i < h).
```

Equivalently, for every `1 <= i <= h`,

```
Q[z_i] = sum_(j=i..h) (-1)^(j-i) e_zj - 1_(i even) e_x.
```

No fresh scratch per subtree has been introduced in this recurrence.

At `b_h`, the rightmost path has completed each left product before descending
right. Its target row is the original target plus the full product times `x`
and each suffix product times the corresponding original connector. The last
`2^(h-i)` factors contain exactly `h-i` negative factors, while the full product
contains `h-1`. Consequently

```
P_b[y] = e_y + (-1)^(h-1)e_x + sum_(i=1..h) (-1)^(h-i)e_zi.
```

Multiply this row by Q. The coefficient of `z_j` is the sum of `j` equal
signs, `j*(-1)^(h+j)`. The source coefficient is
`(-1)^(h-1)*(1+floor(h/2))`, and the target coefficient is one. Their absolute
sum is `2+floor(h/2)+h(h+1)/2 = F_h`. A norm-one vector with these coefficient
signs attains the row norm. Even if its source coordinate is zero, the
attained value is `1+h(h+1)/2`, still quadratic.

The ratio `F_h/(h+2)` is unbounded. This proves the claimed obstruction for
arbitrary joint disturbances at a cut. It does **not** imply quadratic
amplification of a disturbance supported on one leaf destination: the displayed
target-row coefficients on individual dirty registers are only `1,...,h`.
The reverse word represents the same map at reversed **ordered** cuts;
its corresponding forward interval is the inverse, not this same witness.
The lower bound already holds in the positive chronological word.

## Finite evidence and reproduction

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/dirty-interval-coefficient-boundary
```

Or run the standalone mathematical replay and its package tests:

```sh
python3 -I -O -B research/dirty-interval-coefficient-boundary/verify.py
python3 -I -O -B research/dirty-interval-coefficient-boundary/test_package.py
```

Expected mathematical marker: `PASS_DIRTY_INTERVAL_COEFFICIENT_BOUNDARY`.
Default execution compares every deterministic field with [CERTIFICATE.json](CERTIFICATE.json)
and writes no files. `--write NEW_PATH` is explicit authoring mode, not an
admission check; `--bindings-only` certifies only the consumed source bytes.

- **272,012** nonempty intervals for every `n=1..16`, both signs, computed in
  the free noncommutative algebra without a squarefree quotient. Empty intervals
  are identities. Negative-word intervals cover reverse ordered cuts.
- Their coefficient maxima are `2,3,4,6,7,8,8,9,10,10,10,12,12,12,12,14`,
  independently corroborating PR1278's already published counts. **No priority
  is claimed for those counts.** Exact binary sign equations now give a scalar
  isometry attaining every maximum. Hence these are also sharp finite norm
  envelopes for arbitrary contractive operator factors, not just coefficient
  counts. Each monomial has norm at most one by submultiplicativity; real scalar
  sign witnesses attain the upper envelope.
- Literal source/emitter comparisons, full restoration, all prefix/inverse-prefix
  checks and interval witnesses at `h=1..8` cover **87,380** complete leaf events.
- A separate recursive dense prefix/Gauss-Jordan engine checks every attaining
  finite witness and the family through `h=20` (`n=1,048,576`). It expands no
  large word. Large recursive evidence and literal replay are distinguished.
- Seven mathematical controls include omitted restoration, wrong cuts, wrong
  multiplication order, changed factors, aliasing, the false prefix substitution
  and a noncontractive boundary. Package tests add independent scalar-vertex
  enumeration, inverse-prefix recurrence checks and actual source/receipt corruptions.

The registered replay and all six test groups pass locally on macOS arm64,
CPython 3.12.14. Direct isolated optimized CPython 3.14.7 produces the same
complete mathematical receipt. Independent literal scalar enumeration tests all
510 sign assignments and **1,553,988** intervals at n=1..8; the full inverse-cut
recurrence is checked through h=14. Actual source/predecessor corruption, removed
input pins and an understated receipt are rejected; a complete read-only relocated
replay preserves every input byte. Metadata/provenance and selected-record integrity
checks pass. Hosted CI, the selected cold replay and full numerical kernel tests
were not run for this local lemma.

The all-h conclusion rests on the written recurrence above; finite checks are
supporting evidence. Two algorithms are not independent human peer review or a
proof-assistant formalization. See [TASK.json](TASK.json) for the bounded scope.

## Scope, sources and credit

Base main: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Assignment nonce
`6ea4f4e7bb7e3d3c409911656eec36e3`, adversarial-audit / `uniform-transfer-audit`,
refined to this precision implication. [Discussion #1357](https://github.com/CrocSwap/integer-mult-bounds/discussions/1357)
records the claim. [SOURCES.json](SOURCES.json) contains exact base Git/SHA256
pins and byte-identical consumed pending proofs.

Credit **Chafik Boukhalfa** for PR628's dispatcher (head
`0768f97d06c623b8211e651543c66135796b62bf`), PR862's subset argument and PR905;
**Hanson Sun** for PR1085 (`82b99c7d12dac009d35636562df4c6c91e885409`) and
PR1244's noncommuting interval obstruction; **Charles Bethin** for PR1278
(`06b8c006891ae78abe24b30d2fe9d8c188deafe8`), its shared-scratch phase decomposition
and finite coefficient census; **Philipp / mightyOil** for PR1295
(`3a6773708f0d73f7dbee164f4c6e7658b0b41509`) and its explicit sharp-interval
follow-up; **Gareth Davidson** for PR877's perturbation context and retained
lineage including 0xkilgore's PR663 count/restoration audit. The new result is
the all-height commuting-isometry lower family and scalar attainment of the
finite maxima; it does not supersede their valid bounds or precision formulas.

New work is Apache-2.0, prepared for **Arham Tahir** with substantial **OpenAI
Codex assistance** in mathematics, implementation, validation and writing.
Predecessor proof text and source files remain unchanged. This package changes
no selected record, production precision, upstream file, local word or paid profile.

Actual cyclic kernel factors have additional analytic structure. This generic
counterexample need not be realizable by those factors. Internal leaf growth,
preparation, rounding, precision/tape bounds, physical/compiler/hosting interfaces,
full caller admission and the multiplication theorem are unproved here. No
actual deterministic rounding-failure trace or precision minimum is claimed.

## Open next questions

1. **Destination-supported transport:** determine the maximum amplification of
   an error on the actual next leaf destination, rather than an arbitrary joint
   disturbance. This matters because the present quadratic norm lower bound
   does not exclude a linear bound for such errors. First enumerate all source-bound
   destination columns at small sizes, then strengthen the six phase cases to
   a column invariant. The blocker is an all-size proof with the precise rounded
   error support and shared scratch retained.
2. **Sharp constant:** is `floor(h²/2)+h+2` a universal coefficient envelope at
   height h? The small census and the lower family support that question, but do
   not prove it. First derive phase-pair coefficient recurrences using the PR1085
   one-monomial prefix invariant. The blocker is cancellation and shared-scratch
   reuse in arbitrary pairs of cuts, including unbalanced n.

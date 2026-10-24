# Independent review of the low-displacement native budgets

The two budget packets pass within their stated conditional scope. This
review counts all 24 raw and changed words. It also checks 176 complete
profile intervals with a separate exact rational evaluator. Each stated
extra-child limit has a strict upper bound below one. The next count has
a strict lower bound above one. No source file was changed.

This is a native-budget result. It does not admit a changed output at a
global stage. In particular, 224 H1 is a terminal cost comparator for the
changed outputs. It is not an implemented decoder for those outputs.

## Inputs and rate

The reviewed freezes are:

| Packet | Freeze SHA256 |
| --- | --- |
| `budget-geometry-20261017/low-displacement-budget-20261020` | `c730e61f7446b072c60411f9cb6af903e5b252b12ce9a4d9bce906990303fbef` |
| `budget-geometry-20261017/mixed-exit-budget-20261020` | `99f084410fcba6228d396d8c547dd4ed74835dc97de7fce004387b6de6ab92a5` |

Each path is relative to the campaign's `lanes` directory. The checker
verifies every file in each freeze. It also verifies every upstream input
pin in the first budget receipt.

The exponent is read directly from the selected assembly at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The selected record is
[`certificates/selected-result.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/certificates/selected-result.json).
Its SHA256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
It binds
[`research/community-frontier1094-audit/ASSEMBLY.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1094-audit/ASSEMBLY.json)
to SHA256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.
The assembly's exact `complex_lower` is

    b = 67018507072324140917 / 40000000000000000000000.

Thus the rate is a verified historical selected snapshot. This review
does not claim that it is the current selected rate. The calculation
uses D=25, productive width W=224, three calls, and no idle jobs.

## Literal invoices

The checker imports no producer code. It reads each event from both
providers in both orientations. It checks the native recipe reference
and rank, counts the two side maps of each child, and counts each inline
and endpoint monomial map. All scalar and native operands use the 224
data roles.

| Family and exit | Native histogram | Mass | Children | Scalar primitives | Map bound |
| --- | --- | ---: | ---: | ---: | ---: |
| Rank30 raw | 1036 H1, 48 H3, 55 H4, 55 H5, 9 H6, 9 H7 | 1792 | 1212 | 5288 | 2648 |
| Rank16 raw | 1520 H1, 64 H2, 48 H3 | 1792 | 1632 | 7384 | 3488 |
| Rank30 W48/I64 | 988 H1, 48 H2, 55 H4, 55 H5, 9 H6, 9 H7 | 1696 | 1164 | 5288 | 2552 |
| Rank16 W48/I64 | 1472 H1, 112 H2 | 1696 | 1584 | 7384 | 3392 |
| Rank30 W112 | 988 H1, 48 H2, 55 H5, 55 H6, 9 H7, 9 H8 | 1824 | 1164 | 5288 | 2488 |
| Rank16 W112 | 1408 H1, 112 H2, 64 H3 | 1824 | 1584 | 7384 | 3328 |

Every raw data field has total native rank eight. In W48/I64, 96 fields
have rank seven and 128 have rank eight. In W112, those totals are seven
and nine. These are sums along a field, not individual child ranks.

The complete scalar sequence is equal before and after each changed
exit. This was checked for all 16 changed words after exact coefficient
schema conversion. The scalar prices use the stated model tariff:
complex ADD coefficients of absolute value 1, 2, and 3 cost 8, 10, and
12 real primitives. A sign costs two primitives; a double or half costs
two more when present. All endpoint and inline maps remain separate.

The resulting three-call raw subtotals are 15864 scalar primitives and
7944 maps for rank30, or 22152 primitives and 10464 maps for rank16.
The bound on a map count is not a finite implementation price.

The source native phase proofs and the 640-column input checks remain
pinned premises. This review does not repeat them. The source prefix
norm bounds 46/30 for rank30 and 22/22 for rank16 also remain premises;
the invoice check does not prove bounds on recursive child interiors.

## Independent exact arithmetic

For a histogram H, the calculation is

    M(H) = sum_r H[r] r/(25*224) (25/r)^b.

The new evaluator uses only Python integers and rational numbers. It
imports neither retained moment engine. For x>=1, write x=2^k y with
1<=y<2, and put z=(y-1)/(y+1). Then 0<=z<1/3 and

    log(y) = 2 sum_(j>=0) z^(2j+1)/(2j+1).

After 64 terms, the positive omitted tail is at most

    2 z^129 / (129(1-z^2)).

The same expression at z=1/3 bounds log(2). Combine the two bounds and
round outwards to the rational grid 10^-60.

For 0<=t<1/100, use the degree-20 exponential polynomial. Its omitted
tail is at most

    (t^20/20!) t/21 / (1-t/22).

The argument condition is checked exactly for each rank. Monotonicity
gives lower and upper exponential bounds from the logarithm interval.
Each complete profile interval is contained in its retained budget
interval. Floating-point numbers do not determine a result.

The checked limits include ranks 1, 2, 4, 8, 9, and 17 for each of the
nine allowance profiles. The checker also verifies every packed-rank
limit and its successor, the hypothetical decoder comparators, and the
six mixed-exit profiles and their H1/H2 limits.

## Main thresholds and the packing theorem

The raw three-call rank30 bill permits 199 H1 or 99 H2. The rank16 bill
permits 195 H1 or 97 H2. Each pair gives alternatives, not joint
allowances. A 224-H1 terminal must therefore lose at least 25 H1 or
29 H1, respectively, if all other work is fixed.

The strict child-size guard gives maximum rank 17. For 0<b<1, the
function f(r)=r^(1-b) is increasing and strictly concave, with f(0)=0.
For 1<=a<=c<17,

    f(a-1) + f(c+1) < f(a) + f(c).

Repeated use of this inequality puts all but at most one nonzero child
at rank 17. Thus the minimum cost for a total of n ranks has
floor(n/17) copies of H17 and one remainder. This minimum increases
strictly with n, including each multiple of 17. The checker also checks
all 136 discrete transfer inequalities at the stated b.

The raw rank30 limit is 200 total ranks: 11 H17 + H13 passes, and
11 H17 + H14 fails. The raw rank16 limit is 196: 11 H17 + H9 passes,
and 11 H17 + H10 fails. After three W48/I64 calls and the 224-H1
comparator, the corresponding limits are 264 and 259. These are
favorable arithmetic bounds; they do not construct grouped children.

For the mixed exits, the exact thresholds are:

| Family | Changed calls | Extra H1 | Extra H2 |
| --- | ---: | ---: | ---: |
| Rank30 | 1 | 71 | 35 |
| Rank30 | 2 | 167 | 83 |
| Rank30 | 3 | 263 | 131 |
| Rank16 | 1 | 66 | 33 |
| Rank16 | 2 | 162 | 81 |
| Rank16 | 3 | 258 | 129 |

The next count fails in every column. Each allowance must pay for all
added native work. The two columns cannot both be spent.

The literal change is the same in both families:

    H_changed - H_raw = 48(H2 - H1 - H3).

Let u_r be the moment cost of one Hr. One changed call therefore saves
48(u_1+u_3-u_2). In H1 units, this is exactly

    48(1 + 3^(1-b) - 2^(1-b)).

The independent rational enclosure is

    95.846609456084463 < saving/u_1 < 95.846609456084464.

This explains why a 96-rank mass reduction is not a 96-H1 moment
allowance. Restoring all 96k ranks with H1 requires at least 25 H1 to
be omitted for rank30, or 30 H1 for rank16, for k=1, 2, or 3. The
rank16 value 30 is compatible with the raw value 29; the changed
histogram saves fewer than 96 H1 units per call.

For any positive b, a profile with mass DW and all child ranks below D
has M(H)>1. This proves the stated conditional full-restoration
obstruction. It does not prove that full restoration is necessary.
Three W112 calls and terminal mass 224 have mass 5696>5600, so that
combination also fails at b=0.

## H9 comparison and remaining scope

The H9 contraction has a separate independent native review at
`bridge-review-20261017/rank9-completion-review-20261020/FREEZE.json`,
SHA256
`50f2e168cdbf08e2bdad445bf2aa28f96d699cbc669a39892927bf94593e3b51`.
That review was completed after the two budget freezes. This new review
pins it without changing the frozen budget text.

Its complete profile is

    {1:576, 2:144, 5:144, 7:272, 8:192, 9:64}.

The complete mass is 5600. Its moment is inside
[1.002547757087305755,1.002547757087305756]. With all other children
fixed, at most 81 of the final 96 H1 can remain. A reduction of at least
15 H1 is still required.

No material error was found in either reviewed budget packet. The
results do not prove a global caller, the placement of changed exits,
a terminal decoder for their codes, map lowering, a recursive host,
precision, an odd-grid interface, or a kappa improvement.

## Reproduction and credit

Run `python3 -I -B check_review.py`, then repeat with `-O`. Both runs
produce the same receipt bytes. The checked output is:

    PASS 176 exact profile intervals; 24 literal words; 16 unchanged scalar sequences

The new-core-transfer lane supplied the local native words. The
budget-geometry lane supplied the two budget packets. The bridge-access
lane supplied the H9 contraction. This review uses a separate invoice
reader and rational evaluator. It used AI assistance and is not an
independent human review.

No PR, commit, push, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.

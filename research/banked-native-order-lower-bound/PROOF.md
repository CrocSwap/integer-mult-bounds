# A universal bank bound and the single-anchor rank limit

Every legal topological row order of the fixed fifteen-pivot graph needs
at least **1507 private snapshot banks** under the retained storage contract.
The known order from [PR #7724](https://github.com/CrocSwap/integer-mult-bounds/pull/7724)
uses 2106. Thus the global minimum lies in `[1507,2106]`.
The gap of 599 banks remains open. No new schedule or kappa is supplied.

The second result identifies a limit of one lower-bound method. For every
one of the 7643 row anchors, compute the maximal set of old tokens that
must be live there in every legal order. Combine that set's exact rank
with the full output information rank and the separate result bank.
The strongest bound in this precisely defined family is **exactly 1507**.
To prove a larger bound, a certificate must use more than these facts at
one fixed row. This is not a ceiling on other lower-bound methods or on
the global storage minimum.

## Fixed contract and normalized fields

Use graph hash
`d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098`
from [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674).
There are 1501 independent entrances, 6142 paid rows and 1501 terminal rows.
The [PR #7681 contract](https://github.com/aliromman/integer-mult-bounds/blob/1753a3ff56be34b09a217b12b590f51eba15defb/research/banked-native-snapshot-reuse/PROOF.md)
permits reuse after a token's last complete read. The order may now change,
as in PR7724; all other contract terms stay fixed:

- Copy all entrances into distinct private banks before the first row.
- Give each live token its own immutable snapshot. Do not merge equal forms.
- Reserve and initialize the new result before the first donor read.
  Retain every donor through the complete row, child and adapters.
- Keep each literal donor list and coefficient. Do not recompute tokens,
  use public fields as workspace or read extra donors outside the graph.
- Keep all terminal snapshots until common public installation.

The graph's normalized snapshot values are rational linear forms in the
1501 entrance fields. The exact chart contract identifies each physical
field with its normalized field by an invertible map. Different charts
do not create independent information. This argument does not identify
different-chart snapshots as the same physical bank.

## The maximal universally live set

Write `u < v` when the dependency DAG has a nonempty path from u to v.
Fix a row x. For an old token v, define membership in S_x by both conditions:

1. v is an entrance or `v < x`.
2. v has a direct consumer w with `w=x` or `x < w`.

Every member must be born before x and must retain a value for a read at
or after x. It is therefore live when x's new result is reserved.
All direct donors of x belong to S_x. The new result x is separate.

The converse is also exact for this DAG and contract. If a nonentrance
v is not an ancestor of x, a linear extension can put x before v. If
condition 2 fails, x is not an ancestor of any consumer of v. Put the
downward closure of all those consumers before x, then retire v after
its last read. An unused entrance can retire after the entrance phase.
Terminal tokens have no row consumers and can be placed after x; none
is a forced old token at a different anchor. These choices show that a
token outside S_x need not be live there. Late optional retirement cannot
create a universal requirement that is absent under earliest retirement.

Thus S_x is the intersection of the old live-token sets at x over all
permitted row orders and retirement choices. The checker computes it by
forward and reverse reachability recurrences over the entire fixed DAG.
There are 7063 distinct sets, 188816 total owner incidences and at most
443 fixed forced owners at one anchor. Cardinality alone gives no useful
improvement over the entrance reservation. The rank argument below does.

## Information rank gives an additional bank requirement

Let n=1501, let k be the size of S_x, and let r be the rational rank of
its normalized forms. The complete endpoint matrix has rank n. The checker
proves this by exact elimination modulo the verified prime 1000003.
Its nonzero full-size minor remains nonzero over the rationals.

Before x starts, all future terminal values are functions of the live
private token snapshots. Already completed terminals are also live.
Future rows read only their listed token donors; retired values, public
originals and old temporary contents are not extra data channels.
Induction through the remaining linear graph therefore factors the
endpoint map through the current live forms. Those forms have rank at
least n. For full fields with N coordinates, both ranks multiply by N;
one bank still contributes at most one normalized field of information.

The k forced banks contribute only r independent forms. At least n-r
other live banks are needed. The initialized result bank is a separate
bank and contains no entrance information before the first read. Hence

```text
snapshot banks >= k + (n-r) + 1 = n + (k-r) + 1.
```

This argument charges information jointly. It does not add several
per-owner lower bounds or assume that all nonforced owners coexist.

## Explicit witness at row 88772

At row 88772, S_x has 24 owners and exact rank 19. The
[certificate](CERTIFICATE.json) lists all owners, a 19-token basis, five
relations and literal birth/use paths for every owner. Its paths contain
95 dependency edges; no path has more than four vertices.

Four of the relations are equality of normalized forms:

| Dependent token | Basis token with the same normalized form |
| --- | --- |
| 88503 | 88495 |
| 88501 | 88492 |
| 88505 | 88499 |
| 88553 | 88543 |

The fifth relation is

```text
v_88765 = 2*v_88465 + v_88467 - v_88492 + 2*v_88495
          - 2*v_88499 - v_88543 - 2*v_88547 + v_88549 + v_88761.
```

Every relation has coefficient one on its own dependent token and uses
only basis tokens elsewhere. The five relations are independent and
express all 24 forms in the span of 19 basis forms. Exact rational
substitution checks 970 coefficient products and zero residuals.
Modular elimination proves that those 19 basis forms are independent.
Thus r=19 over the rationals, not just modulo the prime.

The information bound gives `24+(1501-19)+1=1507`. The particular owners
of the additional 1482 live banks can depend on the row order. That is
why counting only fixed universally live owners misses the bound.

## Exact ceiling for this certificate family

For every row anchor, the checker computes the rank of S_x modulo the
same prime. Rational rank is at least modular rank. Every resulting
defect upper bound `size(S_x)-modular_rank(S_x)` is at most five. The
24-owner certificate attains rational defect five. Consequently

```text
max_x (1501 + size(S_x) - rank_Q(S_x) + 1) = 1507.
```

This certifies the entire single-anchor family. It does not require all
other modular ranks to equal rational ranks. The receipt labels its
modular-defect histogram as an upper-bound histogram. No exact rational
classification of its other deficient cases is claimed.

The family uses only the forced forms and total information rank. In
that relaxation, complete a basis of the forced span to n independent
forms and retain the k forced tokens plus n-r complementary forms.
Reserve the extra result bank. This attains the formula in the relaxation.
Those complementary forms need not be legal graph snapshots, so this
argument supplies no 1507-bank schedule. A stronger storage proof can
use several row boundaries, order-dependent choices, actual available
complementary forms or other constraints not present in this relaxation.

## Verification and limits

The exact coefficient pass checks all 8533666 products on the source
grid 530841600. Prime testing, full endpoint rank and all 7643 forced-set
rank bounds run with integer arithmetic. The source graph reader and
2106-bank order/allocator/replay are retained unchanged. The upper-bound
replay checks all 169343 reads and the peak at event 3022. It is prior
work, not a new construction. Changed relation and dependency-path
certificates are rejected at their respective checks.

Only the snapshot component is bounded. Public fields, the source
accumulator, scratch, guides, guards, child and adapter backing, and
suspended parent storage retain their separate costs. No new physical
layout, runtime gain, full budget improvement or kappa follows. The five
native/owned/compiler/precision/analytic interfaces remain inherited.
Full physical and caller replays, historical suites, selected cold replay,
Lean and Docker were not run. This is source-aware author checking, not
independent human or formal-kernel acceptance. [CREDITS.md](CREDITS.md)
identifies the source authors and methods.

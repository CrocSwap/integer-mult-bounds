# One-repeat partitioned independent-walk obstruction on (3,5)/(4,4) at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names the one-repeat companions of the partitioned
`(3,5)` and `(4,4)` Hamilton layers at `Q=8` outside leave-alones through
#2851 and pending `cursor/independent-walks-onerepeat-8q-60b9`. Answers open
question 1 of that pending package: do non-distinct (one-repeat) label layers
on `(3,5)` / `(4,4)` improve on distinct-label `R=98` / `R=100`?

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? | Beats distinct? |
|---|---:|---:|---:|---|---|
| Distinct-label `(3,5)` (iw8q) | 10416000 | **98** | ≥500 | no | — |
| One-repeat `(3,5)` (this) | **2499840** | **112** | **≥528** | **no** | **no** |
| Distinct-label `(4,4)` (iw8q) | 14165760 | **100** | ≥504 | no | — |
| One-repeat×distinct `(4,4)` (this) | **1666560** | **112** | **≥528** | **no** | **no** |
| One-repeat×one-repeat `(4,4)` | **0** | — | — | — | — |

Every covering one-repeat dual on these shapes has exact `R=112`. Length-3
cannot host a one-repeat (closed zero edge). Abstract tariff
`38·8 + 2·112 + 2·0 = 528 > 436`. Distinct-label floors `98` / `100` are not
improved. Transfer-coupled / onerepeat-(2,6) / dirty-shadow / iw8q fixtures
are not edited.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-onerepeat-35-44/verify.py
python3.12 -I -O -B research/independent-walks-onerepeat-35-44/verify.py
python3.12 -I -B research/independent-walks-onerepeat-35-44/independent.py
python3.12 -I -B research/independent-walks-onerepeat-35-44/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-onerepeat-35-44
```

Expected:

```text
PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44_OBSTRUCTION one_repeat_35_min_R=112 ... tariff_floor=528 ... answers_independent_walks_onerepeat_8q_oq1 no_new_kappa
PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44 covering_35=2499840 covering_44=1666560 ... tariff_floor=528 ... no_new_kappa
PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-onerepeat-35-44 outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.
VERIFY.json timeout sum `180+180+180+600=1140≤1200`.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2851 / pending iw8q (distinct partitioned dual at Q=8), pending
iwor8q (one-repeat `(2,6)`; OQ1 answered here), #2779, #2846. Leave-alone
through #2851 including #2846, #2840, #2836, #2817, #2779, #2764, #2761,
#2715, #2686, #2677, #2643 is respected; those packages are not edited.
Pending `cursor/independent-walks-onerepeat-8q-60b9@5ee2550c` is not edited
or competed. Deferred soft-overlaps (transfer-coupled-dual/shapes;
shared-xor; host screens) are not opened.

## Open next questions

1. Does any third priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat) undercut
   `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after one-repeat companions.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alone packages through #2851; pending onerepeat-(2,6).
2. Does allowing two repeated nonzero labels (or a full non-distinct layer) on
   any `Q=8` partition undercut the distinct floors?
   Why it matters: closes the next relaxation after one-repeat.
   First step: census two-repeat length-5 multisets against distinct length-3.
   Blocked by: larger search; one-repeat already worsens.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, **#2779**, **#2846**,
**#2851** / pending **independent-walks-8q** (not edited), pending
**independent-walks-onerepeat-8q** (OQ1 answered here; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

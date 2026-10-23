# Transfer-coupled (5,1,1) obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers the
**transfer-coupled** open question left by partitioned independent walks on the
#2715 / #2761 lineage in the five-source common-B mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): can a shared
prefix, priced transfer `C≥1`, and divergent suffixes undercut tariff `436` at
total `Q=7` after a complete dirty bill?

Scoped to maximal-sharing shape `(p,a,b)=(5,1,1)` (two length-6 walks, prefix
counted once).

| Schedule | Covering pairs | Min R | Min fair X at min R | Tariff floor | Undercuts 436? |
|---|---:|---:|---:|---:|---|
| Partitioned dual (#indep-walks) | — | 112 | — | ≥490 | no |
| Transfer-coupled `(5,1,1)` | **8749440** | **84** | **9** | **≥452** | **no** |
| Same-walk even-subset (#2686) | — | 82 | — | ≥442 at X=6 | no |

Every covering distinct-label `(5,1,1)` dual has `R∈{84,88,90}`. On the
`R=84` layer, fair shared-prefix XOR billing with `C=1` is at least `9`
(champion prefix `(0,1,3,6,12)`, tips `(8,16)`). Abstract tariff
`38·7+2·84+2·9=452>436`. Spot samples of other shapes observe `R≥86`, which
already cannot undercut (`R+X≥86>85`).

## Reproduction

```sh
python3.12 -I -B research/transfer-coupled-7q-obstruction/verify.py
python3.12 -I -O -B research/transfer-coupled-7q-obstruction/verify.py
python3.12 -I -B research/transfer-coupled-7q-obstruction/independent.py
python3.12 -I -B research/transfer-coupled-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/transfer-coupled-7q-obstruction
```

Expected:

```text
PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION covering=8749440 min_R=84 min_fair_X=9 tariff_floor=452 answers_transfer_coupled_511 no_new_kappa
PASS_INDEPENDENT_TRANSFER_COUPLED_7Q covering=8749440 min_R=84 min_fair_X=9 tariff_floor=452 ... answers_transfer_coupled_511 no_new_kappa
PASS_TRANSFER_COUPLED_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/transfer-coupled-7q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2686, #2715, #2761, #2764, partitioned independent-walks OQ.
Leave-alone through #2764/#2761 including #2593, #2643, #2677, #2686, #2687,
#2715, #2761, #2764 is respected; those packages are not edited. Pending
`cursor/independent-walks-7q-60b9` is not edited or competed with on its
partitioned fixture. Deferred shared-XOR soft-overlap with #2643 and host
screens are not opened.

## Open next questions

1. Do other transfer-coupled shapes `(p,a,b)` with `p+a+b=7` (e.g. `(4,1,2)`,
   `(3,2,2)`) achieve covering `R≤84` after the same dirty bill?
   Why it matters: closes the remaining transfer-coupled shapes; spot samples
   already show observed min `R≥86`.
   First step: full set-based dual census for `(4,1,2)` and `(3,2,2)`.
   Blocked by: larger search.
2. Does the dirty-shadow sym-diff collapse extend verbatim to eight queries?
   Why it matters: companion of #2761/#2764 priced-shadow OQs.
   First step: reuse the snapshot lemma on length-8 slot lists.
   Blocked by: separate freestanding package; leave-alone #2761/#2764.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, open **#2715**, **#2761**, **#2764**,
partitioned independent-walks (OQ answered here for `(5,1,1)`; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

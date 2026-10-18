# One-repeat transfer-coupled (5,1,1) dual obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 1
of [#2836](https://github.com/CrocSwap/integer-mult-bounds/pull/2836)
(`research/transfer-coupled-all-shapes-7q`) on the five-source common-B
mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): do
non-distinct (one-repeat) label layers inside a transfer-coupled `(5,1,1)`
schedule improve on distinct-label `R=84`?

| Layer | Covering pairs | Exact min R | Tariff at X=0,C=1 | Undercuts 436? | Beats distinct 84? |
|---|---:|---:|---:|---|---|
| Distinct-label (#2836 / #2817) | 8749440 | **84** | ≥439 (needs X≥2) | no | — |
| Prefix-internal double | **2499840** | **98** | **463** | **no** | **no** |
| Suffix–prefix collision | **1666560** | **96** | **459** | **no** | **no** |
| Combined one-repeat | **4166400** | **96** | **459** | **no** | **no** |

Every covering one-repeat dual has `R∈{96,98}`. Combined minimum is `R=96`,
strictly worse than the distinct-label floor `84`. Abstract tariff
`38·7+2·96+1=459>436` already at `X=0`.

## Reproduction

```sh
python3.12 -I -B research/transfer-coupled-onerepeat-7q/verify.py
python3.12 -I -O -B research/transfer-coupled-onerepeat-7q/verify.py
python3.12 -I -B research/transfer-coupled-onerepeat-7q/independent.py
python3.12 -I -B research/transfer-coupled-onerepeat-7q/test_package.py
python3.12 -B scripts/research_package.py --package research/transfer-coupled-onerepeat-7q
```

Expected:

```text
PASS_TRANSFER_COUPLED_ONEREPEAT_7Q_OBSTRUCTION combined_min_R=96 ... tariff_floor=459 ... answers_all_shapes_oq1_onerepeat no_new_kappa
PASS_INDEPENDENT_TRANSFER_COUPLED_ONEREPEAT_7Q ... tariff_floor=459 ... no_new_kappa
PASS_TRANSFER_COUPLED_ONEREPEAT_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/transfer-coupled-onerepeat-7q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.
Requires a working `gcc` to build the local `dual.c` helper (pure-Python dual
fallback remains available).

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2817, #2836 (OQ1 answered here; package not edited). Leave-alone
through #2836 including #2817, #2779, #2764, #2761, #2715, #2687, #2686, #2677,
#2643, #2593, #2487 is respected. Pending `dirty-shadow-8q` under skeptical
review is not edited or competed. Deferred shared-XOR soft-overlap and host
screens are not opened.

## Open next questions

1. Does priced transfer `C>1` (or a dirt-correlated shared-prefix bill) change
   the distinct `(5,1,1)` floor enough to reopen an undercut at `X=2`?
   Why it matters: remaining sensitivity question from #2836 OQ2.
   First step: reprice the distinct covering census with `C=2`.
   Blocked by: model choice; leave-alone dirty-shadow fixtures not reopened.
2. Does any other priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   undercut `436` at `Q=8` after a complete dirty bill?
   Why it matters: remaining unequal-price handoff at eight queries.
   First step: name one new alphabet and census dirt-legal R against tariff 436.
   Blocked by: leave-alone packages through #2836; pending dirty-shadow-8q.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, **#2779**, **#2817**,
open **#2836** (all-shapes; OQ1 answered here; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

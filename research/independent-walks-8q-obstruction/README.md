# Partitioned independent-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names one new dirt-legal readout alphabet at `Q=8` outside
leave-alones through #2840 and pending
`cursor/transfer-coupled-onerepeat-7q-60b9`: two restored walks with distinct
slot lists, independent dirt, and dual even-parity readout. Answers open
question 2 of [#2840](https://github.com/CrocSwap/integer-mult-bounds/pull/2840)
(and the matching onerepeat handoff): does any other priced alphabet undercut
tariff `436` at eight queries after a complete dirty bill?

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? |
|---|---:|---:|---:|---|
| Same-walk even-subset (#2677) | — | ≥74 | ≥452 at X=0 | no |
| Partition `(2,6)` | **3916416** | **92** | **≥488** | **no** |
| Partition `(3,5)` | **10416000** | **98** | **≥500** | **no** |
| Partition `(4,4)` | **14165760** | **100** | **≥504** | **no** |

Global covering minimum is `R=92` on `(2,6)` only (spectrum `{92,96,104}`).
Abstract tariff `38·8 + 2·92 + 2·0 = 488 > 436`. Length-1 components are not
restored. Transfer-coupled / onerepeat / dirty-shadow fixtures are not edited.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-8q-obstruction/verify.py
python3.12 -I -O -B research/independent-walks-8q-obstruction/verify.py
python3.12 -I -B research/independent-walks-8q-obstruction/independent.py
python3.12 -I -B research/independent-walks-8q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-8q-obstruction
```

Expected:

```text
PASS_INDEPENDENT_WALKS_8Q_OBSTRUCTION partition_min_R=92 ... tariff_floor=488 ... answers_priced_alphabet_q8_oq no_new_kappa
PASS_INDEPENDENT_PARTITIONED_WALKS_8Q covering_26=3916416 covering_35=10416000 covering_44=14165760 partition_min_R=92 tariff_floor=488 ... no_new_kappa
PASS_INDEPENDENT_WALKS_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-8q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2677 (distinct-slot `R≥74` at Q=8), #2779 (partitioned walks at Q=7),
#2840 (dirty-shadow at Q=8; OQ2). Leave-alone through #2840 including #2836,
#2817, #2779, #2764, #2761, #2715, #2687, #2686, #2677, #2643, #2593, #2487 is
respected; those packages are not edited. Pending
`cursor/transfer-coupled-onerepeat-7q-60b9@90d879d1` is not edited or competed.
Deferred soft-overlaps (transfer-coupled-dual/shapes vs #2817/#2836; shared-xor;
host screens) are not opened.

## Open next questions

1. Do non-distinct (one-repeat) layers inside a partitioned Q=8 walk improve on
   `R=92` at `(2,6)`?
   Why it matters: closes the one-repeat companion of the Hamilton layer at
   eight queries without reopening transfer-coupled onerepeat.
   First step: allow one repeated nonzero label in the length-6 walk of `(2,6)`.
   Blocked by: larger search; expected to worsen coverage/cost.
2. Does any third priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)` (beyond
   same-walk / dirty-shadow / partitioned dual) undercut `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after this freestanding
   alphabet.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alone packages through #2840; pending onerepeat.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, **#2779**, open **#2840**
(dirty-shadow; OQ2 answered here for partitioned independent walks; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

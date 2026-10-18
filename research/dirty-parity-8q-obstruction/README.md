# Dirty-parity collapse at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 2
of [#2715](https://github.com/CrocSwap/integer-mult-bounds/pull/2715)
(`research/cheaper-readout-7q-obstruction`) in the five-source common-B
mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): does the
same dirty-parity collapse apply at eight queries for all-subset versus
even-subset floors?

| Readout model | Distinct-7 min R | One-dup min R | Tariff at X=0 | Undercuts 436? |
|---|---:|---:|---:|---:|
| All-subset (free, illegal dirt) | **61** | 66 | **426** | yes (not legal) |
| Even-subset (#2677) | 74 | — | 452 | no |
| Parity-repaired odd sets | **74** | **82** | **452** | **no** |

Free all-subset reaches `R=61` (hypothetical tariff `426 < 436` even at `X=0`).
Odd live-connector `R_m` counts leave connector dirt. Minimal zero-slot parity
repair restores even live-connector parity and collapses every covering
distinct-7 schedule to even-subset cost `R≥74` (tariff `≥452`), matching
#2677's distinct-slot floor.

## Reproduction

```sh
python3.12 -I -B research/dirty-parity-8q-obstruction/verify.py
python3.12 -I -O -B research/dirty-parity-8q-obstruction/verify.py
python3.12 -I -B research/dirty-parity-8q-obstruction/independent.py
python3.12 -I -B research/dirty-parity-8q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/dirty-parity-8q-obstruction
```

Expected:

```text
PASS_DIRTY_PARITY_8Q_OBSTRUCTION all_subset_min_R=61 parity_repair_min_R=74 hypothetical_tariff=426 repair_tariff=452 no_undercut_after_dirty_parity_repair answers_cr7q_oq2 matches_2677_even_floor no_new_kappa
PASS_INDEPENDENT_DIRTY_PARITY_8Q covering=2430400 all_min=61 repair_min=74 tariff_free=426 tariff_repair=452 ... answers_cr7q_oq2 no_new_kappa
PASS_DIRTY_PARITY_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/dirty-parity-8q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2677 (distinct-slot `R≥74` at Q=8), #2715 (OQ2). Leave-alone through
#2715 including #2593, #2643, #2677, #2686, #2687, #2715 is respected; those
packages are not edited. Pending `cursor/multi-connector-7q-60b9` dual-census
DEFER, deferred shared-XOR soft-overlap with #2643, and host screens are not
opened. No competing open PR on this freestanding Q=8 dirty-parity fixture at
refresh.

## Open next questions

1. Can a multi-connector alphabet with **independent walks** (partitioned or
   transfer-coupled queries, not the same slot list) undercut tariff 436 after
   charging both walks, transfers, and dirt?
   Why it matters: remaining dual-row direction after same-walk / dirty-parity
   collapses. First step: fix one transfer-coupled schedule and census dirt-legal
   R. Blocked by: pending `multi-connector-7q` dual-census repair; larger search.
2. Does the dirty-shadow sym-diff collapse extend verbatim to eight queries?
   Why it matters: closes the priced-shadow companion of #2715 OQ2 / mc7q OQ2.
   First step: reuse the snapshot lemma on length-8 slot lists.
   Blocked by: pending mc7q dual-census DEFER; larger search.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, open **#2715** (cheaper-readout; OQ2 answered
here; not edited), **TennisBowling / PR1524**, **Ross Richardson / PR943**, and
the retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

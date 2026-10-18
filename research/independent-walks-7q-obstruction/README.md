# Partitioned independent-walk obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers the
**partitioned independent-walks** open question on the #2715 /
multi-connector lineage in the five-source common-B mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): can two
restored walks with distinct slot lists, independent dirt, and dual
even-parity readout undercut tariff `436` at total `Q=7`?

| Dual schedule | Covering pairs | Exact R | Tariff floor (X≥0) | Undercuts 436? |
|---|---:|---:|---:|---|
| Same-walk even-subset (#2686) | — | ≥82 | ≥442 at X=6 | no |
| Partition `(2,5)` | **416640** | **112** | **≥490** | **no** |
| Partition `(3,4)` | **833280** | **112** | **≥490** | **no** |

Every covering partitioned dual has exact `R=112` (structural `F₂⁴` identity
on `(2,5)`; full dual census on `(3,4)`). Length-1 components are not restored.
Same-walk multi-connector remains the pending `multi-connector-7q` package.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-7q-obstruction/verify.py
python3.12 -I -O -B research/independent-walks-7q-obstruction/verify.py
python3.12 -I -B research/independent-walks-7q-obstruction/independent.py
python3.12 -I -B research/independent-walks-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-7q-obstruction
```

Expected:

```text
PASS_INDEPENDENT_WALKS_7Q_OBSTRUCTION partition_min_R=112 ... tariff_floor=490 ... answers_independent_walks_partitioned no_new_kappa
PASS_INDEPENDENT_PARTITIONED_WALKS_7Q covering_25=416640 covering_34=833280 partition_min_R=112 tariff_floor=490 ... no_new_kappa
PASS_INDEPENDENT_WALKS_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-7q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2686, #2715, pending same-walk multi-connector OQ. Leave-alone
through #2715 including #2593, #2643, #2677, #2686, #2687, #2715 is respected;
those packages are not edited. Pending `cursor/multi-connector-7q-60b9` and
`cursor/dirty-parity-8q-60b9` are not edited or competed with on their fixtures.
Deferred shared-XOR soft-overlap with #2643 and host screens are not opened.

## Open next questions

1. Can a **transfer-coupled** dual (shared prefix, priced transfer `C≥1`,
   divergent suffixes) undercut tariff 436 after charging walks+transfers+dirt
   at total `Q=7`?
   Why it matters: remaining independent-walk direction after partitioned
   collapse.
   First step: fix shapes `(p,a,b)` with `p+a+b=7` and census dirt-legal R with
   fair shared-prefix XOR billing.
   Blocked by: larger search; pending same-walk mc7q not a blocker for this
   freestanding fixture.
2. Do non-distinct (repeat-label) layers inside a partitioned walk improve on
   `R=112`?
   Why it matters: closes the one-repeat companion of the Hamilton layer.
   First step: allow one repeated nonzero label in the length-5 walk of `(2,5)`.
   Blocked by: larger search; expected to worsen coverage/cost.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, open **#2715**, pending same-walk
multi-connector (OQ answered here for the partitioned case; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

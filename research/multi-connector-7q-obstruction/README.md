# Multi-connector / priced-shadow readout obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 1
of [#2715](https://github.com/CrocSwap/integer-mult-bounds/pull/2715)
(`research/cheaper-readout-7q-obstruction`) in the five-source common-B
mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): can a
multi-connector readout alphabet reach `R≤78` at `Q=7` with `X=6` after a
complete dirty bill?

| Alphabet | Distinct-6 min R | One-repeat R | Tariff at X=6 | Undercuts 436? |
|---|---:|---:|---:|---|
| Even-subset (#2686) | 82 | 96 | 442 | no |
| Dirty shadow (legal) | **82** | 96 | **442** | **no** |
| Dual indep. same-walk | **82** | 96 | **442** | **no** |
| Clean shadow (illegal) | **71** | 88 | **420** | yes (not legal) |

Dirty shadow collapses to even-subset by sym-diff with the snapshot index.
Independent dual same-walk equals even-subset: each covering set computes
`Σ min_a (e[a]+e[a⊕m])` and checks the even-subset triangle inequality
(machine-checked on all `583296` covering lists). A dirt-free shadow would
undercut, but inherits dirt under PR1898 and fails the dirty bill.

## Reproduction

```sh
python3.12 -I -B research/multi-connector-7q-obstruction/verify.py
python3.12 -I -O -B research/multi-connector-7q-obstruction/verify.py
python3.12 -I -B research/multi-connector-7q-obstruction/independent.py
python3.12 -I -B research/multi-connector-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/multi-connector-7q-obstruction
```

Expected:

```text
PASS_MULTI_CONNECTOR_7Q_OBSTRUCTION legal_min_R=82 ... answers_cr7q_oq1 no_new_kappa
PASS_INDEPENDENT_MULTI_CONNECTOR_7Q covering=583296 legal_min=82 ... answers_cr7q_oq1 no_new_kappa
PASS_MULTI_CONNECTOR_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/multi-connector-7q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2677, #2686, #2715 (OQ1). Leave-alone through #2715 including
#2593, #2643, #2677, #2686, #2687, #2715 is respected; those packages are not
edited. Deferred shared-XOR soft-overlap with #2643 and host screens are not
opened. No competing open PR on this freestanding multi-connector fixture at
refresh.

## Open next questions

1. Can a multi-connector alphabet with **independent walks** (partitioned or
   transfer-coupled queries, not the same slot list) undercut tariff 436 after
   charging both walks, transfers, and dirt?
   Why it matters: remaining dual-row direction after same-walk collapse.
   First step: fix one transfer-coupled Q=7+C schedule and census dirt-legal R.
   Blocked by: larger search; leave-alone host screens deferred.
2. Does the dirty-shadow sym-diff collapse extend verbatim to eight queries?
   Why it matters: extends the unequal-price handoff beyond Q=7.
   First step: reuse the snapshot lemma on length-8 slot lists.
   Blocked by: larger search.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, open **#2715** (cheaper-readout; OQ1 answered
here; not edited), **TennisBowling / PR1524**, **Ross Richardson / PR943**, and
the retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

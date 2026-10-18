# Partitioned independent-walk obstruction at nine queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names the **Q=9 partitioned independent dual companion**
of [#2851](https://github.com/CrocSwap/integer-mult-bounds/pull/2851) on
shapes `(2,7)`, `(3,6)`, and `(4,5)`. Answers preferred next20 and open
question 2 of pending
`cursor/independent-walks-threerepeat-8q-60b9@94b14c36`. Soft-overlap-safe vs
the Q=8 leave-alone cluster (new query count; no leave-alone reopen).

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? | vs same-walk Q9 466? |
|---|---:|---:|---:|---|---|
| Same-walk Q=9 (#2677) | — | ≥62 | ≥466 | no | — |
| Partitioned `(2,7)` (this) | **20512576** | **80** | **≥502** | **no** | **above** |
| Partitioned `(3,6)` (this) | **69370560** | **88** | **≥518** | **no** | **above** |
| Partitioned `(4,5)` (this) | **122561600** | **92** | **≥526** | **no** | **above** |

Global covering minimum is `R=80` on `(2,7)` (spectrum
`{80,82,86,88,92,100}`). Abstract tariff `38·9 + 2·80 + 2·0 = 502 > 436`
and also above the same-walk Q=9 floor `466`. Partitioned duals at nine
queries cannot undercut the six-query endpoint.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-9q/verify.py
python3.12 -I -O -B research/independent-walks-9q/verify.py --quick
python3.12 -I -B research/independent-walks-9q/independent.py
python3.12 -I -B research/independent-walks-9q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-9q
```

Expected:

```text
PASS_INDEPENDENT_WALKS_9Q_OBSTRUCTION partition_min_R=80 ... tariff_floor=502 ... answers_threerepeat_oq2 no_new_kappa
PASS_INDEPENDENT_WALKS_9Q_QUICK partition_min_R=80 tariff_floor=502 ... answers_threerepeat_oq2 no_new_kappa
PASS_INDEPENDENT_PARTITIONED_WALKS_9Q covering_27=20512576 ... tariff_floor=502 ... answers_threerepeat_oq2 no_new_kappa
PASS_INDEPENDENT_WALKS_9Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-9q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.
Full census is the default verify; `--quick` is the `-O` / package-test path.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2851 (distinct partitioned dual at Q=8), #2677 (same-walk Q=9
floor 466), pending threerepeat tip (OQ2 answered here),
#2867/#2861/#2860/#2858/#2846/#2840/#2779. Leave-alone through #2867
including #2861, #2860, #2858, #2851, #2846, #2840, #2836, #2817, #2779,
#2764, #2761 is respected; those packages are not edited. Pending
`cursor/independent-walks-threerepeat-8q-60b9@94b14c36` is not edited or
competed. Deferred soft-overlaps (transfer-coupled-dual/shapes; shared-XOR;
host screens) are not opened.

## Open next questions

1. Does any sixth priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat /
   two-repeat / shared-dirt / three-repeat) undercut `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff on the Q=8 cluster.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alones through #2867; pending three-repeat; deferred soft-overlaps.
2. Does a mixed shared-dirt + excess (e.g. shared-dirt with one-repeat)
   partitioned schedule at `Q=8` undercut the shared-dirt floor `R=82`?
   Why it matters: combines dirt-coupling and excess axes without reopen.
   First step: fix mixed cost and census distinct-label `(2,6)`.
   Blocked by: larger search; expected not to undercut 436 even if R improves.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2779**, open **#2851** / **#2867** / **#2861** / **#2860** /
**#2858** (leave-alone; not edited), pending threerepeat tip (OQ2 answered
here; not edited or competed), open **#2846** / **#2840** / **#2836** /
**#2817** / **#2764** / **#2761** (leave-alone), **TennisBowling / PR1524**,
**Ross Richardson / PR943**, and the retained mutable-source lineage. Live
input pin: `research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by
Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

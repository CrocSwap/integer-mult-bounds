# Shared-dirt partitioned-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names one new dirt-legal readout alphabet at `Q=8` beyond
same-walk / dirty-shadow / partitioned dual / one-repeat / two-repeat:
**shared-dirt** (single coefficient / joint even live-read parity) duals on
distinct partitioned walks. Answers preferred next18 and open questions 1–2 of
pending `cursor/independent-walks-tworepeat-8q-60b9`. Soft-overlap-safe vs
deferred shared-XOR (R-side dirt coupling only).

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? | Beats independent? |
|---|---:|---:|---:|---|---|
| Distinct partitioned (#2851) | — | 92 | ≥488 | no | — |
| One-repeat (pending) | — | 112 | ≥528 | no | — |
| Two-repeat (pending) | 0 | — | — | no | — |
| Shared-dirt `(2,6)` (this) | **3916416** | **82** | **≥468** | **no** | **yes (vs 92)** |
| Shared-dirt `(3,5)` (this) | **10416000** | **82** | **≥468** | **no** | **yes (vs 98)** |
| Shared-dirt `(4,4)` (this) | **14165760** | **82** | **≥468** | **no** | **yes (vs 100)** |

Global covering minimum is `R=82` on every shape (spectrum `{82,88,96}`).
Abstract tariff `38·8 + 2·82 + 2·0 = 468 > 436`. Shared dirt undercuts
independent-dirt floors but cannot undercut the six-query endpoint.

## Reproduction

```sh
python3.12 -I -B research/shared-dirt-walks-8q/verify.py
python3.12 -I -O -B research/shared-dirt-walks-8q/verify.py
python3.12 -I -B research/shared-dirt-walks-8q/independent.py
python3.12 -I -B research/shared-dirt-walks-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/shared-dirt-walks-8q
```

Expected:

```text
PASS_SHARED_DIRT_WALKS_8Q_OBSTRUCTION partition_min_R=82 ... tariff_floor=468 ... answers_fourth_priced_alphabet_q8 soft_overlap_shared_xor_safe no_new_kappa
PASS_SHARED_DIRT_WALKS_8Q covering_26=3916416 covering_35=10416000 covering_44=14165760 partition_min_R=82 tariff_floor=468 ... no_new_kappa
PASS_SHARED_DIRT_WALKS_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/shared-dirt-walks-8q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2851 (distinct partitioned dual), pending tworepeat (OQ answered here),
#2858 / onerepeat tips, #2846/#2840/#2779/#2677. Leave-alone through #2858
including #2851, #2846, #2840, #2836, #2817, #2779, #2764, #2761 is respected;
those packages are not edited. Pending
`cursor/independent-walks-onerepeat-8q-60b9@b07bc1e1` and
`cursor/independent-walks-tworepeat-8q-60b9@c4581aaf` are not edited or
competed. Deferred soft-overlaps (transfer-coupled-dual/shapes; shared-XOR as
X-sharing; host screens) are not opened — shared-dirt is R-side only.

## Open next questions

1. Does any fifth priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat /
   two-repeat / shared-dirt) undercut `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after shared-dirt is closed.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alones through #2858/#2851; pending onerepeat/tworepeat;
   deferred transfer-coupled-dual/shapes and host screens.
2. Does a three-walk partitioned shared-dirt schedule (e.g. `(2,2,4)`) undercut
   the two-walk shared-dirt floor `R=82`?
   Why it matters: extends shared-dirt to three restored components.
   First step: fix triple shared-dirt cost and census distinct-label `(2,2,4)`.
   Blocked by: larger search; expected not to undercut 436 even if R improves
   toward 74.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2779**, open **#2851** / **#2858** (leave-alone; not edited),
pending tworepeat tip (OQ answered here; not edited), pending onerepeat tip
(leave-alone), open **#2846** / **#2840** / **#2836** / **#2817** / **#2764** /
**#2761** (leave-alone), **#2643** (shared-XOR soft-overlap not opened),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

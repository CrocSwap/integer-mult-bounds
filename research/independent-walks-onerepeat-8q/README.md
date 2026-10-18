# One-repeat partitioned independent-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names the one-repeat companion of the partitioned
`(2,6)` Hamilton layer at `Q=8` outside leave-alones through #2846 and
pending `cursor/independent-walks-8q-60b9`. Answers open question 1 of that
pending package: do non-distinct (one-repeat) label layers inside a
partitioned `Q=8` walk improve on distinct-label `R=92` at `(2,6)`?

| Dual schedule | Covering pairs | Exact min R | Tariff floor (X≥0) | Undercuts 436? | Beats distinct 92? |
|---|---:|---:|---:|---|---|
| Distinct-label `(2,6)` (iw8q) | 3916416 | **92** | ≥488 | no | — |
| One-repeat long `(2,6)` (this) | **59996160** | **112** | **≥528** | **no** | **no** |

Every covering one-repeat dual has exact `R=112`. Only rank-4 longs cover,
always with `Σe=40` and `σ` outside the long span (16 choices), so
`R=2·40+32=112`. Abstract tariff `38·8 + 2·112 + 2·0 = 528 > 436`. Distinct-
label floor `92` is not improved. Transfer-coupled / onerepeat / dirty-shadow
/ iw8q fixtures are not edited.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-onerepeat-8q/verify.py
python3.12 -I -O -B research/independent-walks-onerepeat-8q/verify.py
python3.12 -I -B research/independent-walks-onerepeat-8q/independent.py
python3.12 -I -B research/independent-walks-onerepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-onerepeat-8q
```

Expected:

```text
PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q_OBSTRUCTION one_repeat_min_R=112 ... tariff_floor=528 ... answers_independent_walks_8q_oq1_onerepeat no_new_kappa
PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q covering=59996160 ... one_repeat_min_R=112 tariff_floor=528 ... no_new_kappa
PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-onerepeat-8q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, pending iw8q (distinct partitioned dual at Q=8; OQ1 answered here),
#2779 (partitioned walks at Q=7), #2846 (transfer-coupled onerepeat at Q=7).
Leave-alone through #2846 including #2840, #2836, #2817, #2779, #2764, #2761,
#2715, #2687, #2686, #2677, #2643, #2593, #2487 is respected; those packages
are not edited. Pending `cursor/independent-walks-8q-60b9@379aaf8f` is not
edited or competed. Deferred soft-overlaps (transfer-coupled-dual/shapes;
shared-xor; host screens) are not opened.

## Open next questions

1. Do one-repeat layers on partitions `(3,5)` or `(4,4)` improve on their
   distinct-label floors (`98` / `100`)?
   Why it matters: closes the remaining one-repeat companions at eight queries.
   First step: allow one repeated nonzero label in either walk of `(3,5)`.
   Blocked by: larger search; expected to worsen like `(2,6)`.
2. Does any third priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat) undercut
   `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after this freestanding
   alphabet.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alone packages through #2846; pending iw8q.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, **#2779**, **#2846**,
pending **independent-walks-8q** (OQ1 answered here; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

# Three-repeat partitioned-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names one new dirt-legal readout alphabet at `Q=8` beyond
same-walk / dirty-shadow / partitioned dual / one-repeat / two-repeat /
shared-dirt: **three-repeat** (excess-3) layers inside partitioned independent
duals on shapes `(2,6)`, `(3,5)`, and `(4,4)`. Answers preferred next19 and
open question 1 of pending `cursor/shared-dirt-walks-8q-60b9@fc3a2cb3`.

| Dual schedule | Valid objects | Exact covering | Undercuts 436? |
|---|---:|---:|---|
| Distinct partitioned (#2851) | — | min R=92 | no |
| One-repeat (pending tips) | — | min R=112 | no |
| Two-repeat (pending) | — | 0 | no |
| Shared-dirt (pending) | — | min R=82 | no |
| Three-repeat `(2,6)` | **930** walks | **0** | **no** |
| Three-repeat `(3,5)` | **0** multisets | **0** | **no** |
| Three-repeat `(4,4)` | **0** walks | **0** | **no** |

Span lemmas: `(2,6)` long span ≤4 so coset union ≤8; `(3,5)` shape `{d:4}`
never restores; `(4,4)` excess 3 impossible on length-4. No covering `R`
exists, so the alphabet cannot undercut tariff `436`. Soft-overlap with
pending shared-dirt is avoided (independent excess axis; no dirt coupling).

## Reproduction

```sh
python3.12 -I -B research/independent-walks-threerepeat-8q/verify.py
python3.12 -I -O -B research/independent-walks-threerepeat-8q/verify.py
python3.12 -I -B research/independent-walks-threerepeat-8q/independent.py
python3.12 -I -B research/independent-walks-threerepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-threerepeat-8q
```

Expected:

```text
PASS_INDEPENDENT_WALKS_THREEREPEAT_8Q_OBSTRUCTION covering_26=0 covering_35=0 covering_44=0 ... answers_fifth_priced_alphabet_q8 no_undercut_436 no_new_kappa
PASS_INDEPENDENT_WALKS_THREEREPEAT_8Q covering_26=0 covering_35=0 ... answers_fifth_priced_alphabet_q8 no_undercut_436 no_new_kappa
PASS_INDEPENDENT_WALKS_THREEREPEAT_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-threerepeat-8q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2851 (distinct partitioned dual at Q=8), pending onerepeat /
tworepeat / shared-dirt tips, #2846/#2840/#2779/#2677. Leave-alone through
#2861 including #2860, #2858, #2851, #2846, #2840, #2836, #2817, #2779,
#2764, #2761 is respected; those packages are not edited. Pending
`cursor/shared-dirt-walks-8q-60b9@fc3a2cb3` is not edited or competed
(OQ1 answered here on a non-competing excess axis). Deferred soft-overlaps
(transfer-coupled-dual/shapes; shared-xor; host screens) are not opened.

## Open next questions

1. Does any sixth priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat /
   two-repeat / shared-dirt / three-repeat) undercut `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after three-repeat is closed.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alones through #2861/#2860/#2858/#2851; pending shared-dirt;
   deferred soft-overlaps.
2. Does a Q=9 partitioned independent dual companion undercut tariff `436`
   (beyond the same-walk Q=9 floor `466` of #2677)?
   Why it matters: extends the partitioned dual alphabet off the Q=8 leave-alone
   cluster without competing with shared-dirt.
   First step: census distinct-label partitions `(2,7)`/`(3,6)`/`(4,5)`.
   Blocked by: larger search; expected not to undercut 436 if R≥62.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2779**, open **#2851** / **#2861** / **#2860** / **#2858**
(leave-alone; not edited), pending shared-dirt tip (OQ1 answered here; not
edited or competed), open **#2846** / **#2840** / **#2836** / **#2817** /
**#2764** / **#2761** (leave-alone), **TennisBowling / PR1524**, **Ross
Richardson / PR943**, and the retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

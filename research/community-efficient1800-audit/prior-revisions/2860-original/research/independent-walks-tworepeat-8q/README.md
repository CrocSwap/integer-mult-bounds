# Two-repeat partitioned-walk obstruction at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Freestanding
`#840`-style priced obstruction under
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at
`(b,a,x)=(38,2,2)`. Names one new dirt-legal readout alphabet at `Q=8` beyond
same-walk / dirty-shadow / partitioned dual / one-repeat: **two-repeat**
(excess-2) layers inside partitioned independent duals on shapes `(2,6)`,
`(3,5)`, and `(4,4)`. Answers preferred next17 and open questions 1–2 of pending
`cursor/independent-walks-onerepeat-35-44-60b9`.

| Dual schedule | Valid objects | Exact covering | Undercuts 436? |
|---|---:|---:|---|
| Distinct partitioned (#2851) | — | min R=92 | no |
| One-repeat (pending tips) | — | min R=112 | no |
| Two-repeat `(2,6)` | **26970** walks | **0** | **no** |
| Two-repeat `(3,5)` | **465** multisets | **0** | **no** |
| Two-repeat `(4,4)` | **0** walks | **0** | **no** |

Span/sumset lemmas: `(2,6)` long span ≤8 so coset union ≤16; `(3,5)` sumset ≤16;
`(4,4)` shape `{d:3}` never restores. No covering `R` exists, so the alphabet
cannot undercut tariff `436`.

## Reproduction

```sh
python3.12 -I -B research/independent-walks-tworepeat-8q/verify.py
python3.12 -I -O -B research/independent-walks-tworepeat-8q/verify.py
python3.12 -I -B research/independent-walks-tworepeat-8q/independent.py
python3.12 -I -B research/independent-walks-tworepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-tworepeat-8q
```

Expected:

```text
PASS_INDEPENDENT_WALKS_TWOREPEAT_8Q_OBSTRUCTION covering_26=0 covering_35=0 covering_44=0 ... answers_third_priced_alphabet_q8 no_undercut_436 no_new_kappa
PASS_INDEPENDENT_WALKS_TWOREPEAT_8Q covering_26=0 covering_35=0 ... no_undercut_436 no_new_kappa
PASS_INDEPENDENT_WALKS_TWOREPEAT_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-walks-tworepeat-8q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2851 (distinct partitioned dual at Q=8), pending onerepeat tips,
#2846/#2840/#2779/#2677. Leave-alone through #2851 including #2846, #2840,
#2836, #2817, #2779, #2764, #2761 is respected; those packages are not edited.
Pending `cursor/independent-walks-onerepeat-8q-60b9@b07bc1e1` and
`cursor/independent-walks-onerepeat-35-44-60b9@8bd3d298` are not edited or
competed. Deferred soft-overlaps (transfer-coupled-dual/shapes; shared-xor;
host screens) are not opened.

## Open next questions

1. Does any fourth priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)`
   (beyond same-walk / dirty-shadow / partitioned dual / one-repeat / two-repeat)
   undercut `436` at `Q=8`?
   Why it matters: remaining unequal-price handoff after two-repeat is closed.
   First step: name one new alphabet outside leave-alones and census dirt-legal R.
   Blocked by: leave-alones through #2851; pending onerepeat; deferred soft-overlaps.
2. Does a shared-dirt (single coefficient) dual on distinct partitioned walks
   undercut the independent-dirt floors?
   Why it matters: changes the dual cost from independent `min_a` to a coupled
   readout.
   First step: fix shared-dirt dual cost and census `(2,6)` distinct labels.
   Blocked by: soft-overlap risk with shared-XOR leave-alone.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2779**, open **#2851** (distinct partitioned; leave-alone; not
edited), pending onerepeat tips (OQ answered here; not edited), open **#2846** /
**#2840** / **#2836** / **#2817** / **#2764** / **#2761** (leave-alone),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

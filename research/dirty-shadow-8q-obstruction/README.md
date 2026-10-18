# Dirty-shadow sym-diff collapse at eight queries

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 2
of [#2761](https://github.com/CrocSwap/integer-mult-bounds/pull/2761)
(`research/multi-connector-7q-obstruction`) and the matching handoff in
[#2764](https://github.com/CrocSwap/integer-mult-bounds/pull/2764)
(`research/dirty-parity-8q-obstruction`) in the five-source common-B
mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): does the
dirty-shadow sym-diff collapse extend verbatim to eight queries?

| Alphabet | Distinct-7 min R | One-dup min R | Tariff at X=0 | Undercuts 436? |
|---|---:|---:|---:|---|
| Even-subset (#2677) | 74 | 82 | 452 | no |
| Dirty shadow (legal) | **74** | **82** | **452** | **no** |
| Clean shadow (illegal) | **67** | **71** | **438** | **no** (still ≥436) |

Dirty shadow collapses to even-subset by sym-diff with the snapshot index on
every covering distinct-7 list (`matches_even=2430400`) and every covering
one-duplicate multiset (`matches_even=4083072`). A dirt-free shadow would reach
`R=67` (tariff `438`) but still fails to undercut `436` at `X=0` and remains
illegal under PR1898 inherited dirt.

## Reproduction

```sh
python3.12 -I -B research/dirty-shadow-8q-obstruction/verify.py
python3.12 -I -O -B research/dirty-shadow-8q-obstruction/verify.py
python3.12 -I -B research/dirty-shadow-8q-obstruction/independent.py
python3.12 -I -B research/dirty-shadow-8q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/dirty-shadow-8q-obstruction
```

Expected:

```text
PASS_DIRTY_SHADOW_8Q_OBSTRUCTION dirty_shadow_min_R=74 ... answers_mc7q_oq2 matches_2677_even_floor no_new_kappa
PASS_INDEPENDENT_DIRTY_SHADOW_8Q covering=2430400 one_dup=4083072 dirty_min=74 ... answers_mc7q_oq2 no_new_kappa
PASS_DIRTY_SHADOW_8Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/dirty-shadow-8q-obstruction outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2677 (distinct-slot `R≥74` at Q=8), #2761 (dirty-shadow at Q=7; OQ2),
#2764 (dirty-parity at Q=8; OQ2). Freestanding package name
`dirty-shadow-8q-obstruction` — does **not** touch
`research/transfer-coupled-7q-obstruction/` (#2817) or other leave-alones through
#2817. Deferred transfer-coupled-dual soft-overlap, shared-XOR, and host screens
are not opened. No competing open PR on this Q=8 dirty-shadow fixture at refresh.

## Open next questions

1. Can a multi-connector alphabet with **independent walks** (partitioned or
   transfer-coupled shapes other than the open #2817 `(5,1,1)` package) undercut
   tariff 436 after charging both walks, transfers, and dirt?
   Why it matters: remaining dual-row direction after same-walk / dirty-shadow /
   dirty-parity collapses.
   First step: fix one new transfer-coupled shape with a new checkable fact
   beyond #2817's `(5,1,1)`.
   Blocked by: open #2817 package leave-alone; larger search.
2. Does any other priced readout alphabet under PR1898 `(b,a,x)=(38,2,2)` undercut
   436 at Q=8 after a complete dirty bill?
   Why it matters: closes remaining unequal-price handoffs at eight queries.
   First step: name one new alphabet and census dirt-legal R against tariff 436.
   Blocked by: leave-alone packages through #2817; larger search.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, open **#2715**, open **#2761** (mc7q; OQ2
answered here; not edited), open **#2764** (dirty-parity-8q; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

# Transfer-coupled all-shapes dual obstruction at seven queries

**Scoped obstruction / priced alphabet; no new kappa.** Completes the
transfer-coupled census across every unordered shape `(p,a,b)` with
`p+a+b=7`, answering open question 1 of
[#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779) and the
remaining-shapes follow-up left by the maximal-share `(5,1,1)` package on the
five-source common-B mutable-source alphabet of
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): after a
priced transfer `C≥1` and fair shared-prefix XOR, can any transfer-coupled dual
undercut tariff `436`?

| Shape `(p,a,b)` | Covering pairs | Exact min R | Tariff floor (C=1) | Undercuts 436? |
|---|---:|---:|---:|---|
| Same-walk even-subset (#2686) | — | ≥82 | ≥442 at X=6 | no |
| Partitioned dual (#2779) | — | ≥112 | ≥490 at X=0 | no |
| `(5,1,1)` transfer-coupled | **8749440** | **84** | **≥439** (X≥2) | **no** |
| `(4,1,2)` | **34997760** | **86** | **≥439** at X=0 | **no** |
| All other unordered shapes | — | **≥88** | **≥443** at X=0 | **no** |

Global covering minimum is `R=84` at shape `(5,1,1)` only. Gray `X=0` covering
on that shape is empty, and fair path `X` is always even, so covering forces
`X≥2` and tariff `≥439>436`. Every other unordered shape already has `R≥86`,
hence tariff `≥439` even at `X=0`.

## Reproduction

```sh
python3.12 -I -B research/transfer-coupled-all-shapes-7q/verify.py
python3.12 -I -O -B research/transfer-coupled-all-shapes-7q/verify.py
python3.12 -I -B research/transfer-coupled-all-shapes-7q/independent.py
python3.12 -I -B research/transfer-coupled-all-shapes-7q/test_package.py
python3.12 -B scripts/research_package.py --package research/transfer-coupled-all-shapes-7q
```

Expected:

```text
PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION global_min_R=84 ... tariff_floor=439 ... answers_independent_walks_transfer_coupled no_new_kappa
PASS_INDEPENDENT_TRANSFER_COUPLED_7Q companions=7 ... tariff_floor=439 ... no_new_kappa
PASS_TRANSFER_COUPLED_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/transfer-coupled-all-shapes-7q outcome=completed
```

Default verify is read-only. Admission uses `need()`; `-O` also passes.
Requires a working `gcc` to build the local `dual.c` helper (pure-Python dual
fallback remains available).

## Overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643, #2686, #2715, #2761, #2779, and the pending `(5,1,1)`-only
transfer-coupled package (not edited; this package supplies the missing
full-shape census). Leave-alone through #2779 including #2764, #2761, #2715,
#2687, #2686, #2677, #2643, #2593, #2487 is respected; those packages are not
edited. Deferred shared-XOR soft-overlap and host screens are not opened.

## Open next questions

1. Do non-distinct (repeat-label) layers inside a transfer-coupled schedule
   improve on `R=84` at `(5,1,1)`?
   Why it matters: closes the one-repeat companion of the distinct-label layer.
   First step: allow one repeated nonzero label in the length-6 walks of `(5,1,1)`.
   Blocked by: larger search; expected to worsen coverage/cost.
2. Does priced transfer `C>1` (or a dirt-correlated shared-prefix bill) change
   the `(5,1,1)` floor enough to reopen an undercut at `X=2`?
   Why it matters: tests sensitivity of the 439 floor to transfer pricing.
   First step: reprice the same covering census with `C=2` and correlated prefix dirt.
   Blocked by: model choice; leave-alone dirty-shadow fixtures not reopened.

## Credit

Credit **Arham Tahir / PR1898**, **ywz65 / PR2455**, **PR1370**, fork **789q** /
**#2677**, **#2643**, **#2686**, **#2715**, **#2761**, **#2779**, the pending
`(5,1,1)`-only transfer-coupled package (remaining-shapes OQ answered here; not
edited), **TennisBowling / PR1524**, **Ross Richardson / PR943**, and the
retained mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

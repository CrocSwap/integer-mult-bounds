# Odd-cardinality cheaper readout cannot undercut 436 after dirty-parity repair

**Scoped obstruction / priced alphabet; no new kappa.** Answers open question 1
of [#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686)
(`research/seven-query-r-floor`) in the five-source common-B mutable-source
alphabet of
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898).

Define the natural **all-subset** (odd-cardinality allowed) connector-state
readout score on Q=7 walks. Free of dirty-cancellation, it reaches **R=66**
(spectrum `{66,72}` on distinct-6 covers; one-repeat layer `R=80`) and would
tariff **410 < 436** at `X=6`. But odd live-connector `R_m` counts leave
arbitrary connector dirt on those outputs. The minimal **zero-slot parity
repair** restores even live-connector parity and collapses every covering
schedule to even-subset cost **R≥82** (tariff **442**), matching #2686.

| Readout model | Distinct-6 min R | One-repeat R | Tariff at X=6 | Undercuts 436? |
|---|---:|---:|---:|---|
| All-subset (free, illegal dirt) | **66** | 80 | **410** | yes (not legal) |
| Even-subset (#2686) | 82 | 96 | 442 | no |
| Parity-repaired odd sets | **82** | 96 | **442** | **no** |

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/cheaper-readout-7q-obstruction/verify.py
python3.12 -I -O -B research/cheaper-readout-7q-obstruction/verify.py
python3.12 -I -B research/cheaper-readout-7q-obstruction/independent.py
python3.12 -I -B research/cheaper-readout-7q-obstruction/test_package.py
python3.12 -B scripts/research_package.py --package research/cheaper-readout-7q-obstruction
```

Expected:

```text
PASS_CHEAPER_READOUT_7Q_OBSTRUCTION all_subset_min_R=66 parity_repair_min_R=82 hypothetical_tariff=410 repair_tariff=442 no_undercut_after_dirty_parity_repair answers_7qr_oq1 no_new_kappa
PASS_INDEPENDENT_CHEAPER_READOUT_7Q covering=583296 all_min=66 repair_min=82 tariff_free=410 tariff_repair=442 answers_7qr_oq1 no_new_kappa
PASS_CHEAPER_READOUT_7Q_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/cheaper-readout-7q-obstruction outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, #2643 (XOR floor), #2677 / path-lowered 789q invoice, #2686 (even-subset
R floor; OQ1). Leave-alone through #2686 including #2593, #2643, #2677 is
respected; pending `cursor/odd-kernel-query-pair-60b9@c319093b` is not edited.
Deferred shared-XOR soft-overlap with #2643 and host screens are not opened.

## Open next questions

1. Can a **multi-connector** readout alphabet (two live connectors, or a priced
   shadow snapshot) reach `R≤78` at `Q=7` with `X=6` after a complete dirty bill?
   Why it matters: the remaining cheaper-alphabet direction after odd-cardinality
   collapse. First step: fix one dual-connector interface, charge both walks and
   dirt cancellation, and census length-7 covers. Blocked by: no dual-connector
   fixture is priced here.
2. Does the same dirty-parity collapse apply at eight queries for all-subset
   versus even-subset floors?
   Why it matters: extends the unequal-price handoff beyond Q=7. First step:
   reuse the repair lemma on length-8 slot lists and compare to #2677's R≥74
   distinct-slot floor. Blocked by: larger search.

## Credit

Credit **Arham Tahir / PR1898** (alphabet, endpoint tariff), **ywz65 / PR2455**,
**PR1370**, the fork **789q invoice** / **#2677**, open **#2643** and **#2686**
(even-subset R floor; OQ1 answered here; not edited), **TennisBowling / PR1524**,
**Ross Richardson / PR943**, and the retained mutable-source lineage. Live input
pin: `research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.

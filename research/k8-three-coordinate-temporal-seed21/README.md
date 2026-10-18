# Three-coordinate temporal schedule on the original k8 word

This package exactly optimizes one bounded three-coordinate dyadic schedule on the pinned PR1094 original k8 scalar word. It adds L367 to PR1380's L225/L350 interaction and optimizes all three coordinates together in both orientations.

## Result

The exact domain is `[-4,4]^3` at every incident ADD, with the gauge returned to zero at each nonscalar boundary. All 729 exponent triples were covered at each of 347 incident ADDs in each orientation, split into 23 independent event blocks. Two distinct pairwise shared ADDs couple the paths: source event 19,531 for L225/L367 and event 22,786 for L225/L350. L350 and L367 do not share an ADD.

| Orientation | Original complex primitives | Three-coordinate word | Saving | Added scale macros / real work |
|---|---:|---:|---:|---:|
| Forward | 149,002 | 148,234 | 768 | 71 / 80 |
| Backward | 149,018 | 148,250 | 768 | 76 / 86 |

This is 294 complex primitives below PR1380's exact L225/L350 pair schedule per orientation. The paid recursive profile is unchanged. Prefix ceilings and denominator-depth bounds stay at 52 bits / 22 forward and 68 bits / 26 backward. Both complete scalar words replay on all 712 formal columns; the three changed helpers are restored and the eight private centers are cleared.

This is a finite scalar-circuit result on the original PR1094 word. It does not improve the selected kappa, beat the later PR1263 static word, establish optimality outside this three-helper box, or establish physical/native/hosted admission. No kappa or supplier adoption is claimed.

## Reproduction

From the repository root, the direct verifier and focused tests run on Python 3.12 or 3.14. The registered package replay is pinned to Python 3.12:

```sh
python3 -I -O -B research/k8-three-coordinate-temporal-seed21/verify.py
python3 -I -O -B research/k8-three-coordinate-temporal-seed21/test_package.py
python3.12 -B scripts/research_package.py --package research/k8-three-coordinate-temporal-seed21
```

Expected verifier summary:

```text
PASS_K8_THREE_COORDINATE_TEMPORAL
forward incident_adds 347 blocks 23 real_delta -384 complex_delta -768 complex_primitives 148234 scales 71 all712=pass
backward incident_adds 347 blocks 23 real_delta -384 complex_delta -768 complex_primitives 148250 scales 76 all712=pass
shared_adds {'19531': [225, 367], '22786': [225, 350]} pair_control -474
```

The verifier pins both source archives and the literal lowerer to base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, checks the PR1042/PR1094 provider alias, verifies PR1380's certificate hash, and independently recovers PR1380's two-coordinate objective, full-word hash and invoice as a positive control. It also checks every ADD coefficient against the literal lowerer, exact transformed-word invoices, helper frames, paid profiles, local 192-bit charge, and both 712-column endpoints. Negative controls reject a missing schedule event and an out-of-box exponent; flipping the shared ADD sign fails the full endpoint replay. The zero schedule is an exact identity control.

## Task choice and search boundary

OS assignment seed 21 selected the complex supplier track. Three narrow candidates were triaged:

1. Jointly optimize L225/L350/L367 on the original PR1094 word over `[-4,4]^3` in both orientations. Selected by `21 mod 3 = 0`; the third coordinate is selected by `21 mod 15 = 6` from PR1380's other L225 neighbors after excluding L350.
2. Independently audit PR1380's 9-by-9 L225/L350 coupling block. Not selected because PR1380 already checks the full 81-state coupling table and all source schedules.
3. Optimize L225/L350/L352 on the same source and domain. Not selected because the seed-selected L367 triple already tests the same higher-order interaction class with a different shared-event pair.

The search stops after exhaustive exact coverage of the fixed 729-state box for this one triple and both orientations. No result is extrapolated to other triples, other gauge boxes, unconstrained schedules or a global supplier optimum. `TASK.json`, `SOURCES.json` and `RESULT.json` preserve the seed, base, source pins, complete schedule and exact invoices.

## Attribution and limits

The source word and lowerer come from the retained PR1042/PR1094 lineage. The two-coordinate control and event-level gauge method build on Sagar Thakrar's PR1380 and PR1259; Philipp / mightyOil's PR1263 is the later static-gauge comparator. PR1322's common-shift triple census is related but studies a different schedule family. Full ancestry and exact heads are recorded in `SOURCES.json`.

Final overlap refresh at 2026-10-14 00:08:38 UTC: PR1388 (head `3545a0268b049c6bae5a751c2eb9189187aed469`) composes L348/L359 on the later PR1263 static word; PR1385 (head `be95b8063b03f9cf511dbc3d7eb8437ce1e647e5`) optimizes L259 on that word; and discussion claim [#18911723](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911723) proposes composing L248/L253/L259 on that word. Claim [#18911678](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911678) covers L284 on the same later word. These use a different background and coordinates from this PR1094 original-word L225/L350/L367 schedule.

Prepared by Cinna Davis / @1337isnot1337 with substantial OpenAI Codex assistance in task selection, exact optimization, implementation, verification and writing. No independent human review is claimed. The new package is Apache-2.0.

## Open next questions

- Does a bounded multi-coordinate temporal schedule produce a useful effect on the later PR1263 static word? First step: select one exact interacting triple disjoint from the active L259 work and price its complete source invoice. Blocked by the distinct 218-helper static baseline and live overlap checks.
- Can any restricted three-coordinate result be converted into a legal adapter with a lower complete physical supplier invoice? First step: price every changed boundary scale and compiler adapter against the actual destination frame. Blocked by native/hosted admission and whole-supplier integration.

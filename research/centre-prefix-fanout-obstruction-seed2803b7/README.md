# Exact centre-prefix fanout obstruction (seed 2803b7)

**Scoped negative result; no new bound or supplier claim.**

## Question and result

The `centre-path-sharing` card asks whether the selected profile's center path can be shared or reduced. The optimistic aligned two-call profile would reduce center charge from 64 to 32 per call (32 saved), giving an ideal complex-side multiplier of 1.90; the unchanged bit-side ceiling limits the whole-bound gain to about 3.45%. The exact actual-profile overhead budget is pinned in [`centre-sharing-overhead-budget`](../centre-sharing-overhead-budget/README.md). This screen assumes no added carry, copy, restoration, frame, precision, or hosting cost. Before pricing a more elaborate schedule, this package tests the necessary zero-storage timing move: can one center contribution be placed before the selected forward scalar prefix without changing the endpoint?

For each of the eight center outputs, the verifier injects the exact pinned 22-row canonical scatter at the beginning of the selected forward program, suppresses that center output at its native event, and replays every scalar instruction with `fractions.Fraction`. It keeps all 19,693 scalar events and compares all 704 local-role endpoints. In this common-frame scalar projection, the endpoint differs in 34, 34, 36, 36, 54, 54, 56, and 56 roles for the eight basis outputs. One exact witness is `normal - early = 1/4` at local role 114 for center channel 0.

This closes only the tested early-fanout timing route in the common-frame scalar projection. Native frame transport, climbs, adapters, persistent storage, phase reordering, changed interfaces, supplier adoption, and kappa are not established or ruled out. Because the required endpoint identity already fails, no copy/storage/precision/hosting invoice for a surviving schedule is claimed.

The report is pinned to base `e112d71c8d7bb32435debcc54df932593dd8223a`, selected-record SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`, and the source/archive pins in [SOURCES.json](SOURCES.json). Overlap was refreshed before the claim; related work includes [PR #1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708), [PR #1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748), [PR #1791](https://github.com/CrocSwap/integer-mult-bounds/pull/1791), [PR #1829](https://github.com/CrocSwap/integer-mult-bounds/pull/1829), [PR #1838](https://github.com/CrocSwap/integer-mult-bounds/pull/1838), [PR #2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048), and the scoped [Discussion #1963](https://github.com/CrocSwap/integer-mult-bounds/discussions/1963). The present result tests a distinct necessary timing condition and does not duplicate those claims.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/centre-prefix-fanout-obstruction-seed2803b7 --check-only
python3.12 scripts/research_package.py --package research/centre-prefix-fanout-obstruction-seed2803b7
```

The direct verifier prints the same pass marker. To regenerate the result at a new path, run:

```sh
python3 -B research/centre-prefix-fanout-obstruction-seed2803b7/verify.py --write-result /tmp/centre-prefix-result.json
```

All arithmetic is exact rational arithmetic. Controls check a commuting identity prefix, a noncommuting target-read prefix, and rejection of a mutated canonical scatter coefficient.

## Open next questions

Can a specific full-call phase reordering or persistent center bank share one selected center result while preserving every dirty helper endpoint and keeping its fully charged cost below the 32-per-call ideal saving? This matters because such a schedule could avoid the failed early timing move while retaining some center saving. The feasible first step is to specify one exact call pair, all saved center components, source/target owner windows, and the complete copy, restoration, frame, precision, and hosting invoice. The blocker is that no such selected pair and carry-state contract has yet passed both the endpoint and budget screens.

## Credit

Prepared by Cinna Davis. Substantial OpenAI Codex assistance was used in scope selection, derivation, implementation, exact replay, and writing; no independent human review or proof-assistant formalization is claimed. Predecessor attribution is retained above. New work is Apache-2.0.

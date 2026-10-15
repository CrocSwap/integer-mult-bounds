# Exact Clifford state acceleration

This optional adapter accelerates the complete selected helper-interface check by **2.80×** in one local benchmark.
Seven alternating pairs give median times of **1.289 seconds** and **0.460 seconds**.
Every output receipt matches the original byte for byte.

After `research/clifford-state-production/`, the multicold production
`clifford_exact.py` ships the same gate-table `zero_state`. This package vendors
the pairwise-era bytes as `baseline.py` and pins production separately so
opt-in differential replay does not fail working-source drift.

The change affects verification speed only.
The selected conditional bound remains `51110230636731/31250000000000000`.
No selected certificate, circuit, or default verification command changes beyond
the production evaluator wiring above.

## Reproduce

Use Python 3.11 or later.
The package uses only the standard library and files already in this repository.
Run these commands from the repository root:

```sh
python3 -B research/clifford-state-performance/test_state.py
python3 -B research/clifford-state-performance/benchmark.py --pairs 7 --out /tmp/clifford-state-benchmark.json
```

Use a fresh output file for the benchmark.
Expected results are six passing tests and `PASS exact receipts`.
Timing depends on the machine; correctness does not require a speed threshold.

The benchmark runs the unchanged `scripts/verify_cold617_interface.py` in fresh processes.
Both engines read the same archived PR622 native artifacts.
`SOURCE.json` pins nine input and source files, plus the expected output receipt.
The adapter checks all pins before execution.

For fresh provider outputs from a separate complete replay, use:

```sh
python3 -B research/clifford-state-performance/run.py --engine fast \
  --runs /path/to/replay/ck-local /path/to/replay/jp8-local \
  --out /tmp/fresh-helper-check.json
```

This option uses the fixed 36-entering/22-cold inventory.
The helper check alone does not establish that custom providers pass the complete construction replay.
Use `--engine reference` for the original evaluator.

## Method and exactness

The original evaluator computes binary matrix products and quadratic phases separately for every state index at every gate.
The accelerator builds exact tables for these two functions.
Two caches retain at most 64 tables each.
Their keys contain the dimension and every coefficient; they contain no state or acceptance result.

For a permutation gate, write `x = y xor 2^i`, where `i` is the lowest set bit of `x`.
Linearity over the binary field gives:

```text
Gx = Gy xor G(2^i).
```

The table starts at zero and evaluates this recurrence in ascending index order.
Each predecessor `y` has a smaller index.
The result equals the original row-parity matrix product.

For a diagonal gate, let `f(x)` denote its phase modulo four.
Removing the lowest bit leaves only larger indices in `y`.
The original upper-triangular quadratic formula therefore gives:

```text
f(x) = f(y) + alpha[i] + 2 parity(Q[i] & y)  (mod 4).
```

The phase table evaluates this recurrence with exact integers.
Equality with the original upper-triangular evaluator does not require symmetry.
The existing gate constructors retain their own validity checks.

Translations, global phases, and C gates retain the original Gaussian-integer formulas.
The evaluator divides common powers of two after every gate, exactly as before.
It returns every amplitude and the denominator exponent.
Thus induction over a valid circuit preserves the complete exact state, including its global phase.
The tableau computation remains unchanged.

These arguments concern the evaluator's gate semantics.
Finite comparisons do not formally prove the complete multiplication theorem.

## Verification coverage

- Compare 10,220 permutation entries and 10,220 quadratic-phase entries against the original scalar formulas.
- Compare 4,050 complete states across 54 seeded circuits and their 15 prefixes.
- Check every basis state for dimensions one through four.
- Check three basis states per prefix for dimensions five through nine.
- Check all 54 adjoints and 54 circuit/inverse compositions.
- Compare all 204 state evaluations inside the complete helper-interface replay.

- Retain both providers, 34 exact pair instances, and all 68 phase rejection controls.
- Reject altered phase, rank, last-frame, and cleanup inputs in both engines.
- Reject changed source bytes, disabled assertions, unknown gates, and output reuse.

The circuit seed is 86.
The fixed domain above is the stopping rule; there is no search or optimality claim.
Separate phase controls detect changes invisible to a Clifford tableau alone.
Tests also exercise exact denominator reduction and cache eviction.

## Evidence and limits

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected review is `docs/research/community-k492-review.md`.
Original helper inputs come from `research/community-k492-audit/pr622/replay/`.
These artifacts support the selected PR626 composition.

`evidence/benchmark-python313.json` records all 14 timed runs, environment details, source hashes, and output hashes.
The benchmark alternates execution order and starts each process with empty evaluator caches.
It includes source admission, imports, input parsing, all checks, and receipt writing.
Operating-system caches are not flushed.
No other experiment runs concurrently with this benchmark.

The saved measurement uses CPython 3.13 on macOS arm64.
It measures archived-input helper verification, not a fresh supplier construction or the complete `frontier626-verify` target.
No Linux timing or mathematical-search throughput follows from this measurement.
The dedicated workflow runs exact comparisons on Linux with Python 3.11 and 3.13.
Remote results require a separate CI run.

All six tests pass locally on Python 3.13 and 3.14.
The selected source-inventory check also passes locally.
The repository-wide `make verify` suite is outside this scoped adapter validation.
All inherited compiler, hosting, physical, precision, tape, and analytic assumptions remain.

See `CLAIM.md` for task selection and overlap checks.
See `NOTICE.md` for attribution and AI assistance.

# Parallel exact U8 phase recipes (opt-in, byte-identical)

**Status: tooling improvement (verification engineering). No new κ, and no mathematical check is
changed or weakened.**
Track 85–94 (verification engineering), assignment seed 86 (OS CSPRNG via Python `secrets`).
Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

## What it speeds up

The selected T37 replay records a total of 403 s in
`research/community-frontier942-audit/STAGES.json`. Its `u8-native` stage alone takes 254.5 s,
and 154.3 s of that is the exact phase lowering `phases_full.py`, about 38% of the whole replay.
That step lowers 1,005 frames, 2,949 directed edges and 224 endpoint adapters to exact Clifford
recipes. Every edge and adapter is an independent, pure computation with the pinned
`clifford_exact.py`.

`phases_parallel.py` is an opt-in drop-in. It takes the same arguments (`OUT_DIR CLIFFORD_DIR`)
plus `--jobs` and `--engine`:

- The frame loop runs in the parent with all of its assertions, unchanged.
- Each edge and each adapter is computed in a worker process by the unchanged pinned functions,
  including the per-edge rank assertion.
- Results are collected in the serial order. Nothing is written unless every worker succeeds.
- `CLIFFORD-RECIPES.json` is byte-identical: digest `4629507d…`. That is the
  `clifford_recipes_sha256` pin in PR870's `LOCAL-PINS-barch-U8.json` and the hosted template's
  `exact_local_clifford_recipe_sha256`.
- `CLIFFORD-REVIEW.json` equals the archived review in every field except the elapsed seconds.

The pinned `phases_full.py` stays the reference. No pinned file is modified.

`--engine reference` (the default) runs the pinned `clifford_exact.py` exactly as it is.
`--engine dense662` also installs Charles Bethin's merged PR662 exact state evaluator
(`research/clifford-state-performance/fast_state.py`, pinned by digest) as `Op.zero_state` in every
process, the same substitution PR662's own `run.py` makes. The parallel layer composes with any
per-edge evaluator.

## Benchmark (same input, same machine)

| Runner | Wall time | Speedup |
|---|---:|---:|
| pinned serial `phases_full.py` via `run_portable.py` | 92.2 s | 1× |
| `phases_parallel.py --jobs 4`, reference engine | 33.0 s (separate run) | 2.8× |
| `phases_parallel.py --jobs 10`, reference engine | 16.2 s | **5.7×** |
| `--jobs 1 --engine dense662` (the PR662 evaluator alone) | 12.3 s | 7.5× |
| `--jobs 10 --engine dense662` | 3.2 s | **28.8×** |

Every run produced the pinned bytes. Rows without a note come from one harness run.

Machine: macOS 26.5.2 on arm64 with 10 cores (4 performance, 6 efficiency) and Python 3.14.8.
The harness receipt is [`BENCHMARK-macos-arm64.json`](BENCHMARK-macos-arm64.json). These are
local measurements: the recorded replay machine took 154.3 s for the serial step, and the
speedup depends on core count.

## Coverage preserved

- **Identical computation.** Every frame, edge and adapter goes through the same pinned functions
  with the same assertions. Only process scheduling changes.
- **Identical evidence.** The recipe bytes are checked against PR870's pin, and the review against
  the archived review.
- **Failure detection, shown by controls.**
  - C1: a corrupted frame fails the parent's frame rank assertion, and no output is written.
  - C2: an edge between two different frames of equal rank fails the per-edge rank assertion
    inside a worker, under both engines. The run then exits non-zero without writing recipes, and
    the pinned serial script rejects the same input at the same assertion.

## Using it in the selected replay (opt-in, not wired)

`reproduce_barch.py` already has a `--skip-phases` switch. An opt-in replay can run the `u8-native`
stage with `--skip-phases`, then run

```sh
python3 -B research/phase-recipes-parallel/phases_parallel.py <native>/local research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford --jobs N [--engine dense662]
```

It then checks the recipe digest against `LOCAL-PINS-barch-U8.json`, the same assertion
`reproduce_barch.py` makes. Wiring this into `scripts/verify_frontier942.py` is left to the
maintainers, and the serial path remains the default.

## Reproduce

```sh
make phase-recipes-parallel-verify      # parallel run, pins and controls (about 30 s)
make phase-recipes-parallel-benchmark   # also times the pinned serial reference (about 2 min)
```

The expected last line is `PASS_PHASE_RECIPES_PARALLEL`. Both use standard-library Python 3.10+
and no network. The input canonical word is read in memory from the pinned selected T37 archive,
and the payload digest `24db880b…` is checked against PR870's pin.

## Relation to concurrent work

aliromman's open PR1029 attacks the same step with a new sparse exact state evaluator. It reports
16.4× against the original and 2.2× against PR662 on a different machine. This package is
complementary and differs in two ways:

- **Equivalence by construction.** The default engine runs only unchanged pinned functions, so
  only scheduling changes and no new evaluator proof is needed.
- **Composition.** Process-level parallelism multiplies the speed of whatever per-edge evaluator
  is installed. With the already-merged PR662 evaluator it reaches 28.8× here. A sparse evaluator,
  if accepted, could be installed the same way.

## Scope

- This speeds up one step of the `u8-native` stage. The other steps, including
  `layer-end-controls` (77 s), are untouched.
- It does not discharge any mathematical obligation of the selected result, and it is not a
  formal proof.

## Credit

- icekylinx: `phases_full.py`, adapted from PR425 (jacklightChen's mutable-basis interface) for
  heterogeneous centres.
- PR558 (eumemic) and its PR552 lineage: the exact Clifford compiler `clifford_exact.py`.
- Jeremy Kothe and NewBArch (PR869/PR870): `reproduce_barch.py` and the U8 pins.
- Jonathan Capalbo (PR942): the selected replay.
- Prior verification-engineering work using concurrency: navinor's PR853 (pinned stages run
  concurrently) and PR921.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
  (Anthropic) via Claude Code. New material is Apache-2.0.

# Exact sparse phase compilation on the selected frontier1042 `phases` steps

**Status: verification engineering, opt-in, not wired. No new κ. No pinned file changes and no
check is weakened.**

## What this measures

A cold `make frontier1094-verify` runs `scripts/verify_frontier1042.py` as its `baseline1042-cold`
stage. That replay calls the pinned serial `phases_full.py` three times, once in each of the cells,
chain and slots stages. In the maintainer's recorded run
(`research/community-frontier1042-audit/selected-replay.tar.gz`) those three steps took 199.4 s,
134.4 s and 135.3 s: **469 s of the 1162 s run**. PR1151 parallelised the run's five layer-end-control
steps and explicitly left these three unmeasured.

Two merged tools already compile exact phase recipes faster: Ali Romman's sparse evaluator (PR1029,
`research/selected-replay-fastpath/`) and thakrarsagar's process-parallel runner (PR1041,
`research/phase-recipes-parallel/`). Both were measured only on the PR942 U8 word. This package
checks them on the three k8 words of the selected chain.

## Result

For each stage, the archived `local/CANONICAL-WORD.json.gz` has the decompressed SHA256 that the k8
pins file records as `canonical_sha256`. Compiling it gives output that matches the pinned serial
step, as follows:

- **Recipes.** The sparse compiler (`run.py --engine sparse`) writes a `CLIFFORD-RECIPES.json` that is
  **byte-identical** to the archived maintainer recipes. Its digest is the pinned
  `clifford_recipes_sha256`.
- **Review.** `CLIFFORD-REVIEW.json` has the same keys as the archived review, and the same values
  except elapsed seconds.

| Stage | Pins file | `clifford_recipes_sha256` | Frames | Edges | Adapters |
|---|---|---|---:|---:|---:|
| cells | `gauge44-leaver8/.../LEAVER-PINS-k8.json` | `aab63b0a…` | 1036 | 2958 | 224 |
| chain | `gauge44-leaver8/.../CHAIN-PINS-k8.json` | `e3bfdfa2…` | 1004 | 2896 | 224 |
| slots | `gauge44-slots/.../SLOT-PINS-k8.json` | `d0768f21…` | 1004 | 2896 | 224 |

Same-machine wall times are below. The machine is macOS arm64 with 10 cores, running Python 3.14.7.
The host was shared with another research job, so treat these numbers as descriptive. The raw
receipt is [`BENCHMARK-macos-arm64.json`](BENCHMARK-macos-arm64.json).

| Command | cells | chain | slots | Total wall (CPU) |
|---|---:|---:|---:|---:|
| maintainer recording, pinned serial (other host) | 199.4 | 134.4 | 135.3 | 469.1 |
| pinned serial `phases_full.py` via `run_portable.py` | 80.3 | 82.4 | 88.2 | 250.8 (250) |
| `run.py --engine dense` (PR662) | 11.7 | 14.2 | 13.8 | 39.8 (39) |
| `run.py --engine sparse` (PR1029) | 7.9 | 7.8 | 5.0 | 20.7 (19) |
| `phases_parallel.py --jobs 10 --engine dense662` (PR1041) | 2.8 | 2.9 | 3.1 | 8.8 (70) |

All times are in seconds. On this host the sparse compiler is 12× faster than the pinned serial step in wall time, and uses one core. The parallel dense runner is 29× faster but uses about 10 cores.

An earlier scratch run on a less loaded host gave 4.1–4.4 s per word for the sparse compiler and 11 s for the dense one.

Every run in the table produced the pinned bytes.

## Controls

`verify.py` runs two controls on a corrupted cells word. Neither may reproduce the pin.

- **C1.** One one-dimensional frame `<u>` is changed to a different line. `run.py` must reject it
  with an `AssertionError` and write no recipes.
- **C2.** One directed edge is redirected to a frame of a different dimension. It must compile, but
  to different recipes.

Both expected behaviours are asserted exactly, so a change in how the compiler treats either
corruption shows up as a failure.

A bit flip inside a full-rank frame leaves the span unchanged. Its canonical frame and recipes are
then identical, so it is not a corruption. An earlier draft control did exactly that and was replaced.

PR1029's own package covers the remaining controls:

- the four corrupted-word classes;
- source-pin refusal;
- optimized Python;
- output reuse;
- the gate-level tests and `PROOF.md`.

This package does not repeat them.

## Wiring (left to the maintainers)

The three steps feed later stages:

- `verify_slots.py` asserts both the chain and the slots recipe digests.
- `verify_t16.py` copies `CLIFFORD-RECIPES.json` and `CLIFFORD-REVIEW.json` forward and binds their
  content.
- T16's `bind_providers_portable.py` asserts the review's `status`, `canonical_word_sha256`,
  `recipe_sha256`, global-phase flag and `endpoint_adapters == 224`.

`run.py` writes a review that `verify.py` checks equal on all those fields, so the files are drop-in.
The pinned scripts do not accept a substitute today:

- **cells.** `reproduce_leaver.py --skip-phases` works. Its pins are checked key by key, and the
  switch skips the recipe-pin check, so a wrapper must run
  `research/selected-replay-fastpath/run.py --word local/CANONICAL-WORD.json.gz` into `local/` and
  assert `clifford_recipes_sha256` itself.
- **chain.** `reproduce_leaver_chain.py --skip-phases` would **fail**. It ends with
  `assert got == pins` over the whole CHAIN-PINS dictionary, and the recipe key would be missing.
- **slots.** `verify_slots.py` has no switch.

The chain and slots steps, and `verify_frontier1042.py` itself, therefore need changes to
manifest-pinned scripts. That is a maintainer decision. The serial path stays the reference.

## Reproduce

```sh
python3 -B research/frontier1042-phase-fastpath/verify.py                    # ~20 s, sparse
python3 -B research/frontier1042-phase-fastpath/verify.py --engine dense     # ~45 s
python3 scripts/research_package.py --package research/frontier1042-phase-fastpath --check-only
```

The expected last line is `PASS_FRONTIER1042_PHASE_FASTPATH`. The verifier is standard-library
only and reads nothing but committed files. The benchmark harness that produced the receipt is
[`bench.py`](bench.py); it takes `python3 -B research/frontier1042-phase-fastpath/bench.py OUT_DIR
ENGINES` and runs the pinned serial step through the pinned `run_portable.py`, as the replay does.

## Limits

- This package checks recipes compiled from the **archived** canonical words. A cold replay that
  rebuilds those words is checked by the existing pins: equal canonical digests imply equal input
  to the lowering.
- It does not establish anything about the scalar-interface integration or the global emitted
  program. Those obligations are unchanged, as `run.py`'s own review states.

## Open next questions

These are structured in [TASK.json](TASK.json).

1. **Should the cold frontier1042 replay call the sparse compiler for its three phases steps?** On
   Scaling the measured ratio to the recorded machine, it would save about 430 s, about 37% of the
   run; with PR1151 the run would drop to roughly 300 s. First step: an engine option on the three
   phases calls that keeps every pin assertion. Blocker: maintainer decision, since the scripts are
   pinned, chain `--skip-phases` fails its whole-dictionary pin check, and `verify_slots.py` has no
   switch.
2. **Do other cold replays spend comparable time in the 23 byte-identical `phases_full.py` copies?**
   First step: scan archived `STEPS.json` receipts for `phases` steps over 30 s and rerun this
   pattern. Blocker: some archives may not keep the canonical word.

## Credit

- Ali Romman (PR1029): the sparse evaluator.
- thakrarsagar (PR1041): the parallel runner.
- Charles Bethin (PR662): the exact gate tables and the dense evaluator.
- icekylinx: `phases_full.py`, adapted from PR425 (jacklightChen's mutable-basis interface).
- PR558 (eumemic) and its PR552 lineage: `clifford_exact.py`.
- Jeremy Kothe: the construction, with Rohan Arun's slot search and Hao Yan's T16 controller.
- LeaverSAT and LeaverSAT2: the k8 cells and chain recipes.
- Douglas Colkitt: the maintainer replay and its archive.
- PR1151: identifying this gap.

Prepared by Josie Elliston with Claude Code (Claude Opus); no subagents. A Codex read-only review
corrected the wiring section, tightened the controls and the credit. That is separate AI review,
not independent human review. Apache-2.0.

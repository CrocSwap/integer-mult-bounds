# Parallel U8 layer-end controls (opt-in, byte-identical receipt)

**Status: tooling improvement (verification engineering). No new κ, and no check is changed or
weakened.**
Track 85–94 (verification engineering), assignment seed 85 (OS CSPRNG via Python `secrets`).
Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

## What it speeds up

The selected T37 replay's `u8-native` stage spends 77.0 s in `layer-end-controls`, the second
most expensive step after the phase lowering. That step runs PR870's
`layers_p6n/layer_end_controls.py`, which audits the unmutated U8 word and 95 mutated words
with PR635's `hpe_audit_and_transport.run`. Every mutation must be rejected for a pinned reason.
The 96 audits are independent pure computations.

`controls_parallel.py` takes the same arguments and parallelizes them **without editing or
re-implementing the pinned script**:

1. **Record.** The pinned script runs once with a stand-in `hpe_audit_and_transport` that only
   records the exact gzip bytes of each trial word. As each word is recorded, the real audit of
   it starts in a worker process.
2. **Evaluate.** Every distinct word is audited by the real pinned `run` (digest-checked) in a
   worker, giving exactly the outcome `trial()` would observe.
3. **Replay.** The unchanged pinned script runs again. Its stand-in returns or raises the
   precomputed real outcome for the identical bytes. The script's own assertions accept or reject
   every control, check every pinned reason and write `COLD-END-CONTROLS.json`. The sequence of
   trial words must equal the recorded one.

In this design the record pass's placeholder answers never decide anything. Only real outcomes,
evaluated by the pinned audit on the byte-identical words, reach the script's assertions.

## Benchmark (same pinned inputs, same machine)

| Runner | Wall time | Speedup |
|---|---:|---:|
| pinned `layer_end_controls.py` | 49.2 s (standalone), 52.5 s (harness) | 1× |
| `controls_parallel.py --jobs 10` | 16.4 s (standalone), 19.9 s (harness) | **3.0×** (2.6× under harness load) |
| `controls_parallel.py --jobs 4` | 23.3 s (standalone) | 2.1× |

Machine: macOS 26.5.2 arm64, 10 cores, Python 3.14.8. The receipt is in
[`BENCHMARK-macos-arm64.json`](BENCHMARK-macos-arm64.json). The remaining serial cost is the
pinned script's own mutant construction (deep copy, JSON and gzip of each word), which runs once
per pass by design. On the recorded replay machine the serial step took 77.0 s.

## Evidence of equivalence

- `COLD-END-CONTROLS.json` is **byte-identical** to the pinned script's receipt for the same
  arguments, at digest `99a17435…` in every 4-job and 10-job run.
- The printed control lines are identical.
- The 95 rejected controls equal the archived receipt of the selected T37 replay, in order.
- **Control C1:** a corrupted unmutated word, with one gate coefficient doubled, makes the parallel
  runner fail. The failure comes from the pinned script's own assertion, `unmutated cold-end word
  must pass`, in the replay pass, and no receipt is written.

## Using it in the selected replay (opt-in, not wired)

`reproduce_barch.py` runs the pinned script as one step. An opt-in replay can invoke
`controls_parallel.py` with the same three arguments and the same `PR635_CODE` environment, then
check the receipt as `reproduce_barch.py` does. No pinned file is modified, and wiring is left to
the maintainers. This complements the opt-in phase runner in PR1041. Together they would cut the
`u8-native` stage from about 254 s to about a minute on the recorded machine, assuming similar
core counts.

## Reproduce

```sh
make layer-end-controls-parallel-verify      # parallel run, archived-receipt match, control C1 (~40 s)
make layer-end-controls-parallel-benchmark   # also runs the pinned serial reference (~80 s)
```

The expected last line is `PASS_LAYER_END_CONTROLS_PARALLEL`. It uses standard-library Python
3.10+ and no network. The barch word is read from the pinned T37 archive, and its payload is
checked against PR870's `RECIPE-U8.json`.

## Scope

This accelerates one step. It discharges no mathematical obligation, and the timings are local
measurements.

## Credit

- DreamingOfClouds: `layer_end_controls.py`, adapted from PR635's cold-end controls.
- PR635's authors: `hpe_audit_and_transport.py`.
- Jeremy Kothe and NewBArch: PR869/PR870, the barch word and pins.
- Jonathan Capalbo: the PR942 replay.
- Prior concurrency tooling: PR853 and PR921 (navinor), and PR1041.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
  (Anthropic) via Claude Code. New material is Apache-2.0.

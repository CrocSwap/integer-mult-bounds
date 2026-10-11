# A concrete binary count dispatcher in Lean

This package checks a seven-state, two-tape, three-symbol controller that reads an actual finite input word and dispatches one completed increment per bit. The input bits may be either value; the counter adds their number to its initial value, modulo 2^width for the supplied width. Four Lean sources are included, with two exact source dependencies from [PR488](https://github.com/CrocSwap/integer-mult-bounds/pull/488). PR488 need not be merged.

## Checked contract

For every input word and every supplied fixed-width counter bit list, `count_run` reaches the specified halted configuration in at most `(CarryTape.pass word.length bits).2.reads + 2 * word.length + 1` transitions. The input remains represented nearest-first to the left of its visited right blank. The counter returns to its home blank with the same width and value `(initial value + word.length) mod 2^width`. Empty input, zero width and wraparound are included. The counter's home and end blanks are distinct represented cells, including at zero width.

The five-state one-tape increment adapter realizes the reused carry semantics in `2 * trailingOnes + 4` transitions. The controller lifts that table, detects its completion and restarts it from actual scanned symbols. Successful-prefix simulation is proved internally. It does not require a first-halting-time premise.

This is a supplied-width modular-count helper. Width allocation, a cross-model linear amortized bound, compact output, the actual source prelude/caller, and Plan/Budget composition remain outside this package. It does not prove a full multiplication theorem or a κ bound.

## Reuse and contribution

[PR64](https://github.com/CrocSwap/integer-mult-bounds/pull/64) already supplies literal counter and stack machinery with richer direction, exterior-tape, first-completion and amortized guarantees. Binary increment is not claimed as new or improved here. The additional checked result is the explicit `CurrentMain.FixedTapeMachine` symbol-driven restart controller, its exact two-tape endpoint, and its connection to the existing carry-pass receipt. The controller reuses CarryTape/CarryTapePass; this six-module closure does not yet prove the PR64-to-current-model arithmetic transport. The two foundation files and the successful-prefix reduction pattern are reused from the [exact PR488 head](https://github.com/jamesyc/integer-mult-bounds/tree/edd3102b415df5b9d6f633ac0a4dedcf69c58525/research/lean-binary-input-preparation).

## Reproduce

Use Linux, Python3 and Lean4.21.0. The checker uses `/proc` for its memory observations and has no Python package dependencies. Obtain a separate checkout of the foundation repository at the exact commit in `FOUNDATIONS.json`, for example:

```sh
git clone https://github.com/jamesyc/integer-mult-bounds.git foundation-repo
git -C foundation-repo checkout --detach edd3102b415df5b9d6f633ac0a4dedcf69c58525
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --foundation-root /path/to/foundation-repo/research/lean-binary-input-preparation \
  --build-dir /tmp/count-dispatcher-check
```

The build directory must not exist. The checker is offline: it validates both external source hashes and the four included source hashes, then compiles exactly six modules into that fresh directory. Its Lean search path contains only that output directory and the installed core library. No Mathlib is required. Per-module limits are 60 seconds and 4 GiB address space; a successful check over 40 seconds or 3.5 GiB stops for review. No object files are shipped. `ACCEPTED_CHECKS.json` records the exact source-level acceptance receipts and 36 standard-axiom probes. The isolated flat-layout six-module package replay passed in 8.8320 compiler seconds and 0.00303 queue seconds, with peak virtual memory 2,735,955,968 bytes. All six object hashes and all 36 printed axiom outputs matched the accepted sources; see `REPLAY_SUMMARY.json`.

## Author-checked project context

At base commit `12a4934d15006e8c10f9b2264f13f8f341be802b`, the selected conditional project value is κ=`90446448750933/125000000000000000`=`0.000723571590007464`. The captured source and linked certificate agree, as checked by the source author. This project context retains all-size compiler, weighted/common-ancestor chart, restored-row, selector/routing, prime-supply, precision/recovery, complex-symbolic and analytic-transfer assumptions. The generic dispatcher does not discharge those assumptions or prove this κ value. Exact source and dependency pins are in `PROVENANCE.json`, `FOUNDATIONS.json` and `MANIFEST.json`.

The inherited Apache-2.0 license and source attribution are included.

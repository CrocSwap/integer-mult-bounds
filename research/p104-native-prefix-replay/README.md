# Faster complete native checks for the current P104 candidate

The complete PR6453 native replay is **2.74 times as fast** as the prior
gate-table evaluator in three alternating fresh-process pairs on this
host. Median wall time falls from 24.69 to 9.00 seconds. Every run returns
the same 2,941-map recipe payload and checks all 208 main adapters, helper
ranks, signed Pauli images, absolute phases and the wrong-phase control.
These are native-component timings, not complete compiler or multiplier
timings. [BENCHMARK.json](BENCHMARK.json) retains all six measurements.

The new evaluator caches immutable sparse circuit prefixes. The separate
native checker uses its own Gray-order permutation and phase tables.
No acceptance result is cached. Explicit module forks keep the frozen
sources intact. AST checks verify the small set of changed functions.
The cache has 512 entries; it cannot grow with the number of maps.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-native-prefix-replay
python3.12 -B research/p104-native-prefix-replay/benchmark.py --output /tmp/native-benchmark-new.json
```

Expected marker: `PASS_P104_NATIVE_PREFIX_REPLAY`. Both registered modes
check 1,520 complete state comparisons, 32,768 exact Gray-table entries,
cache mutation/eviction controls and the entire current native receipt.
The proof in [PROOF.md](PROOF.md) gives the preservation argument for all
valid circuits in the stated domain. Finite checks are not a proof kernel.

## Source and coordination

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, revision 8,
selected PR6030. Word and native receipt: PR6453 at
`b1a3e525793eca35c56324aa7ffd0b714cf606d4`. The retained compiler and checker
come from the main-branch archive chain in `inputs/PROVENANCE.json`.
All retained bytes are pinned. The generated extraction-path record is
labelled separately from predecessor files.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19363111).
The fresh overlap cache covered 424 open PRs and 6,380 discussion records.
PR662 and PR2329 already provide gate-table evaluation. That method is
the timing baseline here; its speedup is not claimed again. This package
adds prefix reuse and independent Gray-order action tables for the current
native component. Unpublished work remains outside the overlap search.

## Limitations and credit

The full PR6453 caller, compiler, outer proof and physical implementation
were not rerun. No new kappa, selected-frontier change or independent
scientific acceptance follows. Timing depends on the host. All five
framework assumptions remain.

Ali Romman with substantial OpenAI Codex assistance, Apache-2.0. See
[NOTICE](NOTICE). Charles Bethin retains Clifford and gate-table credit;
Wentao Li retains production-integration credit. Cinna Davis and the
retained native authors retain independent-checker credit. David Arias,
Gareth Davidson, Erwan L., Rohan Arun and the retained P104 lineage retain
their word and composition credit.

## Open next questions

Adopt the explicit evaluator inputs in a complete current verifier and
run that package's complete caller/compiler checks. This package supplies
the native component, not that integration. Compare complete-process time
before claiming an end-to-end verification improvement.

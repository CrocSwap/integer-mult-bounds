# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The exact containment-mask acceleration of the per-output triple scans was
introduced by **Aaron Wang** in the opt-in adapter
`research/joint-dual-replay-fast/` (see that package's README and TASK.json).
This package wires an equivalent check into the production
`scripts/experiments/binary_frame_replay.py:replay` path used by
`make joint-dual-verify`.

The original joint-dual serialized-word verifier, PR64 scatter multiset control,
compiler receipts and scientific certificate are by **Chafik Boukhalfa** and the
retained frame-compiler lineage. Upstream material retains its own source
notices and license.

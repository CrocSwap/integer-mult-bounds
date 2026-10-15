# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The exact base-256 byte-lane algorithm and its no-carry argument were introduced
by **Jerry Chen (@CubeJerry)** in the opt-in adapter
`research/leech-minor-byte-lanes/` (incorporated
[CrocSwap/integer-mult-bounds#898](https://github.com/CrocSwap/integer-mult-bounds/pull/898);
see that package's NOTICE.md). This package wires an equivalent check into the
production `scripts/experiments/affine_vector_screens.py:leech_minor` path used
by `make verify-certificates`.

The original affine/vector screens, Golay inventory, Leech line generators,
rational span witnesses, binary elimination and nine-screen certificate are by
**Douglas R. Colkitt**. Upstream material retains its own source notices and
license.

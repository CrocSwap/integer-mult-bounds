# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The injective packed-row algorithm and its radix argument were introduced by
**Ross Richardson (@RossRichardson)** in the opt-in adapter
`research/central-factor-packed/` (see that package's NOTICE.md). This package
wires an equivalent check into the production
`scripts/experiments/complex_centers.py:verify_factor` path used by
`make verify-certificates`.

The original dyadic factor, structural validation, receipt schema, side circuit,
phase argument and cost ledger are by **Douglas R. Colkitt**, retained at
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. Upstream material retains its own
source notices and license.

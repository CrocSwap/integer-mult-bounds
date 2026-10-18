# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The cached update-column algorithm and its equivalence argument were introduced
in the opt-in adapter `research/data-corner-performance/` (see that package's
NOTICE.md). This package wires an equivalent loop into the production
`research/copied-fixed/data_corners.cpp` path used by
`make copied-fixed-verify`.

The historical copied-fixed data-corner checker, receipt and certificate lineage
retain their original author credits in `research/copied-fixed/SOURCE.json` and
`research/copied-fixed/PROOF.md`. Upstream material retains its own source
notices and license.

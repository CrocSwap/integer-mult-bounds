# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The primitive-integer RREF algorithm wired into production was introduced by
**Aman** (PR367 / `research/frame-algebra-performance` lineage) and integrated as
an opt-in adapter by the authors of
`research/r420-rref-performance/` (merged tooling PR; prepared for @MrPink604
with substantial AI assistance). That package's NOTICE.md and PROOF.md retain
the exactness argument. This package wires an equivalent `rref` into the
production `research/e8-bit-r420/code/xcheck.py` path used by
`research/e8-bit-r420/verify.sh` step 2 and `mutants.py`.

The original R420 checker, mutation harness, word and interleaved
scalar-interface lemma are **eumemic**'s PR543, with substantial Anthropic Claude
assistance. Upstream material retains its own source notices and license.

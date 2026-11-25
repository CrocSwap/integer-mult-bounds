# Attribution and license

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu) with substantial
AI assistance for orientation, overlap search, profiling, production wiring,
packaging, benchmarking and writing. Not independent human peer review.
Apache-2.0; see the repository root `LICENSE`.

The one-basis modular closure algorithm and its Hadamard-guard equivalence
argument were introduced by **Ross Richardson** in the opt-in adapter
`research/bit-frame-closure-basis/` (merged as
[CrocSwap/integer-mult-bounds#1666](https://github.com/CrocSwap/integer-mult-bounds/pull/1666);
see that package's NOTICE.md and PROOF.md). This package wires an equivalent
`close` into the production `research/bit589-frame-optimum/frameopt.py` path
used by `research/bit589-frame-optimum/verify.sh`.

The original PR886 frame-only optimum checker, live-line catalogue and paid
profile accounting are by **Seth Burkart**, as refined during maintainer
integration of the bit589 frame-optimum package. Upstream material retains its
own source notices and license.

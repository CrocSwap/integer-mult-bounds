# Attribution

## This package

Prepared by Wentao Li (GitHub [VictorLiwentao](https://github.com/VictorLiwentao),
X [@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
New work is Apache-2.0.

## Predecessors

- **eumemic** authored the PR543 independent exact replay (`xcheck.py`), the
  interleaved-interface mutation harness (`mutants.py`), and the retained R420
  word/pipeline under `research/e8-bit-r420/`.
- **mtpsl** authored the opt-in geometry-reuse adapter
  `research/r420-geometry-cache/` (identical-receipt `GeometryCache` over
  `Word.__init__` / `labels()`), which this package wires into the shipped
  `mutants.py` path.
- Quality-bar and production-promotion pattern:
  [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  and subsequent identical-receipt production tooling PRs.

Original notices under `research/e8-bit-r420/NOTICE.md` and
`research/r420-geometry-cache/` remain authoritative for predecessor bytes.

# Owner improvement over PR637

Conditional **κ = 0.001636456810414854**, exceeding pinned
[PR637](https://github.com/CrocSwap/integer-mult-bounds/pull/637)
by **0.000000008347117783**.

Twenty literal owner rows change. Two neutral swaps and a whole-group transfer
combine idle ranks 4 and 32 into 1 and 35. The native supplier words, dispatch,
and admission code are inherited unchanged from PR637. The complete portable
witness is in [witness637/](witness637/README.md); the
[packing supplement](../kappa-packing-pr637-20261013/README.md) reconstructs the
assignment from pinned PR637 data.

Before publication, exact binding, physical owner admission and its 23 controls,
the finite invoice, both moment engines, a separate rational native/owner/moment
checker, and five independent corruption controls passed. A full fresh replay
of the pinned PR637 baseline passed all 64 stages, with no reuse.

The improved witness's full fresh replay passed **64/64 stages**, with no
baseline or local reuse, in 274.98 seconds. All 51 artifact hashes and 64 stage-log
hashes were independently checked. The supplemental owner, declaration, exporter,
and independent U4 checks and their mutation controls also passed.
The [validation directory](validation/) retains the receipts and full replay archives.
Execution was on macOS; no Linux replay is claimed.

```sh
PYTHON=python3 sh research/pr637-improvement-20261013/witness637/verify.sh /tmp/pr637-improved-fresh
```

Use Python 3.10+, a C++ compiler, Boost headers, and a new output directory.
The inherited compiler, all-size, realization, analytic-transfer and bit H1–H5
assumptions remain. This is a conditional research bound. It does not attain the
relaxed fixed-dispatch packing ceiling, which would require idle ranks 36 and
2229 copies of 48.

Prepared by Chi Zhao with substantial OpenAI Codex assistance. Upstream
construction and contributor credits are preserved in the witness.

The replay used commit `e020728199ed60e0604196f12c6276b5431998c6`. After it
passed, only the witness README and its manifest entry changed. The
[documentation update record](DOCUMENTATION-UPDATE.json) binds both manifests
and confirms that all 311 other manifested inputs are unchanged.

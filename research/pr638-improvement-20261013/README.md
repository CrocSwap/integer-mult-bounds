# Consolidated owner packing after PR638

Conditional **κ = 0.001636461592777116**, exceeding
[PR638](https://github.com/CrocSwap/integer-mult-bounds/pull/638) by
**0.000000004782362262**.

Three width swaps combine the remaining idle ranks 1 and 35 into one rank 36,
with 2229 idle ranks of 48. Native suppliers, helper widths, dispatch, geometry,
and admission code are unchanged. The [packing proof](FIXED-DISPATCH-PACKING-BOUND.md)
shows this minimizes the idle moment for the fixed suppliers, dispatch, geometry,
and capacity limits. This is not a claim of universal κ optimality or an exact
rounded root. Further gains from this packing objective require changing those fixed inputs.

The [portable witness](witness638/README.md) includes all pinned dependencies.
The [owner supplement](../kappa-packing-pr638-20261013/README.md) reconstructs the
assignment from pinned PR638 data.

Exact binding, owner admission and its 23 controls, the finite invoice, both
moment engines, and an independent native/owner/rational-moment check passed.
Five independent corruption controls also passed. The full fresh replay then
passed **64/64 stages**, without reuse, in 296.15 seconds. All 51 artifact and
64 stage-log hashes were independently checked. Supplemental checks, both owner
reconstructions and their mutation controls passed. Complete evidence is retained
in [validation/](validation/). Execution was on macOS; no Linux replay is claimed.

```sh
PYTHON=python3 sh research/pr638-improvement-20261013/witness638/verify.sh /tmp/pr638-improved-fresh
```

Use Python 3.10+, a C++ compiler, Boost headers, and a new output directory.
The inherited all-size, compiler, realization, analytic-transfer, and bit H1–H5
premises remain. Prepared by Chi Zhao with substantial OpenAI Codex assistance;
upstream construction and contributor credits are preserved in the witness.

The replay used commit `cf2f6d77eb555bf5a970d7e334aa46659b5ea66b`. Only the
witness README and its manifest entry changed after execution. The
[documentation update record](DOCUMENTATION-UPDATE.json) confirms all 311 other
manifested inputs are unchanged.

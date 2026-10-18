# Fixed-dispatch packing improvement on PR643

Conditional **κ = 0.001636569158555067**, exceeding
[PR643](https://github.com/CrocSwap/integer-mult-bounds/pull/643) by
**0.000000026935112958**. The conservative bound is
**κ = 0.001636569155685695**.

A 36-row owner reassignment combines idle gaps 12 and 32 into one gap of
44, retaining 2228 gaps of 48. Both native suppliers, helper widths, the
71-JP8/1-JP8b dispatch, call order, geometry and admission code are unchanged.
The [packing proof](FIXED-DISPATCH-PACKING-BOUND.md) shows this minimizes the
idle moment for these fixed inputs. Different suppliers and dispatch remain
possible avenues for improvement.

The [portable witness](witness/README.md) contains all pinned dependencies.
The [owner supplement](../kappa-packing-pr643-20261013/README.md) reconstructs
the literal assignment from pinned PR643 inputs. Upstream is fixed at
`bbfa9fe1d84d5572f4d144c2ee56a3eddc7a83f5`.

Exact binding, owner admission and its mutation controls, the finite invoice,
and both upstream moment engines passed. A separate checker recomputed both
actual native supplier profiles and widths, all 35,424 helper intervals,
and the strict rational moment inequality. The source and packing review
is retained in [validation/independent-review/](validation/independent-review/).
The final fresh candidate replay passed **58/58 stages** without reuse in 327.44 seconds, followed by all supplemental checks: independent native/owner/moment verification and five mutations, declarative reconstruction, exact owner reproduction and four mutations, and six U4 mutations. All 46 receipt artifacts and 58 stage logs were independently hash-checked. Full candidate and source replay archives are retained in validation. Execution was on macOS; no Linux replay is claimed.

```sh
PYTHON=python3 sh research/pr643-improvement-20261013/witness/verify.sh /tmp/pr643-improved-fresh
```

Use Python 3.10+, a C++ compiler, Boost headers, and a new output directory.
The inherited all-size, compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape/exact-recovery, analytic-transfer and bit
H1–H5 assumptions remain. This is finite conditional evidence. Prepared by
Chi Zhao with substantial OpenAI Codex assistance; upstream construction
and contributor credits are preserved in the witness.

The replay used commit `15595d482fd0f2fe6baf4d623e0f8e8a6b8047ef`. Only the witness README and its manifest entry changed afterward; [DOCUMENTATION-UPDATE.json](DOCUMENTATION-UPDATE.json) records that all 313 other manifested inputs are unchanged.

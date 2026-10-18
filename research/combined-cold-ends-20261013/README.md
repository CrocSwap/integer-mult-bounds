# Combined cold ends and owner repair over PR635

Conditional **κ = 0.001636269762440408**, exceeding pinned PR635 by
`0.000000028260864020`. The certified witness is in [witness635/](witness635/README.md).

A complete fresh macOS replay passed **64/64 stages**, with no reused baseline
or supplier results. All 51 receipt artifacts and 64 stage logs were hash-checked.
The independent proof, exact owner/moment check, mutation controls and both
nomination exporters also passed. [Validation and full replay archive](validation635/README.md)
retain the evidence, environment and conditional scope.

```sh
PYTHON=python3 sh research/combined-cold-ends-20261013/witness635/verify.sh /tmp/combined635-fresh
```

Python 3.10+, a C++ compiler and Boost headers are required. Use a new output
directory. The [packing supplement](../kappa-packing-pr635-20261013/README.md)
reconstructs the owner map from pinned PR635 inputs.

The executed input snapshot is commit
`4988e425009a1a94ebd5f4281a251fa5cc9cb162`. After successful execution, only the
witness README's status and its manifest entry were updated. The
[documentation update record](DOCUMENTATION-UPDATE.json) verifies that all
320 other manifested inputs are unchanged; validation retains the original
manifest and README.

The inherited all-size, compiler, realization, analytic-transfer and bit
premises remain. Prepared by Chi Zhao with substantial OpenAI Codex assistance;
complete contributor credit is preserved in the witness.

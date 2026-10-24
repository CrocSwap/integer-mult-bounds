# A funded numerical detector for orthogonal inverse witnesses

Exact nonzero rational witnesses can be small. This package proves a lower
bound for their magnitude and gives a complete dyadic replay that detects
the selected endpoint without using its exact value as an oracle.

For a path of dimension d, q named calls, rational parameter A/B, and product
C of all scalar denominators, every nonzero selected discrepancy has magnitude
at least `1/[C(3B)^(dq)]`. The [proof](PROOF.md) joins this separation to
all matrix-entry quantization, data truncation and scalar amplification.
The detector keeps every role and reads old values on aliased queries.

`detect(program, word, parameter, input_index, output_index)` returns the
selected zero/nonzero decision, the dyadic endpoint difference, its proved
error and precision, and the full matrix-product/rounding counts. A zero
selected endpoint is not a universal identity certificate. The retained
inverse producer can supply a distinguishing word for a false identity.

Run with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/orthogonal-witness-precision
```

Both registered isolated, warning-strict modes end with
`PASS_ORTHOGONAL_WITNESS_PRECISION`. Normal runs write no package files.
`verify.py --write-result` regenerates RESULT.json. `--small` keeps the
boundary controls and a smaller random/stress set.

The finite check covers equal and unequal complete programs, cancelling grid
points, tiny parameters and scalar discrepancies, large scalar gains, aliased
queries, dirty returns and an inverse-series stress family. Exact rational
replay and a separate dense inverse interpreter are test oracles only. The
production detector imports neither the exact endpoint replay nor the
coefficient producer.

This is a sufficient precision and a specified integer/dyadic computation.
It does not claim optimal guards, IEEE behavior, a native Clifford witness,
a tape implementation, a faster identity test or a complete kappa change.
The source coefficient-generation cost and dense matrix products are paid.
The selected frontier remains unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
[PR #5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315) supplies
the orthogonal construction. Krzysztof Wójt's
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262) supplies
the inverse compiler. Retained source notices preserve zxv and the earlier
rational-series/dirty-echo/tensor/phase credit. `SOURCES.json` pins the exact
bytes retained in branch history. Classical determinant and error bounds
retain their credit; no global literature priority is claimed.

## Open next questions

For a fixed native-compatible witness, can sparse or exact factor application
reduce this dense replay and its conservative scalar-gain guard? First pin
all native operator relations and the caller's complete error and cost
contract. This package proves finite detectability; it does not supply that
binding or an optimized physical implementation.

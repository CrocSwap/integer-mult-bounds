# Polynomial bit bounds for complete inverse-circuit certificates

The retained inverse-circuit verifier had a polynomial field-operation bound.
This package proves an explicit polynomial rational-size bound for that same
producer and its independent checker. It covers both equality certificates
and shortest nonzero coefficient words, including dirty inputs and aliases.
The [proof](PROOF.md) uses common denominators and pivot minors to bound
coefficient growth. The source code remains unchanged.

`budget.bounds(program)` gives the state, rational-height and coarse operation
budgets. `budget.audit(program)` compares the two source compilers, inspects
a complete reachable basis, checks the produced certificate's size, and runs
the independent certificate checker. Size checking alone does not prove an
identity. The explicit rational input contract accepts integers and signed
integer/fraction strings. It rejects decimal and exponent strings before
expansion; a caller must pay for any conversion from compressed input.

With CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/inverse-certificate-bit-bounds
```

The registered commands set `-X int_max_str_digits=0` so large explicit
coefficients can be serialized. Both normal and optimized commands print
`PASS_INVERSE_CERTIFICATE_BIT_BOUNDS`. To run one directly:

```sh
python3.12 -I -X int_max_str_digits=0 -W error -B research/inverse-certificate-bit-bounds/verify.py
```

`--write-result` regenerates RESULT.json. Normal verification writes no
package files. The corpus includes a 16,001-bit scalar, unreduced large
fractions, coprime denominators, nearly dependent rows, delayed inverse tails,
dirty queries and a compact weighted program with 2^64 distinct words.
The source certificate checker and literal oracles are unchanged.

This closes the rational-size gap before the orthogonal witness and funded
numerical detector interfaces. It does not establish a practical speedup,
optimal bounds, a native alphabet/type/phase adapter, physical tape cost,
supplier admission or a complete kappa improvement. The full downstream
orthogonal and detector replays are not rerun in this package.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Krzysztof Wójt's [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262)
supplies the unchanged producer, checker and exact oracles. The source proof
and README retain zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235)
and the classical rational-series, Magnus and
weighted-automata credit. The new work is the explicit project-specific
bit bound and its exact audit, not a new general equivalence algorithm.
`SOURCES.json` records all consumed source pins and preserved bytes.

## Open next questions

Bind one actual native inverse-bearing caller to the complete-register
grammar. Preserve every input and helper return, and state its extra operator
relations, types and phases. Compare that adapter with its existing exact
oracle and charge physical storage, movement and all paid calls. Polynomial
certificate size alone does not settle those obligations.

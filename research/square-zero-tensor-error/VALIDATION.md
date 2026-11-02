# Validation record

The universal claim is the written scoped proof in PROOF.md. Exact finite
corroboration is supplied by verify.py, without importing a predecessor
verifier or recomputing its scientific claims.

Local environment: CPython 3.12.15, macOS 27.0.1, arm64. The interpreter is
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`.

Both registered commands passed independently with `/usr/bin/time -p`:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/square-zero-tensor-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/square-zero-tensor-error/verify.py
```

Each reported 0.18 seconds real time. These are timeout checks, not a
performance comparison. The package runner also passed metadata, source
pins and both registered scientific commands:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/square-zero-tensor-error
```

Each scientific run printed `PASS_SQUARE_ZERO_TENSOR_ERROR`, with 21,840
literal entries, 6,144 compressed action/Gram entries, 21,840
inverse-transpose entries, 2,080 first-order level terms, 192 precision
choices, 256 mixed rank-two tensor entries and 11 controls. The runner
printed `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `completed`.

In-memory syntax compilation passed without bytecode output. AST inspection
found every function at most 26 physical lines. The proof was checked
directly for the square-zero singular-value decomposition, positive Gram
sector, symmetric restriction, inverse-transpose order and integer
precision rounding. These are author checks, not independent acceptance.

Canonical main was fetched again before publication; it remained
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Live claims and PRs, merged
square-zero/tensor-error queries and tracked main README searches were
rechecked. PR6400 now concerns an exact recovery-location obstruction for
PR6398; it does not compute this ordinary tensor-error quantity.

CI is pending. No proof obligation is delegated solely to CI. Committed-byte
and source-history results are reported in the PR after the commit exists.

## Limits

No physical supplier, chronological amplified caller, rounded native
implementation, scalar-wrapper conditioning, fixed-tape cost, selected
cold replay or formal proof kernel is run. The theorem assumes a unitary
target and relative square-zero error. The finite fixtures do not exhaust
complex matrices or tensor counts.

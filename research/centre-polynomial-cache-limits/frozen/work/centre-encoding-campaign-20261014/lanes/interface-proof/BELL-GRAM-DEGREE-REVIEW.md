# Independent review of the Bell Gram degree bound

The degree bound of 409 is proved for the actual 112-port weighted
operator at every positive tensor size. This is a scalar-polynomial
bound. It is not a lower bound for general weighted ADD circuits,
matrix-valued state, or native decoder cost.

The reviewed proof is
`../history-encoding/BELL-GRAM-DEGREE-PROOF.md`, SHA-256
`bc3a72690735230e8d9995df1a343f69fe8afed7dce056a82505efc83a884698`.
The exact producer certificate has SHA-256
`4b198523d498b85b96445681fdcd8020402b1abb31c6a27e7d2a45d5df2217e2`.

The independent checker derives R from the original local word through
the separate transpose review. It checks equality with the recorded
interface and its label order. It then builds the integer coordinate
matrix `4 A_11`. That matrix has 499,072 nonzero entries. Its largest
absolute row sum is at most 224. This construction does not use the
producer's factored application of R and its transpose.

An exact four-term Pauli expansion checks all 57,344 Bell basis columns.
This binds both the invariant label and every sign. A separate check
shows that the Pauli identity is a common fixed vector of all 112 source
involutions.

The independent sparse map reproduces all 817 moments. Fraction-free
Bareiss elimination gives the same determinant, 2984 modulo 65537.
A duplicate-column control gives determinant zero. The computations
use signed 64-bit integer arithmetic, with explicit bounds that prevent
overflow. The checker does not import the producer or its determinant
function.

The rational Hankel determinant lies in `Z[1/2]`. Its nonzero reduction
modulo 65537 proves that it is nonzero over Q. A scalar annihilating
polynomial of degree below 409 would make the first 409 Krylov vectors,
and hence this Hankel matrix, dependent. The same nonzero minor remains
nonzero after scalar extension.

For the all-size extension, tensor the certified `c=11` block with the
common fixed Bell vector in every other tensor block. This subspace is
invariant. The root coefficient is applied once, so the restricted
operator is the same `A_11`. It follows that the lower bound holds at
each positive tensor size, even if the proposed polynomial is allowed
to depend on that size.

There is also a direct inverse corollary. If `a I+b A_lambda` is
invertible and b is nonzero, a scalar polynomial q with
`q(A_lambda)=(a I+b A_lambda)^-1` must have degree at least 408.
Otherwise `(a+b t)q(t)-1` is a nonzero annihilating polynomial of degree
below 409. This corollary concerns that polynomial representation only.
It does not assert that the inverse needs 408 general circuit gates.

Run from the workspace root:

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 work/autonomous-kappa-run/venv/bin/python -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/review_bell_gram_degree.py
```

The expected status is
`PASS_INDEPENDENT_EXACT_BELL_GRAM_DEGREE_CERTIFICATE`.
The deterministic receipt is `BELL-GRAM-DEGREE-REVIEW.json`.
This review and the all-size extension used OpenAI Codex assistance.
No independent human review is claimed.

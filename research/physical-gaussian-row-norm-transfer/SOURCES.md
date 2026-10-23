# Source records

Base repository and task-card provenance are in `SOURCES.json`.

| Source | Exact commit | File | SHA256 |
|---|---|---|---|
| [PR #3878: physical Gaussian expansion tile](https://github.com/CrocSwap/integer-mult-bounds/pull/3878) | `1a86a8fb73bb7a0982fff99852a031832c191902` | `research/physical-gaussian-expansion/PROOF.md` | `5452f3e2191824b4a8451c83fbdf58b3b2228f4e1966a6f22c3e60bd152e56b0` |

The exact PR #3878 proof bytes are retained in `inputs/`; the local verifier
checks their hash. Its local tile error estimate is used as a conditional
premise. This package does not independently replay the source construction
or certify its analytic error estimate. PR #3877, head
`5e7bdfa3c53bbb5a8d6e81f0efe7005c89184e6a`, was read as live overlap: its
Theorem 2 already gives an all-dimension recurrence for a different
coefficient-rounded operator. That recurrence and the active full tensor join
are explicitly outside this package's result.

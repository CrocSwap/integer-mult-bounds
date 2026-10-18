# Completed checks and timing

The local checks ran on 2026-10-13 with Python 3.14.7 on macOS 26.6.1
arm64. Each process used one Python thread. The environment set
`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`.
Other research workers used the same host. The timing trials had no
exclusive CPU allocation. These are reference-Python measurements.

## Mathematical receipt

Run from the repository root:

```sh
python3 -I -O -B research/dirty-stride-fast-phases/verify.py
```

Expected result:

```text
PASS_DIRTY_STRIDE_FAST_PHASES phases=98 samples=1474 words=16 costs=3 input_controls=7
```

The completed receipt-generation run took 233.52 seconds of elapsed time
and 208.89 seconds of user CPU time. Its command added
`--write /tmp/k9-fast-phase-final-clean.json`. The verifier printed PASS
and wrote the complete receipt. The `/usr/bin/time -l` wrapper then failed
to read `sysctl kern.clockrate` in the sandbox and returned 1. No maximum
resident-set result is claimed from that wrapper.

The following complete package run resolves that exit-status limitation:

```sh
python3 -I -O -B research/dirty-stride-fast-phases/test_package.py
```

It took 245.149 seconds and returned 0. It rejected all seven semantic
faults and the source corruption with their expected `ValueError` text.
It then ran the full main check from a relocated package whose source
files were read-only. The child returned 0, matched the full typed
receipt, and printed the main PASS line. The package ended with:

```text
PASS_FAST_PHASE_PACKAGE controls=8 relocation=1 derivation=1
```

`EXPECTED.json` has SHA256
`71ca33d21be95a42e05c8b6ebb0102e2d1ba59e16709ee3cc7cade8d5cb6e1d8`.
The exact domains, stopping rule, and distinct failure modes are in
`CHECKS.md`. There was no random search. The main check uses explicit
exceptions, so Python's `-O` mode does not remove its checks.

After that package run, `DERIVATION.diff` changed from three context lines
to zero context lines. The corresponding exact comparison changed with
it. This removes blank diff context lines that Git classifies as trailing
whitespace. A focused exact derivation check passed. No mathematical
source or mathematical receipt changed. Later edits add this record,
the benchmark fields, attribution links, and proof clarifications only.

All eight Python files parsed under Python's 3.11 grammar. Local execution
used Python 3.14.7 only. The included CI matrix for Python 3.11 and 3.14
has not run on GitHub. The selected construction and `upstream/` have no
changes. The coordinator owns the shared repository-wide checks; this
worker did not start a second global suite.

## Same-input baseline

```sh
python3 -I -O -B research/dirty-stride-fast-phases/benchmark.py
```

The baseline is the exact PR1038 implementation retained in this package.
Both methods receive the same dyadic input, descriptor `a=-3`, modulus
`m=2L+1`, data precision, and two opposite data passes. Each trial checks
exact data restoration. Every pair has equal data-tape movement. The
new timing includes seed preparation, all state reconstruction, and seed
erasure. The old API has no explicit seed-erasure call.

The final run took 64.709 seconds and returned 0. It ran three alternating
trials per method and case. `BENCHMARK.json` retains every trial, including
preparation, stream, and erasure time. The following values are medians
of total time in seconds:

| L | W | PR1038 | New stream | New seed width in bits |
| --- | --- | --- | --- | --- |
| 32 | 16 | 0.042217 | 0.191425 | 11,000 |
| 257 | 48 | 0.689942 | 1.286691 | 25,350 |
| 2,048 | 96 | 10.187936 | 9.092779 | 55,767 |

An earlier run of the same arithmetic took 64.830 seconds. Its respective
old/new medians were `0.058589/0.243277`, `0.706142/1.327270`, and
`8.170856/7.149857`. The second run added separate seed-counter fields to
the report. The algorithms did not change. The host load changed between
and within both runs; neither run supports a general wall-time claim.

The deterministic work comparison is separate from timing:

| L | W | PR1038 products | New stream products | New seed products |
| --- | --- | --- | --- | --- |
| 32 | 16 | 14,118 | 966 | 5,184 |
| 257 | 48 | 184,686 | 7,716 | 7,920 |
| 2,048 | 96 | 2,293,206 | 61,446 | 11,808 |

These counts include the new seed erasure. Seed products use much wider
operands than stream products. Scalar counts alone therefore do not
establish a bit-time or wall-time ratio. The proof supplies a separate
bit upper bound. This benchmark does not execute full multiplication or
compare complete dirty-factor words.

## Attempts and stopping decision

Three narrow approaches were considered in `CLAIM.md`. The reversible
state recurrence was viable under its full optimistic budget and was
completed. No move to another worker's route was needed.

A direct rounded complex product cannot be inverted on the full grid;
the collision in `PROOF.md` explains why the implementation uses bounded
shears. This is a concrete collision for that map, not a general
impossibility result. Block polynomial evaluation was not implemented
because the completed recurrence already removes per-site series work.

An intermediate main run was stopped at 184.86 seconds to add explicit
chart erasure and charge both chart divisions. It was not a completed
verification run or a counterexample. All final mathematical checks
include that erasure. No failed search is presented as a proof.

The result stops at the specified interface. It retains the inherited
logarithmic array pool and data precision. It does not import PR1054,
emit a native bit-gate program, or discharge supplier hosting and outer
assembly obligations. No new kappa or production speedup is claimed.

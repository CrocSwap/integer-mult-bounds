# Validation

## Executed checks

CPython 3.12.15, macOS 27.0.1 arm64, standard library only. Both declared
`VERIFY.json` commands passed locally with warnings treated as errors, in normal
and optimized modes. Measured direct times were 0.024 and 0.021 seconds,
respectively; these measurements establish the replay budget, not a speedup.
The registered launcher also passed both commands.

Every run checks thirty lower and thirty upper affine residuals, and lists all
86 and 138 vertices of the two relaxed trace polytopes. The primal minima/maxima
match the dual affine bounds exactly. The seven semantic rejection controls
change a tight source row, omit the missing constituent, strengthen either
supporting line, reverse the transvection sign, or substitute an inadmissible
orbit size. All seven reject in normal and optimized modes.

Two additional private-copy controls appended a space to each retained input,
one at a time. Both optimized runs rejected at the source hash gate, before
using mathematical data. Normal and optimized receipts agree byte for byte.
Receipts are generated from the actual execution and include all ten package
file hashes; there is no hand-written saved receipt.

AST parsing/compilation and direct inspection cover the only new executable,
`verify.py`. Its largest function has 34 physical lines. It has no recursion,
dynamic code generation, subprocess or network use. There are two retained
scientific files, at most 30 character types, 435 unordered type pairs and two
trace boundary values per pair. Every read is capped at 262,144 bytes and the
receipt hashes a fixed ten-file list. Python's dynamic allocation is a declared
managed-runtime deviation from fixed-capacity allocation. The bounded inputs,
at most 900 candidate vertices per orbit, and sequential file reads bound live
data; interpreter and standard-library allocation are not instrumented.

## Proof and review limits

The proof was checked against its exact arithmetic certificate. Self-review
covered the use of quotient degrees, the sign and normalization of the trace
constraint, the two orbit sizes, both affine slopes, the Schur propagation, and
the distinction between relaxed and actual spectral attainment. No independent
human, external reviewer or proof kernel is claimed.

No predecessor numerical engine or scientific verifier ran. The threshold,
multiplicity decomposition, group identification and Pauli-orbit trace argument
are cited mathematical premises from PR6714. Hash binding authenticates the
retained data, not the correctness of those inherited premises.

The selected-source orientation passed. No selected cold replay, physical
native execution, full supplier invoice, Lean or Docker build was run. The five
selected framework assumptions remain. Hosted CI is pending; publication-byte,
source-history and export results are reported in the PR body after committing.

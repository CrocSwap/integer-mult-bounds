# Local validation

Platform: macOS 26.6.2, arm64. Validation date: 2026-10-13 UTC.

The complete verifier passed on Python 3.9.6 and on Python 3.13.14 with
`-O -B`, the latter from a different current directory. Both regenerated
byte-identical receipts with SHA-256
`38eae5165067234caf23a7a950fc009afec799bf13f02dbcdaed29982547f520`.
Measured runtimes were approximately 5.78 and 2.59 seconds respectively;
these are observations, not a benchmark comparison.

Each run checked both pinned published fixtures, every nonzero functional
support, all span-class pairings, all live decoder entries, the attaining
witnesses, both independent rank-three minor obstructions, 18 negative
controls and the exhaustive three-dimensional projection controls.

The package was also replayed after applying its patch to a relocated
minimal base containing only the 16 pinned input files. Source-byte and
receipt tampering were separately rejected. Whitespace and selected-result
integrity checks passed. Raw commands, versions, receipts and elapsed times
are retained in the task's external `evidence/` directory.

Three fresh Astra/max branches participated in the bounded search. Final
AI reviews separately checked the algebraic projection proof, code/source
binding and an independent exhaustive obstruction on the corrected fixtures.
No human-only review, Linux CI run, Lean verification, repository-wide
`make verify`, or full supplier cold replay is claimed.

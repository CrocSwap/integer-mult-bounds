# Validation

Executed on 2026-10-13, macOS 26.5.2 arm64, CPython 3.14.8.
Base `66849e1475c930fd7732b1a0067ffee7e1e95f60`; new files are confined to
`research/complex-ck-scaling-fold/`. The upstream main head remained equal to
that base at the pre-submission refresh.

| Check | Result |
| --- | --- |
| `python3 -I -B research/complex-ck-scaling-fold/verify.py` | PASS, 1,022,007 placements, 62/62 real primitives saved, 38/38 exact boundary columns, six controls |
| `python3 -I -O -B research/complex-ck-scaling-fold/independent.py` | PASS, valuation-only search, 644 minimizers, integer matrices, eight controls |
| Main verifier with `-I -O -B`, invoked by absolute path from outside the repo | PASS |
| `python3 -B scripts/verify_selected_result.py` | PASS, exact selected kappa and source/proof inventory |
| Same native payload in an alternate level-1 gzip container | PASS |
| One newline appended to the decompressed native payload | Rejected by source hash before search |
| Certificate primitive total reduced by one | Rejected by certificate comparison |

The last three checks patched file reads in memory and ran the normal verifier
entry point. No committed input or certificate was altered. Arithmetic controls
are part of the shipped commands. Validation does not depend on Python asserts.

The independent AI worker used a different cost representation and integer
boundary implementation. Its review identified two duplicate mutations in an
early main-checker draft; the third mutation now changes the settlement factor,
and the final checks above include that correction. This is not human review.

Full `make verify`, selected cold replay, global invoice/admission regeneration,
Lean and remote Linux execution were not run. This additive research package
does not change a selected source, generator or construction. The scoped checks
verify its finite claim; the full construction's inherited assumptions remain.

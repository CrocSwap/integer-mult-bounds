# Verification bounds and implementation decisions

Build the Lever shaped the result by replacing a larger pair census with a
small exact replay of the facts needed by the new counting proof. Prove It
Works required receipt equality, literal failure controls and publication-byte
checking. Power of Ten shaped the bounded enumeration and enabled checks
that remain active under Python optimization.

The changed code is confined to this package. No source archive, selected
result, shared runner or upstream input changes. `geometry.py` reconstructs
the root data and finite proof facts; `simplex.py` implements the two arithmetic
applications and one sharp calibration; `verify.py` binds the sole external
input and compares the complete receipt. The universal simplex theorem is
proved in PROOF.md, not inferred from that one calibration.

All control flow is structured and nonrecursive. The largest enumeration is
3,309,747 five-flat kernels; the six-flat pass has 788,035. Pivot patterns
number at most 126, each row has at most 32 choices for dimension five or
64 for dimension six, and every product is finite. Root-plane checking has
7,140 pairs times 120 roots. Elimination is at most eight stages on an
eight-by-nine matrix. The behavioral support-charge check has 4^6 cases.
Registered commands have separate 120-second timeouts and run sequentially.

Rule 3 deviation, managed-runtime allocation: Python allocates integers,
tuples and Fraction objects during enumeration. Preventing those allocations
would replace the standard-library implementation. Live data are bounded by
512 112-bit kernel masks, at most four tuples of at most 64 row masks, 113
histogram entries, 120 eight-dimensional roots, their 120-by-120 Gram table
and bounded eight-dimensional exact elimination. Each kernel is processed
and discarded immediately. The sole external input is capped at 2 MB and
is 971,985 bytes at its pinned version. Generated receipts are written only
to a new external path. Temporary test files use scoped cleanup under
`TMPDIR`. The full replay exercises these capacities. A native implementation
would be justified only if future dimensions exceed these fixed bounds.

Functions remain below 60 physical lines. Internal checks use `require`,
which raises ValueError even with `python -O`; untrusted labels, input bytes,
support caps, dimensions and output paths are checked at their boundaries.
Read-only tuples and function-local histograms avoid shared mutable state.
No dynamic evaluation, registration, runtime code generation or callback
chain is used. A returned receipt is compared structurally, not accepted
because a process exited successfully.

Python's interpreter does not expose C-style dereference limits. Data access
is limited to bounded tuples, arrays and dictionaries; direct calls have
visible targets. No assertion, warning filter or failure status is suppressed.
All mathematical runs use `-W error`; controls also run under `-O`. The
available environment has no separately installed Ruff, Mypy or Pyright.
Bytecode compilation and the registered commands provide recurring language
diagnostics; no repository-wide lint configuration is introduced for this
isolated package. A future repository-wide static-analysis policy should
include these files. Exact commands and results are in CHECKS.json.

The abandoned relaxed twelve-deletion census is not proof evidence. Its
partial output remained only in disposable session scratch and is removed
after publication. The new theorem does not rely on its prefix or on a
failed search.

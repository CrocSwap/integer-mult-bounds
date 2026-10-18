# Verification scope and implementation bounds

Build the Lever changed the deliverable from a calculation into
`verify.py`, a rerunnable receipt with exact source pins. Prove It Works
requires the direct replay, failure controls and an exported-source check
before publication. Unslop is used for the written result. The new
contribution is the deletion/application proof; retained geometry is
explicitly attributed rather than called an independent implementation.

The replay uses only Python's standard library. New functions are below
60 physical lines. External input and retained source sizes are checked
before parsing or importing the geometry. A source-hash failure precedes
the import in the production replay. `ValueError` contracts stay enabled
under optimized Python. No assertions carry acceptance conditions.

All mathematical domains are fixed: 120 roots, 112 live coordinates,
nine binary coordinates, at most eight rational coordinates, five star
extensions, at most 240 signed roots per extension, 7,140 root planes,
3,309,747 five-flats and 788,035 six-flats. The historical weight scan
uses at most nine pieces in six weight classes; the unchanged original
filter covers its fixed 24 cells in a child limited to 45 seconds.
The registered replay and controls have explicit timeouts.

State belongs to the replay call. The optional receipt is a fresh external
file opened exclusively; it never overwrites existing evidence. Failure
propagates. Direct replay creates no checkout outputs. Tests create
bounded temporary copies under `TMPDIR` and remove only those copies.
Read-only source exports are supported by making disposable copies
writable before applying mutations.

Power of Ten deviations are confined to Python and retained inputs:

- Rule 3, fixed allocation. Python and `Fraction` allocate at runtime.
  Live collections are bounded by the fixed domains above; flat
  enumeration stores only 113 histogram bins, not millions of flats.
  The historical subprocess output has 24 rows. A native fixed-capacity
  implementation is appropriate only if a future larger domain needs it.
- Rule 8/9, runtime dispatch. Ordinary Python imports and unittest mocks
  use runtime dispatch. Production imports have a fixed target set,
  authenticated source files and no user-selected module names. Tests
  use mocks only for child failure and incomplete-output controls.
- Rule 10, diagnostics. Python has no static compiler equivalent.
  Warnings-as-errors execution, compilation and available Ruff checks
  cover new code. Retained files remain byte-identical and are not
  reformatted to impose a new style. No global lint or CI policy changes
  are part of this isolated proof package.

No new recursion, unbounded retry, macro or dynamic code generation is
introduced. The inherited module contains other finite routines outside
the invoked path; only `root_extensions` and the named geometry functions
support this result. The retained original filter's top-level execution
is isolated in the bounded child. No historical supplier replay, Lean,
Docker or concurrent artifact-regenerating suite is required.

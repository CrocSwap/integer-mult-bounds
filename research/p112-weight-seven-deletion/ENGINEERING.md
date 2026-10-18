# Implementation boundaries

The new entry points are `verify.py` and `test_verify.py`. Only this package
and its declared immutable P112 input are read. A receipt may be created
only at an exclusive external path. No selected supplier, shared verifier,
frozen predecessor or global configuration is changed.

Build the Lever shaped the choice to keep an exact rerunnable receipt rather
than just a numerical claim. Prove It Works shaped the complete capacity
replay, literal source binding and losing controls. The mathematical change
is dimension deletion before the existing coordinate inequality, not a new
abstraction or a larger search.

## Power-of-ten inspection

- No recursive calls, callbacks or unstructured control flow were introduced.
  Exceptions propagate; the only output handle uses a context manager.
- Every search has fixed bounds. Geometry has 120 roots, 112 live lines and
  nine binary coordinates. Flat enumeration covers 3,309,747 and 788,035
  subspaces. Endpoint checks cover `7^6` assignments. Historical profiles have
  six weights and lengths six through ten; prior-cover tests use 210 index
  quartets and at most 81 assignments per distinct basis.
- Functions remain below sixty physical lines. Internal assumptions use
  always-enabled `require` checks; the replay also runs under optimized Python.
- State is local except fixed geometry/weight tables and package paths.
  No code mutates those tables. Inputs have explicit size limits and
  SHA256/semantic checks. CLI failures,
  invalid dimensions, strict support cutoffs, changed inputs and output
  conflicts are covered by tests. The CLI has no mutation other than optional
  receipt creation, so no network or subprocess cleanup is needed there.
- The one test subprocess executes the retained original fixed checker with a
  thirty-second timeout, captures its result and propagates failure. The
  registered runner gives each command a 120-second limit.
- No generated code, reflection, runtime registration or indirect dispatch was
  added to the proof path. The retained original checker is tested unchanged.
- Local diagnostics use Python warning mode and Ruff's applicable error,
  undefined-name, bugbear, modernization and comprehension checks. No warnings
  are suppressed. CI uses the registered standard-library replay and tests;
  no repository-wide lint/build configuration is changed.

## Managed-runtime deviation

Rule: 3, fixed allocation after initialization.
Location: `geometry.py`, `obstruction.py`, `verify.py`, `test_verify.py`.
Reason: Python integers, exact rational elimination and collection iteration
allocate dynamically. Replacing them would expand this research contribution
into a different runtime implementation.
Scope: This finite standard-library replay only.
Compensating control: All combinatorial domains are fixed above; a flat mask
and histogram are processed at a time, not retained for millions of flats.
Source input is at most two million bytes and each retained source at most
100,000 bytes. Temporary test copies are context-managed and bounded to those
same files. No solver, native build, service or unbounded worklist is used.
Verification: Full replay, failure controls and a second-interpreter export.
Follow-up: Reassess allocation and capacity if any dimension or input limit is
made configurable. Current limits are not performance or memory benchmarks.

The standard Weyl-chamber theorem, original decoder-level reduction and
independent human/proof-kernel review remain outside executable coverage.

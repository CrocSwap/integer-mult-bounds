# Implementation bounds and verification limits

The changed paths are isolated to this package. Its two execution boundaries
are `verify.py` and `test_verify.py`. Frozen files in `vendor/` are raw exports,
not modified implementations. No selected construction, shared compiler or
repository test policy changes.

## Power of Ten inspection

1. New code is structured and nonrecursive. Exceptions propagate. Temporary
   directories and log files use context managers; explicit fresh `--work`
   outputs intentionally survive until the caller removes them. There are no
   background processes. Transport subprocesses have 90-second timeouts.
2. H=9 and N=512 are fixed. Sparse operators have 512 columns, each with at most
   512 entries. Actual target columns have two entries, source columns one,
   and intermediate source products at most four. Preparation is capped at
   12,000 events and 632 live row roles. Input precision is 1..251, bit width
   4..256, and a fanout has at most 8,192 gates and 1,281 wires. Four targets,
   two policies, three replay widths and five vector fixtures are fixed.
   Tests have exactly 1,200 coupled four-bit valid cases. File reads and
   decompression stop at 8,000,000 bytes. Ten frozen files are required.
3. Python integer, Fraction, container and JSON operations allocate dynamically.
   This is a managed-runtime deviation. The enforced finite sizes above bound
   live mathematical data. Work is serial, with at most two bit programs and
   three sparse physical operators needed at one comparison. This is not a
   measured maximum RSS guarantee for the interpreter.
4. Every new function is below 60 physical lines. The scalar pullback, Gaussian
   operators, native reference replay, bit producer/evaluators, source boundary
   and CLI have separate responsibilities. Frozen transport's cohesive `run`
   exceeds this guideline; splitting a scientific input is outside scope.
5. Always-on contracts check literal A gates, frames, preparation rows, unique
   Gaussian variables, exact norms, grids, monomial unit phases/bijections,
   source closure, complete bit-state equality, exact counts, source hashes
   and receipt equality. Grid/range, cleanup and phase failures have controls.
   There is no reliance on new Python `assert` statements.
6. Mutable state is local to one replay. Circuit records are immutable. Source
   and target wires are disjoint, source ownership is exclusive during the
   four-ADD caller, and one carry is reused sequentially. Constants describe
   finite bounds only. The caller does not claim those resources are available
   in the selected hosted supplier.
7. Filesystem, process and JSON errors propagate. Subprocess success is checked;
   captured occupied-output failures are checked explicitly. Input/source sizes,
   containment and regular files are validated. Circuit writes are checked and
   read back. Width, guard, result range, wire aliasing and final carry/source
   restoration are checked before a successful receipt.
8. New code has no dynamic evaluation or plugin registration. Generated data is
   explicit indexed CNOT/Toffoli gates. Dataclasses and unittest use ordinary
   bounded standard-library dispatch. Frozen compiler macros are not rewritten.
9. New calls and data access are direct. The independent bit evaluator imports
   no producer. The independent Gaussian evaluator imports only the pinned
   native Clifford implementation, not the primary sparse arithmetic.
10. Local validation enables warning errors and Ruff E,F,I,B,UP,SIM,C4,PIE,RUF,
    checks formatting and compiles source. Registered replay runs arithmetic
    and behavioral checks. No diagnostic suppression or repository-wide build
    policy change is added. Frozen input formatting is preserved deliberately.

## Frozen native deviations

Rules 1-4 and 10, location `vendor/bw_transport.py`, `vendor/bw_emit.py` and
`vendor/clifford_exact.py`. The retained implementations include data-dependent
elimination/normalization loops, dynamic allocation, long functions and legacy
style diagnostics. Rewriting them would alter immutable scientific inputs and
expand this independently reviewable change. Their fixed authenticated inputs
have h=9, 632 compact roles and bounded word sizes. The independent column
replay accepts at most 30 elementary circuit events and six Fourier divisions;
normalization therefore has at most six halving steps at a time. Binary
elimination has at most nine pivots. The transport and emitter run with assertions enabled
in checked, timed subprocesses and a private bytecode cache. All operator
columns are compared with separately implemented exact sparse arithmetic.
A future native implementation should retain these explicit bounds and assess
its own allocations and diagnostics rather than edit these source exports.

## Decision and review record

Build the Lever led to committed exact Gaussian and gate-list replayers.
Prove It Works required execution of serialized baseline and candidate gates,
not just algebraic operation counts. Test Behavior, Not Implementation led to
literal quarter/range witnesses, signed outputs and cleanup failures. Laziness
Protocol kept the work to one literal adjacent group rather than another
frame/root search or a new compiler abstraction.

The first local scope was A13 alone. Its three adjacent equal-source half-ADDs
have the same prepared norm and grid, so the scope became the complete four-ADD
block and one shared sign-fill lifetime. Source-closing audit initially had a
24-event cap; literal expansion is 30 events with six Fourier divisions. The
bound was corrected to those actual finite limits before the final replay.
No scientific claim was weakened to pass a check.

No separate subagent capability was available. Proof/resource and source/
behavior review passes were performed locally. The two implementations are not
independent human or formal-kernel review. Full physical producer interiors,
approximate children, routing/stock/hosting and the eventual consumer remain
explicitly unverified.

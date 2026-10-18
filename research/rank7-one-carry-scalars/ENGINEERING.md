# Engineering scope and checks

Build the Lever shaped the deliverable: the literal generator, cold replay and
complete invoice are rerunnable artifacts. Prove It Works required execution of
the emitted Boolean gates, restored source/carry checks and fresh native bindings.
Power of Ten shaped the finite width, coefficient, gate and truth-column limits.
The autonomous-run exit predicate is one complete source-bound scalar composition
with a strict local logical-gate reduction and one clean carry, with the changed
exclusive-borrow premise explicit. No full supplier or kappa predicate is claimed.

## Code inspection

- Structured loops, exceptions and context-managed temporary directories; no
  recursive call cycle. Native source is frozen and its engine remains inherited.
- Width 4..256 in the primitive, 23..256 for the full-layer tariff; shifts −12..8,
  at most nine coefficient terms, at most 32 recipe units, at most 20,000 gates.
  Right-shift k<W is enforced; supported full-layer shifts are only −3..1.
- Dependency inventory is bounded to 64 records, with 30 live inputs and two provenance rows, each at most 8 MB.
  Native replay enforces its retained source bounds. Temporary replay outputs
  are owned by the calling session and default cleanup uses TemporaryDirectory.
- Every new function is under 60 physical lines in normal formatting. Runtime
  `require` contracts remain active under optimized Python. Gate ports are
  distinct and constrained to two operand banks plus one carry.
- Exhaustive batches are capped at 65,536 truth columns; actual widths 4..7 use
  at most 16,384 input pairs per template. Larger fixtures are 5 widths × 31
  templates × 10 cases. Gate loops have the explicit gate bound above.
- Hash comparisons occur before predecessor import. CLI `--work` rejects an
  occupied path and output inside the repository. The final JSON is compared
  with the committed receipt on every normal replay.
- No generated code, dynamic evaluation, preprocessing, network access or extra
  checkout is part of replay. All runtime input paths are declared in VERIFY.
- Diagnostics: Ruff E9/F/B correctness checks, Ruff formatting, Python compilation
  with warnings as errors, registered Python 3.12 replay and optimized controls.
  Shared CI configuration is unchanged; this package opts into its runner.

## Managed runtime and dispatch deviations

Rule: 3, fixed memory capacity.
Location: all Python generators/interpreters and the retained native replay.
Reason: Python allocates objects during arithmetic and collection construction;
fixed-allocation execution would require replacing the runtime and frozen engine.
Scope: finite local verification, not a production memory-bound claim.
Compensating control: widths, coefficients, gates, truth columns, input sizes and
registered runtime are bounded; temporary output is context-managed.
Verification: boundary rejection controls, small exhaustive runs and the registered
cold replay; object-count bounds above. Python/library allocation is not instrumented.
Follow-up: supply an allocation-accounted backend before claiming physical memory
or all-size supplier storage from this executable model.

Rule: 9, indirect calls.
Location: verify.factory and checks.run.
Reason: the source-bound circuit/guard pair is supplied across the checker boundary;
Python dispatch and the frozen native engine are retained.
Scope: one build closure (this package's circuit with the authenticated expansion)
and one guard target (PR3094 caller.guards); no plugin or runtime target search.
Compensating control: named fixed targets, authenticated imports and bounded alphabets.
Verification: both interpreters, semantic mutants and all four native bindings.
Follow-up: remove this substitution boundary if the checker and implementation
are later combined into a production backend; no such backend is claimed here.

No unavailable static typing/compiler guarantee or complete inherited-engine
Power-of-Ten compliance is claimed. New code does not edit or widen that engine.

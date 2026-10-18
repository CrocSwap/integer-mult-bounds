# Bounded implementation and checks

The kept change is one isolated research package. It calls an unchanged,
SHA256-bound geometry module rather than copying or editing predecessor code.
The real result is the written characteristic-zero implication in PROOF.md;
the finite replay checks its declared premises and arithmetic, not the whole
multiplication theorem. No subagent or independent human review was available.

## Power-of-ten inspection

1. All new paths use structured loops, exceptions and context-managed files.
   There is no recursion. Input/proof failures propagate as nonzero exits;
   output files are closed on success or failure.
2. Weights have length at most ten, support invoices have exactly six
   endpoints, and dimensions are at most sixteen. Historical enumeration
   checks 7,546 multisets. Prior covers inspect at most 210 index quartets
   and 81 assignments per quartet. Endpoint enumeration has `7^6` assignments.
   The inherited geometry has fixed dimensions and exactly 4,097,782 flat
   iterations. Each registered command has a 120-second bound; the historical
   subprocess has a 30-second bound. The test subprocess emits 24 lines.
3. Python allocates managed objects during execution. Direct fixed-memory
   compliance is unavailable in this runtime. Live state is bounded by those
   input sizes: the geometry keeps small histograms and at most 120 roots,
   not a stored list of millions of flats; the historical list has 69 rows.
   Each input is limited to two megabytes before reading. The interpreter and
   standard-library internals were not allocation-instrumented.
4. AST inspection finds maximum new function lengths of 24, 19 and 15 lines
   in ledger.py, test_verify.py and verify.py, respectively.
5. Explicit `require` contracts remain active with `-OO`. They check dimensions,
   strict support cutoffs, exact input inventories/hashes, profile inclusion,
   arithmetic margins and receipt equality. Tests use unittest checks rather
   than removable Python assertions. No density-only assertions were added.
6. Mutable evidence is function-local. The only import-path change is scoped
   with `finally` and undone immediately. No shared cache or frontier record
   is modified. Test patches are scoped and disposable copies are private.
7. Source reads, exclusive writes and the historical child process either
   return checked results or raise. The child is SHA-bound, uses no shell,
   has a timeout and checks its exit code, stderr and exact row count.
8. No generated code, decorators or evaluation of input text is introduced.
   The one late ordinary module import is necessary to authenticate the
   retained source first. The registered runner supplies private bytecode
   isolation. Direct execution assumes a trusted interpreter/import cache.
9. Calls are direct and data access is shallow. unittest dispatch and scoped
   mock patches are bounded standard-library test mechanisms, not production
   plug-ins. The input module name and location are fixed in the driver.
10. The registered interpreter uses `-W error`; tests also use `-OO`. Applicable
    Ruff checks cover E4,E7,E9,F,B,C4,ICN,PIE,PGH,RUF,UP,SIM,I. Compilation uses
    `compile` in memory and AST function-length inspection, leaving no bytecode.
    CHECKS.json records the exact commands. The replay manifest makes behavior
    and warning checks recur when the package or a declared input changes.

Rules 3 and 9 use managed-runtime/framework deviations. Their scope is this
bounded one-shot Python replay and unittest suite; collection bounds, timeout
checks, cross-version execution and disposable-copy cleanup are the compensating
controls. A future port to a fixed-memory runtime must implement fixed-capacity
buffers before claiming direct compliance. No such port is needed for this
mathematical contribution.

An exploratory Ruff ALL scan also suggested converting unittest to pytest,
adding namespace-package markers and forbidding CLI output/late imports, plus
project-wide annotation/docstring style. Those policies do not apply to this
standard-library standalone verifier. Applicable complexity, import ordering,
tuple construction and comparison findings were resolved. No suppression is
added to source. The applicable check set above passes; a clean ALL result is
not claimed.

The registered replay, independent subset oracle, failure controls, mutation
checks and source-only export are verification evidence. The geometric engine
is re-executed, not independently reimplemented. Standard Weyl theory and the
original decoder reduction remain written dependencies. No Lean, Docker,
physical implementation, native supplier or full selected replay was run.

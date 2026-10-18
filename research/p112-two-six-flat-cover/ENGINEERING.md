# Bounded verification implementation

The new code changes only this research package. It reads one pinned data
file and four retained source/license files. Default replay compares an exact
receipt and writes no mathematical artifacts. Optional output uses exclusive
creation outside the checkout. Source, input, witness and output failures raise
errors; no assertion disappears under Python optimization.

Build the Lever shaped the choice to retain both complete enumerators and the
pair-cover checker. Prove It Works shaped the complete mask equality and literal
attaining witnesses, rather than trusting a saved maximum. The autonomous-run
exit predicate is the sharp cover theorem plus its actual preferred-basis caller.
The local decision trail is audited before publication and summarized in CHECKS.json.

Power of Ten inspection of cover.py, independent.py, verify.py and test_verify.py:

- Control flow is iterative and nonrecursive. The only subprocess is the frozen
  original filter, with checked status, captured output and a 120-second timeout.
- Dimensions are fixed at nine/eight; flat counts are bounded by 788,035 and
  777,240. Root count is 120, support size 112, high-intersection capacity 4,096.
  Pair checks have at most 4,096*4,097/2 iterations per root. The actual retained
  inventories contain 320 or 336 intersections. XOR witness closures are bounded
  by 64 elements. The code checks exhaustion/capacity and exact census totals.
- All new functions are below sixty physical lines. Mutable state stays local.
  Mathematical invariants have runtime checks, including complete census totals,
  capacities, independent equality, binary rank, sharpness and application bounds.
- Source bytes and paths are checked before mathematical replay. The CLI
  explicitly rejects linked inputs, oversized files, inside-checkout outputs
  and preexisting output files. Retained source hashes and input hashes bind
  the replay; tests exercise those failure paths.
- There is no generated code, dynamic evaluation, reflection or registration.
  New data access is shallow and call targets are explicit. No shared-code or
  global diagnostic configuration is changed for this isolated package.

## Managed-runtime deviation

Rule: 3, fix memory capacity before steady operation.
Location: the finite enumerators and per-root intersection sets.
Reason: Python integers, sets and tuples allocate dynamically; prohibiting
allocation would require replacing the standard-library verifier with native
storage and expand its scientific review scope.
Scope: one bounded single-process replay, with at most 788,035 primary entries,
777,240 affine cosets, 776,806 distinct masks per enumerator and 120 receipt rows.
Per-root intersection sets have at most 776,806 entries and are replaced each
iteration. Direct fixed-dimensional loop bounds constrain every allocation.
Compensating control: no input-dependent dimensions or unbounded work queues;
input file sizes are limited to two MB; masks are at most 112 bits; the generic
runner also enforces command timeouts. No mathematical artifact is regenerated
in the checkout.
Verification: full registered replay, exhaustive small pair controls and the
oversized-inventory rejection control in test_verify.py.
Follow-up: use preallocated native arrays only if a concrete larger domain or
memory failure warrants a separate, independently checked implementation.

Frozen vendor sources are authenticated and left unchanged. Their original
style and lack of recurring static-analysis configuration are retained as
predecessor limitations. New source is checked separately with Ruff and
warnings-as-errors compilation; exact commands are in CHECKS.json. The package
runner is the recurring validation entry point, with default Python 3.12.

## Static-analysis scope

Ruff 0.17.1 was first inspected with all rule families. Repository-inapplicable
style policies included mandatory public type/doc annotations, per-file copyright,
namespace-package markers and a ban on CLI output. They are not enabled as a new
repository convention for these standalone scientific scripts. The final profile
uses E,F,I,B,UP,S,C4,PIE,RUF,PERF, including security and correctness checks.

The sole local suppression is S603 on verify.py's subprocess.run call. The command
uses the running interpreter, a fixed package-local filter whose exact SHA256 and
Git blob are authenticated before replay, isolated Python mode, no user-supplied
arguments, checked exit status and a 120-second timeout. The linter cannot infer
this source-binding contract. No shell, dynamic command text or external executable
name is accepted. The unchanged original filter is retained for reproducible source
comparison, so replacing it just to remove this diagnostic would weaken evidence.
Source mutation controls and the complete original table replay check that contract.
Revisit the suppression if this command ever accepts a configurable source or argv.

# Verification and implementation limits

Engineering-mode used the autonomous-run playbook. The exit predicate is one
source-bound useful result, with proof, deterministic evidence and a focused PR.
`decisions.tsv` records the bounded research decision and retained result.

Build the Lever led to `contractions.produce` and the explicit 24-witness
certificate. Prove It Works required actual native transport/emitter execution,
complete emitted-ledger comparisons and source-byte checks. Power of Ten led to
finite input capacities, bounded loops and subprocess timeouts.

## Power of Ten scope

New code is `contractions.py`, `verify.py` and `test_contractions.py`. No shared
repository module changes. Frozen predecessor modules remain byte-identical.

1. Control flow is structured and nonrecursive. Context managers own files and
   disposable directories. Child failures propagate; explicit work directories
   preserve diagnostics. Test class cleanup also runs after setup failure.
2. Exactly 24 edits, 4,079 A gates, 704 registers, 12 frozen inputs, two providers,
   three source versions and two native scripts bound the work. Each native
   subprocess has a 90-second timeout. JSON files and decompressed payloads are
   capped at eight million bytes; emitted streams are capped at 30,000 events.
3. Python, rational arithmetic and the inherited compiler allocate dynamically.
   This is a managed-runtime deviation from fixed steady-state allocation. The
   finite capacities above bound retained collections; the replay is a bounded
   batch, not a service. Compiler internals are inherited, not rearchitected.
4. New functions stay below the roughly 60-line ceiling in normal formatting.
5. Explicit `require` contracts cover preimages, matrix commutation, exact
   coefficients, costs, addresses, cleanup, frame paths, native invoices and
   source bytes. They remain enabled under `-O`.
6. State is local to one producer or one private replay directory. No shared
   mutable registry, worktree writer or broad lifecycle state is introduced.
7. Writes check returned byte counts for native inputs. Child exit codes and
   timeouts are checked. Read results are consumed. Mutation tests verify failure
   behavior and compare against literal matrix/cost expectations.
8. No dynamic evaluation, generated Python, decorators with hidden registration
   or runtime code construction is introduced. Unittest decorators and normal
   test discovery are the framework exception, with a finite test inventory.
9. Calls and data access are direct. Standard-library sort/JSON operations and
   unittest dispatch are bounded framework/runtime exceptions to a C-style ban
   on indirect calls. There are no pointer operations.
10. New files receive strict Ruff checks, formatting checks, warnings-as-errors,
    source compilation, normal and optimized behavioral checks and registered
    Python 3.12 replay. Frozen code is excluded from new style checks to preserve
    source identity; its own warnings/errors still fail native execution.

The reused compiler has assertions and runtime allocation. Compiler children
explicitly remove inherited `PYTHONOPTIMIZE` and run without `-O`; imports use a
fresh private bytecode namespace. These are retained constraints, not claims
that the inherited code satisfies every Power of Ten rule.

## Scientific limits

The elementary-matrix proof checks the changed forward subprograms; paired
forward/inverse native endpoint tests alone would not establish that equality.
The non-scalar stream and every charged recursive child are preserved. No full
physical coefficient-stream, precision, ownership, all-size or outer theorem is
replayed. Runtime speed, instruction materialization and a new κ are not inferred
from the smaller conservative compiler bound.

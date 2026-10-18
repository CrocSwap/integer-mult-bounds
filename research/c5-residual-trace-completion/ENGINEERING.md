# Verification and resource decisions

The falsifiable predicate is sharp complete-plane cost20 on exactly the four
listed strict-scalar C5 cores over Q/R/C. The scientific paths are verify.py,
independent.py and test_verify.py. Shared code, selected records and frozen
inputs are unchanged. Separate Before Serializing Shared State led to an
owned package/worktree/cache and short OS locks for shared Git metadata.
Prove It Works led to actual committed export replay before review freeze.

Power of Ten inspections apply to those three paths:

1. Control flow is structured and nonrecursive. Fixed-path module loading
   has two explicit failure exits. Temporary source controls use scoped
   cleanup. All verifier errors propagate to a nonzero process exit.
2. Geometry has112 labels/56 planes. Each core has32x32 support pairs, at most
   ten labels per side and nine binary label bits. Trace systems have at
   most15 rows, five unknowns and six columns. The excess box is explicitly
   capped at200000 tuples; each count box is capped at6000000 states. Four
   fixed cores and costs 18/19 bound the outer work. Independent cost layers
   are 0..19; their finite state coordinates have the same box bounds.
3. Python allocates managed integers, lists, dictionaries, Fractions and
   sets during replay. Fixed allocation is unavailable for these standard
   types. This runtime deviation is bounded by the finite domains above,
   one process at a time, and 120 second registered command timeouts. The
   actual count certificate has 5327 states across 58 cases. No child process
   or background solver is launched. The numerical discovery solver is
   session scratch, not an imported replay dependency.
4. All functions are at most 60 physical lines after formatting.
5. Runtime need/require contracts check physical C5 incidence, nonnegative
   defects, exact free-term behavior, finite capacity, queue exhaustion,
   actual strict scalar fit and source integrity. They survive Python -O.
6. Mutable state belongs to one function, process or test directory. No
   shared replay artifact is regenerated. RESULT.json is read-only unless
   explicitly generated during author preparation outside registered replay.
7. Source boundaries validate inventory length, exact schema, exact paths,
   fixed usages, regular files, size limits, SHA256 and Git blob hashes.
   Zips are strict. Failure controls test both live source mutations and
   usage reclassification, malformed schemas, duplicates and extra entries.
8. No code generation or evaluation occurs in replay. The two companions
   explicitly load only the fixed adjacent verify.py module. This is a
   Python import-mechanism deviation, with a single visible local target;
   its failure is checked. Package/source export binds those bytes.
9. Scientific calls are direct. The sole indirect target is the fixed
   module loader above. There are no application callback chains.
10. Ruff E,F,B,I,UP,C4,SIM and formatting, warning-strict Python execution,
    registered replay, optimized controls and committed-byte/export checks
    are the scoped diagnostic surface. No unavailable native/compiler,
    Lean or Docker check is implied.

The independent script shares only authentication and receipt hashing. It
rebuilds actual dense pairing matrices, uses fraction-free integer trace
elimination, regenerates all excess cases, and groups states by paid cost.
It does not call the primary scientific routines. The internal peer check
is separate automated read-only review, not human or proof-kernel approval.

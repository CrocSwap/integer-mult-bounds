# Bounded implementation and verification

## Scope and principles

Only this isolated package is new. No shared verifier, frozen input,
selected record or predecessor package changes. Build the Lever selected a
small deterministic theorem checker rather than a search receipt alone.
Prove It Works required the registered replay and a second source-only
interpreter replay. Test Behavior, Not Implementation selected independent
root-lattice labels, frame traversal and binary elimination as controls.
Laziness Protocol kept this to one actual caller and reused unchanged,
source-bound geometry instead of changing the historical implementation.

The exact metric is one newly excluded named profile. The first attempt,
the support-only A3 count, gives equality 80 and is retained as a losing
control. The second uses the endpoint binary rank to reject equality. There
is no timing, statistical evaluation or runtime-speedup claim.

## Power-of-ten inspection

1. All new control flow is structured and nonrecursive. The frame search
   uses an explicit stack; the independent test uses level-by-level lists.
   Errors propagate as ValueError, subprocess failures or timeouts.
2. Inputs are the fixed 120 roots and nine-bit labels. Production frame
   traversal has a one-million-node budget and a 961-entry stack cap; its
   observed complete inventory has 352,876 nodes and 2,025 frames. Orbit
   queues are bounded by 240 roots. Binary closures contain at most 512
   elements. The independent frame test has eight levels and a 200,000-
   prefix cap checked before every extension, with at most 120 candidates
   per update.
   All combinations/products range over explicit finite domains. The
   retained six-flat census has exactly 788,035 subspaces.
3. Rule deviation, managed Python allocation. Python integers, sets,
   Fraction and JSON allocate during computation. Fixed-size domain checks,
   collection caps and two-megabyte source-file limits bound live state.
   No service or unbounded stream is introduced. The independent traversal
   holds at most two bounded levels at once. A separate code reviewer
   identified a post-growth check in the independent frame test; the
   capacity check now runs before every list extension. If the domain
   becomes a user parameter, replace these structures with validated fixed-capacity
   storage or retain an explicitly revised capacity contract first.
4. All affected functions, including the unchanged geometry copy, are
   under the roughly sixty-line review limit in normal formatting.
5. Side-effect-free require checks enforce geometry, source, coverage,
   capacities, exact frame shapes, binary spans and receipt equality.
   They remain active under `-O` and `-OO`; tests use unittest assertions.
6. Mutable state is local to one bounded function. There is no shared
   mutable cache or background verifier. Source bytes and dependencies
   are explicit; no network or Git objects are needed for direct replay.
7. Returned values are consumed or deliberately used only as success
   checks. The original source program's exit status and output table
   are checked. Missing, oversized, linked or changed source files reject.
   The original pinned program has a 120-second timeout. The registered
   commands each have a 240-second timeout.
8. There is no dynamic evaluation, code generation or production runtime
   registration. Test-only unittest mocks deliberately exercise source and
   output failures. Their targets and lifetimes are local with scoped
   cleanup. This is the bounded test substitution deviation for rule 8.
9. Calls are direct. Test-only mock dispatch is the rule-9 framework
   deviation, confined to named test contexts. No arbitrary callback or
   plugin is accepted by the production checker.
10. Ruff diagnostics and formatting checks cover new code; warnings-as-
    errors and syntax compilation cover Python execution. The unchanged
    geometry copy is hash checked rather than reformatted. Registered
    replay repeats the exact theorem checker and behavioral tests in CI.
    No static proof or complete multiplication verification is inferred.

The original filter and retained geometry remain independently bounded
predecessor code, not a repository-wide cleanup target. Their attribution
and bytes are preserved. CPython allocation behavior and the standard
Weyl-chamber theorem are not formally verified here.

## Failure and output handling

The verifier does not write by default. An optional receipt must be a new
file outside the checkout; exclusive creation propagates existing-file
errors without overwriting. A write failure can leave a partial new
external receipt, which must not be treated as evidence of a passing run.
Tests and registered checks do not regenerate committed evidence.

The first registered run caught a comparison bug between integer histogram
keys and their JSON string representation. The comparison now normalizes
the fresh object through JSON before structural equality. A fresh-model
versus committed-receipt test covers this failure. Mathematical values and
the frozen acceptance predicate did not change.

The first direct invocation used Python's `-I`, which hides the script's
local imports. The documented direct interface is `-B`, not `-I`; the
registered runner supplies its own isolated bytecode namespace. Replay
commands in CHECKS.json use that supported interface.

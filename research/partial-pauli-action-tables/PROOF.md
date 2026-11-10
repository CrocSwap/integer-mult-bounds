# Exact finite binary actions with invocation-local tables

This contribution was produced by Nick Petalas. Apache-2.0.

## Equivalence on the declared domain

Let `v=(v_0,...,v_(k-1))`, with `0<=k<=4` and each v_j an integer in
0..15. Let `0<=x<2^k`. The original action is the XOR of those v_j
whose bit j in x is one. It is defined even for zero or dependent columns.

Initialize `T[0]=0`. For c=1,...,2^k-1, let b be its least set bit,
with b=2^j, and set

```text
T[c] = T[c xor b] xor v_j.
```

Because `c xor b<c`, strong induction proves that every T[c] is precisely
the original action. The removed bit j occurs once and every other set bit
is retained. This proves the replacement on the entire declared domain.
The bound four is the fixed caller's two-qubit domain, not a restriction on
the predecessor's written dimension-uniform mathematical theorem.

The dictionary key is a tuple copy of the columns. A later mutation of an
input list therefore selects a different value key. Tables belong to a
single `make_action` closure and cannot be reused across independent replay
invocations. The fast path trusts the authenticated caller's integer-column
contract; it is not a general parser for arbitrary Python numeric objects.
Fresh-key validation and the mask check reject the named malformed controls.

There are at most `sum_(k=0)^4 16^k=69905` possible valid keys and
`sum_(k=0)^4 32^k=1082401` entries across all possible tables. The implementation
enforces key and table capacities. For the actual complete command it builds
only 3,466 tables and 32,551 entries. Each table takes one action-value XOR
per entry after zero, giving 29,085 such XORs. Direct counting of every
original mask gives 468,473 accumulator XORs. Index XORs and dictionary work
are excluded from these operation counts and included in wall measurements.

## Binding to the complete caller

The adapter reads and SHA256-authenticates the exact declared source before
compiling those bytes, so preexisting Python bytecode cannot replace the
retained verifier. It changes only the private module's `act` binding, then
calls the original `main` unchanged. Every original action call uses at most
four four-bit columns and a valid coordinate mask. The complete transcript
checks this finite binding against every original action, and exhaustive
domain equality establishes the replacement independently of digest equality.

Identical action values leave group/subspace enumeration, completion-fiber
minima, selected representatives, signed corrections, literal rational
matrix columns and controls unchanged. No mathematical success, source
table, completion list or signed lift is reused from an earlier process.
Source authentication, table construction and every original check occur
inside each timed command. Both timing sides use the same authentication
wrapper; only the action implementation differs.

The result is an implementation-equivalence proof and a bounded finite
certificate of less repeated work. It does not independently re-establish
Ali Romman's rank theorem. The local timing observation is empirical and
does not follow from the XOR count alone.

## Implementation bounds and deviations

New functions are below sixty physical lines. New loops have explicit fixed
domain limits: four columns, sixteen entries per table, 69,905 tables,
1,082,401 exhaustive actions, twelve named controls, and at most twelve
benchmark pairs. Child commands have thirty-second timeouts; registered
checks have 120-second timeouts. Explicit exceptions remain active under
optimized Python. New code uses no recursion or network service.

Power of Ten rule 1: the unchanged authenticated source retains its recursive
symplectic enumerator. Its fixed n<=2 caller permits at most five active
`extend` frames, with column lists of length at most four. Changing that
enumerator would expand this frozen-source adapter task. The complete replay
exercises its finite bound; a future source change requires a new pin and
separate inspection. A byte-exact interpreter-stack budget is unclaimed.

Rule 3: Python allocates managed integers, tuples, dictionaries and lists.
The capacities above bound the new table storage; the exhaustive check does
not claim constant-space execution. Existing rational arithmetic and source
collections remain bounded by their fixed complete fixture. A native port
would need its own static-capacity arithmetic and allocation ledger.

Rules 8 and 9: executing a hash-pinned source module and replacing its one
action binding are the explicit adapter boundary. Source size is capped at
65,536 bytes. The only production call targets are the retained action or
the new action closure. Test tracing and the one fixed source-corruption
mock are bounded instrumentation. No unauthenticated code is executed.
Any broader plugin or dynamic-input interface needs a separate contract.

Rule 10: warning-strict normal and optimized executions and in-memory syntax
checks are available. No separate Python static analyzer is installed on the
local PATH; stronger static-analysis coverage is unclaimed. No shared build
configuration or diagnostics are weakened for this isolated package.

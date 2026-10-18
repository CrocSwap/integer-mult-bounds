# Implementation bounds and limits

Build the Lever led to the retained dual-code census rather than a hand-reported
maximum. Prove It Works led to complete finite coverage, source-corruption
controls and the Git-free read-only CLI check. Power of Ten led to an explicit
bottom-up merge sort with at most twenty passes, rather than recursive sorting.

## Native inspection

The owned call graph has no recursion or indirect function targets. Initialization
constructs at most 788,035 masks, a same-sized sorting buffer, a bounded union-find
array, twelve 14-by-256 permutation tables and 159 representative indices.
The scan owns fixed arrays for 120 directions, 511 character masks and a second
511-mask sorting buffer. It does not grow those arrays during the census.
Each rank calculation uses nine binary pivots.

Every loop is bounded by those capacities or the fixed dimensions. Character
triples have at most `C(511,3)` iterations, after explicit support filtering.
The outer scan has at most `159*776805` pairs per budget. Cardinality filters
can reduce its work but cannot remove an admissible pair. Subprocess timeouts
are 60 seconds for compilation/oracle controls and 180 seconds per census.
Registered replay is capped at 300 seconds and behavioral checks at 180 seconds.

The replay checks labels, permutations, RREF count, orbit closure/count, six-flat
capacity, oracle agreement and complete output rows with executable error paths.
No mathematical gate depends on an assertion that Python optimization removes.
Returned process failures propagate. Streams, temporary directories and copied
read-only exports have explicit cleanup paths. The native compiler and Python
syntax checks use warnings as errors; the dedicated workflow repeats compilation.
New Python functions stay within 60 physical lines. Frozen vendor code is not
executed, reformatted or held out as newly compliant code.

## Managed-runtime deviation

Rule: 3, fix memory capacity before steady operation.

Location: `geometry.py`, `verify.py`, `test_verify.py`, and standard C++ stream
internals. Python and the platform stream library allocate runtime objects;
the package does not claim an allocation-free implementation of those libraries.

Reason: replacing the offline proof harness and platform I/O with a custom
allocator/runtime would expand the mathematical contribution beyond its safe
scope. The mathematical census uses fixed native capacities.

Scope: this bounded offline verification tool only. It is not a physical
fixed-memory multiplication implementation.

Compensating control: exactly two live inputs of at most two million bytes,
eight predecessor excerpts of at most 40,000 bytes, fixed dimensions and finite
native capacities. The Git-free export test bounds its controlled inventory at
64 paths. The standard filesystem copy is limited to this fixed package tree;
its maximum directory depth is five in the exported fixture.

Verification: the source-capacity control rejects 2,000,001 bytes before native
execution. The final p8 native run used 33,767,424 bytes maximum RSS on the
recorded macOS host and reproduced the committed output hash. This observation
is not a portable hard limit or an audit of library allocation internals.

Follow-up: if an input, directory tree, dimension or platform contract expands,
reassess these bounds and update capacity controls before accepting its result.
A physical caller needs its own allocation and movement proof.

Rule: 1, use structured control flow without recursion.

Location: the test harness's standard-library filesystem copy/removal helpers.

Reason: replacing these platform helpers with a second filesystem implementation
would enlarge the validation code. Their internal recursion is not part of the
native census and was not independently audited.

Scope and compensating control: only the fixed session-owned export tree, at
most 64 paths and depth five; explicit permissions restoration permits cleanup.
No source or canonical input is removed.

Verification: the complete Git-free read-only export and receipt-corruption
controls pass under normal and optimized execution.

Follow-up: replace these helpers with an explicitly bounded traversal if export
structure becomes variable or is exposed as a general tool interface.

# Scope and verification decisions

Build the Lever led to the integer-address grammar oracle in
`specification.py`. It imports neither retained trace emitter nor encoded
arithmetic. Prove It Works required executing both emitters, the encoded
Layout and literal Machine protocol, rather than comparing source text.
Test Behavior, Not Implementation led to literal odd-reset/cutoff assertions,
nonidentity protected results and rejecting controls. An internal review caught
that a counts-only capsule assertion omitted its source and directory bytes;
the final check reads both tapes and rejects loss of either one.

Only this package is changed. The existing caller, frozen inputs, selected
record and global replay tools remain unchanged. `PROOF.md` states every
completed-operation premise. This package does not certify the mathematical
correctness, bounds or implementation style of its predecessors.

## Power of Ten inspections

1. New control flow is iterative. Generators are closed in `finally`, encoded
   words/counts are released, and successful protocol fixtures close both
   machine and borrowed setup. The PC corruption is injected after the parent
   has returned, so its rejection can close that parent normally. Capsule
   corruption is restored before the child returns. No new recursive function
   or production state is introduced.
2. The checker admits no numerical CLI search domain. It runs 100 fixed grammar
   cases. Each plan has at most eight commands, dimensions at most 64 and
   columns at most 129. A source cursor is limited to three blocks per command.
   A leaf has at most 63 coordinates and eight primitives per coordinate.
   There are 90 nonempty small geometry cases and eight normal protocol calls
   plus one wrong-PC call. The selected catalogue has 28,278 request records.
   Its 128-field fallback compiler has at most 32,894 commands, checked before
   selecting a fixture. Source pins fix these finite inputs. The registered
   verifier timeout is 600 seconds and tests have 300 seconds.
3. Python and the retained source require runtime allocation. The finite domains
   above bound new event lists. Each process handles one case at a time.
   Protocol numeric banks have fixed capacities 65,536 and 512; original
   source routines enforce slot exhaustion. The q=3, n=257 fixture bounds all
   extent exponents by 514. These are finite checker bounds, not an all-size
   physical memory theorem. Retained sources are read-only and are not vendored. Temporary source exports
   are session-owned and removed after their checks.
4. Every new function is at most 60 physical lines in normal Ruff formatting.
   Good-plan oracle expansion, fallback expansion, descriptor inspection and
   resource cleanup have separate responsibilities.
5. Explicit `need` checks remain enabled under `-O`. They enforce trace identity,
   live-word restoration, complete spectator volume, capsule bytes, generated
   widths/flags, source hashes and the successor PC. External source files
   are checked before importing their loader.
6. Mutable state is local to a fixture or the unchanged source machine. Four
   test patches target one known emitter and restore it on every exit. Each
   registered command has a separate process. There are no concurrent writers
   or shared generated artifacts.
7. Returned counts, words, descriptors, child extents and output tapes are
   observed and released. Source exceptions propagate. Normal failure of a
   primitive halfway through CALL is outside the theorem and this checker;
   it is not relabelled successful cleanup. Output and directory corruption
   controls restore their local fixture in `finally`.
8. No generated code or dynamic evaluation is added. The existing authenticated
   Python loader remains the module boundary. Test patches are limited to the
   four listed mutations and one controlled source-byte read.
9. Python module dispatch, generators, context managers and test patches are
   required for exercising the literal retained implementation. Their targets
   are explicit and finite. New event data is immutable tuples; no forwarding
   framework or ambient production state is added.
10. Validation uses Python 3.12 with `-W error`, ordinary and optimized behavioral
    tests, the registered replay, source/metadata checks and Ruff 0.17.1 with the
    repository's applicable diagnostics. Publication bytes are checked against
    the actual commit. Hosted CI and formal verification are separate.

## Runtime deviations

Rules 3 and 9 cannot be satisfied literally by this Python checker. Its runtime
allocates managed objects and uses Python dispatch/generator protocols. The
scope is the finite read-only checks above. Input domains, fixed numerical
bank capacities, sequential case execution, explicit cleanup and registered
timeouts are the compensating controls. The normal/optimized replay and state
corruption controls exercise them. A future production implementation must
supply its own allocation and dispatch argument; it must not inherit this
checker deviation as an all-size machine guarantee.

The existing source loader dynamically imports authenticated fixed modules.
This is a rule-8 dependency deviation, confined to the source loader and
132 pinned live files. No new dynamic code construction is added. The source
corruption test rejects changed bytes before loader execution. Replacing this
loader with a static import boundary would require a separate upstream change.

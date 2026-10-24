# Validation and remaining scope

Current fresh-build status and receipts are recorded in
[`../lean-external-review/VALIDATION.md`](../lean-external-review/VALIDATION.md).
The current permanent inventory contains 931 declarations, including
`SourceInvocation.actualContract`. The 930-declaration historical receipts
below do not certify the expanded inventory. The Lean 4.21 port changed proof
bodies and data partitioning while preserving the original theorem statements.
Its current fresh receipt supersedes these historical build claims.

## Historical Lean 4.33 build evidence

The earlier external-review validation reran Task A and source extraction
fresh; Task B explicitly reused all
52 receipt-anchored modules and reran the 930-declaration axiom inventory.
That historical resumed receipt reports zero fresh Task B modules. The original receipt did
not record byte hashes of the installed Lean distribution, Mathlib or its eight
manifest dependencies, so the resumed PASS cannot establish the external-library
bytes used in the original compilation. The linked delivery validation names
those dependencies and explains how fresh reproduction recompiles all 52 modules
and records the dependency hashes for a new run.

**PASS:** the coherent package replay completed at
2026-10-11 23:59:17 UTC. `replay-result.json` records 52 source-built modules
with `lean -t 0` and 930 audited named theorem closures. Every source hash
matched that historical module inventory. Only `propext`, `Quot.sound`, and
`Classical.choice` occur. `source-binding-result.json` separately records the
successful source-extraction replay.

The build began in an empty directory. After the frame certificate passed,
the runner rejected an outdated geometry source hash from its initial
manifest. Resuming with the frozen final manifest reused only hash-verified
successful builds from that same directory; all remaining sources were
compiled there and the complete axiom audit ran afterward. No development
model or external component-build artifact was imported into this replay.

Recorded module wall times total 2,756.5 seconds (about 46 minutes), including
2,070.0 seconds for `FrameData`. These are reproduction observations under
shared machine load, not an isolated performance benchmark. Mathlib preparation
is separate from these local-module timings.

## Separate results

Task A is local commit `13611a8958fc71046a83d8431d2bd6335e6a3e2f`. Its own
fresh replay checked the multi-host theorem, exact single-host recovery,
physical adapter, and boundary controls. Its endpoint contracts are premises.

Task B constructs one such contract from the actual selected PR442
invocation. The final entry module is `SourceInvocation.lean`. It accepts a
field with `2 ≠ 0`, an invertible invocation chart, arbitrary retained state,
and arbitrary original-bank dirt. Ownership injectivity, helper-relative
geometry, input matching, and clean-work guards are proved inside the
dependency chain, rather than supplied as additional hypotheses.

## Concrete evidence

- The complete 19,002-event word has a checked symbolic endpoint for all
  987 live input streams and its one designated clean private row. Boolean
  payloads are arbitrary functions and may be correlated.
- All 944 frame matrices have integer projector and complete-basis
  certificates; all 3,357 distinct MOVE pairs have both absorption equations.
  Matrix wrappers explicitly select matrix multiplication for the finite
  tables, whose stored representation is an ordinary function type.
- Literal trace checks select those certified pairs for all 4,291 actual
  MOVEs. COPY and ERASE have their exact full/zero frame pair and chronological
  guards. Both complete matrix-run equalities refer to the same actual folds
  used by the invocation contract.
- The 747 hosted owners and original bank owners are injective in their
  actual family-and-cover-map representation. Both executions use one shared
  cover extension, with equality of retained native inputs proved after
  private-row initialization. The review caught and corrected the earlier
  use of incompatible extensions.
- All affected hosts and data streams are retained. Original-bank outputs
  are the real outputs of the old execution and are threaded as auxiliary
  state. They are not silently replaced with their initial values.

The component receipt `review-receipts/final-bridge-components.json` records
the final bridge source and artifact hashes. The independent native-input
review has its own receipt and log. Reviews disclose their authorship overlap;
they are separate agent reviews, not independent human audits.

## Reproduction boundary

`check_sources.py` verifies six source snapshots, reconstructs the original
binary records, independently compares all normalized events in order, and
regenerates the literal certificates. This extraction uses Python and SymPy;
it is not a verified JSON parser or source compiler. Lean checks the resulting
embedded mathematical statements. Exact versions are in `source-versions.json`.

The historical package replay started from manifested sources and used `lean -t 0`.
The current route uses ordinary `lake build`; see the linked validation report.
It accepts only `propext`, `Quot.sound`, and `Classical.choice` in transitive
axiom closures. No project axiom, `sorry`, `admit`, `native_decide`, or unsafe
proof mechanism is permitted. Generated checkpoint theorems comprise much of
the declaration inventory; their count is not a count of new mathematical ideas.

## Limits

The result concerns one complete forward invocation, with explicit local
embeddings. All 19,002 instructions form one event in the multi-host theorem's
event list. Pairwise disjointness between separate events is vacuous in this
application; cross-invocation disjointness is not exercised. The separately
proved owner injectivity concerns this invocation only.

The pending-coordinate ranges 15..21 and 1..28 (half-open `[15,22)` and
`[1,29)`) are hand-supplied. Lean checks their containment of the target masks
through `PhysicalSourceConnection.tag_pending_contains`; nothing in Lean
or the source-extraction check binds those ranges to the source schedule.
The remaining pending swaps are applied immediately after the invocation.
The result does not prove
the later recursive child schedule, complete cover sweep, equivalence of
arbitrary global allocations, resource charging, all-size compilation, or
an integer-multiplication bound. A continuation that observes or reuses old
auxiliary outputs needs the appropriate separate scope or restoration proof.

The two mutation controls check a corrupted next checkpoint and a dirty-private
first-COPY state; they are not full executions of corrupted programs. PR448's
split-stream gain remains unestablished. No source algorithm or claimed κ was
changed. This validation preceded publication on the public review branch.

# Verification engineering claim

- Track: verification engineering; operating-system random seed: 86.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Task: `01a1332f-ca11-7d63-abca-38d955a2a1af`.

- Start: `2026-10-13T02:56:34Z`.
- Expected finish: `2026-10-13T03:36:34Z`.
- Scope: exact state evaluation in the selected helper-interface check.
- Deliverable: an optional accelerator, exact comparisons, rejection controls, and repeated timings.

## Selection

Three candidates are source inventory hashing, exact owner-moment intervals, and exact helper-wrapper evaluation.
The value `86 mod 3 = 2` selects the third candidate for the final scope.
Source hashing offers little mathematical work to accelerate.
An owner-check profile assigns only 0.076 seconds to interval operations.
The helper-check profile assigns 3.717 seconds to state evaluation within a 4.343-second run.
These profiles include instrumentation overhead.

The selected target replaces repeated binary permutation and quadratic phase calculations with exact tables.
The same integer Gaussian state arithmetic retains every gate and its global phase.
No circuit, wrapper recipe, tableau check, or source certificate changes.

## Overlap and boundaries

GitHub has no pinned sprint issue at selection time.
The only open issue is #650, about Discussions.
The local claim therefore records this scope.

PR154 addresses parallel checks and paired-cube frames.
PR367 addresses rational frame elimination.
PR452 addresses PR358 prefixes, rational scalar admission, and transcript work.
None of their listed changes replaces this Clifford state evaluator.
The prior negative-search index concerns construction searches; this task does not reopen one.

Use the selected PR622 native artifacts for both configurations.
Compare every result field without normalization.
Test small circuits, every basis vector at small dimensions, and phase-sensitive rejection controls.
Reserve the final quarter of the sprint for verification and handoff.
Do not claim a faster multiplication algorithm or a new bound.

## Result

The optional accelerator completes the chosen scope.
Seven alternating pairs give median times of 1.289 and 0.460 seconds, a 2.80× speedup.
All 14 receipts match exactly.
Six tests pass on Python 3.13 and 3.14, including 4,050 prefix states and 204 full-replay states.
Both engines reject all four corrupted artifact types.
The source-inventory check passes; the selected sources remain unchanged.

The overlap check at 2026-10-13T03:07:51Z finds no competing Clifford performance PR.
Main remains at the recorded base commit.
The contribution remains scoped to helper verification with archived inputs.
Submission details belong to the pull request and the task's local handoff record.

# Sprint claim

- Track: verification engineering.
- Assignment seed: 88, drawn with `secrets.randbelow(100)` from operating-system randomness.
- Task: `01a13378-812e-75b3-9b4b-0dd927f1901a`.
- Start: `2026-10-13T04:15:36.018560+00:00`.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Expected finish: `2026-10-13T05:00:00Z`.

## Candidates

1. Reuse exact leading principal minors in the selected bit Gram checker.
2. Replace the selected owner checker's repeated rational exponential operations.
3. Accelerate exact state evaluation in the selected helper-interface checker.

PR672 covers candidate 2. PR662 covers candidate 3.
Choose candidate 1. Use seed 88 for the matrix controls and benchmark order.

## Scope

Optimize determinant evaluation in the pinned `gram_frames.py` checker for the selected R420 bit word.
Compute the leading principal minors in one exact Bareiss pass.
Retain the original pivoted determinant for zero-pivot cases.

Compare every requested determinant with the original implementation.
Run the complete Gram checker on identical exported frames with both engines.
Retain rank, annihilator, prime-witness, positivity, and failure checks.
Provide exact source pins, negative controls, raw timings, and an optional adapter.

The deliverable is a tooling improvement. It makes no new kappa claim.
Reserve the final quarter of the session for verification and the handoff.

## Coordination and predecessors

GitHub reports no pinned issues at the initial inspection.
The local claim follows the sprint instructions for that case.
The overlap scan covers 513 open PRs through PR693 and the review ledger.
PR239 uses dual Gram matrices for large frames.
PR367 changes rational rank and canonical basis calculations for a historical verifier.

PR452 shares producer prefixes and changes scalar admission in another historical pipeline.
PR154 changes concurrency and binary frame operations.
Those contributions use different mechanisms. None is a code dependency.

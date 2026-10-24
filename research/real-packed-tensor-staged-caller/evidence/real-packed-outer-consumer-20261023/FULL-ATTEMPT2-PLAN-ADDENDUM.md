# Proposed unchanged-fixture replacement: durability repair and900-second budget

**Not authorized to execute and not executed.** This addendum responds to the coordinator's request for a static replacement proposal after the first complete-caller attempt's deadline-triggered failure. It does not revise that failed receipt or supply the missing opposite/recovery/lifetime result.

## Frozen first attempt

The original harness `5797e4a8bc6bb69403db119f7740abc41c590484225103120087fe46e9acd671`, log, FAIL receipt `50187fdd957a3efc04ab0fedb165877bf6e84bb5dfd85e2245dcebed3564ef7d`, launch metadata, report and prior plan/freezes are retained unchanged at their original paths and copied into `full-attempt1-frozen/`, with SHA256SUMS.json. The original process exited nonzero at580.390962seconds.

The first packed Tensor completed between the360.365s and390.376s heartbeats. The second/opposite Tensor remained unfinished when the580s internal deadline fired. Thus the original600s process envelope with580s computational alarm did not complete this particular unchanged q4 fixture. Two forward CRTs and the complete packed-forward/J/product comparisons succeeded; one of two started Tensor calls completed. The expected staged diagnostic0 versus true product43113955509404415 remains an oracle prediction, not an observed recovery output.

The first error was the explicit TimeoutError. Inherited source cleanup then raised outstanding-lease and owned-marker errors, masking it at the top level. No source cleanup is silently repaired here. Arbitrary interrupted-numerical-child cleanup and the post-run lifetime assertions remain unvalidated.

## Minimal instrumentation repair

`run_full_packed_attempt2_DRAFT.py` retains the same frozen candidate,83source files, coefficient cache, digit streams, exact staged oracle, preflight controls, two-Tensor/three-Converter census, output checks and declared failure cut. `FULL-ATTEMPT2-HARNESS-DIFF.patch` is the exact diff from the frozen first harness.

The repair is observation durability:

1. Attach the actual Tensor and Converter observation lists to R immediately when created, before constructor controls and numerical execution. A later exception therefore no longer omits already completed return observations from the final receipt.
2. After each delegated child successfully returns and its full equality check passes, atomically write a checkpoint containing every completed raw return, its hash, source/candidate/harness pins and elapsed time. Flush and fsync the temporary file before replacement. The first packed-forward raw records/hash are durable **before** the parent enters the opposite call.
3. Also checkpoint the actual fused product bits after their successful comparison. This adds only host inspection/evidence traffic; no scientific operation or oracle is changed.
4. Keep existing observer cleanup: if capture, comparison or checkpointing raises while the observer holds a successful child return, clear/retire that return before propagating the error.

New evidence filenames are `FULL-PACKED-ATTEMPT2-RESULT.json`, `FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json` and its temporary file. The proposed script refuses to overwrite an existing attempt2 result or completed checkpoint. Original attempt1 paths are untouched.

The deadline handler records its firing in R before raising, so any subsequently masked cleanup failure still carries an explicit deadline flag. It does not change inherited cleanup or turn such a failure into a successful endpoint. Source/candidate/harness integrity mismatch still forces nonzero failure.

Checkpoint writes/fsync and observers are experiment evidence overhead, not free operations credited to the proposed algorithm or a controlled speed benchmark. A checkpoint is explicitly a record of completed matched stages, never a whole-caller success token.

## Same scientific fixture and checks

Retain source(5,7), target(8,8), p48/P80, b8,q4, inputs `(255,0,3,17)` and `(1,254,0,9)`, rows1, require_recovery=False. Keep all35 records. No Hermitian-orbit pairing, gamma-parity shortcut, coefficient regeneration, child allocator change, precision change, alternate payload or replacement numerical backend is introduced.

The hypothetical replacement repeats the previously authorized actual caller once because the first did not complete; it does not repeat the unchanged original source full replay or passed source leaves. The cached public100402-byte catalogue remains the same produced asset. The source/candidate behavior and all endpoint assertions are unchanged.

## Proposed single process and limits

Subject to independent static review of the exact diff and a **new explicit root GO**, propose one900-second external process cap with an880-second internal alarm. The same30-second heartbeat remains. An approximate700–850second planning envelope is a budget proposal, not a termination guarantee: the first numerical Tensor alone took roughly360–390s, and the opposite had not completed after more than190s when interrupted. The original300–500second planning estimate proved inadequate for this local packed q4 run.

Proposed command, not run:

    timeout -k 10s 900s python3 -I -B -W error run_full_packed_attempt2_DRAFT.py > FULL-PACKED-ATTEMPT2.log 2>&1

The internal alarm is880seconds. There is no automatic retry, fixture change, adaptive parameter search or later budget increase. On any failure/timeout retain the first-attempt evidence, new checkpoints, trace and nonzero outcome. If no replacement is authorized, the present result remains the first attempt's partial forward/J/product match and deadline-triggered FAIL.

No numerical process has started for this proposal. The unchanged candidate remains SHA256 `5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483`; no completed two-call caller, production accuracy, total finite saving or κ improvement is claimed.

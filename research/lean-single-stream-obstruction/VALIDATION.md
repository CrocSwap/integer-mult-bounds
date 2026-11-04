# Local validation

All checks below concern main pinned at
`12a4934d15006e8c10f9b2264f13f8f341be802b` plus this new directory.
No inherited source file, selected certificate, upstream source or scientific
checker was changed. This records the initial local validation on 2026-10-11;
no CI result or publication occurred as part of that validation.

## Lean contribution: PASS

Official Linux Lean 4.33.0, compiler commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`.
The downloaded release archive's SHA-256 matched GitHub's published asset digest:
`4b3fb03c29a1e0a253fb1d11f9bae3725f19a0dc6fc09b3ea16d2c9df3349e2c`.
Toolchain installation is a local setup step; replay itself is offline.

The command below uses portable example paths for the compiler and receipt:

```sh
python3 research/lean-single-stream-obstruction/replay.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/final-lean-replay.json
```

Recorded result:

```text
{"status": "PASS", "compiled_modules": 1, "axiom_reports": 15, "negative_controls_rejected": 5}
```

Two fresh packaged replay receipts matched byte-for-byte. The runner checks
all theorem dependencies, trust level zero, source hash, and Lean rejection
of five explicit false statements. The record is `replay-result.json`.
The runner also passed Python syntax compilation.

## Predecessor replay: PASS

PR397 at `cb6455fa1e9af68be47c33948d3d1a6f0717a5e4` was replayed in its
detached worktree with the same installed compiler:

```
{"status": "PASS", "compiled_targets": 3, "transitive_axiom_reports": 22, "lean_negative_controls_rejected": 5}
```

Its original full receipt, `pr397-replay.json`, was retained locally and is
not included in this package; the result above records that historical run.
This is independent execution evidence for that scalar packet, not a rebuild
of Sussman's full Mathlib development or a certification of a physical supplier.

## Inherited broad-suite blocker

`make joint-dual-verify` exits 2 with `AssertionError: Makefile` in
`scripts/experiments/joint_dual_compose.py:70`. The identical failure was
reproduced on a clean detached worktree of the pinned main commit, with no
new contribution files. The original `joint-dual-verify.log` and
`baseline-joint-dual-verify.log` were retained locally and are not included
in this package. The result is summarized in [repository-checks.json](repository-checks.json).

`make verify` was started and completed historical copied-fixed pair checks,
including all 4,073,300 data pairs. It was subsequently **stopped**, before
completion, after the required joint-dual subtarget's baseline failure was
confirmed directly. Its full result is not claimed as a pass or as a completed
failing run. Its original partial log, `make-verify.log`, is not included;
the stopped status is recorded in `repository-checks.json`.
No inherited source-hash check was weakened or repinned.

## Required selected gen4 replay: PASS

`make gen4-bank-verify` exited 0. All nine mandatory stages passed:
virtual, raw, bit, scalar, primes, banks, complex, math and finite.
All 112 pinned inputs remained unchanged. The existing selected conditional
certificate was reproduced; no exponent claim was changed by this contribution.
Runtime was approximately 400 seconds. The original full log,
`gen4-bank-verify.log`, is not included; its hash and result are recorded in
`repository-checks.json`.

## Original stream-model audit replay: PASS

The separately fetched, pinned RaD `job1_stream_model.py` was executed with
NumPy 2.3.5. It reproduced 18 split cases and 152 single-register programs,
with zero equal to the intended original operator. Whole-hosting and
two-register controls passed. This is a finite Python replay, not a universal
Lean whole-program theorem and not a κ computation. The original
`stream-model-results.json` receipt is not included; its result summary is in
[AUDIT.json](AUDIT.json).

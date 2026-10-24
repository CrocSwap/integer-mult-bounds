# Validation of the Lean 4.21 port

Exact upstream base: `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`.
Original port build candidate: `0d4aec339032498a182cf0eec7cb571b2cdd48f6`. Its proof sources and dependency pins remain unchanged by the CI repair.

## CI compatibility repair

The original verifier incorrectly required an OS stack soft limit of at most
8 MiB. GitHub job 114937263040 rejected the runner before compiling Lean,
after the source and parser checks passed. The repair records inherited
limits before and after verification and requires them to stay unchanged;
it never changes resource limits. It still rejects external Lean tuning.
A recorded limit alone cannot authenticate the caller's prior environment.
The workflow and reproduction commands apply no resource overrides.

The current fresh receipt is [validation/lean421-ci-fix-fresh.json](validation/lean421-ci-fix-fresh.json).
The clean build candidate is `b86b4072edc15c717e762ebb5768905c78f4cf3f`.
All 153 local modules compiled fresh and all five audits passed with standard
axioms only. The normal Make target passed in **1018.396 seconds (16m58s)**.
The same conservative model gives **2049.113 seconds (34m09s)**, within the
35-minute target under its explicit setup/cache assumptions. This estimate
is not an observed GitHub run. See [repair timing](validation/lean421-ci-fix-timing.json),
[projection](validation/lean421-ci-fix-projection.json) and
[normalized log](validation/lean421-ci-fix-make.log).
The workflow uploads its own receipt as `pr442-lean421-receipt`; inspect that
run independently of this local result.

No local contribution artifacts were reused. External source/artifact and
toolchain fingerprints matched the original receipt before reuse and were
checked again by the fresh verifier. The inherited local limits were
`[8388608, -1]` (8 MiB soft, unlimited hard), unchanged after verification.
No resource settings, compilation flags, Lean files or theorem statements
were changed.
The original `validation/lean421-fresh.json`, timing and projection files below
remain unchanged historical evidence for the original port manifest; they do
not validate the revised Python verifier. The new receipt above does.

The unrelated research CI failure came from an upstream stale fingerprint in
`certificates/mixed-point-audit.json`. Regenerating it with
`python3 scripts/audit_mixed_point.py` updates only the hash of
`scripts/rational_span_frames.py`; the mathematical certificate is unchanged.

## Original port fresh verification: PASS

Fresh verification passed on Lean 4.21.0 with the exact upstream Mathlib pin.
All 153 local modules compiled from an empty build directory, with no local
artifact reuse. The five axiom inventories passed: Task B 931, Task A 21,
hosting 47, earlier source invocation 422 and single-stream 15 declarations.
Only `propext`, `Classical.choice` and `Quot.sound` occur.

The normal Make target took 1043.269 seconds (17.39 minutes), including
source checks, parser mutation checks, fingerprints, all builds and audits,
package verification and the clean-tree check. Lake build time was 960.718
seconds. The slower four-core CI estimate is **34.90 minutes**:
`1.2 × (1.5 × 1043.269 + 180)` seconds. The three-minute setup allowance is
an explicit unmeasured assumption covering checkout, installation and a
successful pinned Mathlib cache download. The 20% margin applies to both
compute and setup. The result is 34 minutes 53.884 seconds: it qualifies
under the revised 35-minute gate, by about six seconds. At the assumed
slowdown, setup above 185.097 seconds would exceed that gate. Upstream's
hard limit remains 45 minutes. No additional checkpoint split is required
by the revised gate.

The official cache endpoint is blocked here. Only exact, fingerprinted
external dependencies built previously from source were reused; no local
contribution artifact was reused. Adding the earlier 522.650-second external
source-build fallback gives an estimated **50.58 minutes**
under the same model. Cache-free CI is not qualified by the cached-setup estimate.

The original receipt is [validation/lean421-fresh.json](validation/lean421-fresh.json).
[The source binding receipt](validation/lean421-source-binding.json) records
the separate regeneration check of all 19,002 ordered source events.
[validation/lean421-timing.json](validation/lean421-timing.json) records module
observations and full Make timing; [the CI projection](validation/lean421-ci-projection.json)
records the assumptions and setup sensitivity. Logs normalize local paths,
retaining the original and normalized hashes. No external stack, compiler
flags or environment tuning was used. Source heartbeat/recursion options are
retained. The installed compiler, bundled libraries, all nine dependency
sources/artifacts and local artifacts were fingerprinted before/after as
specified in the receipt. This is a fresh local build, not a resumed build.
The local Make run used Python 3.12; the workflow selects Python 3.13.
The complete GitHub setup/job has not been executed here; its Make commands
were run from the clean checkout with the pinned compiler selected explicitly.

The 66 original contribution files are covered by 64 compiled modules and two
audit scripts; same-content partitioning adds 89 modules. All nine archived
third-party snapshots remain byte-identical and are excluded from compilation,
CI and audits. The static comparison finds 1,388 original named theorem
headers/contexts unchanged; it is not a substitute for Lean type checking.
The differential test is delegated separately and is not a reported check.

## Historical Lean 4.33 evidence

`validation/task-a.json`, `validation/task-b.json`, their logs and
`validation/run-metadata.json` are retained at their original paths for
historical comparison. **They are not receipts for the current port.**
The 4.33 run completed Task B at 2026-10-12 03:19:37 UTC, compiling six Task A
modules and 52 Task B modules fresh and auditing 21 and 931 declarations.
It used Lean `d8b18978322de05a8f3dba51ef03cf5461676c17` and Mathlib
`db584cd6d46c92f209a44c0f1c829460d327499d`.

That recorded fresh run fingerprinted the installed Lean distribution,
Mathlib, its eight dependencies and their artifacts before and after
compilation. Earlier historical Task B builds had not fingerprinted installed
Mathlib/dependency libraries. The later 4.33 fresh run records its own
libraries; it neither authenticates the earlier bytes nor establishes the
4.21 port. No historical receipt is reanchored as current verification.

## Integrity and limitations

The strict package verifier checks current file hashes, the canonical port
manifest and a matching fresh receipt. It fails when the current receipt is
absent. Preparation mode `--allow-pending-port` can report `PENDING_PORT` only for an unfinished package.
These checks inspect recorded evidence; they do not run Lean or authenticate
the origin of the receipt. [BUILD.md](BUILD.md) describes fresh reproduction.

Only standard Lean axioms are permitted. A count of named axiom reports is
not a count of new mathematical ideas. A project build against fingerprinted
public dependencies does not claim a fresh Mathlib rebuild or a
`leanchecker --fresh` audit of every imported constant.

Source fidelity, comparison boundaries and integration still require
maintainer review. Hand-supplied pending ranges remain unbound to the source
schedule; cross-invocation disjointness is not exercised. Full cover sweeps,
later scheduling, global allocation equivalence, costs, all-size compilation,
analytic transfer and κ remain outside the mathematical scope.

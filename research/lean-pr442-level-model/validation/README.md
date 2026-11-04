# Phase 1 validation

AI-written report. This records a machine check, not an independent human audit.

## Local recorded run

`local-phase1.json` reports **PASS** for source commit
`60a63999d56b9b4048b9b2887b3f7ef188ef9c35` and manifest
`85ce87c3b0805f014d5de21466a019fd1eeef74946e4050926ec5dba35d6134a`.
The receipt SHA-256 is
`8afc32d4450b0b341c64a94c3f4725bd99b1d261878a73629d48a10005f82b87`.

- Lean: 4.21.0, release commit `6741444a63ee`.
- Mathlib: `308445d7985027f538e281e18df29ca16ede2ba3`.
- Fresh package build: **153.175 seconds**.
- Complete verifier, audit and controls: **166.107 seconds**.
- Axiom audit: all **84 named declarations**, including **38 theorems**;
  only `propext`, `Quot.sound` and `Classical.choice` occur.
- Five positive controls compiled. Five corresponding mutations were rejected
  by Lean's decision procedure as false: entrance frame ID, root coordinate,
  stage-2 axis, reflected-call orientation, and recorded source level.
- Input hashes, reproducible extraction, and all 519 recorded predecessor
  file hashes passed.

The package's `.lake/build` directory was empty when this run started. Its four
new modules and the separately rooted, unchanged `PendingScheduleData` were
compiled afresh. Existing predecessor and Mathlib artifacts were reused;
**this is not a fresh build of every dependency**. Those artifacts are covered
by the receipt's source/dependency revisions and runtime artifact fingerprints.
The predecessor modules needed here had been built during this session's
initial probe, but that probe is not being presented as a complete recorded run.

The operating-system stack limits stayed `(8388608, -1)`, with no stack changes
or external Lean tuning. Only ordinary `lake build` / `lake env lean` commands
were used; the local absolute Lake executable selection is recorded portably
as `lake`. Source-level heartbeat and recursion options are in the tracked
Lean files.

The earlier exploratory run was resumed and passed. It is superseded for local
Phase 1 evidence by this fresh-package run. Existing PR540 package integrity
and its source-extraction check also passed; no existing proof receipt or file
was changed.

## Independent CI evidence

The dedicated [fork Actions workflow](https://github.com/cheesegrader/integer-mult-bounds/actions/workflows/pr442-level-model.yml)
checks out the pushed commit and builds the package and required predecessor
modules from a clean checkout, using the pinned Mathlib cache for library
artifacts. It publishes its own exact-commit receipt as the
`pr442-level-model-phase1` artifact. Consult the run's conclusion and receipt;
this local report does not substitute for a successful CI run.

Receipts and this report are kept outside `MANIFEST.json`'s source inventory to
avoid a self-hash cycle. The receipt embeds the exact source inventory and
manifest hash. Adding this report and receipt changes no built source.

## Remaining work

Phase 1 proves finite source joins and the rational entrance-line theorem.
The ambient endpoint interpretation, local-entry/prior-endpoint agreement,
transport to fields with two nonzero, and `idle_pending_operator` are not proved.
A planning estimate for Phase 2 is 3–5 modules and 450–900 handwritten Lean lines,
plus supporting extraction/audit documentation, with 2–4 focused days of work.
Confidence is moderate: route/reflection alignment dominates the uncertainty.
Additional build time is estimated at 1–8 minutes with dependencies available;
that estimate is unmeasured and is not a CI qualification.

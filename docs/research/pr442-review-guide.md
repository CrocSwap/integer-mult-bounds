# Reviewing the PR442 level-model contributions

AI-assisted integration repair; this guide is not an independent mathematical review.

## Phase 1: PR #1365

The phase-specific comparison is `448690c3b7e5c2b5975b760075b162fe0a8cfb03..d418130e3bbee1cb6923f0f734d5788e09933f57`.
It adds only `research/lean-pr442-level-model/` and
`.github/workflows/pr442-level-model.yml`. Start with `BaseLevel.lean`:
`source_entrance_projector` identifies the literal entrance projector with
`qqᵀ/4`; `source_entrance_range` identifies its rational range with `span(q)`.
`LevelFrameJoins.lean` and `LevelSchedule.lean` supply the source joins and
two-child endpoint provenance. `THEOREMS.md` lists the statements and
`Audit.lean` enumerates all 84 audited declarations.

The other proof packages in the PR are inherited dependencies, not additional
Phase 1 claims. In particular, `lean-multi-host-source` is the PR540 invocation
proof, and `lean-pending-derivation` is the PR1231 schedule derivation. Phase 1's
`BASE-FILES.json` pins all 519 predecessor files. Removing those packages would
break the reproducible, locally linked Lake dependency chain. They remain
byte-for-byte unchanged by this repair.

## Phase 2: PR #1494

The phase-specific comparison is `d418130e3bbee1cb6923f0f734d5788e09933f57..80ce84e3f05f5032e16ab22576c275f2e7e485ed`.
It adds only `research/lean-pr442-level-model-phase2/` and
`.github/workflows/pr442-level-model-phase2.yml`. Start with `IdleOperators.lean`
and `idle_pending_operator`; then follow `EntranceContinuity.lean`,
`RouteTransport.lean` and `FieldEntrance.lean` for the endpoint, route and field
transport prerequisites. The package's `THEOREMS.md` lists 92 theorems and its
`Audit.lean` probes 116 declarations. `SOURCE-REVIEW.md` describes the independent
rational corroboration and its limitations.

Phase 2 incorporates the repaired Phase 1 history. Its 542 protected files,
including frozen Phase 1 sources and receipts, remain unchanged. The full diff
against upstream includes those dependencies; use the pinned comparison above
to review just the Phase 2 contribution. `pendingAxes` occurs on the comparison
side, rather than supplying physical endpoint definitions. The claim is scoped
to children 1 and 2 of the selected invocation, both sides and all 120 ports,
over fields with two nonzero.

The local source-only check passed the manifest, exact theorem statement
inventory, dependency pins and all 542 protected hashes. Its Windows harness
omitted the unused POSIX resource import and normalized path separators in the
in-memory validator; it did not modify the package or execute Lean.

## Reconciliation with upstream

The repair merges canonical upstream `6f100d4bb5083f8c35d96fd95a539811c62f245c`
without rewriting the submitted history. It preserves upstream's entire
`certificates/mixed-point-audit.json`: the old branch's source fingerprint
predates subsequent upstream source edits. The Makefile retains both upstream's
current verification targets and the inherited `formal-pr442-verify` target.
The general research workflow retains upstream's manual trigger and historical
replay routing; this PR does not re-enable automatic historical sweeps.

The dedicated Phase 1 workflow builds the pinned package, audits axioms, and
runs five semantic mutation controls on the pushed branch. A separate scoped
integration workflow runs the inherited invocation source checks, full module
build and five axiom audits. Each run publishes its exact-commit receipt.
Historical receipts remain frozen and do not establish a pass for a new head.

At the time of this repair, GitHub reports that Actions is disabled on the fork
because of its usage volume. No new CI run should be inferred from a branch
update. Re-enable Actions and run the scoped workflows to obtain new Linux
receipts; the inherited integration workflow runs automatically only on the
Phase 1 branch, and can be dispatched on Phase 2 when needed.

## Reproduce and interpret the evidence

Follow `research/lean-pr442-level-model/README.md` for its pinned Lean 4.21.0 /
Mathlib setup and `python3 verify.py --receipt /tmp/pr442-level-model-phase1.json`.
For the inherited invocation package, install
`research/lean-external-review/requirements.txt`, fetch its documented Mathlib
cache, and run `make formal-pr442-verify` from the repository root.

The integration repair's Windows source-only check verified package manifests,
all predecessor hashes, the declaration inventory, pinned dependencies and exact
regeneration of `LevelSourceData.lean`. This did not execute Lean: Windows lacks
the verifier's POSIX `resource` module. Fresh proof-build evidence must come
from the dedicated Linux CI receipts. No compiler options, proof sources,
protected manifests or historical receipts were changed.

## Open next questions

Review the two rational entrance theorems and literal source joins first, then
inspect the fresh CI receipts and inherited proof boundary. The parser and
hashing remain external trust boundaries. Phase 1 does not establish complete
physical execution, cross-invocation scheduling, or a multiplication bound.
The Phase 2 pending-operator work is tracked separately in PR #1494.

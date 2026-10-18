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

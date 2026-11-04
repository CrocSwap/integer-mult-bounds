# PR442 integration repair: local validation

AI-assisted verification; not an independent mathematical review.

The repair merges canonical upstream `6f100d4bb5083f8c35d96fd95a539811c62f245c`, preserves its current mixed-point certificate fingerprints, retains both Makefile target groups, and carries the repaired Phase 1 history into Phase 2. No frozen proof source, manifest, predecessor file or historical receipt was changed.

## Evidence

Local checks used the official Windows Lean 4.21.0 release (commit `6741444a63ee`), Mathlib `308445d7985027f538e281e18df29ca16ede2ba3`, and all nine manifest-pinned library revisions. The tested combined head is `ec4172920b8abf3ba74a91bef5d3d2bb9c08d5cd`; its Phase 1 proof package has exactly the same manifest and protected source bytes as repaired PR #1365.

| Check | Result |
| --- | --- |
| Phase 2 default Lake build, including required predecessors | PASS |
| Complete Phase 1 default target (`lake build @PR442LevelModel`) | PASS |
| Phase 1 axiom audit | PASS: all 84 declarations |
| Phase 2 axiom audit | PASS: all 116 declarations |
| Phase 1 semantic controls | PASS: 5 positive witnesses and 5 false mutations |
| Phase 2 semantic controls | PASS: 8 positive witnesses and 8 false mutations |
| Protected source/receipt hashes | PASS: 519 Phase 1 and 542 Phase 2 entries |
| Current mixed-point certificate fingerprints | PASS: all 3 sources |
| Inherited invocation source extraction | PASS: 19,002 events, 987 roles, 6 immutable input hashes |
| Independent rational Phase 2 replay | PASS: 2,640 checks plus 6 negative controls |

All audited axiom sets are subsets of `propext`, `Quot.sound`, and `Classical.choice`. Mutation failures were accepted only for the expected semantic rejection; Phase 2 separately typechecks each proposition. The original 120-second per-command timeouts were retained.

The [machine-readable record](pr442-integration-validation.json) includes executable and source-manifest hashes, declaration-by-declaration axiom sets, control results, artifacts and dependency revisions. See the [review guide](pr442-review-guide.md) for phase-specific comparisons.

## Scope and reproduction

These are local Windows kernel-build, audit and control results, **not a Linux POSIX verifier receipt or a new GitHub Actions pass**. The phase proofs and required predecessor modules were built from source; the documented pinned Mathlib cache supplied library artifacts. The complete inherited five-library default build and its five audits were not rerun.

Both original control suites ran in the combined Phase 2 Lake workspace, which links the unchanged Phase 1 package. Source-only validation used an in-memory Windows adaptation for POSIX imports and path separators. Generated inherited Lean modules were compared as text modulo Windows newline encoding; immutable source/input hashes remained byte exact. The repository verifiers and protected files were not edited. No Lean tuning flags, environment overrides or resource-limit changes were introduced.

For the canonical Linux checks, follow each phase package's README and its unchanged dedicated workflow. The new `pr442-integration.yml` workflow supplies the separate full inherited-invocation build and audits. GitHub reported Actions disabled on the fork during this repair; consult actual run results before treating any new head as CI-qualified.

This integration repair changes no mathematical scope, selected bound, all-size claim or physical-execution guarantee. Historical receipts remain evidence for their original sources.

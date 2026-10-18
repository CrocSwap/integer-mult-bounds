# Primary-proof provenance binding

**Research consolidation / tooling repair. No new kappa.**

## Reproduced discrepancy

At base `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`,
`scripts/verify_selected_result.py` checks certificate bytes, exact kappa,
complete source inventories and every proof supplement. Its final loop only
requires the `proof`, `review` and `validation` paths to exist. Consequently,
changing only the primary `proof` pointer to an existing unverified file with
contents `NO PROOF` still passes. Neither a hash nor a mathematical input needs
to change. The historical checker is retained byte-for-byte under `vendor/`,
Git blob `4f0e4bded003a48b5122cbff597af4282f4d6329`.

This is a concrete acceptance gap in a metadata consistency check, **not** an
incorrect published proof, a counterfeit accepted construction, or a mathematical
counterexample. The current and eight checkpoint records inspected at the base
already have a digest covering their primary-proof reference; see
`REFERENCE-COVERAGE.json`. That file records a source inspection, not fresh
verification of their complete inventories or suppliers.

## Repair and its invariant

The checker now requires the resolved primary-proof path to belong to the set
of files whose digests it has just verified. Package-relative manifest keys are
resolved from the manifest's directory; `repository-packages-sha256-v1` keys are
resolved from the repository root. Supplement keys remain repository-relative.
This distinction preserves source527 and gen4, whose primary proofs are in the
source inventory but are not explicitly listed among the supplements.

For a stable filesystem during the call, successful inventory equality means
every collected inventory path has the recorded digest. Successful supplement
checks establish the same fact for their paths. Membership of the primary proof
in this union therefore establishes its coverage. The implementation uses the
existing resolved-path semantics, including in-root aliases to a verified file.
It does not equate distinct files merely because their bytes happen to match.

The kappa, certificate, inventory and supplement checks are not relaxed.
Review and validation retain their existing existence requirement; any digest
already imposed on them by a source inventory or supplement still applies.
In particular, a review also serving as the pinned primary proof is **not**
made mutable by this change.

This is **coverage**, not authentication of the selection record or semantic
proof checking. A coherently edited inventory and record are outside the threat
model. Redirecting to a different already-verified file is not excluded; whether
that file proves the claimed mathematics remains a review obligation. Concurrent
filesystem mutation and cryptographic hash security are not addressed here.

## Reproduce

From the repository root with Python 3.11+ and the standard library:

```sh
python3 -I -B research/selected-proof-binding/reproduce.py
```

Expected final line:

```text
PASS_SELECTED_PROOF_BINDING 11 reproduced gaps; 11 repaired rejections; 12 tests
```

The driver checks the baseline Git blob before importing it, compares the base
and repaired implementation on six positive fixtures and eleven detached-proof
mutations, runs all twelve regression tests, and compares the complete count
receipt with `EXPECTED.json`. It downloads nothing and writes no result files.
Temporary synthetic files are removed after each case. No scientific supplier
code is executed by the synthetic fixtures.

The eleven reproducible mutations are five unverified destinations in each
manifest layout (decoy, review, validation, certificate and byte-identical copy),
plus a root-level shadow of the legacy package-relative `PROOF.md` key. The base
accepts all eleven; the repair rejects all eleven at the new predicate. Further
tests preserve positive inventory/supplement-only and normalized-path cases,
mutable unpinned publication receipts, arithmetic/digest failures, inventory
closure, missing/outside files and existing resolved-alias semantics. Symlink
checks explicitly skip only on platforms that cannot create symlinks.

The API-level checks also pass under `-O`; the production command-line entry
point continues to refuse optimized execution, as required by its inherited
verification pipeline. The reproduction driver checks that refusal.

## Validation and limits

Local Linux / CPython 3.13.5:

- The command above and its `-I -O -B` variant passed with identical JSON receipts.
- All twelve regression tests passed normally and under `-O`; no symlink skips.
- A relocated minimal source snapshot in a path with spaces passed. Baseline,
  expected-receipt and repaired-predicate corruption controls failed as expected.
- Staged whitespace and clean patch-application checks passed.

A full clone was attempted but the runtime could not resolve `github.com`.
The GitHub connector supplied pinned text files; the local baseline checker
matches its exact Git blob. The isolated local Git repository is a **partial
source snapshot**, not a fabricated checkout of the upstream commit. The remote
contribution branch was created directly from the exact upstream base.

Full `make verify`, `make selected-record-check`, the existing full-selection
test module, all historical full inventories, cold supplier replays, Lean and
remote CI were **not run** in this session. The focused tests are complete in
their stated fixture domain, not substitutes for those integration checks.
No speedup, new mathematical bound, fresh review of the multiplication theorem,
or independent human peer review is claimed. No selected record, historical
record, source inventory, supplier, ledger disposition or `upstream/` file changes.

## Provenance and credit

The exact base and OS-random assignment seed **96** are recorded in `CLAIM.json`.
`REFERENCE-COVERAGE.json` pins inspected metadata and distinguishes digest
membership from source execution. The selected context is PR741 with PR589 at
`1661202643272239/1000000000000000000`; it is not a contribution of this patch.
During final verification main advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting PR799 at
`1661634653669567/1000000000000000000`. Its selected record and maintainer
review were read. The affected checker remains exactly blob
`4f0e4bded003a48b5122cbff597af4282f4d6329`; the new primary proof is also
explicitly covered by a supplement. The original experimental base is retained.
This is metadata compatibility inspection, not a fresh PR799 replay.

The selected construction/review and the experiment log were consulted before
choosing this task. No closed mathematical search is reopened.

Douglas Colkitt's original checker, its tests, review infrastructure and OpenAI
Codex disclosure are retained. Related PR704 by roife strengthens **review-ledger
metadata**; PR474 binds **fresh gen4 replay certificates**; neither is imported
or replaced here. PR746 (Will Richards) and PR828 (Mihir Srivastava) already cover
the two source-reconciliation candidates rejected during task selection. Supplier
credit remains with Chafik Boukhalfa/chafreaky, DreamingOfClouds, Jeremy Kothe,
eumemic, and the full lineage in the selected maintainer review.

Prepared for **Mihir Srivastava (`mihir-s-05`) with substantial OpenAI assistance**
in investigation, implementation, testing and writing. Apache-2.0, following the
repository license. The vendored baseline retains its original author/license
header unchanged. No private material or new external library is included.

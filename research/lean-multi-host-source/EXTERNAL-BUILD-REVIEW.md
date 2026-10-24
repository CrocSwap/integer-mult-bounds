# External build and retained-cache review

Reviewed on 2026-10-12 against committed contribution
`f7330c5f5b1c5e85f91a98c95e8efc0e27c03490`, with the runner fixes described
below. No mathematical statement or Lean proof was changed in this review.

The retained Task B build can be reused with an explicit historical-provenance
qualification. It cannot honestly be described as a new 52-module compilation.
An outside reviewer should use the fresh build documented in [BUILD.md](BUILD.md).

## Findings and implemented fixes

The previous Task B runner checked manifested source bytes, copied source bytes,
local `.olean` hashes, direct local dependency hashes, and the Lean and Mathlib
commit identifiers. Its mutable progress file was the only resume anchor. It
did not record byte hashes for the installed Lean 4.33.0 distribution (including
Lean/Std libraries), Mathlib's compiled artifacts, or those of its eight manifest
dependencies: plausible, LeanSearchClient, importGraph, proofwidgets, aesop, Qq,
batteries, and Cli. Exact dependency revisions are in `mathlib-lake-manifest.json`.
Its summary also counted reused modules as fresh. Task A always compiled fresh,
but checked only the Lean version prefix rather than the exact recorded compiler
commit.

Both runners now check the exact compiler commit and snapshot the actual installed
toolchain bytes before and after validation. Task B additionally checks clean
tracked Mathlib and dependency sources at every pinned Git revision, hashes all
their `.lake/build` artifacts and Lake configuration artifacts, and records the
ordered external library search paths. These hashes include companion object,
IR, native, and trace files; they do not rely on `.hash` sidecars. An unexpected
library search root is rejected. A resumed local build rejects unmanifested
`.olean`, `.olean.private`, `.olean.server`, `.ir`, `.ir.sig`, and `.so` files,
including nested paths, and symlinked subdirectories that could shadow library
imports.

New cache entries bind the source, local object and companion files, dependency
objects and companions, dependency source hashes, and current external snapshot.
The receipt reports fresh, reused, and legacy-reused module counts separately.
Task A remains fresh-only.

Historical entries lack an external snapshot. The default resume policy rejects
their reuse. The explicit legacy option requires the old successful receipt to
match the bytes committed at a specified Git commit. Each reused historical
module must match that receipt's source hash, object hash, ordered dependency
hashes, recorded duration, and compiler output. Extra unrecorded companion files
prevent legacy reuse. A current environment snapshot is recorded separately;
`historical_external_environment` remains `unrecorded`, including on subsequent
explicit resumes. No new snapshot retrospectively certifies the old environment.

This limits the final Task B PASS: it establishes that the 52 reused local
modules match the old successful receipt and that their 930-declaration axiom
audit passes now; it does not establish the external-library bytes used for
their original compilation. The documented fresh reproduction resolves this
for a new run by recompiling all 52 local modules and recording the installed
toolchain/library hashes before and after compilation. Use new build/receipt
directories, the pinned public dependency setup, and no resume options.
The resulting new receipt does not retrospectively repair the old one.

The snapshot observes current bytes and clean pinned source checkouts. It does
not itself prove that every external compiled object was produced from those
sources, or authenticate a downloaded compiler archive. The dependency setup
and archive verification records supply those separate reproducibility steps.

## Existing artifacts and honest reuse

The old committed successful Task B receipt completed at
`2026-10-11T23:59:17.947059+00:00`, with 52 module records, 930 audited declarations,
and 2,756.5 seconds of accumulated module compilation time. Its SHA-256 is
`462fefd26aec066a37714a115e74dac08e1cef4b8b756ea3ff1c71f63699078e`.
Those durations describe the historical compilation, not the new resume run.

| Historical artifact group | Objects | Runner progress | Use |
| --- | ---: | --- | --- |
| Complete Task B cache | 52 | 52 records | Complete historical cache; source, object, and dependency checks passed |
| Partial framed replay | 27 | None | Partial development artifacts |
| Framework review | 6 | None | Earlier framework review |
| Independent review | 6 | None | Earlier independent review |
| Frame-geometry model | 5 | None | Development model; not validation of the actual source certificate |
| Separate component builds | 1–18 each | None | Intermediate scalar, ownership, native, frame, and bridge builds |
| Earlier contribution build | 7 | None | Earlier contribution build |

Only the first directory supplies the complete old runner record. The other
directories should not be silently adopted as a coherent replay cache. The
read-only check of all 52 cached modules and their committed receipt is saved in
[retained-cache.json](review-receipts/external-build/retained-cache.json).

To preserve the historical directory, copy it to a new directory before resuming.
The recorded review used a separate copy. Exact historical locations are
preserved only in the linked evidence. After preserving the original committed
receipt as `old-task-b.json`, an illustrative local reuse command has this form;
these placeholders are not the command that produced the historical receipt:

```sh
python3 research/lean-multi-host-source/replay.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --mathlib /path/to/mathlib4 \
  --build-dir /path/to/copied-historical-cache \
  --resume --allow-legacy-resume \
  --legacy-receipt old-task-b.json \
  --legacy-commit f7330c5f5b1c5e85f91a98c95e8efc0e27c03490 \
  --receipt /tmp/task-b-resume.json
```

The old receipt can be recovered with `git show` at the exact commit above and
path `research/lean-multi-host-source/replay-result.json`. The runner verifies
that committed content itself. Reviewers without historical artifacts should
omit all resume options and choose a new build directory.

## Checks and limits

The full current external snapshot passed in 6.27 seconds. It covers the
17,505-file, 3,255,938,837-byte installed Lean distribution, Mathlib, and all eight
actual pinned dependency checkouts. The snapshot digest is
`4af0e99cf6f50d5aa306da33e7957bf99e1c81ccb35619d14cc7e78cad437559`;
the exact component hashes and revisions are in
[environment.json](review-receipts/external-build/environment.json).
The compiler is Lean commit `d8b18978322de05a8f3dba51ef03cf5461676c17`;
Mathlib is `db584cd6d46c92f209a44c0f1c829460d327499d`.

Both Python scripts passed syntax compilation. Sixteen focused reuse-policy
checks and eight artifact-inventory checks passed, including the real retained
inventory and committed ordered receipt. Their record is
[reuse-policy-checks.json](review-receipts/external-build/reuse-policy-checks.json).
The committed [check_reuse_policy.py](review-receipts/external-build/check_reuse_policy.py)
repeats 22 self-contained fixture checks: rejected unapproved legacy reuse,
altered source/object/dependency bytes, altered dependency companion/source
hashes, changed external environment, unrecorded companions, shadow libraries,
and symlinked search subtrees. Its fixture bytes are explicitly not Lean proofs.
The two additional original checks inspected the actual repository receipt and
retained build. No full Task B rebuild was launched for these policy checks.

The historical packaging receipts are
[Task A](https://github.com/cheesegrader/integer-mult-bounds/blob/377012d9e1d350c29fc47669e82415249429f60c/research/lean-external-review/validation/task-a.json) and
[Task B](https://github.com/cheesegrader/integer-mult-bounds/blob/377012d9e1d350c29fc47669e82415249429f60c/research/lean-external-review/validation/task-b.json).
That run freshly compiled Task A's six modules; Task B reused 52 modules and
reran the historical 930-declaration axiom inventory with `lean -t 0`.
These are not the new upstream-based fresh replay. Its separate 931-entry
inventory and current status are in
[external-review validation](../lean-external-review/VALIDATION.md).

This final inventory is not a `leanchecker --fresh` rechecking of every constant
in the complete imported Lean/Std/Mathlib environment. Lean's supplied checker
supports that broader operation, but it was not run here. The record therefore
states exactly which modules were compiled earlier, which artifacts were
reused, what was hashed now, and what audit was rerun now.

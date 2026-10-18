# PR236 source and receipt reconciliation

**Research consolidation; no new κ.** This restores James Chang's complete,
unchanged 14-file PR236 source package at
[`f825b6fdfd763f189db3aa1c02fdd5d604c85a01`](https://github.com/CrocSwap/integer-mult-bounds/pull/236)
and connects it to the maintainer's already published review evidence.

At base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, the
[review ledger](../../docs/research/pr-ledger.md) explicitly left PR236 source
integration outstanding. The [publication review](../../docs/research/community-pr210-review.md)
retained the full execution receipts but excluded the standalone source package.
Consequently a checkout contained the receipts but could not run PR236's
input-only check without obtaining its sources elsewhere. The restored
[`lean-paired-cube-d1d6`](../lean-paired-cube-d1d6/README.md) package resolves
that availability gap. This does not change PR236's recorded disposition,
close its PR, or replace its original authorship with an integration author.

## Reproduce

From the repository root, with Python 3.11+ on macOS or Linux:

```sh
python3 -I -B research/pr236-source-reconciliation/verify.py
```

Expected:

```text
PASS_PR236_SOURCE_RECEIPT_RECONCILIATION 3606 modules, 14320 audits, 8 scientific inputs, 17 rejected controls
```

The command needs no network, Git history, third-party Python libraries or Lean
installation. It reads both archives in memory, executes no scientific input,
invokes no compiler, writes no files, and checks its deterministic result against
[`RESULT.json`](RESULT.json). It reuses the original, hash-checked driver's
source-command and axiom-log parsers; it is not an independent Lean parser or a
new mathematical implementation.

Additional focused checks:

```sh
python3 -I -B research/pr236-source-reconciliation/test_verify.py -v
python3 -B research/lean-paired-cube-d1d6/test_offline_check.py -v
```

These provide 12 source/archive tests and the original 11 driver fixture tests.
The original package README supplies the separate input-only and Lean build
commands. Its statement about an unrun clean build describes the original
submission and original memory-capped driver; it is preserved verbatim.

Validation on macOS arm64: the main command passed under Python 3.14.6 and
3.13.11, including ordinary repeated runs and optimized Python. The 12 new
tests, 11 original tests, original full input-only check, selected-record check
and its five tests, and existing 528-PR reconciliation check passed. No generator,
selected construction or inherited verifier changed, so the repository-wide
`make verify` and cold supplier replay were not rerun. No hosted CI result is
substituted for these local checks.

## What is bound

[`SOURCE-PINS.json`](SOURCE-PINS.json) records the Git blob, SHA256, byte count
and source commit for all 14 restored files, eight existing evidence files and
the unchanged selected record. Every restored file was compared directly with
the fetched PR236 head. All eight embedded scientific inputs were also compared
byte-for-byte with their original paths at scientific target
`d1d6c070f5a8c684727ee7ec35d930f9ebfa9758`. The offline command rechecks those
recorded identities; it does not contact GitHub to reestablish commit membership.

The complete reconciliation checks:

- Exactly 3,614 source archive members: 3,606 Lean modules and eight scientific
  inputs. Each source digest, import list, audit-command list and ordered
  dependency is checked against `INPUT_MAP.json`. All six principal theorem
  copies and all 13 original `SHA256SUMS` entries agree.
- Exactly 7,215 evidence archive members: 3,606 receipts, 3,606 logs, the input
  map, summary and Darwin driver. Archive/member hashes and the separately
  published map, summary and driver agree.
- Every receipt's source identity, compiler record, timeout, memory policy,
  audit requests and 7,253 internal dependency-object hash references. The
  three recorded Darwin adapter changes reproduce the saved driver exactly.
- Every requested audit name and recorded transitive-axiom set, plus summary
  receipt hashes and complete rebuilt/reused coverage. The totals are 14,320
  audited declarations, including 2,816 axiom-free declarations. The 101
  modules with no audit requests correctly have empty audit logs.
- Exactly 3,602 historically rebuilt modules and four historically reused
  modules. The saved policy has **no address-space cap**; it is not evidence of
  a Linux run or execution under the original 4 GiB cap.

The 17 receipt controls alter coverage, status, module/map/source identity,
dependency hashes, memory policy, audit totals or audit output. Where needed,
they repair enclosing receipt/summary hashes so rejection tests the actual
relationship, rather than merely noticing a changed checksum. Separate source
tests cover missing/extra/changed members, rehashed import and audit mismatches,
altered theorem mirrors, duplicate JSON keys, unsafe archive paths, duplicate
members and nonregular members. JSON booleans are distinguished from integers.

## Evidence boundaries

No disagreement was found between the restored source package and archived
execution evidence. This contribution makes their relationship reproducible
from one checkout; it does **not** repeat the historical kernel run.

Neither archive contains compiled `.olean` objects, the compiler executable or
its installed standard-library objects. Dependency hashes are therefore checked
for consistency with the recorded receipts, not against freshly compiled object
bytes. The [historical finalizer](../community-round9-audit/finalize_pr236_audit.py)
did check actual object bytes during the original audit; that step cannot be
repeated from the published evidence archive alone. The original acceptance
manifest referenced by `ARCHIVE_READBACK.json.accepted_manifest_sha256` is also
absent. Source completeness here is relative to the public `INPUT_MAP.json`.

The package concerns historical conditional κ = 4609169/10000000000, not the
selected #626 value. The selected record remains byte-identical at
κ = 51110230636731/31250000000000000. The existing concrete-field, real-analysis,
physical-composition, dirty-spill/restored-row, fixed-tape and all-size
obligations remain as described in the
[scoped maintainer review](../community-round9-audit/pr236-scope-review.md).
No full formal multiplication theorem, new bound, or human peer review is claimed.

## Sprint scope and attribution

OS-random assignment seed **98**, research consolidation. Three candidates were
the later #210 changes, the later #279 changes and PR236 source integration;
`98 mod 3 = 2` selected the third, a bounded 14-file package. The local claim
was recorded before implementation. No pinned coordination issue existed and
Discussions was disabled. The initial overlap inventory covered 539 open PRs
through #720; the pre-submission refresh covered 551 through #732 and confirmed
the unchanged PR236 head. PR695 addresses #626 Linux execution evidence; PR704
addresses family-ledger metadata validation; PR721 streams PR181 ZIP evidence.
None is a dependency of this contribution.
No source search or mathematical parameter search is claimed.

James Chang (`jamesyc`) authored the PR236 formalization/package, with the OpenAI
assistance disclosed in its original README. Douglas R. Colkitt prepared the
retained maintainer review, Darwin adapter and full execution receipts. The
paired-cube construction retains all original community attribution. Their
source files and historical evidence are unchanged.

Will Richards (`williamreidrichards`) prepared this integration and reconciliation
with substantial OpenAI Codex assistance, including a separate agent's source
audit and code review. New and restored material is covered by the repository's
[Apache-2.0 license](../../LICENSE); existing attribution and notices are retained.

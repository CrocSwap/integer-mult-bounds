# Signed completion independent static review

**HOLD pending controller failure-reporting repair and a separate independently verified freeze.** This review did not run science, guard, service, live audit quarantine or source mutation. No new window is authorized.

## Initial finding

`launch.py:173-174` reads and JSON-decodes the job `RESOURCE.json` unguarded inside `finally`. An unreadable or malformed receipt raises before `control/RESULT.json` is written, potentially masking an earlier signed, timeout, controller, or audit failure and losing its primary/secondary error record. Catch and record receipt-read/parse exceptions as separate secondary failures, fail closed, and still produce controller result where possible; preserve an existing primary failure. Add synthetic controls for malformed/unreadable/missing receipt in combination with failed body and audit cleanup. Abrupt hard-deadline exit is already explicitly reported as unverified and remains a separate inherent limit.

## Static observations

- The proposed job retains original prepare and certificates plus fresh certificate replay and native pass; only signed and resources run anew, with 900/20-second caps, 1190 inner, 1195 wrapper and 1200 service. Controller declares one CPU, 2 GiB memory, zero swap and 16 tasks; guard-only path does not move source audit. Copies of predecessor work and sibling certificates are byte checked against snapshots; no predecessor destination is used.
- The predecessor native receipt/result pins are `cafc2c05b287d9c4e732fbff0c57a438e6848faecb0c333f78377ce9ab74467e` and `2cf79508c3dbffb56a1f0609710ccc921590dd4747850279edefe8f71238b682`. Identity, adapter and original/copy launcher are bound. The failed signed attempt stays visible and missing signed artifacts are checked. The original scientific scripts, resource conjunction, stale checks and six inventory-consumer controls remain in use.
- `audit_custody.py` checks 33 pinned files plus PINS, exact expected directories, rejects symlinks/special or unknown entries, validates known-row contents and size bound, verifies the predecessor SHA, and uses same-filesystem `renameat2(RENAME_NOREPLACE)` with inode and byte recheck. The raw predecessor audit is preserved in a separate frozen input. Controller captures any variable-length signed audit only after group-empty verification and accepts absence only with exact original inventory; successful scientific body alone is not controller acceptance.
- All 494 distinct PLAN closure paths exist and include all 393 predecessor-freeze paths. Independent hash checks found all 393 predecessor rows unchanged; the old run and control snapshots match, with no symlinks. The new FREEZE is absent by design and must be created and independently checked after final edits. These are static observations, not runtime qualification or proof that every fault mode was tested.

## Inspected versions

| File | SHA-256 |
| --- | --- |
| `job.py` | `3afcfc4e87d508d4243d43b1c742333539f7db95ecbfe316f059d9e53db13fce` |
| `run_once.py` | `242f4a67b4338537711bdd28e5217709461507ee9ebb9d4e9d51363941d76909` |
| `launch.py` | `39e71f77e5033720266dcf9b6bd481634ab103e86db1af68844dc5f50755e8a8` |
| `controlled_entry.py` | `f47c5353f9c660cf862f19180b97f3dd57b2af7bad670bae8a5bad0e73fc4b70` |
| `audit_custody.py` | `d7b384f039c0d93451e7994c39ca1c4317c7d27dacfdce5a4982cdc61f1f46e5` |
| `PLAN.json` | `18fdddf83ad3fe505602400cf444f4f27b889014e86938838f3fec534f38170e` |
| `PREPARATION.md` | `1b24042e4a4f1e5f7b72f0017cdc507c4af6936ec62b55663255714540734666` |

## Controller repair re-review

The initial receipt-parse hold is **resolved by static inspection** in the changed `record_job_receipt` function. Missing, unreadable, malformed or wrongly shaped job receipts are caught and recorded separately, leave an earlier `record["error"]` intact, and make completion false; failure to write an auxiliary incomplete receipt is also recorded separately. Valid completion additionally requires return code zero, verified empty group, successful audit capture and a positive executed job receipt. Earlier stop, kill and audit errors remain separate and prevent success. The final controller result write and hard-deadline exit can still themselves fail, in which case the existing contract correctly treats final completion and cleanup as unverified. Synthetic controller tests are reported in PREPARATION; I did not independently run them or a service.

The saved predecessor audit copy was independently confirmed byte-for-byte identical to the still-present real source log: 566 bytes, two rows, SHA-256 `ca23807a4b1d9675daf67903608a6d874e37b94c70109a45fa73732ee8123841`. No source file was moved. This re-review leaves no further static code hold in the reviewed scope; the separate new freeze and independent closure verification remain necessary before requesting fresh user authorization. No launch is authorized by review.

Changed reviewed hashes: `launch.py` `84650e1cf322bc38aa05ce2d2fba48702e23c27871b5728563ec5c1e09cb978b`; `PREPARATION.md` `34994cfd656205b34a3198af67da036d857c06c9faef89b16ba4855bf88f6f5c`. Other inspected file hashes remain as listed above.

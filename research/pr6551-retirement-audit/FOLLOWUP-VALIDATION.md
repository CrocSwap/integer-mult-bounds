# Verification after Claude's review

This follow-up keeps the exact #6551/#6545 construction pins and mathematical claim of original contribution `13e880a734cc03f2a52c82a412a9a0e6ac2b1f0c`. It expands the second engine to both full endpoints, retains and binds the two pricing sources, and separates local integrity from optional Git-object provenance. [EXTERNAL-REVIEW.md](EXTERNAL-REVIEW.md) distinguishes Claude Code / Claude Opus 5.5's reported review of the original snapshot from the new GPT-6 Astra / Codex implementation and internal review.

## Current scientific evidence

CPython 3.12.14, Linux x86_64, standard library only. Actual commands from the activated contribution checkout:

```sh
python3 -B scripts/research_package.py --package research/pr6551-retirement-audit
python3 -I -B research/pr6551-retirement-audit/verify.py
python3 -I -O -B research/pr6551-retirement-audit/verify.py
```

All pass. The registered normal/optimized pair took 3.702 seconds; additional direct runs took 1.609 and 1.778 seconds and reproduced RESULT.json byte-for-byte. RESULT SHA256 is `8c6a7c6fc8872b8de465ebd3101428c9344aed3d93bf82a1a930f183802c8c13`. The measuring process's cumulative child high-water mark was 95,784 KiB. Every subprocess had a 120-second outer limit, with the integrated four-fiber child additionally bounded at 30 seconds. Exact commands, timestamps/source context, elapsed measurements and logs are in [evidence/followup](evidence/followup).

The integrated receipt contains 26 semantic failures (11 primary caller, seven accounting, four cut, four changed-suffix) plus three source-contract failures. New suffix controls pass the earlier cut/lifetime checks before failing specific endpoint coefficients; a valid inverse-pair suffix edit passes. These distinguish useful coverage from blanket rejection of changed files. Three external optimized corruption controls also reject modified caller bytes, native archive bytes and expected receipt; [external-corruptions.json](evidence/followup/external-corruptions.json) records exact error strings. These controls demonstrate integrity and recomputation, not origin authentication.

All 22 retained inputs match their exact original Git objects, including the four #6398 files and two newly retained pricing sources. [direct-source-comparison.json](evidence/followup/direct-source-comparison.json) records the byte comparison. The optional anchored checker additionally passes all 20 original inputs under the original contribution pin and rejects a consistent manifest/source substitution accepted by the portable old replay; [provenance-control.json](evidence/followup/provenance-control.json) records that deliberately different trust boundary. New-publication comparison is part of the committed-byte check below.

[scientific-inventory.json](evidence/followup/scientific-inventory.json) records the hashes of scientific programs, frozen inputs, RESULT and argument/review-boundary documents. It excludes subsequent publication receipts and validation records to avoid self-referential hashes; it is an integrity record, not an external trust anchor. Three reviewed wording fixes after the first integrated run did not change programs, inputs or RESULT. Original logs and FINAL-REVIEW.md remain historical snapshots and are not relabelled as review of the new checker.

## Committed-byte and export procedure

The publication process runs these commands on the exact committed scientific snapshot and repeats them on the final evidence commit:

```sh
python3 -B scripts/check_research_commit.py --package research/pr6551-retirement-audit --check-source-history --check-modes
python3 -I -B research/pr6551-retirement-audit/check_source_objects.py --repository . --publication-commit FULL_TESTED_COMMIT
python3 -B scripts/export_research_package.py export --package research/pr6551-retirement-audit --ref FULL_TESTED_COMMIT --output /tmp/retirement-audit.tar
python3 -B scripts/export_research_package.py check /tmp/retirement-audit.tar
```

After integrity checking, extraction occurs outside the checkout. Every exported file is made read-only, Git metadata is absent, PATH is empty, and both direct isolated Python modes run from the exported root. Full file hashes and modes are compared before/after. The frozen scientific inventory must still match. An evidence commit can retain receipts for its parent but cannot embed its own commit identifier; each retained receipt must therefore name its actual tested commit, and the final exact-head check is reported separately in the PR publication record. No claim of final-head evidence is inferred from a parent's receipt alone.

## Review, continuity and limits

The final code review and documentation review are separate AI roles using the same GPT-6 Astra model family. Findings and resolutions are preserved in FOLLOWUP-REVIEW.md and DOCUMENTATION-REVIEW.md. The external Claude review applies to the earlier snapshot only. Shared opcode, physical tariff and Python rational-arithmetic assumptions remain; agreement is not a proof of those assumptions.

Canonical upstream was refreshed at the time recorded in [context-refresh.json](evidence/followup/context-refresh.json) and remained `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. All three predecessor heads were unchanged. The bounded live overlap refresh found no competing exact audit; its stated partial coverage is not evidence of novelty.

No native/all-width physical replay, physical ordinary-rate proof, numerical crossing, completion-tail, compiler or outer replay, selected-construction replay, historical full suite, Lean or Docker run was needed or performed. All five framework assumptions remain. Remote CI and draft/maintainer status must be reported separately. Next useful work remains a separately derived rational audit of the changed completion-tail parameters.

## Recorded committed snapshot

The expanded scientific snapshot is `092009c8548a520c9913eb905f351c7ce2a4b8cd`. Its committed-byte/history/mode preflight passed on all 75 package files. The optional publication-anchored source check passed on all 22 retained inputs. Export integrity passed; both isolated normal/optimized cold replays reproduced RESULT exactly, and all 76 exported file hashes and modes stayed unchanged. All 37 scientific-inventory entries matched. See [publication-checks.json](evidence/followup/publication-checks.json), [export-inventory.json](evidence/followup/export-inventory.json) and the corresponding `.txt` logs in [evidence/followup](evidence/followup).

The following evidence commit adds this paragraph and those receipt/log files only. It leaves all scientific-inventory entries unchanged. Its own exact-head preflight, source comparison, export integrity and read-only replays are repeated after committing, and their actual SHA/count/results are reported in the PR body. The 75-file receipt above remains explicitly a receipt for `092009c8548a520c9913eb905f351c7ce2a4b8cd`; it is not relabelled as a receipt for the evidence commit.

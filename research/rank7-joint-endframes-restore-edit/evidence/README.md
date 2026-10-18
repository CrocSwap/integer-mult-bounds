# Provenance of the files in this directory

`ADMISSION-RESULT.json`, `ADMISSION-STAGES.json`, `RELEASE-RECEIPT.json`, `FULL-NATIVE-*`, `ENVIRONMENT.json`, `RUNTIME-PATCHES.json`,
`ADAPTER-DERIVATION.json`, `OVERLAY-DERIVATION.json` (PR #2979's rank-7 stage), `EDITS-DERIVATION.json` (the declared edit stage),
`FULL-REPLAY-STAGES.json`, `FULL-REPLAY-RESULT.json` and `logs/` come from ONE development run of `reproduce.py` on Windows with an
explicitly reused, authenticated retained-native cache (`--retained`); the changed words' native chains, the complete admission and the
outer release were fresh. The run used this package before these evidence files were added (the final inventory assertion compares the
package with its manifest at the start of the run). After the run, `reproduce.py`'s result record was split into
`rank7_source_manifest_sha256` and `source_manifest_sha256` (the edited source); `FULL-REPLAY-RESULT.json` was patched to the same two
fields, with the values the run had computed. `EDITS-REVIEW.json` is the output of `edits/edits_review.py` on the shipped words;
`run_registered.py` re-runs it and requires equality. PR #2979's own evidence is in `pr2979/`.
The complete NO-CACHE `verify_release.py` runs (Windows and WSL) are separate; their times are in the PR description.

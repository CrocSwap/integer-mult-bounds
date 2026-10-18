# Provenance of the files in this directory

`ADMISSION-RESULT.json`, `ADMISSION-STAGES.json`, `RELEASE-RECEIPT.json`, `FULL-NATIVE-*`, `ENVIRONMENT.json`, `RUNTIME-PATCHES.json`,
`ADAPTER-DERIVATION.json`, `OVERLAY-DERIVATION.json` (PR #2979's rank-7 stage), `EDITS-DERIVATION.json` (the declared edit stage),
`FULL-REPLAY-STAGES.json`, `FULL-REPLAY-RESULT.json` and `logs/` come from one complete run of `reproduce.py` on macOS arm64 with an
explicitly reused, authenticated retained-native cache (`--retained`); the changed words' native chains, the complete admission and the
outer release were fresh, ending `PASS_RANK7_EDITS_COMPLETE_REPLAY` at `κ = 0.0017297361663879159868119999999999999999999998999999999999999999999999`. `EDITS-REVIEW.json` is the output of `edits/edits_review.py` on the shipped words (`{'base': 11, 'extra': 11}` controls);
`run_registered.py` re-runs it and requires equality. PR #2979's own evidence is in `pr2979/`.

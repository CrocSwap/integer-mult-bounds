# Provenance of the files in this directory

`ADMISSION-RESULT.json`, `ADMISSION-STAGES.json`, `RELEASE-RECEIPT.json`, `FULL-NATIVE-*`, `ENVIRONMENT.json`, `RUNTIME-PATCHES.json`, `ADAPTER-DERIVATION.json`, `SOURCE-DERIVATION.json`, `FULL-REPLAY-STAGES.json` and `REWRITE-REVIEW.json` come from ONE development run of `reproduce.py` on Windows with an explicitly reused, authenticated retained-native cache (`--retained`). In that run the changed words' native chains, the complete admission and the outer release were fresh. (That run's final inventory assertion failed only because package text files were edited after packing; every stage had passed, so no `FULL-REPLAY-RESULT.json` is stored.)

The complete NO-CACHE `verify_release.py` runs (fresh retained bootstrap, fresh native chains, complete admission and outer release) are separate; their pass times are listed in the PR description and their receipts are not stored here.

`evidence/pr2930/` is the inherited record of PR2930's own run (its words, fill and cap certificate), kept for reference; `check_cap.py` and `certificates/` describe PR2930's profile and are not run for this package.

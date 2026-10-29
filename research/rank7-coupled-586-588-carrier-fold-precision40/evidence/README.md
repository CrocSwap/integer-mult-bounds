# Provenance of the files in this directory

`ADMISSION-RESULT.json`, `ADMISSION-STAGES.json`, `RELEASE-RECEIPT.json`, `RELEASE-VERIFY-RESULT.json`, `FULL-NATIVE-*`, `ENVIRONMENT.json`, `RUNTIME-PATCHES.json`,
`ADAPTER-DERIVATION.json`, `OVERLAY-DERIVATION.json` (PR #2979's rank-7 stage), `EDITS-DERIVATION.json` (the declared edit stage),
`FULL-REPLAY-STAGES.json`, `FULL-REPLAY-RESULT.json`, `SEAL.json`, and `logs/` bind one complete precision-40 `reproduce.py` run.
The fresh retained-provider bootstrap and its native cache were created in the preceding precision-30 attempt; this run reused them only
after exact receipt and cache-tree authentication (`--retained`). Both changed words' native chains, the full replica admission and the
outer release were run for precision 40. The replay ended `PASS_RANK7_EDITS_COMPLETE_REPLAY` at
`κ = 0.00172977608940512033423846781989357386829999999999999999999998999999999999999999999999`, strictly above PR #3133's public claim
by the exact positive rational recorded in `CLAIM.json`. `FULL-REPLAY-RESULT.json` explicitly records the retained-cache reuse. `EDITS-REVIEW.json`
is the output of `edits/edits_review.py` on the shipped words (`{'base': 21, 'extra': 21}` controls); `run_registered.py` re-runs it and
requires equality. PR #2979's own evidence is in `pr2979/`.


This precision-40 package rebinds its terminal admission, native and release receipts to the exact `CLAIM.json` above. The source words and T74 allocation remain byte-identical to PR #3133; only the endpoint arithmetic and its source-bound verifier change.

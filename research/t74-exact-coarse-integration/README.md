# Source-bound T74 integration of the exact coarse exponential

This applies PR2168's exact-interval arithmetic to the actual slow rejection call in PR2044's complete T74 replay. It builds an explicitly derived package in a fresh separate directory. The frozen parent package, original engine, selected certificate, native words, precision, invoice and every original assertion remain unchanged.

The only caller change is `M.moment(H,73,owner['live'],b,True)` to `exact_coarse_moment(M,H,73,owner['live'],b,True)`, plus the required import. The adapter is copied byte-for-byte from the pinned PR2168 source. An inverse byte transformation proves that all other original caller bytes remain; AST assertion counts also match. A new manifest honestly identifies the derived package and its two source changes; it is not a forged parent receipt.

Run `python3 -B research/t74-exact-coarse-integration/verify.py` for the source-only gate. To perform the full integration, obtain PR2044 head 322949a53488d64023fedb89a6774927707e57ba and its `research/capped-fusion-t74-k554` package. Run `build.py --parent PARENT_PACKAGE --out FRESH_DERIVED_PACKAGE`, then the derived package's unchanged `verify.py --work FRESH_REPLAY_WORK` with the native prerequisites and optional honest source-bound native cache. Finally run this package's `verify.py --baseline ORIGINAL_REPLAY_WORK --derived DERIVED_REPLAY_WORK --out COMPARISON_RESULT`.

The final comparator requires complete admission statuses, identical kappa and controls, exact equality of **every assembly field**, all admission/bit/independent control outcomes, and all six geometry controls. Control source hashes must equal the exact old/new caller hashes. The independent auditor's six location-keyed input digests are each checked against the actual files and compared as a complete basename/digest inventory; fresh-work-directory locations are the only location difference. It does not drop hash fields, normalize proof data, skip checks, cache fabricated results or edit assertions. The original external parent is validated against its entire pinned manifest before copying any file.

No new kappa or multiplication-theorem claim. Source-bound native reuse is recorded explicitly; no fresh native replay is implied when unchanged witnesses are reused. The registered fast hook checks the derivation only; the separate actual full replay is required for an integration claim. Inherited parent aggregate CRLF/LF and broad historical source-pin limitations remain separate. Machine-specific timings and private raw logs are excluded.

Credit PR2168 (exact integer adapter), PR2044 / Jeremy Kothe and the retained T74, PR1297, PR1319, PR1672, native, moment-engine and precision-repair contributors. Frozen notices are preserved. Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

Review and adopt the verified derived caller through an explicit maintained source-manifest update. The selected/default frontier and frozen parent are not modified by this package.

## Completed integration evidence

The actual derived package's full verifier returns `PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION`. The integration gate returns `PASS_FULL_T74_EXACT_ARITHMETIC_INTEGRATION`. The complete assembly is byte-for-byte identical to the original; native/conservative endpoints, both engines, adjacent-grid rejection, both 47-inequality assemblies, profiles, coefficients, source/invoice hashes and all other assembly fields match. All original admission/bit/controller/owner/geometry controls pass. Expected changed caller hashes are checked against the exact derivation; all six independent input file digests are validated and their location-independent inventory matches. No mathematical field is discarded.

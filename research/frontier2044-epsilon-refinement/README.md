# PR2044 free-epsilon refinement

This conditional arithmetic contribution changes only the free outer point from delta = 2 r0 to delta = (1025/1024) r0, where epsilon = 1 - delta and r0 = 10^(-30010). Beta remains 1 - 3 delta. The inherited supplier, fine engines, endpoint precision, owners, native words and all-size assumptions are unchanged. Parent package bytes are frozen.

The gain is strictly positive but extremely small: approximately (1023/1024) q r0. It does not improve the paid supplier ceiling. The exact kappa and gain are in CLAIM.json. The fast verifier checks all 62 retained inequalities and 17 rejecting controls, independently derives the nine cost powers, and checks both the previous point and the exact gain. It intentionally makes no standalone native-admission claim.

From repository root, run `python3 -B research/frontier2044-epsilon-refinement/verify.py` for the arithmetic gate. The registered Python 3.12 hook runs only that fast gate.

For complete finite admission, run the unchanged parent's `verify.py --work SUPPLIER_WORK --audit-shards 2` on Linux with the native toolchain, and its unchanged `outer/run_outer.py OUTER_WORK` on Windows, capturing its output to OUTER_LOG. Then run `python3 -B research/frontier2044-epsilon-refinement/verify.py --supplier-work SUPPLIER_WORK --outer-work OUTER_WORK --outer-log OUTER_LOG --out RESULT_FILE`. Work paths must be fresh and outside the parent package. All three steps are required. Supported native caches require source-bound honest receipts.

**Parent reproduction detail:** PR2044 commits CRLF ledger artifacts. Its Linux `verify_release.py` attempt fails the original byte comparison even when every parsed value is identical, because Linux regenerates LF. The unchanged outer checker is therefore replayed on Windows, where it reproduces both artifacts byte for byte. The supplier admission runs separately on Linux; the final gate binds its exact manifest, endpoint, profile, controls and assembly to the unchanged outer artifacts. No parent assertion, certificate or source file is modified. This contribution does not claim a Linux `PASS_RELEASE` for the parent aggregate wrapper.

All inherited compiler, hosting, precision/tape, recovery, analytic, prime-theorem and bit-supplier hypotheses remain conditional. This is not a full multiplication theorem verification. No independent human review is claimed.

Credit PR2044 and Jeremy Kothe's capped-fusion package; PR1786 (Chafik Boukhalfa) and Tim Trudgian's prime theorem; PR1673 (Vlado Vojdanovski); PR1758 and the retained outer lineage; PR1625, PR1672, PR1319, PR1297 and the supplier/native lineage; PR1956 (Josie Elliston), PR1964 (Sagar Thakrar), and PR2029. Existing predecessor notices retain detailed attribution. Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

A material gain needs a cheaper fully admitted supplier. This arithmetic refinement leaves that problem open. See TASK.json for the next experiment and the explicit stopping rule.

## Validation limits

The source-bound complete finite gate passes; RESULT.json binds the executed parent components. Required gen4-bank and frontier741 checks pass. The broader `make verify` stops at the **pre-existing** `split-skip-check` source pin for `scripts/audit_fused_block.py`. Both that source and its frozen pin are byte-identical to PR2044. No frozen pin was changed. VALIDATION.json records the expected/actual public source hashes and the interrupted extra unit-suite run. A whole-repository green regression or hosted-CI pass is not claimed.

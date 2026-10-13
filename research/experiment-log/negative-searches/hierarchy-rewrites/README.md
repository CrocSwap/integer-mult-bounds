# Hierarchy rewrites: all 424 alternatives and the baseline

This batch searched a different source hierarchy neighborhood after the previous retiming searches found no gain. All 424 alternatives plus the baseline compiled successfully. **Only candidate-201 reduced helper stock from 715 to 714. This is a nomination, not a new kappa or a full certificate.** The other 423 alternatives did not reduce helper stock; some may still have useful paid profiles. No final global price was computed for this batch.

| Helpers after reuse and retiming | Cases, including baseline |
|---|---:|
| 714 | 1 |
| 715 | 112 |
| 716 | 111 |
| 717 | 151 |
| 718 | 48 |
| 719 | 2 |

[Complete ledger](LEDGER.json) retains all 425 results, exact replacement rules, compiler statistics, paid-rank histograms, retiming moves and canonical word hashes. [All compiled cases](ALL-COMPILED-CASES.tar.gz) contains every WORD.json.gz and RESULT.json, including the baseline and every losing candidate. [Terminal completion](COMPLETE.json) and [summary](SUMMARY.json) separate execution failures (zero) from candidates that failed to reduce helper count (423).

The [inventory](r715-hierarchy-rewrite-inventory/RESULT.json) examined 822403 unordered pairs among 1283 hierarchy symbols, checked XOR equality, frame containment and acyclicity, and found 424 alternatives. Seventy reduced reachable-symbol count, but the only helper-stock reduction came from a rule that increased reachable-symbol count. Do not prune future searches using that proxy alone.

Candidate-201 replaces rule 647's children [645,629] with [0,1128]. Its canonical word SHA256 is d026dcef68dc9f863818805be37c314336cef429fb55cdf154df7ff38118d231. Its compiler uses 241 carriers and 714 reused helpers. It passed compiler F2 checks and the monotone frame/profile screen after six retiming sweeps with M=78. Independent dirty-column replay for the changed stock, native checks, fresh kernel/target-factor search, physical hosting and exact composition remain pending. Old R715 helper indices and factor witnesses cannot be reused without reconstruction and checks.

## Retained failed baseline comparison

The initial reconstruction compiled to 839 helpers, reused to 715, then retimed with M=64. Its strict object comparison with the pinned word failed. The [original failure log](r715-hierarchy-baseline-rebuild.log) remains unchanged. [Order-equivalence diagnosis](r715-hierarchy-baseline-rebuild/ORDER-EQUIVALENCE.json) identifies exactly two swapped source lists, at B gates 356 and 432. They have the same frame and destination and distinct unchanged source registers, so the additions commute; all other fields match. This does not turn the failed strict comparison into a byte-equality pass. The 425-case screen saved its own baseline under the same ordering and M=78 settings as its alternatives.

## Sources and retry guidance

The hierarchy comes from [PR463](https://github.com/CrocSwap/integer-mult-bounds/pull/463), acquired at commit 1b1de4833686bfa335509b21266afc44baef0fd2; original contributors retain attribution. [Acquisition record](SOURCE463-ACQUISITION.json), [dependency hashes](DEPENDENCY-HASHES.json), [inert JSON hierarchy](r715-hierarchy-rewrite-inventory/HIERARCHY.json), [original hierarchy](PINNED-HIERARCHY.h) and [reference word](PINNED-R715-WORD.json.gz) are retained. The original hierarchy is a pickle: the inventory script uses a restricted loader accepting only ham1.SH as an inert data class; do not load untrusted pickles unrestricted.

The four archived Python scripts preserve their original workspace-relative paths. Restore the matching dependencies before replaying; they are evidence, not a portable full verifier. Preserve the recorded output folders and run any changed experiment in a fresh directory. Do not rerun the same 424 alternatives unless changing the compiler, objective, source or verification scope. Useful followups are independent checks of candidate-201, fresh objective-aware pricing, or multi-rule rewrites. A bounded losing screen is not a proof of impossibility.

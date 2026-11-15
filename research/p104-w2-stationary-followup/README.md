# W2 stationary-lifetime follow-up (conditional, candidate-adapted)

This is a separate follow-up to the original PR #7603 package, which is left unchanged. It is **not** a new unconditional integer multiplication bound, formal proof-kernel result, maintainer acceptance, or selected-frontier change.

## Result and scope

The literal W2 word has conditional signed claim **C = 0.003656628302607**, under the same five inherited assumptions: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. The directed crossing is strictly between **0.00365662830260** and **0.00365662830261**. The native ingredient claim is separately **0.003655910458378**; do not confuse it with the complete 17-stage signed application.

Fresh full candidate-adapted native and signed applications passed, including all 3040 signed catalogue cases and assembly. Evidence is in `evidence/NATIVE.json`, `evidence/SIGNED.json` and full logs. Paid signed positions: 110213; productive fields: 22461; ordinary bill: 785258936 (< 10^9); precision context: 2430. Fixed tape: 44069536 scalar services, 25425383744 elementary records, 1156 reserved owned banks.

## Construction and lifetime boundary

W1 ports the #7611 stay drops and #7612 contact134/329 rechart onto the **uncollapsed #7605** schedule. W2 adds 39 stationary auxiliary lifetimes. It preserves all 74 original lifetimes and the original 195-event owned INIT/MOVE/CLEAR chronology as a subsequence, including their erased contents. Total CLEARs are **113 = 74 original + 39 new**, not 113 newly discovered erasures. Peak live count is50; declared owned labels remain68.

All113 CLEAR relations were checked exactly over Q against other still-live rows (110 nonzero,3 zero); corrupted coefficient and cleared-field-as-source controls are rejected. A CLEAR relation does not itself implement a universal physical erasure service. Every added lifetime stays in its INIT chart and has no owned MOVE. The fixed allocation `(native occurrence, declared owned field)` reserves17*68=1156 distinct banks, not17*peak50. This establishes literal sequential non-overlap and identity under atomic-child-return and owned-erasure services; it does **not** prove those inherited services unconditionally. #7609's same-events theorem is not applied to the added events. The collapsed CLEAR44 candidate is not silently adopted.

## What was adapted, not waived

`adapters/native.json` and `adapters/signed.json` contain exact before/after substitutions with occurrence counts. Hash, event census and invoice expectations are candidate-specific. The original assertion that six legacy direct chart pairs remain was replaced by equality to the complete actual affected-pair census versus pinned #7481: **442 pairs on84 public fields**. Every affected pair retains512 forward and512 adjoint Gaussian column tests, absolute-phase checks and wrong-phase rejection. Native corruption, insufficient-grid, endpoint and paid-move controls remain. Exact source reconstruction is followed by the SHA-pinned literal edit manifest `data/edits7605.json`.

The signed precision adapter changes the explicit expected census tuple from(74,50,68) to(113,50,68), retaining the original bound computation and fresh native-to-signed receipt chain. Status markers deliberately say `W2_ADAPTED`, not original-unmodified acceptance.

The original #7605 baseline was separately reproduced on Windows. One full-SHA-pinned in-memory source path rendering change (`relative_to(...).as_posix()`) fixes a slash comparison, without altering archives or disabling archive hashes/safe-path checks. Seven baseline receipt hash differences were exactly CRLF versus LF; normalized receipts matched the original pinned signed and final receipts. `windows_path_shim.py` declares this compatibility patch. No registry/security settings were changed. W2 full candidate checks are distinct from that baseline reproduction. No Linux run is claimed.

## Reproduction

Python3.12 was used; assertions must be enabled. Obtain the immutable source tree for PR #7605 from `CrocSwap/integer-mult-bounds`, and supply its `research/p104-timed-helper757` directory. `SOURCE.json` pins the exact application hash; its retained-source `authenticate()` is rerun. The checked #7605 head is `e1d2756eecf03e146338239fee81772a99ba8d4c`. Fetching a different source version will fail rather than silently proceed.

```
python reproduce.py --source /path/to/pr7605/research/p104-timed-helper757 --work /short/new-work --stage all
python verify_certificates.py data/word.json.gz evidence/certs-w2.json
python verify_lifetimes.py /existing/output-directory
```

`--stage prepare` only constructs adapters; `native` and `signed` run sequential stages against the prepared directory. Signed requires a successful fresh W2 native receipt. Each stage has a1200-second deadline. Use a short output path on Windows. The portable preparation was tested and produced exactly the same native and signed scripts as the completed full run. Reproduction writes only its work directory and the shim's adaptation log; it does not modify the supplied source tree or contact any external service.

`PINS.json` authenticates packaged evidence and inputs. `data/word.json.gz` compressed SHA256 is ed760a6d4efc06ffdc831acd99b1a4661b09eb3cd82e2942a4783f4af0e52110. `evidence/w1-to-w2-patch.json` gives299 literal replacement blocks (no metadata changes); literal reconstruction alone is not a semantic proof.

## Credit and next review

Prepared for SYLforge with substantial AI assistance: candidate work using Claude Opus5.5, and independent checks/integration using OpenAI assistance. Imported improvements are not claimed as new here. Base #7605 is Ali Romman with Codex; #7611 stay-drop work is DreamingOfClouds with Claude; #7612 contact rechart is Clear1nsight with OpenAI assistance. Retain Hao Yan/FanPUYen (#7604), SYLforge (#7603), DreamingOfClouds (#7601/#7607 and related), ToikY (#7546/#7544), Rohan Arun (#7113 and rechart work), dillona, CubeJerry and all nested-source authors. `BASE-NOTICE` retains the baseline notices; the required source tree retains its complete nested notices. Apache-2.0. #7613 is an invoice comparator, not the W1 construction base.

The contribution is this stationary-bypass composition and scoped fresh verification, not ownership of the inherited framework. Review should inspect the five assumptions, CLEAR service interpretation and literal identity/ordinary/tape accounting. Nothing in this package changes the selected public frontier, claims reviewer approval, or treats a conditional bound as unconditional.

## Concurrent #7615 comparison

Before submission, PR #7615 was observed at conditional C=.00365455370060. Its four courier pairs are not identical to this composition. W2 independently contains the same direct public pairs(3,746) for field1250 and(743,245) for field7; it does not contain(719,127), and fields532/226/990/779 retain their #7605 routes. We do not claim priority or exclusive novelty for those overlapping contractions. #7615 was not used to construct the pinned W2 artifact; its overlap is disclosed here for reviewer context. Neither invoice value implies unconditional acceptance.

Packaged text uses LF; log trailing spaces are trimmed. Numerical and status content is unchanged.

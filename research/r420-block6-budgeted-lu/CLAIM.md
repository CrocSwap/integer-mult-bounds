# Local sprint claim

- **Track:** bit supplier.
- **OS assignment seed:** 06, sampled with `secrets.randbelow(60)`.
- **Base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` (`origin/main`).
- **Object:** eumemic's PR543 R420 phase-B block index 6, frame 548, the fixed 12-by-12 transfer in `B[417:471]` (54 XOR gates).
- **Question:** does the retained randomized pivoted-LU sampler contain a shorter exact circuit that the original cancellation-free-norm-only selector does not choose?
- **Method/domain:** enumerate exactly 20,000 randomized LU candidates for this matrix, using `Random(42)` from the generator's existing `7 * block_index` rule; retain the Pareto frontier in (XOR count, cancellation-free positive norm). Require an exact map and a candidate no worse than the 2,000-trial baseline on positive norm. The output assignment and all downstream routes are regenerated.
- **Optimistic complete price:** a net block reduction of two XORs saves four scalar ADD records when its literal reverse cleanup is rebuilt and no other accounting term increases. This local R420 edit cannot improve the current selected κ by itself; rank mass, paid histogram and hosted bills must be reported separately.
- **Candidates checked:** (1) R420 block 0, slice `B[120:176]`, 56 gates; (2) R420 block 2, slice `B[222:263]`, 41 gates; (3) R420 block 6, slice `B[417:471]`, 54 gates (chosen because the assignment seed selects block 6 and it has the largest untouched baseline).
- **Overlap and prior results:** a complete fresh overlap snapshot covered 839 open PRs and 88 discussions with no warnings. No exact block-6 circuit submission or claim appeared. Current neighboring block work is #670 block 3, #674 block 5, #789 block 7, #810 block 8, #790 block 9, and #1363 block 4. The same-seed branch `research/seed06-bit-supplier` is a distinct R439 frame-509 local-minimum proof (#1359). PR #661 proves a negative result only for fixed-gate-stream frame reassignment; it explicitly excludes circuit resynthesis. PR #674's prior 10,000-trial block-5 search found 37 gates against its accepted 34-gate circuit, a block-specific failed search, not an exclusion for block 6. PR #1015 searches multi-write shears on a different R439 word.
- **Coordination:** GitHub reports no pinned issues. Per the task's local-claim instruction, no separate issue or discussion was opened.
- **Stopping rule:** finish the fixed 20,000-candidate sweep, with a 10-CPU-minute cap. If no qualifying circuit appears, perform at most one distinct, explicitly bounded pivot, then hand off the searched domain and limits. Reserve the final quarter for verification and handoff.
- **Expected deliverable:** exact replacement and regenerated word with a reproducible verifier, or a scoped finite-search result; no new κ claim.
- **Expected finish:** 2026-10-14 00:38 UTC.

DONE — 2026-10-13 23:59 UTC. [PR #1390](https://github.com/CrocSwap/integer-mult-bounds/pull/1390) records the fixed 20,000-sample Pareto-selected LU result: block 6 goes from 54 to 47 XORs, and full local scalar ADDs from 26,916 to 26,902. Local exact replay, 660-column interface checks, mutation controls, and the adapted native/hosted R420 pipeline passed. The selected κ is unchanged; no optimality or new-κ claim is made.

# Experiment ledger

Deterministic runs, no random seed and no paid compute. This continuation began
2026-10-16 05:18 UTC with a roughly 60-minute budget. Four delegated agents
handled frontier/reproduction, independent dual arithmetic, structural changes,
and outer precision. Native chain concurrency never exceeded two.

At the pinned endpoint, approximate moment contributions are rank1:33.54%,
rank48:26.56%, rank2:17.78%, rank3:11.44%, rank4:7.08%, rank5:2.72%,
and rank8:0.88% (floating screening only; exact acceptance uses rational
intervals). Rank-one native work and rank-48 remainders dominate. The attained
fixed-inventory dual removes repacking as a degree of freedom; changed native
work/interfaces or a sharper explicit endpoint remain the tested possibilities.

| Hypothesis | Decision and evidence |
| --- | --- |
| Repacking the same inventory can lower the moment | Rejected. Independent enumeration checks all 1,163 patterns; the attained dual closes this fixed model. `audit/check_optimum.py`, `evidence/INDEPENDENT-OPTIMUM.json`. |
| Add a fifth independent cancellation direction by adjoining one nonzero column | Rejected for the stated domain: 216 columns/provider, none lie in the required span. Redistribution of existing kernel directions by basis changes is not excluded. `experiments/RAW-BASIS.json`. Joint rank was already in PR2857. |
| Lift one zero-compensation helper entry frame | Rejected: 47 cases/provider, all94 fail fixed centre/warp/endpoint constraints. `experiments/ENTRY-LIFT.json`. No complete-cost candidate reached native admission. |
| Refine rational endpoints while retaining the whole construction | Exact native/conservative signs and all outer rows pass as a screen. The 40-digit candidate is frozen; complete release passed. `evidence/INDEPENDENT-PRECISION.json`. |
| Published baseline reproduces unchanged | Failed: exactly two manifest-listed files absent. Separate exact recovery then exposed gzip OS-header inequality. No original check or manifest changed. `evidence/run-logs/` and `notes/PORTABILITY.md`. |
| Portable finite replay and cold full baseline agree | Passed. Decoded regenerated payload equality plus immutable container hashes; five finite mathematical stages, mutation controls, six fresh native chains, retained-parent admission and strict complete baseline release. `evidence/BASELINE-RESULT.json`. |

Exact commands, working directories, exit codes, timings and log hashes are in
`evidence/run-logs/*.json`, the native/admission stage receipts and the structural
`experiments/RUN.json`. Historical absolute paths identify the actual local
runs; README.md gives portable reproduction commands. Early agent notes remain
labelled as screens, even when later complete evidence is available.

Only one bounded structural pivot was undertaken. A broader changed-program
claim by Mason Hale (ROUND-4, posted05:22UTC) was already active in
[Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612)
at the final census, so these negative tests carry no exclusive priority claim.
More packing seeds or repetition of the same47-case entry subset are not
justified. Other helpers and entry lines remain unsearched.

The combined `reproduce_all.py` orchestrator has source-export, syntax and help
preflight, but has not been run as a second redundant cold job. Its constituent
full stages are run separately in this session. That distinction is retained
in ENVIRONMENT.json and the final handoff.

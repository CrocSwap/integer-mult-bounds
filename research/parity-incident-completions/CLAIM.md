# Sprint claim

- Track: structural decoder research; OS assignment seed 47 (unbiased UInt32 rejection sampling, 2026-10-13 08:43 PDT).
- Base: 407d52ff15b2217b6e22bce44728b4c3907b6515.
- Object: the 692 pointwise-completable degenerate nodes in the deterministic historical ParitySide(10) DAG; all minimum-dimension nondegenerate sandwiches, with every actual source-line and target-line residual required to be zero or nonalternating.
- Method: exhaustive exact enumeration of one-dimensional extensions of radical-one source spans inside target-perp; independent explicit-vector residual checks. Seed 47 selects h=10 and this refinement of the odd-label interface.
- Deliverable: exact census/certificates, proof of coverage, meaningful negative controls, source pins and one reproducible offline command. No supplier or new kappa claim.
- Expected finish: 2026-10-13 09:25 PDT, including final verification/handoff.
- Alternatives considered: simultaneous nested frames for the same DAG (too broad); several added E8 decoder totals with fixed readers (crowded and larger search). This is distinct from PR972's pointwise sandwich census and PR920's two-source/two-target rectangles.
- Coordination: public issues page and a repo-scoped sprint-issue query checked; no pinned coordination issue found. Claim retained locally as requested. Relevant open PRs and review ledger inspected; PR972 fetched for exact source comparison. Delegated work stays within this residual-completion census.

## Result update

Completed the fixed-domain census and exact local dimension refinement:
560 nodes admit a safe minimum, 12 require one extra dimension, 100 require
two extra dimensions, and 20 have no incident-safe frame at any dimension.
The producer and independent vector-set checker agree on all 3,096 minimum
frames. The 22-test suite passes normally and with assertions disabled;
fresh regeneration is byte-identical. No new kappa or legal supplier is claimed.

The open-PR overlap search was refreshed before submission. PR #920 and
PR #972 remain open at the exact heads recorded in SOURCES.json; this note
adds full-DAG line residuals, larger-frame minima and the 20 absolute local
obstructions beyond those predecessors. The current main moved to
`8bddbee377e2f3ce1f1247196c4b290d55767d20`; the contribution retains its
declared base and source pins. An isolated worktree was used after concurrent
work was detected in the initial checkout.

Result package: [woklerx research branch](https://github.com/woklerx/integer-mult-bounds/tree/research/seed47-incident-completions/research/parity-incident-completions).
The final chat handoff links the focused PR. No coordination issue was available
to receive a public claim update.

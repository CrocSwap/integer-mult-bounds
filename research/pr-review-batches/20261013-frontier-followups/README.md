# Frozen 18-PR follow-up batch

This is **triage, not an integration or approval record**. The selected conditional
frontier remains PR799 at κ = 0.001661634653669567. The live snapshot contains
705 open PRs, including 90 drafts: 271 outside the recorded ledger, 147 partially
reviewed, 280 unreviewed, six previously marked changed, and one newly changed
head. There are no open PRs immediately closable solely from a completed current
ledger disposition.

| Order | Related work | Frozen open PRs |
|---|---|---|
| 1 | Evidence coverage and proof pointers | #838, #841, #847, #851, #865 |
| 2 | Opt-in concurrent complex replay | #853 |
| 3 | U8 and T21 frontier, independent check | #869, #870, #881, #890 |
| 4 | Related scoped bounds and audits | #864, #874, #886, #894, #909, #910, #911, #812 |

PR858 is a closed dependency, credited to Hao Yan, whose T16 work is used by
#870 and #890. It is recorded separately rather than counted as an open PR or
silently reopened. The newer #890 headline is an unreviewed contributor claim.

The first group needs a compatibility review: #847 and #865 overlap, while #851
proposes changing a historically hash-pinned binding. Do not apply these patches
blindly or discard either author's credit. Preserve historical proof/source
contracts while strengthening the public admission path. #853 changes scheduling;
verify its dependency graph and equivalent evidence before using it to accelerate
later batch replays.

The immutable source heads and complete Git-derived path inventories are in
[PLAN.json](PLAN.json). Screening receipts establish only their stated local
checks, not completion of the entire PR. The central review ledger is unchanged.

Follow the [batch policy](../../../docs/research/pr-batch-review-policy.md):
share checked dependencies, retain per-PR claim/attribution/coverage, publish
compatible completed subsets, and carry forward unresolved work explicitly.

Initial screening reproduced #838's 111 accepted altered-evidence cases and its
117 supplemental rejections, and #841's 11 detached-proof acceptances/rejections
plus 12 regression tests. See [SCREENING.json](SCREENING.json). These findings
concern evidence admission; they do not show that the actual retained replay
was incomplete or the mathematical construction incorrect. Integration and
compatibility review of the proposed fixes remain pending.

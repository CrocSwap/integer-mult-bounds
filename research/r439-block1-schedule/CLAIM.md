# Local sprint claim

- Track: bit supplier. OS assignment seed **8**, drawn with Python
  `secrets.randbelow(100)` on 2026-10-13 at approximately 08:37 UTC.
- Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Scope: selected PR589 R439 phase-B block **1**, `B[128:163]`, frame 507,
  ordered registers `[0,3,11,61,62,63,68,69,72,465]`. This punctured ten-wire
  block includes arbitrary dirty helper 465, unlike the twelve-source blocks.
- Hypothesis: exact positive-integer rescheduling of the two existing factors
  (first 14 gates, last 21 gates) reduces the scalar additions while preserving
  the physical output assignment and not increasing positive reverse bounds.
- Method: complete subset-state dynamic programming in each factor's
  destination-once positive-addition class. No helper, output permutation,
  repeated destination batch, frame change, or additional copied total.
- Deliverable: literal circuit, finite search certificate, full local arbitrary
  input replay, exact complete cost, native checks if available, source pins,
  negative controls and a scoped research note. No kappa claim.
- Timebox: 40 minutes from 08:37 to 09:17 UTC; orientation ends by 08:45;
  reserve 09:07 onward for verification and handoff.
- Claim recorded: 2026-10-13 approximately 08:43 UTC. No pinned issue exists
  (GitHub GraphQL `pinnedIssues(first:10)` returned an empty list immediately
  before this claim); no separate issue opened.

## Candidate selection and overlap

Three candidates: (1) a fixed-frame rewrite of a punctured phase-B block;
(2) an A-stage single-summand transport at frame 509; (3) smaller cleanup frames
for the fixed decoder. Candidate 2 overlaps PR589's fixed-point transport and
PR843's new source sum; candidate 3 is excluded in the stated fixed-prefix model
by PR827 and has the restored-sharing obstruction in PR848. Choose candidate 1.

Diversification: apply `random.Random(8).sample([0,1,3,5],4)` to the four
punctured blocks, obtaining `[1,5,3,0]`; take block 1. This selects a different
matrix and dirty-helper interface, not merely a new seed for an old search.
The completed greedy transport search in PR589 does not search this class.
PR844 changes block 4 and PR857 changes block 8. PR728/792 change A mini-nodes.
Historical R420 block work (PR789/790/810) supplies related scheduling ideas,
but no pending code or savings are imported. PR661 fixes the gate word and
PR827 excludes smaller cleanup frames; neither excludes a scalar rewrite.

Read the contribution rules, selected certificate, current review and status,
central review ledger and contribution-review index. Current conditional
kappa is 0.001661634653669567 (PR799/589), not a historical PR title.
Initial live overlap check: recent 100 open PRs through #867, all R420/R439
search results; exact R439 search returned 11 open/closed PRs and no block-1
claim. Source PR589 head is `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.

Contributor: @Deftsalt-debug, with substantial OpenAI Codex assistance.

## Result and handoff — 2026-10-13, approximately 09:02 UTC

Completed: [construction, proof and replay](README.md). Block 1 falls 35 -> 30
ADDs and complete native ADDs fall 24,305 -> 24,295. Both fixed-factor optima
(14 + 16) are checked over all 2,048 states by two different implementations.
All 661 dirty-input columns, thirteen controls, identical frame paths/profile
and the reduced positive prefix pass. Both words also pass unchanged native
legality and 5/9/11-stage checks with 96 bridge controls; minimal relocated
optimized replay passes. No new kappa, unrestricted optimum or hosted invoice.

Final overlap refresh through #874 found navinor's #873 at
`117c48527dd4f066dad103121761154cf1bb39cd`, a distinct whole-block rescheduling of
frame 508. It is credited in the README; no priority or composition is claimed.
PR844 and PR857 still concern frames 520 and 523. Main remains the exact base.

Initial GitHub fork creation returned HTTP 403, `Resource not accessible by
integration`, so the first handoff was a local commit and verified patch.
After the contributor created the fork, the finished branch was successfully
[pushed to Deftsalt-debug/integer-mult-bounds](https://github.com/Deftsalt-debug/integer-mult-bounds/tree/research/r439-block1-schedule-seed8).
A publication-time overlap refresh through PR876 found no matching block-1
contribution; main remained the exact base. Both CLI and connected-app attempts
to create the upstream PR returned HTTP 403. No PR was created. The contributor
can [open the prepared comparison](https://github.com/CrocSwap/integer-mult-bounds/compare/main...Deftsalt-debug:research/r439-block1-schedule-seed8?expand=1).
Validation details are in [VALIDATION.md](VALIDATION.md).

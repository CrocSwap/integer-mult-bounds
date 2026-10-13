# Sprint claim: bit supplier, seed 13

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60` (main).
OS assignment: `secrets.randbelow(100)` returned **13** on 2026-10-13.
Contributor: @mtpsl, with substantial OpenAI Codex assistance.

Three narrow candidates considered:

1. Resynthesize phase-A quad 13's six-register circuit in the PR543 R420 word.
2. Resynthesize an unclaimed phase-B block. PR670 and PR674 already cover blocks
   3 and 5, making this the more crowded direction.
3. Investigate phase-A frame reassignment at quad 13. PR661's fixed-order
   phase-B result does not cover it, but a circuit change gives a more directly
   checkable bounded experiment.

Selected scope: candidate 1, quad `13 mod 60 = 13`, frame 315, original A gates
873 through 891 (zero based), registers 267,347,349,376,467,491. Search only
commutations and three-to-at-most-two XOR rewrites whose forward and reversed
nonnegative transfer matrices are entrywise no larger. Seed 13 also fixes the
nomination order. Stop after 100 restarts of 1,000 attempted rewrites.

Expected deliverable: a finite circuit replacement, exact transfer matrices,
whole-native-word replay and controls, or a scoped failed-search report. No
selected-frontier change and no new kappa without the full supplier pipeline.
Expected finish: 2026-10-13 12:30 Asia/Singapore. Reserve the last quarter of the
session for verification and handoff.

Coordination: GitHub's pinnedIssues query returned no pinned issues; the only
open issue was #650 (requesting Discussions), with no comments. Claim recorded
locally rather than posting to an unrelated issue. PR metadata was inspected
through #685. Relevant ledger, negative results and predecessors read: PR543,
PR589, PR620 (decoder floors, not circuit lower bounds), PR661, PR670, PR674,
and the selected PR626 construction/review. PR661 explicitly excludes circuit
resynthesis; the two circuit PRs change phase B, whereas this changes phase A.

Result: **completed finite circuit improvement**, submitted as
[PR691](https://github.com/CrocSwap/integer-mult-bounds/pull/691). Quad 13 uses
12 gates instead of 19; literal cleanup gives 14 fewer native ADDs overall.
The forward integer matrix agrees, the reverse positive matrix is dominated,
all 660 dirty-input columns restore, frame paths and rank mass 5112 agree, and
all eight rejection controls pass. No new kappa. `VALIDATION.json` records the
bounded checks and unreplayed downstream obligations.

Final metadata refresh covered new PRs through #690 and found no phase-A quad
overlap. PR686 changes D, and PR688 composes phase-B blocks from PR670/674;
neither is imported here. Main still equals the recorded base. This is the
single result update to the local claim; no coordination thread was available.

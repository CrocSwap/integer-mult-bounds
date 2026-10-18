# Sprint scope claim (recorded locally)

No pinned sprint coordination issue exists (checked 2026-10-13; the only open
issue is #650, unrelated), so the scope claim is recorded here, per the sprint
protocol.

- Track and seed: **bit supplier (00-19), OS random seed 8**.
- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631` (origin/main at
  sprint start; selected PR799/PR589, conditional kappa
  0.001661634653669567).
- Object: the phase-B block schedule of PR589's tuned punctured R439 word
  (`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`), section B
  runs at frames 506-509 and 519-524.
- Method: whole-block single-write class (PR #873's formulation) searched by
  a realized-subset dynamic program with meet-in-the-middle donor sums;
  class-infeasibility by two independent exhaustive recursions plus
  order-independent per-row donor-supply certificates.
- Parameter range: all ten phase-B blocks of the word; constructions spliced
  only for frames 506 and 523.
- Expected deliverable: one verified research package
  (`research/r439-bsection-survey/`) with two block shortenings (24,305 ->
  24,289 local ADDs), certified class minima for the feasible blocks, and
  scoped infeasibility certificates for the rest; no new kappa.
- Overlap check at claim time (2026-10-13): open PRs #873 (block 508),
  #843 (block 509), #844 (block 520), #857 (block 523) cover four claimed
  blocks with other mechanisms; #728/#792 cover phase-A mini-nodes. No open
  PR changes frames 506/507/519/521/522/524. Blocks 508/509/520/523 appear
  here only as cross-checks (and frame 523 as a strictly shorter independent
  witness than #857's published 40-gate program).
- Overlap refreshed before submission (2026-10-13): PR #880 (frame 507,
  fixed-factor class, 35 -> 30) and PR #884 (frame 521, factorization class,
  47 -> 31) landed on two surveyed blocks after the search completed; both
  use mechanisms outside the single-write class and are disclosed as
  complementary evidence in README.md. Frames 506 and 523 remain uncovered
  by any open PR except #857's weaker 523 witness.
- Status: completed in session; submitted as
  https://github.com/CrocSwap/integer-mult-bounds/pull/891 (branch
  `research/agent-04-bit-seed08`, commit `bdff756c`). See README.md and
  VALIDATION.md.

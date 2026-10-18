# Sprint scope claim (recorded locally)

No pinned sprint coordination issue exists (checked 2026-10-13; open issues
#650 and #913 are unrelated), so the scope claim is recorded here, per the
sprint protocol.

- Track and seed: **bit supplier (00-19)**, OS random seed **16** (drawn from
  `System.Security.Cryptography.RandomNumberGenerator`).
- Base commit: `007664306fff84fbb1c9a1b4053b69f439764034` (origin/main at
  sprint start; selected #890/#869/#870 with #589 on #555, conditional kappa
  0.001661957774647029).
- Three narrow candidates evaluated during orientation: (a) exact class
  minimality for the frame-521 factorization of merged PR #884; (b) the
  multi-write shear class on frame 523, where the best recorded program (39,
  PR #891) is only a single-write class minimum and PR #857's factor search
  stopped at 40; (c) cheaper synthesis of the literal reverse cleanup
  section C. Seed `16 mod 3 = 1` selected candidate (b).
- Exact object: the phase-B block schedule of PR589's tuned punctured R439
  word (`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`),
  section B at frames 506-509 and 519-524. Because the search is per-block
  and generic over the schedule, the claimed scope widened from frame 523 to
  all ten blocks of this one frame schedule, which the track allows ("one
  specific circuit, frame schedule").
- Method: deterministic three-phase search (6,000 min-excess greedy
  reductions with random tie-breaks, 4,000 uniform random legal
  trajectories capped at 90, one width-6,000 beam below the incumbent) over
  the full multi-write shear class = legal nonnegative row/column
  subtraction paths from each block's transfer matrix to the identity.
  Seeds `20261013 + frame` per block; all trials complete; no adaptive
  stopping.
- Parameter range: all ten phase-B blocks of the pinned word; all ten
  spliced into the verified word.
- Expected deliverable: one verified research package
  (`research/r439-bsection-multwrite/`) with per-block replacement programs,
  a spliced word, exact bills and bounds, and scoped search-coverage
  statements; no new kappa.
- Overlap check at claim time (2026-10-13, before the search ran): open PRs
  #857/#873/#880/#884/#906/#908/#914/#923 hold per-block claims on frames
  507/508/519/520/521/522/523/524; merged PR #891 holds the single-write
  minima for 506/508/523. All use bounded randomized or fixed-factor
  classes; none claims a class minimum in the full multi-write class and
  none covers all ten blocks with one search. A second, independent method
  on the same schedule is intended: complete-class coverage and strictly
  shorter programs, with every competitor's number reproduced only as a
  comparison row.
- Status: completed in session; branch `research/agent-10-bit-seed16`, commit
  `8f878062`; submitted as
  https://github.com/CrocSwap/integer-mult-bounds/pull/1015. Result:
  388 -> 262 phase-B gates; 24,305 -> 24,053 complete local ADDs; nine of
  ten blocks improve on every recorded claim, frame 520 does not beat open
  PR #923. See README.md and VALIDATION.md.

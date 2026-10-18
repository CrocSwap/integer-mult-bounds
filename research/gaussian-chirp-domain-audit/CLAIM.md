# Sprint claim: Gaussian chirp domain and block budgets

- Track: adversarial mathematical audit; OS-random assignment seed **64**
  (`secrets.randbelow(100)`, drawn 2026-10-13 03:37 UTC).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claimed at: 2026-10-13 03:43 UTC. Expected finish: 04:17 UTC.
- Exact object: the hypotheses, integer windows and precision budgets of
  `lem:chirped-gaussian`, as inserted by `scripts/make_fast_gaussian_patch.py`;
  compare the domain caveat in PR #371 at
  `988ef67986c313445936fc7103908b6163b9d47e`.
- Method: follow generated source rather than the unmodified upstream header;
  derive rational uniform bounds and use a separate standard-library checker
  for bounded integer cases and deliberately invalid controls.
- Deliverable: one source-pinned audit note, reproducible exact checker and
  receipt. No new kappa or full analytic/tape theorem claim.
- Time allocation: 40 minutes from 03:37 UTC; orientation ends before 03:45,
  verification and handoff begin no later than 04:07.

## Selection and overlap

Three narrow candidates were considered, ordered as follows:

0. Recheck the missing exact infeasibility evidence behind PR #620's P111
   decoder floor. The review already identifies absent proof logs and
   nonportable scripts; a portable solver audit would need more setup.
1. Audit the Gaussian chirp domain and block budgets left conditional in
   PR #371. This is an older unreviewed contribution with a small exact seam.
2. Audit the normalized zero/power-of-two boundary in PR #573's eight-tape
   handoff. The sources have substantial scoped Lean checks already.

Seed `64 % 3 = 1` chooses candidate 1. It also determines the finite residue
sampling order; the claim is useful because it checks a different obligation,
not because it uses a different random seed.

At selection, GitHub returned 491 open PRs. The central ledger marks #371
unreviewed. Its final-grid counterexample and correction are predecessor work,
not claimed here. PRs #479, #481 and #489 address different Gaussian mechanisms.
The repository had no pinned issues and its sole open issue was #650
(Discussions), so this claim is recorded locally. Pinned issues and #371's
head/comments were refreshed immediately before recording the claim.

## Result update

Pending verification and handoff.

# Sprint claim: R439 phase-B frame 522

- Track: bit supplier; OS assignment seed **17**, drawn with
  `secrets.randbelow(100)` at 2026-10-13 11:21:12 UTC.
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`, also the live
  upstream `main` head returned by the GitHub connector. Git fetch could not
  connect to the environment proxy; the existing full checkout matches that
  independently fetched commit. Work is in an isolated worktree/branch.
- Selected result inspected: PR799/PR589, conditional
  kappa `1661634653669567/1000000000000000000`; source manifest, construction,
  review, CONTRIBUTING and review ledger inspected.
- Three candidates considered: (1) PR589 fixed-word frame reassignment, already
  covered by open PR886; (2) one additional P112 decoder total, covered by
  PR845 and related copy-floor work; (3) full positive-integer factorization
  of PR589 phase-B frame 522, selected here. Seed 17 modulo the ten B blocks
  selects index 7 (frame 522), not a fresh run on an already covered block.
- Exact object: B[361:404] of
  `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, 43 additions
  on 12 registers, with rebuilt literal reverse C cleanup.
- Method: bounded seeded row-subtraction factorization of the exact integer
  block map, allowing multiple writes/intermediate donors. Check full integer
  map, arbitrary dirty Boolean inputs, frames, positive prefix bounds and
  paid profile; admit no extra helpers or source access.
- Budget: at most 12,000 trajectories, stop early only for an explicit resource
  limit and report completed coverage. A shorter local program cannot improve
  the unchanged paid recursive profile or complex-bound kappa; it can reduce
  native ADDs. Full-word accounting is required before claiming that saving.
- Expected deliverable: one finite circuit with exact verification and negative
  controls, or a scoped search report if the candidate cannot meet the budget.
- Finish by 2026-10-13 12:21 UTC; reserve the final fifteen minutes for checks
  and handoff.
- Overlap: open PR891 surveys a whole-block single-write class and excludes
  frame 522 in that class. Repeated writes are a strictly different search
  class. PR873 covers frame 508, PR857/891 frame 523, PR880 frame 507,
  PR884 frame 521, PR843 frame 509, and PR844 block 4. PR792/728 alter
  phase-A mini-nodes. Their circuits/savings are not combined into this task.
- Coordination: issue search found only open issue 650 (request to enable
  Discussions), with no comments and no sprint claim thread. Claim recorded
  locally; no reservation issue opened. Latest PR metadata inspected through
  PR901, and a separate frame-522 search found no result.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. No subagents.
Apache-2.0, retaining the supplier lineage's attribution.

## Result update

Completed one finite bit-circuit construction: frame 522 falls from 43 to
33 ADDs; with literal reverse cleanup, the complete local word falls from
24,305 to 24,285 ADDs. The integer block map, all 661 frame paths, nine copies
and paid mass 5,129 are preserved. Full reverse positive bound falls to
1,045,786; payload remains 93 bits. No new kappa is claimed.

The 12,000-trial search completed (492 identity factorizations, seven with
33 ADDs). Exact Python, optimized/relocated replay, eleven mathematical and
six package controls, fresh native legality/5/9/11-stage checks on both words,
96 omitted-bridge controls, receipt regeneration and selected-record checks
pass. Reproduce with `python3 -I -B research/r439-block522-factor/verify.py`.

Final overlap inspection through PR904 found its one-ADD replacement of the
four-register B[380:384] subinterval. This contribution's ten-ADD whole-block
replacement is distinct. Its certificate is unchanged at refreshed head
`883a0bdf7792693e57c16be660824b57aacfbe05`; attribution and non-composition are
recorded in README.md. A later successful `git fetch upstream main` confirms
the same exact base `f567884aeb8851b6e794af1184119a3bfbe1e631`.

[Published contribution branch](https://github.com/CubeJerry/integer-mult-bounds/tree/research/r439-block522-seed17-112112/research/r439-block522-factor).
Upstream PR creation was denied with HTTP 403 / "Resource not accessible by
integration" through both the GitHub connector's REST call and the existing
authenticated CLI's GraphQL call. No PR was created. The clean patch and
prepared PR description are provided in the local handoff; the published
branch is ready for review/submission. No coordination issue exists to update.

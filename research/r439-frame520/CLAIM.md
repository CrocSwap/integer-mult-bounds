# Local sprint claim

- Track: bit supplier; OS-random assignment seed **05** (`secrets.randbelow(100)`).
- Exact base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
- Claimed 2026-10-13 12:39 UTC; expected finish 13:15 UTC (2026-10-14 00:15 Melbourne).
- Object: selected PR589 R439 word, phase B frame **520**, `B[242:283]`,
  a 41-ADD, 12-register block, plus its required literal reverse cleanup.
- Method: bounded whole-block nonnegative-integer factor synthesis on the same
  ordered registers; retain exact forward integer transfer, explicitly price
  reverse growth, and check all dirty inputs and frame paths. At most 5,000
  seeded elimination trajectories; stop with a checked strict improvement or a
  scoped report. No changes to copied information or selected frontier.
- Deliverable: one exact finite circuit and verifier with accounting and negative
  controls, or concrete bounded negative evidence; no new kappa claim.
- Three candidates considered: whole-block frame 520 synthesis (chosen), frame
  509 source-sum reuse (already PR843), and target-basis D compensation (PR915).
  Seed 05 selects block index 4 through `(seed - 1) % 10`; the actual distinction
  is an unclaimed whole-block integer map, not the seed alone.
- Coordination: no pinned issues returned by GitHub immediately before claiming.
  Relevant open PR metadata inspected: #873/#880/#884/#857/#891/#906/#908/#914
  concern other whole blocks; #904 covers up-to-four-wire windows and #915 the
  D prefix. Compare #904 on this block before submission. #886 already closes
  frame-only changes: this claim changes the scalar program instead.
- Workers are restricted to this one block and its validation. No separate issue
  was opened; this local claim substitutes for a pinned coordination comment.

## Result update — 2026-10-13 12:59 UTC

Submitted [PR923](https://github.com/CrocSwap/integer-mult-bounds/pull/923):
**29 ADDs instead of 41**, plus literal reverse cleanup, gives **24 complete
local ADDs saved**. The all-state overlap review found Gautam Gupta's closed
PR844 (31 ADDs); this result adds **four complete ADDs** beyond that predecessor,
whose original certificate is retained and replayed. PR844's initial failed
mixed-factor search is explicitly credited; the new necessary diagonal guard
prunes branches unable to reach identity, without claiming a new feasible class.

Full local matrix/dirty-column/frame/interface/cost checks, nine controls,
12 package tests, unchanged native 5/9/11-stage checks with 96 bridge controls,
search regeneration and selected-record integrity passed. Exact receipts and
coverage limits are in README.md and VALIDATION.md. No new kappa, global hosted
repricing or full multiplication proof is claimed. No pinned sprint issue
exists, so this single local result update is the coordination handoff.

Implementation commit: `76d3fde8` (the subsequent commit only adds this result
update). The PR remains open for independent review; no merge was performed.

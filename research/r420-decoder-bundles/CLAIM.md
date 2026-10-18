# Local sprint claim

- Track: bit supplier. Assignment seed 19, drawn with Node crypto.randomInt(100), backed by operating-system randomness.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13 04:49 UTC. Expected finish: 05:30 UTC. Final verification begins no later than 05:20 UTC.
- Object: the nine FULL-frame phase-A decoder totals of eumemic's PR543 R420 bit word.
- Hypothesis: restored bundles of at least three non-retained operand registers can improve on the disjoint-pair mechanism in PR708, after paying preparation, restoration and literal reverse cleanup.
- Method: exact enumeration of small bundles, followed by one bounded disjoint selection. Preserve every frame path and arbitrary dirty inputs; recompute positive scalar growth. Seed 19 fixes tie ordering.
- Deliverable: one frozen circuit and exact verifier, or a scoped negative result if the paid budget fails. No new kappa claim.
- Three candidates considered: phase-B block resynthesis, phase-A quad synthesis, and decoder bundles. PR670/674/688 cover block rewrites and PR691 covers quad synthesis. Bundles change the search class beyond PR708's pair matching.
- Coordination check: GitHub pinnedIssues returned an empty list; no separate issue opened. Open PR metadata inspected through PR720. PR708 is the direct predecessor and will be credited and pinned; PR686/694 cover frame-zero compensation, a different circuit.
- Contributor: Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex assistance. Apache-2.0.

## Completed result, 2026-10-13 05:07 UTC

[PR753](https://github.com/CrocSwap/integer-mult-bounds/pull/753) contains one
finite bit-circuit construction. Eleven restored stars save 128 native ADDs,
including every preparation/restoration and literal cleanup, preserving the
complete A operator and D. The nine-stage C++ replay passes 1,380 columns and
18/18 omitted-bridge controls for both words; payload grows from 100 to 103 bits,
below 104. No new kappa or complete hosted invoice is claimed.

The initial optimistic three-operand screen was replaced by exact partial-row
accounting, giving additive star-edge costs. The single accepted nomination
covers all 6,320 oriented edges on 80 operands, then one seed-19 greedy star
packing; its frozen coverage and stopping rule are checked. A three-register
witness separates stars from disjoint pairs on the same registers.

Final overlap refresh through #751 found no duplicate fixed-A decoder-star
contribution. PR708's head remained `2ec522a466ec448f148d4355dc43b51c0ef1e0b5`.
PR748 at `0ccc0b425d2b9667108d3a0918a5cfa0aa7a5861` has larger savings via a
changed dirt map and recomputed D; it is credited rather than superseded.
PR733/742 change D bases. Their savings are not added here. Main remained at
the exact base above and the pinned-issue query was still empty.

Implementation and nomination were frozen before the final review and handoff.
Final verification included a relocated minimal archive, eight built-in controls,
an altered-coverage rejection, selected-record integrity, and staged whitespace.
The separate AI review's metadata-binding and proof-wording findings were fixed.
Full hosted/outer assembly, repository-wide verification, remote CI and full
theorem formalization remain outside this contribution.

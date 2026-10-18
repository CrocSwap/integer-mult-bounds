# Local sprint claim

- Track: complex supplier; fresh OS-random assignment seed **31**, generated
  with Python `secrets.randbelow(100)` on 2026-10-13.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: consecutive same-source additions in the selected #626 JP8
  `full_frame_cleanup`, keeping the existing operation order and frame 1.
- Hypothesis: between different odd numerators, a positive unit source read
  bracketed by dyadic shifts can cost less than clearing and rebuilding the
  existing private coefficient stream.
- Method: enumerate routes `w *= 2^u; w += x; w *= 2^v`,
  `-16 <= u,v <= 16`, alongside existing power-of-two reuse; charge every
  source read, shift, accumulation and boundary clear. Admit only routes
  within the original positive prefix envelope and strictly cheaper than
  reset. Stop after this finite route class and the exact replay.
- Deliverable: executable finite construction, exact full scalar-projection
  replay, source pins, cost certificate, negative controls and scoped note.
- Expected finish: 2026-10-13 06:40 UTC; hard handoff before 06:54 UTC.

Three narrow candidates were considered: (0) CK cleanup additive transitions,
(1) JP8 cleanup additive transitions, and (2) private-center quarter-coefficient
factoring. Seed `31 % 3 = 1` selected JP8; #786 already covers candidate 2
and reports a larger conservative local invoice. The additive transition
class differs from #739's power-of-two-only reuse and its explicitly excluded
odd-numerator transitions. #769 covers CK power-of-two ladders; #793 instead
permutes commuting frame-zero compensation. #722, #734, #751, #755 and #787
cover equal-magnitude reuse, individual signed Horner circuits, target fan-in,
other phases, or composition. None of their implementations is imported.

Before claiming, read the selected record, construction/review, contribution
instructions, review ledger and preserved-research index. Checked open PR
metadata through #799 at 05:53 UTC. GitHub returned no pinned coordination
issue; the only open issue was #650 about Discussions. This file records the
claim under the requested fallback. No separate reservation issue is opened.

Contributor: Ryan Haines (@Ryan-Haines), with substantial OpenAI Codex
assistance. New material is Apache-2.0. Result and handoff will be recorded
once after verification.

## Result and handoff

Completed: [PR #811](https://github.com/CrocSwap/integer-mult-bounds/pull/811).
The 269 positive one-read transitions save 2,784 real primitives beyond the
power-only comparator; total forward saving is 32,810 (257,232 to 224,422).
Both orientations pass literal replay on 725 arbitrary columns. Independent
integer enumeration covers 849,420 exponent pairs and 6,776 block input
columns. Windows and Linux, optimized/relocated/recompressed replay, 12+4+25
mutation controls, four packaging tests, Ruff and selected-record integrity
pass. The unchanged backward maximum leaves the local invoice unchanged;
no new kappa is claimed. README.md gives the reproduction command and limits.

Final overlap refresh: 629 open PRs through #810 at 06:08 UTC, plus renewed
confirmation of no pinned issue and unchanged `origin/main`. New #807
changes CK helper bases; #809 changes a historical center basis. Neither
examines fixed-order JP8 cleanup numerator transitions. Source/comparison
heads for #739 and #793 are pinned; no pending implementation is imported.

The initial research commit is `e80c08f`; this final claim update records the
result once. A clean patch and short handoff are also retained in the local
workspace as `jp8-additive-s31.patch` and `jp8-additive-HANDOFF.txt`, including
the final commit and verification command. This local claim is the requested
coordination fallback because no pinned sprint issue exists.

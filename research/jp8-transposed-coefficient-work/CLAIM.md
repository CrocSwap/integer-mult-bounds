# Local sprint claim: transposed private work

- Track: complex supplier; fresh OS-random seed **25** (`secrets.randbelow(100)`).
- Exact base: `c290b7b919790300e14004a75d8d24b55ca3c5b5`.
- Current accepted result: #741/#589, conditional kappa
  `1661202643272239/1000000000000000000`; read its certificate, construction
  and maintainer review. This experiment deliberately uses historical #626.
- Exact object: the inverse-transpose companion of the fixed-source JP8
  cleanup blocks constructed in #811, including varying magnitudes and
  positive numerator-changing source reads.
- Method: transpose each literal private-work circuit in reverse order,
  reverse the sign of updates into the original source, and check all dirty
  native/private inputs, complete prefix envelopes and all costs. Compare
  with #751's equal-coefficient reverse-Horner result. No larger search.
- Deliverable: standalone pinned companion construction, finite exact
  certificate, independent block check, negative controls and cost note.
- Expected finish: 06:45 UTC on 2026-10-13; handoff before 06:54 UTC.

Three candidates: (0) CK numerator-changing forward reuse; (1) JP8
inverse-transpose continuation; (2) transport coefficient reuse into #741.
Seed `25 % 3 = 1` selects the second. Candidate 0 repeats the recent forward
mechanism; candidate 2 requires a wider interface audit. This claim concerns
the backward dual, not another forward coefficient search.

Checked open metadata through #811, #751 at
`7a1a3a319da359ec8b6e83230a7fcf7733fac8e5`, #739, #793 and the review ledger.
#751 handles 999 equal-magnitude fan-in runs; #739/#811 report no backward
same-source join. This extends the backward circuit class to the transposes
of their varying-magnitude continuations. #793 changes compensation order.
There is no pinned sprint issue; the issue list only contains #650 about
Discussions. This file is the local coordination fallback. #811 will be
pinned at its completed historical-assembly update, with full attribution.

Contributor: Ryan Haines (@Ryan-Haines), with substantial OpenAI Codex
assistance. Apache-2.0. Result and handoff will be recorded once after checks.

## Result and handoff

Completed: [PR #830](https://github.com/CrocSwap/integer-mult-bounds/pull/830).
All 1,091 backward companions pass; complete backward count is 224,470,
saving 32,810 real primitives and 13,122 beyond #751's equal-coefficient
result. Paired counts are 224,422/224,470. Exact complete prefixes remain
64/101 bits, while 377 isolated prefixes grow (worst ratio 40/9), explicitly
recorded as a limit on blanket transposition arguments. No new kappa.

Literal replay covers 725 arbitrary columns in both orientations; the
independent integer checker covers 6,776 block input columns and the full
backward prefix recurrence. Windows/Linux, 10+4+25 mutation controls, five
optimized/relocated/recompressed packaging tests, Ruff, Git-byte source pins
and current selected-record integrity pass. README.md gives the commands.

Final overlap refresh: 638 open PRs through #825 at 06:33 UTC; no new
transposed-coefficient/fan-in claim was present. #816 is a CK target forest;
#821 audits a global prefix estimate, a different object. #811 and #751
remain at the pinned heads. No pinned coordination issue exists. Main
advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; all six consumed
input files are unchanged, and the selected #741 frontier remains separate.

Initial research commit: `0a5e2034c0d537c05a2cc3bb45f5d35ae0e3a668`.
This is the single final claim update. The local workspace also retains
`jp8-transposed-s25.patch` and `jp8-transposed-HANDOFF.txt`, with the final
commit, patch hash and reproduction command, as a submission-independent
handoff. No issue was opened merely to reserve this scope.

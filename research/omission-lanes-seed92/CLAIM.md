# Packed literal omission replay

Claimed 2026-10-14 00:33 UTC. Verification engineering, OS assignment seed 92
from `secrets.randbelow(100)`. Base
`cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`.

Object: the 5,563 complete literal mutant replays in
`research/r439-omission-atlas-seed81/verify.py`, retained from woklerx's PR1017.
Test 64 independent omission executions in disjoint integer bit lanes. The
batch size is `2 ** (4 + 92 % 3)`; it is a bounded implementation choice, not
evidence of novelty. Preserve every prefix and suffix gate, all 661 symbolic
inputs and outputs, the independent factor comparison and all existing controls.
No factor-derived mutant maps, sampling or shared mathematical assumptions are
introduced by the packing.

Expected deliverable: an opt-in source-pinned replay, exact equivalence and
corruption controls, same-input baseline/optimized timings and a focused tooling
PR. No new kappa. Finish by 01:07 UTC; verification/handoff by 00:57 UTC.

Three candidates considered:

1. P112 Gram spectrum polynomial evaluation, rejected as a small target after
   the full existing replay took 0.283 seconds here.
2. T37 independent endpoint evaluation, already documented as about 2 seconds;
   logarithm/exponential tooling has substantial existing overlap.
3. R439 omission replay, selected after an unchanged 2.249-second execution and
   profiling showed 5,565 literal replay calls dominating the check. Independent
   bit lanes preserve its complete literal coverage.

At 00:33:18 UTC the repository overlap helper reported complete pagination of
783 open PRs and 143 discussion records, 326 local records, no warnings, and
only the predecessor README for the terms `r439-omission-atlas`, `packed omission`
and `literal mutant`. Also inspected the review ledger, selected #1094 review,
open tooling PRs, negative-result guidance and recent discussion claims. No
pinned coordination issue exists, so the claim is local. No novelty theorem is
inferred from the search. The selected record remains conditional and unchanged.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance. Apache-2.0.

## Completed result, claim released

2026-10-14 00:47 UTC. The 64-lane trial was slower; the bounded 16/32-lane
follow-up selected 16. Final full-audit medians are 2.167 seconds literal and
1.490 seconds packed, a 1.45x speedup on macOS arm64 CPython 3.14.8. All 5,563
661-by-661 mutant matrices, complete certificates, 1,564 short/boundary words,
seven inherited and thirteen new controls agree or reject as required. The
Python 3.12 registered replay and Python 3.11 optimized relocation also pass.
See the [result package](https://github.com/thakrarsagar/integer-mult-bounds/tree/tooling/cycle17-seed92-packed-omission/research/omission-lanes-seed92).

Final overlap refresh at 00:45:48 UTC covered 792 open PRs, 149 discussion
records and 328 local records with complete remote pagination and no warnings.
Only the predecessor matched the three declared terms; no competing tool was
found. Main advanced to `410026dc5513b87db92ae98571d1d5984c69a983`, and all five
live source inputs are byte-identical there. Original source/base pins remain.
The focused result adds an opt-in exact implementation and equivalence evidence
to PR1017, with no new kappa, native/hosting replay or full theorem claim.

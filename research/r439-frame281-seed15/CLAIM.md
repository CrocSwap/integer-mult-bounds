# Bit supplier sprint claim, seed 15

- Assignment: first operating-system cryptographic random draw, rejection sampled
  uniformly from 0 through 99, was **15** (bit supplier).
- Exact base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
- Claim recorded: 2026-10-13 15:34 UTC; target handoff: 16:18 UTC.
- Object: complete six-register phase-A frame **281** (quad 15) in the R439
  bit word; compare the selected PR589 word and the retained PR952 candidate.
- Method: bounded exact nonnegative row-subtraction synthesis for the fixed
  positive transfer, with repeated destination writes, followed by independent
  matrix replay, dirty-column and paid-frame checks. This differs from PR952's
  bounded pivot-order Boolean elimination scan and PR925's frame-267 matrix.
- Expected deliverable: one source-pinned finite circuit improvement or scoped
  exact class boundary, a reproducible checker, negative controls and attribution.
- Budget: one matrix, at most 1,000,000 discovery states initially; one
  evidence-driven pivot allowed within this same frame. Final quarter reserved
  for independent verification, overlap refresh and handoff.

Three candidates considered: (1) frame281 fixed-transfer synthesis (chosen by
seed15 among the 60 complete six-register phase-A frames); (2) another phase-B
fixed-factor schedule (declined because the ten blocks have recent direct
contributions); (3) multi-helper D compensation (declined because PR965/967
already investigate coupled helpers and restored stars). Existing PR933 closes
the selected word's relocation/Steinberg class; this claim changes the full
six-wire circuit instead. PR904/936/952 prefix results and PR925 are predecessor
work, not imported savings unless explicitly replayed and compared.

The issues page at claim selection showed only issues #913 and #650 and no
pinned sprint coordination issue. No reservation issue was opened. Public
Curiosity Bot searches checked recent bit/frame PRs and frame281 references;
the local claim is used as requested. No selected frontier or upstream edit.

Selected result at the base: PR942, conditional kappa 0.001661960547713947,
complex-bound, retaining PR589 on PR555. This task does not promise a new kappa.

Prepared for contributor @woklerx with substantial OpenAI Codex assistance.

## Result update (2026-10-13)

Completed the single evidence-driven pivot to PR952's distinct frame281
integer transfer after detecting that the initial selected-word matrix is
conjugate to PR925's prior result. The final 12-ADD circuit saves two complete
local ADDs, including cleanup: 23,673 -> 23,671. Two different exhaustive
implementations establish the fixed-transfer minimum12 and reverse-envelope
minimum13. Exact source/dirty-column/exported-record checks pass; native C++
and full make verification remain unavailable in this environment.

Final overlap refresh inspected concurrent PR980 at
`ba1cf68bef0c97dfb120add04304e2de0db6f29c`: its frame281 still has the same
13-ADD transfer. Its general admission method is credited separately and its
other block savings are not composed here. All workers stayed within this
frame's discovery, independent proof, replay or review scope.

Reviewable result:
[frame281 package on the submission branch](https://github.com/woklerx/integer-mult-bounds/tree/research/seed15-bit-supplier/research/r439-frame281-seed15).
One focused upstream PR is the handoff; no merge or selected-frontier edit.

# Targeted T16 whole-helper repacking

Conditional candidate kappa **0.001672653061493085**, **+0.0001101589%** over PR1074 (0.001672651218919025). A twelve-bin whole-helper repacking moves idle ranks 2 and 3 into a rank-5 remainder while preserving the scalar word, role widths and source-event times.

Published as a draft first, then passed the complete publication-package replay through the unchanged PR1074 strict verifier. All 69 admission controls, 12 bit controls, 15 controller mutations, six independent owner controls, two exact moment engines and 47 outer inequalities pass. The finite witness changes 30 role placements. VALIDATION.json records the local evidence. Hosted CI remains separate; this reuses the checked PR1018 native baseline and PR1005 chain rather than rebuilding the full ancestry.

All-size/compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer and PR589 bit H1-H5 assumptions remain. No unconditional theorem, global optimum or Lean claim.

Credit PR1074 and preceding owner-packing work by jeremykothe2 with Claude assistance; FanPUYen PR858; PR1018 including rohanarun PR987; PR1005; NewBArch PR869 and the retained PR799/741/685/645/589 lineage. Prepared by Rohan Arun with substantial OpenAI Codex assistance; new material Apache-2.0.

## Replay

Python 3.12+; use the pinned dependency checkout accepted by PR1074 and the checked PR1018 native local replay on the PR1005 chain.

```sh
python3 -B research/complex-t16-targeted-repacking/verify.py --main /path/to/pinned-dependencies --local /path/to/checked-slots/local --work /path/to/fresh-output
```

The archive preserves all 179 original source files and notices. Only the three frozen data files are overlaid. The unchanged original verifier checks the full conditional finite assembly; reused native ancestry is not a full cold rebuild.

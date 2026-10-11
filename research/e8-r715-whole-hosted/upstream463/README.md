# E8 bit word R715: carrier lower bound plus F2 overlap cancellation (draft snapshot)

**Status: draft.** The word is independently validated, and its bit supplier is computed exactly. The full package is in progress: the eleven-stage assembly with a complex supplier, the fresh-copy verify, and an independent audit.

## What changed (relative to the R740 word of the #443/#444 lineage)
1. **Carrier lower bound (proved).**
   - The 63 lines of each target's E7 cap form a spherical 4-design, so no two hyperplanes contain them all. Two consequences:
     - every target needs ≥ 2 registers reaching its hyperplane, so R ≥ 240 for those registers (tight);
     - every source needs ≥ 3 registers holding it, so carriers ≥ 240.
   - The R740 word used 272 carriers, because frame sources used 7 chains each.
   - Rebuilding each D4(c) as Bcw plus two frame-pair sums (the 12 pairs in one block's 3 parallel classes) brings the carriers to exactly 240. That costs 16 extra copies.
2. **F2 overlap cancellation** ("total minus complement", after Alman–Rao).
   - Needed rules are re-expressed as x⊕y of existing symbols, so shared frame lines cancel: 8 true cancellations and 3 overlap-free re-associations.
3. **Stack:** R 740 → **715** (not additive: 724 from (1) alone, 729 from (2) alone).

## Exact results (bit supplier, eleven stages, whole-residual #442-style hosting; no cross-family split, cf. #451)
| word | bit c |
| --- | --- |
| R740, same pipeline | about 1.2649e-3 unmixed |
| R729 / R722 | 1.27445e-3 / 1.28141e-3 (mixed) |
| **R715 (mixed)** | **1.28512873989e-3**, vs #454/#460's bit c ≈ 1.2757e-3 (+0.74%) |

Paired with #458's lemma-less complex supplier (b = 1.2972e-3), κ is bit-bound at about 1.2835e-3. That is roughly +0.71% over #460 (1.274416e-3). It is **not yet certified**; it comes from the exact bit c and the outer formula κ = (1−η)c/(1+c).

## Independent validation (separate agent, `validation/`)
- **F2 checker:** PR #370's checker, with only its two frame-0 asserts relaxed for kernel words, passes: 955 columns on the pre-kernel word, and the kernel and mixed words. It rejects a dropped gate and a non-nested frame.
- **C++ checks:**
  - legality: PASS;
  - columns_h: 1195 columns, PASS;
  - columns_k5 (eleven-stage): 1915 columns, 24/24 bridge controls rejected;
  - mutate_records: 6/6 rejected;
  - Gram: 969 frames, PASS.
- **Rekid legality:** every re-expressed rule is acyclic, XOR-correct, frame-nested and inside its cap, with 4 negative controls.
- **Mixing:** byte-identical regeneration; 4 stock mutants and 2 extra mutants rejected.
- **Tape:** recomputed independently: R=715, W=1200, rank mass 93192, deficit 408, and c as above.

## Pending
- the eleven-stage assembly with a complex supplier (#458's), certified κ, and next-grid rejection;
- `verify.py` and two fresh-copy replays;
- an independent audit.

## Credits
- #370 (Dylan Crow), #443–#445 and #451/#454/#458 (chafreaky), #442 (DaysSky), #436/#453/#460 (rohanarun), #448 (higherbeing), #425/#386 (jacklightChen);
- #450 (ours: target mixing, eleven-stage tools);
- Jacob Sussman (gx, the E8 unit);
- Alman–Rao for the cancellation idea.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

# T16 whole-helper exchanges: conditional kappa 0.001672267698427438

This changes only the owner map of PR1050 (kappa 0.001672241870811633), with an improvement of 0.00154449%. Repeated two-role exchanges and two-for-one whole-helper exchanges concentrate idle remainder ranks. The local word, helper widths, call order, and source-event times are unchanged. RESULT.json records every changed placement relative to the exact parent.

The parent construction and code are credited to PR1050 and its PR1022/1028/1031/1042 lineage, FanPUYen's PR858 controller, PR1018's seven slots including rohanarun's PR987 search, PR1005's leaver cells and frames, NewBArch's PR869 and the retained PR799/741/685/645/589 suppliers. The original 180-file package is preserved byte for byte in upstream1050.tar.gz, including its notices. Only OWNERS, PLAN and SPEC are overlaid for replay. No verifier checks are changed.

## Reproduce

Python 3.12+ and the same pinned dependency checkout and completed PR1018 local replay accepted by PR1050 are required. First run PR1005's documented chain and PR1018's verify_slots.py, or reuse completed checked outputs as those packages permit. This package verifies the same dependency hashes and local bindings through the unchanged upstream strict driver.

```sh
python3 -B research/complex-t16-owner-exchanges/verify.py --main /path/to/pinned-dependencies --local /path/to/checked-slots/local --work /path/to/new-output
```

Expected: PASS_T16_WHOLE_HELPER_EXCHANGES 0.001672267698427438.

## Verification status

The candidate passed the original strict verifier locally: all 69 admission controls, 12 bit controls, 15 controller mutations, six independent owner controls, exact moment and 47 outer checks. The local baseline was rebuilt and checked earlier; this is not a new cold ancestry rebuild. The publication wrapper passed a fresh local replay after draft publication, reproducing the complete strict result. Hosted CI and Lean are not claimed.

All-size/compiler, common-label and mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer and the retained PR589 bit H1-H5 assumptions remain. This is a finite conditional witness, not an unconditional multiplication theorem or a global packing optimum.

Prepared by Rohan Arun with substantial OpenAI Codex assistance. New material is Apache-2.0; upstream attribution and licenses are retained.

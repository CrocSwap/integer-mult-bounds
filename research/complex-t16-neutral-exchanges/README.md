# T16 neutral reshuffles and whole-helper exchanges

Candidate conditional kappa **0.001672285678298543**, above PR1056's **0.001672267698427438**. Equal-width reshuffles preserve the paid profile while changing which improving exchanges are legal. A 500-swap reshuffle (seed 4286363695) followed by whole-helper exchanges found this map. This is a finite witness, not an unrestricted or neighborhood-optimal packing claim.

Published as a draft first; the full strict publication-package replay now passes. All 69 admission, 12 bit, 15 controller-mutation and six independent owner controls pass, with two exact arithmetic engines and 47 outer inequalities. This improves PR1056 but is below the subsequent PR1061 claim (0.00167259071506618). Frozen OWNERS, PROFILE and PRICE retain the original candidate; data/ holds its independently measured PLAN and SPEC. The PR1050 source archive and all its notices remain byte-exact. Only the three frozen data files are overlaid; no verifier checks are altered.

## Reproduce

Python 3.12+, the pinned dependency checkout accepted by PR1050, and the completed checked PR1018 local replay on the checked PR1005 chain are required. This uses the same baseline-reuse contract and checks their source/artifact bindings through the unchanged upstream strict driver.

```sh
python3 -B research/complex-t16-neutral-exchanges/verify.py --main /path/to/pinned-dependencies --local /path/to/checked-slots/local --work /path/to/new-output
```

Expected: PASS_T16_NEUTRAL_EXCHANGES 0.001672285678298543.

All-size/compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer and PR589 bit H1-H5 assumptions remain. No unconditional theorem, full cold ancestry rebuild, Lean or hosted CI success is claimed.

Credits PR1056/1050 and preceding owner maps, FanPUYen PR858, PR1018 including rohanarun PR987, PR1005, NewBArch PR869 and all retained supplier notices. Prepared by Rohan Arun with substantial OpenAI Codex assistance; new material Apache-2.0.

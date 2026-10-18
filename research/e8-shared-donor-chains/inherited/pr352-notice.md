# Attribution and provenance

Prepared by DaysSky, assisted with Claude. Apache-2.0 (see `LICENSE`) applies to the new code and to the inherited Apache-2.0
code below; third-party notices are preserved where files are vendored.

- **Complex supplier: the E8 unit** (`code/complex/inputs/e8/`): Jacob Sussman, jacobalansussman/wht-power-saving-lean
  at `9c94857bbaee886f8649edee0bc2d3c738f9555e` (Apache-2.0, Copyright 2026 Jacob Sussman; his `LICENSE` and `NOTICE`
  are vendored beside the files). The certificate `tools/certificate/gcert1-e8-r783.json.gz`, the 24 Lean modules and
  the comparator configuration of his kernel-checked theorem `wht_main_block_B2Ge8x`, his Lean-data generators
  (`tools/gx/{gxgen,gxrate,gxbind,gxunit,gxcore,gsmirror,gxpaths,regen_check,regen_check_e8}.py`,
  `tools/gen/{foldlib,foldgen,gen_rates,gen_sharp}.py` and templates) and his stand-alone `tools/e8/replay.py` are
  vendored byte-identical and sha-pinned in `code/complex/inputs/complex/source-pins.json`. His README credits
  devices from this repository in the unit: slot reuse with a compensating read (jamesyc #124, eumemic #143), late
  pairing (Chafik Boukhalfa #200/#233), the in-place pair (icekylinx #184, carried in ikeboy's #191/#193).
- **Bit word, Design T, twin condensation, checkers and engines** (`data/bit/`, `code/builders/`, `code/checkers/`,
  `code/pricing/`, `code/export_p10.py`, `code/stage_cohort.py`): unchanged from LJH-217's PR #346 at
  `11b4de5ff8ed5fccf55d4af1043358d257308e8e`, which builds on DreamingOfClouds' PR #325 p10b word and PR #315 engines
  (#285/#276 gen5/gen4 lineage on eumemic's PR168 generator and source527 package, PR #200's physical rules, hcg890
  and Jacob Sussman's five-stage architecture, Evan McKinney's completed banks), utcorvusvolat-dotcom's w3 Design T,
  twin condensation and verifier (PR #310) and PR #266's official checkers. See PR #346's notice for detail.
  `json.hpp`: Niels Lohmann, MIT license in its header.
- **Complex checks** (`code/complex/portable_complex.py`, `code/complex/code/`, `code/complex/inputs/complex/`):
  PR #315's portable complex checks as ported to p = 10 in PR #346 (#256/#233/#202/#200/#194/#184 lineage:
  icekylinx, Chafik Boukhalfa, Avi Eisenberg, eumemic and others). Jacob Sussman's `gx.check1`, `gxcore` and pinned
  Lean chain sources under `code/complex/inputs/complex/sources` are unchanged from PR #346 (byte-identical at
  `9c94857` except his `ORIGIN.md`, kept at `f010392`).
- **New here**: `code/complex/code/scatter.py` and the generalization of the label, scalar, splice and guard checks
  from the paired-cube star scatter with h centres of rank h − 2 to any gx scatter (table or star) with any number
  of retained totals of any rank (regression: on PR #346's p = 10 program the generalized checks give byte-identical
  scalar schedules, splice programs, primitive expansions, ledger and precision guard); the generalized final-climb
  partition; the E8 pins; the Lean-binding and replay steps of `certify_complex.py`; `verify.sh` changes.

Credits do not imply endorsement or review by the credited authors.

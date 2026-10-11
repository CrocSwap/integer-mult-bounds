# Attribution and provenance

Prepared by DaysSky, assisted with Claude. Apache-2.0 (see `LICENSE`) applies to the new code and to the inherited
Apache-2.0 code below; third-party notices are preserved where files are vendored.

- **The bridged word and the E8 unit** (`code/complex/inputs/e8/`, `code/complex/inputs/complex/sources/`):
  Jacob Sussman, jacobalansussman/wht-power-saving-lean at `9c94857bbaee886f8649edee0bc2d3c738f9555e` (Apache-2.0,
  Copyright 2026 Jacob Sussman; his `LICENSE` and `NOTICE` are vendored beside the files).
  - B₂ is his: the bridged five-stage word (`Work/Bridge/Net.lean`, `Work/BridgeGeom/*.lean`) and its general
    stage geometry. `code/complex/code/bridged.py` generalises its schedule and twin gates to K pairs.
  - The E8 certificate, gx, gxcore, the Lean-data generators and the stand-alone replay are vendored byte-identical
    and sha-pinned in `code/complex/inputs/complex/source-pins.json`.
- **Complex checks and pricing** (`code/complex/`, `code/pricing/`): PR #352 (DaysSky) at
  `04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2`, on LJH-217's PR #346 port of PR #315's portable complex checks and
  engines (#256/#233/#202/#200/#194/#184 lineage: icekylinx, Chafik Boukhalfa, Avi Eisenberg, eumemic and others).
  `SOURCE-pr352.json` pins the 93 unchanged files by git blob id.
- **New here:**
  - `bridged.py`: the bridged word B_K and its finite layout check;
  - the layout parameter K in `portable_complex.py`, `complex_splice.py` and `complex_scalars.py`;
  - `pins-e8-b3.json`;
  - `certify_b3.py`, `provenance.py` and `verify.sh`.

Credits do not imply endorsement or review by the credited authors.

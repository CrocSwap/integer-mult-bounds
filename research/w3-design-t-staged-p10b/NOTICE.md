# Notice

Apache-2.0 (`LICENSE`). Prepared by Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance.

- `data/parity`: #325's p10b parity-fused word (DreamingOfClouds), exported in PR249 snapshot format. It is identical to
  #346's `BASE-*` snapshot (records sha256 f1933dbf…).
- `data/staged`: that word after our #329 stages descent, target, restore and sink. These stages come from the
  #268/#273 (eumemic), #280/#283/#287/#295 (incl. Rohan Arun's descent) and #320/#329 lineage.
- `data/labels.json`: the cube labels of the p10b word, as shipped by #346.
- `code/dt.py`, `classify.py`, `comp.py`, `twin.py`: our reimplementation of utcorvusvolat-dotcom's w3 Design T
  and twin condensation (#310), following LJH-217's h = 20 port (#346). Neither was run here; both were read as data.
- `code/checkers/legality_h.cpp`, `columns_h.cpp`, `json.hpp`: #266's official cohort checkers (via our #312
  vendoring). Only the constants h, v and R were changed, and `bits/stdc++.h` is a portability shim.
- `code/engines/moment.py`, `base_two_moment.py`, `outer.py`: #315's engines as vendored in our #329 package.
- `complex/`: Jacob Sussman's `gcert1-e8-r783.json.gz`, `gx.py` and `gxcore.py` from
  jacobalansussman/wht-power-saving-lean at `9c94857`, under Apache-2.0. Its LICENSE and NOTICE are kept alongside.
  DaysSky (#352) first used this unit as the complex supplier.

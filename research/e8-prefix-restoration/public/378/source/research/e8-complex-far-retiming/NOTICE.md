# Notice

Apache-2.0 (`LICENSE`). Prepared by Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance.

- `complex/gcert1-e8-r783.json.gz`, `complex/gx/gx.py`, `complex/gx/gxcore.py`: Jacob Sussman,
  jacobalansussman/wht-power-saving-lean at `9c94857`, Apache-2.0. The bytes are identical (by git blob id) to the copies vendored in
  DaysSky's #363/#375 and aliromman's #365. The upstream LICENSE and NOTICE are kept as `complex/LICENSE-wht-power-saving-lean`
  and `complex/NOTICE-wht-power-saving-lean`.
- `data/gcert1-e8-r783-far.json.gz`: this package's certificate, derived from Sussman's by `code/cxfar.py` and `code/cxfinal.py`.
  It keeps his format, and its `derived_from` field records the derivation.
- `data/bit/bitE8-r865.json.gz`: utcorvusvolat-dotcom's (Dylan Crow) #370 E8 bit word, byte-identical to #370's and #373's
  `data/bit` (Apache-2.0).
- `code/engines/moment.py`, `base_two_moment.py`, `outer.py`: PR #315's engines (DreamingOfClouds; eumemic; the #144/#23
  lineage), as vendored in our #329/#359 packages.
- `code/layout_bk.py`: our reimplementation of DaysSky's B_K rule (#363), on Sussman's B₂ and stage geometry. #363's `bridged.py` was read as data
  and not run.
- `code/e8core.py`, `cxcheck.py`, `cxop.py`, `kappa.py`, `cxretime.py`, `cxsplit.py`, `cxpiece.py`, `cxfar.py`, `cxfinal.py`,
  `cxkernel.py`: our own code. The retiming and reorder mechanisms follow our #329/#359 stage lineage (#287/#291/#299/#306), and
  aliromman's #365 is generalised (read as data, not run). `cxkernel.py` also holds the exterior-gauge kernel census, which is
  unprofitable on this unit, together with the helpers it shares with the search (`rehist`, `price`).
- PR #375's halving-degree-two guard (DaysSky) is cited, not vendored.

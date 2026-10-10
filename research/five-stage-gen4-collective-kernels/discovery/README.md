# Discovery: twin dirty-helper pairs on the gen4 word

Provenance for `../kernel-selection.json`. Nothing here is executed by `verify.py`.

* `dump_transcript.py PKG OUT` — runs `prepare -> physical527 -> parity_transform` of the package and dumps the
  six-int transcript, frame tables, initial frames and the raw ledger.
* `census.py DUMP` — the census (output frozen in `twin-census.json`): 13,944 plain dirty helpers (initial frame
  ZERO, not gauges) all have every initial compensation read before their first other use (gap >= 41,247 records),
  so every helper has its own cut. Grouping by complete F2 target response gives 1,568 twin classes (1,544 of size
  2, 24 of size 3); the response matrix has rank 1,760 (nullity 12,184). 568 twin pairs have a common cut and a
  nondegenerate (9I-J) line inside the intersection of their first frames (436 lines e_i-e_j, 132 generic rational
  lines; 1,000 twin pairs have trivially intersecting first frames).
* `pick_k.py PKG DUMP` — prices K pairs in phi order (phi(r) = r ln(120/r) on the first-move ranks) on the package's
  own ledger (literal stock = priced five-stage mass/2 + 2200, 60 replicas, normalization 12; the model reproduces
  #276's kappa exactly). The best K is 424: all pairs with negative phi gain (220 of first dims (2,2), 180 of (3,3),
  24 of (3,5)); pairs beyond are net negative. 424 is even and tiles: 60*424 rank-23 slots = 4 * 6360 banks of
  (23^4,4^7), whose 7*6360 rank-4 blocks come out of the (4^30) banks (4400 -> 2916).
* `build_selection.py K` — freezes the K best pairs with their cut reads (bound by content), entrance lines and the
  input hashes of the fresh parity-fused transcript.
* `generate_pins.py OUT` — replays every stage with `pins.RECORD` set and writes `../expected/kernel-pins.json`.
  `verify.py` refuses to run in that mode.

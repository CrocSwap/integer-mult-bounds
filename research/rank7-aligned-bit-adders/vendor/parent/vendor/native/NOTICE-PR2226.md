# Credit: anticipatory dirty borrowing (PR2226)

The construction realised by this native chain is **PR2226, "anticipatory dirty borrowing"**, by Cinna Davis
(@1337isnot1337), prepared with substantial OpenAI Codex assistance (Apache-2.0): the logical reference change
K_G of a lender register (a monomial Clifford: a permutation of the 512 columns with phase mod 4), the initial
compensation terms c K_G z, the early cold tail, the exact cold restoration and the private zero buffers of the
FULL-frame cleanup.  `vendor/pr2226_operators.py`, `vendor/pr2226_replay.py` and `vendor/PR2226-NOTICE.md` are byte copies
of PR2226's `operators.py`, `replay.py` and `NOTICE.md`.  `bw_gauss.py` is a port of `operators.py` (change, monomial,
apply_mono, coord, frame, check) and adds a decoder from a serialized `clifford_exact` monomial to its exact 512 x 512
Gaussian matrix.

What this chain adds (the P3 native realisation, with the borrowing work's explicit chronological BORROW-WORD as input):
warp events and zero buffers in `LOCAL-PROGRAMS`, warp recipes in `CLIFFORD-RECIPES.json` (lowered with the unchanged
`lower_child`, rank zero, then compared with the exact numpy column product), logical K_G recipes in
`RESIDUAL-ADAPTERS.json`, an independent local replay in both orientations that checks every warp product on all 512
columns, and the negative controls listed in `INDEPENDENT-LOCAL-REPLAY.json`, `WRAPPER-CHECKS.json`, `WARP-RECIPE-CHECKS.json`
and `bw_tamper.py`.

Lineage retained: icekylinx (PR425/433/514, scalar and wrapper machinery), DreamingOfClouds (PR458/484/593 hyperplane/cold-HPE
extensions), the clifford_exact compiler (vendor531), and the owners named in the package README.  `vendor/clifford/clifford_exact.py`
is a byte copy.

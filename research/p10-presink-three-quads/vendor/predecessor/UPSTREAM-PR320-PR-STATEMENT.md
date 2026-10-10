κ = 7.69553898621543e-4

# The p = 10 bit word with the transcript stage stack

A conditional finite construction with **κ = 769553898621543/10¹⁸ ≈ 7.69553898621543 × 10⁻⁴** (+0.697% over
#315's 7.64230861320245e-4, +0.046% over our #320's 7.69198971896986e-4, +0.169% over #319's 7.68257328708259e-4).
The bit binds: its certified root 7.70146568251934e-4 is below the complex leaf cap
of #315's centre-sharing supplier (7.72714351296671e-4), which is unchanged.

#315's p = 10 word ran with no transcript stages. This package adds the gen5 stage stack, re-derived on that
word: #287's concave descent (480 gates) and target-prefix squares (120 groups), a shared-donor kernel (1,047
entries of total entrance rank 1,200: per-entrance maximum-weight closure over alternate response bases, donors
shared by up to 30 entries, after eumemic's #319; it replaces #320's 775-entry packing and keeps the sink helpers
out), #280/#283 early
restorations (240), #283 terminal sinks (7) and #299's reorder (133 moves). Each stage was predicted with the
φ ledger before it was built; every prediction equals the verified κ of the package truncated after that stage
(table in `README.md`). A second descent, a second reorder round and a second kernel round find nothing (worth a
stage) on this word.

The p = 12 literals of the stage code are replaced by cube-size formulas or strict pins in `word-pins.json`; the
banks get an exact economy tiling for the new residual widths (no padding). Run `python3 -B verify.py --output
NEW_DIR` (Python 3.12+, sympy 1.14.0; about four minutes).

See `README.md`, `STAGES-PROOF.md`, `BANK-PROOF.md`, `discovery/README.md`, `NOTICE.md`; the base package is
described in `README-PR315.md` and `PROOF.md`.

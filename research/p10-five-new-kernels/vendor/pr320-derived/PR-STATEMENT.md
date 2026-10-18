κ = 7.69198971896986e-4

# The p = 10 bit word with the transcript stage stack

A conditional finite construction with **κ = 384599485948493/(5·10¹⁷) ≈ 7.69198971896986 × 10⁻⁴** (+0.650% over
#315's 7.64230861320245e-4). The bit binds: its certified root 7.69791094751301e-4 is below the complex leaf cap
of #315's centre-sharing supplier (7.72714351296671e-4), which is unchanged.

#315's p = 10 word ran with no transcript stages. This package adds the gen5 stage stack, re-derived on that
word: #287's concave descent (480 gates) and target-prefix squares (120 groups), collective kernel entries (775:
536 twin pairs and 239 multi-donor families, restart-packed, packed around the sink helpers), #280/#283 early
restorations (240), #283 terminal sinks (7) and #299's reorder (133 moves). Each stage was predicted with the
φ ledger before it was built; every prediction equals the verified κ of the package truncated after that stage
(table in `README.md`). A second descent and a second reorder round find nothing on this word.

The p = 12 literals of the stage code are replaced by cube-size formulas or strict pins in `word-pins.json`; the
banks get an exact economy tiling for the new residual widths (no padding). Run `python3 -B verify.py --output
NEW_DIR` (Python 3.12+, sympy 1.14.0; about four minutes).

See `README.md`, `STAGES-PROOF.md`, `BANK-PROOF.md`, `discovery/README.md`, `NOTICE.md`; the base package is
described in `README-PR315.md` and `PROOF.md`.

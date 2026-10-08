# Contiguous-pair coordinate pricing and two-round circuit exchange

Conditional **$\kappa = 26402609637081 / 500000000000000000 = 5.2805219274162 \times 10^{-5}$** (**+0.026060% above PR #98**, $+13,757,650,460$ grid steps over PR #98 and $+15,602,338,941$ over PR #91), with bit saving `52808007812753/1000000000000000000`. Under the inherited analytic and fixed finite-alphabet multitape hypotheses, $T(n) = O(n(\log n)^{1-\kappa})$.

This package certifies two cumulative improvements on the aligned-composition track (PRs #91, #93, #94, #95, #98):

1. **Stage A — Contiguous-pair coordinate pricing with the unchanged PR #91 engine ($\kappa = 26400279929441/500000000000000000 = 5.2800559858882 \times 10^{-5}$)**:
   In PR #91 (and PRs #93–#98), the odd singleton coordinate (`22` at $h=23$, `24` at $h=25$) was placed at index `4`, splitting the chain of consecutive coordinate pairs, and coordinates `(17,18)` at $h=25$ were transposed to `(23,22)`, splitting pairs `(16,17)` and `(18,19)`. Restoring pair contiguity and pricing $h=25$ carriers in the contiguous-pair order causes the **pristine, unmodified PR #91 engine** (`scripts/experiments/aligned_composition_engine.py`) to reclaim an additional role at $h=25$ (**$R_{25} = 34,771$**, down from $34,772$, width $W = 130,416,141$) and gain $+9,098,235,180$ grid steps over PR #98.
2. **Stage B — Two-round carry exchange and min-cost circuit reclamation ($\kappa = 26402609637081/500000000000000000 = 5.2805219274162 \times 10^{-5}$)**:
   Running two outer rounds of carry exchange (`outer_exchange_rounds = 2`) and toggling retired clearing supports across all zero-sum $\mathbb{F}_2$ circuits ordered by pending transition cost reclaims **4 roles at $h=25$** (**$R_{25} = 34,768$**) and sharpens the $h=23$ internal profile ($R_{23} = 26,399, W = 130,438,428$).

Every exterior, copied-center charge, side-growth contribution, and early/late restoration gate remains paid in full; the finite bridge formula and complex layer are unchanged.

```sh
python3 research/contiguous-pair-exchange/verify.py
python3 research/contiguous-pair-exchange/test_controls.py
# Regenerate both Stage A (pristine PR91 engine) and Stage B words from scratch:
python3 research/contiguous-pair-exchange/verify.py --regenerate
make verify
```

See [PROOF.md](PROOF.md) for the mathematical argument and complete paid accounting.

Credit Chafik Boukhalfa (#91), Rohan Arun (#93/#95/#98), Maxime Fleury with Codebuff assistance (#94), Alejandro Zarzuelo Urdiales, Thomas DiFiore, Dominik Scholz, eumemic, Avi Eisenberg, Rohan Garg, icekylinx, James Chang, Zhihao Chen, Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, Douglas Colkitt, OpenAI, and all predecessors. Original code and notices are preserved.

Prepared by Thomas Marchand with Google Antigravity assistance.

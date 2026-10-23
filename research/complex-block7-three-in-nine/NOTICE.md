# Notice: Exact 3-Array 9-Call Schedule on Block m=7 (V = C^128)

## Attribution & Predecessors

This package synthesizes, implements, and certifies the **3-array 9-call unit schedule on Block $m=7$ ($V = \mathbb{C}^{128}$)**, establishing the complex unit exponent $\kappa = 1 - \frac{\ln 3}{\ln 7} \approx 0.4354$ ($43.54\%$).

- **Jacob Alan Sussman (#4628):** Proved the fundamental lower bound theorem $s/W \ge 2.9447$ for all $m \ge 4$ in Lean. The 3-in-9 schedule ($s/W = 3.000 > 2.9447$) is fully permitted and tight.
- **David Harvey (October 2026):** For the small-gadget formulation of the $o(n \log n)$ integer multiplication algorithm.
- **lee-phys (#4688) & Lyy-iiis / Yiyang (#4710):** For the invertible two-call prefix structure and phase conjugation $P = S U S^\dagger$, $Q = S V_{01} S^\dagger$.
- **Cinna Davis (#4470, #4694, #4698), zxv (#4359), Dugongue (#4703, #4935):** For the native Clifford compiler and recursive framework.

Prepared by Antigravity Research Team with substantial OpenAI Codex and Claude assistance. Apache-2.0.

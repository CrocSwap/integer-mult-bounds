# P104 relay construction v2: 1,031 lifetimes (cell-tree design)

FINDING, no κ claim. Card `p104-side-correction`, revision 4. This follows `../relay-construction` (2,185 lifetimes).

- **Construction.** `WORD_ct12.json` (sha256 10d47696…) is an exact 104-target correction in the X-only model (#2353/#2393/#2445) with **1,031 lifetimes**. The published checker `../relay-construction/check_p104_relay_construction.py <repo> WORD_ct12.json` prints `PASS_P104_RELAY_CONSTRUCTION lifetimes=1031`, and `controls.py` prints `CONTROLS_PASS`. No new ops were needed.
- **Design ("cell trees").**
  - A binary tree of F₂ functionals splits the 104 sources into cells.
  - Target t's pools are supp(t) ∩ cell. A pool's frame is the span of its sources, and pools are canonical, so targets that need the same source set share a pool. The root split gives 2 arrivals per target.
  - Junk per pool is scored exactly as rank(D|a) + rank(D|b) − rank(D).
  - Local search over the flags (`celltree.py`) reached J = 927, so L = 104 + J = 1,031.
- **Counts.**
  - 1,126 pools, 705 of them shared.
  - Profile {1:2427, 2:1094, 3:998, 4:96, 5:66, 6:157, 7:2}, rank mass 9,279.
  - The junk sits mostly in unshared upper pools of ≥ 12 sources: 453 of it, about 4.4 per target.
- **Allowance at PR #2559** (`allow2559.py`, `allowp.py`).
  - Lifetime caps are 482 / 463 / 417 / 322 for {1,1,7} / {1,1,1,6} / {1,1,1,1,5} / nine rank-1 steps.
  - An arrival lifetime must pass H_t and then FULL, so it cannot have the {1,1,7} shape. Any relay design is therefore capped at **≤ 463 lifetimes (merge-loss ≤ 255)**, and less for deeper chains. Chain caps: [1,6,1,1] 463, [5,2,1,1] 440, [1,5,1,1,1] 417.
  - The current best claim (#2571) is higher than #2559, so the real cap is slightly lower still.
  - 1,031 is 2.2× over the cap. **This is not a supplier.**
- **Exact structure for a future floor.**
  - Off the diagonal C = −G/2, and G = PPᵀ/4 has rank 8. So a pool demand built from full restrictions has rank ≤ 8.
  - The normals lie in an affine hyperplane, so |S(V)|·|T(V)| ≤ 128 for every frame.
  - Identities: L = 104 + Σ_P (in − ρ) = n_line + Σ_U (out − ρ).
- **Floor.** No floor above 255 is proved. A sharing count gives only L ≳ 387.

Author-checked with Claude Code assistance (a sub-agent did the search). The main session re-ran the checker and controls. Not independently reviewed.

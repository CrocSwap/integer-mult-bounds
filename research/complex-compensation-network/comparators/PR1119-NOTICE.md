# Notice and Attribution

**Package:** `research/u8-cleanup-markowitz-lpr-seed30`
**License:** Apache-2.0 (following the repository license at the root of `CrocSwap/integer-mult-bounds`).

## Contributor Attribution and AI Disclosure

- **Contributor:** `steph4n-gh`
- **AI Assistance Disclosure:** Substantial AI assistance from **Gemini 4 Argon** (Google DeepMind / Antigravity) was used in the mathematical formulation of the two-sided Markowitz $R^{-1} P L^{-1}$ Schur-complement cleanup factorization and Weyl-group signed cycle realization, the analysis of the partial-$E_4$ entrance-promotion climb-splitting lemma, and the implementation of `verify.py`, `independent.py`, and `test_package.py`.

## Credit to Predecessor Work

This package builds directly on and credits the following predecessor contributions in `CrocSwap/integer-mult-bounds`:

- **Jonathan Capalbo (`jon314159`, PR #942):** Selected frontier certificate (`certificates/selected-result.json`, $\kappa = 1661960547713947 / 10^{18}$), T37 owner-allocation proof (`research/complex-t37-owners/`), and the PR #942 audit bundle (`research/community-frontier942-audit/t37-replay.tar.gz`).
- **Jeremy Kothe (`jeremykothe2`, PR #869 / PR #870):** The U8 complex supplier word (`research/gauge44-barch/construction/barch/RECIPE-U8.json`, `LOCAL-PINS-barch-U8.json`) and the `gauge44-barch` pipeline (`PROOF-NOTE-BARCH.md`, `PROOF-NOTE-FRAMES-X4.md`, `PROOF-NOTE-PROMO.md`, `PROOF-NOTE-LAYERS.md`, `PROOF-NOTE-NOTRI.md`).
- **Chafik Boukhalfa (`chafreaky`, PR #890) and Hao Yan (`icekylinx`, PR #858, PR #704, PR #635, PR #571, PR #558, PR #552, PR #531, PR #514, PR #433, PR #425):** The hyperplane-ended (`HPE`) and cold-hyperplane-ended (`COLD-HPE`) local compiler and verification suite (`hpe_audit_and_transport.py`, `hpe_emit_local.py`, `hpe_audit_local.py`, `hpe_adapters_local.py`), the `cold44x.py` refactored-cleanup architecture, and the multi-cold global assembly pipeline.
- **DreamingOfClouds (PR #484, PR #593, PR #589, PR #555):** Entrance-frame residual wrapper theorems ($L_{E,U}^{-1} S_{E,U} R_{E,U}^{-1} = C_{[w]} \otimes I$), arbitrary-dirt local compensation audits, and the selected bit-side supplier (`PR #589` on `PR #555`).
- **`steph4n-gh` (PR #1072):** Analysis of the remaining rank-1 idle slots in T37 under $J$-pair unpromotion (`research/complex-t37-jpair-unpromotion-seed24/`).

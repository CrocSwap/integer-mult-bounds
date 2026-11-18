# P104: a class junk floor |J| ≥ 4166 at owned mass 56 and κ ≤ .0122445 for the C = 56 flag class (Lean + certificate, no κ claim)

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. **No κ claim.** Two parts: a Lean theorem that takes the junk count `|J| ≥ 4166` as a hypothesis, and an external exact certificate that this count holds in a stated model class.

## What this is, and what it is not
* The class: F1's C = 56 flag model (rank-8 Y-plane rows, 8 chain pairs, each chain a monotone frame chain, one gather piece and one read piece per chain, plane separation). In that class the minimum junk count is certified to lie in **[4166, 4216]**. The upper end is a witness (two configurations, 4216 cells, odd and diagonal constraints met, rank 55/56). The lower end is a Lagrangian dual bound with exact rational arithmetic; Lean does not check it.
* The ceiling: with `|J| ≥ 4166` the same ceiling functional as `ceiling_native` (which used 1936) gives F(1 − t) < 0 for t in [.0122445, 1], i.e. κ ≤ .0122445. `.0122444` fails (margin −1.5e-2 at the point), so .0122445 is the tightest certified 7-digit value of this piece set.
* **The frontier words are NOT in this class.** They have rank 11 and multi-dimensional lifetimes; they are covered by #7668 and #7678 instead. This package says nothing about them. It bounds the C = 56 flag class only, as a structural statement about what such decoders must pay.

## Scope hypotheses (none proved in Lean; see PROVED.md)
1. Rank-8 Y-plane rows with C = 56 in one of F1's 8 configurations. The rigidity of the factorisation is numerical and quoted.
2. Monotone frame chains with any step sizes. Multi-dimensional steps are dominated by a refinement (proved on paper in the audit, so not a hypothesis).
3. One piece per gather and one piece per read, per chain. **No split gathers and no split reads is a real hypothesis**: with split gathers a non-forced chain contributes an unbounded prefix sum, the local term drops to −∞ for multi-chain cells, and the 4166 bound does not follow (only the single-chain 1936 survives splits). No cost rule excludes splits.
4. Plane separation (no second owned plane carries plane-1 X content). Without it the floor collapses.
Also not covered: decoders with 9 or more rows, network decoders, owned mass above 56, public-layer cancellation of arrival junk. The ceiling inherits the scope of the I3 congestion premises (`hcong`, `hdist`, ...) of `ceiling_native`.

## Files
| path | content |
|---|---|
| PR_BODY.md | draft PR description |
| PROVED.md | the main statements copied from the Lean text, plus the scope list |
| CHECK.txt | fresh compile table (46 modules) and `#print axioms` |
| lean/ | Lean subproject; new modules `Nov15/CongestionC56*.lean`, inherited modules unchanged from the previous native-ceiling package |
| certificate/ | the exact certificate: frozen multipliers, geometry data, two independent checkers, logs, SHA256SUMS |

## The Lean part
New modules: `CongestionC56Defs` (outward-rounded rational tables for three t-pieces on [.0122445, .0136564]), `CongestionC56Sig0..2` (kernel sigma certificates), `CongestionC56Pt0..2` (kernel F_base point enclosures), `CongestionC56D` (kernel derivative bound), `CongestionC56Unit` (kernel unit bounds), `CongestionC56` (`ceiling_c56`). Kernel-only: no `sorry`, no `native_decide`; `decide +kernel` for the numerics. Axioms: propext, Classical.choice, Quot.sound.
The table numbers were produced by a script (80-digit Decimal, ±1e-70 brackets; rounding outward) and are then re-checked by the kernel; the script is not in the package. Lean takes `hspTabK` and `hcstTabK` (spF and cst endpoint brackets) as hypotheses, as `ceiling_native` does for its tables.
Toolchain `leanprover/lean4:v4.33.0-rc1`; Mathlib commit `55b7917b472489c7c56a0fa6393af05cfd536599` (`lean/lakefile.toml`, `lean/lake-manifest.json`). CHECK.txt was produced file by file with `lean -j1 -o`; `lake build` was not run.

## The certificate (computer-certified outside Lean)
For any multipliers `lam ≥ 0` on (even cell, chain) pairs, weak duality gives |J| ≥ Σ_k min over complete flags of Σ_c lam_ck [τ_k(t) > σ_k(s)] + Σ_c min over live-chain subsets L of (junk indicator(L) − Σ lam_ck L_k). The chain term is an exact per-chain flag DP over the subspace lattice (29,212 subspaces of z^⊥ containing z'), the local term a small enumeration per cell. Odd-cell and diagonal constraints are dropped, which is a relaxation, so the bound is valid.
`certificate/multipliers/lam_cfg{0..7}_fin.pkl` are frozen multipliers (one file per configuration, the final iterate of each run; `lam_cfg6_fin.pkl` is configuration 6's third resume; SHA-256 in `certificate/SHA256SUMS`). Two independent implementations evaluate them over Q: `jr_lagx.py` (flag DP in the echelon-basis form, `jr_lag.py`) and `aud_cert.py` (element-set form, different code). Results on the frozen files:

| config | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| `aud_cert.py` exact LB | 4199.82 | 4199.82 | 4200.19 | 4200.11 | 4200.22 | 4199.84 | 4197.33 | 4200.09 |
| `jr_lagx.py` exact LB | 4199.82 | 4199.82 | 4200.19 | 4200.11 | 4200.22 | 4199.84 | 4197.33 | 4200.09 |

The two checkers return the identical exact fraction in all 8 configurations. Minimum over configurations 4197.33 (configuration 6), so the frozen multipliers in fact certify |J| ≥ 4198; the Lean theorem uses the more conservative 4166, the value of the first-pass multipliers that the independent audit re-certified (4165.98 for configuration 0, all others higher). A rerun of the Lean pieces at N = 4198 would move the ceiling to about .0122264 (same crossing computation); that is not done here.
Because J is an integer, every configuration gives |J| ≥ 4166 in the class. Running the checkers needs Python 3 with numpy: `PYTHON=python3 certificate/run_audit_checker.sh` (about 45 s per configuration) and `certificate/run_lagx_checker.sh` (about 4 min per configuration).
The multipliers were found by projected subgradient in floating point (not included); only the exact re-evaluation matters for validity.

## Not included
The SAT searches, the witness search code, the multiplier search, and the table-generation scripts. Working notes are not included.

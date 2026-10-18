# B258 VERDICT: SPEC / FORCED. By the letter it is MIXED, but both convention slivers are inert on every window, so nothing is unlocked. KPR5 material is in evidence/KPR5-endcap.md.
"y_t ends ⊆ perp(P_t)" is three rules stacked. Only the first is the swap contract. None of them is the ≥ 1 unit charge, which is the price of breaking the cap, not a rule.
1. SPEC: the sink label of Y_t is a complement hyperplane of the source label ⟨u_t⟩.
   - Complex route operator C_{U_sink(Y)} C_{U_src(X)}^{-1} must equal C^{⊗m} up to free per-role Z/phase wrappers: upstream/build/sections/03-motifs.tex:625-668 (Prop complex-motif-interface) and 05-layers.tex:141-154.
   - Bit analogue: 04-swap.tex:117-121 (eq finite-shear-contract), 03-motifs.tex:492-497, terminal table :235-243.
   - Legal sinks are exactly w^⊥ with w·u = 1, at zero rank. A non-complement costs rank n-2 (format-limits-corrected C.3 gate 0).
2. CONVENTION, but pinned: the choice w_t = u_t, which is the literal perp(P_t).
   - Census row 6, class C (research/format-limits-corrected/README.md B.2; re-checked on origin/main ba82555c, unchanged).
   - Lemma R (C.3) forces w_t = u_t whenever the drop-free taint of t spans u_t^⊥ (112/112 targets on #531/#569/#571).
3. CONVENTION, but priced: the last gate frame of y must lie inside the sink, i.e. no descent edge (nesting, census row 3, "C (priced, not forbidden)").
   - A non-nested final edge G→S costs d = dim G + dim S − 2 dim(G∩S).
   - Reader descents are registered dead: R39-H, R40-C, J24-C1 (≈ −5.5%/call).
Verifier enforcement, for targets only. Helpers get arbitrary ends via helper_final (#593/#599):
- gk_word.py:117 does the final climb of r ∈ [V, 2V) to perp(P[r−V]); the assert at :102 raises 'frame violation'.
- gk_word.py:116 climbs BOTH ADD operands. This is the read drag: census row 1, SPEC, 03-motifs.tex:157.
- gauge44-slots/independent/audit_local.py:115 sets end = perp(p) per port; :122 checks 'frame not monotone'; :142 does the final climb; :116 helper_final is helpers only.
- freeze_spec.py and invoice_allcold.py carry no separate target-cap rule.
"≥ 1 unit/target" is the minimum price of violating (1)+(3), and it is rank-intrinsic (B29/B35). A FULL sink forces M_in(X_t) = 0: X loses its port dimension, +1 rank. A descent FULL→perp costs d = 1. Either way it is +1 rank per call on the target.

## Decisive fact: every violator ends FULL
Measured on all 84 B252/B253 gauge-forward words (endcap.py; b252_caps.txt):
- every violating y ends at dim 9 = FULL, with u_t ∈ frame (u_t inside the final frame) in 100% of cases;
- so 0 violators fit ANY complement hyperplane, and relaxing sliver (2) unlocks nothing, independently of Lemma R;
- each violator is exactly 1 dimension out (dim − dim(frame ∩ perp) = 1).
The only remaining relaxations are "FULL end + unit" or "descent", and each costs 1 rank unit/call.
Violator counts: single S3 copy 4; SS16 16; rr32 48; Wr32 48; rr+SS48 64; rr+Wr64 48; rr+Wr+SS80 64.

## Prices
Exact unit price: kap_free.py runs the package's own price_profile.py (two exact engines + outer47 + PR589 bit). The only change is that the 2560 deficit pin is replaced by the honest deficit; nothing else in the package is edited. Base κ = 1.67166528321877e-3, which reproduces the package.
- +1 rank-1 local unit ×72 calls: κ 1.624537144e-3, −2.819%. +4: −11.275%. +16: −45.061%. +32: −90.02%. ≥ about 36: certify fails (no saving left).
Window bands = B252 pre-cap band + exact charge, first-order:

| window | pre-cap band, reproduced exactly by relax_price.py (H1 / H16 / H48) | ≥ 1 unit per violator | ≥ 2 units per violator |
|---|---|---|---|
| single S3 copy (4 y) | −0.01 / +0.05 / +0.07% | ≈ −11.2% | ≈ −21.5% |
| SS16 (16 y) | −0.35 / +1.34 / +2.02% | ≈ −43% | κ ≈ 0 |
| rr32, Wr32, rr+Wr64 (48 y) | ≤ +3.52% | κ → 0 (no saving) | κ → 0 |
| rr+SS48, all 80 (64 y) | ≤ +3.52% | κ → 0 (no saving) | κ → 0 |

- The ≥ 2 units column applies when the 8→9 climb, which the band convention sends to idle, is also charged honestly.
- WARNING: B252's band convention lets idle absorb added TARGET rank. That is how relax_price.py printed only −0.3% for the 80. It is wrong for data registers (B15 item 5: data-carrying registers cannot be hosted). Use the deficit-honest unit.
Break-even: the best pre-cap credit is +3.52%/80 = 0.044% per deleted copy, and the charge is 2.82% per violating y, so a deletion pays only if it breaks ≤ 0.016 y caps per copy.
- B255 (16 hub packets) and B244 partner caps are the same mechanism and price, so the same kill applies.
- S4 (0/112) is blocked by VALUE (the pair mixer), not by the cap. The relaxation does not touch it.

No legality case is written (part c): there is no convention whose relaxation is free. The CONVENTION bar fails at step 2: there is no soundness argument for an uncharged FULL end, by B29/B35, and the exact price above confirms what that unit costs (−2.819% per unit per call).
Escapes that remain (all SPEC-legal, none touching the cap): version reconstruction (B256); drag reordering (B256/B257); snapshot hoist (B257); a decoder/motif redesign that changes the u_t's (Lemma R scope).
Files: endcap.py, relax_price.py, kap_free.py, b252_caps.txt (cards/B258/). Nothing was pushed, no SPEC or HEADROOM files were touched, and no heavy jobs were run.

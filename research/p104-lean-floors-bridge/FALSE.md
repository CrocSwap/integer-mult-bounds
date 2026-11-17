# Prose statements refuted by Lean, with fixes

Each is a Lean theorem in `lean/Nov15/`. None of the source cards was published: they are local Nov 15–16 cards, later than the last shipped PRs.
Corrected forms are proved in the same files.
1. JUNKLB2 T4 "public arrivals only" : `JunkLB2.T4_public_only_false`. Fix: count owned arrivals (`T4_departer`, `ExportLaw.T4_star`).
2. SYLEQ RANK/EQ monotone on the raw state space: `SYLEQ.rankEqRaw_not_mono`. Fix: map empty candidate sets to ⊥ (`rankEqFix_mono`).
3. EXPORTLAW "needs od, oe and clr": `ExportLaw.drop_owned_false`, `drop_od_false`, `drop_oe_false`. Fix: od, oe needed, clr not (`E2_export`).
4. TOKENRANK TR1(a) |exits| = |entries| with CLEAR: `TokenRank.TR1_count_literal_false`. Fix: add #CLEAR/COPY (`TR1_count`).
5. RankLaw "every op except CLEAR is invertible": `RankLaw.copy_lossy_example`. Fix: Lossy = COPY over a live row and SCALE 0.
6. "The V mix is unique" without independent end rows: `HubSettle.vmix_not_unique_example`. Fix: rank X[G1] = |G1| (`vmix_unique`).
7. "M ∈ GL(A) iff the determinants are A-units": `HubSettle.iff_false_example`. Fix: "if" holds (`solve_inGL`); "only if" gives det B / det A1 ∈ A^× (`inGL_det_ratio`).
8. JUNKLB3 L2 (Y-relay): `YRelay.scale_leak`, `read_leak`. Fix: Y_p written only by ADDs in the window, Y_q quiet (`relay_no_token`).
9. Difference chain with SCALE: `DiffChain.scale_breaks`. Fix: ADD-only between deliveries.
10. TOKENCANCEL T2 literal "Σ a_i = 0": `TokenCancel.T2_literal_false`. Fix: effective coefficients (`T2_corrected`) or no SCALE between contacts (`contacts_noscale`).
11. BITE-DEPART D1 for any class-N word: `DepartD1.D1_false`. Fix: hypothesis hArr (`D1`) or count born departers (`D1_all`).
Also: LemmaPG char ≠ 2 is necessary (`char_two_counterexample`), as the source stated.

## Bridge: "helperD0 ≥ JB(relay edges)" (V2Bridge)
12. The uncorrected statement "helper D0 ≥ JB cost of the helper relay" is false in general. Fix: `V2Bridge.bridge` (adds Σ_h corr_θ), `bridge_0V` ({0}→V helpers), `bridge_beta_V`.
   - Counterexample A (helper ends below V): one helper with one move, dim 1 → dim 2, which is also its final chart. D0 = f(1) − f(1) − f(0) = 0, but the JB edge (1,2) costs 8 ln 8 − 7 ln 7 ≈ 3.02.
   - Counterexample B (line-born helper): a helper born at a line L, moving L → Y (dim b ≤ 8) → V has D0 = c(1,b), while JB_β charges c(1,b) + B1 with B1 = f(9) − f(8) ≈ 3.14; D0 does not contain the B1 term.

# Nov15/SpecTS.lean 
Formalises T1 = R42 Lemma TS (internal notes section 2; hand re-derivation internal notes). Kernel-only: no sorry, no native_decide; `#print axioms` on all 8 headline theorems = [propext, Classical.choice, Quot.sound]. 6 s / 2.0 GB. Builds on `SpecTSUR` (product formula `pp_eq`, general `lemmaTS`, which already proved Gram = 2I; SpecTS adds the explicit model setting, rank facts, and corollaries).
**Verdict: paper statement TRUE as written (verbatim, any J; no counterexample).**

## Model setting (INHERITED, UNAUDITED; taken as hypotheses/definitions, not proved)
Coordinates `tau + alpha` (targets, ancillas). Character `mu : iota -> ZMod 2`, target vectors `t j : iota -> ZMod 2`; `sD mu t` = `-1` on target j iff `mu . t_j = 1`, else `+1`, and `+1` on ancillas; `Dmod = diag (sD)`. Jobs `refl (x i) (y i) = I - x_i y_i^T` (y_i . x_i = 2 is NOT assumed). Unit-free character = the unit letters are inactive (mu . Q = 0), encoded as hypothesis `pp x y k = Dmod mu t` (ordered product of the k ACTIVE jobs equals D_mu, whatever the order). Not modelled: the relation lattice, why a character is unit-free, which jobs are active. Tightness `hcard`: #{targets j : mu . t_j = 1} = k. Also char != 2 (`(2:K) != 0`).

## Proved (all under exactly those hypotheses)
- `lemmaTS_model` (conjunction): (G) `y_i . x_j = 2 delta_ij` for all i, j (both orders; any word order); (N) `Y^T X = 2 N`, `N = 1` (so `N = G/2 = I + strict-upper(G)`), `IsUnit N`; (R) `rank X = k`, `rank Y = k`; (S) `x_i, y_i` vanish on every ancilla and on every unflipped target; (I) `range(I - D) = span(x_i)`.
- Corollaries: `model_job_blocks` (each job = `fromBlocks job_R 0 0 1`, i.e. supports in target coordinates), `model_job_fix_anc` (a job fixes every ancilla coordinate), `model_commute` (all jobs of the tight set commute), `model_invol` (each job is an involution), `model_any_order` (the product in ANY permuted order = D_mu), `model_gd` (`g_T = g_{T^c} * D_mu` for every subset T of the tight set, `D_mu = D_R + I_ancillas`; i.e. g_d = (prod_{S-d} g) D_R).
- Proof route differs from the hand proof (hand: full rank => N invertible => N = G/2 => compare); Lean derives G = 2I first (via left inverses of Z = X N^-1 in `lemmaTS`) and then reads off rank X = rank Y = k, N = I = G/2 as consequences. Equivalent: all those facts hold.
- Non-vacuity: `ex_prod`/`ex_card` (Q, k = 1, one flipped target, one ancilla, x = (1,0), y = (2,0)) satisfy the hypotheses and `lemmaTS_model` is applied to them.
- Hypothesis necessity (already in SpecTSUR): `tight_needed` (r = k cannot be dropped: two equal jobs on Fin 1 over Q multiply to I, r = 0 < k = 2, Gram not 2I).

## Caveats
- Commutation/any-order statements are about the k active jobs of ONE tight character; "jobs in a common tight set" in the notes = jobs active at the same tight mu.
- The model setting is not audited here (same residual caveat as AUDIT43/T1J7-AUDIT).

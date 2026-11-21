# LEANZ4 (Nov 20) lean/decoder-duality/Nov15/HalvingLaw.lean
KERNEL-CHECKED via runlean.sh (~10 s, 2.3 GB). No sorry/native_decide/new axioms; all headlines depend only on [propext, Classical.choice, Quot.sound]. Own copy of the TensorPot F2 layer (no cross-imports); extra imports GroupTheory.Index, FieldTheory.Finiteness.

Model: charts = F2-subspaces C of F2^nu; hat C = preimage in (Z/4)^nu (|hat C| = 2^(dim C + n), card_hat). Values stored DOUBLED a_r in Lambda^omega (w = a/2, so den<=2 by construction), Lambda a ring with rho : Lambda -> Z/4 (Lambda = Z shown; Z_[2] works verbatim). Encoding [w] = rho(a) = 2w mod 4. Potential pot4 C [w] = hat C (x) [w] (AddSubgroup of Matrix nu omega (Z/4)); measure lam = log2 |.| (Nat.card).
Moves Mv4: add (integral scalar, incl. carries; needs ch d <= ch e), halve (w_d += (u/2) w_e, w_e = b integral: a_e = 2b; a_d += u b; counted by k), init, down (owned), upOwn, upPub.

Landed:
- ascent_card: |S + f D|*|C| <= |S|*|D| for f C <= S (any finite abelian groups; no 2-torsion needed).
- asc_step: Z/4 ascent costs <= climb. halve_card: |S + theta(A)| <= |S| 2^n when theta(2a) in S (proof: [A:2A] = |A cap ker 2| <= 2^n).
- step_bound4: ADD/INIT/descent/discard 0; ascent <= climb; halving <= n (|S'| <= |S| 2^(dc+dp+n dk)).
- run_inv4, run_pub_climb4; halving_headline: dim_F2(S0 + T) <= R + n k + Sum_P dim(final chart), where S0+T is the span of PUBLIC terms; public integral values make these 2-torsion = eps-image of the F2 potentials (pot4_eq), so lam(S0+T) = F2 dim of the shadow span.
- toy_rank_le4: R + n*k >= rank_F2(Q o Mbar) (any relays, any owned registers; Mbar is whatever the integral M reduces to, encoded in the Shadow hypothesis on the final publics).
- Non-vacuity: {1,2,7}: inst4_tight (rank 3, explicit run R=3, k=0), inst4_bound (every run, any halvings: 3 <= R + 3k). Halving: halving_nonvacuous (n=1, public w=1, owned receives w/2 : Run4 with R=0, one halve; potential strictly grows, an order-4 element appears).

Gaps / sharpenings vs CP.md (none fatal):
1. lam is log2 of cardinality. It equals Z/4 module length (every composition factor is Z/2) but that identification is not formalised; the F2-dim-of-a-layer version is only used through the 2-torsion shadow.
2. CP §1 "ascent <= climb via 2-torsion of C'^/C^" is stronger than needed: pure index counting suffices (ascent_card), no Z/4 structure.
3. Halving needs the SAME legality as ADD (ch d <= ch e) AND an integral source (a_e = 2b). A halving of a half-valued source (den 4) is outside the model, as in CP.
4. Hypotheses needed: owned registers start with rho(a) = 0; publics never descend; BOTH public start and final values are integral (Shadow: [w_r] = 2 w-bar_r, same chart) -- M integral is only used through this. Without integral publics the 2-torsion identification (pot4_eq) fails.
5. Psi-refinement (H_Psi from 2-torsion only) NOT formalised; H = n per halving move (CP's coarse H). On Q96 this charges 41 units = at least ceil(41/n) halving moves, n = register-chart dimension.
6. Z_(2)/odd-denominator scalars: covered by generic Lambda with rho, Lambda = Z_[2] not instantiated here.

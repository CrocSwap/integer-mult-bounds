# LEANTENSOR (Nov 20) — lean/decoder-duality/Nov15/TensorPot.lean
KERNEL-CHECKED via runlean.sh (~9 s, 2.3 GB). No sorry/native_decide/axioms; all headlines depend only on [propext, Classical.choice, Quot.sound].
Imports: Mathlib.LinearAlgebra.Matrix.Rank, ...FiniteDimensional.Lemmas, Algebra.Field.ZMod, NumberTheory.Padics.RingHoms.

Model: charts = Submodule K (ν → K); values = ω → K; C ⊗ w = image of C under c ↦ vecMulVec c w in Matrix ν ω K (≅ V ⊗ W).
Moves Mv: add (chart d ≤ chart e), init, down (owned only; discard = down to ⊥), upOwn (cost dim D − dim C into c), upPub (into p).
Run P s0 s S c p carries the cumulative potential S = sup over history.

Landed:
- ascent_dim / map_dim_le: dim(S ⊔ f D) + dim C ≤ dim S + dim D when f C ≤ S, C ≤ D.
- step_bound (per move): ADD/INIT/down add 0, ascent adds ≤ climb.
- run_inv, run_pub_climb (public climbs telescope), headline:
  dim(S0 ⊔ T) + Σ_P dim(start) ≤ dim S0 + R + Σ_P dim(final)   [R ≥ dim(S0+T) − dim S0 − Σ_publics(dim F − dim S)]
- headline' (S0 dropped, since dim S0 ≤ Σ_P dim start): dim(S0 ⊔ T) ≤ R + Σ_P dim(final chart).
- toy_lower: dim(S0+T) ≥ |ν||Q| + Σ dim q_s^⊥ + Σ dim F_j + rank(Q∘M)  (any relays J, no hypotheses on q).
- toy_rank_le: every run toyStart → toyFinal (any owned regs O, any relays J) has R ≥ rank(Q∘M)  [Q∘M = had q M, Hadamard of Gram(q) and M], any field.
- Item 4: RunR (values over a ring Λ, ADD scalars in Λ), red_run (reduction under φ : Λ →+* K is a legal run, same costs), headline_reduced, headline_padic2, toy_rank_le_reduced, toy_rank_le_padic2 (Λ = ℤ_[2], K = 𝔽₂): R ≥ rank_F2(Q∘(M mod 2)).
- Non-vacuity: {1,2,7} in 𝔽₂³, M = I, no relays: inst_tight = rank 3 ∧ explicit run with R = 3; inst_bound (any run ≥ 3).

REV.md gaps / sharpenings found while formalising (none fatal):
1. Owned registers must START at value 0 (S0 = publics only). Implicit in REV; it is the hypothesis h0. With nonzero owned starts S0 must include them (weaker bound).
2. ADD needs only chart_d ≤ chart_e (REV: same chart). Same-chart is a special case; the proof is unchanged.
3. Public descent is forbidden: essential for the telescoping Σ(dim F − dim S) = public climbs. Public INIT/ADD are harmless.
4. S0 can be dropped: R ≥ dim(S0+T) − Σ_P dim F_P. The toy then needs only ≥ (K ⊆ S0+T ∩ ker π); REV's "x-part is all of F^n⊗X" and kernel equality are only needed as inclusions/lower bounds. No need for q_t ≠ 0, dim q_t^⊥ = n−1, or q_t ∉ q_t^⊥ — the bound is stated in terms of the actual chart dimensions.
5. Relay cancellation needs the relay values z_j on FRESH coordinates (independent of the x/y block). Implicit in REV §2; here W = Q ⊕ Q ⊕ J.
6. Item 4: the reduction is on VALUES only; charts must already be F2-subspaces (the model's hypothesis), ADD scalars map to ADD scalars, INIT to INIT, all costs unchanged. "Supports only shrink" is not used. Initial/final reduced values must equal the toy's (hypotheses hs0, hs). ℤ_[2] ⊇ ℤ_(2) (odd-denominator rationals) so the odd-denominator model is covered.
7. Not formalised: REV §5 (mod-4 / LIFT LEMMA barriers), §3 fuzz, rendezvous-gadget replay. Charts here are subspaces of a fixed K^ν, not RegionCore's abstract preorder, so RegionCore was not reused (no shared code).

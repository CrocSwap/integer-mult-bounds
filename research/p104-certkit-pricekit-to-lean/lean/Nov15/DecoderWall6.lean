import Nov15.DecoderWall6X
/-!
# DecoderWall6 (lane RIGID): DYADICPORTS rigidity for P104, kernel-checked.
`rigid`: for every rank-8 decoder (`Hyp W U`: `card T = 8`, `M_pp = 1`, `M_pq = 0` on odd label pairs,
`M = W Uᵀ`) over a field of characteristic 0, `M_pq = (λ_p/λ_q) · ⟨Ah_p, Ah_q⟩ / 4` with all `λ_p ≠ 0`,
where `Ah = G104[:, F0]` (`F0 = [0,6,16,22,29,36,45,95]`) and `⟨Ah_p, Ah_q⟩ = 2·G104_pq` (`gram_link`).
So `M = Λ (G/2) Λ⁻¹`: the completion is the E8 one up to diagonal gauge.
Proof: frame factorisation (DW6.factor) ⇒ frame sums of `z(p,q) = M_pq M_qp`; exact linear certificate
(files Z*, ZS*, ZT*) ⇒ `z = 1/4` on frame pairs; ratio transport on the 28 pair graphs (R*) and the cocycle (X).
-/
set_option maxHeartbeats 0
namespace DW6
variable {T K : Type*} [Fintype T] [DecidableEq T] [Field K] [CharZero K] {W U : Fin 104 → T → K}

theorem hx_all (h : Hyp W U) (p : Fin 104) (a : Fin 8) :
    Mx W U p (F0 a) = (Ah p a : K) * al W U p * mu W U a := by
  fin_cases p
  exacts [hx_0 h a, hx_1 h a, hx_2 h a, hx_3 h a, hx_4 h a, hx_5 h a, hx_6 h a, hx_7 h a, hx_8 h a, hx_9 h a, hx_10 h a, hx_11 h a, hx_12 h a, hx_13 h a, hx_14 h a, hx_15 h a, hx_16 h a, hx_17 h a, hx_18 h a, hx_19 h a, hx_20 h a, hx_21 h a, hx_22 h a, hx_23 h a, hx_24 h a, hx_25 h a, hx_26 h a, hx_27 h a, hx_28 h a, hx_29 h a, hx_30 h a, hx_31 h a, hx_32 h a, hx_33 h a, hx_34 h a, hx_35 h a, hx_36 h a, hx_37 h a, hx_38 h a, hx_39 h a, hx_40 h a, hx_41 h a, hx_42 h a, hx_43 h a, hx_44 h a, hx_45 h a, hx_46 h a, hx_47 h a, hx_48 h a, hx_49 h a, hx_50 h a, hx_51 h a, hx_52 h a, hx_53 h a, hx_54 h a, hx_55 h a, hx_56 h a, hx_57 h a, hx_58 h a, hx_59 h a, hx_60 h a, hx_61 h a, hx_62 h a, hx_63 h a, hx_64 h a, hx_65 h a, hx_66 h a, hx_67 h a, hx_68 h a, hx_69 h a, hx_70 h a, hx_71 h a, hx_72 h a, hx_73 h a, hx_74 h a, hx_75 h a, hx_76 h a, hx_77 h a, hx_78 h a, hx_79 h a, hx_80 h a, hx_81 h a, hx_82 h a, hx_83 h a, hx_84 h a, hx_85 h a, hx_86 h a, hx_87 h a, hx_88 h a, hx_89 h a, hx_90 h a, hx_91 h a, hx_92 h a, hx_93 h a, hx_94 h a, hx_95 h a, hx_96 h a, hx_97 h a, hx_98 h a, hx_99 h a, hx_100 h a, hx_101 h a, hx_102 h a, hx_103 h a]

theorem hy_all (h : Hyp W U) (p : Fin 104) (a : Fin 8) :
    Mx W U (F0 a) p = (Ah p a : K) / (4 * al W U p * mu W U a) := by
  fin_cases p
  exacts [hy_0 h a, hy_1 h a, hy_2 h a, hy_3 h a, hy_4 h a, hy_5 h a, hy_6 h a, hy_7 h a, hy_8 h a, hy_9 h a, hy_10 h a, hy_11 h a, hy_12 h a, hy_13 h a, hy_14 h a, hy_15 h a, hy_16 h a, hy_17 h a, hy_18 h a, hy_19 h a, hy_20 h a, hy_21 h a, hy_22 h a, hy_23 h a, hy_24 h a, hy_25 h a, hy_26 h a, hy_27 h a, hy_28 h a, hy_29 h a, hy_30 h a, hy_31 h a, hy_32 h a, hy_33 h a, hy_34 h a, hy_35 h a, hy_36 h a, hy_37 h a, hy_38 h a, hy_39 h a, hy_40 h a, hy_41 h a, hy_42 h a, hy_43 h a, hy_44 h a, hy_45 h a, hy_46 h a, hy_47 h a, hy_48 h a, hy_49 h a, hy_50 h a, hy_51 h a, hy_52 h a, hy_53 h a, hy_54 h a, hy_55 h a, hy_56 h a, hy_57 h a, hy_58 h a, hy_59 h a, hy_60 h a, hy_61 h a, hy_62 h a, hy_63 h a, hy_64 h a, hy_65 h a, hy_66 h a, hy_67 h a, hy_68 h a, hy_69 h a, hy_70 h a, hy_71 h a, hy_72 h a, hy_73 h a, hy_74 h a, hy_75 h a, hy_76 h a, hy_77 h a, hy_78 h a, hy_79 h a, hy_80 h a, hy_81 h a, hy_82 h a, hy_83 h a, hy_84 h a, hy_85 h a, hy_86 h a, hy_87 h a, hy_88 h a, hy_89 h a, hy_90 h a, hy_91 h a, hy_92 h a, hy_93 h a, hy_94 h a, hy_95 h a, hy_96 h a, hy_97 h a, hy_98 h a, hy_99 h a, hy_100 h a, hy_101 h a, hy_102 h a, hy_103 h a]

/-- **DYADICPORTS rigidity (P104).** -/
theorem rigid (h : Hyp W U) (p q : Fin 104) :
    Mx W U p q = al W U p / al W U q * ((∑ a, Ah p a * Ah q a : ℤ) : K) / 4 := by
  rw [frame_fac h F0 frF0 p q]
  simp only [hx_all h p, hy_all h q]
  have hp := al_ne h p
  have hq := al_ne h q
  push_cast
  rw [Finset.mul_sum, div_eq_mul_inv, Finset.sum_mul]
  refine Finset.sum_congr rfl (fun a _ => ?_)
  have := mu_ne h a
  field_simp

theorem rigid_lam (h : Hyp W U) : ∃ lam : Fin 104 → K, (∀ p, lam p ≠ 0) ∧
    ∀ p q, Mx W U p q = lam p / lam q * ((∑ a, Ah p a * Ah q a : ℤ) : K) / 4 :=
  ⟨al W U, al_ne h, rigid h⟩

end DW6

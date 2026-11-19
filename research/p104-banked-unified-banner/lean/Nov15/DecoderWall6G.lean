import Nov15.DecoderWall6
import Nov15.DecoderWall4Defs
/-! DecoderWall6G : `⟨Ah_p, Ah_q⟩ = 2·G104_pq` with `G104 = DW4.g` (DecoderWall4Data gramRows). -/
set_option maxHeartbeats 0
namespace DW6
def adot (p q : Fin 104) : ℤ := Ah p 0 * Ah q 0 + Ah p 1 * Ah q 1 + Ah p 2 * Ah q 2 + Ah p 3 * Ah q 3
  + Ah p 4 * Ah q 4 + Ah p 5 * Ah q 5 + Ah p 6 * Ah q 6 + Ah p 7 * Ah q 7
theorem gl_0 : ∀ q : Fin 104, adot 0 q = 2 * DW4.g 0 q.val := by decide
theorem gl_1 : ∀ q : Fin 104, adot 1 q = 2 * DW4.g 1 q.val := by decide
theorem gl_2 : ∀ q : Fin 104, adot 2 q = 2 * DW4.g 2 q.val := by decide
theorem gl_3 : ∀ q : Fin 104, adot 3 q = 2 * DW4.g 3 q.val := by decide
theorem gl_4 : ∀ q : Fin 104, adot 4 q = 2 * DW4.g 4 q.val := by decide
theorem gl_5 : ∀ q : Fin 104, adot 5 q = 2 * DW4.g 5 q.val := by decide
theorem gl_6 : ∀ q : Fin 104, adot 6 q = 2 * DW4.g 6 q.val := by decide
theorem gl_7 : ∀ q : Fin 104, adot 7 q = 2 * DW4.g 7 q.val := by decide
theorem gl_8 : ∀ q : Fin 104, adot 8 q = 2 * DW4.g 8 q.val := by decide
theorem gl_9 : ∀ q : Fin 104, adot 9 q = 2 * DW4.g 9 q.val := by decide
theorem gl_10 : ∀ q : Fin 104, adot 10 q = 2 * DW4.g 10 q.val := by decide
theorem gl_11 : ∀ q : Fin 104, adot 11 q = 2 * DW4.g 11 q.val := by decide
theorem gl_12 : ∀ q : Fin 104, adot 12 q = 2 * DW4.g 12 q.val := by decide
theorem gl_13 : ∀ q : Fin 104, adot 13 q = 2 * DW4.g 13 q.val := by decide
theorem gl_14 : ∀ q : Fin 104, adot 14 q = 2 * DW4.g 14 q.val := by decide
theorem gl_15 : ∀ q : Fin 104, adot 15 q = 2 * DW4.g 15 q.val := by decide
theorem gl_16 : ∀ q : Fin 104, adot 16 q = 2 * DW4.g 16 q.val := by decide
theorem gl_17 : ∀ q : Fin 104, adot 17 q = 2 * DW4.g 17 q.val := by decide
theorem gl_18 : ∀ q : Fin 104, adot 18 q = 2 * DW4.g 18 q.val := by decide
theorem gl_19 : ∀ q : Fin 104, adot 19 q = 2 * DW4.g 19 q.val := by decide
theorem gl_20 : ∀ q : Fin 104, adot 20 q = 2 * DW4.g 20 q.val := by decide
theorem gl_21 : ∀ q : Fin 104, adot 21 q = 2 * DW4.g 21 q.val := by decide
theorem gl_22 : ∀ q : Fin 104, adot 22 q = 2 * DW4.g 22 q.val := by decide
theorem gl_23 : ∀ q : Fin 104, adot 23 q = 2 * DW4.g 23 q.val := by decide
theorem gl_24 : ∀ q : Fin 104, adot 24 q = 2 * DW4.g 24 q.val := by decide
theorem gl_25 : ∀ q : Fin 104, adot 25 q = 2 * DW4.g 25 q.val := by decide
theorem gl_26 : ∀ q : Fin 104, adot 26 q = 2 * DW4.g 26 q.val := by decide
theorem gl_27 : ∀ q : Fin 104, adot 27 q = 2 * DW4.g 27 q.val := by decide
theorem gl_28 : ∀ q : Fin 104, adot 28 q = 2 * DW4.g 28 q.val := by decide
theorem gl_29 : ∀ q : Fin 104, adot 29 q = 2 * DW4.g 29 q.val := by decide
theorem gl_30 : ∀ q : Fin 104, adot 30 q = 2 * DW4.g 30 q.val := by decide
theorem gl_31 : ∀ q : Fin 104, adot 31 q = 2 * DW4.g 31 q.val := by decide
theorem gl_32 : ∀ q : Fin 104, adot 32 q = 2 * DW4.g 32 q.val := by decide
theorem gl_33 : ∀ q : Fin 104, adot 33 q = 2 * DW4.g 33 q.val := by decide
theorem gl_34 : ∀ q : Fin 104, adot 34 q = 2 * DW4.g 34 q.val := by decide
theorem gl_35 : ∀ q : Fin 104, adot 35 q = 2 * DW4.g 35 q.val := by decide
theorem gl_36 : ∀ q : Fin 104, adot 36 q = 2 * DW4.g 36 q.val := by decide
theorem gl_37 : ∀ q : Fin 104, adot 37 q = 2 * DW4.g 37 q.val := by decide
theorem gl_38 : ∀ q : Fin 104, adot 38 q = 2 * DW4.g 38 q.val := by decide
theorem gl_39 : ∀ q : Fin 104, adot 39 q = 2 * DW4.g 39 q.val := by decide
theorem gl_40 : ∀ q : Fin 104, adot 40 q = 2 * DW4.g 40 q.val := by decide
theorem gl_41 : ∀ q : Fin 104, adot 41 q = 2 * DW4.g 41 q.val := by decide
theorem gl_42 : ∀ q : Fin 104, adot 42 q = 2 * DW4.g 42 q.val := by decide
theorem gl_43 : ∀ q : Fin 104, adot 43 q = 2 * DW4.g 43 q.val := by decide
theorem gl_44 : ∀ q : Fin 104, adot 44 q = 2 * DW4.g 44 q.val := by decide
theorem gl_45 : ∀ q : Fin 104, adot 45 q = 2 * DW4.g 45 q.val := by decide
theorem gl_46 : ∀ q : Fin 104, adot 46 q = 2 * DW4.g 46 q.val := by decide
theorem gl_47 : ∀ q : Fin 104, adot 47 q = 2 * DW4.g 47 q.val := by decide
theorem gl_48 : ∀ q : Fin 104, adot 48 q = 2 * DW4.g 48 q.val := by decide
theorem gl_49 : ∀ q : Fin 104, adot 49 q = 2 * DW4.g 49 q.val := by decide
theorem gl_50 : ∀ q : Fin 104, adot 50 q = 2 * DW4.g 50 q.val := by decide
theorem gl_51 : ∀ q : Fin 104, adot 51 q = 2 * DW4.g 51 q.val := by decide
theorem gl_52 : ∀ q : Fin 104, adot 52 q = 2 * DW4.g 52 q.val := by decide
theorem gl_53 : ∀ q : Fin 104, adot 53 q = 2 * DW4.g 53 q.val := by decide
theorem gl_54 : ∀ q : Fin 104, adot 54 q = 2 * DW4.g 54 q.val := by decide
theorem gl_55 : ∀ q : Fin 104, adot 55 q = 2 * DW4.g 55 q.val := by decide
theorem gl_56 : ∀ q : Fin 104, adot 56 q = 2 * DW4.g 56 q.val := by decide
theorem gl_57 : ∀ q : Fin 104, adot 57 q = 2 * DW4.g 57 q.val := by decide
theorem gl_58 : ∀ q : Fin 104, adot 58 q = 2 * DW4.g 58 q.val := by decide
theorem gl_59 : ∀ q : Fin 104, adot 59 q = 2 * DW4.g 59 q.val := by decide
theorem gl_60 : ∀ q : Fin 104, adot 60 q = 2 * DW4.g 60 q.val := by decide
theorem gl_61 : ∀ q : Fin 104, adot 61 q = 2 * DW4.g 61 q.val := by decide
theorem gl_62 : ∀ q : Fin 104, adot 62 q = 2 * DW4.g 62 q.val := by decide
theorem gl_63 : ∀ q : Fin 104, adot 63 q = 2 * DW4.g 63 q.val := by decide
theorem gl_64 : ∀ q : Fin 104, adot 64 q = 2 * DW4.g 64 q.val := by decide
theorem gl_65 : ∀ q : Fin 104, adot 65 q = 2 * DW4.g 65 q.val := by decide
theorem gl_66 : ∀ q : Fin 104, adot 66 q = 2 * DW4.g 66 q.val := by decide
theorem gl_67 : ∀ q : Fin 104, adot 67 q = 2 * DW4.g 67 q.val := by decide
theorem gl_68 : ∀ q : Fin 104, adot 68 q = 2 * DW4.g 68 q.val := by decide
theorem gl_69 : ∀ q : Fin 104, adot 69 q = 2 * DW4.g 69 q.val := by decide
theorem gl_70 : ∀ q : Fin 104, adot 70 q = 2 * DW4.g 70 q.val := by decide
theorem gl_71 : ∀ q : Fin 104, adot 71 q = 2 * DW4.g 71 q.val := by decide
theorem gl_72 : ∀ q : Fin 104, adot 72 q = 2 * DW4.g 72 q.val := by decide
theorem gl_73 : ∀ q : Fin 104, adot 73 q = 2 * DW4.g 73 q.val := by decide
theorem gl_74 : ∀ q : Fin 104, adot 74 q = 2 * DW4.g 74 q.val := by decide
theorem gl_75 : ∀ q : Fin 104, adot 75 q = 2 * DW4.g 75 q.val := by decide
theorem gl_76 : ∀ q : Fin 104, adot 76 q = 2 * DW4.g 76 q.val := by decide
theorem gl_77 : ∀ q : Fin 104, adot 77 q = 2 * DW4.g 77 q.val := by decide
theorem gl_78 : ∀ q : Fin 104, adot 78 q = 2 * DW4.g 78 q.val := by decide
theorem gl_79 : ∀ q : Fin 104, adot 79 q = 2 * DW4.g 79 q.val := by decide
theorem gl_80 : ∀ q : Fin 104, adot 80 q = 2 * DW4.g 80 q.val := by decide
theorem gl_81 : ∀ q : Fin 104, adot 81 q = 2 * DW4.g 81 q.val := by decide
theorem gl_82 : ∀ q : Fin 104, adot 82 q = 2 * DW4.g 82 q.val := by decide
theorem gl_83 : ∀ q : Fin 104, adot 83 q = 2 * DW4.g 83 q.val := by decide
theorem gl_84 : ∀ q : Fin 104, adot 84 q = 2 * DW4.g 84 q.val := by decide
theorem gl_85 : ∀ q : Fin 104, adot 85 q = 2 * DW4.g 85 q.val := by decide
theorem gl_86 : ∀ q : Fin 104, adot 86 q = 2 * DW4.g 86 q.val := by decide
theorem gl_87 : ∀ q : Fin 104, adot 87 q = 2 * DW4.g 87 q.val := by decide
theorem gl_88 : ∀ q : Fin 104, adot 88 q = 2 * DW4.g 88 q.val := by decide
theorem gl_89 : ∀ q : Fin 104, adot 89 q = 2 * DW4.g 89 q.val := by decide
theorem gl_90 : ∀ q : Fin 104, adot 90 q = 2 * DW4.g 90 q.val := by decide
theorem gl_91 : ∀ q : Fin 104, adot 91 q = 2 * DW4.g 91 q.val := by decide
theorem gl_92 : ∀ q : Fin 104, adot 92 q = 2 * DW4.g 92 q.val := by decide
theorem gl_93 : ∀ q : Fin 104, adot 93 q = 2 * DW4.g 93 q.val := by decide
theorem gl_94 : ∀ q : Fin 104, adot 94 q = 2 * DW4.g 94 q.val := by decide
theorem gl_95 : ∀ q : Fin 104, adot 95 q = 2 * DW4.g 95 q.val := by decide
theorem gl_96 : ∀ q : Fin 104, adot 96 q = 2 * DW4.g 96 q.val := by decide
theorem gl_97 : ∀ q : Fin 104, adot 97 q = 2 * DW4.g 97 q.val := by decide
theorem gl_98 : ∀ q : Fin 104, adot 98 q = 2 * DW4.g 98 q.val := by decide
theorem gl_99 : ∀ q : Fin 104, adot 99 q = 2 * DW4.g 99 q.val := by decide
theorem gl_100 : ∀ q : Fin 104, adot 100 q = 2 * DW4.g 100 q.val := by decide
theorem gl_101 : ∀ q : Fin 104, adot 101 q = 2 * DW4.g 101 q.val := by decide
theorem gl_102 : ∀ q : Fin 104, adot 102 q = 2 * DW4.g 102 q.val := by decide
theorem gl_103 : ∀ q : Fin 104, adot 103 q = 2 * DW4.g 103 q.val := by decide
theorem gram_link (p q : Fin 104) : (∑ a, Ah p a * Ah q a) = 2 * DW4.g p.val q.val := by
  rw [Fin.sum_univ_eight]
  show adot p q = _
  fin_cases p
  exacts [gl_0 q, gl_1 q, gl_2 q, gl_3 q, gl_4 q, gl_5 q, gl_6 q, gl_7 q, gl_8 q, gl_9 q, gl_10 q, gl_11 q, gl_12 q, gl_13 q, gl_14 q, gl_15 q, gl_16 q, gl_17 q, gl_18 q, gl_19 q, gl_20 q, gl_21 q, gl_22 q, gl_23 q, gl_24 q, gl_25 q, gl_26 q, gl_27 q, gl_28 q, gl_29 q, gl_30 q, gl_31 q, gl_32 q, gl_33 q, gl_34 q, gl_35 q, gl_36 q, gl_37 q, gl_38 q, gl_39 q, gl_40 q, gl_41 q, gl_42 q, gl_43 q, gl_44 q, gl_45 q, gl_46 q, gl_47 q, gl_48 q, gl_49 q, gl_50 q, gl_51 q, gl_52 q, gl_53 q, gl_54 q, gl_55 q, gl_56 q, gl_57 q, gl_58 q, gl_59 q, gl_60 q, gl_61 q, gl_62 q, gl_63 q, gl_64 q, gl_65 q, gl_66 q, gl_67 q, gl_68 q, gl_69 q, gl_70 q, gl_71 q, gl_72 q, gl_73 q, gl_74 q, gl_75 q, gl_76 q, gl_77 q, gl_78 q, gl_79 q, gl_80 q, gl_81 q, gl_82 q, gl_83 q, gl_84 q, gl_85 q, gl_86 q, gl_87 q, gl_88 q, gl_89 q, gl_90 q, gl_91 q, gl_92 q, gl_93 q, gl_94 q, gl_95 q, gl_96 q, gl_97 q, gl_98 q, gl_99 q, gl_100 q, gl_101 q, gl_102 q, gl_103 q]

variable {T K : Type*} [Fintype T] [DecidableEq T] [Field K] [CharZero K] {W U : Fin 104 → T → K}

/-- **DYADICPORTS rigidity, Gram form**: `M = Λ (G104/2) Λ⁻¹`. -/
theorem rigid_gram (h : Hyp W U) : ∃ lam : Fin 104 → K, (∀ p, lam p ≠ 0) ∧
    ∀ p q, Mx W U p q = lam p / lam q * (DW4.g p.val q.val : K) / 2 := by
  refine ⟨al W U, al_ne h, fun p q => ?_⟩
  rw [rigid h p q, gram_link p q]
  push_cast
  ring

end DW6

import Contract

/-! Exact kernel examples and hypothesis counterexamples. No native_decide.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0. -/

open Matrix DecoderRankBound

namespace DecoderRankExamples

def binaryMatrix : Matrix (Fin 2) (Fin 3) (ZMod 2) := !![1, 1, 0; 0, 1, 1]
def firstTwo : Fin 2 → Fin 3 := fun i => ⟨i.val, by omega⟩

/-- The output is rectangular and has a nonzero off-diagonal entry. -/
theorem rectangular_non_diagonal : binaryMatrix 0 1 = 1 := rfl

/-- This actual proper field extension exercises the base-field cost. -/
abbrev Extension := RatFunc (ZMod 2)

theorem rational_function_minor :
    ((DecoderRankBound.hadamard (ZMod.castHom (dvd_refl 2) Extension) binaryMatrix
      (fun (_ : Fin 1) (_ : Fin 2) => (1 : Extension))
      (fun (_ : Fin 1) (_ : Fin 3) => (1 : Extension))).submatrix id firstTwo).det ≠ 0 := by
  norm_num [DecoderRankBound.hadamard, binaryMatrix, firstTwo, Matrix.det_fin_two, Matrix.submatrix]

theorem rectangular_cost_at_least_two :
    2 ≤ cost binaryMatrix (fun (_ : Fin 1) => Finset.univ) (fun _ => Finset.univ) := by
  have bound := minor_le_cost (ZMod.castHom (dvd_refl 2) Extension) binaryMatrix
    (fun (_ : Fin 1) (_ : Fin 2) => (1 : Extension))
    (fun (_ : Fin 1) (_ : Fin 3) => (1 : Extension))
    (fun _ => Finset.univ) (fun _ => Finset.univ)
    (by intros; simp) (by intros; simp) id firstTwo rational_function_minor
  simpa using bound

theorem empty_term_family {F I J : Type*} [Field F] [Fintype I] [Fintype J]
    [DecidableEq I] [DecidableEq J] (B : Matrix I J F)
    (p : Fin 0 → I → F) (q : Fin 0 → J → F)
    (S : Fin 0 → Finset I) (U : Fin 0 → Finset J) :
    (weighted (RingHom.id F) B p q).rank = 0 ∧ cost B S U = 0 := by
  simp [weighted, cost]

theorem zero_left_support {F I J T : Type*} [Field F] [Fintype I] [Fintype J]
    [Fintype T] [DecidableEq I] [DecidableEq J]
    (B : Matrix I J F) (q : T → J → F) :
    (weighted (RingHom.id F) B (fun _ _ => 0) q).rank = 0 := by
  simp [weighted]

def oneMatrix : Matrix (Fin 1) (Fin 1) (ZMod 2) := 1

theorem unit_output_rank :
    (DecoderRankBound.hadamard (RingHom.id (ZMod 2)) oneMatrix
      (fun (_ : Fin 1) _ => 1) (fun _ _ => 1)).rank = 1 := by
  have h : DecoderRankBound.hadamard (RingHom.id (ZMod 2)) oneMatrix
      (fun (_ : Fin 1) _ => 1) (fun _ _ => 1) = 1 := by
    ext i j
    simp [DecoderRankBound.hadamard, oneMatrix]
  rw [h, Matrix.rank_one]
  rfl

/-- Dropping the left support condition would allow the false bound 1 ≤ 0. -/
theorem missing_left_support_counterexample :
    ¬ (DecoderRankBound.hadamard (RingHom.id (ZMod 2)) oneMatrix
      (fun (_ : Fin 1) _ => 1) (fun _ _ => 1)).rank ≤
      cost oneMatrix (fun (_ : Fin 1) => ∅) (fun _ => Finset.univ) := by
  rw [unit_output_rank]
  simp only [cost, Fin.sum_univ_succ, Fin.sum_univ_zero, add_zero, not_le, Nat.lt_one_iff]
  apply Nat.eq_zero_of_le_zero
  simpa using Matrix.rank_le_card_height
    (oneMatrix.submatrix ((↑) : ↥(∅ : Finset (Fin 1)) → Fin 1)
      ((↑) : ↥(Finset.univ : Finset (Fin 1)) → Fin 1))

/-- The right support condition is independently necessary. -/
theorem missing_right_support_counterexample :
    ¬ (DecoderRankBound.hadamard (RingHom.id (ZMod 2)) oneMatrix
      (fun (_ : Fin 1) _ => 1) (fun _ _ => 1)).rank ≤
      cost oneMatrix (fun (_ : Fin 1) => Finset.univ) (fun _ => ∅) := by
  rw [unit_output_rank]
  simp only [cost, Fin.sum_univ_succ, Fin.sum_univ_zero, add_zero, not_le, Nat.lt_one_iff]
  apply Nat.eq_zero_of_le_zero
  simpa using Matrix.rank_le_card_width
    (oneMatrix.submatrix ((↑) : ↥(Finset.univ : Finset (Fin 1)) → Fin 1)
      ((↑) : ↥(∅ : Finset (Fin 1)) → Fin 1))

/-- A zero determinant cannot certify the size of its square minor. -/
theorem zero_minor_counterexample :
    ¬ 1 ≤ cost (0 : Matrix (Fin 1) (Fin 1) (ZMod 2))
      (fun (_ : Fin 1) => Finset.univ) (fun _ => Finset.univ) := by
  simp [cost]

/-- Entrywise reinterpretation in characteristic zero is not a field map. -/
theorem no_wrong_characteristic_map : ¬ Nonempty (ZMod 2 →+* ℚ) := by
  rintro ⟨f⟩
  have bad : f (2 : ZMod 2) = (2 : ℚ) := map_natCast f 2
  rw [show (2 : ZMod 2) = 0 by decide, map_zero] at bad
  exact (by norm_num : (0 : ℚ) ≠ 2) bad


end DecoderRankExamples

#print axioms DecoderRankExamples.rectangular_cost_at_least_two
#print axioms DecoderRankExamples.empty_term_family
#print axioms DecoderRankExamples.zero_left_support
#print axioms DecoderRankExamples.missing_left_support_counterexample
#print axioms DecoderRankExamples.missing_right_support_counterexample
#print axioms DecoderRankExamples.zero_minor_counterexample
#print axioms DecoderRankExamples.no_wrong_characteristic_map

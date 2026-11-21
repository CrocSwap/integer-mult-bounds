import Nov15.LinKbarC0
import Nov15.LinKbarC1
import Nov15.LinKbarC2
import Nov15.LinKbarC3
import Nov15.LinCB
/-!
LINKBARFIN (lane LEANCB).  mod-2 kernel of the P104 decoder law: {0, B}, and the dependent orthogonal quadruple.
-/
open Matrix Finset LinCore LinFinal

namespace P104
open P104Data

lemma kern_id_all : ∀ i j a b : Fin 8,
    (∑ r : Fin 63, if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then lab (selTf r) a * lab (selSf r) b else 0) =
      (if a = i ∧ b = j then 1 else 0) + Bm i j * (if a = 0 ∧ b = 1 then 1 else 0) := by
  intro i j a b
  fin_cases i
  · exact kern_id0 j a b
  · exact kern_id1 j a b
  · exact kern_id2 j a b
  · exact kern_id3 j a b
  · exact kern_id4 j a b
  · exact kern_id5 j a b
  · exact kern_id6 j a b
  · exact kern_id7 j a b

lemma dot_expand (u s : Fin 8 → F2) (K : Matrix (Fin 8) (Fin 8) F2) :
    u ⬝ᵥ (K *ᵥ s) = ∑ a, ∑ b, K a b * (u a * s b) := by
  simp only [dotProduct, mulVec, Finset.mul_sum]
  exact Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun b _ => by ring

lemma swap3 (K : Fin 8 → Fin 8 → F2) (f : Fin 63 → Fin 8 → Fin 8 → F2) :
    ∑ r, ∑ a, ∑ b, K a b * f r a b = ∑ a, ∑ b, K a b * ∑ r, f r a b := by
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun a _ => ?_
  rw [Finset.sum_comm]
  exact Finset.sum_congr rfl fun b _ => by rw [Finset.mul_sum]

lemma pick (g : Fin 8 → Fin 8 → F2) (i j : Fin 8) :
    ∑ a, ∑ b, g a b * (if a = i ∧ b = j then (1 : F2) else 0) = g i j := by
  rw [Finset.sum_eq_single i (fun a _ ha => ?_) (by simp)]
  · rw [Finset.sum_eq_single j (fun b _ hb => ?_) (by simp)]
    · simp
    · simp [hb]
  · apply Finset.sum_eq_zero; intro b _; simp [ha]

lemma coef_sum (K : Matrix (Fin 8) (Fin 8) F2) (i j : Fin 8) :
    ∑ a, ∑ b, K a b * ((if a = i ∧ b = j then (1 : F2) else 0) + Bm i j * (if a = 0 ∧ b = 1 then 1 else 0)) =
      K i j + Bm i j * K 0 1 := by
  have h1 := pick (fun a b => K a b) i j
  have h2 := pick (fun a b => K a b * Bm i j) 0 1
  simp only [mul_add, Finset.sum_add_distrib]
  have h3 : ∀ a b : Fin 8, K a b * (Bm i j * (if a = 0 ∧ b = 1 then (1 : F2) else 0)) =
      K a b * Bm i j * (if a = 0 ∧ b = 1 then (1 : F2) else 0) := fun a b => (mul_assoc _ _ _).symm
  simp only [h3]
  rw [h1, h2]
  ring

/-- mod-2 kernel of the decoder law on P104: K ∈ {0, B}. -/
theorem kern_B (K : Matrix (Fin 8) (Fin 8) F2)
    (h : ∀ t s, (Bm *ᵥ lab t) ⬝ᵥ lab s = 0 → lab t ⬝ᵥ (K *ᵥ lab s) = 0) :
    ∀ i j, K i j = Bm i j * K 0 1 := by
  intro i j
  set tb : Fin 63 → Prop := fun r => (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 = true with htb
  have h1 : (∑ r : Fin 63, if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then
      lab (selTf r) ⬝ᵥ (K *ᵥ lab (selSf r)) else 0) = 0 :=
    Finset.sum_eq_zero fun r _ => by
      split_ifs
      · exact h _ _ (sel_orth r)
      · rfl
  have h2 : (∑ r : Fin 63, if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then
      lab (selTf r) ⬝ᵥ (K *ᵥ lab (selSf r)) else 0) = K i j + Bm i j * K 0 1 := by
    have e : ∀ r : Fin 63, (if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then
        lab (selTf r) ⬝ᵥ (K *ᵥ lab (selSf r)) else 0) =
        ∑ a, ∑ b, K a b * (if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then
          lab (selTf r) a * lab (selSf r) b else 0) := by
      intro r
      split_ifs
      · exact dot_expand _ _ _
      · simp
    rw [Finset.sum_congr rfl fun r _ => e r, swap3 K (fun r a b => if (lamM.getD (i.1 * 8 + j.1) 0).testBit r.1 then
          lab (selTf r) a * lab (selSf r) b else 0)]
    simp only [kern_id_all]
    exact coef_sum K i j
  have h3 := h1.symm.trans h2
  have h4 : K i j = - (Bm i j * K 0 1) := eq_neg_of_add_eq_zero_left h3.symm
  rw [h4, ZMod.neg_eq_self_mod_two]

/-- non-vacuity: B itself satisfies the kernel hypothesis, and B is not 0. -/
lemma Bm_in_kernel : ∀ t s, (Bm *ᵥ lab t) ⬝ᵥ lab s = 0 → lab t ⬝ᵥ (Bm *ᵥ lab s) = 0 := by
  intro t s h
  rw [← hsd Bm Bm_symm]; exact h

lemma Bm_ne : Bm 0 1 = 1 := by decide

lemma dep_sum : ∀ a : Fin 8, lab 0 a + lab 6 a + lab 16 a + lab 95 a = 0 := by decide +kernel
lemma dep_orth0 : (Bm *ᵥ lab 6) ⬝ᵥ lab 0 = 0 := by decide +kernel
lemma dep_orth1 : (Bm *ᵥ lab 16) ⬝ᵥ lab 0 = 0 := by decide +kernel
lemma dep_orth2 : (Bm *ᵥ lab 95) ⬝ᵥ lab 0 = 0 := by decide +kernel

#print axioms P104.kern_B

end P104

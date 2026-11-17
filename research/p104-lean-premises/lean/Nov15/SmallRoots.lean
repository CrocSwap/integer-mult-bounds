/-
(Nov 17): kernel check that the SMALLCALLER exact rational roots 1|1 (A and B form) and 2|2 (A form)
satisfy the root conditions of rc.py (algebraic core only).  See SmallRoots.md for the scope.
Kernel only: no sorry, no native_decide.
-/
import Nov15.SmallRootsA22Corners
namespace SmallRoots

namespace A11c
theorem shape : A11_X.length = 6 + 2 ∧ A11_Y.length = 6 + 2 ∧ (∀ r ∈ A11_X, r.length = 6) ∧ ∀ r ∈ A11_Y, r.length = 6 := by decide +kernel
theorem isotropy : ∀ p ∈ List.zip A11_X A11_Y, dotv p.2 p.1 = 0 := by decide +kernel
theorem nonzero : ∀ p ∈ List.zip A11_X A11_Y, (∃ v ∈ p.1, v ≠ 0) ∧ ∃ v ∈ p.2, v ≠ 0 := by decide +kernel
theorem product : pref 6 A11_X A11_Y (6 + 2) = negIdMat 6 := by decide +kernel
theorem ordered : (A11_st.map (·.u0)).Pairwise (fun a b => a + 1 < b) ∧ ∀ s ∈ A11_st, s.u0 + 1 < 6 + 2 := by decide +kernel
theorem inside : ∀ s ∈ A11_st, inMask 6 A11_X A11_Y s := by decide +kernel
theorem before : ∀ s ∈ A11_st, commMask 6 s.mask (pref 6 A11_X A11_Y s.u0) := by decide +kernel
theorem after : ∀ s ∈ A11_st, commMask 6 s.mask (pref 6 A11_X A11_Y (s.u0 + 2)) := by decide +kernel
theorem len : A11_st.length = 2 := by decide +kernel
theorem bits_eq : bits 2 = [[0, 0], [1, 0], [0, 1], [1, 1]] := by decide +kernel
theorem corner0 : Mend 6 A11_X A11_Y A11_st ([0, 0] : List ℚ) = tgtD 6 A11_st ([0, 0] : List ℚ) := by decide +kernel
theorem corner1 : Mend 6 A11_X A11_Y A11_st ([1, 0] : List ℚ) = tgtD 6 A11_st ([1, 0] : List ℚ) := by decide +kernel
theorem corner2 : Mend 6 A11_X A11_Y A11_st ([0, 1] : List ℚ) = tgtD 6 A11_st ([0, 1] : List ℚ) := by decide +kernel
theorem corner3 : Mend 6 A11_X A11_Y A11_st ([1, 1] : List ℚ) = tgtD 6 A11_st ([1, 1] : List ℚ) := by decide +kernel
theorem symbolic : ∀ D ∈ bits A11_st.length, Mend 6 A11_X A11_Y A11_st D = tgtD 6 A11_st D := by
  rw [len, bits_eq]
  intro D hD
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hD
  rcases hD with rfl | rfl | rfl | rfl
  · exact corner0
  · exact corner1
  · exact corner2
  · exact corner3
theorem pairs : ∀ s ∈ A11_st, (dotv (A11_Y.getD s.u0 []) (A11_X.getD (s.u0 + 1) []), dotv (A11_Y.getD (s.u0 + 1) []) (A11_X.getD s.u0 [])) = A11_pair := by decide +kernel
theorem rG : rankCert 6 (gram A11_X A11_Y) A11_rkG := by decide +kernel
theorem rX : rankCert 6 A11_X A11_rkX := by decide +kernel
theorem rY : rankCert 6 A11_Y A11_rkY := by decide +kernel
theorem conn : (reach (gram A11_X A11_Y) true).length = 6 + 2 ∧ (reach (gram A11_X A11_Y) false).length = 6 + 2 := by decide +kernel
end A11c

theorem smallcaller_1_1_A : IsRoot 6 A11_X A11_Y A11_st A11_pair :=
  ⟨A11c.shape, A11c.isotropy, A11c.nonzero, A11c.product, A11c.ordered, A11c.inside, A11c.before, A11c.after,
   A11c.symbolic, A11c.pairs, ⟨_, A11c.rG⟩, ⟨_, A11c.rX⟩, ⟨_, A11c.rY⟩, A11c.conn⟩

namespace B11c
theorem shape : B11_X.length = 6 + 2 ∧ B11_Y.length = 6 + 2 ∧ (∀ r ∈ B11_X, r.length = 6) ∧ ∀ r ∈ B11_Y, r.length = 6 := by decide +kernel
theorem isotropy : ∀ p ∈ List.zip B11_X B11_Y, dotv p.2 p.1 = 0 := by decide +kernel
theorem nonzero : ∀ p ∈ List.zip B11_X B11_Y, (∃ v ∈ p.1, v ≠ 0) ∧ ∃ v ∈ p.2, v ≠ 0 := by decide +kernel
theorem product : pref 6 B11_X B11_Y (6 + 2) = negIdMat 6 := by decide +kernel
theorem ordered : (B11_st.map (·.u0)).Pairwise (fun a b => a + 1 < b) ∧ ∀ s ∈ B11_st, s.u0 + 1 < 6 + 2 := by decide +kernel
theorem inside : ∀ s ∈ B11_st, inMask 6 B11_X B11_Y s := by decide +kernel
theorem before : ∀ s ∈ B11_st, commMask 6 s.mask (pref 6 B11_X B11_Y s.u0) := by decide +kernel
theorem after : ∀ s ∈ B11_st, commMask 6 s.mask (pref 6 B11_X B11_Y (s.u0 + 2)) := by decide +kernel
theorem len : B11_st.length = 2 := by decide +kernel
theorem bits_eq : bits 2 = [[0, 0], [1, 0], [0, 1], [1, 1]] := by decide +kernel
theorem corner0 : Mend 6 B11_X B11_Y B11_st ([0, 0] : List ℚ) = tgtD 6 B11_st ([0, 0] : List ℚ) := by decide +kernel
theorem corner1 : Mend 6 B11_X B11_Y B11_st ([1, 0] : List ℚ) = tgtD 6 B11_st ([1, 0] : List ℚ) := by decide +kernel
theorem corner2 : Mend 6 B11_X B11_Y B11_st ([0, 1] : List ℚ) = tgtD 6 B11_st ([0, 1] : List ℚ) := by decide +kernel
theorem corner3 : Mend 6 B11_X B11_Y B11_st ([1, 1] : List ℚ) = tgtD 6 B11_st ([1, 1] : List ℚ) := by decide +kernel
theorem symbolic : ∀ D ∈ bits B11_st.length, Mend 6 B11_X B11_Y B11_st D = tgtD 6 B11_st D := by
  rw [len, bits_eq]
  intro D hD
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hD
  rcases hD with rfl | rfl | rfl | rfl
  · exact corner0
  · exact corner1
  · exact corner2
  · exact corner3
theorem pairs : ∀ s ∈ B11_st, (dotv (B11_Y.getD s.u0 []) (B11_X.getD (s.u0 + 1) []), dotv (B11_Y.getD (s.u0 + 1) []) (B11_X.getD s.u0 [])) = B11_pair := by decide +kernel
theorem rG : rankCert 6 (gram B11_X B11_Y) B11_rkG := by decide +kernel
theorem rX : rankCert 6 B11_X B11_rkX := by decide +kernel
theorem rY : rankCert 6 B11_Y B11_rkY := by decide +kernel
theorem conn : (reach (gram B11_X B11_Y) true).length = 6 + 2 ∧ (reach (gram B11_X B11_Y) false).length = 6 + 2 := by decide +kernel
end B11c

theorem smallcaller_1_1_B : IsRoot 6 B11_X B11_Y B11_st B11_pair :=
  ⟨B11c.shape, B11c.isotropy, B11c.nonzero, B11c.product, B11c.ordered, B11c.inside, B11c.before, B11c.after,
   B11c.symbolic, B11c.pairs, ⟨_, B11c.rG⟩, ⟨_, B11c.rX⟩, ⟨_, B11c.rY⟩, B11c.conn⟩

namespace A22c
theorem shape : A22_X.length = 10 + 2 ∧ A22_Y.length = 10 + 2 ∧ (∀ r ∈ A22_X, r.length = 10) ∧ ∀ r ∈ A22_Y, r.length = 10 := by decide +kernel
theorem isotropy : ∀ p ∈ List.zip A22_X A22_Y, dotv p.2 p.1 = 0 := by decide +kernel
theorem nonzero : ∀ p ∈ List.zip A22_X A22_Y, (∃ v ∈ p.1, v ≠ 0) ∧ ∃ v ∈ p.2, v ≠ 0 := by decide +kernel
theorem product : pref 10 A22_X A22_Y (10 + 2) = negIdMat 10 := by decide +kernel
theorem ordered : (A22_st.map (·.u0)).Pairwise (fun a b => a + 1 < b) ∧ ∀ s ∈ A22_st, s.u0 + 1 < 10 + 2 := by decide +kernel
theorem inside : ∀ s ∈ A22_st, inMask 10 A22_X A22_Y s := by decide +kernel
theorem before : ∀ s ∈ A22_st, commMask 10 s.mask (pref 10 A22_X A22_Y s.u0) := by decide +kernel
theorem after : ∀ s ∈ A22_st, commMask 10 s.mask (pref 10 A22_X A22_Y (s.u0 + 2)) := by decide +kernel
theorem len : A22_st.length = 4 := by decide +kernel
theorem bits_eq : bits 4 = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [1, 0, 1, 0], [0, 1, 1, 0], [1, 1, 1, 0], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]] := by decide +kernel
theorem symbolic : ∀ D ∈ bits A22_st.length, Mend 10 A22_X A22_Y A22_st D = tgtD 10 A22_st D := by
  rw [len, bits_eq]
  intro D hD
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hD
  rcases hD with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact corner0
  · exact corner1
  · exact corner2
  · exact corner3
  · exact corner4
  · exact corner5
  · exact corner6
  · exact corner7
  · exact corner8
  · exact corner9
  · exact corner10
  · exact corner11
  · exact corner12
  · exact corner13
  · exact corner14
  · exact corner15
theorem pairs : ∀ s ∈ A22_st, (dotv (A22_Y.getD s.u0 []) (A22_X.getD (s.u0 + 1) []), dotv (A22_Y.getD (s.u0 + 1) []) (A22_X.getD s.u0 [])) = A22_pair := by decide +kernel
theorem rG : rankCert 10 (gram A22_X A22_Y) A22_rkG := by decide +kernel
theorem rX : rankCert 10 A22_X A22_rkX := by decide +kernel
theorem rY : rankCert 10 A22_Y A22_rkY := by decide +kernel
theorem conn : (reach (gram A22_X A22_Y) true).length = 10 + 2 ∧ (reach (gram A22_X A22_Y) false).length = 10 + 2 := by decide +kernel
end A22c

theorem smallcaller_2_2_A : IsRoot 10 A22_X A22_Y A22_st A22_pair :=
  ⟨A22c.shape, A22c.isotropy, A22c.nonzero, A22c.product, A22c.ordered, A22c.inside, A22c.before, A22c.after,
   A22c.symbolic, A22c.pairs, ⟨_, A22c.rG⟩, ⟨_, A22c.rX⟩, ⟨_, A22c.rY⟩, A22c.conn⟩

/-- the pair types are exactly A = (0,0) and B = (-1, 1/2). -/
theorem pair_types : A11_pair = (0, 0) ∧ A22_pair = (0, 0) ∧ B11_pair = (-1, 1/2) := by decide +kernel

end SmallRoots

#print axioms SmallRoots.smallcaller_1_1_A
#print axioms SmallRoots.smallcaller_1_1_B
#print axioms SmallRoots.smallcaller_2_2_A
#print axioms SmallRoots.pair_types

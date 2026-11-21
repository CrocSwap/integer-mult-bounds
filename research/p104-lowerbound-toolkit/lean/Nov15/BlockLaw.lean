import Nov15.BlockComplete
import Mathlib.LinearAlgebra.Span.Defs
import Mathlib.Tactic.Ring
import Mathlib.Algebra.Module.Pi
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Dimension.Free
import Mathlib.LinearAlgebra.Pi
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Algebra.Field.ZMod
namespace BlockLaw
open FrameCert BlockComplete

instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

abbrev V := Fin 9 → ZMod 2

def vecOf (n : Nat) : V := fun j => if n.testBit j.val then 1 else 0
def lab (t : Fin 104) : V := vecOf (labelAt t.val)
def dotN (u : Nat) (v : V) : ZMod 2 := ∑ j : Fin 9, if u.testBit j.val then v j else 0

def b2z (b : Bool) : ZMod 2 := if b then 1 else 0

lemma b2z_xor (x y : Bool) : b2z (x ^^ y) = b2z x + b2z y := by
  cases x <;> cases y <;> decide

/-- generic fold over the 104 ports: bit s of colMask j is the j-th label bit of port s -/
lemma colfold (j : Nat) : ∀ (l : List Nat) (acc s : Nat),
    (l.foldl (fun a t => if (labelAt t).testBit j then a ||| 2 ^ t else a) acc).testBit s =
      (acc.testBit s || (decide (s ∈ l) && (labelAt s).testBit j)) := by
  intro l
  induction l with
  | nil => intro acc s; simp
  | cons t ts ih =>
    intro acc s
    simp only [List.foldl_cons, ih, List.mem_cons]
    by_cases hl : (labelAt t).testBit j = true
    · simp only [hl, if_true, Nat.testBit_or, Nat.testBit_two_pow]
      by_cases hst : s = t
      · subst hst; simp [hl]
      · have : ¬ (t = s) := fun h => hst h.symm
        simp [hst, this]
    · have hl' : (labelAt t).testBit j = false := by simpa using hl
      simp only [hl', Bool.false_eq_true, if_false]
      by_cases hst : s = t
      · subst hst; simp [hl']
      · simp [hst]

lemma colMask_testBit (j s : Nat) (hs : s < 104) :
    (colMask j).testBit s = (labelAt s).testBit j := by
  unfold colMask
  rw [colfold]
  simp [hs]


lemma pmL_bit (u t : Nat) (ht : t < 104) : ∀ l : List Nat,
    b2z ((pmL u l).testBit t) =
      (l.map (fun j => if (u.testBit j && (labelAt t).testBit j) = true then (1 : ZMod 2) else 0)).sum := by
  intro l
  induction l with
  | nil => simp [pmL, b2z]
  | cons j js ih =>
    simp only [pmL, Nat.testBit_xor, b2z_xor, ih, List.map_cons, List.sum_cons]
    congr 1
    by_cases hu : u.testBit j = true
    · simp [hu, colMask_testBit j t ht, b2z]
    · have hu' : u.testBit j = false := by simpa using hu
      simp [hu', b2z]

lemma dotN_eq_list (u : Nat) (v : V) :
    dotN u v = ((List.range 9).map (fun j => if u.testBit j = true then (if h : j < 9 then v ⟨j, h⟩ else 0) else 0)).sum := by
  simp [dotN, Fin.sum_univ_succ, List.range_succ]


lemma dot_lab (u : Nat) (t : Fin 104) : dotN u (lab t) = b2z ((parMask u).testBit t.val) := by
  rw [parMask_eq_pmL, pmL_bit u t.val t.isLt, dotN_eq_list]
  congr 1
  apply List.map_congr_left
  intro j hj
  have hj9 : j < 9 := List.mem_range.1 hj
  simp only [hj9, dif_pos, lab, vecOf]
  by_cases h1 : u.testBit j = true <;> by_cases h2 : (labelAt t.val).testBit j = true <;> simp [h1, h2]

lemma z2_zero_iff (a : ZMod 2) : a = 0 ↔ ¬ a = 1 := by revert a; decide
lemma b2z_eq_one (b : Bool) : b2z b = 1 ↔ b = true := by cases b <;> simp [b2z]

/-- Lam(u1,u2) = ports whose label is annihilated by both normals -/
theorem lam_bit (u1 u2 : Nat) (t : Fin 104) :
    (lamMask u1 u2).testBit t.val = true ↔ dotN u1 (lab t) = 0 ∧ dotN u2 (lab t) = 0 := by
  rw [dot_lab, dot_lab, z2_zero_iff, z2_zero_iff, b2z_eq_one, b2z_eq_one]
  unfold lamMask
  rw [Nat.testBit_xor, Nat.testBit_or, Nat.testBit_two_pow_sub_one]
  have := t.isLt
  simp [this]


open Classical in
/-- ports whose label lies in M -/
noncomputable def Lam (M : Submodule (ZMod 2) V) : Finset (Fin 104) :=
  Finset.univ.filter (fun t => lab t ∈ M)

lemma lamSet_eq_Lam (M : Submodule (ZMod 2) V) (u1 u2 : Nat)
    (hM : ∀ v, v ∈ M ↔ dotN u1 v = 0 ∧ dotN u2 v = 0) :
    lamSet (lamMask u1 u2) = Lam M := by
  ext t
  simp only [lamSet, Lam, Finset.mem_filter, Finset.mem_univ, true_and]
  rw [lam_bit, hM]

/-- ALL-OR-NOTHING for a 7-dim section given semantically (M = common kernel of two distinct nonzero
normals), blocking in the frame sense; no list / data hypothesis. -/
theorem all_or_nothing_sub (M : Submodule (ZMod 2) V) (u1 u2 : Nat) (h1 : 0 < u1) (h2 : 0 < u2)
    (hne : u1 ≠ u2) (h1' : u1 < 512) (h2' : u2 < 512)
    (hM : ∀ v, v ∈ M ↔ dotN u1 v = 0 ∧ dotN u2 v = 0)
    (hblock : ∀ i, i < 759 → ∃ t : Fin 104, (frameAt i).testBit t.val = true ∧ lab t ∈ M)
    (A B : Finset (Fin 104)) (H_FS4 : ind (A ∩ B) ∈ Fperp) (H_supp : ∀ t ∈ A, lab t ∈ M) :
    A ∩ B = ∅ ∨ (A = Lam M ∧ Lam M ⊆ B) := by
  have hb : ∀ i, i < 759 → frameAt i &&& lamMask u1 u2 ≠ 0 := by
    intro i hi h0
    obtain ⟨t, ht1, ht2⟩ := hblock i hi
    have hl : (lamMask u1 u2).testBit t.val = true := (lam_bit u1 u2 t).2 ((hM _).1 ht2)
    have := congrArg (fun x => x.testBit t.val) h0
    simp [Nat.testBit_and, ht1, hl] at this
  rw [← lamSet_eq_Lam M u1 u2 hM]
  refine all_or_nothing_blocking u1 u2 h1 h2 hne h1' h2' hb A B H_FS4 ?_
  intro t ht
  have h := H_supp t ht
  simp only [lamSet, Finset.mem_filter, Finset.mem_univ, true_and]
  exact (lam_bit u1 u2 t).2 ((hM _).1 h)

/-- ROW FORM with the span step: M = span of labels of D (support of row k), N = span of labels of S
(support of row l); A = odd support of row k inside D, B odd support of row l inside S.
Conclusion: A ∩ B = ∅, or (A = L ∩ M, L ∩ M ⊆ B and M ≤ N). -/
theorem all_or_nothing_rows_real (D S A B : Finset (Fin 104)) (u1 u2 : Nat) (h1 : 0 < u1) (h2 : 0 < u2)
    (hne : u1 ≠ u2) (h1' : u1 < 512) (h2' : u2 < 512)
    (hM : ∀ v, v ∈ Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104))) ↔
      dotN u1 v = 0 ∧ dotN u2 v = 0)
    (hblock : ∀ i, i < 759 → ∃ t : Fin 104, (frameAt i).testBit t.val = true ∧
      lab t ∈ Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104))))
    (hA : A ⊆ D) (hB : B ⊆ S) (H_FS4 : ind (A ∩ B) ∈ Fperp) :
    A ∩ B = ∅ ∨ (A = Lam (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) ∧
      Lam (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) ⊆ B ∧
      Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104))) ≤
        Submodule.span (ZMod 2) (lab '' (S : Set (Fin 104)))) := by
  have hD : ∀ t ∈ D, lab t ∈ Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104))) :=
    fun t ht => Submodule.subset_span ⟨t, ht, rfl⟩
  rcases all_or_nothing_sub _ u1 u2 h1 h2 hne h1' h2' hM hblock A B H_FS4
      (fun t ht => hD t (hA ht)) with h | ⟨hAL, hLB⟩
  · exact Or.inl h
  · refine Or.inr ⟨hAL, hLB, ?_⟩
    apply Submodule.span_le.2
    rintro _ ⟨t, ht, rfl⟩
    have htL : t ∈ Lam (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) := by
      classical
      simp only [Lam, Finset.mem_filter, Finset.mem_univ, true_and]
      exact hD t ht
    exact Submodule.subset_span ⟨t, hB (hLB htL), rfl⟩

lemma gfold (g : Nat → Bool) : ∀ (l : List Nat) (acc s : Nat),
    (l.foldl (fun a t => if g t = true then a ||| 2 ^ t else a) acc).testBit s =
      (acc.testBit s || (decide (s ∈ l) && g s)) := by
  intro l
  induction l with
  | nil => intro acc s; simp
  | cons t ts ih =>
    intro acc s
    simp only [List.foldl_cons, ih, List.mem_cons]
    by_cases hl : g t = true
    · simp only [hl, if_true, Nat.testBit_or, Nat.testBit_two_pow]
      by_cases hst : s = t
      · subst hst; simp [hl]
      · have : ¬ (t = s) := fun h => hst h.symm
        simp [hst, this]
    · have hl' : g t = false := by simpa using hl
      simp only [hl', Bool.false_eq_true, if_false]
      by_cases hst : s = t
      · subst hst; simp [hl']
      · simp [hst]

lemma vec_surj (c : V) : ∃ u : Nat, u < 512 ∧ vecOf u = c := by
  let g : Nat → Bool := fun j => if h : j < 9 then decide (c ⟨j, h⟩ = 1) else false
  let u := (List.range 9).foldl (fun a t => if g t = true then a ||| 2 ^ t else a) 0
  have hbit : ∀ s, u.testBit s = (decide (s < 9) && g s) := by
    intro s; simp only [u, gfold]; simp
  refine ⟨u, ?_, ?_⟩
  · have : u < 2 ^ 9 := by
      apply Nat.lt_pow_two_of_testBit
      intro i hi
      rw [hbit]; simp [show ¬ i < 9 by omega]
    simpa using this
  · funext j
    simp only [vecOf, hbit]
    have hj := j.isLt
    simp only [hj, decide_true, Bool.true_and, g, dif_pos]
    have : ∀ a : ZMod 2, (if decide (a = 1) = true then (1 : ZMod 2) else 0) = a := by decide
    simpa using this (c j)

lemma exists_code (φ : Module.Dual (ZMod 2) V) :
    ∃ u : Nat, u < 512 ∧ ∀ v, φ v = dotN u v := by
  obtain ⟨u, hlt, hu⟩ := vec_surj (fun j => φ (Pi.single j 1))
  refine ⟨u, hlt, fun v => ?_⟩
  rw [LinearMap.pi_apply_eq_sum_univ φ v]
  unfold dotN
  refine Finset.sum_congr rfl (fun j _ => ?_)
  have hj := congrFun hu j
  have e1 : (fun i => (if j = i then (1 : ZMod 2) else 0)) = Pi.single j 1 := by
    funext i; by_cases h : j = i <;> simp [Pi.single_apply, h, eq_comm]
  rw [e1]
  rw [← hj]
  simp only [vecOf]
  by_cases hb : u.testBit j.val = true <;> simp [hb]


lemma dotN_zero (v : V) : dotN 0 v = 0 := by simp [dotN]

/-- BRIDGE: a 7-dimensional subspace of F2^9 is the common kernel of two distinct nonzero normals < 512. -/
theorem exists_normals (M : Submodule (ZMod 2) V) (h7 : Module.finrank (ZMod 2) M = 7) :
    ∃ u1 u2 : Nat, 0 < u1 ∧ 0 < u2 ∧ u1 ≠ u2 ∧ u1 < 512 ∧ u2 < 512 ∧
      ∀ v, v ∈ M ↔ dotN u1 v = 0 ∧ dotN u2 v = 0 := by
  have hV : Module.finrank (ZMod 2) V = 9 := by simp
  have hsum := Subspace.finrank_add_finrank_dualAnnihilator_eq (K := ZMod 2) (V := V) M
  have hW : Module.finrank (ZMod 2) M.dualAnnihilator = 2 := by omega
  let b := Module.finBasisOfFinrankEq (ZMod 2) M.dualAnnihilator hW
  obtain ⟨u1, hu1, hφ1⟩ := exists_code (b 0 : Module.Dual (ZMod 2) V)
  obtain ⟨u2, hu2, hφ2⟩ := exists_code (b 1 : Module.Dual (ZMod 2) V)
  have hb0 : (b 0 : Module.Dual (ZMod 2) V) ≠ 0 := fun h => b.ne_zero 0 (Subtype.ext h)
  have hb01 : (b 0 : Module.Dual (ZMod 2) V) ≠ (b 1 : Module.Dual (ZMod 2) V) := fun h =>
    absurd (b.injective (Subtype.ext h)) (by decide)
  have hb1 : (b 1 : Module.Dual (ZMod 2) V) ≠ 0 := fun h => b.ne_zero 1 (Subtype.ext h)
  refine ⟨u1, u2, ?_, ?_, ?_, hu1, hu2, ?_⟩
  · rcases Nat.eq_zero_or_pos u1 with h | h
    · exfalso; exact hb0 (LinearMap.ext (fun v => by rw [hφ1, h, dotN_zero]; rfl))
    · exact h
  · rcases Nat.eq_zero_or_pos u2 with h | h
    · exfalso; exact hb1 (LinearMap.ext (fun v => by rw [hφ2, h, dotN_zero]; rfl))
    · exact h
  · intro h; exact hb01 (LinearMap.ext (fun v => by rw [hφ1, hφ2, h]))
  · intro v
    rw [← hφ1, ← hφ2]
    conv_lhs => rw [← Subspace.dualAnnihilator_dualCoannihilator_eq (W := M)]
    rw [Submodule.mem_dualCoannihilator]
    constructor
    · intro h
      exact ⟨h _ (b 0).2, h _ (b 1).2⟩
    · rintro ⟨h0, h1⟩ φ hφ
      have hx := b.sum_repr ⟨φ, hφ⟩
      have := congrArg (fun y : M.dualAnnihilator => (y : Module.Dual (ZMod 2) V) v) hx.symm
      simp only [Submodule.coe_sum, Submodule.coe_smul, LinearMap.sum_apply, Fin.sum_univ_two,
        LinearMap.smul_apply, Submodule.coe_add, LinearMap.add_apply] at this
      rw [this, h0, h1]; simp

/-- semantic frame-blocking: every one of the 759 frames contains a port whose label lies in M -/
def SemBlocking (M : Submodule (ZMod 2) V) : Prop :=
  ∀ i, i < 759 → ∃ t : Fin 104, (frameAt i).testBit t.val = true ∧ lab t ∈ M

lemma sem_blocking_iff (M : Submodule (ZMod 2) V) (u1 u2 : Nat)
    (hM : ∀ v, v ∈ M ↔ dotN u1 v = 0 ∧ dotN u2 v = 0) :
    SemBlocking M ↔ ∀ i, i < 759 → frameAt i &&& lamMask u1 u2 ≠ 0 := by
  constructor
  · intro hb i hi h0
    obtain ⟨t, ht1, ht2⟩ := hb i hi
    have hl : (lamMask u1 u2).testBit t.val = true := (lam_bit u1 u2 t).2 ((hM _).1 ht2)
    have := congrArg (fun x => x.testBit t.val) h0
    simp [Nat.testBit_and, ht1, hl] at this
  · intro hb i hi
    by_contra hcon
    apply hb i hi
    apply Nat.eq_of_testBit_eq
    intro s
    rw [Nat.testBit_and, Nat.zero_testBit]
    by_cases hs : s < 104
    · by_cases h1 : (frameAt i).testBit s = true
      · by_cases h2 : (lamMask u1 u2).testBit s = true
        · exfalso; apply hcon
          exact ⟨⟨s, hs⟩, h1, (hM _).2 ((lam_bit u1 u2 ⟨s, hs⟩).1 h2)⟩
        · simp [h2]
      · simp [h1]
    · have : (frameAt i).testBit s = false := by
        apply Nat.testBit_lt_two_pow
        have : frameAt i < 2 ^ 104 := Nat.mod_lt _ (by positivity)
        calc frameAt i < 2 ^ 104 := this
          _ ≤ 2 ^ s := Nat.pow_le_pow_right (by omega) (by omega)
      simp [this]

/-- HEADLINE: the 8-row ALL-OR-NOTHING law with the span step.  Hypotheses are semantic only:
M = span of labels of D_k is 7-dimensional and frame-blocking; A odd support of row k (inside D_k),
B odd support of row l (inside S_l), ind(A ∩ B) ∈ F^perp (the FS-4 coupling).  No normals, no lists. -/
theorem all_or_nothing_8row (D S A B : Finset (Fin 104))
    (h7 : Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) = 7)
    (hblock : SemBlocking (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))))
    (hA : A ⊆ D) (hB : B ⊆ S) (H_FS4 : ind (A ∩ B) ∈ Fperp) :
    A ∩ B = ∅ ∨ (A = Lam (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) ∧
      Lam (Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104)))) ⊆ B ∧
      Submodule.span (ZMod 2) (lab '' (D : Set (Fin 104))) ≤
        Submodule.span (ZMod 2) (lab '' (S : Set (Fin 104)))) := by
  obtain ⟨u1, u2, h1, h2, hne, h1', h2', hM⟩ := exists_normals _ h7
  exact all_or_nothing_rows_real D S A B u1 u2 h1 h2 hne h1' h2' hM
    hblock hA hB H_FS4

/-! ## non-vacuity -/
noncomputable def dotL (u : Nat) : V →ₗ[ZMod 2] ZMod 2 :=
  ∑ j : Fin 9, if u.testBit j.val = true then LinearMap.proj j else 0

lemma dotL_apply (u : Nat) (v : V) : dotL u v = dotN u v := by
  simp only [dotL, dotN, LinearMap.sum_apply]
  refine Finset.sum_congr rfl (fun j _ => ?_)
  by_cases h : u.testBit j.val = true <;> simp [h]

/-- the 7-dim section with normals u1,u2 as a submodule -/
noncomputable def KerN (u1 u2 : Nat) : Submodule (ZMod 2) V :=
  LinearMap.ker (dotL u1) ⊓ LinearMap.ker (dotL u2)

lemma mem_KerN (u1 u2 : Nat) (v : V) : v ∈ KerN u1 u2 ↔ dotN u1 v = 0 ∧ dotN u2 v = 0 := by
  simp [KerN, dotL_apply]

/-- a certified blocking section satisfies SemBlocking (hypothesis of the headline is satisfiable) -/
theorem nv_semblocking : SemBlocking (KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))) :=
  (sem_blocking_iff _ _ _ (mem_KerN _ _)).2 nv_blocking_instance

/-- ... and fails for the (1,2) section: SemBlocking is a genuine restriction -/
theorem nv_not_semblocking : ¬ SemBlocking (KerN 1 2) := by
  intro h
  obtain ⟨i, hi, h0⟩ := nv_nonblocking_instance
  exact (sem_blocking_iff _ _ _ (mem_KerN 1 2)).1 h i hi h0

/-- the semantic law instantiated at the certified section (trivial rows A = B = empty) -/
theorem nv_sub_instance :
    (∅ : Finset (Fin 104)) ∩ ∅ = ∅ ∨
      ((∅ : Finset (Fin 104)) = Lam (KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))) ∧
        Lam (KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))) ⊆ ∅) :=
  all_or_nothing_sub (KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])))
    (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])) (by decide +kernel) (by decide +kernel)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (mem_KerN _ _) nv_semblocking ∅ ∅
    (by simpa using ind_empty_mem) (by simp)

#print axioms exists_normals
#print axioms all_or_nothing_sub
#print axioms all_or_nothing_rows_real
#print axioms all_or_nothing_8row
#print axioms nv_sub_instance

end BlockLaw

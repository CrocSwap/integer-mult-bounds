/-
Bridge7761Chart (lane LEAN-BRIDGE, Nov 18).  Generic chart machinery for decide-checkable subspaces of V = F_2^9:
a chart is given by a reduced-echelon basis list B and pivot list P; `cht B` = span of the basis vectors (as a family over Fin B.length).
  finrank_cht  : ech B P → finrank (cht B) = B.length
  cht_le       : (∀ b ∈ B, inSpanB B' P' b) → cht B ≤ cht B'
  cht_ker      : ech, length 8, all basis vectors killed by phi a, a has a bit → cht B = ker (phi a)
  cht_top, cht_bot, cht_single.
Kernel only (no sorry / native_decide / axioms).
-/
import Nov15.BankWireC
import Mathlib.LinearAlgebra.LinearIndependent.Basic
import Mathlib.LinearAlgebra.FiniteDimensional.Defs

namespace Bridge7761
open Finset Module Submodule BankWireC BankFlagB

def cht (B : List ℕ) : Submodule (ZMod 2) V :=
  span (ZMod 2) (Set.range (fun i : Fin B.length => vec (B.getD i 0)))

/-- reduced-echelon property: pivots below 9, B_j has bit P_i iff i = j. -/
def ech (B P : List ℕ) : Prop :=
  B.length = P.length ∧ ∀ i, i < B.length → ∀ j, j < B.length →
    P.getD i 0 < 9 ∧ (B.getD j 0).testBit (P.getD i 0) = decide (i = j)

instance (B P : List ℕ) : Decidable (ech B P) := by unfold ech; infer_instance

theorem vec_xor (a b : ℕ) : vec (a ^^^ b) = vec a + vec b := by
  funext i
  simp only [vec, Pi.add_apply, Nat.testBit_xor]
  cases ha : a.testBit i <;> cases hb : b.testBit i <;> simp <;> decide

theorem vec_zero : vec 0 = 0 := by funext i; simp [vec]

theorem finrank_cht {B P : List ℕ} (h : ech B P) : finrank (ZMod 2) (cht B) = B.length := by
  obtain ⟨hl, h2⟩ := h
  have hli : LinearIndependent (ZMod 2) (fun i : Fin B.length => vec (B.getD i 0)) := by
    rw [Fintype.linearIndependent_iff]
    intro g hg i
    have hP : P.getD i 0 < 9 := (h2 i i.2 i i.2).1
    have := congrFun hg ⟨P.getD i 0, hP⟩
    simp only [Finset.sum_apply, Pi.smul_apply, vec, smul_eq_mul, Pi.zero_apply] at this
    have key : ∀ j : Fin B.length, g j * (if (B.getD j 0).testBit (P.getD i 0) then (1 : ZMod 2) else 0) =
        if j = i then g i else 0 := by
      intro j
      have := (h2 i i.2 j j.2).2
      by_cases hji : j = i
      · subst hji; have e : (B.getD j 0).testBit (P.getD j 0) = true := by simpa using this
        rw [if_pos e, if_pos rfl, mul_one]
      · have e : (B.getD j 0).testBit (P.getD i 0) = false := by
          rw [this]; exact decide_eq_false (fun hh => hji (Fin.ext hh.symm))
        rw [if_neg (by rw [e]; decide), if_neg hji, mul_zero]
    simp only [key] at this
    simpa using this
  unfold cht
  rw [finrank_span_eq_card hli]; simp

/-- membership test: x is the xor of the basis vectors selected by its pivot bits. -/
def xorPick (B P : List ℕ) (x : ℕ) : ℕ :=
  (List.range B.length).foldl (fun acc i => if x.testBit (P.getD i 0) then acc ^^^ B.getD i 0 else acc) 0

def inSpanB (B P : List ℕ) (x : ℕ) : Bool := xorPick B P x == x

theorem fold_mem (B P : List ℕ) (x : ℕ) :
    ∀ (l : List ℕ), (∀ i ∈ l, i < B.length) → ∀ acc : ℕ, vec acc ∈ cht B →
    vec (l.foldl (fun acc i => if x.testBit (P.getD i 0) then acc ^^^ B.getD i 0 else acc) acc) ∈ cht B := by
  intro l
  induction l with
  | nil => intro _ acc h; simpa using h
  | cons i l ih =>
    intro hl acc h
    simp only [List.foldl_cons]
    apply ih (fun j hj => hl j (List.mem_cons_of_mem _ hj))
    split_ifs
    · rw [vec_xor]
      exact add_mem h (subset_span ⟨⟨i, hl i (List.mem_cons_self)⟩, rfl⟩)
    · exact h

theorem inSpanB_mem {B P : List ℕ} {x : ℕ} (h : inSpanB B P x = true) : vec x ∈ cht B := by
  unfold inSpanB at h
  have e : xorPick B P x = x := by simpa using h
  have := fold_mem B P x (List.range B.length) (fun i hi => List.mem_range.mp hi) 0 (by rw [vec_zero]; exact zero_mem _)
  unfold xorPick at e
  rw [e] at this
  exact this

theorem basis_mem {B : List ℕ} {b : ℕ} (hb : b ∈ B) : vec b ∈ cht B := by
  obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem hb
  exact subset_span ⟨⟨i, hi⟩, by simp [List.getD_eq_getElem?_getD, hi]⟩

theorem cht_le {B B' P' : List ℕ} (h : ∀ b ∈ B, inSpanB B' P' b = true) : cht B ≤ cht B' := by
  unfold cht
  apply span_le.mpr
  rintro _ ⟨i, rfl⟩
  have hb : B.getD i 0 ∈ B := by
    simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem i.2, Option.getD_some]
    exact List.getElem_mem _
  exact inSpanB_mem (h _ hb)

theorem cht_nil : cht [] = ⊥ := by
  unfold cht
  have : Set.range (fun i : Fin ([] : List ℕ).length => vec (([] : List ℕ).getD i 0)) = ∅ := by
    ext x; simp
  rw [this]; exact span_empty

theorem cht_single (v : ℕ) : cht [v] = span (ZMod 2) {vec v} := by
  unfold cht
  congr 1
  ext x; simp [Fin.exists_fin_one]

theorem cht_top {B P : List ℕ} (h : ech B P) (h9 : B.length = 9) : cht B = ⊤ := by
  apply Submodule.eq_top_of_finrank_eq
  rw [finrank_cht h, h9, Module.finrank_fin_fun]

theorem ker_rank {a : ℕ} (h : ∃ i : Fin 9, a.testBit i = true) :
    finrank (ZMod 2) (LinearMap.ker (phi a)) = 8 := by
  obtain ⟨i, hi⟩ := h
  have hs : Function.Surjective (phi a) := by
    intro y
    refine ⟨y • Pi.single i 1, ?_⟩
    have hsum : (∑ x : Fin 9, if a.testBit ↑x = true then (if x = i then (1 : ZMod 2) else 0) else 0) = 1 := by
      rw [Finset.sum_eq_single i]
      · simp [hi]
      · intro b _ hb; simp [hb]
      · simp
    rw [LinearMap.map_smul, phi_apply]
    simp [Pi.single_apply, hsum]
  have h1 := LinearMap.finrank_range_add_finrank_ker (phi a)
  rw [LinearMap.range_eq_top.mpr hs, finrank_top, Module.finrank_self, Module.finrank_fin_fun] at h1
  omega

theorem cht_ker {B P : List ℕ} (h : ech B P) (h8 : B.length = 8) {a : ℕ}
    (ha : ∃ i : Fin 9, a.testBit i = true) (hk : ∀ b ∈ B, par a b = 0) :
    cht B = LinearMap.ker (phi a) := by
  apply Submodule.eq_of_le_of_finrank_eq
  · unfold cht
    apply span_le.mpr
    rintro _ ⟨i, rfl⟩
    have hb : B.getD i 0 ∈ B := by
      simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem i.2, Option.getD_some]
      exact List.getElem_mem _
    show phi a _ = 0
    rw [phi_vec, hk _ hb]; rfl
  · rw [finrank_cht h, h8, ker_rank ha]

end Bridge7761

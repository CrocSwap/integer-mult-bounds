/-
V2FloorNativeData (lane LEAN-NEXT21, Nov 16): member lists / tables of the pair data's L and U subspaces and the
table form of containment, for the native route. No native_decide here.
-/
import Nov15.V2FloorNativeTab2
import Mathlib.Data.ZMod.Basic

namespace V2Floor
open Finset Module
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 2000000

/-! ### L side -/

def Lms (B : List ℕ) : List ℕ := B.foldl addv' [0]

theorem Lsub_cons (b : ℕ) (B : List ℕ) : Lsub (b :: B) = Submodule.span (ZMod 2) {vec b} ⊔ Lsub B := by
  unfold Lsub
  have : {x | x ∈ (b :: B).map vec} = insert (vec b) {x | x ∈ B.map vec} := by
    ext x; simp [eq_comm]
  rw [this, Submodule.span_insert]

theorem foldl_Rep' : ∀ (B : List ℕ) (acc : List ℕ) (S : Sub), Rep' acc S → (∀ b ∈ B, b < 512) →
    Rep' (B.foldl addv' acc) (S ⊔ Lsub B) := by
  intro B
  induction B with
  | nil =>
    intro acc S h _
    have : Lsub [] = ⊥ := by simp [Lsub]
    simpa [this] using h
  | cons b B ih =>
    intro acc S h hB
    have := ih (addv' acc b) _ (Rep'_add h (hB b (by simp))) (fun x hx => hB x (by simp [hx]))
    rw [List.foldl_cons]
    rw [Lsub_cons, ← sup_assoc]
    exact this

theorem Rep'_Lms (B : List ℕ) (hB : ∀ b ∈ B, b < 512) : Rep' (Lms B) (Lsub B) := by
  have := foldl_Rep' B [0] ⊥ Rep'_bot hB
  rw [bot_sup_eq] at this
  exact this

/-! ### U side -/

def ipn (h v : ℕ) (m : ℕ) : ℕ := ((List.range m).filter (fun j => h.testBit j && v.testBit j)).length

def kerMs (H : List ℕ) : List ℕ := (List.range 512).filter (fun v => H.all (fun h => ipn h v 9 % 2 == 0))

theorem ipn_succ (h v m : ℕ) : ipn h v (m + 1) = ipn h v m + (if h.testBit m && v.testBit m then 1 else 0) := by
  unfold ipn
  rw [List.range_succ, List.filter_append]
  by_cases hh : (h.testBit m && v.testBit m) = true <;> simp [hh]

theorem ip_sum (h v : ℕ) : (∑ j : Fin 9, (vec h j * vec v j : ZMod 2)) = ((ipn h v 9 : ℕ) : ZMod 2) := by
  have e : (∑ j : Fin 9, (vec h j * vec v j : ZMod 2)) = ∑ j ∈ Finset.range 9,
      ((if h.testBit j then (1 : ZMod 2) else 0) * (if v.testBit j then 1 else 0)) := by
    rw [← Fin.sum_univ_eq_sum_range (fun j => (if h.testBit j then (1 : ZMod 2) else 0) * (if v.testBit j then 1 else 0)) 9]
    rfl
  rw [e]
  have : ∀ m, (∑ j ∈ Finset.range m, ((if h.testBit j then (1 : ZMod 2) else 0) * (if v.testBit j then 1 else 0))) =
      ((ipn h v m : ℕ) : ZMod 2) := by
    intro m
    induction m with
    | zero => simp [ipn]
    | succ m ih =>
      rw [Finset.sum_range_succ, ih, ipn_succ]
      by_cases h1 : h.testBit m = true <;> by_cases h2 : v.testBit m = true <;> simp [h1, h2]
  exact this 9

theorem Rep'_kerMs (H : List ℕ) : Rep' (kerMs H) (Usub H) := by
  refine ⟨fun v hv => by simp [kerMs] at hv; exact hv.1, fun v hv => ?_⟩
  unfold kerMs Usub
  simp only [List.mem_filter, List.mem_range, hv, true_and, List.all_eq_true, beq_iff_eq,
    LinearMap.mem_ker, Matrix.mulVecLin_apply]
  constructor
  · intro h
    funext i
    simp only [Matrix.mulVec, dotProduct, Matrix.of_apply, Pi.zero_apply]
    have := h (H.get i) (List.get_mem _ _)
    rw [show (∑ j : Fin 9, vec (H.get i) j * vec v j) = ((ipn (H.get i) v 9 : ℕ) : ZMod 2) from ip_sum _ _]
    rw [ZMod.natCast_eq_zero_iff]
    omega
  · intro h hh hmem
    obtain ⟨i, rfl⟩ := List.mem_iff_get.1 hmem
    have := congrFun h i
    simp only [Matrix.mulVec, dotProduct, Matrix.of_apply, Pi.zero_apply] at this
    rw [show (∑ j : Fin 9, vec (H.get i) j * vec v j) = ((ipn (H.get i) v 9 : ℕ) : ZMod 2) from ip_sum _ _] at this
    rw [ZMod.natCast_eq_zero_iff] at this
    omega

/-! ### tables and containment -/

theorem RepT_le_iff {s t : ℕ} {S S' : Sub} (hs : RepT s S) (ht : RepT t S') : S ≤ S' ↔ s &&& t = s := by
  constructor
  · intro h
    apply Nat.eq_of_testBit_eq
    intro i
    rw [Nat.testBit_and]
    by_cases hi : i < 512
    · rw [hs.2 i hi, ht.2 i hi]
      by_cases hm : vec i ∈ S
      · simp [hm, h hm]
      · simp [hm]
    · have : s.testBit i = false := bits_of_lt hs.1 i (by omega)
      simp [this]
  · intro h x hx
    obtain ⟨v, hv, rfl⟩ := vec_surj x
    have h1 : s.testBit v = true := by rw [hs.2 v hv]; simpa using hx
    have h2 : (s &&& t).testBit v = true := by rw [h]; exact h1
    rw [Nat.testBit_and, Bool.and_eq_true] at h2
    have := h2.2
    rw [ht.2 v hv] at this
    simpa using this

end V2Floor

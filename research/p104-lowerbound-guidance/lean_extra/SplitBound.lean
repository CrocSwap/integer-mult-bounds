import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
/-!
SPLITBOUND (lane LEAN-SPLIT).  Kernel-only: no sorry / native_decide / axioms.
Split bound for mod-4 pseudo-decoders (VC.md item 5), abstract index type ι, abstract pattern Mz
(0/1 and unit diagonal are NOT needed for the proof).  Rows w_k, v_k integer vectors with
  sum_k w_k(t) v_k(s) Mz(t,s) = 2 [t = s].
SPLIT: no port has both an odd w-entry and an odd v-entry:  ∀ t, (∀ k, w_k t even) ∨ (∀ k, v_k t even).
A = {t | ∀ k, v_k t even}, B = complement (there all w even).  Qk = Mz padded to supp w x supp v over F2.
Cost C = sum_k rank_F2 Qk.  Result: |A| ≤ C, |B| ≤ C, hence C ≥ max(|A|,|B|) and 2C ≥ n (C ≥ ceil(n/2)).
-/
open Matrix Finset

namespace SplitBound

instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

variable {ι κ : Type*} [Fintype ι] [DecidableEq ι]

lemma rank_add_le' {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n (ZMod 2)) :
    (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  have h : LinearMap.range (A + B).mulVecLin ≤
      LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin := by
    rintro _ ⟨x, rfl⟩
    exact Submodule.mem_sup.2 ⟨A.mulVecLin x, ⟨x, rfl⟩, B.mulVecLin x, ⟨x, rfl⟩, by simp [add_mulVec]⟩
  exact (Submodule.finrank_mono h).trans (Submodule.finrank_add_le_finrank_add_finrank _ _)

lemma rank_sum_le (s : Finset κ) (f : κ → Matrix ι ι (ZMod 2)) :
    (∑ j ∈ s, f j).rank ≤ ∑ j ∈ s, (f j).rank := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    rw [sum_insert ha, sum_insert ha]
    exact (rank_add_le' _ _).trans (Nat.add_le_add_left ih _)

lemma rank_diag_mul_diag_le (x y : ι → ZMod 2) (Q : Matrix ι ι (ZMod 2)) :
    (diagonal x * Q * diagonal y).rank ≤ Q.rank :=
  (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)

/-- (2) the F2 decoder bound: a decoder over F2 on a port set S with unit diagonal has
total climb ≥ |S|. -/
theorem f2_decoder_rank (J : Finset κ) (S : Finset ι) (Q : κ → Matrix ι ι (ZMod 2))
    (x y : κ → ι → ZMod 2)
    (h : ∀ t ∈ S, ∀ s ∈ S, ∑ k ∈ J, x k t * Q k t s * y k s = if t = s then 1 else 0) :
    S.card ≤ ∑ k ∈ J, (Q k).rank := by
  classical
  have hD : (diagonal (fun t => if t ∈ S then (1 : ZMod 2) else 0) : Matrix ι ι (ZMod 2)) =
      ∑ k ∈ J, diagonal (fun t => if t ∈ S then x k t else 0) * Q k *
        diagonal (fun s => if s ∈ S then y k s else 0) := by
    ext t s
    rw [Matrix.sum_apply]
    simp only [Matrix.diagonal_mul, Matrix.mul_diagonal]
    by_cases ht : t ∈ S
    · by_cases hs : s ∈ S
      · simp only [ht, hs, if_true]
        rw [h t ht s hs]
        by_cases hts : t = s
        · subst hts; simp [ht]
        · simp [hts, Matrix.diagonal_apply_ne _ hts]
      · simp [hs, ht, Matrix.diagonal_apply]
        intro hts; subst hts; exact absurd ht hs
    · simp [ht, Matrix.diagonal_apply]
  have hr : (diagonal (fun t => if t ∈ S then (1 : ZMod 2) else 0) : Matrix ι ι (ZMod 2)).rank
      = S.card := by
    rw [Matrix.rank_diagonal]
    simp only [ne_eq, ite_eq_right_iff, one_ne_zero, imp_false, not_not]
    rw [Fintype.card_subtype]
    congr 1
    ext t; simp
  rw [← hr, hD]
  refine (rank_sum_le J _).trans (Finset.sum_le_sum fun k _ => ?_)
  exact rank_diag_mul_diag_le _ _ _


/-- padded pattern of one row over F2 (as in HalfCancel). -/
def Qk (Mz : ι → ι → ℤ) (w v : ι → ℤ) : Matrix ι ι (ZMod 2) :=
  Matrix.of fun t s => if w t ≠ 0 ∧ v s ≠ 0 then (Mz t s : ZMod 2) else 0

variable (Mz : ι → ι → ℤ) (J : Finset κ) (w v : κ → ι → ℤ)

lemma cast_two (x : ℤ) (hx : x % 2 = 0) : ((x : ℤ) : ZMod 2) = 0 := by
  have : x = 2 * (x / 2) := by omega
  rw [this]; push_cast
  have : (2 : ZMod 2) = 0 := by decide
  rw [this, zero_mul]

/-- (1a) A-block: ports where every v is even carry an F2 decoder  a_k Q v'_k. -/
theorem blockA (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (t s : ι) (ht : ∀ k ∈ J, v k t % 2 = 0) (hs : ∀ k ∈ J, v k s % 2 = 0) :
    ∑ k ∈ J, ((w k t : ℤ) : ZMod 2) * Qk Mz (w k) (v k) t s * (((v k s / 2 : ℤ)) : ZMod 2)
      = if t = s then 1 else 0 := by
  have e := hdec t s
  have e2 : ∑ k ∈ J, w k t * (v k s / 2) * Mz t s = if t = s then 1 else 0 := by
    have : ∑ k ∈ J, w k t * v k s * Mz t s = 2 * ∑ k ∈ J, w k t * (v k s / 2) * Mz t s := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun k hk => ?_
      have := hs k hk
      have h2 : v k s = 2 * (v k s / 2) := by omega
      conv_lhs => rw [h2]
      ring
    rw [this] at e
    split_ifs at e ⊢ <;> omega
  have e3 := congrArg (fun z : ℤ => (z : ZMod 2)) e2
  simp only [Int.cast_sum, Int.cast_mul] at e3
  rw [show ((if t = s then (1 : ℤ) else 0 : ℤ) : ZMod 2) = if t = s then 1 else 0 by
    split_ifs <;> simp] at e3
  rw [← e3]
  refine Finset.sum_congr rfl fun k _ => ?_
  by_cases hw : w k t = 0
  · simp [hw]
  · by_cases hv : v k s = 0
    · simp [hv]
    · simp [Qk, hw, hv]; ring

/-- (1b) B-block: ports where every w is even carry an F2 decoder  w'_k Q v_k. -/
theorem blockB (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (t s : ι) (ht : ∀ k ∈ J, w k t % 2 = 0) (hs : ∀ k ∈ J, w k s % 2 = 0) :
    ∑ k ∈ J, (((w k t / 2 : ℤ)) : ZMod 2) * Qk Mz (w k) (v k) t s * ((v k s : ℤ) : ZMod 2)
      = if t = s then 1 else 0 := by
  have e := hdec t s
  have e2 : ∑ k ∈ J, (w k t / 2) * v k s * Mz t s = if t = s then 1 else 0 := by
    have : ∑ k ∈ J, w k t * v k s * Mz t s = 2 * ∑ k ∈ J, (w k t / 2) * v k s * Mz t s := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun k hk => ?_
      have := ht k hk
      have h2 : w k t = 2 * (w k t / 2) := by omega
      conv_lhs => rw [h2]
      ring
    rw [this] at e
    split_ifs at e ⊢ <;> omega
  have e3 := congrArg (fun z : ℤ => (z : ZMod 2)) e2
  simp only [Int.cast_sum, Int.cast_mul] at e3
  rw [show ((if t = s then (1 : ℤ) else 0 : ℤ) : ZMod 2) = if t = s then 1 else 0 by
    split_ifs <;> simp] at e3
  rw [← e3]
  refine Finset.sum_congr rfl fun k _ => ?_
  by_cases hw : w k t = 0
  · simp [hw]
  · by_cases hv : v k s = 0
    · simp [hv]
    · simp [Qk, hw, hv]; ring

/-- SPLIT hypothesis. -/
def Split : Prop := ∀ t, (∀ k ∈ J, w k t % 2 = 0) ∨ (∀ k ∈ J, v k t % 2 = 0)

/-- (1) the split construction: A = {all v even}, B = {not all v even}; (3) both are bounded by cost C. -/
theorem split_bound (hsplit : Split J w v)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    (Finset.univ.filter fun t : ι => ∀ k ∈ J, v k t % 2 = 0).card ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank ∧
    (Finset.univ.filter fun t : ι => ¬ ∀ k ∈ J, v k t % 2 = 0).card ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  classical
  constructor
  · exact f2_decoder_rank J _ (fun k => Qk Mz (w k) (v k)) (fun k t => ((w k t : ℤ) : ZMod 2))
      (fun k s => (((v k s / 2 : ℤ)) : ZMod 2)) fun t ht s hs => by
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ht hs
        exact blockA Mz J w v hdec t s ht hs
  · refine f2_decoder_rank J _ (fun k => Qk Mz (w k) (v k)) (fun k t => (((w k t / 2 : ℤ)) : ZMod 2))
      (fun k s => ((v k s : ℤ) : ZMod 2)) fun t ht s hs => ?_
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at ht hs
    have hw : ∀ u, ¬ (∀ k ∈ J, v k u % 2 = 0) → ∀ k ∈ J, w k u % 2 = 0 := fun u hu =>
      (hsplit u).resolve_right hu
    exact blockB Mz J w v hdec t s (hw t ht) (hw s hs)

/-- (2) cost ≥ max(|A|,|B|). -/
theorem cost_ge_max (hsplit : Split J w v)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    max (Finset.univ.filter fun t : ι => ∀ k ∈ J, v k t % 2 = 0).card
        (Finset.univ.filter fun t : ι => ¬ ∀ k ∈ J, v k t % 2 = 0).card
      ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  obtain ⟨h1, h2⟩ := split_bound Mz J w v hsplit hdec
  exact max_le h1 h2

/-- (3) corollary: n ≤ 2 C, i.e. C ≥ ceil(n/2). -/
theorem cost_ge_ceil_half (hsplit : Split J w v)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    Fintype.card ι ≤ 2 * ∑ k ∈ J, (Qk Mz (w k) (v k)).rank ∧
    (Fintype.card ι + 1) / 2 ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  obtain ⟨h1, h2⟩ := split_bound Mz J w v hsplit hdec
  have h3 := Finset.card_filter_add_card_filter_not
    (s := (Finset.univ : Finset ι)) (fun t : ι => ∀ k ∈ J, v k t % 2 = 0)
  rw [Finset.card_univ] at h3
  constructor <;> omega

/-! (4) non-vacuity: n = 2, Mz = identity pattern, one row w = (1,2), v = (2,1).
Port 0: w odd, v even; port 1: w even, v odd.  Split, identity holds, |A| = |B| = 1, cost = 2. -/
section Inst
def Mi : Fin 2 → Fin 2 → ℤ := fun t s => if t = s then 1 else 0
def Wi : Fin 1 → Fin 2 → ℤ := fun _ t => if t = 0 then 1 else 2
def Vi : Fin 1 → Fin 2 → ℤ := fun _ t => if t = 0 then 2 else 1

lemma inst_dec : ∀ t s : Fin 2, ∑ k ∈ (Finset.univ : Finset (Fin 1)), Wi k t * Vi k s * Mi t s
    = if t = s then 2 else 0 := by decide

lemma inst_split : Split Finset.univ Wi Vi := by
  intro t; fin_cases t
  · right; decide
  · left; decide

theorem inst_bound :
    (Finset.univ.filter fun t : Fin 2 => ∀ k, Vi k t % 2 = 0).card = 1 ∧
    (Finset.univ.filter fun t : Fin 2 => ¬ ∀ k, Vi k t % 2 = 0).card = 1 ∧
    2 ≤ 2 * ∑ k ∈ (Finset.univ : Finset (Fin 1)), (Qk Mi (Wi k) (Vi k)).rank :=
  ⟨by decide, by decide, (cost_ge_ceil_half Mi _ Wi Vi inst_split inst_dec).1⟩

end Inst

#print axioms f2_decoder_rank
#print axioms blockA
#print axioms blockB
#print axioms split_bound
#print axioms cost_ge_max
#print axioms cost_ge_ceil_half
#print axioms inst_bound

end SplitBound

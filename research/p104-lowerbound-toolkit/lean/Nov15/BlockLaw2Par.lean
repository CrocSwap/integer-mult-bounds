import Nov15.BlockLaw
import Mathlib.Algebra.BigOperators.Intervals
namespace BlockLaw2Par
open FrameCert BlockComplete BlockLaw

/-! ## 1. parity: every frame meets Lam(c) evenly, i.e. 1_Lam ∈ Fperp -/

/-- xor of g over c positions j, j+s, j+2s, ... -/
def Yp (g : Nat → Bool) (s : Nat) : Nat → Nat → Bool
  | 0, _ => false
  | c + 1, j => xor (g j) (Yp g s c (j + s))

lemma Y_double (g : Nat → Bool) (s : Nat) : ∀ c j,
    xor (Yp g (2 * s) c j) (Yp g (2 * s) c (j + s)) = Yp g s (2 * c) j := by
  intro c
  induction c with
  | zero => intro j; simp [Yp]
  | succ c ih =>
    intro j
    have h := ih (j + 2 * s)
    have e1 : j + s + 2 * s = j + 2 * s + s := by omega
    have e2 : 2 * (c + 1) = 2 * c + 1 + 1 := by omega
    have e3 : j + s + s = j + 2 * s := by omega
    rw [e2]
    simp only [Yp, e1, e3]
    rw [← h]
    cases g j <;> cases g (j + s) <;> cases Yp g (2 * s) c (j + 2 * s) <;>
      cases Yp g (2 * s) c (j + 2 * s + s) <;> rfl

lemma xs_step (v n j : Nat) : (v ^^^ (v >>> n)).testBit j = xor (v.testBit j) (v.testBit (j + n)) := by
  rw [Nat.testBit_xor, Nat.testBit_shiftRight, Nat.add_comm n j]

lemma par128_bit (m : Nat) :
    par128 m = if Yp (fun i => m.testBit i) 1 128 0 = true then 1 else 0 := by
  have s0 : ∀ j, m.testBit j = Yp (fun i => m.testBit i) 128 1 j := by
    intro j; simp [Yp]
  set g : Nat → Bool := fun i => m.testBit i with hg
  let v1 := m ^^^ (m >>> 64)
  have h1 : ∀ j, v1.testBit j = Yp g 64 2 j := by
    intro j
    have := Y_double g 64 1 j
    simp only [v1, xs_step]
    rw [s0 j, s0 (j + 64)]
    simpa using this
  let v2 := v1 ^^^ (v1 >>> 32)
  have h2 : ∀ j, v2.testBit j = Yp g 32 4 j := by
    intro j
    have := Y_double g 32 2 j
    simp only [v2, xs_step]
    rw [h1 j, h1 (j + 32)]
    simpa using this
  let v3 := v2 ^^^ (v2 >>> 16)
  have h3 : ∀ j, v3.testBit j = Yp g 16 8 j := by
    intro j
    have := Y_double g 16 4 j
    simp only [v3, xs_step]
    rw [h2 j, h2 (j + 16)]
    simpa using this
  let v4 := v3 ^^^ (v3 >>> 8)
  have h4 : ∀ j, v4.testBit j = Yp g 8 16 j := by
    intro j
    have := Y_double g 8 8 j
    simp only [v4, xs_step]
    rw [h3 j, h3 (j + 8)]
    simpa using this
  let v5 := v4 ^^^ (v4 >>> 4)
  have h5 : ∀ j, v5.testBit j = Yp g 4 32 j := by
    intro j
    have := Y_double g 4 16 j
    simp only [v5, xs_step]
    rw [h4 j, h4 (j + 4)]
    simpa using this
  let v6 := v5 ^^^ (v5 >>> 2)
  have h6 : ∀ j, v6.testBit j = Yp g 2 64 j := by
    intro j
    have := Y_double g 2 32 j
    simp only [v6, xs_step]
    rw [h5 j, h5 (j + 2)]
    simpa using this
  let v7 := v6 ^^^ (v6 >>> 1)
  have h7 : ∀ j, v7.testBit j = Yp g 1 128 j := by
    intro j
    have := Y_double g 1 64 j
    simp only [v7, xs_step]
    rw [h6 j, h6 (j + 1)]
    simpa using this
  have hp : par128 m = v7 &&& 1 := rfl
  rw [hp, Nat.and_one_is_mod]
  have := h7 0
  rw [Nat.testBit_zero] at this
  by_cases hY : Yp g 1 128 0 = true
  · rw [if_pos hY]
    rw [hY] at this
    simpa using this
  · rw [if_neg hY]
    have hY' : Yp g 1 128 0 = false := by simpa using hY
    rw [hY'] at this
    have : ¬ (v7 % 2 = 1) := by simpa using this
    omega

lemma b2z_Yp (g : Nat → Bool) : ∀ c j, b2z (Yp g 1 c j) = ∑ i ∈ Finset.range c, b2z (g (j + i)) := by
  intro c
  induction c with
  | zero => intro j; simp [Yp, b2z]
  | succ c ih =>
    intro j
    rw [Finset.sum_range_succ', Yp, b2z_xor, ih (j + 1)]
    rw [add_comm]
    have : ∀ i, j + 1 + i = j + (i + 1) := by intro i; omega
    simp only [this, Nat.add_zero]

lemma dot_ind_lam (m lam : Nat) (hm : m < 2 ^ 104) :
    dot m (ind (lamSet lam)) = b2z (Yp (fun i => (m &&& lam).testBit i) 1 128 0) := by
  rw [b2z_Yp]
  simp only [Nat.zero_add]
  have hz : ∀ i, 104 ≤ i → (m &&& lam).testBit i = false := by
    intro i hi
    rw [Nat.testBit_and, Nat.testBit_lt_two_pow (lt_of_lt_of_le hm (Nat.pow_le_pow_right (by omega) hi))]
    simp
  have h104 : ∑ i : Fin 104, (if m.testBit i.val then ind (lamSet lam) i else 0) =
      ∑ i ∈ Finset.range 104, b2z ((m &&& lam).testBit i) := by
    rw [← Fin.sum_univ_eq_sum_range (fun i => b2z ((m &&& lam).testBit i)) 104]
    refine Finset.sum_congr rfl (fun i _ => ?_)
    simp only [ind, lamSet, Finset.mem_filter, Finset.mem_univ, true_and, Nat.testBit_and, b2z]
    by_cases h1 : m.testBit i.val = true <;> by_cases h2 : lam.testBit i.val = true <;> simp [h1, h2]
  unfold dot
  rw [h104]
  apply Finset.sum_subset
  · exact Finset.range_subset_range.2 (by norm_num)
  · intro i hi hn
    simp at hi hn
    rw [hz i (by omega)]; rfl

lemma par128_zero_ind (m lam : Nat) (hm : m < 2 ^ 104) (h : par128 (m &&& lam) = 0) :
    dot m (ind (lamSet lam)) = 0 := by
  rw [dot_ind_lam m lam hm]
  rw [par128_bit] at h
  by_cases hY : Yp (fun i => (m &&& lam).testBit i) 1 128 0 = true
  · rw [if_pos hY] at h; omega
  · have : Yp (fun i => (m &&& lam).testBit i) 1 128 0 = false := by simpa using hY
    rw [this]; rfl

lemma frameAt_lt (i : Nat) : frameAt i < 2 ^ 104 := Nat.mod_lt _ (by positivity)

theorem evenMeet_sound (lam : Nat) (h : evenMeet lam = true) : ind (lamSet lam) ∈ Fperp := by
  intro m hm
  obtain ⟨i, hi, rfl⟩ := List.mem_map.1 hm
  have := List.all_eq_true.1 h i hi
  simp only [beq_iff_eq] at this
  exact par128_zero_ind _ lam (frameAt_lt i) this

def evenChk (c : List Nat) : Bool := evenMeet (lamMask' (cu1 c) (cu2 c))

theorem all_app4 {a b : List (List Nat)} (ha : a.all evenChk = true) (hb : b.all evenChk = true) :
    (a ++ b).all evenChk = true := by
  rw [List.all_append, ha, hb]; rfl

end BlockLaw2Par

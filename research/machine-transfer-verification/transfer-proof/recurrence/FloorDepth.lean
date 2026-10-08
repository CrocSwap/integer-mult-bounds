import Mathlib.Tactic

/-! Executable depth and exact row-stock closure for child = t * (e / m).
No ceiling envelope or physical machine cost is assumed by these definitions.
-/
namespace FloorDepth

def child (m t e : ℕ) : ℕ := t * (e / m)

theorem child_lt (m t e : ℕ) (ht : t < m) (he : m ≤ e) : child m t e < e := by
  have hm : 0 < m := Nat.zero_lt_of_lt ht
  have hf : 0 < e / m := Nat.div_pos he hm
  calc
    child m t e = t * (e / m) := rfl
    _ < m * (e / m) := Nat.mul_lt_mul_of_pos_right ht hf
    _ ≤ e := Nat.mul_div_le e m

theorem child_pos (m t e : ℕ) (hm : 0 < m) (ht : 0 < t) (he : m ≤ e) :
    0 < child m t e := Nat.mul_pos ht (Nat.div_pos he hm)

theorem child_mono (m t : ℕ) : Monotone (child m t) := by
  intro e f hef
  exact Nat.mul_le_mul_left t (Nat.div_le_div_right hef)

def depth (m t : ℕ) (ht : t < m) (e : ℕ) : ℕ :=
  if h : e < m then 0 else 1 + depth m t ht (child m t e)
termination_by e
decreasing_by exact child_lt m t e ht (Nat.le_of_not_gt h)

theorem depth_base (m t : ℕ) (ht : t < m) (e : ℕ) (he : e < m) :
    depth m t ht e = 0 := by rw [depth, dif_pos he]

theorem depth_step (m t : ℕ) (ht : t < m) (e : ℕ) (he : m ≤ e) :
    depth m t ht e = 1 + depth m t ht (child m t e) := by
  rw [depth, dif_neg (Nat.not_lt_of_ge he)]

theorem depth_mono (m t : ℕ) (ht : t < m) : Monotone (depth m t ht) := by
  intro e f hef
  induction f using Nat.strong_induction_on generalizing e with
  | h f ih =>
    by_cases hf : f < m
    · rw [depth_base m t ht f hf, depth_base m t ht e (lt_of_le_of_lt hef hf)]
    · have hfm : m ≤ f := Nat.le_of_not_gt hf
      by_cases he : e < m
      · rw [depth_base m t ht e he]; exact Nat.zero_le _
      · rw [depth_step m t ht f hfm, depth_step m t ht e (Nat.le_of_not_gt he)]
        exact Nat.add_le_add_left (ih (child m t f) (child_lt m t f ht hfm)
          (child_mono m t hef)) 1

theorem child_depth_drop (m tmax t e : ℕ) (htmax : tmax < m)
    (ht : t ≤ tmax) (he : m ≤ e) :
    depth m tmax htmax (child m t e) + 1 ≤ depth m tmax htmax e := by
  rw [depth_step m tmax htmax e he]
  have hc : child m t e ≤ child m tmax e := Nat.mul_le_mul_right (e / m) ht
  have hd := depth_mono m tmax htmax hc
  omega

/-- At every internal call all W role streams have an integer number of rows. -/
theorem row_split_exact (m tmax e W R : ℕ) (htmax : tmax < m) (he : m ≤ e)
    (stock : W ^ depth m tmax htmax e ∣ R) : W * (R / W) = R := by
  have hd : 1 ≤ depth m tmax htmax e := by rw [depth_step m tmax htmax e he]; omega
  have hw : W ∣ R := dvd_trans (by simpa using pow_dvd_pow W hd) stock
  exact Nat.mul_div_cancel' hw

/-- One exact row split leaves sufficient stock for every allowed child. -/
theorem child_row_stock (m tmax t e W R : ℕ) (htmax : tmax < m)
    (ht : t ≤ tmax) (he : m ≤ e) (hW : 0 < W)
    (stock : W ^ depth m tmax htmax e ∣ R) :
    W ^ depth m tmax htmax (child m t e) ∣ R / W := by
  have hd := child_depth_drop m tmax t e htmax ht he
  have hpow : W ^ (depth m tmax htmax (child m t e) + 1) ∣ R :=
    dvd_trans (pow_dvd_pow W hd) stock
  obtain ⟨k, hk⟩ := hpow
  rw [hk, pow_succ]
  have heq : W ^ depth m tmax htmax (child m t e) * W * k / W =
      W ^ depth m tmax htmax (child m t e) * k := by
    rw [mul_assoc, mul_comm W k, ← mul_assoc, Nat.mul_div_left _ hW]
  rw [heq]
  exact dvd_mul_right _ _

end FloorDepth

#print axioms FloorDepth.child_lt
#print axioms FloorDepth.child_pos
#print axioms FloorDepth.child_mono
#print axioms FloorDepth.depth_base
#print axioms FloorDepth.depth_step
#print axioms FloorDepth.depth_mono
#print axioms FloorDepth.child_depth_drop
#print axioms FloorDepth.row_split_exact
#print axioms FloorDepth.child_row_stock

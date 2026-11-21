import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace DirectTensorStability

variable {X : Type*} [SeminormedAddCommGroup X]

/-- Run the ideal stages in their prescribed time order. -/
def run (A : ℕ → X → X) : ℕ → ℕ → X → X
  | _, 0, x => x
  | i, k+1, x => run A (i+1) k (A i x)

/-- The error of a finite measured segment is a sum over its local defects.
The norm bound applies to each full intervening ideal interval. -/
theorem segment (A : ℕ → X → X) (z : ℕ → X) (N : ℕ) (M δ : ℝ)
    (hM : 0 ≤ M)
    (hinterval : ∀ i k, i+k ≤ N → ∀ x y,
      dist (run A i k x) (run A i k y) ≤ M * dist x y) :
    ∀ k i, i+k ≤ N → (∀ j, i ≤ j → j < i+k →
      dist (z (j+1)) (A j (z j)) ≤ δ) →
      dist (z (i+k)) (run A i k (z i)) ≤ (k : ℝ)*M*δ := by
  intro k
  induction k with
  | zero => intro i _ _; simp [run]
  | succ k ih =>
    intro i hfit hlocal
    have htail : ∀ j, i+1 ≤ j → j < (i+1)+k →
        dist (z (j+1)) (A j (z j)) ≤ δ := by
      intro j hlo hhi
      exact hlocal j (by omega) (by omega)
    have ht := ih (i+1) (by omega) htail
    have hh := hinterval (i+1) k (by omega) (z (i+1)) (A i (z i))
    have hfirst := hlocal i le_rfl (by omega)
    have hm := mul_le_mul_of_nonneg_left hfirst hM
    change dist (z (i+(k+1))) (run A (i+1) k (A i (z i))) ≤ _
    rw [show i+(k+1) = (i+1)+k by omega]
    calc
      _ ≤ dist (z ((i+1)+k)) (run A (i+1) k (z (i+1))) +
          dist (run A (i+1) k (z (i+1))) (run A (i+1) k (A i (z i))) :=
        dist_triangle _ _ _
      _ ≤ (k : ℝ)*M*δ + M*δ := add_le_add ht (hh.trans hm)
      _ = _ := by push_cast; ring

/-- State-relative local rounding is sufficient. A bound on the computed
state follows from the ideal radius and the available global error budget. -/
theorem bounded_computation (A : ℕ → X → X) (z : ℕ → X) (N : ℕ) (M ε R : ℝ)
    (hM : 0 ≤ M) (hε : 0 ≤ ε) (hR : 0 ≤ R)
    (hbudget : (N : ℝ)*M*ε ≤ 1/2)
    (hinterval : ∀ i k, i+k ≤ N → ∀ x y,
      dist (run A i k x) (run A i k y) ≤ M*dist x y)
    (hideal : ∀ k, k ≤ N → ‖run A 0 k (z 0)‖ ≤ R)
    (hloc : ∀ j, j < N → dist (z (j+1)) (A j (z j)) ≤ ε*(1 + ‖z j‖)) :
    ∀ k, k ≤ N → ‖z k‖ ≤ 2*R+1 ∧
      dist (z k) (run A 0 k (z 0)) ≤ (k : ℝ)*M*ε*(2+2*R) := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro hk
    have hlocal : ∀ j, 0 ≤ j → j < 0+k →
        dist (z (j+1)) (A j (z j)) ≤ ε*(2+2*R) := by
      intro j _ h
      have hj : j < k := by omega
      have prev := (ih j hj (by omega)).1
      exact (hloc j (by omega)).trans (mul_le_mul_of_nonneg_left (by linarith) hε)
    have herr := segment A z N M (ε*(2+2*R)) hM hinterval k 0 (by omega) hlocal
    simp only [zero_add] at herr
    have hn : (k : ℝ) ≤ N := by exact_mod_cast hk
    have hcoeff : (k : ℝ)*M*ε ≤ 1/2 :=
      (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_right hn hM) hε).trans hbudget
    have ht := mul_le_mul_of_nonneg_right hcoeff (show 0 ≤ 2+2*R by linarith)
    have hnorm := norm_le_insert' (z k) (run A 0 k (z 0))
    rw [← dist_eq_norm] at hnorm
    constructor
    · nlinarith [hideal k hk]
    · calc
        _ ≤ (k : ℝ)*M*(ε*(2+2*R)) := herr
        _ = _ := by ring

#print axioms segment
#print axioms bounded_computation

end DirectTensorStability

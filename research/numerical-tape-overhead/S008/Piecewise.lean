import Mathlib.Data.Nat.Log
import S008.WholeProfile

/-! A finite, nondecreasing surplus at the actual spatial child widths,
    and the two-branch numerical clock at the R=240 endpoint. -/
namespace S008.Piecewise

open S008.NumericalCutoff S008.WholeProfile
open scoped BigOperators

/-- The log address actually used by a spatial child of bit width f. -/
def activeLog (f : ℕ) : ℕ := Nat.clog 2 (f+2)

theorem activeLog_mono : Monotone activeLog := by
  intro f a h
  exact Nat.clog_mono_right 2 (Nat.add_le_add_right h 2)

/-- Prefix surplus, sampled at the integer arguments used by recursion. -/
noncomputable def history (H : ℕ → ℝ) : ℕ → ℝ
  | 0 => max 0 (H 0 - (159/4:ℝ)*phi 0)
  | n+1 => max (history H n) (H (n+1) - (159/4:ℝ)*phi ((n+1:ℕ):ℝ))

noncomputable def envelope (H : ℕ → ℝ) (n : ℕ) : ℝ :=
  48*phi (n:ℝ) + history H n

theorem history_mono (H : ℕ → ℝ) : Monotone (history H) :=
  monotone_nat_of_le_succ (fun _ => le_max_left _ _)

theorem history_nonneg (H : ℕ → ℝ) (n : ℕ) : 0 ≤ history H n :=
  (le_max_left _ _ : 0 ≤ history H 0).trans (history_mono H (Nat.zero_le n))

theorem history_current (H : ℕ → ℝ) (n : ℕ) :
    H n - (159/4:ℝ)*phi (n:ℝ) ≤ history H n := by
  cases n with
  | zero => simp [history]
  | succ n => exact le_max_right _ _

theorem history_upper (H : ℕ → ℝ) {n : ℕ} {D : ℝ} (hD : 0 ≤ D)
    (h : ∀ j ≤ n, H j - (159/4:ℝ)*phi (j:ℝ) ≤ D) : history H n ≤ D := by
  induction n with
  | zero => simpa [history] using (max_le hD (h 0 (le_refl _)))
  | succ n ih =>
    exact max_le (ih fun j hj => h j (Nat.le_succ_of_le hj)) (h (n+1) (le_refl _))

/-- The native bill at any rounded existential child left in the local data
    invoice fits the parent bound. H itself is only sampled, not required monotone. -/
theorem covers_earlier (H : ℕ → ℝ) {v x : ℕ} (hv : v ≤ x)
    (hphi : phi (v:ℝ) ≤ phi (x:ℝ)) :
    H v + (33/4:ℝ)*phi (x:ℝ) ≤ envelope H x := by
  have h := (history_current H v).trans (history_mono H hv)
  unfold envelope
  linarith

/-- An index represents a paid child invocation, including repeat uses. The factor
    w may contain the occupied child volume and its own square-root width. -/
theorem weighted_quarter {ι : Type*} (s : Finset ι) (f : ι → ℕ) (a : ℕ)
    (w : ι → ℝ) (parent : ℝ) (H : ℕ → ℝ)
    (hf : ∀ i ∈ s, f i ≤ a) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hq : ∑ i ∈ s, w i*(2:ℝ)^(48*phi (activeLog (f i):ℝ)) ≤
      parent*(2:ℝ)^(48*phi (activeLog a:ℝ))/4) :
    ∑ i ∈ s, w i*(2:ℝ)^(envelope H (activeLog (f i))) ≤
      parent*(2:ℝ)^(envelope H (activeLog a))/4 := by
  have h2 : (0:ℝ) < 2 := by norm_num
  calc
    _ ≤ ∑ i ∈ s, (w i*(2:ℝ)^(48*phi (activeLog (f i):ℝ))) *
        (2:ℝ)^(history H (activeLog a)) := by
      apply Finset.sum_le_sum
      intro i hi
      rw [envelope, Real.rpow_add h2, ← mul_assoc]
      exact mul_le_mul_of_nonneg_left
        (Real.rpow_le_rpow_of_exponent_le (by norm_num) (history_mono H (activeLog_mono (hf i hi))))
        (mul_nonneg (hw i hi) (Real.rpow_nonneg h2.le _))
    _ = (∑ i ∈ s, w i*(2:ℝ)^(48*phi (activeLog (f i):ℝ))) *
        (2:ℝ)^(history H (activeLog a)) := by rw [Finset.sum_mul]
    _ ≤ (parent*(2:ℝ)^(48*phi (activeLog a:ℝ))/4) *
        (2:ℝ)^(history H (activeLog a)) :=
        mul_le_mul_of_nonneg_right hq (Real.rpow_nonneg h2.le _)
    _ = _ := by rw [envelope, Real.rpow_add h2]; ring


end S008.Piecewise

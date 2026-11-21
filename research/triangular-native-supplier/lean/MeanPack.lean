import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.Linarith

namespace TriangularSupplier

variable {I : Type*}

/-- One true Fourier row is a mean of phases. A hole returns its original value. -/
noncomputable def axis (rows : I → Option (Finset I)) (phase : I → I → ℂ)
    (x : I → ℂ) (i : I) : ℂ :=
  match rows i with
  | none => x i
  | some t => ((t.card : ℝ)⁻¹) • ∑ j ∈ t, phase i j * x j

def Close (r : ℝ) (x y : I → ℂ) : Prop := ∀ i, ‖x i - y i‖ ≤ r

theorem mean_contracts (rows : I → Option (Finset I)) (phase : I → I → ℂ)
    (unit : ∀ i j, ‖phase i j‖ ≤ 1) {r : ℝ} (hr : 0 ≤ r)
    {x y : I → ℂ} (h : Close r x y) :
    Close r (axis rows phase x) (axis rows phase y) := by
  intro i
  cases e : rows i with
  | none => simpa [axis, e] using h i
  | some t =>
    simp only [axis, e, ← smul_sub, ← Finset.sum_sub_distrib, ← mul_sub, norm_smul,
      Real.norm_eq_abs, abs_inv, abs_of_nonneg (Nat.cast_nonneg t.card : (0 : ℝ) ≤ t.card)]
    by_cases pos : t.Nonempty
    · have ct : (0 : ℝ) < t.card := by exact_mod_cast Finset.card_pos.mpr pos
      apply (inv_mul_le_iff₀ ct).2
      calc ‖∑ j ∈ t, phase i j * (x j - y j)‖
          ≤ ∑ j ∈ t, ‖phase i j * (x j - y j)‖ := norm_sum_le _ _
        _ ≤ ∑ _j ∈ t, r := Finset.sum_le_sum (fun j _ => by
          rw [norm_mul]
          calc ‖phase i j‖ * ‖x j - y j‖ ≤ 1 * ‖x j - y j‖ :=
                 mul_le_mul_of_nonneg_right (unit i j) (norm_nonneg _)
               _ ≤ r := by simpa using h j)
        _ = _ := by simp
    · simp [Finset.not_nonempty_iff_eq_empty.mp pos, hr]

theorem pack_error (ideal measured : ℕ → I → ℂ) (pack : ℕ → (I → ℂ) → I → ℂ)
    (count : ℕ) (δ : ℝ) (hδ : 0 ≤ δ) (budget : (count : ℝ) * δ ≤ 1)
    (entry : measured 0 = ideal 0)
    (ideal_step : ∀ j, j < count → ideal (j+1) = pack j (ideal j))
    (inside : ∀ j, j ≤ count → ∀ i, ‖ideal j i‖ ≤ 1)
    (contract : ∀ j, j < count → ∀ {r x y}, 0 ≤ r → Close r x y →
      Close r (pack j x) (pack j y))
    (local_error : ∀ j, j < count → (∀ i, ‖measured j i‖ ≤ 2) →
      Close δ (measured (j+1)) (pack j (measured j))) :
    ∀ k, k ≤ count → Close ((k : ℝ)*δ) (measured k) (ideal k) := by
  intro k
  induction k with
  | zero => intro _ i; simp [entry]
  | succ k ih =>
    intro hk
    have lt : k < count := hk
    have prev := ih (Nat.le_of_lt lt)
    have small : (k : ℝ)*δ ≤ 1 :=
      (mul_le_mul_of_nonneg_right (by exact_mod_cast Nat.le_of_lt lt) hδ).trans budget
    have radius (i : I) : ‖measured k i‖ ≤ 2 := by
      have tri := norm_sub_le (measured k i - ideal k i) (-ideal k i)
      simp only [sub_neg_eq_add, sub_add_cancel, norm_neg] at tri
      linarith [prev i, inside k (Nat.le_of_lt lt) i]
    intro i
    rw [ideal_step k lt]
    have tri := norm_sub_le_norm_sub_add_norm_sub (measured (k+1) i)
      (pack k (measured k) i) (pack k (ideal k) i)
    have left := local_error k lt radius i
    have right := contract k lt (mul_nonneg (Nat.cast_nonneg k) hδ) prev i
    push_cast
    linarith

#print axioms mean_contracts
#print axioms pack_error

end TriangularSupplier

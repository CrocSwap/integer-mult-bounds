import MultitapeToolkit.Model
import Mathlib.Analysis.Asymptotics.Defs
import Mathlib.Order.Filter.AtTopBot.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Certified multitape runtimes and quadratic asymptotics

All complexity claims in this layer bind time witnesses to actual executions of
an explicitly supplied finite-control machine, to halting, and to a semantic
output predicate. A uniform concrete quadratic bound implies the usual real
`IsBigO` statement; fixed affine overhead preserves it.
-/

namespace MultitapeToolkit

open Filter Asymptotics

variable {ι Γ Q X : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- A universal sufficient time bound on all inputs, including semantic output. -/
def ComputesInTime (M : Machine ι Γ Q) (input : X → Config ι Γ Q)
    (output : X → Config ι Γ Q → Prop) (size : X → ℕ) (T : ℕ → ℕ) : Prop :=
  ∀ x, ∃ t final, t ≤ T (size x) ∧ Runs M t (input x) final ∧
    Halts M final ∧ output x final

/-- Actual time and output witnesses for a family of completed computations. -/
structure CertifiedRuntime (M : Machine ι Γ Q) (input : X → Config ι Γ Q)
    (output : X → Config ι Γ Q → Prop) where
  time : X → ℕ
  final : X → Config ι Γ Q
  runs : ∀ x, Runs M (time x) (input x) (final x)
  halted : ∀ x, Halts M (final x)
  correct : ∀ x, output x (final x)

/-- Certified executions and a concrete bound establish universal computation. -/
theorem CertifiedRuntime.computesInTime {M : Machine ι Γ Q}
    {input : X → Config ι Γ Q} {output : X → Config ι Γ Q → Prop}
    (R : CertifiedRuntime M input output) (size : X → ℕ) (T : ℕ → ℕ)
    (h : ∀ x, R.time x ≤ T (size x)) : ComputesInTime M input output size T := by
  intro x
  exact ⟨R.time x, R.final x, h x, R.runs x, R.halted x, R.correct x⟩

/-- Choosing already-proved executions does not assume a machine or compiler. -/
noncomputable def certifiedOfComputesInTime {M : Machine ι Γ Q}
    {input : X → Config ι Γ Q} {output : X → Config ι Γ Q → Prop}
    {size : X → ℕ} {T : ℕ → ℕ} (h : ComputesInTime M input output size T) :
    CertifiedRuntime M input output where
  time x := Classical.choose (h x)
  final x := Classical.choose (Classical.choose_spec (h x))
  runs x := (Classical.choose_spec (Classical.choose_spec (h x))).2.1
  halted x := (Classical.choose_spec (Classical.choose_spec (h x))).2.2.1
  correct x := (Classical.choose_spec (Classical.choose_spec (h x))).2.2.2

/-- Choice retains the concrete bound of every actual execution witness. -/
theorem certifiedOfComputesInTime_bound {M : Machine ι Γ Q}
    {input : X → Config ι Γ Q} {output : X → Config ι Γ Q → Prop}
    {size : X → ℕ} {T : ℕ → ℕ} (h : ComputesInTime M input output size T) (x : X) :
    (certifiedOfComputesInTime h).time x ≤ T (size x) :=
  (Classical.choose_spec (Classical.choose_spec (h x))).1

/-- Converting a concrete natural quadratic bound to standard asymptotic notation. -/
theorem quadratic_bound_isBigO (t : ℕ → ℕ) (C : ℕ)
    (h : ∀ n, t n ≤ C * (n + 1) ^ 2) :
    (fun n : ℕ => (t n : ℝ)) =O[atTop] (fun n : ℕ => (n : ℝ) ^ 2) := by
  refine isBigO_iff.mpr ⟨4 * (C : ℝ), ?_⟩
  apply (eventually_ge_atTop (1 : ℕ)).mono
  intro n hn
  have hshift : (n + 1) ^ 2 ≤ 4 * n ^ 2 := by nlinarith
  have hnat : t n ≤ 4 * C * n ^ 2 := by
    calc
      t n ≤ C * (n + 1) ^ 2 := h n
      _ ≤ C * (4 * n ^ 2) := Nat.mul_le_mul_left C hshift
      _ = 4 * C * n ^ 2 := by ring
  have hreal : (t n : ℝ) ≤ 4 * (C : ℝ) * (n : ℝ) ^ 2 := by
    exact_mod_cast hnat
  simpa [Real.norm_eq_abs] using hreal

/-- Fixed multiplicative and additive work preserves a concrete quadratic bound. -/
theorem affine_overhead_bound (t : ℕ → ℕ) (A B C : ℕ)
    (h : ∀ n, t n ≤ C * (n + 1) ^ 2) (n : ℕ) :
    A * t n + B ≤ (A * C + B) * (n + 1) ^ 2 := by
  have hone : 1 ≤ n + 1 := Nat.succ_le_succ (Nat.zero_le n)
  have hsquare : 1 ≤ (n + 1) ^ 2 := by
    simpa [pow_two] using Nat.mul_le_mul hone hone
  have hmul := Nat.mul_le_mul_left A (h n)
  have hconst : B ≤ B * (n + 1) ^ 2 := by
    simpa using Nat.mul_le_mul_left B hsquare
  calc
    A * t n + B ≤ A * (C * (n + 1) ^ 2) + B := Nat.add_le_add_right hmul B
    _ ≤ A * (C * (n + 1) ^ 2) + B * (n + 1) ^ 2 := Nat.add_le_add_left hconst _
    _ = (A * C + B) * (n + 1) ^ 2 := by ring

/-- Actual work dominated by fixed affine overhead remains quadratic. -/
theorem affine_overhead_isBigO (t s : ℕ → ℕ) (A B C : ℕ)
    (h : ∀ n, t n ≤ C * (n + 1) ^ 2)
    (hover : ∀ n, s n ≤ A * t n + B) :
    (fun n : ℕ => (s n : ℝ)) =O[atTop] (fun n : ℕ => (n : ℝ) ^ 2) := by
  apply quadratic_bound_isBigO s (A * C + B)
  intro n
  exact (hover n).trans (affine_overhead_bound t A B C h n)

/-- A quadratic bound on actual completed computations implies quadratic runtime. -/
theorem CertifiedRuntime.quadratic_isBigO {M : Machine ι Γ Q}
    {input : X → Config ι Γ Q} {output : X → Config ι Γ Q → Prop}
    (R : CertifiedRuntime M input output) (select : ℕ → X) (C : ℕ)
    (h : ∀ n, R.time (select n) ≤ C * (n + 1) ^ 2) :
    (fun n : ℕ => (R.time (select n) : ℝ)) =O[atTop]
      (fun n : ℕ => (n : ℝ) ^ 2) :=
  quadratic_bound_isBigO (fun n => R.time (select n)) C h

/-- Every universal quadratic computation bound has certified quadratic runtimes
along every sequence of inputs whose sizes are bounded by its index. -/
theorem computesInTime_quadratic {M : Machine ι Γ Q}
    {input : X → Config ι Γ Q} {output : X → Config ι Γ Q → Prop}
    {size : X → ℕ} {C : ℕ}
    (h : ComputesInTime M input output size (fun n => C * (n + 1) ^ 2)) :
    ∃ R : CertifiedRuntime M input output,
      (∀ x, R.time x ≤ C * (size x + 1) ^ 2) ∧
      ∀ select : ℕ → X, (∀ n, size (select n) ≤ n) →
        (fun n : ℕ => (R.time (select n) : ℝ)) =O[atTop]
          (fun n : ℕ => (n : ℝ) ^ 2) := by
  refine ⟨certifiedOfComputesInTime h, certifiedOfComputesInTime_bound h, ?_⟩
  intro select hsize
  apply CertifiedRuntime.quadratic_isBigO _ select C
  intro n
  exact (certifiedOfComputesInTime_bound h (select n)).trans
    (Nat.mul_le_mul_left C (pow_le_pow_left' (Nat.add_le_add_right (hsize n) 1) 2))

end MultitapeToolkit







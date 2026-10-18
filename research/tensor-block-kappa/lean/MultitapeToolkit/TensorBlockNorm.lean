import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic

/-! Squared-norm accounting for direct sums of tensor-isomorphic blocks.
No independence assumption is made on the initial block values.
Concrete hosted endpoints and ownership are certified separately. -/
namespace MultitapeToolkit.TensorBlockNorm

/-- Coordinatewise growth depends on the number of active steps on that block,
not the total number of steps across unrelated blocks. -/
theorem block_energy_prefix {I : Type*} (energy : Nat → I → Real)
    (cost : Nat → I → Nat)
    (hstep : ∀ t i, energy (t+1) i ≤ (4:Real)^(cost t i) * energy t i)
    (t : Nat) (i : I) :
    energy t i ≤ (4:Real)^(∑ s ∈ Finset.range t, cost s i) * energy 0 i := by
  induction t with
  | zero => simp
  | succ t ih =>
    calc
      energy (t+1) i ≤ (4:Real)^(cost t i) * energy t i := hstep t i
      _ ≤ (4:Real)^(cost t i) * ((4:Real)^(∑ s ∈ Finset.range t, cost s i) * energy 0 i) :=
        mul_le_mul_of_nonneg_left ih (by positivity)
      _ = (4:Real)^(∑ s ∈ Finset.range (t+1), cost s i) * energy 0 i := by
        rw [Finset.sum_range_succ, pow_add]
        ring

/-- A direct-sum energy bound uniform in the number of blocks. In particular,
unitary actions on donor blocks cost zero even with correlated initial data. -/
theorem total_energy_bound {I : Type*} [Fintype I]
    (energy : Nat → I → Real) (cost : Nat → I → Nat)
    (hinit : ∀ i, 0 ≤ energy 0 i)
    (hstep : ∀ t i, energy (t+1) i ≤ (4:Real)^(cost t i) * energy t i)
    (t depth : Nat)
    (hdepth : ∀ i, (∑ s ∈ Finset.range t, cost s i) ≤ depth) :
    (∑ i, energy t i) ≤ (4:Real)^depth * ∑ i, energy 0 i := by
  calc
    (∑ i, energy t i) ≤ ∑ i, (4:Real)^depth * energy 0 i := by
      apply Finset.sum_le_sum
      intro i hi
      exact (block_energy_prefix energy cost hstep t i).trans
        (mul_le_mul_of_nonneg_right (pow_le_pow_right₀ (by norm_num) (hdepth i)) (hinit i))
    _ = (4:Real)^depth * ∑ i, energy 0 i := by rw [Finset.mul_sum]

/-- Eighteen active block steps give the same squared-norm multiplier for any
number of replicas; all other completed actions must be block isometries. -/
theorem eighteen_step_energy_bound {I : Type*} [Fintype I]
    (energy : Nat → I → Real) (cost : Nat → I → Nat)
    (hinit : ∀ i, 0 ≤ energy 0 i)
    (hstep : ∀ t i, energy (t+1) i ≤ (4:Real)^(cost t i) * energy t i)
    (t : Nat) (hdepth : ∀ i, (∑ s ∈ Finset.range t, cost s i) ≤ 18) :
    (∑ i, energy t i) ≤ (2:Real)^36 * ∑ i, energy 0 i := by
  convert total_energy_bound energy cost hinit hstep t 18 hdepth using 1 <;> norm_num

/-- Numeric precision envelope after the topology and local-prefix checks.
The strict slack permits a conservative extra scratch bit. -/
theorem hosted_prefix_reserve :
    (70 + 37 + 18 + 1330 + 1 + 4 : Nat) < 2048 ∧
      (128 + 37 + 18 + 1330 + 1 + 4 : Nat) < 2048 := by
  norm_num

/-- A unit-coefficient shear costs at most a factor two in Hilbert norm,
expressed here through norms of the two summands. -/
theorem shear_energy_bound {V : Type*} [SeminormedAddCommGroup V] (x y : V) :
    ‖x+y‖^2 + ‖y‖^2 ≤ 4 * (‖x‖^2 + ‖y‖^2) := by
  have h := norm_add_le x y
  have hx := norm_nonneg x
  have hy := norm_nonneg y
  have hz := norm_nonneg (x+y)
  have hs : ‖x+y‖^2 ≤ (‖x‖+‖y‖)^2 := by nlinarith
  nlinarith [sq_nonneg (‖x‖-‖y‖)]

end MultitapeToolkit.TensorBlockNorm

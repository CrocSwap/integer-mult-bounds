import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMMultiplyMacro20261001
import Mathlib.Analysis.Asymptotics.Defs

set_option autoImplicit false

/-!
# Exact binary schoolbook multiplication with quadratic stack-machine cost

The input convention of this module is a prepared six-stack configuration:
multiplier and multiplicand are least-significant-bit-first words of width `2*n`,
and the accumulator is an equally wide zero word.  The bounds count the existing
TM2 macro transitions, including the final halt transition.  Preparing serialized
input and translating each macro transition to conventional tape transitions are
separate costs, accounted for by the multitape integration module.
-/

namespace MultitapeToolkit.BinaryMultiplication

open Lax51Proofs.RamToTM
open Filter Asymptotics

/-- Double operand width keeps the entire product, without modular truncation. -/
def productWidth (n : ℕ) : ℕ := 2 * n

/-- Prepared machine configuration; this is not a serialized-input loader. -/
def preparedInput (n a b : ℕ) : mulMachine.Cfg :=
  mulOuterCfg (fixedBits (productWidth n) b) (fixedBits (productWidth n) a)
    (fixedBits (productWidth n) 0)

/-- A halted configuration retains the accumulator for output inspection. -/
def mulHaltedCfg (multiplicand accumulator : List Bool) : mulMachine.Cfg where
  l := none
  var := default
  stk := mulStacks [] multiplicand accumulator [] [] []

/-- Count through the transition which changes the control label to `none`. -/
def macroTime (n b : ℕ) : ℕ :=
  mulRunTime (fixedBits (productWidth n) b) (productWidth n) + 1

@[simp] theorem mul_done_halts (m a : List Bool) :
    mulMachine.step (mulDoneCfg m a) = some (mulHaltedCfg m a) := by
  rfl

@[simp] theorem mul_halted_step (m a : List Bool) :
    mulMachine.step (mulHaltedCfg m a) = none := by
  rfl

/-- Product fits in double width, including zero-width operands. -/
theorem product_lt_double_width {n a b : ℕ}
    (ha : a < 2 ^ n) (hb : b < 2 ^ n) :
    a * b < 2 ^ productWidth n := by
  have h := Nat.mul_lt_mul_of_lt_of_lt ha hb
  simpa [productWidth, two_mul, pow_add] using h

/-- An operand also fits in the double-width workspace. -/
theorem operand_lt_double_width {n a : ℕ} (ha : a < 2 ^ n) :
    a < 2 ^ productWidth n := by
  exact ha.trans_le (Nat.pow_le_pow_right (by decide) (by simp only [productWidth]; omega))

/-- The output decodes to the exact natural-number product. -/
theorem output_decode {n a b : ℕ} (ha : a < 2 ^ n) (hb : b < 2 ^ n) :
    bitsValue (fixedBits (productWidth n) (a * b)) = a * b :=
  bitsValue_fixedBits_of_lt (product_lt_double_width ha hb)

/-- Trailing zero bits leave the decoded value unchanged. -/
theorem bitsValue_append_zeros (bits : List Bool) (n : ℕ) :
    bitsValue (bits ++ List.replicate n false) = bitsValue bits := by
  induction bits with
  | nil => simp [bitsValue]
  | cons b bits ih => simp [bitsValue, ih]

/-- Zero extension of an operand to the multiplication workspace. -/
theorem fixedBits_pad {n a : ℕ} (ha : a < 2 ^ n) :
    fixedBits n a ++ List.replicate n false = fixedBits (productWidth n) a := by
  apply bitsValue_injective_of_length
  · simp [productWidth, two_mul]
  · rw [bitsValue_append_zeros, bitsValue_fixedBits_of_lt ha,
      bitsValue_fixedBits_of_lt (operand_lt_double_width ha)]

/-- Inspecting the output stack of any such terminal configuration gives the
whole product, independently of the final temporary multiplicand. -/
theorem terminal_output {n a b : ℕ} (ha : a < 2 ^ n) (hb : b < 2 ^ n)
    (finalMultiplicand : List Bool) :
    bitsValue ((mulHaltedCfg finalMultiplicand
      (fixedBits (productWidth n) (a * b))).stk MulStack.accumulator) = a * b := by
  exact output_decode ha hb
/-- Full correctness and halt for the prepared macro input.  No positive-width
assumption is imposed on callers: at width zero both encoded operands are zero. -/
theorem exact_product_halts (n a b : ℕ) (ha : a < 2 ^ n) (hb : b < 2 ^ n) :
    ∃ finalMultiplicand : List Bool,
      finalMultiplicand.length = productWidth n ∧
      ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[macroTime n b])
        (some (preparedInput n a b)) =
      some (mulHaltedCfg finalMultiplicand (fixedBits (productWidth n) (a * b))) ∧
      bitsValue (fixedBits (productWidth n) (a * b)) = a * b := by
  have hrun : ∃ finalMultiplicand : List Bool,
      finalMultiplicand.length = productWidth n ∧
      ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
        mulRunTime (fixedBits (productWidth n) b) (productWidth n)])
        (some (preparedInput n a b)) =
      some (mulDoneCfg finalMultiplicand (fixedBits (productWidth n) (a * b))) := by
    by_cases hn : n = 0
    · subst n
      refine ⟨[], rfl, ?_⟩
      change mulMachine.step (mulOuterCfg [] [] []) = some (mulDoneCfg [] [])
      exact mul_step_outer_nil [] []
    · exact mulMachine_fixed_correct_with_length (productWidth n) a b
        (by simp [productWidth]; omega) (operand_lt_double_width hb)
  rcases hrun with ⟨final, hlen, hrun⟩
  refine ⟨final, hlen, ?_, output_decode ha hb⟩
  rw [macroTime, Function.iterate_succ_apply', hrun]
  exact mul_done_halts final (fixedBits (productWidth n) (a * b))

/-- Concrete worst-case bound, inclusive of the halt transition. -/
theorem macroTime_le (n b : ℕ) :
    macroTime n b ≤ 20 * n ^ 2 + 16 * n + 2 := by
  have h := mulMachine_fixed_time_le (productWidth n) b
  have heq : productWidth n * (5 * productWidth n + 8) + 1 + 1 =
      20 * n ^ 2 + 16 * n + 2 := by
    simp only [productWidth]
    ring
  simpa only [macroTime, heq] using Nat.add_le_add_right h 1

/-- For positive operand width, a single constant times `n²` bounds all data. -/
theorem macroTime_le_quadratic (n b : ℕ) (hn : 1 ≤ n) :
    macroTime n b ≤ 38 * n ^ 2 := by
  have h := macroTime_le n b
  have hn2 : n ≤ n ^ 2 := by nlinarith
  have hsq : 1 ≤ n ^ 2 := by nlinarith
  nlinarith

/-- Actual prepared-macro execution counts are `O(n²)`, uniformly for any
choice of multiplier data as a function of width.  Tape compilation and input
loading costs are intentionally absent from this standalone macro statement. -/
theorem macroTime_isBigO (b : ℕ → ℕ) :
    (fun n : ℕ => (macroTime n (b n) : ℝ)) =O[atTop]
      (fun n : ℕ => (n : ℝ) ^ 2) := by
  apply isBigO_iff.mpr
  refine ⟨38, ?_⟩
  filter_upwards [eventually_ge_atTop 1] with n hn
  have h := macroTime_le_quadratic n (b n) hn
  have hcast : (macroTime n (b n) : ℝ) ≤ 38 * (n : ℝ) ^ 2 := by
    exact_mod_cast h
  simpa only [Real.norm_eq_abs, abs_of_nonneg (show (0 : ℝ) ≤ (macroTime n (b n) : ℝ) from Nat.cast_nonneg _),
    abs_of_nonneg (sq_nonneg (n : ℝ))] using hcast

end MultitapeToolkit.BinaryMultiplication





import MultitapeToolkit.Model
import MultitapeToolkit.Complexity
import MultitapeToolkit.TM2Compiler
import MultitapeToolkit.Reused.Computability.BinaryMultiplicationSetup20261013
import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMMultiplyMacro20261001

set_option backward.isDefEq.respectTransparency false

namespace MultitapeToolkit.BinaryMultiplicationIntegration

open MultitapeToolkit
open Lax51Proofs.RamToTM

/-- A fixed finite-state, six-tape binary multiplication machine. -/
structure BinaryMachine where
  State : Type
  finiteState : Fintype State
  start : State
  transition : State → (MulStack → Option Bool) →
    Option (State × (MulStack → Action (Option Bool)))

attribute [instance] BinaryMachine.finiteState

def BinaryMachine.machine (B : BinaryMachine) :
    Machine MulStack (Option Bool) B.State where
  transition := B.transition

/-- Two ordinary n-bit input tapes; all four work tapes are initially blank. -/
def inputTapes (n a b : ℕ) : MulStack → Turing.Tape (Option Bool) :=
  fun k => stackTape (mulStacks (fixedBits n b) (fixedBits n a) [] [] [] [] k)

def BinaryMachine.initial (B : BinaryMachine) (n a b : ℕ) :
    Config MulStack (Option Bool) B.State :=
  ⟨B.start, inputTapes n a b⟩

open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.TM2Compiler

local instance setupStackFinite : Fintype setupMachine.K := inferInstanceAs (Fintype MulStack)
local instance setupLabelFinite : Fintype setupMachine.Λ := inferInstanceAs (Fintype SetupLabel)
local instance setupRegisterFinite : Fintype setupMachine.σ := inferInstanceAs (Fintype MulControl)

/-- One concrete machine, fixed independently of all operand lengths and values. -/
noncomputable def binaryMachine : BinaryMachine where
  State := Control setupMachine.m
  finiteState := inferInstance
  start := (encode setupMachine.m (rawInput 0 0 0)).state
  transition := (compile setupMachine.m).transition

theorem binaryMachine_machine :
    binaryMachine.machine = compile setupMachine.m := rfl

theorem binaryMachine_initial (n a b : ℕ) :
    binaryMachine.initial n a b = encode setupMachine.m (rawInput n a b) := rfl


/-- Every syntax path in the fixed loader/multiplier has at most seven nodes. -/
theorem setup_overhead_le : overhead setupMachine.m ≤ 14 := by
  have h : Finset.univ.sup (fun l : SetupLabel => depth (setupMachine.m l)) ≤ 7 := by
    apply Finset.sup_le
    intro l _
    cases l with
    | inl p =>
      cases p <;> simp [setupMachine, setupIteration, setupBack, depth]
    | inr l =>
      cases l <;> simp [setupMachine, liftMulStmt, mulMachine, mulMoveIteration, depth]
  exact Nat.mul_le_mul_left 2 h

/-- The fixed machine produces the whole product, accounting for input loading,
all elementary tape transitions, and halt. The two supplied operands are n-bit
words; four work tapes begin completely blank. -/
theorem quadratic_binary_multiplication :
    ∃ (B : BinaryMachine) (C : ℕ), ∀ (n a b : ℕ),
      a < 2 ^ n → b < 2 ^ n →
      ∃ (t : ℕ) (final : Config MulStack (Option Bool) B.State),
        t ≤ C * (n + 1) ^ 2 ∧
        Runs B.machine t (B.initial n a b) final ∧
        Halts B.machine final ∧
        final.tapes MulStack.accumulator =
          stackTape (fixedBits (2 * n) (a * b)) ∧
        bitsValue (readStack (2 * n) (final.tapes MulStack.accumulator)) = a * b := by
  refine ⟨binaryMachine, 700, ?_⟩
  intro n a b ha hb
  rcases raw_product_halts n a b ha hb with ⟨final, hlen, hrun, hout⟩
  let terminal := liftMulCfg (mulHaltedCfg final
    (fixedBits (productWidth n) (a * b)))
  have htape := compile_run setupMachine.m (6 * n + 6 + macroTime n b)
    (rawInput n a b) terminal hrun
  rcases htape with ⟨t, ht, hr⟩
  refine ⟨t, encode setupMachine.m terminal, ?_, ?_, ?_, ?_, ?_⟩
  · have hraw := rawTime_le n b
    have hmajor : 6 * n + 6 + macroTime n b ≤ 50 * (n + 1) ^ 2 := by
      nlinarith
    calc
      t ≤ overhead setupMachine.m * (6 * n + 6 + macroTime n b) := ht
      _ ≤ 14 * (6 * n + 6 + macroTime n b) := Nat.mul_le_mul_right _ setup_overhead_le
      _ ≤ 14 * (50 * (n + 1) ^ 2) :=
        Nat.mul_le_mul_left 14 hmajor
      _ = 700 * (n + 1) ^ 2 := by ring
  · simpa only [binaryMachine_machine, binaryMachine_initial] using hr
  · rw [binaryMachine_machine]
    exact encode_halts setupMachine.m _ _
  · rfl
  · change bitsValue (readStack (2 * n)
      (stackTape (fixedBits (2 * n) (a * b)))) = a * b
    have hread := readStack_stackTape (fixedBits (2 * n) (a * b))
    have hread' : readStack (2 * n) (stackTape (fixedBits (2 * n) (a * b))) =
        fixedBits (2 * n) (a * b) := by simpa using hread
    rw [hread']
    exact hout


/-- The produced machine has genuinely quadratic completed runtimes for every
family of valid unsigned operands, including all loading and tape simulation. -/
theorem quadratic_binary_multiplication_asymptotic :
    ∃ B : BinaryMachine,
      ∀ (a b : ℕ → ℕ), (∀ n, a n < 2 ^ n) → (∀ n, b n < 2 ^ n) →
      ∃ (time : ℕ → ℕ) (final : ℕ → Config MulStack (Option Bool) B.State),
        (∀ n, Runs B.machine (time n) (B.initial n (a n) (b n)) (final n) ∧
          Halts B.machine (final n) ∧
          (final n).tapes MulStack.accumulator =
            stackTape (fixedBits (2 * n) (a n * b n))) ∧
        (fun n : ℕ => (time n : ℝ)) =O[Filter.atTop]
          (fun n : ℕ => (n : ℝ) ^ 2) := by
  classical
  rcases quadratic_binary_multiplication with ⟨B, C, h⟩
  refine ⟨B, ?_⟩
  intro a b ha hb
  have hex n := h n (a n) (b n) (ha n) (hb n)
  let time (n : ℕ) := Classical.choose (hex n)
  let final (n : ℕ) := Classical.choose (Classical.choose_spec (hex n))
  have hspec n : time n ≤ C * (n + 1) ^ 2 ∧
      Runs B.machine (time n) (B.initial n (a n) (b n)) (final n) ∧
      Halts B.machine (final n) ∧
      (final n).tapes MulStack.accumulator =
        stackTape (fixedBits (2 * n) (a n * b n)) ∧
      bitsValue (readStack (2 * n) ((final n).tapes MulStack.accumulator)) =
        a n * b n :=
    Classical.choose_spec (Classical.choose_spec (hex n))
  refine ⟨time, final, ?_, quadratic_bound_isBigO time C (fun n => (hspec n).1)⟩
  intro n
  exact ⟨(hspec n).2.1, (hspec n).2.2.1, (hspec n).2.2.2.1⟩

end MultitapeToolkit.BinaryMultiplicationIntegration






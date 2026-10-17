import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSubtractMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

inductive ShiftStack | source | temp | result
  deriving DecidableEq, Fintype, Inhabited

inductive ShiftLabel | first | discard | second | prepend | done
  deriving DecidableEq, Fintype, Inhabited

def shiftMachine : Turing.FinTM2 where
  K := ShiftStack
  k₀ := .source
  k₁ := .result
  Γ _ := Bool
  Λ := ShiftLabel
  main := .first
  σ := MoveControl
  initialState := default
  m
    | .first => moveIteration .source .temp .first .discard
    | .discard => .pop .temp (fun _ _ => ⟨none⟩) (.goto fun _ => .second)
    | .second => moveIteration .temp .result .second .prepend
    | .prepend => .push .result (fun _ => false) (.goto fun _ => .done)
    | .done => .halt

def shiftStacks (source temp result : List Bool) : ShiftStack → List Bool
  | .source => source
  | .temp => temp
  | .result => result

def shiftCfg (l : ShiftLabel) (source temp result : List Bool) : shiftMachine.Cfg where
  l := some l
  var := ⟨none⟩
  stk := shiftStacks source temp result

@[simp] theorem shift_step_first_cons (a : Bool) (as temp result : List Bool) :
    shiftMachine.step (shiftCfg .first (a :: as) temp result) =
      some (shiftCfg .first as (a :: temp) result) := by
  change some (TM2.stepAux
    (moveIteration ShiftStack.source ShiftStack.temp ShiftLabel.first ShiftLabel.discard)
    ⟨none⟩ (shiftStacks (a :: as) temp result)) = _
  simp [moveIteration, shiftCfg, shiftStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem shift_step_first_nil (temp result : List Bool) :
    shiftMachine.step (shiftCfg .first [] temp result) =
      some (shiftCfg .discard [] temp result) := by
  change some (TM2.stepAux
    (moveIteration ShiftStack.source ShiftStack.temp ShiftLabel.first ShiftLabel.discard)
    ⟨none⟩ (shiftStacks [] temp result)) = _
  simp [moveIteration, shiftCfg, shiftStacks]

@[simp] theorem shift_step_discard (source result : List Bool) :
    shiftMachine.step (shiftCfg .discard source [] result) =
      some (shiftCfg .second source [] result) := by
  change some (TM2.stepAux
    (.pop ShiftStack.temp (fun _ _ => (⟨none⟩ : MoveControl))
      (.goto fun _ => ShiftLabel.second))
    ⟨none⟩ (shiftStacks source [] result)) = _
  simp [shiftCfg, shiftStacks]

@[simp] theorem shift_step_discard_cons (source result : List Bool) (a : Bool)
    (temp : List Bool) :
    shiftMachine.step (shiftCfg .discard source (a :: temp) result) =
      some (shiftCfg .second source temp result) := by
  change some (TM2.stepAux
    (.pop ShiftStack.temp (fun _ _ => (⟨none⟩ : MoveControl))
      (.goto fun _ => ShiftLabel.second))
    ⟨none⟩ (shiftStacks source (a :: temp) result)) = _
  simp [shiftCfg, shiftStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem shift_step_discard_any (source temp result : List Bool) :
    shiftMachine.step (shiftCfg .discard source temp result) =
      some (shiftCfg .second source temp.tail result) := by
  cases temp with
  | nil => exact shift_step_discard source result
  | cons a temp => exact shift_step_discard_cons source result a temp

@[simp] theorem shift_step_second_cons (source result : List Bool) (a : Bool)
    (temp : List Bool) :
    shiftMachine.step (shiftCfg .second source (a :: temp) result) =
      some (shiftCfg .second source temp (a :: result)) := by
  change some (TM2.stepAux
    (moveIteration ShiftStack.temp ShiftStack.result ShiftLabel.second ShiftLabel.prepend)
    ⟨none⟩ (shiftStacks source (a :: temp) result)) = _
  simp [moveIteration, shiftCfg, shiftStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem shift_step_second_nil (source result : List Bool) :
    shiftMachine.step (shiftCfg .second source [] result) =
      some (shiftCfg .prepend source [] result) := by
  change some (TM2.stepAux
    (moveIteration ShiftStack.temp ShiftStack.result ShiftLabel.second ShiftLabel.prepend)
    ⟨none⟩ (shiftStacks source [] result)) = _
  simp [moveIteration, shiftCfg, shiftStacks]

@[simp] theorem shift_step_prepend (source temp result : List Bool) :
    shiftMachine.step (shiftCfg .prepend source temp result) =
      some (shiftCfg .done source temp (false :: result)) := by
  change some (TM2.stepAux
    (.push ShiftStack.result (fun _ : MoveControl => false)
      (.goto fun _ => ShiftLabel.done))
    ⟨none⟩ (shiftStacks source temp result)) = _
  simp [shiftCfg, shiftStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem shift_first_iterate (source temp result : List Bool) :
    ((fun o : Option shiftMachine.Cfg => o.bind shiftMachine.step)^[source.length])
      (some (shiftCfg .first source temp result)) =
      some (shiftCfg .first [] (source.reverse ++ temp) result) := by
  induction source generalizing temp with
  | nil => rfl
  | cons a as ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, shift_step_first_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem shift_second_iterate (source temp result : List Bool) :
    ((fun o : Option shiftMachine.Cfg => o.bind shiftMachine.step)^[temp.length])
      (some (shiftCfg .second source temp result)) =
      some (shiftCfg .second source [] (temp.reverse ++ result)) := by
  induction temp generalizing result with
  | nil => rfl
  | cons a temp ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, shift_step_second_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem shiftMachine_correct_nonempty (a : Bool) (as : List Bool) :
    ((fun o : Option shiftMachine.Cfg => o.bind shiftMachine.step)^[2 * (a :: as).length + 3])
      (some (shiftCfg .first (a :: as) [] [])) =
      some (shiftCfg .done [] [] (shiftLeftBits (a :: as))) := by
  let stepO := fun o : Option shiftMachine.Cfg => o.bind shiftMachine.step
  have chain {m n : ℕ} {x y z : Option shiftMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have hfirst := shift_first_iterate (a :: as) [] []
  have hsecond := shift_second_iterate ([] : List Bool) (a :: as).reverse.tail []
  simp only [List.append_nil] at hfirst hsecond
  have h₁ : (stepO^[1]) (some (shiftCfg .first [] (a :: as).reverse [])) =
      some (shiftCfg .discard [] (a :: as).reverse []) := by
    simpa [stepO] using shift_step_first_nil (a :: as).reverse ([] : List Bool)
  have h₂ : (stepO^[1]) (some (shiftCfg .discard [] (a :: as).reverse [])) =
      some (shiftCfg .second [] (a :: as).reverse.tail []) := by
    simpa [stepO] using shift_step_discard_any ([] : List Bool) (a :: as).reverse []
  have h₃ : (stepO^[1])
      (some (shiftCfg .second [] [] (a :: as).reverse.tail.reverse)) =
      some (shiftCfg .prepend [] [] (a :: as).reverse.tail.reverse) := by
    simpa [stepO] using
      shift_step_second_nil ([] : List Bool) (a :: as).reverse.tail.reverse
  have h₄ : (stepO^[1])
      (some (shiftCfg .prepend [] [] (a :: as).reverse.tail.reverse)) =
      some (shiftCfg .done [] [] (false :: (a :: as).reverse.tail.reverse)) := by
    simpa [stepO] using
      shift_step_prepend ([] : List Bool) ([] : List Bool) (a :: as).reverse.tail.reverse
  have h01 := chain hfirst h₁
  have h02 := chain h01 h₂
  have h03 := chain h02 hsecond
  have h04 := chain h03 h₃
  have h05 := chain h04 h₄
  dsimp [stepO] at h05
  have hexp :
      1 + (1 + ((a :: as).reverse.tail.length + (1 + (1 + (as.length + 1))))) =
        2 * (a :: as).length + 3 := by simp; omega
  rw [hexp] at h05
  have hout : (a :: as).reverse.tail.reverse = (a :: as).take as.length := by
    rw [List.tail_reverse, List.reverse_reverse, List.dropLast_eq_take]
    simp
  rw [hout] at h05
  simpa [shiftLeftBits] using h05

end Lax51Proofs.RamToTM

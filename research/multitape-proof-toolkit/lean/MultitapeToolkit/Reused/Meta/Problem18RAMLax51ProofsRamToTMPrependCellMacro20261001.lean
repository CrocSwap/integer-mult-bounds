import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMLiteralWordMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-! A sparse write is represented by prepending a serialized cell.  The
address and value inputs are reversed fixed-width words, which is the common
orientation used by the lookup and arithmetic macros. -/

structure PrependCellControl where
  held : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

inductive PrependCellStack | address | value | memory
  deriving DecidableEq, Fintype, Inhabited

inductive PrependCellLabel
  | cellEnd | valueEnd | value | addressEnd | address | done
  deriving DecidableEq, Fintype, Inhabited

def prependCellMoveIteration {K Λ : Type} [DecidableEq K]
    (source target : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ PrependCellControl :=
  .pop source (fun _ a => ⟨a⟩) <|
    .branch (fun s => s.held.isNone)
      (.goto fun _ => done)
      (.push target (fun s => s.held.getD (.bit false)) <|
        .load (fun _ => default) <| .goto fun _ => loop)

def prependCellMachine : Turing.FinTM2 where
  K := PrependCellStack
  k₀ := .address
  k₁ := .memory
  Γ _ := SparseSymbol
  Λ := PrependCellLabel
  main := .cellEnd
  σ := PrependCellControl
  initialState := default
  m
    | .cellEnd => .push .memory (fun _ => .cellEnd) <| .goto fun _ => .valueEnd
    | .valueEnd => .push .memory (fun _ => .wordEnd) <| .goto fun _ => .value
    | .value => prependCellMoveIteration .value .memory .value .addressEnd
    | .addressEnd => .push .memory (fun _ => .wordEnd) <| .goto fun _ => .address
    | .address => prependCellMoveIteration .address .memory .address .done
    | .done => .halt

def prependCellStacks (address value memory : List SparseSymbol) :
    PrependCellStack → List SparseSymbol
  | .address => address
  | .value => value
  | .memory => memory

def prependCellCfg (label : PrependCellLabel)
    (address value memory : List SparseSymbol) : prependCellMachine.Cfg where
  l := some label
  var := default
  stk := prependCellStacks address value memory

@[simp] theorem prependCell_step_cellEnd (address value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .cellEnd address value memory) =
      some (prependCellCfg .valueEnd address value (.cellEnd :: memory)) := by
  simp [prependCellMachine, prependCellCfg, prependCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_valueEnd (address value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .valueEnd address value memory) =
      some (prependCellCfg .value address value (.wordEnd :: memory)) := by
  simp [prependCellMachine, prependCellCfg, prependCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_value_cons (a : SparseSymbol)
    (address value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .value address (a :: value) memory) =
      some (prependCellCfg .value address value (a :: memory)) := by
  simp [prependCellMachine, prependCellMoveIteration, prependCellCfg,
    prependCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_value_nil (address memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .value address [] memory) =
      some (prependCellCfg .addressEnd address [] memory) := by
  simp [prependCellMachine, prependCellMoveIteration, prependCellCfg,
    prependCellStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_addressEnd (address value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .addressEnd address value memory) =
      some (prependCellCfg .address address value (.wordEnd :: memory)) := by
  simp [prependCellMachine, prependCellCfg, prependCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_address_cons (a : SparseSymbol)
    (address value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .address (a :: address) value memory) =
      some (prependCellCfg .address address value (a :: memory)) := by
  simp [prependCellMachine, prependCellMoveIteration, prependCellCfg,
    prependCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem prependCell_step_address_nil (value memory : List SparseSymbol) :
    prependCellMachine.step (prependCellCfg .address [] value memory) =
      some (prependCellCfg .done [] value memory) := by
  simp [prependCellMachine, prependCellMoveIteration, prependCellCfg,
    prependCellStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem prependCell_value_iterate (address value memory : List SparseSymbol) :
    ((fun o : Option prependCellMachine.Cfg => o.bind prependCellMachine.step)^[
      value.length])
      (some (prependCellCfg .value address value memory)) =
    some (prependCellCfg .value address [] (value.reverse ++ memory)) := by
  induction value generalizing memory with
  | nil => rfl
  | cons a value ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, prependCell_step_value_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem prependCell_address_iterate (address value memory : List SparseSymbol) :
    ((fun o : Option prependCellMachine.Cfg => o.bind prependCellMachine.step)^[
      address.length])
      (some (prependCellCfg .address address value memory)) =
    some (prependCellCfg .address [] value (address.reverse ++ memory)) := by
  induction address generalizing memory with
  | nil => rfl
  | cons a address ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, prependCell_step_address_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem prependCell_correct (address value memory : List SparseSymbol) :
    ((fun o : Option prependCellMachine.Cfg => o.bind prependCellMachine.step)^[
      address.length + value.length + 5])
      (some (prependCellCfg .cellEnd address value memory)) =
    some (prependCellCfg .done [] []
      (address.reverse ++
        (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory)))) := by
  let stepO := fun o : Option prependCellMachine.Cfg => o.bind prependCellMachine.step
  have chain {r s : ℕ} {x y z : Option prependCellMachine.Cfg}
      (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by
    rw [Function.iterate_add_apply, hr, hs]
  have h0 : (stepO^[1]) (some (prependCellCfg .cellEnd address value memory)) =
      some (prependCellCfg .valueEnd address value (.cellEnd :: memory)) := by
    simpa [stepO] using prependCell_step_cellEnd address value memory
  have h1 : (stepO^[1])
      (some (prependCellCfg .valueEnd address value (.cellEnd :: memory))) =
      some (prependCellCfg .value address value (.wordEnd :: .cellEnd :: memory)) := by
    simpa [stepO] using prependCell_step_valueEnd address value (.cellEnd :: memory)
  have h2 := prependCell_value_iterate address value (.wordEnd :: .cellEnd :: memory)
  have h3 : (stepO^[1])
      (some (prependCellCfg .value address []
        (value.reverse ++ .wordEnd :: .cellEnd :: memory))) =
      some (prependCellCfg .addressEnd address []
        (value.reverse ++ .wordEnd :: .cellEnd :: memory)) := by
    simpa [stepO] using prependCell_step_value_nil address
      (value.reverse ++ .wordEnd :: .cellEnd :: memory)
  have h4 : (stepO^[1])
      (some (prependCellCfg .addressEnd address []
        (value.reverse ++ .wordEnd :: .cellEnd :: memory))) =
      some (prependCellCfg .address address []
        (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory))) := by
    simpa [stepO, List.append_assoc] using prependCell_step_addressEnd address []
      (value.reverse ++ .wordEnd :: .cellEnd :: memory)
  have h5 := prependCell_address_iterate address []
    (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory))
  have h6 : (stepO^[1])
      (some (prependCellCfg .address [] []
        (address.reverse ++
          (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory))))) =
      some (prependCellCfg .done [] []
        (address.reverse ++
          (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory)))) := by
    simpa [stepO, List.append_assoc] using prependCell_step_address_nil []
      (address.reverse ++
        (.wordEnd :: value.reverse ++ (.wordEnd :: .cellEnd :: memory)))
  have hrun := chain (chain (chain (chain (chain (chain h0 h1) h2) h3) h4) h5) h6
  have hexp : 1 + (address.length + (1 + (1 + (value.length + (1 + 1))))) =
      address.length + value.length + 5 := by omega
  rw [hexp] at hrun
  simpa [stepO, List.append_assoc] using hrun

theorem prependCell_fixed_correct (w a v : ℕ) (memory : List SparseSymbol) :
    ((fun o : Option prependCellMachine.Cfg => o.bind prependCellMachine.step)^[
      2 * w + 5])
      (some (prependCellCfg .cellEnd
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit) memory)) =
    some (prependCellCfg .done [] [] (encodeSparseCell w (a, v) ++ memory)) := by
  have h := prependCell_correct
    ((fixedBits w a).reverse.map SparseSymbol.bit)
    ((fixedBits w v).reverse.map SparseSymbol.bit) memory
  simp only [List.length_map, List.length_reverse, fixedBits_length] at h
  have htime : w + w + 5 = 2 * w + 5 := by omega
  rw [htime] at h
  simpa [encodeSparseCell, encodeFixedWord, List.map_reverse,
    List.append_assoc] using h

end Lax51Proofs.RamToTM

import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMCellTransferMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure SymbolMoveControl where
  held : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

def symbolMoveIteration {K Λ : Type} [DecidableEq K]
    (source target : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ SymbolMoveControl :=
  .pop source (fun _ a => ⟨a⟩) <|
    .branch (fun s => s.held.isNone)
      (.goto fun _ => done)
      (.push target (fun s => s.held.getD (.bit false)) <|
        .load (fun _ => default) <| .goto fun _ => loop)

inductive SymbolMoveStack | source | target
  deriving DecidableEq, Fintype, Inhabited

inductive SymbolMoveLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def symbolMoveMachine : Turing.FinTM2 where
  K := SymbolMoveStack
  k₀ := .source
  k₁ := .target
  Γ _ := SparseSymbol
  Λ := SymbolMoveLabel
  main := .loop
  σ := SymbolMoveControl
  initialState := default
  m
    | .loop => symbolMoveIteration .source .target .loop .done
    | .done => .halt

def symbolMoveStacks (source target : List SparseSymbol) :
    SymbolMoveStack → List SparseSymbol
  | .source => source
  | .target => target

def symbolMoveCfg (source target : List SparseSymbol) : symbolMoveMachine.Cfg where
  l := some .loop
  var := default
  stk := symbolMoveStacks source target

def symbolMoveCfgState (state : SymbolMoveControl)
    (source target : List SparseSymbol) : symbolMoveMachine.Cfg where
  l := some .loop
  var := state
  stk := symbolMoveStacks source target

def symbolMoveDoneCfg (target : List SparseSymbol) : symbolMoveMachine.Cfg where
  l := some .done
  var := default
  stk := symbolMoveStacks [] target

@[simp] theorem symbolMove_step_state_nil (state : SymbolMoveControl)
    (target : List SparseSymbol) :
    symbolMoveMachine.step (symbolMoveCfgState state [] target) =
      some (symbolMoveDoneCfg target) := by
  change some (TM2.stepAux
    (symbolMoveIteration SymbolMoveStack.source SymbolMoveStack.target
      SymbolMoveLabel.loop SymbolMoveLabel.done)
    state (symbolMoveStacks [] target)) = _
  simp [symbolMoveIteration, symbolMoveDoneCfg, symbolMoveCfgState,
    symbolMoveStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem symbolMove_step_state_cons (state : SymbolMoveControl)
    (a : SparseSymbol) (source target : List SparseSymbol) :
    symbolMoveMachine.step (symbolMoveCfgState state (a :: source) target) =
      some (symbolMoveCfg source (a :: target)) := by
  change some (TM2.stepAux
    (symbolMoveIteration SymbolMoveStack.source SymbolMoveStack.target
      SymbolMoveLabel.loop SymbolMoveLabel.done)
    state (symbolMoveStacks (a :: source) target)) = _
  simp [symbolMoveIteration, symbolMoveCfgState, symbolMoveCfg,
    symbolMoveStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem symbolMove_step_nil (target : List SparseSymbol) :
    symbolMoveMachine.step (symbolMoveCfg [] target) =
      some (symbolMoveDoneCfg target) := by
  change some (TM2.stepAux
    (symbolMoveIteration SymbolMoveStack.source SymbolMoveStack.target
      SymbolMoveLabel.loop SymbolMoveLabel.done)
    default (symbolMoveStacks [] target)) = _
  simp [symbolMoveIteration, symbolMoveDoneCfg, symbolMoveStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem symbolMove_step_cons (a : SparseSymbol)
    (source target : List SparseSymbol) :
    symbolMoveMachine.step (symbolMoveCfg (a :: source) target) =
      some (symbolMoveCfg source (a :: target)) := by
  change some (TM2.stepAux
    (symbolMoveIteration SymbolMoveStack.source SymbolMoveStack.target
      SymbolMoveLabel.loop SymbolMoveLabel.done)
    default (symbolMoveStacks (a :: source) target)) = _
  simp [symbolMoveIteration, symbolMoveCfg, symbolMoveStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem symbolMove_iterate (source target : List SparseSymbol) :
    ((fun o : Option symbolMoveMachine.Cfg => o.bind symbolMoveMachine.step)^[source.length])
        (some (symbolMoveCfg source target)) =
      some (symbolMoveCfg [] (source.reverse ++ target)) := by
  induction source generalizing target with
  | nil => rfl
  | cons a source ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, symbolMove_step_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem symbolMove_reaches_done (source target : List SparseSymbol) :
    ((fun o : Option symbolMoveMachine.Cfg => o.bind symbolMoveMachine.step)^[source.length + 1])
        (some (symbolMoveCfg source target)) =
      some (symbolMoveDoneCfg (source.reverse ++ target)) := by
  rw [Nat.add_comm, Function.iterate_add_apply, symbolMove_iterate]
  simp only [Function.iterate_one, Option.bind_some, symbolMove_step_nil]

theorem symbolMove_reaches_done_from (state : SymbolMoveControl)
    (source target : List SparseSymbol) :
    ((fun o : Option symbolMoveMachine.Cfg => o.bind symbolMoveMachine.step)^[
      source.length + 1])
      (some (symbolMoveCfgState state source target)) =
      some (symbolMoveDoneCfg (source.reverse ++ target)) := by
  cases source with
  | nil => simpa using symbolMove_step_state_nil state target
  | cons a source =>
      rw [List.length_cons,
        show source.length + 1 + 1 = (source.length + 1) + 1 by omega,
        Function.iterate_succ_apply]
      simp only [Option.bind_some, symbolMove_step_state_cons]
      simpa [List.reverse_cons, List.append_assoc] using
        symbolMove_reaches_done source (a :: target)

theorem symbolMove_reverses_encoded_cell (w a v : ℕ)
    (target : List SparseSymbol) :
    ((fun o : Option symbolMoveMachine.Cfg => o.bind symbolMoveMachine.step)^[
      (encodeSparseCell w (a, v)).length + 1])
        (some (symbolMoveCfg (encodeSparseCell w (a, v)).reverse target)) =
      some (symbolMoveDoneCfg (encodeSparseCell w (a, v) ++ target)) := by
  simpa using symbolMove_reaches_done (encodeSparseCell w (a, v)).reverse target

end Lax51Proofs.RamToTM

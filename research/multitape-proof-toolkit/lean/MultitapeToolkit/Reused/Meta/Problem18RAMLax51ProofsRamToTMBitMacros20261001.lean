import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMFixedWord20261001
import Mathlib.Tactic.DeriveFintype

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-- Finite local control used by the ripple-carry TM2 statement. -/
structure AddControl where
  carry : Bool
  left : Option Bool
  right : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def AddControl.setLeft (s : AddControl) (a : Option Bool) : AddControl :=
  { s with left := a }

def AddControl.setRight (s : AddControl) (b : Option Bool) : AddControl :=
  { s with right := b }

def AddControl.sumBit (s : AddControl) : Bool :=
  (fullAdder (s.left.getD false) (s.right.getD false) s.carry).1

def AddControl.advance (s : AddControl) : AddControl :=
  { carry := (fullAdder (s.left.getD false) (s.right.getD false) s.carry).2,
    left := none, right := none }

/-- One TM2 statement implementing a complete iteration of ripple-carry
addition. The two operands are popped from their stacks and the result bit is
pushed onto a third (therefore reversed) stack. Empty left input exits to
`done`. Equal operand lengths are an invariant of callers. -/
def addIteration {K Λ : Type} [DecidableEq K]
    (left right result : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ AddControl :=
  .pop left AddControl.setLeft <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right AddControl.setRight <|
        .push result AddControl.sumBit <|
          .load AddControl.advance <|
            .goto fun _ => loop)

@[simp] theorem stepAux_addIteration_nil {K Λ : Type} [DecidableEq K]
    (left right result : K) (loop done : Λ) (s : AddControl)
    (S : K → List Bool) (hleft : S left = []) :
    TM2.stepAux (addIteration left right result loop done) s S =
      ⟨some done, { s with left := none }, S⟩ := by
  simp [addIteration, AddControl.setLeft, hleft]

theorem stepAux_addIteration_cons {K Λ : Type} [DecidableEq K]
    (left right result : K) (loop done : Λ) (s : AddControl)
    (S : K → List Bool) (a b : Bool) (as bs : List Bool)
    (hleft : S left = a :: as) (hright : S right = b :: bs)
    (hlr : left ≠ right) (hlres : left ≠ result) (hrres : right ≠ result) :
    TM2.stepAux (addIteration left right result loop done) s S =
      ⟨some loop,
        { carry := (fullAdder a b s.carry).2, left := none, right := none },
        Function.update (Function.update (Function.update S left as) right bs)
          result ((fullAdder a b s.carry).1 :: S result)⟩ := by
  have hright' : Function.update S left as right = b :: bs := by
    rw [Function.update_of_ne hlr.symm, hright]
  have hresult' : Function.update (Function.update S left as) right bs result = S result := by
    rw [Function.update_of_ne hrres.symm, Function.update_of_ne hlres.symm]
  simp [addIteration, AddControl.setLeft, AddControl.setRight,
    AddControl.sumBit, AddControl.advance, hleft, hright', hresult']

/-! A concrete finite TM2 component and its whole-loop correctness theorem.
This component is later embedded into the RAM interpreter's larger control
graph. -/

inductive AddStack | left | right | result
  deriving DecidableEq, Fintype, Inhabited

inductive AddLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def addMachine : Turing.FinTM2 where
  K := AddStack
  k₀ := .left
  k₁ := .result
  Γ _ := Bool
  Λ := AddLabel
  main := .loop
  σ := AddControl
  initialState := default
  m
    | .loop => addIteration .left .right .result .loop .done
    | .done => .halt

def addStackFamily (left right result : List Bool) : AddStack → List Bool
  | .left => left
  | .right => right
  | .result => result

def addCfg (carry : Bool) (left right result : List Bool) : addMachine.Cfg where
  l := some .loop
  var := ⟨carry, none, none⟩
  stk := addStackFamily left right result

def addDoneCfg (carry : Bool) (right result : List Bool) : addMachine.Cfg where
  l := some AddLabel.done
  var := ⟨carry, none, none⟩
  stk := addStackFamily [] right result

def addCarryOut : List Bool → List Bool → Bool → Bool
  | a :: as, b :: bs, carry => (addCarryOut as bs (fullAdder a b carry).2)
  | _, _, carry => carry

@[simp] theorem addMachine_step_nil (carry : Bool) (right result : List Bool) :
    addMachine.step (addCfg carry [] right result) = some
      { l := some .done, var := ⟨carry, none, none⟩,
        stk := addStackFamily [] right result } := by
  change some (TM2.stepAux
      (addIteration AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
      ⟨carry, none, none⟩ (addStackFamily [] right result)) = _
  rw [stepAux_addIteration_nil]
  · rfl

@[simp] theorem addMachine_step_cons (carry a b : Bool)
    (as bs result : List Bool) :
    addMachine.step (addCfg carry (a :: as) (b :: bs) result) =
      some (addCfg (fullAdder a b carry).2 as bs
        ((fullAdder a b carry).1 :: result)) := by
  change some (TM2.stepAux
      (addIteration AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
      ⟨carry, none, none⟩ (addStackFamily (a :: as) (b :: bs) result)) = _
  have h := stepAux_addIteration_cons
    (left := AddStack.left) (right := AddStack.right) (result := AddStack.result)
    (loop := AddLabel.loop) (done := AddLabel.done)
    (s := (⟨carry, none, none⟩ : AddControl))
    (S := addStackFamily (a :: as) (b :: bs) result)
    (a := a) (b := b) (as := as) (bs := bs) rfl rfl
    (by decide) (by decide) (by decide)
  rw [h]
  congr 2
  funext k
  cases k <;> rfl

theorem addMachine_iterate (carry : Bool) (as bs result : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option addMachine.Cfg => o.bind addMachine.step)^[as.length])
        (some (addCfg carry as bs result)) =
      some (addCfg (addCarryOut as bs carry) [] []
        ((addBits as bs carry).reverse ++ result)) := by
  induction as generalizing bs carry result with
  | nil =>
      cases bs with
      | nil => rfl
      | cons b bs => simp at hlen
  | cons a as ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
        simp at hlen
        rw [List.length_cons, Function.iterate_succ_apply]
        simp only [Option.bind_some, addMachine_step_cons]
        rw [ih (fullAdder a b carry).2 bs
          ((fullAdder a b carry).1 :: result) hlen]
        simp [addBits, addCarryOut, List.reverse_cons, List.append_assoc]

theorem addMachine_reaches_done (carry : Bool) (as bs result : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option addMachine.Cfg => o.bind addMachine.step)^[as.length + 1])
        (some (addCfg carry as bs result)) =
      some (addDoneCfg (addCarryOut as bs carry) []
        ((addBits as bs carry).reverse ++ result)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    addMachine_iterate carry as bs result hlen]
  simp only [Function.iterate_one, Option.bind_some]
  rw [addMachine_step_nil]
  rfl

/-! Stack reversal/move macro. -/

structure MoveControl where
  held : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def moveIteration {K Λ : Type} [DecidableEq K]
    (source target : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ MoveControl :=
  .pop source (fun _ b => ⟨b⟩) <|
    .branch (fun s => s.held.isNone)
      (.goto fun _ => done)
      (.push target (fun s => s.held.getD false) <|
        .load (fun _ => ⟨none⟩) <|
          .goto fun _ => loop)

inductive MoveStack | source | target
  deriving DecidableEq, Fintype, Inhabited

inductive MoveLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def moveMachine : Turing.FinTM2 where
  K := MoveStack
  k₀ := .source
  k₁ := .target
  Γ _ := Bool
  Λ := MoveLabel
  main := .loop
  σ := MoveControl
  initialState := default
  m
    | .loop => moveIteration .source .target .loop .done
    | .done => .halt

def moveStacks (source target : List Bool) : MoveStack → List Bool
  | .source => source
  | .target => target

def moveCfg (source target : List Bool) : moveMachine.Cfg where
  l := some .loop
  var := ⟨none⟩
  stk := moveStacks source target

def moveDoneCfg (target : List Bool) : moveMachine.Cfg where
  l := some .done
  var := ⟨none⟩
  stk := moveStacks [] target

@[simp] theorem moveMachine_step_nil (target : List Bool) :
    moveMachine.step (moveCfg [] target) = some (moveDoneCfg target) := by
  change some (TM2.stepAux
    (moveIteration MoveStack.source MoveStack.target MoveLabel.loop MoveLabel.done)
    ⟨none⟩ (moveStacks [] target)) = _
  simp [moveIteration, moveDoneCfg, moveStacks]

@[simp] theorem moveMachine_step_cons (a : Bool) (as target : List Bool) :
    moveMachine.step (moveCfg (a :: as) target) = some (moveCfg as (a :: target)) := by
  change some (TM2.stepAux
    (moveIteration MoveStack.source MoveStack.target MoveLabel.loop MoveLabel.done)
    ⟨none⟩ (moveStacks (a :: as) target)) = _
  simp [moveIteration, moveCfg, moveStacks, Function.update]
  congr 2
  funext k
  cases k <;> rfl

theorem moveMachine_iterate (source target : List Bool) :
    ((fun o : Option moveMachine.Cfg => o.bind moveMachine.step)^[source.length])
      (some (moveCfg source target)) = some (moveCfg [] (source.reverse ++ target)) := by
  induction source generalizing target with
  | nil => rfl
  | cons a as ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, moveMachine_step_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem moveMachine_reaches_done (source target : List Bool) :
    ((fun o : Option moveMachine.Cfg => o.bind moveMachine.step)^[source.length + 1])
      (some (moveCfg source target)) = some (moveDoneCfg (source.reverse ++ target)) := by
  rw [Nat.add_comm, Function.iterate_add_apply, moveMachine_iterate]
  simp only [Function.iterate_one, Option.bind_some, moveMachine_step_nil]

/-! Pointwise binary Boolean-operation macro (`and`, `or`, and `xor`). -/

structure ZipControl where
  left : Option Bool
  right : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def zipIteration {K Λ : Type} [DecidableEq K] (f : Bool → Bool → Bool)
    (left right result : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ ZipControl :=
  .pop left (fun s a => { s with left := a }) <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right (fun s b => { s with right := b }) <|
        .push result (fun s => f (s.left.getD false) (s.right.getD false)) <|
          .load (fun _ => ⟨none, none⟩) <|
            .goto fun _ => loop)

def zipMachine (f : Bool → Bool → Bool) : Turing.FinTM2 where
  K := AddStack
  k₀ := .left
  k₁ := .result
  Γ _ := Bool
  Λ := AddLabel
  main := .loop
  σ := ZipControl
  initialState := default
  m
    | .loop => zipIteration f .left .right .result .loop .done
    | .done => .halt

def zipCfg (f : Bool → Bool → Bool) (left right result : List Bool) :
    (zipMachine f).Cfg where
  l := some .loop
  var := ⟨none, none⟩
  stk := addStackFamily left right result

def zipPartialDoneCfg (f : Bool → Bool → Bool) (right result : List Bool) :
    (zipMachine f).Cfg where
  l := some .done
  var := ⟨none, none⟩
  stk := addStackFamily [] right result

def zipDoneCfg (f : Bool → Bool → Bool) (result : List Bool) :
    (zipMachine f).Cfg := zipPartialDoneCfg f [] result

@[simp] theorem zipMachine_step_nil (f : Bool → Bool → Bool)
    (right result : List Bool) :
    (zipMachine f).step (zipCfg f [] right result) =
      some (zipPartialDoneCfg f right result) := by
  change some (TM2.stepAux
    (zipIteration f AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
    ⟨none, none⟩ (addStackFamily [] right result)) = _
  simp [zipIteration, zipPartialDoneCfg, addStackFamily]

@[simp] theorem zipMachine_step_cons (f : Bool → Bool → Bool) (a b : Bool)
    (as bs result : List Bool) :
    (zipMachine f).step (zipCfg f (a :: as) (b :: bs) result) =
      some (zipCfg f as bs (f a b :: result)) := by
  change some (TM2.stepAux
    (zipIteration f AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
    ⟨none, none⟩ (addStackFamily (a :: as) (b :: bs) result)) = _
  simp [zipIteration, zipCfg, addStackFamily, Function.update]
  congr 2
  funext k
  cases k <;> rfl

theorem zipMachine_iterate (f : Bool → Bool → Bool) (as bs result : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option (zipMachine f).Cfg => o.bind (zipMachine f).step)^[as.length])
      (some (zipCfg f as bs result)) =
      some (zipCfg f [] [] ((zipBits f as bs).reverse ++ result)) := by
  induction as generalizing bs result with
  | nil =>
      cases bs with
      | nil => rfl
      | cons b bs => simp at hlen
  | cons a as ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
        simp at hlen
        rw [List.length_cons, Function.iterate_succ_apply]
        simp only [Option.bind_some, zipMachine_step_cons]
        rw [ih bs (f a b :: result) hlen]
        simp [zipBits, List.reverse_cons, List.append_assoc]

theorem zipMachine_reaches_done (f : Bool → Bool → Bool)
    (as bs result : List Bool) (hlen : as.length = bs.length) :
    ((fun o : Option (zipMachine f).Cfg => o.bind (zipMachine f).step)^[as.length + 1])
      (some (zipCfg f as bs result)) =
      some (zipDoneCfg f ((zipBits f as bs).reverse ++ result)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    zipMachine_iterate f as bs result hlen]
  simp only [Function.iterate_one, Option.bind_some, zipMachine_step_nil]
  rfl

end Lax51Proofs.RamToTM

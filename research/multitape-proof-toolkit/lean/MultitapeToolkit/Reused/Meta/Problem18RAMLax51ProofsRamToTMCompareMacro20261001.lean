import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMBitMacros20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure CompareControl where
  less : Bool
  left : Option Bool
  right : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def CompareControl.advance (s : CompareControl) : CompareControl :=
  { less := if s.left = s.right then s.less
      else (!(s.left.getD false) && s.right.getD false),
    left := none, right := none }

def compareIteration {K Λ : Type} [DecidableEq K]
    (left right leftBackup rightBackup : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ CompareControl :=
  .pop left (fun s a => { s with left := a }) <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right (fun s b => { s with right := b }) <|
        .push leftBackup (fun s => s.left.getD false) <|
          .push rightBackup (fun s => s.right.getD false) <|
            .load CompareControl.advance <|
              .goto fun _ => loop)

inductive CompareStack | left | right | leftBackup | rightBackup
  deriving DecidableEq, Fintype, Inhabited

inductive CompareLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def compareMachine : Turing.FinTM2 where
  K := CompareStack
  k₀ := .left
  k₁ := .right
  Γ _ := Bool
  Λ := CompareLabel
  main := .loop
  σ := CompareControl
  initialState := default
  m
    | .loop => compareIteration .left .right .leftBackup .rightBackup .loop .done
    | .done => .halt

def compareStacks (left right leftBackup rightBackup : List Bool) :
    CompareStack → List Bool
  | .left => left
  | .right => right
  | .leftBackup => leftBackup
  | .rightBackup => rightBackup

def compareCfg (less : Bool) (left right leftBackup rightBackup : List Bool) :
    compareMachine.Cfg where
  l := some .loop
  var := ⟨less, none, none⟩
  stk := compareStacks left right leftBackup rightBackup

def compareDoneCfg (less : Bool) (leftBackup rightBackup : List Bool) :
    compareMachine.Cfg where
  l := some .done
  var := ⟨less, none, none⟩
  stk := compareStacks [] [] leftBackup rightBackup

@[simp] theorem compareMachine_step_nil (less : Bool) (right lb rb : List Bool) :
    compareMachine.step (compareCfg less [] right lb rb) = some
      { l := some CompareLabel.done, var := ⟨less, none, none⟩,
        stk := compareStacks [] right lb rb } := by
  change some (TM2.stepAux
    (compareIteration CompareStack.left CompareStack.right CompareStack.leftBackup
      CompareStack.rightBackup CompareLabel.loop CompareLabel.done)
    ⟨less, none, none⟩ (compareStacks [] right lb rb)) = _
  simp [compareIteration, compareStacks]

@[simp] theorem compareMachine_step_cons (less a b : Bool)
    (as bs lb rb : List Bool) :
    compareMachine.step (compareCfg less (a :: as) (b :: bs) lb rb) =
      some (compareCfg (if a = b then less else (!a && b))
        as bs (a :: lb) (b :: rb)) := by
  change some (TM2.stepAux
    (compareIteration CompareStack.left CompareStack.right CompareStack.leftBackup
      CompareStack.rightBackup CompareLabel.loop CompareLabel.done)
    ⟨less, none, none⟩ (compareStacks (a :: as) (b :: bs) lb rb)) = _
  simp [compareIteration, CompareControl.advance, compareCfg, compareStacks,
    Function.update]
  congr 2
  funext k
  cases k <;> rfl

theorem compareMachine_iterate (less : Bool) (as bs lb rb : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option compareMachine.Cfg => o.bind compareMachine.step)^[as.length])
      (some (compareCfg less as bs lb rb)) =
      some (compareCfg (lessBits as bs less) [] []
        (as.reverse ++ lb) (bs.reverse ++ rb)) := by
  induction as generalizing bs less lb rb with
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
        simp only [Option.bind_some, compareMachine_step_cons]
        rw [ih (if a = b then less else (!a && b)) bs (a :: lb) (b :: rb) hlen]
        simp [lessBits, List.reverse_cons, List.append_assoc]

theorem compareMachine_reaches_done (less : Bool) (as bs lb rb : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option compareMachine.Cfg => o.bind compareMachine.step)^[as.length + 1])
      (some (compareCfg less as bs lb rb)) =
      some (compareDoneCfg (lessBits as bs less)
        (as.reverse ++ lb) (bs.reverse ++ rb)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    compareMachine_iterate less as bs lb rb hlen]
  simp only [Function.iterate_one, Option.bind_some, compareMachine_step_nil]
  rfl

theorem compareMachine_fixed_correct (w a b : ℕ)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) :
    ((fun o : Option compareMachine.Cfg => o.bind compareMachine.step)^[w + 1])
      (some (compareCfg false (fixedBits w a) (fixedBits w b) [] [])) =
      some (compareDoneCfg (decide (a < b))
        (fixedBits w a).reverse (fixedBits w b).reverse) := by
  have hrun := compareMachine_reaches_done false (fixedBits w a) (fixedBits w b) [] []
    (by simp)
  simp only [fixedBits_length] at hrun
  rw [hrun, lessBits_fixed w a b ha hb]
  simp

end Lax51Proofs.RamToTM

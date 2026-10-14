import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMCompareMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure SubControl where
  borrow : Bool
  left : Option Bool
  right : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def SubControl.differenceBit (s : SubControl) : Bool :=
  (fullSubtractor (s.left.getD false) (s.right.getD false) s.borrow).1

def SubControl.advance (s : SubControl) : SubControl :=
  { borrow := (fullSubtractor (s.left.getD false) (s.right.getD false) s.borrow).2,
    left := none, right := none }

def subIteration {K Λ : Type} [DecidableEq K]
    (left right result : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ SubControl :=
  .pop left (fun s a => { s with left := a }) <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right (fun s b => { s with right := b }) <|
        .push result SubControl.differenceBit <|
          .load SubControl.advance <|
            .goto fun _ => loop)

def subMachine : Turing.FinTM2 where
  K := AddStack
  k₀ := .left
  k₁ := .result
  Γ _ := Bool
  Λ := AddLabel
  main := .loop
  σ := SubControl
  initialState := default
  m
    | .loop => subIteration .left .right .result .loop .done
    | .done => .halt

def subCfg (borrow : Bool) (left right result : List Bool) : subMachine.Cfg where
  l := some .loop
  var := ⟨borrow, none, none⟩
  stk := addStackFamily left right result

def subPartialDoneCfg (borrow : Bool) (right result : List Bool) : subMachine.Cfg where
  l := some .done
  var := ⟨borrow, none, none⟩
  stk := addStackFamily [] right result

def subDoneCfg (borrow : Bool) (result : List Bool) : subMachine.Cfg :=
  subPartialDoneCfg borrow [] result

@[simp] theorem subMachine_step_nil (borrow : Bool) (right result : List Bool) :
    subMachine.step (subCfg borrow [] right result) =
      some (subPartialDoneCfg borrow right result) := by
  change some (TM2.stepAux
    (subIteration AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
    ⟨borrow, none, none⟩ (addStackFamily [] right result)) = _
  simp [subIteration, subPartialDoneCfg, addStackFamily]

@[simp] theorem subMachine_step_cons (borrow a b : Bool)
    (as bs result : List Bool) :
    subMachine.step (subCfg borrow (a :: as) (b :: bs) result) =
      some (subCfg (fullSubtractor a b borrow).2 as bs
        ((fullSubtractor a b borrow).1 :: result)) := by
  change some (TM2.stepAux
    (subIteration AddStack.left AddStack.right AddStack.result AddLabel.loop AddLabel.done)
    ⟨borrow, none, none⟩ (addStackFamily (a :: as) (b :: bs) result)) = _
  simp [subIteration, SubControl.differenceBit, SubControl.advance,
    subCfg, addStackFamily, Function.update]
  congr 2
  funext k
  cases k <;> rfl

theorem subMachine_iterate (borrow : Bool) (as bs result : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option subMachine.Cfg => o.bind subMachine.step)^[as.length])
      (some (subCfg borrow as bs result)) =
      some (subCfg (subBorrowOut as bs borrow) [] []
        ((subBits as bs borrow).reverse ++ result)) := by
  induction as generalizing bs borrow result with
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
        simp only [Option.bind_some, subMachine_step_cons]
        rw [ih (fullSubtractor a b borrow).2 bs
          ((fullSubtractor a b borrow).1 :: result) hlen]
        simp [subBits, subBorrowOut, List.reverse_cons, List.append_assoc]

theorem subMachine_reaches_done (borrow : Bool) (as bs result : List Bool)
    (hlen : as.length = bs.length) :
    ((fun o : Option subMachine.Cfg => o.bind subMachine.step)^[as.length + 1])
      (some (subCfg borrow as bs result)) =
      some (subDoneCfg (subBorrowOut as bs borrow)
        ((subBits as bs borrow).reverse ++ result)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    subMachine_iterate borrow as bs result hlen]
  simp only [Function.iterate_one, Option.bind_some, subMachine_step_nil]
  rfl

theorem subMachine_fixed_correct (w : ℕ) {a b : ℕ}
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) (hba : b ≤ a) :
    ((fun o : Option subMachine.Cfg => o.bind subMachine.step)^[w + 1])
      (some (subCfg false (fixedBits w a) (fixedBits w b) [])) =
      some (subDoneCfg false (fixedBits w (a - b)).reverse) := by
  have hrun := subMachine_reaches_done false (fixedBits w a) (fixedBits w b) []
    (by simp)
  simp only [fixedBits_length] at hrun
  rw [hrun, subBorrowOut_fixed_false_of_le w ha hb hba,
    ← fixedBits_sub_of_le w hba]
  simp

end Lax51Proofs.RamToTM

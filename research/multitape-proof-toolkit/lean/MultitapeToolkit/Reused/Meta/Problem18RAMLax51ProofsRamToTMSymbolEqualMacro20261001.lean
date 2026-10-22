import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseInvariant20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

def symbolsEqual : List SparseSymbol → List SparseSymbol → Bool → Bool
  | a :: as, b :: bs, equal => symbolsEqual as bs (equal && decide (a = b))
  | _, _, equal => equal

structure SymbolEqualControl where
  equal : Bool
  left : Option SparseSymbol
  right : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

inductive SymbolEqualStack | left | right | leftBackup | rightBackup
  deriving DecidableEq, Fintype, Inhabited

inductive SymbolEqualLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def SymbolEqualControl.advance (s : SymbolEqualControl) : SymbolEqualControl :=
  { equal := s.equal && decide (s.left = s.right), left := none, right := none }

def symbolEqualIteration {K Λ : Type} [DecidableEq K]
    (left right leftBackup rightBackup : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ SymbolEqualControl :=
  .pop left (fun s a => { s with left := a }) <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right (fun s b => { s with right := b }) <|
        .push leftBackup (fun s => s.left.getD (.bit false)) <|
          .push rightBackup (fun s => s.right.getD (.bit false)) <|
            .load SymbolEqualControl.advance <|
              .goto fun _ => loop)

def symbolEqualMachine : Turing.FinTM2 where
  K := SymbolEqualStack
  k₀ := .left
  k₁ := .right
  Γ _ := SparseSymbol
  Λ := SymbolEqualLabel
  main := .loop
  σ := SymbolEqualControl
  initialState := ⟨true, none, none⟩
  m
    | .loop => symbolEqualIteration .left .right .leftBackup .rightBackup .loop .done
    | .done => .halt

def symbolEqualStacks (left right leftBackup rightBackup : List SparseSymbol) :
    SymbolEqualStack → List SparseSymbol
  | .left => left
  | .right => right
  | .leftBackup => leftBackup
  | .rightBackup => rightBackup

def symbolEqualCfg (equal : Bool) (left right leftBackup rightBackup : List SparseSymbol) :
    symbolEqualMachine.Cfg where
  l := some .loop
  var := ⟨equal, none, none⟩
  stk := symbolEqualStacks left right leftBackup rightBackup

def symbolEqualDoneCfg (equal : Bool)
    (leftBackup rightBackup : List SparseSymbol) : symbolEqualMachine.Cfg where
  l := some .done
  var := ⟨equal, none, none⟩
  stk := symbolEqualStacks [] [] leftBackup rightBackup

def symbolEqualPartialDoneCfg (equal : Bool) (right leftBackup rightBackup :
    List SparseSymbol) : symbolEqualMachine.Cfg where
  l := some .done
  var := ⟨equal, none, none⟩
  stk := symbolEqualStacks [] right leftBackup rightBackup

@[simp] theorem symbolEqual_step_nil (equal : Bool) (right lb rb : List SparseSymbol) :
    symbolEqualMachine.step (symbolEqualCfg equal [] right lb rb) =
      some (symbolEqualPartialDoneCfg equal right lb rb) := by
  change some (TM2.stepAux
    (symbolEqualIteration SymbolEqualStack.left SymbolEqualStack.right
      SymbolEqualStack.leftBackup SymbolEqualStack.rightBackup
      SymbolEqualLabel.loop SymbolEqualLabel.done)
    ⟨equal, none, none⟩ (symbolEqualStacks [] right lb rb)) = _
  simp [symbolEqualIteration, symbolEqualPartialDoneCfg, symbolEqualStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem symbolEqual_step_cons (equal : Bool) (a b : SparseSymbol)
    (as bs lb rb : List SparseSymbol) :
    symbolEqualMachine.step (symbolEqualCfg equal (a :: as) (b :: bs) lb rb) =
      some (symbolEqualCfg (equal && decide (a = b)) as bs (a :: lb) (b :: rb)) := by
  change some (TM2.stepAux
    (symbolEqualIteration SymbolEqualStack.left SymbolEqualStack.right
      SymbolEqualStack.leftBackup SymbolEqualStack.rightBackup
      SymbolEqualLabel.loop SymbolEqualLabel.done)
    ⟨equal, none, none⟩ (symbolEqualStacks (a :: as) (b :: bs) lb rb)) = _
  simp [symbolEqualIteration, SymbolEqualControl.advance, symbolEqualCfg,
    symbolEqualStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem symbolEqual_iterate (equal : Bool) (as bs lb rb : List SparseSymbol)
    (hlen : as.length = bs.length) :
    ((fun o : Option symbolEqualMachine.Cfg => o.bind symbolEqualMachine.step)^[as.length])
        (some (symbolEqualCfg equal as bs lb rb)) =
      some (symbolEqualCfg (symbolsEqual as bs equal) [] []
        (as.reverse ++ lb) (bs.reverse ++ rb)) := by
  induction as generalizing bs equal lb rb with
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
        simp only [Option.bind_some, symbolEqual_step_cons]
        rw [ih (equal && decide (a = b)) bs (a :: lb) (b :: rb) hlen]
        simp [symbolsEqual, List.reverse_cons, List.append_assoc]

theorem symbolEqual_reaches_done (equal : Bool) (as bs lb rb : List SparseSymbol)
    (hlen : as.length = bs.length) :
    ((fun o : Option symbolEqualMachine.Cfg => o.bind symbolEqualMachine.step)^[as.length + 1])
        (some (symbolEqualCfg equal as bs lb rb)) =
      some (symbolEqualDoneCfg (symbolsEqual as bs equal)
        (as.reverse ++ lb) (bs.reverse ++ rb)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    symbolEqual_iterate equal as bs lb rb hlen]
  simp only [Function.iterate_one, Option.bind_some, symbolEqual_step_nil]
  rfl

@[simp] theorem symbolsEqual_false (as bs : List SparseSymbol) :
    symbolsEqual as bs false = false := by
  induction as generalizing bs with
  | nil => simp [symbolsEqual]
  | cons a as ih =>
      cases bs <;> simp [symbolsEqual, ih]

theorem symbolsEqual_true_of_length (as bs : List SparseSymbol)
    (hlen : as.length = bs.length) : symbolsEqual as bs true = decide (as = bs) := by
  induction as generalizing bs with
  | nil => cases bs <;> simp_all [symbolsEqual]
  | cons a as ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
        simp at hlen
        by_cases hab : a = b
        · subst b
          simp [symbolsEqual, ih bs hlen]
        · simp [symbolsEqual, hab]

theorem encodedFixedBits_injective_of_fit {w a b : ℕ}
    (ha : a < 2 ^ w) (hb : b < 2 ^ w)
    (h : (fixedBits w a).reverse.map SparseSymbol.bit =
      (fixedBits w b).reverse.map SparseSymbol.bit) : a = b := by
  have hbits : fixedBits w a = fixedBits w b := by
    have hm : (fixedBits w a).map SparseSymbol.bit =
        (fixedBits w b).map SparseSymbol.bit := by
      simpa using congrArg List.reverse h
    have hv := congrArg (List.map SparseSymbol.bitValue) hm
    have hfun : SparseSymbol.bitValue ∘ SparseSymbol.bit = id := by
      funext bit
      cases bit <;> rfl
    simpa only [List.map_map, hfun, List.map_id] using hv
  have := congrArg bitsValue hbits
  simpa [bitsValue_fixedBits_of_lt ha, bitsValue_fixedBits_of_lt hb] using this

theorem symbolEqual_fixed_correct (w a b : ℕ)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) :
    ((fun o : Option symbolEqualMachine.Cfg => o.bind symbolEqualMachine.step)^[w + 1])
        (some (symbolEqualCfg true
          ((fixedBits w a).reverse.map SparseSymbol.bit)
          ((fixedBits w b).reverse.map SparseSymbol.bit) [] [])) =
      some (symbolEqualDoneCfg (decide (a = b))
        ((fixedBits w a).map SparseSymbol.bit)
        ((fixedBits w b).map SparseSymbol.bit)) := by
  have hrun := symbolEqual_reaches_done true
    ((fixedBits w a).reverse.map SparseSymbol.bit)
    ((fixedBits w b).reverse.map SparseSymbol.bit) [] [] (by simp)
  simp only [List.length_map, List.length_reverse, fixedBits_length] at hrun
  rw [hrun, symbolsEqual_true_of_length _ _ (by simp)]
  have heq :
      decide ((fixedBits w a).reverse.map SparseSymbol.bit =
        (fixedBits w b).reverse.map SparseSymbol.bit) = decide (a = b) := by
    by_cases hab : a = b
    · subst b
      simp
    · have hencoded : ¬((fixedBits w a).reverse.map SparseSymbol.bit =
          (fixedBits w b).reverse.map SparseSymbol.bit) := by
        intro h
        exact hab (encodedFixedBits_injective_of_fit ha hb h)
      have hplain : ¬((fixedBits w a).map SparseSymbol.bit =
          (fixedBits w b).map SparseSymbol.bit) := by
        intro h
        apply hencoded
        simpa using congrArg List.reverse h
      simp [hab, hencoded, hplain]
  rw [heq]
  simp

end Lax51Proofs.RamToTM

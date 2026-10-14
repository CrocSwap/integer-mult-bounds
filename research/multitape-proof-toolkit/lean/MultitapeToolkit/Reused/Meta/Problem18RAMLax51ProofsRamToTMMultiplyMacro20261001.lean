import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMAlphabetEmbedding20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-! A width-uniform schoolbook multiplier.  The outer loop consumes the
multiplier least-significant bit first.  A true bit performs one ripple add;
every round shifts the multiplicand left once. -/

structure MulControl where
  selected : Option Bool
  carry : Bool
  left : Option Bool
  right : Option Bool
  held : Option Bool
  deriving DecidableEq, Fintype, Inhabited

def MulControl.sumBit (s : MulControl) : Bool :=
  (fullAdder (s.left.getD false) (s.right.getD false) s.carry).1

def MulControl.addAdvance (s : MulControl) : MulControl :=
  { s with
    carry := (fullAdder (s.left.getD false) (s.right.getD false) s.carry).2,
    left := none, right := none }

def MulControl.clearHeld (s : MulControl) : MulControl := { s with held := none }

inductive MulStack
  | multiplier | multiplicand | accumulator | multiplicandBackup | sumReverse | shiftTemp
  deriving DecidableEq, Fintype, Inhabited

inductive MulLabel
  | outer | select | add | restoreMultiplicand | restoreSum
  | shiftFirst | shiftDiscard | shiftSecond | shiftPrepend | done
  deriving DecidableEq, Fintype, Inhabited

def mulMoveIteration {K Λ : Type} [DecidableEq K]
    (source target : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => Bool) Λ MulControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held.isNone)
      (.load MulControl.clearHeld <| .goto fun _ => done)
      (.push target (fun s => s.held.getD false) <|
        .load MulControl.clearHeld <| .goto fun _ => loop)

def mulMachine : Turing.FinTM2 where
  K := MulStack
  k₀ := .multiplicand
  k₁ := .accumulator
  Γ _ := Bool
  Λ := MulLabel
  main := .outer
  σ := MulControl
  initialState := default
  m
    | .outer =>
        .pop .multiplier (fun s a => { s with selected := a }) <|
          .branch (fun s => s.selected.isNone)
            (.goto fun _ => .done) (.goto fun _ => .select)
    | .select => .branch (fun s => s.selected.getD false)
        (.load (fun s => { s with carry := false, left := none, right := none }) <|
          .goto fun _ => .add)
        (.goto fun _ => .shiftFirst)
    | .add =>
        .pop .multiplicand (fun s a => { s with left := a }) <|
          .branch (fun s => s.left.isNone)
            (.goto fun _ => .restoreMultiplicand)
            (.pop .accumulator (fun s b => { s with right := b }) <|
              .push .multiplicandBackup (fun s => s.left.getD false) <|
                .push .sumReverse MulControl.sumBit <|
                  .load MulControl.addAdvance <| .goto fun _ => .add)
    | .restoreMultiplicand => mulMoveIteration .multiplicandBackup .multiplicand
        .restoreMultiplicand .restoreSum
    | .restoreSum => mulMoveIteration .sumReverse .accumulator
        .restoreSum .shiftFirst
    | .shiftFirst => mulMoveIteration .multiplicand .shiftTemp
        .shiftFirst .shiftDiscard
    | .shiftDiscard =>
        .pop .shiftTemp (fun s _ => MulControl.clearHeld s) <|
          .goto fun _ => .shiftSecond
    | .shiftSecond => mulMoveIteration .shiftTemp .multiplicand
        .shiftSecond .shiftPrepend
    | .shiftPrepend => .push .multiplicand (fun _ => false) <|
        .load (fun _ => default) <| .goto fun _ => .outer
    | .done => .halt

def mulStacks (multiplier multiplicand accumulator multiplicandBackup sumReverse shiftTemp :
    List Bool) : MulStack → List Bool
  | .multiplier => multiplier
  | .multiplicand => multiplicand
  | .accumulator => accumulator
  | .multiplicandBackup => multiplicandBackup
  | .sumReverse => sumReverse
  | .shiftTemp => shiftTemp

def mulCfg (label : MulLabel) (selected carry : Bool)
    (multiplier multiplicand accumulator multiplicandBackup sumReverse shiftTemp :
      List Bool) : mulMachine.Cfg where
  l := some label
  var := ⟨some selected, carry, none, none, none⟩
  stk := mulStacks multiplier multiplicand accumulator multiplicandBackup sumReverse shiftTemp

def mulOuterCfg (multiplier multiplicand accumulator : List Bool) : mulMachine.Cfg where
  l := some .outer
  var := default
  stk := mulStacks multiplier multiplicand accumulator [] [] []

def mulDoneCfg (multiplicand accumulator : List Bool) : mulMachine.Cfg where
  l := some .done
  var := default
  stk := mulStacks [] multiplicand accumulator [] [] []

@[simp] theorem mul_step_outer_nil (multiplicand accumulator : List Bool) :
    mulMachine.step (mulOuterCfg [] multiplicand accumulator) =
      some (mulDoneCfg multiplicand accumulator) := by
  simp [mulMachine, mulOuterCfg, mulDoneCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_outer_cons (b : Bool)
    (bits multiplicand accumulator : List Bool) :
    mulMachine.step (mulOuterCfg (b :: bits) multiplicand accumulator) =
      some (mulCfg .select b false bits multiplicand accumulator [] [] []) := by
  have hdefault : (default : MulControl)=⟨none,false,none,none,none⟩ := rfl
  simp [mulMachine, mulOuterCfg, mulCfg, mulStacks, Function.update,hdefault]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_select_false (bits multiplicand accumulator : List Bool) :
    mulMachine.step
        (mulCfg .select false false bits multiplicand accumulator [] [] []) =
      some (mulCfg .shiftFirst false false bits multiplicand accumulator [] [] []) := by
  simp [mulMachine, mulCfg, mulStacks]
  all_goals rfl

@[simp] theorem mul_step_select_true (bits multiplicand accumulator : List Bool) :
    mulMachine.step
        (mulCfg .select true false bits multiplicand accumulator [] [] []) =
      some (mulCfg .add true false bits multiplicand accumulator [] [] []) := by
  simp [mulMachine, mulCfg, mulStacks]
  all_goals rfl

@[simp] theorem mul_step_add_cons (selected carry x a : Bool)
    (bits xs as backup result temp : List Bool) :
    mulMachine.step
        (mulCfg .add selected carry bits (x :: xs) (a :: as) backup result temp) =
      some (mulCfg .add selected (fullAdder x a carry).2 bits xs as
        (x :: backup) ((fullAdder x a carry).1 :: result) temp) := by
  simp [mulMachine, MulControl.sumBit, MulControl.addAdvance, mulCfg, mulStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_add_nil (selected carry : Bool)
    (bits backup result temp : List Bool) :
    mulMachine.step
        (mulCfg .add selected carry bits [] [] backup result temp) =
      some (mulCfg .restoreMultiplicand selected carry bits [] [] backup result temp) := by
  simp [mulMachine, mulCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem mul_add_iterate (selected carry : Bool)
    (bits left right backup result temp : List Bool)
    (hlen : left.length = right.length) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[left.length])
      (some (mulCfg .add selected carry bits left right backup result temp)) =
    some (mulCfg .add selected (addCarryOut left right carry) bits [] []
      (left.reverse ++ backup) ((addBits left right carry).reverse ++ result) temp) := by
  induction left generalizing right carry backup result with
  | nil =>
      cases right with
      | nil => rfl
      | cons _ _ => simp at hlen
  | cons x xs ih =>
      cases right with
      | nil => simp at hlen
      | cons a as =>
          simp at hlen
          rw [List.length_cons, Function.iterate_succ_apply]
          simp only [Option.bind_some, mul_step_add_cons]
          rw [ih (fullAdder x a carry).2 as (x :: backup)
            ((fullAdder x a carry).1 :: result) hlen]
          simp [addCarryOut, addBits, List.reverse_cons, List.append_assoc]

@[simp] theorem mul_step_restoreMultiplicand_cons (selected carry a : Bool)
    (bits source target accumulator result temp : List Bool) :
    mulMachine.step (mulCfg .restoreMultiplicand selected carry bits target accumulator
      (a :: source) result temp) =
    some (mulCfg .restoreMultiplicand selected carry bits (a :: target) accumulator
      source result temp) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_restoreMultiplicand_nil (selected carry : Bool)
    (bits target accumulator result temp : List Bool) :
    mulMachine.step (mulCfg .restoreMultiplicand selected carry bits target accumulator
      [] result temp) =
    some (mulCfg .restoreSum selected carry bits target accumulator [] result temp) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_restoreSum_cons (selected carry a : Bool)
    (bits multiplicand accumulator backup source temp : List Bool) :
    mulMachine.step (mulCfg .restoreSum selected carry bits multiplicand accumulator
      backup (a :: source) temp) =
    some (mulCfg .restoreSum selected carry bits multiplicand (a :: accumulator)
      backup source temp) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_restoreSum_nil (selected carry : Bool)
    (bits multiplicand accumulator backup temp : List Bool) :
    mulMachine.step (mulCfg .restoreSum selected carry bits multiplicand accumulator
      backup [] temp) =
    some (mulCfg .shiftFirst selected carry bits multiplicand accumulator
      backup [] temp) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftFirst_cons (selected carry a : Bool)
    (bits source accumulator backup result temp : List Bool) :
    mulMachine.step (mulCfg .shiftFirst selected carry bits (a :: source) accumulator
      backup result temp) =
    some (mulCfg .shiftFirst selected carry bits source accumulator backup result
      (a :: temp)) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftFirst_nil (selected carry : Bool)
    (bits accumulator backup result temp : List Bool) :
    mulMachine.step (mulCfg .shiftFirst selected carry bits [] accumulator
      backup result temp) =
    some (mulCfg .shiftDiscard selected carry bits [] accumulator backup result temp) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftDiscard_cons (selected carry a : Bool)
    (bits accumulator backup result temp : List Bool) :
    mulMachine.step (mulCfg .shiftDiscard selected carry bits [] accumulator
      backup result (a :: temp)) =
    some (mulCfg .shiftSecond selected carry bits [] accumulator backup result temp) := by
  simp [mulMachine, MulControl.clearHeld, mulCfg, mulStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftSecond_cons (selected carry a : Bool)
    (bits multiplicand accumulator backup result source : List Bool) :
    mulMachine.step (mulCfg .shiftSecond selected carry bits multiplicand accumulator
      backup result (a :: source)) =
    some (mulCfg .shiftSecond selected carry bits (a :: multiplicand) accumulator
      backup result source) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftSecond_nil (selected carry : Bool)
    (bits multiplicand accumulator backup result : List Bool) :
    mulMachine.step (mulCfg .shiftSecond selected carry bits multiplicand accumulator
      backup result []) =
    some (mulCfg .shiftPrepend selected carry bits multiplicand accumulator
      backup result []) := by
  simp [mulMachine, mulMoveIteration, MulControl.clearHeld, mulCfg, mulStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem mul_step_shiftPrepend (selected carry : Bool)
    (bits multiplicand accumulator : List Bool) :
    mulMachine.step (mulCfg .shiftPrepend selected carry bits multiplicand accumulator
      [] [] []) =
    some (mulOuterCfg bits (false :: multiplicand) accumulator) := by
  simp [mulMachine, mulCfg, mulOuterCfg, mulStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem mul_restoreMultiplicand_iterate (selected carry : Bool)
    (bits source target accumulator result temp : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[source.length])
      (some (mulCfg .restoreMultiplicand selected carry bits target accumulator
        source result temp)) =
    some (mulCfg .restoreMultiplicand selected carry bits
      (source.reverse ++ target) accumulator [] result temp) := by
  induction source generalizing target with
  | nil => rfl
  | cons a source ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, mul_step_restoreMultiplicand_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem mul_restoreSum_iterate (selected carry : Bool)
    (bits multiplicand accumulator backup source temp : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[source.length])
      (some (mulCfg .restoreSum selected carry bits multiplicand accumulator
        backup source temp)) =
    some (mulCfg .restoreSum selected carry bits multiplicand
      (source.reverse ++ accumulator) backup [] temp) := by
  induction source generalizing accumulator with
  | nil => rfl
  | cons a source ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, mul_step_restoreSum_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem mul_shiftFirst_iterate (selected carry : Bool)
    (bits source accumulator backup result temp : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[source.length])
      (some (mulCfg .shiftFirst selected carry bits source accumulator backup result temp)) =
    some (mulCfg .shiftFirst selected carry bits [] accumulator backup result
      (source.reverse ++ temp)) := by
  induction source generalizing temp with
  | nil => rfl
  | cons a source ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, mul_step_shiftFirst_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem mul_shiftSecond_iterate (selected carry : Bool)
    (bits multiplicand accumulator backup result source : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[source.length])
      (some (mulCfg .shiftSecond selected carry bits multiplicand accumulator
        backup result source)) =
    some (mulCfg .shiftSecond selected carry bits (source.reverse ++ multiplicand)
      accumulator backup result []) := by
  induction source generalizing multiplicand with
  | nil => rfl
  | cons a source ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, mul_step_shiftSecond_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem mul_shift_phase (selected carry a : Bool) (as bits accumulator : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
      2 * (a :: as).length + 3])
      (some (mulCfg .shiftFirst selected carry bits (a :: as) accumulator [] [] [])) =
    some (mulOuterCfg bits (shiftLeftBits (a :: as)) accumulator) := by
  let stepO := fun o : Option mulMachine.Cfg => o.bind mulMachine.step
  have chain {r s : ℕ} {x y z : Option mulMachine.Cfg}
      (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by
    rw [Function.iterate_add_apply, hr, hs]
  have hfirst := mul_shiftFirst_iterate selected carry bits (a :: as) accumulator [] [] []
  have hfirstEnd : (stepO^[1])
      (some (mulCfg .shiftFirst selected carry bits [] accumulator [] []
        (a :: as).reverse)) =
      some (mulCfg .shiftDiscard selected carry bits [] accumulator [] []
        (a :: as).reverse) := by
    simpa [stepO] using mul_step_shiftFirst_nil selected carry bits accumulator [] []
      (a :: as).reverse
  have hrev : (a :: as).reverse ≠ [] := by simp
  cases htemp : (a :: as).reverse with
  | nil => contradiction
  | cons top rest =>
      have hfirst' := hfirst
      simp only [List.append_nil] at hfirst'
      rw [htemp] at hfirst'
      have hfirstEnd' := hfirstEnd
      rw [htemp] at hfirstEnd'
      have hdiscard : (stepO^[1])
          (some (mulCfg .shiftDiscard selected carry bits [] accumulator [] []
            (top :: rest))) =
          some (mulCfg .shiftSecond selected carry bits [] accumulator [] [] rest) := by
        simpa [stepO] using mul_step_shiftDiscard_cons selected carry top bits accumulator [] [] rest
      have hsecond := mul_shiftSecond_iterate selected carry bits [] accumulator [] [] rest
      have hsecond' := hsecond
      simp only [List.append_nil] at hsecond'
      have hsecondEnd : (stepO^[1])
          (some (mulCfg .shiftSecond selected carry bits rest.reverse accumulator [] [] [])) =
          some (mulCfg .shiftPrepend selected carry bits rest.reverse accumulator [] [] []) := by
        simpa [stepO] using mul_step_shiftSecond_nil selected carry bits rest.reverse accumulator [] []
      have hprepend : (stepO^[1])
          (some (mulCfg .shiftPrepend selected carry bits rest.reverse accumulator [] [] [])) =
          some (mulOuterCfg bits (false :: rest.reverse) accumulator) := by
        simpa [stepO] using mul_step_shiftPrepend selected carry bits rest.reverse accumulator
      have hrun := chain (chain (chain (chain hfirst' hfirstEnd') hdiscard) hsecond')
        (chain hsecondEnd hprepend)
      have hrest : rest = (a :: as).reverse.tail := by simp [htemp]
      have hout : false :: rest.reverse = shiftLeftBits (a :: as) := by
        rw [hrest, List.tail_reverse, List.reverse_reverse, List.dropLast_eq_take]
        simp [shiftLeftBits]
      have hlen : rest.length + 1 = (a :: as).length := by
        rw [hrest]
        simp
      have hexp : 1 + 1 + (rest.length + (1 + (1 + (a :: as).length))) =
          2 * (a :: as).length + 3 := by omega
      rw [hexp] at hrun
      simpa [stepO, hout] using hrun

theorem mul_false_round (a : Bool) (as bits accumulator : List Bool) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
      2 * (a :: as).length + 5])
      (some (mulOuterCfg (false :: bits) (a :: as) accumulator)) =
    some (mulOuterCfg bits (shiftLeftBits (a :: as)) accumulator) := by
  let stepO := fun o : Option mulMachine.Cfg => o.bind mulMachine.step
  have h0 : (stepO^[1])
      (some (mulOuterCfg (false :: bits) (a :: as) accumulator)) =
      some (mulCfg .select false false bits (a :: as) accumulator [] [] []) := by
    simpa [stepO] using mul_step_outer_cons false bits (a :: as) accumulator
  have h1 : (stepO^[1])
      (some (mulCfg .select false false bits (a :: as) accumulator [] [] [])) =
      some (mulCfg .shiftFirst false false bits (a :: as) accumulator [] [] []) := by
    simpa [stepO] using mul_step_select_false bits (a :: as) accumulator
  have hs := mul_shift_phase false false a as bits accumulator
  have chain {r s : ℕ} {x y z : Option mulMachine.Cfg}
      (hr : (stepO^[r]) x = y) (ht : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by rw [Function.iterate_add_apply, hr, ht]
  have hrun := chain (chain h0 h1) hs
  have hexp : (2 * (a :: as).length + 3) + (1 + 1) =
      2 * (a :: as).length + 5 := by omega
  rw [hexp] at hrun
  simpa [stepO] using hrun

theorem mul_true_round (a : Bool) (as bits accumulator : List Bool)
    (hlen : accumulator.length = (a :: as).length) :
    ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
      5 * (a :: as).length + 8])
      (some (mulOuterCfg (true :: bits) (a :: as) accumulator)) =
    some (mulOuterCfg bits (shiftLeftBits (a :: as))
      (addBits (a :: as) accumulator false)) := by
  let x := a :: as
  let sum := addBits x accumulator false
  let carry := addCarryOut x accumulator false
  let stepO := fun o : Option mulMachine.Cfg => o.bind mulMachine.step
  have chain {r s : ℕ} {u v z : Option mulMachine.Cfg}
      (hr : (stepO^[r]) u = v) (ht : (stepO^[s]) v = z) :
      (stepO^[s + r]) u = z := by rw [Function.iterate_add_apply, hr, ht]
  have h0 : (stepO^[1]) (some (mulOuterCfg (true :: bits) x accumulator)) =
      some (mulCfg .select true false bits x accumulator [] [] []) := by
    simpa [stepO, x] using mul_step_outer_cons true bits x accumulator
  have h1 : (stepO^[1])
      (some (mulCfg .select true false bits x accumulator [] [] [])) =
      some (mulCfg .add true false bits x accumulator [] [] []) := by
    simpa [stepO] using mul_step_select_true bits x accumulator
  have hadd := mul_add_iterate true false bits x accumulator [] [] [] hlen.symm
  have hadd' := hadd
  simp only [List.append_nil] at hadd'
  have haddEnd : (stepO^[1])
      (some (mulCfg .add true carry bits [] [] x.reverse sum.reverse [])) =
      some (mulCfg .restoreMultiplicand true carry bits [] [] x.reverse sum.reverse []) := by
    simpa [stepO, carry, sum] using mul_step_add_nil true carry bits x.reverse sum.reverse []
  have hrestoreX := mul_restoreMultiplicand_iterate true carry bits x.reverse [] []
    sum.reverse []
  have hrestoreX' := hrestoreX
  simp only [List.reverse_reverse, List.append_nil] at hrestoreX'
  have hrestoreXEnd : (stepO^[1])
      (some (mulCfg .restoreMultiplicand true carry bits x [] [] sum.reverse [])) =
      some (mulCfg .restoreSum true carry bits x [] [] sum.reverse []) := by
    simpa [stepO] using mul_step_restoreMultiplicand_nil true carry bits x [] sum.reverse []
  have hrestoreSum := mul_restoreSum_iterate true carry bits x [] [] sum.reverse []
  have hrestoreSum' := hrestoreSum
  simp only [List.reverse_reverse, List.append_nil] at hrestoreSum'
  have hrestoreSumEnd : (stepO^[1])
      (some (mulCfg .restoreSum true carry bits x sum [] [] [])) =
      some (mulCfg .shiftFirst true carry bits x sum [] [] []) := by
    simpa [stepO] using mul_step_restoreSum_nil true carry bits x sum [] []
  have hshift := mul_shift_phase true carry a as bits sum
  have h02 := chain h0 h1
  have h03 := chain h02 hadd'
  have h04 := chain h03 haddEnd
  have h05 := chain h04 hrestoreX'
  have h06 := chain h05 hrestoreXEnd
  have h07 := chain h06 hrestoreSum'
  have h08 := chain h07 hrestoreSumEnd
  have hrun := chain h08 hshift
  simp only [List.length_reverse] at hrun
  have hsum : sum.length = x.length := by
    dsimp [sum]
    exact addBits_length_of_eq false hlen.symm
  have hexp : (2 * (a :: as).length + 3) +
      (1 + (sum.length + (1 + (x.length +
        (1 + (x.length + (1 + 1))))))) = 5 * x.length + 8 := by
    rw [hsum]
    change 2 * x.length + 3 +
      (1 + (x.length + (1 + (x.length + (1 + (x.length + (1 + 1))))))) = _
    omega
  rw [hexp] at hrun
  simpa [stepO, x, sum, carry] using hrun

def mulRunTime : List Bool → ℕ → ℕ
  | [], _ => 1
  | false :: bits, w => 2 * w + 5 + mulRunTime bits w
  | true :: bits, w => 5 * w + 8 + mulRunTime bits w

theorem mulRunTime_le (bits : List Bool) (w : ℕ) :
    mulRunTime bits w ≤ bits.length * (5 * w + 8) + 1 := by
  induction bits with
  | nil => simp [mulRunTime]
  | cons b bits ih =>
      cases b <;> simp only [mulRunTime, List.length_cons]
      · have : 2 * w + 5 ≤ 5 * w + 8 := by omega
        rw [Nat.add_mul, Nat.one_mul]
        omega
      · rw [Nat.add_mul, Nat.one_mul]
        omega

theorem mulMachine_fixed_time_le (w b : ℕ) :
    mulRunTime (fixedBits w b) w ≤ w * (5 * w + 8) + 1 := by
  simpa using mulRunTime_le (fixedBits w b) w

/-- Functional shift-and-add semantics mirrored by `mulMachine`. -/
def mulAccBits : List Bool → List Bool → List Bool → List Bool
  | [], _, acc => acc
  | b :: bs, multiplicand, acc =>
      mulAccBits bs (shiftLeftBits multiplicand)
        (if b then addBits multiplicand acc false else acc)

@[simp] theorem mulAccBits_length (bits multiplicand acc : List Bool)
    (hm : multiplicand.length = acc.length) :
    (mulAccBits bits multiplicand acc).length = acc.length := by
  induction bits generalizing multiplicand acc with
  | nil => rfl
  | cons b bits ih =>
      cases b with
      | false =>
          simp only [mulAccBits, Bool.false_eq_true, if_false]
          apply ih
          rw [shiftLeftBits_length, hm]
      | true =>
          simp only [mulAccBits, if_true]
          have hadd : (addBits multiplicand acc false).length = acc.length := by
            rw [addBits_length_of_eq false hm, hm]
          have hargs : (shiftLeftBits multiplicand).length =
              (addBits multiplicand acc false).length := by
            rw [shiftLeftBits_length, hadd, hm]
          rw [ih _ _ hargs, hadd]

theorem mulAccBits_fixed_aux (k w a b z : ℕ) (hbfit : b < 2 ^ k) :
    mulAccBits (fixedBits k b) (fixedBits w a) (fixedBits w z) =
      fixedBits w (z + a * b) := by
  induction k generalizing a b z with
  | zero =>
      have : b = 0 := by simpa using hbfit
      subst b
      simp [fixedBits, mulAccBits]
  | succ k ih =>
      simp only [fixedBits, mulAccBits]
      have hdiv : b.div2 < 2 ^ k := by
        rw [pow_succ'] at hbfit
        rw [Nat.div2_val]
        omega
      cases hbit : b.bodd with
      | true =>
        simp only [hbit, if_true]
        rw [← fixedBits_add]
        rw [shiftLeftBits_fixed]
        rw [ih _ _ _ hdiv]
        congr 1
        rw [← Nat.bit_bodd_div2 b]
        simp [hbit, Nat.bit, pow_succ]
        ring
      | false =>
        simp only [hbit, Bool.false_eq_true, if_false]
        rw [shiftLeftBits_fixed, ih _ _ _ hdiv]
        congr 1
        rw [← Nat.bit_bodd_div2 b]
        simp [hbit, Nat.bit, pow_succ]
        ring

theorem mulAccBits_fixed (w a b z : ℕ) (hb : b < 2 ^ w) :
    mulAccBits (fixedBits w b) (fixedBits w a) (fixedBits w z) =
      fixedBits w (z + a * b) :=
  mulAccBits_fixed_aux w w a b z hb

theorem mulMachine_correct (bits multiplicand accumulator : List Bool)
    (w : ℕ) (hw : 0 < w) (hbits : bits.length ≤ w)
    (hm : multiplicand.length = w) (ha : accumulator.length = w) :
    ∃ finalMultiplicand : List Bool, finalMultiplicand.length = w ∧
      ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[mulRunTime bits w])
        (some (mulOuterCfg bits multiplicand accumulator)) =
      some (mulDoneCfg finalMultiplicand (mulAccBits bits multiplicand accumulator)) := by
  induction bits generalizing multiplicand accumulator with
  | nil =>
      refine ⟨multiplicand, hm, ?_⟩
      simpa [mulRunTime, mulAccBits] using mul_step_outer_nil multiplicand accumulator
  | cons b bits ih =>
      have hle : bits.length ≤ (b :: bits).length := by simp
      have htail : bits.length ≤ w := hle.trans hbits
      cases multiplicand with
      | nil => simp at hm; omega
      | cons m ms =>
        cases b with
        | false =>
            have hround := mul_false_round m ms bits accumulator
            have hm' : (shiftLeftBits (m :: ms)).length = w := by
              rw [shiftLeftBits_length, hm]
            rcases ih (shiftLeftBits (m :: ms)) accumulator htail hm' ha with
              ⟨final, hfinal, htailRun⟩
            refine ⟨final, hfinal, ?_⟩
            let stepO := fun o : Option mulMachine.Cfg => o.bind mulMachine.step
            have chain {r s : ℕ} {x y z : Option mulMachine.Cfg}
                (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
                (stepO^[s + r]) x = z := by rw [Function.iterate_add_apply, hr, hs]
            have hrun := chain hround htailRun
            have htime : mulRunTime bits w + (2 * (m :: ms).length + 5) =
                2 * w + 5 + mulRunTime bits w := by
              rw [hm]
              omega
            rw [htime] at hrun
            simpa [stepO, mulRunTime, mulAccBits] using hrun
        | true =>
            have hround := mul_true_round m ms bits accumulator (by omega)
            have hm' : (shiftLeftBits (m :: ms)).length = w := by
              rw [shiftLeftBits_length, hm]
            have hsum : (addBits (m :: ms) accumulator false).length = w := by
              rw [addBits_length_of_eq false (by omega), hm]
            rcases ih (shiftLeftBits (m :: ms))
                (addBits (m :: ms) accumulator false) htail hm' hsum with
              ⟨final, hfinal, htailRun⟩
            refine ⟨final, hfinal, ?_⟩
            let stepO := fun o : Option mulMachine.Cfg => o.bind mulMachine.step
            have chain {r s : ℕ} {x y z : Option mulMachine.Cfg}
                (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
                (stepO^[s + r]) x = z := by rw [Function.iterate_add_apply, hr, hs]
            have hrun := chain hround htailRun
            have htime : mulRunTime bits w + (5 * (m :: ms).length + 8) =
                5 * w + 8 + mulRunTime bits w := by
              rw [hm]
              omega
            rw [htime] at hrun
            simpa [stepO, mulRunTime, mulAccBits] using hrun

theorem mulMachine_fixed_correct (w a b : ℕ) (hw : 0 < w)
    (hb : b < 2 ^ w) :
    ∃ finalMultiplicand : List Bool,
      ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
        mulRunTime (fixedBits w b) w])
        (some (mulOuterCfg (fixedBits w b) (fixedBits w a) (fixedBits w 0))) =
      some (mulDoneCfg finalMultiplicand (fixedBits w (a * b))) := by
  rcases mulMachine_correct (fixedBits w b) (fixedBits w a) (fixedBits w 0)
      w hw (by simp) (by simp) (by simp) with ⟨final, _, hrun⟩
  refine ⟨final, ?_⟩
  rw [mulAccBits_fixed w a b 0 hb] at hrun
  simpa using hrun

theorem mulMachine_fixed_correct_with_length (w a b : ℕ) (hw : 0 < w)
    (hb : b < 2 ^ w) :
    ∃ finalMultiplicand : List Bool, finalMultiplicand.length = w ∧
      ((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[
        mulRunTime (fixedBits w b) w])
        (some (mulOuterCfg (fixedBits w b) (fixedBits w a) (fixedBits w 0))) =
      some (mulDoneCfg finalMultiplicand (fixedBits w (a * b))) := by
  rcases mulMachine_correct (fixedBits w b) (fixedBits w a) (fixedBits w 0)
      w hw (by simp) (by simp) (by simp) with ⟨final, hlen, hrun⟩
  refine ⟨final, hlen, ?_⟩
  rw [mulAccBits_fixed w a b 0 hb] at hrun
  simpa using hrun

end Lax51Proofs.RamToTM

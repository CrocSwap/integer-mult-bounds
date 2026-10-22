import MultitapeToolkit.Reused.Computability.BinaryMultiplication20261013

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

namespace MultitapeToolkit.BinaryMultiplication

open Turing TM2 Lax51Proofs.RamToTM

inductive SetupPhase
  | copyA | padA | restoreA | copyB | padB | restoreB
  deriving DecidableEq, Fintype, Inhabited

abbrev SetupLabel := SetupPhase ⊕ MulLabel

def liftMulStmt : TM2.Stmt (fun _ : MulStack => Bool) MulLabel MulControl →
    TM2.Stmt (fun _ : MulStack => Bool) SetupLabel MulControl
  | .push k f q => .push k f (liftMulStmt q)
  | .peek k f q => .peek k f (liftMulStmt q)
  | .pop k f q => .pop k f (liftMulStmt q)
  | .load f q => .load f (liftMulStmt q)
  | .branch f q r => .branch f (liftMulStmt q) (liftMulStmt r)
  | .goto f => .goto (fun s => .inr (f s))
  | .halt => .halt

/-- A pop loop executes one fixed finite statement per consumed bit, followed
by one empty-stack transition.  Its pushed bits are held in finite control. -/
def setupIteration (_p : SetupPhase) (source : MulStack)
    (body : TM2.Stmt (fun _ : MulStack => Bool) SetupLabel MulControl)
    (next : SetupLabel) : TM2.Stmt (fun _ : MulStack => Bool) SetupLabel MulControl :=
  .pop source (fun s bit => { s with held := bit }) <|
    .branch (fun s => s.held.isNone)
      (.load (fun _ => default) <| .goto (fun _ => next)) body

def setupBack (p : SetupPhase) :
    TM2.Stmt (fun _ : MulStack => Bool) SetupLabel MulControl :=
  .load (fun _ => default) <| .goto (fun _ => .inl p)

def setupMachine : Turing.FinTM2 where
  K := MulStack
  k₀ := .multiplicand
  k₁ := .accumulator
  Γ _ := Bool
  Λ := SetupLabel
  main := .inl .copyA
  σ := MulControl
  initialState := default
  m
    | .inr label => liftMulStmt (mulMachine.m label)
    | .inl .copyA => setupIteration .copyA .multiplicand
        (.push .multiplicandBackup (fun s => s.held.getD false) <|
          .push .accumulator (fun _ => false) <|
            .push .shiftTemp (fun _ => false) <| setupBack .copyA)
        (.inl .padA)
    | .inl .padA => setupIteration .padA .shiftTemp
        (.push .multiplicand (fun s => s.held.getD false) <|
          .push .sumReverse (fun s => s.held.getD false) <| setupBack .padA)
        (.inl .restoreA)
    | .inl .restoreA => setupIteration .restoreA .multiplicandBackup
        (.push .multiplicand (fun s => s.held.getD false) <| setupBack .restoreA)
        (.inl .copyB)
    | .inl .copyB => setupIteration .copyB .multiplier
        (.push .multiplicandBackup (fun s => s.held.getD false) <|
          .push .accumulator (fun _ => false) <| setupBack .copyB)
        (.inl .padB)
    | .inl .padB => setupIteration .padB .sumReverse
        (.push .multiplier (fun s => s.held.getD false) <| setupBack .padB)
        (.inl .restoreB)
    | .inl .restoreB => setupIteration .restoreB .multiplicandBackup
        (.push .multiplier (fun s => s.held.getD false) <| setupBack .restoreB)
        (.inr .outer)

def liftMulCfg (c : mulMachine.Cfg) : setupMachine.Cfg where
  l := c.l.map Sum.inr
  var := c.var
  stk := c.stk

/-- All scratch stacks start empty; the only supplied data are the two
`n`-bit operands.  The finite machine itself creates zero padding. -/
def rawInput (n a b : ℕ) : setupMachine.Cfg where
  l := some (.inl .copyA)
  var := default
  stk := mulStacks (fixedBits n b) (fixedBits n a) [] [] [] []

def setupCfg (label : SetupLabel) (b a acc backup sum temp : List Bool) :
    setupMachine.Cfg where
  l := some label
  var := default
  stk := mulStacks b a acc backup sum temp

abbrev setupStep (o : Option setupMachine.Cfg) : Option setupMachine.Cfg :=
  o.bind setupMachine.step

@[simp] theorem setupStep_some (c : setupMachine.Cfg) :
    setupStep (some c) = setupMachine.step c := rfl
private theorem run_chain {r s : ℕ} {x y z : Option setupMachine.Cfg}
    (hr : (setupStep^[r]) x = y) (hs : (setupStep^[s]) y = z) :
    (setupStep^[s + r]) x = z := by
  rw [Function.iterate_add_apply, hr, hs]

 theorem liftMul_stepAux (q : TM2.Stmt (fun _ : MulStack => Bool) MulLabel MulControl)
    (s : MulControl) (ss : MulStack → List Bool) :
    TM2.stepAux (liftMulStmt q) s ss =
      liftMulCfg (TM2.stepAux q s ss) := by
  induction q generalizing s ss with
  | push k f q ih => exact ih s (Function.update ss k (f s :: ss k))
  | peek k f q ih => exact ih (f s (ss k).head?) ss
  | pop k f q ih => exact ih (f s (ss k).head?) (Function.update ss k (ss k).tail)
  | load f q ih => exact ih (f s) ss
  | branch f q r ihq ihr =>
      cases h : f s <;> simp [liftMulStmt, TM2.stepAux, h, ihq, ihr]
  | goto f => rfl
  | halt => rfl

 theorem liftMul_step (c : mulMachine.Cfg) :
    setupMachine.step (liftMulCfg c) = (mulMachine.step c).map liftMulCfg := by
  rcases c with ⟨l, s, ss⟩
  cases l with
  | none => rfl
  | some l =>
      change some (TM2.stepAux (liftMulStmt (mulMachine.m l)) s ss) = _
      rw [liftMul_stepAux]
      rfl

 theorem liftMul_run (t : ℕ) (c : mulMachine.Cfg) :
    (setupStep^[t]) (some (liftMulCfg c)) =
      (((fun o : Option mulMachine.Cfg => o.bind mulMachine.step)^[t]) (some c)).map
        liftMulCfg := by
  have hstep (o : Option mulMachine.Cfg) :
      setupStep (o.map liftMulCfg) = (o.bind mulMachine.step).map liftMulCfg := by
    cases o with
    | none => rfl
    | some c => exact liftMul_step c
  induction t with
  | zero => rfl
  | succ t ih =>
      rw [Function.iterate_succ_apply', Function.iterate_succ_apply', ih, hstep]


theorem setup_copyA_run (b a acc backup sum temp : List Bool) :
    (setupStep^[a.length + 1]) (some (setupCfg (.inl .copyA) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inl .padA) (b) ([]) (List.replicate a.length false ++ acc) (a.reverse ++ backup) (sum) (List.replicate a.length false ++ temp)) := by
  induction a generalizing b acc backup sum temp with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .copyA) (b) (x :: xs) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .copyA) (b) (xs) (false :: acc) (x :: backup) (sum) (false :: temp)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.replicate_succ', List.append_assoc]

theorem setup_padA_run (b a acc backup sum temp : List Bool) :
    (setupStep^[temp.length + 1]) (some (setupCfg (.inl .padA) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inl .restoreA) (b) (temp.reverse ++ a) (acc) (backup) (temp.reverse ++ sum) ([])) := by
  induction temp generalizing b a acc backup sum with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .padA) (b) (a) (acc) (backup) (sum) (x :: xs)) = some (setupCfg (.inl .padA) (b) (x :: a) (acc) (backup) (x :: sum) (xs)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem setup_restoreA_run (b a acc backup sum temp : List Bool) :
    (setupStep^[backup.length + 1]) (some (setupCfg (.inl .restoreA) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inl .copyB) (b) (backup.reverse ++ a) (acc) ([]) (sum) (temp)) := by
  induction backup generalizing b a acc sum temp with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .restoreA) (b) (a) (acc) (x :: xs) (sum) (temp)) = some (setupCfg (.inl .restoreA) (b) (x :: a) (acc) (xs) (sum) (temp)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem setup_copyB_run (b a acc backup sum temp : List Bool) :
    (setupStep^[b.length + 1]) (some (setupCfg (.inl .copyB) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inl .padB) ([]) (a) (List.replicate b.length false ++ acc) (b.reverse ++ backup) (sum) (temp)) := by
  induction b generalizing a acc backup sum temp with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .copyB) (x :: xs) (a) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .copyB) (xs) (a) (false :: acc) (x :: backup) (sum) (temp)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.replicate_succ', List.append_assoc]

theorem setup_padB_run (b a acc backup sum temp : List Bool) :
    (setupStep^[sum.length + 1]) (some (setupCfg (.inl .padB) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inl .restoreB) (sum.reverse ++ b) (a) (acc) (backup) ([]) (temp)) := by
  induction sum generalizing b a acc backup temp with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .padB) (b) (a) (acc) (backup) (x :: xs) (temp)) = some (setupCfg (.inl .padB) (x :: b) (a) (acc) (backup) (xs) (temp)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem setup_restoreB_run (b a acc backup sum temp : List Bool) :
    (setupStep^[backup.length + 1]) (some (setupCfg (.inl .restoreB) (b) (a) (acc) (backup) (sum) (temp))) =
      some (setupCfg (.inr .outer) (backup.reverse ++ b) (a) (acc) ([]) (sum) (temp)) := by
  induction backup generalizing b a acc sum temp with
  | nil =>
      simp [setupStep, setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
  | cons x xs ih =>
      have hfirst : setupMachine.step (setupCfg (.inl .restoreB) (b) (a) (acc) (x :: xs) (sum) (temp)) = some (setupCfg (.inl .restoreB) (x :: b) (a) (acc) (xs) (sum) (temp)) := by
        simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
        all_goals (funext k; cases k <;> rfl)
      rw [List.length_cons, Function.iterate_succ_apply, setupStep_some, hfirst]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

/-- Actual six-phase input preparation takes `6*n+6` macrosteps. -/
theorem setup_exact (n a b : ℕ) (ha : a < 2 ^ n) (hb : b < 2 ^ n) :
    (setupStep^[6 * n + 6]) (some (rawInput n a b)) =
      some (liftMulCfg (preparedInput n a b)) := by
  let A := fixedBits n a
  let B := fixedBits n b
  let Z := List.replicate n false
  have h1 : (setupStep^[n + 1])
      (some (setupCfg (.inl .copyA) B A [] [] [] [])) =
      some (setupCfg (.inl .padA) B [] Z A.reverse [] Z) := by
    simpa [A, B, Z] using setup_copyA_run B A [] [] [] []
  have h2 : (setupStep^[n + 1])
      (some (setupCfg (.inl .padA) B [] Z A.reverse [] Z)) =
      some (setupCfg (.inl .restoreA) B Z Z A.reverse Z []) := by
    simpa [Z] using setup_padA_run B [] Z A.reverse [] Z
  have h3 : (setupStep^[n + 1])
      (some (setupCfg (.inl .restoreA) B Z Z A.reverse Z [])) =
      some (setupCfg (.inl .copyB) B (A ++ Z) Z [] Z []) := by
    simpa [A] using setup_restoreA_run B Z Z A.reverse Z []
  have h4 : (setupStep^[n + 1])
      (some (setupCfg (.inl .copyB) B (A ++ Z) Z [] Z [])) =
      some (setupCfg (.inl .padB) [] (A ++ Z) (Z ++ Z) B.reverse Z []) := by
    simpa [A, B, Z] using setup_copyB_run B (A ++ Z) Z [] Z []
  have h5 : (setupStep^[n + 1])
      (some (setupCfg (.inl .padB) [] (A ++ Z) (Z ++ Z) B.reverse Z [])) =
      some (setupCfg (.inl .restoreB) Z (A ++ Z) (Z ++ Z) B.reverse [] []) := by
    simpa [Z] using setup_padB_run [] (A ++ Z) (Z ++ Z) B.reverse Z []
  have h6 : (setupStep^[n + 1])
      (some (setupCfg (.inl .restoreB) Z (A ++ Z) (Z ++ Z) B.reverse [] [])) =
      some (setupCfg (.inr .outer) (B ++ Z) (A ++ Z) (Z ++ Z) [] [] []) := by
    simpa [B] using setup_restoreB_run Z (A ++ Z) (Z ++ Z) B.reverse [] []
  have hrun := run_chain (run_chain (run_chain (run_chain (run_chain h1 h2) h3) h4) h5) h6
  have htime : (n + 1) + ((n + 1) + ((n + 1) +
      ((n + 1) + ((n + 1) + (n + 1))))) = 6 * n + 6 := by omega
  rw [htime] at hrun
  have hinit : setupCfg (.inl .copyA) B A [] [] [] [] = rawInput n a b := rfl
  have hzero : Z ++ Z = fixedBits (productWidth n) 0 := by
    rw [fixedBits_zero]
    change List.replicate n false ++ List.replicate n false = List.replicate (2 * n) false
    rw [← List.replicate_add]
    congr 1
    omega
  have hfinal : setupCfg (.inr .outer) (B ++ Z) (A ++ Z) (Z ++ Z) [] [] [] =
      liftMulCfg (preparedInput n a b) := by
    rw [show A ++ Z = fixedBits (productWidth n) a from fixedBits_pad ha,
      show B ++ Z = fixedBits (productWidth n) b from fixedBits_pad hb, hzero]
    rfl
  simpa only [hinit, hfinal] using hrun

/-- Real input preparation followed by the verified schoolbook macro. -/
theorem raw_product_halts (n a b : ℕ) (ha : a < 2 ^ n) (hb : b < 2 ^ n) :
    ∃ finalMultiplicand : List Bool,
      finalMultiplicand.length = productWidth n ∧
      (setupStep^[6 * n + 6 + macroTime n b]) (some (rawInput n a b)) =
        some (liftMulCfg (mulHaltedCfg finalMultiplicand
          (fixedBits (productWidth n) (a * b)))) ∧
      bitsValue (fixedBits (productWidth n) (a * b)) = a * b := by
  rcases exact_product_halts n a b ha hb with ⟨final, hlen, hrun, hout⟩
  have hlift := liftMul_run (macroTime n b) (preparedInput n a b)
  rw [hrun] at hlift
  have hfull := run_chain (setup_exact n a b ha hb) hlift
  refine ⟨final, hlen, ?_, hout⟩
  simpa only [Nat.add_comm, Option.map_some] using hfull

/-- Includes the finite machine's input preparation and halt transition. -/
theorem rawTime_le (n b : ℕ) :
    6 * n + 6 + macroTime n b ≤ 20 * n ^ 2 + 22 * n + 8 := by
  have h := macroTime_le n b
  omega

end MultitapeToolkit.BinaryMultiplication





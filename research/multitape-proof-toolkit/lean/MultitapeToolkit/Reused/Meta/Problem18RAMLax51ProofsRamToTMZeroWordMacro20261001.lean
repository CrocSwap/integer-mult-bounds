import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMLookupScanCorrect20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure ZeroWordControl where
  held : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

inductive ZeroWordStack | query | backup | result
  deriving DecidableEq, Fintype, Inhabited

inductive ZeroWordLabel | fill | restore | done
  deriving DecidableEq, Fintype, Inhabited

def zeroWordMachine : Turing.FinTM2 where
  K := ZeroWordStack
  k₀ := .query
  k₁ := .result
  Γ _ := SparseSymbol
  Λ := ZeroWordLabel
  main := .fill
  σ := ZeroWordControl
  initialState := default
  m
    | .fill =>
        .pop .query (fun _ a => ⟨a⟩) <|
          .branch (fun s => s.held.isNone)
            (.load (fun _ => default) <| .goto fun _ => .restore)
            (.push .backup (fun s => s.held.getD (.bit false)) <|
              .push .result (fun _ => .bit false) <|
                .load (fun _ => default) <| .goto fun _ => .fill)
    | .restore =>
        .pop .backup (fun _ a => ⟨a⟩) <|
          .branch (fun s => s.held.isNone)
            (.load (fun _ => default) <| .goto fun _ => .done)
            (.push .query (fun s => s.held.getD (.bit false)) <|
              .load (fun _ => default) <| .goto fun _ => .restore)
    | .done => .halt

def zeroWordProgram : ZeroWordLabel →
    TM2.Stmt (fun _ : ZeroWordStack => SparseSymbol)
      ZeroWordLabel ZeroWordControl := zeroWordMachine.m

def zeroWordStacks (query backup result : List SparseSymbol) :
    ZeroWordStack → List SparseSymbol
  | .query => query
  | .backup => backup
  | .result => result

def zeroWordCfg (label : ZeroWordLabel) (query backup result : List SparseSymbol) :
    zeroWordMachine.Cfg where
  l := some label
  var := default
  stk := zeroWordStacks query backup result

def zeroWordCfgState (label : ZeroWordLabel) (state : ZeroWordControl)
    (query backup result : List SparseSymbol) :
    TM2.Cfg (fun _ : ZeroWordStack => SparseSymbol)
      ZeroWordLabel ZeroWordControl where
  l := some label
  var := state
  stk := zeroWordStacks query backup result

theorem zeroWord_first_step_independent (state : ZeroWordControl)
    (query backup result : List SparseSymbol) :
    TM2.step zeroWordProgram
        (zeroWordCfgState .fill state query backup result) =
      TM2.step zeroWordProgram (zeroWordCfg .fill query backup result) := by
  cases query with
  | nil =>
      simp [TM2.step, zeroWordProgram, zeroWordMachine, zeroWordCfgState,
        zeroWordCfg, zeroWordStacks]
  | cons a query =>
      simp [TM2.step, zeroWordProgram, zeroWordMachine, zeroWordCfgState,
        zeroWordCfg, zeroWordStacks]

@[simp] theorem zeroWord_step_fill_nil (backup result : List SparseSymbol) :
    zeroWordMachine.step (zeroWordCfg .fill [] backup result) =
      some (zeroWordCfg .restore [] backup result) := by
  simp [zeroWordMachine, zeroWordCfg, zeroWordStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem zeroWord_step_fill_cons (a : SparseSymbol)
    (query backup result : List SparseSymbol) :
    zeroWordMachine.step (zeroWordCfg .fill (a :: query) backup result) =
      some (zeroWordCfg .fill query (a :: backup) (.bit false :: result)) := by
  simp [zeroWordMachine, zeroWordCfg, zeroWordStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem zeroWord_step_restore_nil (query result : List SparseSymbol) :
    zeroWordMachine.step (zeroWordCfg .restore query [] result) =
      some (zeroWordCfg .done query [] result) := by
  simp [zeroWordMachine, zeroWordCfg, zeroWordStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem zeroWord_step_restore_cons (a : SparseSymbol)
    (query backup result : List SparseSymbol) :
    zeroWordMachine.step (zeroWordCfg .restore query (a :: backup) result) =
      some (zeroWordCfg .restore (a :: query) backup result) := by
  simp [zeroWordMachine, zeroWordCfg, zeroWordStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem replicate_append_same_cons (n : ℕ) (a : SparseSymbol)
    (result : List SparseSymbol) :
    List.replicate n a ++ a :: result = a :: (List.replicate n a ++ result) := by
  induction n with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ, ih]

theorem zeroWord_fill_iterate (query backup result : List SparseSymbol) :
    ((fun o : Option zeroWordMachine.Cfg => o.bind zeroWordMachine.step)^[query.length])
      (some (zeroWordCfg .fill query backup result)) =
    some (zeroWordCfg .fill [] (query.reverse ++ backup)
      (List.replicate query.length (.bit false) ++ result)) := by
  induction query generalizing backup result with
  | nil => rfl
  | cons a query ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, zeroWord_step_fill_cons]
      rw [ih]
      congr 2
      · simp [List.reverse_cons, List.append_assoc]
      · exact replicate_append_same_cons query.length (.bit false) result

theorem zeroWord_restore_iterate (query backup result : List SparseSymbol) :
    ((fun o : Option zeroWordMachine.Cfg => o.bind zeroWordMachine.step)^[backup.length])
      (some (zeroWordCfg .restore query backup result)) =
    some (zeroWordCfg .restore (backup.reverse ++ query) [] result) := by
  induction backup generalizing query with
  | nil => rfl
  | cons a backup ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, zeroWord_step_restore_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem zeroWord_correct (query result : List SparseSymbol) :
    ((fun o : Option zeroWordMachine.Cfg => o.bind zeroWordMachine.step)^[
      2 * query.length + 2])
      (some (zeroWordCfg .fill query [] result)) =
    some (zeroWordCfg .done query []
      (List.replicate query.length (.bit false) ++ result)) := by
  let stepO := fun o : Option zeroWordMachine.Cfg => o.bind zeroWordMachine.step
  have hfill := zeroWord_fill_iterate query [] result
  have hfillEnd := zeroWord_step_fill_nil query.reverse
    (List.replicate query.length (.bit false) ++ result)
  have hfillEnd' : (stepO^[1])
      (some (zeroWordCfg .fill [] query.reverse
        (List.replicate query.length (.bit false) ++ result))) =
      some (zeroWordCfg .restore [] query.reverse
        (List.replicate query.length (.bit false) ++ result)) := by
    simpa [stepO] using hfillEnd
  have hrestore := zeroWord_restore_iterate [] query.reverse
    (List.replicate query.length (.bit false) ++ result)
  have hrestoreEnd := zeroWord_step_restore_nil query
    (List.replicate query.length (.bit false) ++ result)
  have hrestoreEnd' : (stepO^[1])
      (some (zeroWordCfg .restore query []
        (List.replicate query.length (.bit false) ++ result))) =
      some (zeroWordCfg .done query []
        (List.replicate query.length (.bit false) ++ result)) := by
    simpa [stepO] using hrestoreEnd
  have chain {r s : ℕ} {x y z : Option zeroWordMachine.Cfg}
      (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by
    rw [Function.iterate_add_apply, hr, hs]
  have hrestore' := hrestore
  simp only [List.reverse_reverse, List.append_nil] at hrestore'
  have hfill' := hfill
  simp only [List.append_nil] at hfill'
  have hrun := chain (chain (chain hfill' hfillEnd') hrestore') hrestoreEnd'
  simp only [List.length_reverse] at hrun
  have hexp : 1 + (query.length + (1 + query.length)) = 2 * query.length + 2 := by
    omega
  rw [hexp] at hrun
  simpa [stepO] using hrun

theorem zeroWord_correct_from (state : ZeroWordControl)
    (query result : List SparseSymbol) :
    ((fun o : Option zeroWordMachine.Cfg => o.bind (TM2.step zeroWordProgram))^[
      2 * query.length + 2])
      (some (zeroWordCfgState .fill state query [] result)) =
    some (zeroWordCfg .done query []
      (List.replicate query.length (.bit false) ++ result)) := by
  rw [show 2 * query.length + 2 = (2 * query.length + 1) + 1 by omega,
    Function.iterate_succ_apply]
  simp only [Option.bind_some, zeroWord_first_step_independent]
  have h := zeroWord_correct query result
  rw [show 2 * query.length + 2 = (2 * query.length + 1) + 1 by omega,
    Function.iterate_succ_apply] at h
  exact h

theorem zeroWord_fixed_correct (w query : ℕ) :
    ((fun o : Option zeroWordMachine.Cfg => o.bind zeroWordMachine.step)^[2 * w + 2])
      (some (zeroWordCfg .fill
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [])) =
    some (zeroWordCfg .done
      ((fixedBits w query).reverse.map SparseSymbol.bit) []
      ((fixedBits w 0).reverse.map SparseSymbol.bit)) := by
  simpa [fixedBits_zero, List.map_replicate, List.reverse_replicate] using
    zeroWord_correct ((fixedBits w query).reverse.map SparseSymbol.bit) []

def zeroWordTypedCfg (label : ZeroWordLabel)
    (query backup result : List SparseSymbol) :
    TM2.Cfg (fun _ : ZeroWordStack => SparseSymbol)
      ZeroWordLabel ZeroWordControl where
  l := some label
  var := default
  stk := zeroWordStacks query backup result

theorem zeroWordTyped_correct (query result : List SparseSymbol) :
    ((fun o : Option (TM2.Cfg (fun _ : ZeroWordStack => SparseSymbol)
      ZeroWordLabel ZeroWordControl) => o.bind (TM2.step zeroWordProgram))^[
        2 * query.length + 2])
      (some (zeroWordTypedCfg .fill query [] result)) =
    some (zeroWordTypedCfg .done query []
      (List.replicate query.length (.bit false) ++ result)) := by
  simpa [zeroWordProgram, zeroWordTypedCfg, zeroWordCfg, zeroWordMachine, Turing.FinTM2.Cfg] using
    zeroWord_correct query result

theorem zeroWordTyped_fixed_correct (w query : ℕ) :
    ((fun o : Option (TM2.Cfg (fun _ : ZeroWordStack => SparseSymbol)
      ZeroWordLabel ZeroWordControl) => o.bind (TM2.step zeroWordProgram))^[
        2 * w + 2])
      (some (zeroWordTypedCfg .fill
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [])) =
    some (zeroWordTypedCfg .done
      ((fixedBits w query).reverse.map SparseSymbol.bit) []
      ((fixedBits w 0).reverse.map SparseSymbol.bit)) := by
  simpa [zeroWordProgram, zeroWordTypedCfg, zeroWordCfg, zeroWordMachine, Turing.FinTM2.Cfg] using
    zeroWord_fixed_correct w query

end Lax51Proofs.RamToTM

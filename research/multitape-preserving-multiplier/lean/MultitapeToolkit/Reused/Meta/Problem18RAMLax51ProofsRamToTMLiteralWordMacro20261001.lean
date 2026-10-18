import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMZeroWordMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure LiteralWordControl (n : ℕ) where
  held : Option SparseSymbol
  remaining : Fin (n + 1)
  deriving DecidableEq, Fintype

def LiteralWordControl.initial (n : ℕ) : LiteralWordControl n :=
  ⟨none, ⟨n, Nat.lt_succ_self n⟩⟩

def LiteralWordControl.advance {n : ℕ}
    (s : LiteralWordControl n) : LiteralWordControl n :=
  ⟨none, ⟨s.remaining.val.div2,
    lt_of_le_of_lt (Nat.div_le_self _ _) s.remaining.isLt⟩⟩

inductive LiteralWordStack | query | backup | result
  deriving DecidableEq, Fintype, Inhabited

inductive LiteralWordLabel | emit | restore | done
  deriving DecidableEq, Fintype, Inhabited

def literalWordMachine (n : ℕ) : Turing.FinTM2 where
  K := LiteralWordStack
  k₀ := .query
  k₁ := .result
  Γ _ := SparseSymbol
  Λ := LiteralWordLabel
  main := .emit
  σ := LiteralWordControl n
  initialState := LiteralWordControl.initial n
  m
    | .emit =>
        .pop .query (fun s a => { s with held := a }) <|
          .branch (fun s => s.held.isNone)
            (.load (fun s => { s with held := none }) <| .goto fun _ => .restore)
            (.push .backup (fun s => s.held.getD (.bit false)) <|
              .push .result (fun s => .bit s.remaining.val.bodd) <|
                .load LiteralWordControl.advance <| .goto fun _ => .emit)
    | .restore =>
        .pop .backup (fun s a => { s with held := a }) <|
          .branch (fun s => s.held.isNone)
            (.load (fun s => { s with held := none }) <| .goto fun _ => .done)
            (.push .query (fun s => s.held.getD (.bit false)) <|
              .load (fun s => { s with held := none }) <| .goto fun _ => .restore)
    | .done => .halt

def literalWordStacks (query backup result : List SparseSymbol) :
    LiteralWordStack → List SparseSymbol
  | .query => query
  | .backup => backup
  | .result => result

def literalWordCfg (n : ℕ) (label : LiteralWordLabel) (remaining : Fin (n + 1))
    (query backup result : List SparseSymbol) : (literalWordMachine n).Cfg where
  l := some label
  var := ⟨none, remaining⟩
  stk := literalWordStacks query backup result

@[simp] theorem literalWord_step_emit_nil (n : ℕ) (remaining : Fin (n + 1))
    (backup result : List SparseSymbol) :
    (literalWordMachine n).step
      (literalWordCfg n .emit remaining [] backup result) =
    some (literalWordCfg n .restore remaining [] backup result) := by
  simp [literalWordMachine, literalWordCfg, literalWordStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem literalWord_step_emit_cons (n : ℕ) (remaining : Fin (n + 1))
    (a : SparseSymbol) (query backup result : List SparseSymbol) :
    (literalWordMachine n).step
      (literalWordCfg n .emit remaining (a :: query) backup result) =
    some (literalWordCfg n .emit
      ⟨remaining.val.div2,
        lt_of_le_of_lt (Nat.div_le_self _ _) remaining.isLt⟩
      query (a :: backup) (.bit remaining.val.bodd :: result)) := by
  simp [literalWordMachine, LiteralWordControl.advance, literalWordCfg,
    literalWordStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem literalWord_step_restore_nil (n : ℕ) (remaining : Fin (n + 1))
    (query result : List SparseSymbol) :
    (literalWordMachine n).step
      (literalWordCfg n .restore remaining query [] result) =
    some (literalWordCfg n .done remaining query [] result) := by
  simp [literalWordMachine, literalWordCfg, literalWordStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem literalWord_step_restore_cons (n : ℕ) (remaining : Fin (n + 1))
    (a : SparseSymbol) (query backup result : List SparseSymbol) :
    (literalWordMachine n).step
      (literalWordCfg n .restore remaining query (a :: backup) result) =
    some (literalWordCfg n .restore remaining (a :: query) backup result) := by
  simp [literalWordMachine, literalWordCfg, literalWordStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem literalWord_emit_iterate (n : ℕ) (remaining : Fin (n + 1))
    (query backup result : List SparseSymbol) :
    ((fun o : Option (literalWordMachine n).Cfg => o.bind (literalWordMachine n).step)^[
      query.length])
      (some (literalWordCfg n .emit remaining query backup result)) =
    some (literalWordCfg n .emit
      ⟨remaining.val / 2 ^ query.length, by
        exact lt_of_le_of_lt (Nat.div_le_self _ _) remaining.isLt⟩
      [] (query.reverse ++ backup)
      ((fixedBits query.length remaining.val).reverse.map SparseSymbol.bit ++ result)) := by
  induction query generalizing remaining backup result with
  | nil =>
      simp [literalWordCfg, fixedBits]
  | cons a query ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, literalWord_step_emit_cons]
      rw [ih]
      congr 2
      · apply Fin.ext
        simp only [Nat.div2_val, Nat.div_div_eq_div_mul, pow_succ]
        rw [Nat.mul_comm]
      · simp [List.reverse_cons, List.append_assoc]
      · simp [fixedBits, List.map_reverse, List.append_assoc]

theorem literalWord_restore_iterate (n : ℕ) (remaining : Fin (n + 1))
    (query backup result : List SparseSymbol) :
    ((fun o : Option (literalWordMachine n).Cfg => o.bind (literalWordMachine n).step)^[
      backup.length])
      (some (literalWordCfg n .restore remaining query backup result)) =
    some (literalWordCfg n .restore remaining (backup.reverse ++ query) [] result) := by
  induction backup generalizing query with
  | nil => rfl
  | cons a backup ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, literalWord_step_restore_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem literalWord_correct_exact (n : ℕ) (query result : List SparseSymbol) :
    ((fun o : Option (literalWordMachine n).Cfg =>
        o.bind (literalWordMachine n).step)^[2 * query.length + 2])
      (some (literalWordCfg n .emit ⟨n, Nat.lt_succ_self n⟩ query [] result)) =
    some (literalWordCfg n .done
      ⟨n / 2 ^ query.length,
        lt_of_le_of_lt (Nat.div_le_self _ _) (Nat.lt_succ_self n)⟩
      query []
      ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)) := by
  let stepO := fun o : Option (literalWordMachine n).Cfg =>
    o.bind (literalWordMachine n).step
  let remaining : Fin (n + 1) :=
    ⟨n / 2 ^ query.length, lt_of_le_of_lt (Nat.div_le_self _ _) (Nat.lt_succ_self n)⟩
  have h0 := literalWord_emit_iterate n ⟨n, Nat.lt_succ_self n⟩ query [] result
  have h1raw := literalWord_step_emit_nil n remaining query.reverse
    ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)
  have h1 : (stepO^[1])
      (some (literalWordCfg n .emit remaining [] query.reverse
        ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result))) =
      some (literalWordCfg n .restore remaining [] query.reverse
        ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)) := by
    simpa [stepO] using h1raw
  have h2 := literalWord_restore_iterate n remaining [] query.reverse
    ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)
  have h2' := h2
  simp only [List.reverse_reverse, List.append_nil] at h2'
  have h3raw := literalWord_step_restore_nil n remaining query
    ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)
  have h3 : (stepO^[1])
      (some (literalWordCfg n .restore remaining query []
        ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result))) =
      some (literalWordCfg n .done remaining query []
        ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)) := by
    simpa [stepO] using h3raw
  have h0' := h0
  simp only [List.append_nil] at h0'
  have chain {r s : ℕ} {x y z : Option (literalWordMachine n).Cfg}
      (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by
    rw [Function.iterate_add_apply, hr, hs]
  have hrun := chain (chain (chain h0' h1) h2') h3
  simp only [List.length_reverse] at hrun
  have hexp : 1 + (query.length + (1 + query.length)) = 2 * query.length + 2 := by
    omega
  rw [hexp] at hrun
  simpa [stepO, remaining] using hrun

theorem literalWord_correct (n : ℕ) (query result : List SparseSymbol) :
    ∃ remaining : Fin (n + 1),
      ((fun o : Option (literalWordMachine n).Cfg =>
          o.bind (literalWordMachine n).step)^[2 * query.length + 2])
        (some (literalWordCfg n .emit ⟨n, Nat.lt_succ_self n⟩ query [] result)) =
      some (literalWordCfg n .done remaining query []
        ((fixedBits query.length n).reverse.map SparseSymbol.bit ++ result)) := by
  exact ⟨_, literalWord_correct_exact n query result⟩

/-- The finite-control residue left by literal generation records precisely
whether the program literal fitted in the dynamic word width. -/
theorem literalWord_remaining_eq_zero_iff (n w : ℕ) :
    n / 2 ^ w = 0 ↔ n < 2 ^ w := by
  exact Nat.div_eq_zero_iff_lt (by positivity)

theorem literalWord_fixed_correct (n w query : ℕ) :
    ∃ remaining : Fin (n + 1),
      ((fun o : Option (literalWordMachine n).Cfg =>
          o.bind (literalWordMachine n).step)^[2 * w + 2])
        (some (literalWordCfg n .emit ⟨n, Nat.lt_succ_self n⟩
          ((fixedBits w query).reverse.map SparseSymbol.bit) [] [])) =
      some (literalWordCfg n .done remaining
        ((fixedBits w query).reverse.map SparseSymbol.bit) []
        ((fixedBits w n).reverse.map SparseSymbol.bit)) := by
  simpa using literalWord_correct n
    ((fixedBits w query).reverse.map SparseSymbol.bit) []

end Lax51Proofs.RamToTM

import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMOperandSemantics20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-! Exact embedding of a finite-stack TM statement into the left summands of
larger stack and label types.  Local control is paired with arbitrary ambient
control.  This is the composition lemma used to reuse the verified arithmetic
and memory macros inside the RAM interpreter. -/

def liftLeftStmt {α K Kx Λ Λx σ τ : Type} [DecidableEq K]
    [DecidableEq (Sum K Kx)] :
    TM2.Stmt (fun _ : K => α) Λ σ →
      TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ)
  | .push k f q => .push (.inl k) (fun s => f s.1) (liftLeftStmt q)
  | .peek k f q => .peek (.inl k)
      (fun s a => (f s.1 a, s.2)) (liftLeftStmt q)
  | .pop k f q => .pop (.inl k)
      (fun s a => (f s.1 a, s.2)) (liftLeftStmt q)
  | .load f q => .load (fun s => (f s.1, s.2)) (liftLeftStmt q)
  | .branch f q₁ q₂ => .branch (fun s => f s.1)
      (liftLeftStmt q₁) (liftLeftStmt q₂)
  | .goto f => .goto (fun s => .inl (f s.1))
  | .halt => .halt

def sumStacks {α K Kx : Type} (left : K → List α) (right : Kx → List α) :
    Sum K Kx → List α
  | .inl k => left k
  | .inr k => right k

def embedLeftCfg {α K Kx Λ Λx σ τ : Type}
    (c : TM2.Cfg (fun _ : K => α) Λ σ) (ambient : τ)
    (right : Kx → List α) : TM2.Cfg (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ) where
  l := c.l.map Sum.inl
  var := (c.var, ambient)
  stk := sumStacks c.stk right

theorem update_sumStacks_inl {α K Kx : Type} [DecidableEq K]
    [DecidableEq (Sum K Kx)] (left : K → List α) (right : Kx → List α)
    (k : K) (xs : List α) :
    Function.update (sumStacks left right) (.inl k) xs =
      sumStacks (Function.update left k xs) right := by
  funext j
  cases j with
  | inl j =>
      by_cases h : j = k
      · subst j; simp [sumStacks]
      · have h' : Sum.inl j ≠ (Sum.inl k : Sum K Kx) := by simp [h]
        simp [sumStacks, h, h']
  | inr j =>
      have h : Sum.inr j ≠ (Sum.inl k : Sum K Kx) := by simp
      simp [sumStacks, h]

theorem stepAux_liftLeftStmt {α K Kx Λ Λx σ τ : Type}
    [DecidableEq K] [DecidableEq (Sum K Kx)]
    (q : TM2.Stmt (fun _ : K => α) Λ σ) (v : σ) (ambient : τ)
    (left : K → List α) (right : Kx → List α) :
    TM2.stepAux (liftLeftStmt (Kx := Kx) (Λx := Λx) (τ := τ) q)
        (v, ambient) (sumStacks left right) =
      embedLeftCfg (TM2.stepAux q v left) ambient right := by
  induction q generalizing v left with
  | push k f q ih =>
      simp only [liftLeftStmt, TM2.stepAux]
      rw [update_sumStacks_inl]
      exact ih v (Function.update left k (f v :: left k))
  | peek k f q ih =>
      simp only [liftLeftStmt, TM2.stepAux, sumStacks]
      exact ih (f v (left k).head?) left
  | pop k f q ih =>
      simp only [liftLeftStmt, TM2.stepAux, sumStacks]
      rw [update_sumStacks_inl]
      exact ih (f v (left k).head?) (Function.update left k (left k).tail)
  | load f q ih =>
      simp only [liftLeftStmt, TM2.stepAux]
      exact ih (f v) left
  | branch f q₁ q₂ ih₁ ih₂ =>
      simp only [liftLeftStmt, TM2.stepAux]
      cases h : f v <;> simp [h]
      · exact ih₂ v left
      · exact ih₁ v left
  | goto f => rfl
  | halt => rfl

def liftLeftProgram {α K Kx Λ Λx σ τ : Type} [DecidableEq K]
    [DecidableEq (Sum K Kx)]
    (left : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (right : Λx → TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ)) :
    Sum Λ Λx → TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ)
  | .inl l => liftLeftStmt (Kx := Kx) (Λx := Λx) (τ := τ) (left l)
  | .inr l => right l

theorem step_liftLeftProgram_embed {α K Kx Λ Λx σ τ : Type}
    [DecidableEq K] [DecidableEq (Sum K Kx)]
    (left : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (rightProgram : Λx →
      TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ))
    (c : TM2.Cfg (fun _ : K => α) Λ σ) (ambient : τ)
    (rightStacks : Kx → List α) :
    TM2.step (liftLeftProgram left rightProgram)
        (embedLeftCfg c ambient rightStacks) =
      (TM2.step left c).map
        (fun c' => embedLeftCfg c' ambient rightStacks) := by
  cases c with
  | mk label v stk =>
      cases label with
      | none => rfl
      | some label =>
          simp only [embedLeftCfg, Option.map_some, TM2.step, liftLeftProgram,
            Option.map_some]
          rw [stepAux_liftLeftStmt]
          rfl

def embedLeftOption {α K Kx Λ Λx σ τ : Type}
    (c : Option (TM2.Cfg (fun _ : K => α) Λ σ)) (ambient : τ)
    (rightStacks : Kx → List α) :
    Option (TM2.Cfg (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ)) :=
  c.map (fun c' => embedLeftCfg c' ambient rightStacks)

theorem iterate_optionBind_none {α : Type} (f : α → Option α) (n : ℕ) :
    ((fun o : Option α => o.bind f)^[n]) none = none := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [Function.iterate_succ_apply]
      exact ih

theorem iterate_liftLeftProgram_embed {α K Kx Λ Λx σ τ : Type}
    [DecidableEq K] [DecidableEq (Sum K Kx)]
    (left : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (rightProgram : Λx →
      TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ))
    (n : ℕ) (c : TM2.Cfg (fun _ : K => α) Λ σ) (ambient : τ)
    (rightStacks : Kx → List α) :
    ((fun o => o.bind (TM2.step (liftLeftProgram left rightProgram)))^[n])
        (some (embedLeftCfg c ambient rightStacks)) =
      embedLeftOption
        (((fun o => o.bind (TM2.step left))^[n]) (some c))
        ambient rightStacks := by
  induction n generalizing c with
  | zero => rfl
  | succ n ih =>
      rw [Function.iterate_succ_apply, Function.iterate_succ_apply]
      simp only [Option.bind_some, step_liftLeftProgram_embed]
      cases h : TM2.step left c with
      | none =>
          simp only [Option.map_none, embedLeftOption]
          rw [iterate_optionBind_none, iterate_optionBind_none]
          rfl
      | some c' =>
          simp only [h, Option.map_some, Option.bind_some]
          exact ih c'

theorem transport_iterate_liftLeftProgram {α K Kx Λ Λx σ τ : Type}
    [DecidableEq K] [DecidableEq (Sum K Kx)]
    (left : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (rightProgram : Λx →
      TM2.Stmt (fun _ : Sum K Kx => α) (Sum Λ Λx) (σ × τ))
    {n : ℕ} {c d : TM2.Cfg (fun _ : K => α) Λ σ}
    (h : ((fun o => o.bind (TM2.step left))^[n]) (some c) = some d)
    (ambient : τ) (rightStacks : Kx → List α) :
    ((fun o => o.bind (TM2.step (liftLeftProgram left rightProgram)))^[n])
        (some (embedLeftCfg c ambient rightStacks)) =
      some (embedLeftCfg d ambient rightStacks) := by
  rw [iterate_liftLeftProgram_embed]
  simp [h, embedLeftOption]

end Lax51Proofs.RamToTM

import Std

/- Source-extracted Mathlib definitions. Context is restricted to Type,
   exactly the universes of FinTM2. verify.py checks each definition body
   against the pinned sources; this file does not import all of Mathlib. -/
namespace Model
variable {K : Type} {Γ : K → Type} {Λ σ : Type}

def update {α : Type} {β : α → Type} [DecidableEq α]
    (f : ∀ a, β a) (a' : α) (v : β a') (a : α) : β a :=
  if h : a = a' then Eq.ndrec v h.symm else f a

inductive Stmt (Γ : K → Type) (Λ σ : Type)
  | push : ∀ k, (σ → Γ k) → Stmt Γ Λ σ → Stmt Γ Λ σ
  | peek : ∀ k, (σ → Option (Γ k) → σ) → Stmt Γ Λ σ → Stmt Γ Λ σ
  | pop : ∀ k, (σ → Option (Γ k) → σ) → Stmt Γ Λ σ → Stmt Γ Λ σ
  | load : (σ → σ) → Stmt Γ Λ σ → Stmt Γ Λ σ
  | branch : (σ → Bool) → Stmt Γ Λ σ → Stmt Γ Λ σ → Stmt Γ Λ σ
  | goto : (σ → Λ) → Stmt Γ Λ σ
  | halt : Stmt Γ Λ σ

open Stmt

structure Cfg (Γ : K → Type) (Λ σ : Type) where
  l : Option Λ
  var : σ
  stk : ∀ k, List (Γ k)

variable [DecidableEq K]

def stepAux : Stmt Γ Λ σ → σ → (∀ k, List (Γ k)) → Cfg Γ Λ σ
  | push k f q, v, S => stepAux q v (update S k (f v :: S k))
  | peek k f q, v, S => stepAux q (f v (S k).head?) S
  | pop k f q, v, S => stepAux q (f v (S k).head?) (update S k (S k).tail)
  | load a q, v, S => stepAux q (a v) S
  | branch f q₁ q₂, v, S => cond (f v) (stepAux q₁ v S) (stepAux q₂ v S)
  | goto f, v, S => ⟨some (f v), v, S⟩
  | halt, v, S => ⟨none, v, S⟩

def step (M : Λ → Stmt Γ Λ σ) : Cfg Γ Λ σ → Option (Cfg Γ Λ σ)
  | ⟨none, _, _⟩ => none
  | ⟨some l, v, S⟩ => some (stepAux (M l) v S)

end Model

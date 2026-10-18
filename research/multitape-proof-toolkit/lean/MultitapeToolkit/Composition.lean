import MultitapeToolkit.Model
import Mathlib.Data.Fintype.Sum

/-!
# Sequential composition with an explicit unit-cost handoff

Both machines use the same fixed tape indices and alphabet. Control is their
finite disjoint sum. Successful source transitions are reproduced exactly.
When the first component halts, one non-writing stationary transition enters
the second component at its fixed entry state. The second component's halt
is the halt of the composite. Tapes and head positions are never reset for free.
-/

set_option autoImplicit false

namespace MultitapeToolkit

variable {ι Γ Q₁ Q₂ : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q₁] [Fintype Q₂]

/-- A handoff changes finite control without writing or moving any tape. -/
def handoffAction : Action Γ := ⟨none, .stay⟩

@[simp] theorem act_handoffAction (t : Turing.Tape Γ) : act handoffAction t = t := rfl

/-- Enter the first summand, preserving the entire tape configuration. -/
def leftCfg (c : Config ι Γ Q₁) : Config ι Γ (Q₁ ⊕ Q₂) :=
  ⟨.inl c.state, c.tapes⟩

/-- Enter the second summand, preserving the entire tape configuration. -/
def rightCfg (c : Config ι Γ Q₂) : Config ι Γ (Q₁ ⊕ Q₂) :=
  ⟨.inr c.state, c.tapes⟩

@[simp] theorem leftCfg_tapes (c : Config ι Γ Q₁) :
    (leftCfg (Q₂ := Q₂) c).tapes = c.tapes := rfl

@[simp] theorem rightCfg_tapes (c : Config ι Γ Q₂) :
    (rightCfg (Q₁ := Q₁) c).tapes = c.tapes := rfl

/-- Sequential finite-control composition. The only administrative cost is one handoff. -/
def compose (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂) :
    Machine ι Γ (Q₁ ⊕ Q₂) where
  transition
    | .inl q, heads =>
      match A.transition q heads with
      | none => some (.inr entryB, fun _ => handoffAction)
      | some (q', actions) => some (.inl q', actions)
    | .inr q, heads => (B.transition q heads).map fun p => (.inr p.1, p.2)

/-- Every successful first-component transition is simulated by exactly one transition. -/
theorem compose_step_left (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    {c d : Config ι Γ Q₁} (h : step A c = some d) :
    step (compose A B entryB) (leftCfg c) = some (leftCfg d) := by
  cases ht : A.transition c.state (fun i => (c.tapes i).head) with
  | none => simp [step, ht] at h
  | some p =>
    have hd : d = ⟨p.1, fun i => act (p.2 i) (c.tapes i)⟩ := by
      simpa [step, ht] using h.symm
    subst d
    cases p
    simp [step, compose, leftCfg, ht]

/-- The second component is simulated exactly, including its genuine halting test. -/
theorem compose_step_right (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    (c : Config ι Γ Q₂) :
    step (compose A B entryB) (rightCfg c) = (step B c).map rightCfg := by
  cases ht : B.transition c.state (fun i => (c.tapes i).head) with
  | none => simp [step, compose, rightCfg, ht]
  | some p => simp [step, compose, rightCfg, ht]

/-- A first-component halt triggers exactly one handoff with every tape preserved. -/
theorem compose_handoff (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    (d : Config ι Γ Q₁) (h : Halts A d) :
    step (compose A B entryB) (leftCfg d) =
      some (rightCfg ⟨entryB, d.tapes⟩) := by
  have ht : A.transition d.state (fun i => (d.tapes i).head) = none := by
    cases h' : A.transition d.state (fun i => (d.tapes i).head) with
    | none => rfl
    | some p => simp [Halts, step, h'] at h
  simp [step, compose, leftCfg, rightCfg, ht]

/-- First-component executions preserve their exact transition counts. -/
theorem compose_runs_left (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    {n : Nat} {c d : Config ι Γ Q₁} (h : Runs A n c d) :
    Runs (compose A B entryB) n (leftCfg c) (leftCfg d) := by
  induction h with
  | refl c => exact .refl _
  | cons hs hr ih => exact .cons (compose_step_left A B entryB hs) ih

/-- Second-component executions preserve their exact transition counts. -/
theorem compose_runs_right (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    {n : Nat} {c d : Config ι Γ Q₂} (h : Runs B n c d) :
    Runs (compose A B entryB) n (rightCfg c) (rightCfg d) := by
  induction h with
  | refl c => exact .refl _
  | cons hs hr ih =>
    apply Runs.cons _ ih
    rw [compose_step_right, hs]
    rfl

/-- The second component's true halt is precisely a true halt of the composite. -/
theorem compose_halts_right (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    (d : Config ι Γ Q₂) (h : Halts B d) :
    Halts (compose A B entryB) (rightCfg d) := by
  change step B d = none at h
  change step (compose A B entryB) (rightCfg d) = none
  rw [compose_step_right, h]
  rfl

/-- Universal exact-cost sequential execution, with the handoff charged explicitly. -/
theorem compose_runs (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂) (entryB : Q₂)
    {n m : Nat} {c d : Config ι Γ Q₁} {e : Config ι Γ Q₂}
    (hA : Runs A n c d) (hhalt : Halts A d)
    (hB : Runs B m ⟨entryB, d.tapes⟩ e) :
    Runs (compose A B entryB) (n + 1 + m) (leftCfg c) (rightCfg e) :=
  ((compose_runs_left A B entryB hA).trans
    (Runs.one (compose_handoff A B entryB d hhalt))).trans
      (compose_runs_right A B entryB hB)

/-- Actual bounded computations compose, with no hidden tape-interface assumption. -/
theorem compose_computesWithin (A : Machine ι Γ Q₁) (B : Machine ι Γ Q₂)
    (entryB : Q₂) {a b : Nat} {c d : Config ι Γ Q₁} {e : Config ι Γ Q₂}
    (hA : ComputesWithin A a c d)
    (hB : ComputesWithin B b ⟨entryB, d.tapes⟩ e) :
    ComputesWithin (compose A B entryB) (a + 1 + b) (leftCfg c) (rightCfg e) := by
  rcases hA with ⟨⟨n, hn, hrunA⟩, hhaltA⟩
  rcases hB with ⟨⟨m, hm, hrunB⟩, hhaltB⟩
  exact ⟨⟨n + 1 + m, Nat.add_le_add (Nat.add_le_add_right hn 1) hm,
    compose_runs A B entryB hrunA hhaltA hrunB⟩,
    compose_halts_right A B entryB e hhaltB⟩

end MultitapeToolkit



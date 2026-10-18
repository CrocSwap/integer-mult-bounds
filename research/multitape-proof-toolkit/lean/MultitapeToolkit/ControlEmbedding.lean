import MultitapeToolkit.Absolute
import Mathlib.Data.Fintype.Sum

/-!
# Cost-exact finite-control embeddings

A finite subroutine can occupy its own disjoint tag in a common finite control
bank. Every successful transition and true halt is preserved exactly. A tag is
not an unbounded stack or a free interpreter: the resulting local table is
explicit and reads only the tagged state and scanned symbols.
-/

namespace MultitapeToolkit.Absolute.ControlEmbedding

variable {ι Γ Q R : Type*}
  [Fintype ι] [Fintype Γ] [Fintype Q] [Fintype R]

/-- Change only finite control; all physical head and cell data are retained. -/
def taggedCfg (encode : Q → R) (c : Config ι Γ Q) : Config ι Γ R :=
  ⟨encode c.state, c.head, c.cell⟩

/-- An explicit local table on a larger finite control bank. Unused tags halt. -/
def liftProgram (P : Program ι Γ Q) (encode : Q → R)
    (decode : R → Option Q) : Program ι Γ R where
  transition r scanned := (decode r).bind fun q =>
    (P.transition q scanned).map fun p => (encode p.1, p.2)

/-- A left inverse is enough to transfer every successful physical transition. -/
theorem lift_step (P : Program ι Γ Q) (encode : Q → R) (decode : R → Option Q)
    (hdecode : ∀ q, decode (encode q) = some q) (c : Config ι Γ Q) :
    step (liftProgram P encode decode) (taggedCfg encode c) =
      (step P c).map (taggedCfg encode) := by
  simp only [step, liftProgram, taggedCfg, hdecode, Option.bind_some]
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => simp
  | some p => cases p; rfl

/-- A tagged routine has an actual run at precisely its original transition count. -/
theorem lift_runs (P : Program ι Γ Q) (encode : Q → R) (decode : R → Option Q)
    (hdecode : ∀ q, decode (encode q) = some q)
    {n : ℕ} {c d : Config ι Γ Q} (h : Runs P n c d) :
    Runs (liftProgram P encode decode) n (taggedCfg encode c) (taggedCfg encode d) := by
  induction h with
  | refl c => exact .refl _
  | cons hs hr ih =>
    apply Runs.cons (d := taggedCfg encode _)
    · rw [lift_step P encode decode hdecode, hs]
      rfl
    · exact ih

/-- A true component halt remains a true halt in its finite tag. -/
theorem lift_halts (P : Program ι Γ Q) (encode : Q → R) (decode : R → Option Q)
    (hdecode : ∀ q, decode (encode q) = some q) (c : Config ι Γ Q) :
    Halts (liftProgram P encode decode) (taggedCfg encode c) ↔ Halts P c := by
  rw [Halts, lift_step P encode decode hdecode, Halts]
  cases step P c <;> simp

/-- The standard left injection has a concrete partial decoder. -/
def leftDecode : Q ⊕ R → Option Q
  | .inl q => some q
  | .inr _ => none

/-- The standard right injection has a concrete partial decoder. -/
def rightDecode : Q ⊕ R → Option R
  | .inl _ => none
  | .inr r => some r

omit [Fintype Q] [Fintype R] in
@[simp] theorem leftDecode_inl (q : Q) : leftDecode (.inl q : Q ⊕ R) = some q := rfl
omit [Fintype Q] [Fintype R] in
@[simp] theorem rightDecode_inr (r : R) : rightDecode (.inr r : Q ⊕ R) = some r := rfl

end MultitapeToolkit.Absolute.ControlEmbedding
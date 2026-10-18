import MultitapeToolkit.Locality

/-!
# Exact-cost bridge to absolute-coordinate multitape semantics

The numbered model used in integer-multiplication work keeps absolute integer
head coordinates and writes a symbol on every successful transition. This
module supplies that semantics over arbitrary fixed finite types and proves
that the existing head-relative Mathlib-tape machine simulates it with exactly
one transition per transition. An omitted write becomes rewriting the scanned
symbol. No input conversion or fast multiplication algorithm is assumed here.
-/

namespace MultitapeToolkit.Absolute

open Locality

@[ext] structure Config (ι Γ Q : Type*) where
  state : Q
  head : ι → ℤ
  cell : ι → ℤ → Γ

/-- Literal finite local table: read scanned cells, write one symbol, move one unit. -/
structure Program (ι Γ Q : Type*) [Fintype ι] [Fintype Γ] [Fintype Q] where
  transition : Q → (ι → Γ) → Option (Q × (ι → Γ × Move))

variable {ι Γ Q : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- Preserve a no-write action by rewriting its already scanned symbol. -/
def ofMachine (M : Machine ι Γ Q) : Program ι Γ Q where
  transition q scanned := (M.transition q scanned).map fun p =>
    (p.1, fun i => ((p.2 i).write.getD (scanned i), (p.2 i).move))

/-- One literal absolute-coordinate transition; no global tape arithmetic is performed. -/
def step (P : Program ι Γ Q) (c : Config ι Γ Q) : Option (Config ι Γ Q) :=
  (P.transition c.state (fun i => c.cell i (c.head i))).map fun p =>
    { state := p.1
      head := fun i => c.head i + moveOffset (p.2 i).2
      cell := fun i x => if x = c.head i then (p.2 i).1 else c.cell i x }

inductive Runs (P : Program ι Γ Q) : ℕ → Config ι Γ Q → Config ι Γ Q → Prop
  | refl (c) : Runs P 0 c c
  | cons {n c d e} : step P c = some d → Runs P n d e → Runs P (n+1) c e

def Halts (P : Program ι Γ Q) (c : Config ι Γ Q) : Prop := step P c = none

/-- Realize the same physical tape with a chosen absolute head coordinate. -/
def realize (c : MultitapeToolkit.Config ι Γ Q) (heads : ι → ℤ) : Config ι Γ Q :=
  ⟨c.state, heads, fun i x => absoluteCell (c.tapes i) (heads i) x⟩

omit [Fintype ι] [Fintype Γ] [Fintype Q] in
@[simp] theorem realize_scanned (c : MultitapeToolkit.Config ι Γ Q) (heads : ι → ℤ) (i : ι) :
    (realize c heads).cell i ((realize c heads).head i) = (c.tapes i).head := by
  simp [realize, absoluteCell, Turing.Tape.nth_zero]

/-- One successful relative step gives precisely one absolute step with unit head motion. -/
theorem step_simulation (M : Machine ι Γ Q)
    {c d : MultitapeToolkit.Config ι Γ Q}
    (h : MultitapeToolkit.step M c = some d) (heads : ι → ℤ) :
    ∃ heads', step (ofMachine M) (realize c heads) = some (realize d heads') ∧
      ∀ i, (heads' i - heads i).natAbs ≤ 1 := by
  cases ht : M.transition c.state (fun i => (c.tapes i).head) with
  | none => simp [MultitapeToolkit.step, ht] at h
  | some p =>
    rcases p with ⟨q, actions⟩
    have hd : d = ⟨q, fun i => act (actions i) (c.tapes i)⟩ := by
      simpa [MultitapeToolkit.step, ht] using h.symm
    subst d
    refine ⟨fun i => heads i + moveOffset (actions i).move, ?_, ?_⟩
    · have hscan : (fun i => (realize c heads).cell i ((realize c heads).head i)) =
          (fun i => (c.tapes i).head) := funext (realize_scanned c heads)
      simp only [step, ofMachine, realize, absoluteCell, sub_self, Turing.Tape.nth_zero, ht, Option.map_some]
      congr 1
      apply Config.ext
      · rfl
      · rfl
      · funext i x
        exact (act_absoluteCell (actions i) (c.tapes i) (heads i) x).symm
    · intro i
      simpa using moveOffset_unit (actions i).move

/-- Actual finite runs retain exactly their transition count in the literal model. -/
theorem runs_simulation (M : Machine ι Γ Q) {n : ℕ}
    {c d : MultitapeToolkit.Config ι Γ Q}
    (h : MultitapeToolkit.Runs M n c d) (heads : ι → ℤ) :
    ∃ heads', Runs (ofMachine M) n (realize c heads) (realize d heads') := by
  induction h generalizing heads with
  | refl c => exact ⟨heads, .refl _⟩
  | cons hs hr ih =>
    rcases step_simulation M hs heads with ⟨middle, hm, _⟩
    rcases ih middle with ⟨last, hl⟩
    exact ⟨last, .cons hm hl⟩

/-- Halting equivalence does not insert an uncharged final transition. -/
theorem halts_iff (M : Machine ι Γ Q) (c : MultitapeToolkit.Config ι Γ Q) (heads : ι → ℤ) :
    Halts (ofMachine M) (realize c heads) ↔ MultitapeToolkit.Halts M c := by
  have hscan : (fun i => (realize c heads).cell i ((realize c heads).head i)) =
      (fun i => (c.tapes i).head) := funext (realize_scanned c heads)
  simp [Halts, step, ofMachine, MultitapeToolkit.Halts, MultitapeToolkit.step,
    realize, absoluteCell, Turing.Tape.nth_zero]

/-- Every actual bounded completed computation transfers at the identical budget. -/
theorem computesWithin_simulation (M : Machine ι Γ Q) {budget : ℕ}
    {c d : MultitapeToolkit.Config ι Γ Q}
    (h : MultitapeToolkit.ComputesWithin M budget c d) (heads : ι → ℤ) :
    ∃ heads' t, t ≤ budget ∧ Runs (ofMachine M) t (realize c heads) (realize d heads') ∧
      Halts (ofMachine M) (realize d heads') := by
  rcases h with ⟨⟨t, ht, hr⟩, hh⟩
  rcases runs_simulation M hr heads with ⟨last, hl⟩
  exact ⟨last, t, ht, hl, (halts_iff M d last).2 hh⟩

end MultitapeToolkit.Absolute



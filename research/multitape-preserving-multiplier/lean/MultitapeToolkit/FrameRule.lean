import MultitapeToolkit.Trace
import Mathlib.Data.Finset.Card

/-!
# Actual footprints, lockstep simulation, and dirty-region frames

A footprint records precisely the cells scanned by successful literal machine
transitions. It is constructed from an actual run, not guessed from endpoints.
Agreement on those cells suffices for a second configuration to execute the same
trace, even if every other cell contains arbitrary unrelated dirty data.
Sequential handoffs are actual runs and their transition counts are included.
-/

namespace MultitapeToolkit.Absolute.FrameRule

open MultitapeToolkit.Locality

variable {ι Γ Q : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- Exact executions annotated by their finite read/write footprint on each tape. -/
inductive FootprintedRuns (P : Program ι Γ Q) :
    ℕ → Config ι Γ Q → Config ι Γ Q → (ι → Finset ℤ) → Prop
  | refl (c) : FootprintedRuns P 0 c c (fun _ => ∅)
  | cons {n c d e F} : step P c = some d → FootprintedRuns P n d e F →
      FootprintedRuns P (n + 1) c e (fun i => insert (c.head i) (F i))

/-- An annotated trace is an actual execution at exactly the recorded cost. -/
theorem FootprintedRuns.toRuns {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F) :
    Runs P n c d := by
  induction h with
  | refl c => exact .refl c
  | cons hs hr ih => exact .cons hs ih

/-- Every actual execution admits its finite footprint, with no extra hypothesis. -/
theorem footprint_of_runs {P : Program ι Γ Q} {n : ℕ} {c d : Config ι Γ Q}
    (h : Runs P n c d) : ∃ F, FootprintedRuns P n c d F := by
  induction h with
  | refl c => exact ⟨fun _ => ∅, .refl c⟩
  | cons hs hr ih =>
    rcases ih with ⟨F, hF⟩
    exact ⟨_, .cons hs hF⟩

/-- At most one cell per tape is scanned in each actual transition. -/
theorem FootprintedRuns.card_le {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F) :
    ∀ i, (F i).card ≤ n := by
  induction h with
  | refl c => intro i; simp
  | @cons n c d e F hs hr ih =>
    intro i
    exact (Finset.card_insert_le _ _).trans (Nat.add_le_add_right (ih i) 1)

/-- Every cell outside the actual footprint preserves its arbitrary initial data. -/
theorem FootprintedRuns.frame {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F) :
    ∀ i x, x ∉ F i → d.cell i x = c.cell i x := by
  induction h with
  | refl c => intro i x _; rfl
  | @cons n c middle final F hs hr ih =>
    intro i x hfar
    have hne : x ≠ c.head i := by
      intro hx
      subst x
      exact hfar (Finset.mem_insert_self _ _)
    have htail : x ∉ F i := fun hx => hfar (Finset.mem_insert_of_mem hx)
    exact (ih i x htail).trans ((Trace.step_frame _ hs).2 i x hne)

/-- Shared finite control/head positions and shared tape data on a chosen region. -/
def MatchesOn (region : ι → Set ℤ) (c d : Config ι Γ Q) : Prop :=
  c.state = d.state ∧ c.head = d.head ∧
    ∀ i x, x ∈ region i → c.cell i x = d.cell i x

/-- A transition table observing equal scanned cells yields an actual lockstep successor. -/
theorem step_lockstep (P : Program ι Γ Q) (region : ι → Set ℤ)
    {c d other : Config ι Γ Q} (hs : step P c = some d)
    (hm : MatchesOn region c other) (hheads : ∀ i, c.head i ∈ region i) :
    ∃ otherNext, step P other = some otherNext ∧ MatchesOn region d otherNext := by
  have hscan : (fun i => other.cell i (other.head i)) =
      (fun i => c.cell i (c.head i)) := by
    funext i
    rw [← hm.2.1]
    exact (hm.2.2 i (c.head i) (hheads i)).symm
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => simp [step, ht] at hs
  | some p =>
    rcases p with ⟨q, actions⟩
    have hd : d =
        { state := q
          head := fun i => c.head i + moveOffset (actions i).2
          cell := fun i x => if x = c.head i then (actions i).1 else c.cell i x } := by
      simpa [step, ht] using hs.symm
    subst d
    let otherNext : Config ι Γ Q :=
      { state := q
        head := fun i => other.head i + moveOffset (actions i).2
        cell := fun i x => if x = other.head i then (actions i).1 else other.cell i x }
    have htable : P.transition other.state (fun i => other.cell i (other.head i)) =
        some (q, actions) := by
      rw [← hm.1, hscan]
      exact ht
    refine ⟨otherNext, by simp [step, htable, otherNext], rfl, ?_, ?_⟩
    · funext i
      change c.head i + moveOffset (actions i).2 = other.head i + moveOffset (actions i).2
      rw [hm.2.1]
    · intro i x hx
      change (if x = c.head i then (actions i).1 else c.cell i x) =
        (if x = other.head i then (actions i).1 else other.cell i x)
      rw [← hm.2.1]
      by_cases hcell : x = c.head i
      · simp [hcell]
      · simp [hcell, hm.2.2 i x hx]

/-- Initial agreement on actual visited cells suffices for a complete lockstep run.
The ambient region can include ancestor data as well as the exact footprint. -/
theorem FootprintedRuns.lockstep {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F)
    (region : ι → Set ℤ) (hcontained : ∀ i x, x ∈ F i → x ∈ region i)
    (other : Config ι Γ Q) (hm : MatchesOn region c other) :
    ∃ otherFinal, FootprintedRuns P n other otherFinal F ∧ MatchesOn region d otherFinal := by
  induction h generalizing other with
  | refl c => exact ⟨other, .refl other, hm⟩
  | @cons n c middle final F hs hr ih =>
    have hheads : ∀ i, c.head i ∈ region i :=
      fun i => hcontained i _ (Finset.mem_insert_self _ _)
    rcases step_lockstep P region hs hm hheads with ⟨otherMiddle, hsOther, hmMiddle⟩
    have htail : ∀ i x, x ∈ F i → x ∈ region i :=
      fun i x hx => hcontained i x (Finset.mem_insert_of_mem hx)
    rcases ih htail otherMiddle hmMiddle with ⟨otherFinal, hrun, hmFinal⟩
    have hfull := FootprintedRuns.cons hsOther hrun
    have heq : (fun i => insert (other.head i) (F i)) =
        (fun i => insert (c.head i) (F i)) := by rw [hm.2.1]
    rw [heq] at hfull
    exact ⟨otherFinal, hfull, hmFinal⟩

/-- Actual sequential executions union their footprints and add all transition costs. -/
theorem FootprintedRuns.compose {P : Program ι Γ Q} {n m : ℕ}
    {c d e : Config ι Γ Q} {F G : ι → Finset ℤ}
    (h : FootprintedRuns P n c d F) (h' : FootprintedRuns P m d e G) :
    FootprintedRuns P (n + m) c e (fun i => F i ∪ G i) := by
  induction h with
  | refl c => simpa using h'
  | @cons n c d e F hs hr ih =>
    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, Finset.insert_union] using
      FootprintedRuns.cons hs (ih h')

/-- A handoff is itself an actual charged computation; protected dirty data survive all stages. -/
theorem charged_handoff_frame {P : Program ι Γ Q} {n k m : ℕ}
    {c d e final : Config ι Γ Q} {F H G : ι → Finset ℤ}
    (first : FootprintedRuns P n c d F) (handoff : FootprintedRuns P k d e H)
    (second : FootprintedRuns P m e final G) :
    FootprintedRuns P (n + k + m) c final (fun i => (F i ∪ H i) ∪ G i) ∧
      ∀ i x, x ∉ (F i ∪ H i) ∪ G i → final.cell i x = c.cell i x := by
  have h := (first.compose handoff).compose second
  exact ⟨h, h.frame⟩

/-- Every actual run supplies a finite sufficient frame for all alternative dirty configurations. -/
theorem runs_finite_frame_simulation {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} (h : Runs P n c d) :
    ∃ F : ι → Finset ℤ,
      (∀ i, (F i).card ≤ n) ∧
      (∀ i x, x ∉ F i → d.cell i x = c.cell i x) ∧
      ∀ other, MatchesOn (fun i => (F i : Set ℤ)) c other →
        ∃ otherFinal, Runs P n other otherFinal ∧
          MatchesOn (fun i => (F i : Set ℤ)) d otherFinal ∧
          ∀ i x, x ∉ F i → otherFinal.cell i x = other.cell i x := by
  rcases footprint_of_runs h with ⟨F, hF⟩
  refine ⟨F, hF.card_le, hF.frame, ?_⟩
  intro other hm
  rcases hF.lockstep (fun i => (F i : Set ℤ)) (fun _ _ hx => hx) other hm with
    ⟨otherFinal, hOther, hmFinal⟩
  exact ⟨otherFinal, hOther.toRuns, hmFinal, hOther.frame⟩

/-- Equal terminal observations preserve an actual halting decision. -/
theorem halts_lockstep (P : Program ι Γ Q) (region : ι → Set ℤ)
    {c other : Config ι Γ Q} (hh : Halts P c) (hm : MatchesOn region c other)
    (hheads : ∀ i, c.head i ∈ region i) : Halts P other := by
  have hscan : (fun i => other.cell i (other.head i)) =
      (fun i => c.cell i (c.head i)) := by
    funext i
    rw [← hm.2.1]
    exact (hm.2.2 i (c.head i) (hheads i)).symm
  have htable : P.transition c.state (fun i => c.cell i (c.head i)) = none := by
    simpa [Halts, step] using hh
  have hother : P.transition other.state (fun i => other.cell i (other.head i)) = none := by
    rw [← hm.1, hscan]
    exact htable
  simp [Halts, step, hother]

/-- Terminal read agreement gives a completed lockstep computation at the same charged cost. -/
theorem FootprintedRuns.completed_lockstep {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F)
    (region : ι → Set ℤ) (hcontained : ∀ i x, x ∈ F i → x ∈ region i)
    (hterminal : ∀ i, d.head i ∈ region i) (hh : Halts P d)
    (other : Config ι Γ Q) (hm : MatchesOn region c other) :
    ∃ otherFinal, FootprintedRuns P n other otherFinal F ∧
      Halts P otherFinal ∧ MatchesOn region d otherFinal := by
  rcases h.lockstep region hcontained other hm with ⟨otherFinal, hOther, hmFinal⟩
  exact ⟨otherFinal, hOther, halts_lockstep P region hh hmFinal hterminal, hmFinal⟩

/-- Every actual completed run has a finite sufficient observation frame, including
its terminal halt decision, for all configurations with arbitrary outside data. -/
theorem completed_runs_finite_frame {P : Program ι Γ Q} {n : ℕ}
    {c d : Config ι Γ Q} (h : Runs P n c d) (hh : Halts P d) :
    ∃ S : ι → Finset ℤ,
      (∀ i, (S i).card ≤ n + 1) ∧
      (∀ i x, x ∉ S i → d.cell i x = c.cell i x) ∧
      ∀ other, MatchesOn (fun i => (S i : Set ℤ)) c other →
        ∃ otherFinal, Runs P n other otherFinal ∧ Halts P otherFinal ∧
          MatchesOn (fun i => (S i : Set ℤ)) d otherFinal ∧
          ∀ i x, x ∉ S i → otherFinal.cell i x = other.cell i x := by
  rcases footprint_of_runs h with ⟨F, hF⟩
  let S : ι → Finset ℤ := fun i => insert (d.head i) (F i)
  have hsub : ∀ i x, x ∈ F i → x ∈ (S i : Set ℤ) :=
    fun i x hx => Finset.mem_insert_of_mem hx
  have houtside : ∀ i x, x ∉ S i → x ∉ F i :=
    fun i x hx hmem => hx (Finset.mem_insert_of_mem hmem)
  refine ⟨S, ?_, ?_, ?_⟩
  · intro i
    exact (Finset.card_insert_le _ _).trans (Nat.add_le_add_right (hF.card_le i) 1)
  · intro i x hx
    exact hF.frame i x (houtside i x hx)
  · intro other hm
    rcases hF.completed_lockstep (fun i => (S i : Set ℤ)) hsub
      (fun i => Finset.mem_insert_self _ _) hh other hm with
      ⟨otherFinal, hOther, hhOther, hmFinal⟩
    exact ⟨otherFinal, hOther.toRuns, hhOther, hmFinal,
      fun i x hx => hOther.frame i x (houtside i x hx)⟩

end MultitapeToolkit.Absolute.FrameRule



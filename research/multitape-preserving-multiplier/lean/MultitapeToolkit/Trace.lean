import MultitapeToolkit.Absolute
import Lean.Elab.Tactic.Omega

/-!
# Universal tape frames for exact physical runs

In `n` actual transitions a tape head moves at most `n` cells. Because each
transition writes before moving, every cell at distance at least `n` from the
initial head remains unchanged. These laws protect arbitrary pre-existing
ancestor regions and compose over actual executions, with no assumed oracle.
-/

namespace MultitapeToolkit.Absolute.Trace

open MultitapeToolkit.Locality

variable {ι Γ Q : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- Integer head distance satisfies the triangle inequality. -/
theorem head_distance_triangle (a b c : ℤ) :
    (a - c).natAbs ≤ (a - b).natAbs + (b - c).natAbs := by
  have h := Int.natAbs_add_le (a - b) (b - c)
  have he : (a - b) + (b - c) = a - c := by omega
  rwa [he] at h

/-- A successful step moves each head by at most one and preserves every other cell. -/
theorem step_frame (P : Program ι Γ Q) {c d : Config ι Γ Q}
    (h : step P c = some d) :
    (∀ i, (d.head i - c.head i).natAbs ≤ 1) ∧
      ∀ i x, x ≠ c.head i → d.cell i x = c.cell i x := by
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => simp [step, ht] at h
  | some p =>
    rcases p with ⟨q, actions⟩
    have hd : d =
        { state := q
          head := fun i => c.head i + moveOffset (actions i).2
          cell := fun i x => if x = c.head i then (actions i).1 else c.cell i x } := by
      simpa [step, ht] using h.symm
    subst d
    constructor
    · intro i
      simpa using moveOffset_unit (actions i).2
    · intro i x hne
      simp [hne]

/-- Every exact run has bounded head reach and preserves all cells outside its write cone.
The boundary `distance = n` is also preserved since writing precedes head movement. -/
theorem runs_reach_and_frame (P : Program ι Γ Q) {n : ℕ} {c d : Config ι Γ Q}
    (h : Runs P n c d) :
    (∀ i, (d.head i - c.head i).natAbs ≤ n) ∧
      ∀ i x, n ≤ (x - c.head i).natAbs → d.cell i x = c.cell i x := by
  induction h with
  | refl c =>
    constructor
    · intro i; simp
    · intro i x _; rfl
  | @cons n c middle final hs hr ih =>
    rcases step_frame P hs with ⟨hstep, hcell⟩
    constructor
    · intro i
      exact (head_distance_triangle (final.head i) (middle.head i) (c.head i)).trans
        (Nat.add_le_add (ih.1 i) (hstep i))
    · intro i x hfar
      have htriangle : (x - c.head i).natAbs ≤ (x - middle.head i).natAbs + 1 :=
        (head_distance_triangle x (middle.head i) (c.head i)).trans
          (Nat.add_le_add_left (hstep i) _)
      have hmiddle : n ≤ (x - middle.head i).natAbs := by omega
      have hne : x ≠ c.head i := by
        intro heq
        subst x
        simp at hfar
      exact (ih.2 i x hmiddle).trans (hcell i x hne)

/-- A protected region disjoint from the write cone survives the whole computation. -/
theorem runs_preserve_region (P : Program ι Γ Q) {n : ℕ} {c d : Config ι Γ Q}
    (h : Runs P n c d) (region : ι → Set ℤ)
    (hsafe : ∀ i x, x ∈ region i → n ≤ (x - c.head i).natAbs) :
    ∀ i x, x ∈ region i → d.cell i x = c.cell i x := by
  intro i x hx
  exact (runs_reach_and_frame P h).2 i x (hsafe i x hx)

/-- Actual consecutive executions add their transition counts exactly. -/
theorem runs_trans (P : Program ι Γ Q) {n m : ℕ} {c d e : Config ι Γ Q}
    (h : Runs P n c d) (h' : Runs P m d e) : Runs P (n + m) c e := by
  induction h with
  | refl => simpa using h'
  | @cons n c d e hs hr ih =>
    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using Runs.cons hs (ih h')

/-- Sequential computation protects every cell outside the combined write cone. -/
theorem runs_frame_compose (P : Program ι Γ Q) {n m : ℕ} {c d e : Config ι Γ Q}
    (h : Runs P n c d) (h' : Runs P m d e) :
    ∀ i x, n + m ≤ (x - c.head i).natAbs → e.cell i x = c.cell i x :=
  (runs_reach_and_frame P (runs_trans P h h')).2

/-- Every witnessed prefix with at most the budget remains inside its head cone. -/
theorem prefix_heads_within_budget (P : Program ι Γ Q) {k budget : ℕ}
    {c reached : Config ι Γ Q} (h : Runs P k c reached) (hk : k ≤ budget) :
    ∀ i, (reached.head i - c.head i).natAbs ≤ budget := by
  intro i
  exact ((runs_reach_and_frame P h).1 i).trans hk

/-- A concrete table leaves a chosen tape stationary and rewrites its scanned symbol. -/
def IdleOn (P : Program ι Γ Q) (tape : ι) : Prop :=
  ∀ state scanned next actions,
    P.transition state scanned = some (next, actions) →
      (actions tape).2 = Move.stay ∧ (actions tape).1 = scanned tape

/-- A checked idle-table condition preserves the entire chosen tape in one actual step. -/
theorem step_idle_tape (P : Program ι Γ Q) (tape : ι) (hidle : IdleOn P tape)
    {c d : Config ι Γ Q} (h : step P c = some d) :
    d.head tape = c.head tape ∧ ∀ x, d.cell tape x = c.cell tape x := by
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => simp [step, ht] at h
  | some p =>
    rcases p with ⟨q, actions⟩
    have hd : d =
        { state := q
          head := fun i => c.head i + moveOffset (actions i).2
          cell := fun i x => if x = c.head i then (actions i).1 else c.cell i x } := by
      simpa [step, ht] using h.symm
    subst d
    rcases hidle c.state (fun i => c.cell i (c.head i)) q actions ht with ⟨hm, hw⟩
    constructor
    · simp [hm, moveOffset]
    · intro x
      by_cases hx : x = c.head tape
      · simp [hx, hw]
      · simp [hx]

/-- A tape certified idle by the actual finite table survives every exact run. -/
theorem runs_idle_tape (P : Program ι Γ Q) (tape : ι) (hidle : IdleOn P tape)
    {n : ℕ} {c d : Config ι Γ Q} (h : Runs P n c d) :
    d.head tape = c.head tape ∧ ∀ x, d.cell tape x = c.cell tape x := by
  induction h with
  | refl => exact ⟨rfl, fun _ => rfl⟩
  | cons hs hr ih =>
    have hfirst := step_idle_tape P tape hidle hs
    exact ⟨ih.1.trans hfirst.1, fun x => (ih.2 x).trans (hfirst.2 x)⟩

end MultitapeToolkit.Absolute.Trace




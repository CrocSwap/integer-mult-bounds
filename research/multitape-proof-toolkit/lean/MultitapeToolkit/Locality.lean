import MultitapeToolkit.Model
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fintype.Prod
import Mathlib.Data.Fintype.Option
import Lean.Elab.Tactic.Omega

/-!
# Finite transition tables and literal multitape locality

These universal laws apply to the existing finite-control machine, not to an
assumed external simulator. The absolute-coordinate law states that one step
writes only the cell under each old head and moves each head by at most one.
The finite decision table sees precisely the control state and scanned symbols.
-/

namespace MultitapeToolkit.Locality

open Turing

/-- Signed displacement of one elementary head movement. -/
def moveOffset : Move → ℤ
  | .stay => 0
  | .left => -1
  | .right => 1

/-- Every head movement has magnitude at most one cell. -/
theorem moveOffset_unit (m : Move) : (moveOffset m).natAbs ≤ 1 := by
  cases m <;> decide

/-- A head movement only changes which tape coordinate is called zero. -/
theorem moveTape_nth {Γ : Type*} [Inhabited Γ] (m : Move) (t : Tape Γ) (j : ℤ) :
    (moveTape m t).nth j = t.nth (j + moveOffset m) := by
  cases m with
  | stay => simp [moveTape, moveOffset]
  | left => simpa [moveTape, moveOffset, sub_eq_add_neg] using Tape.move_left_nth t j
  | right => exact Tape.move_right_nth t j

/-- A local action shifts coordinates and optionally changes only the old head. -/
theorem act_nth {Γ : Type*} [Inhabited Γ] (a : Action Γ) (t : Tape Γ) (j : ℤ) :
    (act a t).nth j =
      match a.write with
      | none => t.nth (j + moveOffset a.move)
      | some b => if j + moveOffset a.move = 0 then b else t.nth (j + moveOffset a.move) := by
  cases a with
  | mk w m => cases w <;> simp [act, moveTape_nth, Tape.write_nth]

/-- Every cell away from the old scanned position survives a local action. -/
theorem act_preserves_unscanned {Γ : Type*} [Inhabited Γ]
    (a : Action Γ) (t : Tape Γ) (j : ℤ)
    (h : j + moveOffset a.move ≠ 0) :
    (act a t).nth j = t.nth (j + moveOffset a.move) := by
  rw [act_nth]
  cases a.write <;> simp [h]

/-- Place a head-relative Mathlib tape at a particular absolute head coordinate. -/
def absoluteCell {Γ : Type*} [Inhabited Γ] (t : Tape Γ) (head x : ℤ) : Γ :=
  t.nth (x - head)

/-- In absolute coordinates, an action writes at most the old head cell;
all other cells are unchanged, and the new head is `head + moveOffset`. -/
theorem act_absoluteCell {Γ : Type*} [Inhabited Γ]
    (a : Action Γ) (t : Tape Γ) (head x : ℤ) :
    absoluteCell (act a t) (head + moveOffset a.move) x =
      if x = head then a.write.getD t.head else absoluteCell t head x := by
  unfold absoluteCell
  rw [act_nth]
  have hcoordinate : x - (head + moveOffset a.move) + moveOffset a.move = x - head := by
    omega
  rw [hcoordinate]
  cases hwrite : a.write with
  | none =>
    by_cases h : x = head
    · subst x; simp [Tape.nth_zero]
    · simp [h]
  | some b => simp [sub_eq_zero]

/-- There are exactly three available local head movements. -/
instance moveFintype : Fintype Move :=
  ⟨{.stay, .left, .right}, by intro m; cases m <;> simp⟩

@[simp] theorem card_move : Fintype.card Move = 3 := by decide

/-- Finite tape actions consist solely of an optional symbol and unit movement. -/
def actionEquiv (Γ : Type*) : Action Γ ≃ Option Γ × Move where
  toFun a := (a.write, a.move)
  invFun p := ⟨p.1, p.2⟩
  left_inv a := by cases a; rfl
  right_inv p := by cases p; rfl

noncomputable instance actionFintype {Γ : Type*} [Fintype Γ] : Fintype (Action Γ) :=
  Fintype.ofEquiv (Option Γ × Move) (actionEquiv Γ).symm

/-- The number of actions is fixed by the alphabet, independent of the input. -/
theorem card_action (Γ : Type*) [Fintype Γ] :
    Fintype.card (Action Γ) = (Fintype.card Γ + 1) * 3 := by
  rw [Fintype.card_congr (actionEquiv Γ), Fintype.card_prod]
  simp

section Machine

variable {ι Γ Q : Type*} [Inhabited Γ] [Fintype ι] [Fintype Γ] [Fintype Q]

/-- The complete finite observation available to a transition. -/
def observation (c : Config ι Γ Q) : Q × (ι → Γ) :=
  (c.state, fun i => (c.tapes i).head)

/-- Equal state and scanned symbols yield the same transition decision. -/
theorem transition_of_observation_eq (M : Machine ι Γ Q)
    {c d : Config ι Γ Q} (h : observation c = observation d) :
    M.transition c.state (fun i => (c.tapes i).head) =
      M.transition d.state (fun i => (d.tapes i).head) := by
  exact congrArg (fun p : Q × (ι → Γ) => M.transition p.1 p.2) h

/-- A complete finite table for the fixed machine's local transition function. -/
noncomputable def decisionTable (M : Machine ι Γ Q) :
    Finset ((Q × (ι → Γ)) × Option (Q × (ι → Action Γ))) := by
  classical
  exact Finset.univ.image fun o => (o, M.transition o.1 o.2)

/-- Every observation has precisely its actual machine decision in the table. -/
theorem decisionTable_lookup (M : Machine ι Γ Q) (o : Q × (ι → Γ))
    (r : Option (Q × (ι → Action Γ))) :
    (o, r) ∈ decisionTable M ↔ r = M.transition o.1 o.2 := by
  classical
  simp [decisionTable, eq_comm]

/-- Finite-table size is bounded independently of input length and tape contents. -/
theorem decisionTable_card_le (M : Machine ι Γ Q) :
    (decisionTable M).card ≤ Fintype.card Q * Fintype.card Γ ^ Fintype.card ι := by
  classical
  calc
    (decisionTable M).card ≤ (Finset.univ : Finset (Q × (ι → Γ))).card :=
      Finset.card_image_le
    _ = Fintype.card Q * Fintype.card Γ ^ Fintype.card ι := by
      simp [Fintype.card_prod, Fintype.card_fun]

/-- A supplied transition gives precisely its simultaneous local tape actions. -/
theorem step_of_transition (M : Machine ι Γ Q) (c : Config ι Γ Q)
    (q : Q) (actions : ι → Action Γ)
    (h : M.transition c.state (fun i => (c.tapes i).head) = some (q, actions)) :
    step M c = some ⟨q, fun i => act (actions i) (c.tapes i)⟩ := by
  simp [step, h]

/-- Every successful transition satisfies literal local read/write/move laws. -/
theorem step_locality (M : Machine ι Γ Q) {c d : Config ι Γ Q}
    (h : step M c = some d) :
    ∃ q actions,
      M.transition c.state (fun i => (c.tapes i).head) = some (q, actions) ∧
      d.state = q ∧
      (∀ i, (moveOffset (actions i).move).natAbs ≤ 1) ∧
      ∀ (head : ι → ℤ) (i : ι) (x : ℤ),
        absoluteCell (d.tapes i) (head i + moveOffset (actions i).move) x =
          if x = head i then (actions i).write.getD (c.tapes i).head
          else absoluteCell (c.tapes i) (head i) x := by
  cases ht : M.transition c.state (fun i => (c.tapes i).head) with
  | none => simp [step, ht] at h
  | some p =>
    rcases p with ⟨q, actions⟩
    have hd : d = ⟨q, fun i => act (actions i) (c.tapes i)⟩ := by
      exact Option.some.inj ((step_of_transition M c q actions ht).symm.trans h).symm
    subst d
    exact ⟨q, actions, rfl, rfl, fun i => moveOffset_unit _,
      fun head i x => act_absoluteCell (actions i) (c.tapes i) (head i) x⟩

/-- A deterministic machine has only one successor from a given configuration. -/
theorem step_deterministic (M : Machine ι Γ Q) {c d e : Config ι Γ Q}
    (h : step M c = some d) (h' : step M c = some e) : d = e :=
  Option.some.inj (h.symm.trans h')

/-- Exact execution length and starting configuration uniquely determine the result. -/
theorem runs_deterministic (M : Machine ι Γ Q) {n : ℕ} {c d e : Config ι Γ Q}
    (h : Runs M n c d) (h' : Runs M n c e) : d = e := by
  induction h generalizing e with
  | refl => cases h'; rfl
  | @cons n c d final hs hr ih =>
    cases h' with
    | @cons _ _ d' _ hs' hr' =>
      have hd : d = d' := step_deterministic M hs hs'
      subst d'
      exact ih hr'

end Machine

end MultitapeToolkit.Locality



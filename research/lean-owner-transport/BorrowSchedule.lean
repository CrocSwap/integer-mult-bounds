/-
Copyright (c) 2026 Rohan Arun. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
A finite controller certificate for borrowing windows. Positions are one-based;
zero denotes the boundary before the first event. Unknown events conservatively
block every pair on their replica, or every replica if unscoped.
This is a controller trace model, not yet a fixed-tape implementation.
-/
import OwnerSeparation
namespace OwnerTransport.BorrowSchedule
open OwnerTable OwnerSeparation

structure Event where
  replica : Option Nat
  touchedPairs : List Nat
  idleChildren : List Nat
  call : Option (Nat × Nat)
  unknownEffects : Bool
  deriving Inhabited, Repr

structure Trace where
  count : Nat
  event : Nat → Event
  callPosition : Nat → Nat
  bounds : Nat → Nat × Nat

def hits (e : Event) (replica pair : Nat) : Bool :=
  decide (e.replica = some replica ∨ e.replica = none) &&
    (e.unknownEffects || e.touchedPairs.contains pair)

def windowCount (c : Table) : Nat := c.replicas * c.children

def CallFacts (c : Table) (s : Trace) (pair : Nat → Nat) (t : Nat) : Prop :=
  let p := s.callPosition t
  0 < p ∧ p ≤ s.count ∧ (s.event p).call = some ((c.call t).1, t) ∧
    (s.event p).replica = some (c.call t).2 ∧
    (s.event p).touchedPairs = [pair (c.call t).1]

instance (c : Table) (s : Trace) (pair : Nat → Nat) (t : Nat) : Decidable (CallFacts c s pair t) := by
  unfold CallFacts
  infer_instance

def checkCall (c : Table) (s : Trace) (pair : Nat → Nat) (t : Nat) : Bool :=
  decide (CallFacts c s pair t)

def EndpointFacts (c : Table) (s : Trace) (g : Nat) : Prop :=
  let lo := (s.bounds g).1
  let hi := (s.bounds g).2
  let r := g / c.children
  let child := g % c.children
  lo < hi ∧ hi ≤ s.count ∧ (s.event hi).replica = some r ∧
    child ∈ (s.event hi).idleChildren ∧
    (lo = 0 ∨ hits (s.event lo) r (c.lane child / 2) = true)

instance (c : Table) (s : Trace) (g : Nat) : Decidable (EndpointFacts c s g) := by
  unfold EndpointFacts
  infer_instance

/-- Endpoints, an untouched interior, and the exact admitted call set. -/
def WindowFacts (c : Table) (s : Trace) (g : Nat) : Prop :=
  EndpointFacts c s g ∧
  (∀ p, (s.bounds g).1 < p → p < (s.bounds g).2 →
    hits (s.event p) (g / c.children) (c.lane (g % c.children) / 2) = false) ∧
  (∀ t, t ∈ (c.window g).times → t < c.calls ∧
    (s.bounds g).1 < s.callPosition t ∧ s.callPosition t < (s.bounds g).2) ∧
  (∀ t, t < c.calls →
    (t ∈ (c.window g).times ↔ (s.bounds g).1 < s.callPosition t ∧ s.callPosition t < (s.bounds g).2))

def checkWindow (c : Table) (s : Trace) (g : Nat) : Bool :=
  decide (EndpointFacts c s g) &&
  (List.range s.count).all (fun j => decide
    ((s.bounds g).1 < j + 1 ∧ j + 1 < (s.bounds g).2 →
      hits (s.event (j + 1)) (g / c.children) (c.lane (g % c.children) / 2) = false)) &&
  (c.window g).times.all (fun t => decide (t < c.calls ∧
    (s.bounds g).1 < s.callPosition t ∧ s.callPosition t < (s.bounds g).2)) &&
  (List.range c.calls).all (fun t => decide
    (t ∈ (c.window g).times ↔ (s.bounds g).1 < s.callPosition t ∧ s.callPosition t < (s.bounds g).2))

theorem window_sound (c : Table) (s : Trace) (g : Nat) (h : checkWindow c s g = true) :
    WindowFacts c s g := by
  simp only [checkWindow, Bool.and_eq_true] at h
  obtain ⟨⟨⟨hend, hclear⟩, hadmit⟩, hcomplete⟩ := h
  have he := of_decide_eq_true hend
  refine ⟨he, ?_, ?_, ?_⟩
  · intro p hlo hhi
    have hb : (s.bounds g).2 ≤ s.count := he.2.1
    have hr := List.all_eq_true.mp hclear (p - 1) (List.mem_range.mpr (by omega))
    have hp : p - 1 + 1 = p := by omega
    simp only [hp, decide_eq_true_eq] at hr
    exact hr ⟨hlo, hhi⟩
  · intro t ht
    exact of_decide_eq_true (List.all_eq_true.mp hadmit t ht)
  · intro t ht
    exact of_decide_eq_true (List.all_eq_true.mp hcomplete t (List.mem_range.mpr ht))

/-- Child windows of one replica and lane must be separated. -/
def Separate (c : Table) (s : Trace) (g h : Nat) : Prop :=
  g ≠ h → g / c.children = h / c.children →
    c.lane (g % c.children) = c.lane (h % c.children) →
    (s.bounds g).2 ≤ (s.bounds h).1 ∨ (s.bounds h).2 ≤ (s.bounds g).1

instance (c : Table) (s : Trace) (g h : Nat) : Decidable (Separate c s g h) := by
  unfold Separate
  infer_instance

def checkSeparations (c : Table) (s : Trace) (g : Nat) : Bool :=
  (List.range (windowCount c)).all (fun h => decide (Separate c s g h))

def Accepted (c : Table) (s : Trace) (pair : Nat → Nat) : Prop :=
  (∀ t, t < c.calls → checkCall c s pair t = true) ∧
  (∀ g, g < windowCount c → checkWindow c s g = true) ∧
  (∀ g, g < windowCount c → checkSeparations c s g = true)

theorem accepted_call (c : Table) (s : Trace) (pair : Nat → Nat)
    (h : Accepted c s pair) (t : Nat) (ht : t < c.calls) : CallFacts c s pair t :=
  of_decide_eq_true (h.1 t ht)

theorem accepted_window (c : Table) (s : Trace) (pair : Nat → Nat)
    (h : Accepted c s pair) (g : Nat) (hg : g < windowCount c) : WindowFacts c s g :=
  window_sound c s g (h.2.1 g hg)

theorem accepted_separation (c : Table) (s : Trace) (pair : Nat → Nat)
    (h : Accepted c s pair) (g k : Nat) (hg : g < windowCount c) (hk : k < windowCount c) :
    Separate c s g k :=
  of_decide_eq_true (List.all_eq_true.mp (h.2.2 g hg) k (List.mem_range.mpr hk))

/-- A local call touches its active pair in the controller model. -/
theorem call_hits_active_pair (c : Table) (s : Trace) (pair : Nat → Nat) (t : Nat)
    (h : CallFacts c s pair t) : hits (s.event (s.callPosition t)) (c.call t).2 (pair (c.call t).1) = true := by
  obtain ⟨_, _, _, hr, hp⟩ := h
  simp [hits, hr, hp]

/-- Distinct indexed calls cannot occupy the same controller position. -/
theorem call_positions_injective (c : Table) (s : Trace) (pair : Nat → Nat)
    (h : Accepted c s pair) (t u : Nat) (ht : t < c.calls) (hu : u < c.calls)
    (heq : s.callPosition t = s.callPosition u) : t = u := by
  have ha := (accepted_call c s pair h t ht).2.2.1
  have hb := (accepted_call c s pair h u hu).2.2.1
  rw [heq] at ha
  have hp : ((c.call t).1, t) = ((c.call u).1, u) := Option.some.inj (ha.symm.trans hb)
  exact congrArg Prod.snd hp

/-- Controller certification derives the previous declared-window exclusion. -/
theorem windows_avoid_data (c : Table) (s : Trace) (pair : Nat → Nat)
    (h : Accepted c s pair) : WindowsAvoidData c pair := by
  intro r child hr hc t ht
  let g := r * c.children + child
  have hg : g < windowCount c := by
    have hm := Nat.mul_le_mul_right c.children (Nat.succ_le_of_lt hr)
    simp only [Nat.succ_mul] at hm
    unfold g windowCount
    omega
  have hd : g / c.children = r := div_tail _ _ _ hc
  have hmod : g % c.children = child := by
    have hm := Nat.div_add_mod g c.children
    rw [hd] at hm
    unfold g at hm ⊢
    rw [Nat.mul_comm c.children r] at hm
    omega
  have hw := accepted_window c s pair h g hg
  have ha := hw.2.2.1 t ht
  have hf := hw.2.1 (s.callPosition t) ha.2.1 ha.2.2
  rw [hd, hmod] at hf
  by_cases he : (c.call t).2 = r
  · right
    intro hp
    have htouched := call_hits_active_pair c s pair t (accepted_call c s pair h t ha.1)
    rw [he, ← hp, hf] at htouched
    contradiction
  · exact Or.inl he

/-- Helpers admitted by an accepted table execute strictly inside the traced window. -/
theorem helper_inside_window (c : Table) (s : Trace) (pair : Nat → Nat)
    (hs : Accepted c s pair) (hc : OwnerTable.Accepted c) (i : Nat) (hi : i < rowCount c) :
    let g := (c.row i).ownerReplica * c.children + (c.row i).child
    (s.bounds g).1 < s.callPosition (c.row i).time ∧
      s.callPosition (c.row i).time < (s.bounds g).2 := by
  have hr := accepted_row c hc i hi
  simp only [RowValid] at hr
  obtain ⟨_, _, _, _, _, hrep, hchild, _, _, _, _, _, _, _, _, htime⟩ := hr
  have hg : (c.row i).ownerReplica * c.children + (c.row i).child < windowCount c := by
    have hm := Nat.mul_le_mul_right c.children (Nat.succ_le_of_lt hrep)
    simp only [Nat.succ_mul] at hm
    unfold windowCount
    omega
  exact ((accepted_window c s pair hs _ hg).2.2.1 _ htime).2

end OwnerTransport.BorrowSchedule

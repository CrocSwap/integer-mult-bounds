import MultitapeToolkit.MarkedStreams

/-!
Actual footprints of the literal transfer and flip tables stay on or right of
-1. Every spectator scans only its stationary initial head. Thus arbitrary dirty
ancestor data is protected by both the read trace and the resulting frame law.
-/
namespace MultitapeToolkit.Absolute.MarkedStreams
open MultitapeToolkit.Locality MultitapeToolkit.Absolute.FrameRule
variable {ι Q : Type*} [Fintype ι] [DecidableEq ι] [Fintype Q]

/-- A literal table moves right or stays, and preserves the marker when it scans one. -/
def MarkerTable (P : Program ι Symbol Q) (i : ι) : Prop :=
  ∀ q scanned next actions, P.transition q scanned = some (next,actions) →
    scanned i = .separator →
      (actions i).1 = .separator ∧ 0 ≤ moveOffset (actions i).2

def MarkerSafe (c : Config ι Symbol Q) (i : ι) : Prop :=
  -1 ≤ c.head i ∧ c.cell i (-1) = .separator

theorem marker_step (P : Program ι Symbol Q) (i : ι) (ht : MarkerTable P i)
    {c d : Config ι Symbol Q} (hs : step P c = some d) (hc : MarkerSafe c i) :
    MarkerSafe d i := by
  cases htable : P.transition c.state (fun j => c.cell j (c.head j)) with
  | none => simp [step,htable] at hs
  | some p =>
    rcases p with ⟨q,actions⟩
    have hd : d =
        { state := q
          head := fun j => c.head j + moveOffset (actions j).2
          cell := fun j x => if x=c.head j then (actions j).1 else c.cell j x } := by
      simpa [step,htable] using hs.symm
    subst d
    by_cases hm : c.head i = -1
    · have hscan : c.cell i (c.head i) = .separator := by rw [hm]; exact hc.2
      have hact := ht _ _ _ _ htable hscan
      constructor
      · change -1 ≤ c.head i + moveOffset (actions i).2
        rw [hm]; omega
      · change (if (-1:ℤ)=c.head i then (actions i).1 else c.cell i (-1)) = .separator
        simpa [hm] using hact.1
    · have hh : 0 ≤ c.head i := by have h := hc.1; omega
      have ha : -1 ≤ moveOffset (actions i).2 := by cases (actions i).2 <;> simp [moveOffset]
      constructor
      · change -1 ≤ c.head i + moveOffset (actions i).2
        omega
      · change (if (-1:ℤ)=c.head i then (actions i).1 else c.cell i (-1)) = .separator
        simp [Ne.symm hm,hc.2]

/-- Every recorded read, not just the endpoint, respects the marker boundary. -/
theorem footprint_marker_safe {P : Program ι Symbol Q} {n : ℕ}
    {c d : Config ι Symbol Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F)
    (i : ι) (ht : MarkerTable P i) (hc : MarkerSafe c i) :
    MarkerSafe d i ∧ ∀ x ∈ F i, -1 ≤ x := by
  induction h with
  | refl c => exact ⟨hc,by simp⟩
  | @cons n c mid final F hs hr ih =>
    have hmid := marker_step P i ht hs hc
    have htail := ih hmid
    refine ⟨htail.1,?_⟩
    intro x hx
    rcases Finset.mem_insert.mp hx with he|he
    · subst x; exact hc.1
    · exact htail.2 x he

/-- A literally idle tape records only its unchanged head cell. -/
theorem footprint_idle {P : Program ι Symbol Q} {n : ℕ}
    {c d : Config ι Symbol Q} {F : ι → Finset ℤ} (h : FootprintedRuns P n c d F)
    (i : ι) (ht : Trace.IdleOn P i) : ∀ x ∈ F i, x = c.head i := by
  induction h with
  | refl c => simp
  | @cons n c mid final F hs hr ih =>
    intro x hx
    rcases Finset.mem_insert.mp hx with he|he
    · exact he
    · exact (ih x he).trans (Trace.step_idle_tape P i ht hs).1

theorem move_source_marker (s d : ι) : MarkerTable (moveProgram s d) s := by
  intro q scanned next actions ht hsep
  cases q <;> cases hs : scanned s <;> cases hd : scanned d <;>
    simp [moveProgram,hs,hd] at ht
  all_goals rcases ht with ⟨rfl,rfl⟩
  all_goals simp_all [actions2,moveOffset]

theorem move_dest_marker (s d : ι) (hne : s ≠ d) : MarkerTable (moveProgram s d) d := by
  intro q scanned next actions ht hsep
  cases q <;> cases hs : scanned s <;> cases hd : scanned d <;>
    simp [moveProgram,hs,hd] at ht
  all_goals rcases ht with ⟨rfl,rfl⟩
  all_goals simp_all [actions2,moveOffset,Ne.symm hne]

theorem flip_marker (s : ι) : MarkerTable (flipProgram s) s := by
  intro q scanned next actions ht hsep
  cases q <;> cases hs : scanned s <;> simp [flipProgram,hs] at ht
  all_goals rcases ht with ⟨rfl,rfl⟩
  all_goals simp_all [actions1,moveOffset]

theorem move_idle (s d i : ι) (his : i ≠ s) (hid : i ≠ d) : Trace.IdleOn (moveProgram s d) i := by
  intro q scanned next actions ht
  cases q <;> cases hs : scanned s <;> cases hd : scanned d <;>
    simp [moveProgram,hs,hd] at ht
  all_goals rcases ht with ⟨rfl,rfl⟩
  all_goals simp [actions2,his,hid]

theorem flip_idle (s i : ι) (hi : i ≠ s) : Trace.IdleOn (flipProgram s) i := by
  intro q scanned next actions ht
  cases q <;> cases hs : scanned s <;> simp [flipProgram,hs] at ht
  all_goals rcases ht with ⟨rfl,rfl⟩
  all_goals simp [actions1,hi]

/-- Actual exact transfer admits a trace protected from all left ancestor cells. -/
theorem move_footprints (s d : ι) (hne : s ≠ d) (bits : List Bool)
    (sp dp : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    ∃ F, FootprintedRuns (moveProgram s d) (2*bits.length+2)
      (moveInput s d bits sp dp H C) (moveOutput s d bits sp dp H C) F ∧
      (∀ x ∈ F s, -1 ≤ x) ∧ (∀ x ∈ F d, -1 ≤ x) ∧
      (∀ i, i ≠ s → i ≠ d → ∀ x ∈ F i, x=H i) := by
  rcases footprint_of_runs (move_runs s d hne bits sp dp H C) with ⟨F,hF⟩
  have hsafeS : MarkerSafe (moveInput s d bits sp dp H C) s := by
    simp [MarkerSafe,moveInput,bank2,streamTape,TapeData.cell,cellView]
  have hsafeD : MarkerSafe (moveInput s d bits sp dp H C) d := by
    simp [MarkerSafe,moveInput,bank2,streamTape,TapeData.cell,cellView,Ne.symm hne]
  refine ⟨F,hF,(footprint_marker_safe hF s (move_source_marker s d) hsafeS).2,
    (footprint_marker_safe hF d (move_dest_marker s d hne) hsafeD).2,?_⟩
  intro i his hid x hx
  have he := footprint_idle hF i (move_idle s d i his hid) x hx
  simpa [moveInput,bank2,his,hid] using he

/-- The real bit-flip child likewise has an ancestor-free actual trace. -/
theorem flip_footprints (s : ι) (bits : List Bool) (p : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    ∃ F, FootprintedRuns (flipProgram s) (2*bits.length+2)
      (flipInput s bits p H C) (flipOutput s bits p H C) F ∧
      (∀ x ∈ F s, -1 ≤ x) ∧ (∀ i, i ≠ s → ∀ x ∈ F i, x=H i) := by
  rcases footprint_of_runs (flip_runs s bits p H C) with ⟨F,hF⟩
  have hsafe : MarkerSafe (flipInput s bits p H C) s := by
    simp [MarkerSafe,flipInput,bank1,streamTape,TapeData.cell,cellView]
  refine ⟨F,hF,(footprint_marker_safe hF s (flip_marker s) hsafe).2,?_⟩
  intro i hi x hx
  have he := footprint_idle hF i (flip_idle s i hi) x hx
  simpa [flipInput,bank1,hi] using he

end MultitapeToolkit.Absolute.MarkedStreams


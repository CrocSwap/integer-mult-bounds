import MultitapeToolkit.ParkingController
import MultitapeToolkit.MarkerLifecycle

/-!
# A closed physical caller from unmarked buffers

The fixed three-component machine installs its own four stream markers, executes
an actual bit-flip caller, then removes the markers. Both administrative handoffs
are physical transitions. IO and temporary tapes are blank at entry and return;
the inactive stream and arbitrary parking ancestors are restored literally.
-/
namespace MultitapeToolkit.Absolute.CleanBoundary

open scoped BigOperators
open MarkedStreams ParkStack ControlEmbedding Subroutines MarkerLifecycle
open ParkingController

abbrev Payload := Fin 3 ⊕ Control FlipPhase
abbrev MachineState := Fin 3 × Payload

def selected (i : Tapes) : Bool := decide (i ≠ 3)

/-- Clear the four private stream boundary markers, leaving the parking tape. -/
def cleanCells (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) : Tapes → ℤ → Symbol :=
  markerCells selected .blank (homeHeads h) (initialCells x y h past)

/-- A buffer word with its origin at zero and no marker at minus one. -/
def unmarkedWord (bits : List Bool) : ℤ → Symbol :=
  fun j => if j = -1 then .blank else word bits j

private theorem initial_marker (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (i : Tapes) (hi : selected i = true) :
    initialCells x y h past i (homeHeads h i - 1) = .separator := by
  have hin : i ≠ 3 := by simpa [selected] using hi
  fin_cases i <;> simp_all [initialCells,homeHeads,word,markedStream,cellView]

/-- Installation restores exactly the marked interface required by the caller. -/
theorem install_cells (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    markerCells selected .separator (homeHeads h) (cleanCells x y h past) =
      initialCells x y h past := by
  funext i j
  unfold cleanCells
  cases hs : selected i
  · simp [markerCells,hs]
  · by_cases hj : j = homeHeads h i - 1
    · simp [markerCells,hs,hj,initial_marker x y h past i hs]
    · simp [markerCells,hs,hj]

/-- The four selected tapes are actual unmarked words; IO/temp are empty words. -/
theorem clean_streams (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    cleanCells x y h past 0 = unmarkedWord x ∧
    cleanCells x y h past 1 = unmarkedWord y ∧
    cleanCells x y h past 2 = unmarkedWord [] ∧
    cleanCells x y h past 4 = unmarkedWord [] := by
  exact ⟨rfl,rfl,rfl,rfl⟩

/-- A genuinely blank empty buffer includes its minus-one boundary cell. -/
theorem unmarked_empty : unmarkedWord [] = fun _ => Symbol.blank := by
  funext j
  simp [unmarkedWord,word,markedStream,cellView]
  intro hn hj hidx
  exfalso
  omega

/-- Cleanup does not touch the parking tape, including its current separator. -/
theorem clean_parking (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    cleanCells x y h past 3 = parkBase h past := by
  funext j
  simp [cleanCells,markerCells,selected,initialCells]

def components : Fin 3 → Program Tapes Symbol Payload
  | i => match i.val with
    | 0 => liftProgram (markerProgram selected .separator) Sum.inl leftDecode
    | 1 => liftProgram boundaryMachine Sum.inr rightDecode
    | _ => liftProgram (markerProgram selected .blank) Sum.inl leftDecode

def componentEntry : Fin 3 → Payload
  | i => if i = 1 then .inr (boundaryInput [] [] 0 ParkStack.clean).state else .inl 0

/-- One fixed table; no lengths or ancestor functions occur in its control. -/
def machine : Program Tapes Symbol MachineState := scheduler components componentEntry

def begins (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Fin 3 → Config Tapes Symbol Payload
  | i => match i.val with
    | 0 => taggedCfg Sum.inl (markerInput (homeHeads h) (cleanCells x y h past))
    | 1 => taggedCfg Sum.inr (boundaryInput x y h past)
    | _ => taggedCfg Sum.inl (markerInput (homeHeads h)
        (initialCells (x.map Bool.not) y h past))

def finishes (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Fin 3 → Config Tapes Symbol Payload
  | i => match i.val with
    | 0 => taggedCfg Sum.inl (markerOutput selected .separator (homeHeads h)
        (cleanCells x y h past))
    | 1 => taggedCfg Sum.inr (boundaryOutput x y h past)
    | _ => taggedCfg Sum.inl (markerOutput selected .blank (homeHeads h)
        (initialCells (x.map Bool.not) y h past))

def times (x y : List Bool) : Fin 3 → ℕ :=
  fun i => if i = 1 then 6*x.length + 5*y.length + 18 else 2

def input (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol MachineState :=
  stageCfg 0 ⟨.inl 0,homeHeads h,cleanCells x y h past⟩

def output (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol MachineState :=
  stageCfg (Fin.last 2) ⟨.inl 2,homeHeads h,cleanCells (x.map Bool.not) y h past⟩

private theorem begins_entry (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    ∀ i, (begins x y h past i).state = componentEntry i := by
  intro i
  fin_cases i <;> rfl

private theorem components_run (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    ∀ i, Runs (components i) (times x y i)
      (begins x y h past i) (finishes x y h past i) := by
  intro i
  fin_cases i
  · exact lift_runs (markerProgram selected .separator) Sum.inl leftDecode (fun _ => rfl)
      (marker_run selected .separator (homeHeads h) (cleanCells x y h past))
  · exact lift_runs boundaryMachine Sum.inr rightDecode (fun _ => rfl)
      (boundary_machine_correct x y h past).1
  · exact lift_runs (markerProgram selected .blank) Sum.inl leftDecode (fun _ => rfl)
      (marker_run selected .blank (homeHeads h) (initialCells (x.map Bool.not) y h past))

private theorem components_halt (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    ∀ i, Halts (components i) (finishes x y h past i) := by
  intro i
  fin_cases i
  · exact (lift_halts (markerProgram selected .separator) Sum.inl leftDecode
      (fun _ => rfl) _).2
      (marker_halts selected .separator (homeHeads h) (cleanCells x y h past))
  · exact (lift_halts boundaryMachine Sum.inr rightDecode (fun _ => rfl) _).2
      (boundary_machine_correct x y h past).2
  · exact (lift_halts (markerProgram selected .blank) Sum.inl leftDecode
      (fun _ => rfl) _).2
      (marker_halts selected .blank (homeHeads h) (initialCells (x.map Bool.not) y h past))

private theorem literal_boundaries (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Boundaries (begins x y h past) (finishes x y h past) := by
  intro i hi
  fin_cases i <;> try (norm_num at hi)
  · constructor
    · rfl
    · exact (install_cells x y h past).symm
  · constructor <;> rfl

/-- Universal complete execution from unmarked input buffers, including actual
marker installation/removal, all handoffs, literal restoration and true halt. -/
theorem machine_correct (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Runs machine (6*x.length+5*y.length+24) (input x y h past) (output x y h past) ∧
    Halts machine (output x y h past) := by
  have H := scheduler_assembly components componentEntry (begins x y h past)
    (finishes x y h past) (times x y) (begins_entry x y h past)
    (components_run x y h past) (components_halt x y h past) (literal_boundaries x y h past)
  have hsum : (∑ i, times x y i) + 2 = 6*x.length+5*y.length+24 := by
    simp [Fin.sum_univ_succ,times]
    omega
  rw [hsum] at H
  exact H

theorem finite_states : Fintype.card MachineState = 279 := by
  have hp : Fintype.card Payload = 93 := by
    change Fintype.card (Fin 3 ⊕ Control FlipPhase) = 93
    rw [Fintype.card_sum,boundary_states]
    rfl
  change Fintype.card (Fin 3 × Payload) = 279
  rw [Fintype.card_prod,hp]
  rfl
 theorem finite_tapes : Fintype.card Tapes = 5 := by decide

/-- The returned IO and temporary tapes are fully blank, rather than marked-empty. -/
theorem output_workspace_blank (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    (output x y h past).cell 2 = (fun _ => .blank) ∧
    (output x y h past).cell 4 = (fun _ => .blank) := by
  exact ⟨(clean_streams (x.map Bool.not) y h past).2.2.1.trans unmarked_empty,
    (clean_streams (x.map Bool.not) y h past).2.2.2.trans unmarked_empty⟩

end MultitapeToolkit.Absolute.CleanBoundary
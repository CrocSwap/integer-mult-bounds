import MultitapeToolkit.ParkingController
import MultitapeToolkit.TapeEmbedding
import MultitapeToolkit.CleanBoundary

/-!
# Actual parking callers on arbitrary finite physical banks

Five roles are selected by an injection. A genuine child may use the entire
larger bank and may return changed extra workspace explicitly. The pre-call
and post-call helpers preserve every extra tape literally. The closed flip
instance has no child premise. All handoffs retain their actual charges.
-/
namespace MultitapeToolkit.Absolute.GenericParkingController
open scoped BigOperators
open MarkedStreams ParkStack ControlEmbedding Subroutines
variable {ι Q : Type*} [Fintype ι] [Fintype Q]

abbrev State := ParkingController.State
abbrev Control := ParkingController.Control

def stub : Program (Fin 5) Symbol Q where transition _ _ := none

noncomputable def stages (r : Fin 5 ↪ ι) (child : Program ι Symbol Q) :
    Fin 6 → Program ι Symbol (State Q) :=
  fun i => if i=3 then liftProgram child ParkingController.encodeChild ParkingController.decodeChild
    else TapeEmbedding.liftProgram r (ParkingController.stages (stub (Q:=Q)) i)

noncomputable def wrapper (r : Fin 5 ↪ ι) (child : Program ι Symbol Q) (entry : Q) :
    Program ι Symbol (Control Q) := scheduler (stages r child) (ParkingController.entry entry)

noncomputable def childInput (r : Fin 5 ↪ ι) (entry : Q) (x y : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol Q :=
  TapeEmbedding.liftCfg r (ParkingController.childInput entry x y h past) H C
noncomputable def childOutput (r : Fin 5 ↪ ι) (exit : Q) (z y : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol Q :=
  TapeEmbedding.liftCfg r (ParkingController.childOutput exit z y h past) H C

noncomputable def wrapperInput (r : Fin 5 ↪ ι) (entry : Q) (x y : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol (Control Q) :=
  TapeEmbedding.liftCfg r (ParkingController.wrapperInput entry x y h past) H C
noncomputable def wrapperOutput (r : Fin 5 ↪ ι) (z y : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol (Control Q) :=
  TapeEmbedding.liftCfg r (ParkingController.wrapperOutput z y h past) H C

noncomputable def begins (r : Fin 5 ↪ ι) (entry : Q) (x y z : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H0 : ι → ℤ) (C0 : ι → ℤ → Symbol)
    (H1 : ι → ℤ) (C1 : ι → ℤ → Symbol) : Fin 6 → Config ι Symbol (State Q) :=
  fun i => TapeEmbedding.liftCfg r (ParkingController.begins entry x y z h past i)
    (if i.val≤3 then H0 else H1) (if i.val≤3 then C0 else C1)
noncomputable def finishes (r : Fin 5 ↪ ι) (entry exit : Q) (x y z : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H0 : ι → ℤ) (C0 : ι → ℤ → Symbol)
    (H1 : ι → ℤ) (C1 : ι → ℤ → Symbol) : Fin 6 → Config ι Symbol (State Q) :=
  fun i => TapeEmbedding.liftCfg r (ParkingController.finishes entry exit x y z h past i)
    (if i.val<3 then H0 else H1) (if i.val<3 then C0 else C1)

/-- Primitive source runs are reused only outside the actual child stage. -/
theorem primitive_runs (entry exit : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (t : ℕ) (i : Fin 6) (hi : i≠3) :
    Runs (ParkingController.stages (stub (Q:=Q)) i) (ParkingController.stageTimes x y z t i)
      (ParkingController.begins entry x y z h past i) (ParkingController.finishes entry exit x y z h past i) := by
  fin_cases i
  · exact .refl _
  · exact lift_runs (pushProgram (1:Fin 5) 3) ParkingController.encodePush ParkingController.decodePush (fun _ => rfl)
      (push_correct (1:Fin 5) 3 (by decide) y h past (ParkingController.homeHeads h) (ParkingController.initialCells x y h past))
  · exact lift_runs (moveProgram (0:Fin 5) 2) ParkingController.encodeMove ParkingController.decodeMove (fun _ => rfl)
      (move_runs (0:Fin 5) 2 (by decide) x clean clean (ParkingController.parkedHeads y h) (ParkingController.parkedCells x y h past))
  · exact False.elim (hi rfl)
  · exact lift_runs (moveProgram (2:Fin 5) 0) ParkingController.encodeMove ParkingController.decodeMove (fun _ => rfl)
      (move_runs (2:Fin 5) 0 (by decide) z clean clean (ParkingController.parkedHeads y h) (ParkingController.callCells z y h past))
  · exact lift_runs (popProgram (1:Fin 5) 4 3) ParkingController.encodePop ParkingController.decodePop (fun _ => rfl)
      (pop_correct (1:Fin 5) 4 3 (by decide) (by decide) (by decide) y h past
        (ParkingController.parkedHeads y h) (ParkingController.parkedCells z y h past))

theorem primitive_halts (entry exit : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (i : Fin 6) (hi : i≠3) :
    Halts (ParkingController.stages (stub (Q:=Q)) i)
      (ParkingController.finishes entry exit x y z h past i) := by
  fin_cases i
  · rfl
  · exact (lift_halts (pushProgram (1:Fin 5) 3) ParkingController.encodePush ParkingController.decodePush (fun _ => rfl) _).2
      (pushFinal_halts (1:Fin 5) 3 y h past (ParkingController.homeHeads h) (ParkingController.initialCells x y h past))
  · exact (lift_halts (moveProgram (0:Fin 5) 2) ParkingController.encodeMove ParkingController.decodeMove (fun _ => rfl) _).2
      (move_halts (0:Fin 5) 2 x clean clean (ParkingController.parkedHeads y h) (ParkingController.parkedCells x y h past))
  · exact False.elim (hi rfl)
  · exact (lift_halts (moveProgram (2:Fin 5) 0) ParkingController.encodeMove ParkingController.decodeMove (fun _ => rfl) _).2
      (move_halts (2:Fin 5) 0 z clean clean (ParkingController.parkedHeads y h) (ParkingController.callCells z y h past))
  · exact (lift_halts (popProgram (1:Fin 5) 4 3) ParkingController.encodePop ParkingController.decodePop (fun _ => rfl) _).2
      (popFinal_halts (1:Fin 5) 4 3 y h past (ParkingController.parkedHeads y h) (ParkingController.parkedCells z y h past))

theorem stages_runs (r : Fin 5 ↪ ι) (child : Program ι Symbol Q) (entry exit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) (t : ℕ)
    (H0 H1 : ι → ℤ) (C0 C1 : ι → ℤ → Symbol)
    (hc : Runs child t (childInput r entry x y h past H0 C0) (childOutput r exit z y h past H1 C1)) :
    ∀ i, Runs (stages r child i) (ParkingController.stageTimes x y z t i)
      (begins r entry x y z h past H0 C0 H1 C1 i)
      (finishes r entry exit x y z h past H0 C0 H1 C1 i) := by
  intro i
  by_cases hi : i=3
  · subst i
    simpa [stages,begins,finishes,childInput,childOutput,ParkingController.begins,ParkingController.finishes,
      TapeEmbedding.liftCfg,taggedCfg,ParkingController.stageTimes] using
      lift_runs child ParkingController.encodeChild ParkingController.decodeChild (fun _ => rfl) hc
  · have hp := primitive_runs entry exit x y z h past t i hi
    have he : (i.val≤3) = (i.val<3) := by fin_cases i <;> simp_all
    simpa [stages,begins,finishes,hi,he] using TapeEmbedding.lift_runs r _ hp
      (if i.val<3 then H0 else H1) (if i.val<3 then C0 else C1)

theorem stages_halts (r : Fin 5 ↪ ι) (child : Program ι Symbol Q) (entry exit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H0 H1 : ι → ℤ) (C0 C1 : ι → ℤ → Symbol)
    (hc : Halts child (childOutput r exit z y h past H1 C1)) :
    ∀ i, Halts (stages r child i) (finishes r entry exit x y z h past H0 C0 H1 C1 i) := by
  intro i
  by_cases hi : i=3
  · subst i
    simpa [stages,finishes,childOutput,ParkingController.finishes,TapeEmbedding.liftCfg,taggedCfg] using
      (lift_halts child ParkingController.encodeChild ParkingController.decodeChild (fun _ => rfl) _).2 hc
  · simpa [stages,finishes,hi] using
      (TapeEmbedding.lift_halts r _ _ (if i.val<3 then H0 else H1) (if i.val<3 then C0 else C1)).2
        (primitive_halts entry exit x y z h past i hi)

theorem literal_boundaries (r : Fin 5 ↪ ι) (entry exit : Q) (x y z : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (H0 H1 : ι → ℤ) (C0 C1 : ι → ℤ → Symbol) :
    Boundaries (begins r entry x y z h past H0 C0 H1 C1) (finishes r entry exit x y z h past H0 C0 H1 C1) := by
  intro i hi
  have hb := ParkingController.literal_boundaries entry exit x y z h past i hi
  fin_cases i <;> try (norm_num at hi)
  all_goals constructor
  all_goals funext j
  all_goals cases hd : TapeEmbedding.decode r j with
  | none => simp [begins,finishes,nextStage,TapeEmbedding.liftCfg,hd]
  | some k =>
    first
    | simpa [begins,finishes,nextStage,TapeEmbedding.liftCfg,hd] using congrFun hb.1 k
    | simpa [begins,finishes,nextStage,TapeEmbedding.liftCfg,hd] using congrFun hb.2 k

/-- A real child can use and return changed extra work tapes. The return bank,
including those extras, is literal, and caller overhead is exact. -/
theorem wrapper_correct (r : Fin 5 ↪ ι) (child : Program ι Symbol Q) (entry exit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) (t : ℕ)
    (H0 H1 : ι → ℤ) (C0 C1 : ι → ℤ → Symbol)
    (hr : Runs child t (childInput r entry x y h past H0 C0) (childOutput r exit z y h past H1 C1))
    (hh : Halts child (childOutput r exit z y h past H1 C1)) :
    Runs (wrapper r child entry) (2*x.length+2*z.length+5*y.length+16+t)
      (wrapperInput r entry x y h past H0 C0) (wrapperOutput r z y h past H1 C1) ∧
    Halts (wrapper r child entry) (wrapperOutput r z y h past H1 C1) := by
  have hentry : ∀ i, (begins r entry x y z h past H0 C0 H1 C1 i).state = ParkingController.entry entry i := by
    intro i
    exact ParkingController.begins_entry entry x y z h past i
  have hs := scheduler_assembly (stages r child) (ParkingController.entry entry)
    (begins r entry x y z h past H0 C0 H1 C1) (finishes r entry exit x y z h past H0 C0 H1 C1)
    (ParkingController.stageTimes x y z t) hentry
    (stages_runs r child entry exit x y z h past t H0 H1 C0 C1 hr)
    (stages_halts r child entry exit x y z h past H0 H1 C0 C1 hh)
    (literal_boundaries r entry exit x y z h past H0 H1 C0 C1)
  have hc : (∑ i, ParkingController.stageTimes x y z t i)+5 = 2*x.length+2*z.length+5*y.length+16+t := by
    simp only [Fin.sum_univ_succ,Fin.sum_univ_zero]
    simp [ParkingController.stageTimes]
    omega
  have hout : stageCfg (Fin.last 5) (finishes r entry exit x y z h past H0 C0 H1 C1 (Fin.last 5)) =
      wrapperOutput r z y h past H1 C1 := by
    change TapeEmbedding.liftCfg r (stageCfg (Fin.last 5) (ParkingController.finishes entry exit x y z h past (Fin.last 5))) H1 C1 = _
    rw [ParkingController.final_bank]
    rfl
  rw [hc,hout] at hs
  exact hs

noncomputable def bitFlipChild (r : Fin 5 ↪ ι) : Program ι Symbol FlipPhase :=
  TapeEmbedding.liftProgram r ParkingController.bitFlipChild
noncomputable def boundaryMachine (r : Fin 5 ↪ ι) : Program ι Symbol (Control FlipPhase) :=
  wrapper r (bitFlipChild r) .copy
noncomputable def boundaryInput (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) := wrapperInput r MovePhase.copy x y h past H C
noncomputable def boundaryOutput (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol (Control FlipPhase) :=
  wrapperOutput r (x.map Bool.not) y h past H C

/-- A fixed finite caller works on every larger tape bank, with arbitrary dirty
extras and no unknown child hypothesis. -/
theorem boundary_machine_correct (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (boundaryMachine r) (6*x.length+5*y.length+18)
      (boundaryInput r x y h past H C) (boundaryOutput r x y h past H C) ∧
    Halts (boundaryMachine r) (boundaryOutput r x y h past H C) := by
  have hc := flip_runs (2:Fin 5) x clean (ParkingController.parkedHeads y h) (ParkingController.callCells x y h past)
  have hh := flip_halts (2:Fin 5) x clean (ParkingController.parkedHeads y h) (ParkingController.callCells x y h past)
  rw [ParkingController.flip_entry_bank,ParkingController.flip_return_bank] at hc
  rw [ParkingController.flip_return_bank] at hh
  have hr := TapeEmbedding.lift_runs r ParkingController.bitFlipChild hc H C
  have hhalt := (TapeEmbedding.lift_halts r ParkingController.bitFlipChild _ H C).2 hh
  have hm := wrapper_correct r (bitFlipChild r) .copy .done x y (x.map Bool.not) h past
    (2*x.length+2) H H C C hr hhalt
  have hcost : 2*x.length+2*(x.map Bool.not).length+5*y.length+16+(2*x.length+2) =
      6*x.length+5*y.length+18 := by simp only [List.length_map]; omega
  rw [hcost] at hm
  exact hm

/-- The complete marked-input-free controller, lifted into an arbitrary larger bank. -/
noncomputable def cleanMachine (r : Fin 5 ↪ ι) :
    Program ι Symbol CleanBoundary.MachineState := TapeEmbedding.liftProgram r CleanBoundary.machine
noncomputable def cleanInput (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol CleanBoundary.MachineState :=
  TapeEmbedding.liftCfg r (CleanBoundary.input x y h past) H C
noncomputable def cleanOutput (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol CleanBoundary.MachineState :=
  TapeEmbedding.liftCfg r (CleanBoundary.output x y h past) H C

/-- Universal actual clean execution: install/call/remove markers and both extra
handoffs are charged. Arbitrary extra tape dirt is preserved literally. -/
theorem clean_machine_correct (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (cleanMachine r) (6*x.length+5*y.length+24)
      (cleanInput r x y h past H C) (cleanOutput r x y h past H C) ∧
    Halts (cleanMachine r) (cleanOutput r x y h past H C) := by
  have hm := CleanBoundary.machine_correct x y h past
  exact ⟨TapeEmbedding.lift_runs r _ hm.1 H C,
    (TapeEmbedding.lift_halts r _ _ H C).2 hm.2⟩

/-- IO and temporary workspace are actually all blank at return. -/
theorem clean_workspace_blank (r : Fin 5 ↪ ι) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    (cleanOutput r x y h past H C).cell (r 2) = (fun _ => .blank) ∧
    (cleanOutput r x y h past H C).cell (r 4) = (fun _ => .blank) := by
  simpa [cleanOutput] using CleanBoundary.output_workspace_blank x y h past

/-- Every clean-controller prefix preserves every extra tape completely. -/
theorem clean_preserves_extra (r : Fin 5 ↪ ι) (i : ι) (hi : i ∉ Set.range r)
    {n : ℕ} {c d : Config ι Symbol CleanBoundary.MachineState}
    (hr : Runs (cleanMachine r) n c d) :
    d.head i=c.head i ∧ ∀ x, d.cell i x=c.cell i x :=
  TapeEmbedding.preserves_extra r CleanBoundary.machine i hi hr

end MultitapeToolkit.Absolute.GenericParkingController


import PairedTrackExtractionFraming
import PositionalMetadataReturn

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Three-tape paid acquisition from an existing packed store: actual positional
access, one charged handoff, unchanged chosen-track extraction, one charged
handoff and actual return to global home. Both pair tracks and all other packed
blocks are preserved, as is the supplied unary control and Boolean scratch.
The fresh output starts empty; the copy machine writes its markers and bits.
Its seven registers are cleared, rather than restoring their old dirty values.

All input symbols and the ordered layout are supplied. A logical locate result
only selects that layout; no runtime key search, free tape relayout or Nat-to-bit
conversion occurs. The track selector is a fixed Boolean program parameter.
Author-checked conditional context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PaidPairedTrackAcquisition
open PairedBitXorScan (Tape Pair)
open PackedMetadataSlots (Block Focus pack capacity locate)
open PositionalMetadataAccess (ControlSymbol)
open SequentialBitAddition (Registers)
abbrev OutputTape := Tape MarkedZeroPadding.Symbol

inductive State where
  | access (output : OutputTape) (registers : Registers) (s : PositionalMetadataAccess.State)
  | extracting (control : Tape ControlSymbol) (scratch : Bool) (s : PairedTrackExtraction.State)
  | home (output : OutputTape) (registers : Registers) (s : PositionalMetadataReturn.State)

def step (second : Bool) : State → State
  | .access output registers s =>
      if s.phase=.halt then
        .extracting s.controlTape s.scratch ⟨s.dataTape,output,registers,.writeOutputLeft⟩
      else .access output registers (PositionalMetadataAccess.step s)
  | .extracting control scratch s =>
      if s.phase=.halt then
        .home s.output s.registers ⟨s.source,control,scratch,.enterControl⟩
      else .extracting control scratch (PairedTrackExtraction.step second s)
  | .home output registers s => .home output registers (PositionalMetadataReturn.step s)

def run (second : Bool) : Nat → State → State
  | 0,s => s
  | k+1,s => run second k (step second s)
def Halted : State → Prop
  | .home _ _ s => s.phase=.halt
  | _ => False

def tapeCells {α : Type} (s : Tape α) : Nat := s.left.length+s.right.length
def cells : State → Nat
  | .access out _ s => tapeCells out+PositionalMetadataAccess.cells s
  | .extracting control _ s => tapeCells control+PairedTrackExtraction.cells s
  | .home out _ s => tapeCells out+PositionalMetadataReturn.cells s

def initial (position : Nat) (blocks : List Block) (scratch : Bool) (r : Registers) : State :=
  .access ⟨[],[]⟩ r (PositionalMetadataAccess.initial position blocks scratch)
def focusedInitial (pre : List Block) (selected : Block) (post : List Block) (r : Registers) : PairedTrackExtraction.State :=
  PairedTrackExtractionFraming.embed (pack pre).reverse (pack post) (PairedTrackExtraction.initial selected.rows r)
def focusedFinal (second : Bool) (pre : List Block) (selected : Block) (post : List Block) : PairedTrackExtraction.State :=
  PairedTrackExtractionFraming.embed (pack pre).reverse (pack post) (PairedTrackExtraction.final second selected.rows)
def final (second : Bool) (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) : State :=
  .home (PairedTrackExtraction.final second selected.rows).output SequentialBitAddition.clearRegisters
    (PositionalMetadataReturn.final pre.length (pre++selected::post) scratch)
def travel (pre : List Block) : Nat := capacity pre+2*pre.length+4
def copyTime (selected : Block) : Nat := 6*selected.rows.length+16
def totalTime (pre : List Block) (selected : Block) : Nat := travel pre+1+copyTime selected+1+travel pre

private theorem run_add (second : Bool) (m n : Nat) (s : State) :
    run second (m+n) s=run second n (run second m s) := by
  induction m generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ m ih => simpa only [Nat.succ_add,run] using ih (step second s)
private theorem run_succ (second : Bool) (k : Nat) (s : State) :
    run second (k+1) s=step second (run second k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (step second s)
private theorem access_succ (k : Nat) (s : PositionalMetadataAccess.State) :
    PositionalMetadataAccess.run (k+1) s=PositionalMetadataAccess.step (PositionalMetadataAccess.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (PositionalMetadataAccess.step s)
private theorem extracting_succ (second : Bool) (k : Nat) (s : PairedTrackExtraction.State) :
    PairedTrackExtraction.run second (k+1) s=PairedTrackExtraction.step second (PairedTrackExtraction.run second k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (PairedTrackExtraction.step second s)
private theorem access_upto (second : Bool) (out : OutputTape) (r : Registers) (s : PositionalMetadataAccess.State) (k : Nat)
    (h : ∀ j<k,(PositionalMetadataAccess.run j s).phase≠.halt) :
    run second k (.access out r s)=.access out r (PositionalMetadataAccess.run k s) := by
  induction k with
  | zero => rfl
  | succ k ih =>
      rw [run_succ,ih (fun j hj=>h j (by omega)),access_succ]
      simp only [step,if_neg (h k (by omega))]
private theorem extracting_upto (second : Bool) (control : Tape ControlSymbol) (scratch : Bool)
    (s : PairedTrackExtraction.State) (k : Nat)
    (h : ∀ j<k,(PairedTrackExtraction.run second j s).phase≠.halt) :
    run second k (.extracting control scratch s)=.extracting control scratch (PairedTrackExtraction.run second k s) := by
  induction k with
  | zero => rfl
  | succ k ih =>
      rw [run_succ,ih (fun j hj=>h j (by omega)),extracting_succ]
      simp only [step,if_neg (h k (by omega))]
private theorem home_run (second : Bool) (out : OutputTape) (r : Registers) (s : PositionalMetadataReturn.State) (k : Nat) :
    run second k (.home out r s)=.home out r (PositionalMetadataReturn.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (PositionalMetadataReturn.step s)

theorem access_prefix (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (k : Nat) (hk : k≤travel pre) :
    run second k (initial pre.length (pre++selected::post) scratch r)=
      .access ⟨[],[]⟩ r (PositionalMetadataAccess.run k (PositionalMetadataAccess.initial pre.length (pre++selected::post) scratch)) := by
  apply access_upto
  intro j hj
  exact (PositionalMetadataAccess.access_first_halt pre selected post scratch).2 j
    (by simpa only [travel] using Nat.lt_of_lt_of_le hj hk)

/-- This charged switch passes the reached head and existing output allocation. -/
theorem enter_extraction (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) :
    run second (travel pre+1) (initial pre.length (pre++selected::post) scratch r)=
      .extracting (PositionalMetadataAccess.unary pre.length) scratch (focusedInitial pre selected post r) := by
  rw [run_succ,access_prefix second pre selected post scratch r _ (Nat.le_refl _)]
  rw [show travel pre=capacity pre+2*pre.length+4 from rfl,PositionalMetadataAccess.access_result]
  rfl

theorem extraction_prefix (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (j : Nat) (hj : j≤copyTime selected) :
    run second (travel pre+1+j) (initial pre.length (pre++selected::post) scratch r)=
      .extracting (PositionalMetadataAccess.unary pre.length) scratch
        (PairedTrackExtraction.run second j (focusedInitial pre selected post r)) := by
  rw [run_add,enter_extraction]
  apply extracting_upto
  intro k hk
  exact (PairedTrackExtractionFraming.framed_result second (pack pre).reverse (pack post) selected.rows r).2 k
    (by simpa only [copyTime] using Nat.lt_of_lt_of_le hk hj)

/-- The actual source is passed back to the return controller, without repacking. -/
theorem home_handoff (second : Bool) (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    step second (.extracting (PositionalMetadataAccess.unary pre.length) scratch (focusedFinal second pre selected post))=
      .home (PairedTrackExtraction.final second selected.rows).output SequentialBitAddition.clearRegisters
        (PositionalMetadataReturn.initial pre selected post scratch) := rfl

theorem home_suffix (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (j : Nat) :
    run second (travel pre+1+copyTime selected+1+j) (initial pre.length (pre++selected::post) scratch r)=
      .home (PairedTrackExtraction.final second selected.rows).output SequentialBitAddition.clearRegisters
        (PositionalMetadataReturn.run j (PositionalMetadataReturn.initial pre selected post scratch)) := by
  have hr := (PairedTrackExtractionFraming.framed_result second (pack pre).reverse (pack post) selected.rows r).1
  change PairedTrackExtraction.run second (copyTime selected) (focusedInitial pre selected post r)=focusedFinal second pre selected post at hr
  rw [run_add,run_succ,extraction_prefix second pre selected post scratch r _ (Nat.le_refl _),hr,home_handoff,home_run]

/-- Exact first halt, all original packed symbols and the control restored at
home, with a newly written chosen-track word. Both handoffs are charged. -/
theorem machine_result (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) :
    run second (totalTime pre selected) (initial pre.length (pre++selected::post) scratch r)=final second pre selected post scratch ∧
    Halted (final second pre selected post scratch) ∧
    ∀ k<totalTime pre selected,¬Halted (run second k (initial pre.length (pre++selected::post) scratch r)) := by
  refine ⟨?_,rfl,?_⟩
  · unfold totalTime
    rw [home_suffix,show travel pre=capacity pre+2*pre.length+4 from rfl,PositionalMetadataReturn.return_result]
    rfl
  · intro k hk
    by_cases ha:k≤travel pre
    · rw [access_prefix second pre selected post scratch r k ha]
      exact fun h=>h
    · by_cases he:k≤travel pre+1+copyTime selected
      · have hs:k=travel pre+1+(k-(travel pre+1)):=by omega
        rw [hs,extraction_prefix second pre selected post scratch r _ (by omega)]
        exact fun h=>h
      · have hs:k=travel pre+1+copyTime selected+1+(k-(travel pre+1+copyTime selected+1)):=by omega
        rw [hs,home_suffix]
        apply (PositionalMetadataReturn.return_first_halt pre selected post scratch).2
        simpa only [travel] using (show k-(travel pre+1+copyTime selected+1)<travel pre by unfold totalTime at hk;omega)

theorem time_eq (pre : List Block) (selected : Block) :
    totalTime pre selected=2*capacity pre+4*pre.length+6*selected.rows.length+26 := by
  unfold totalTime travel copyTime
  omega

theorem initial_cells (position : Nat) (blocks : List Block) (scratch : Bool) (r : Registers) :
    cells (initial position blocks scratch r)=capacity blocks+(position+2) := by
  simp only [initial,cells,tapeCells,PositionalMetadataAccess.initial,PositionalMetadataAccess.cells,
    PositionalMetadataAccess.tapeCells,PositionalMetadataAccess.unary,List.length_nil,List.length_cons,
    List.length_append,List.length_replicate,PackedMetadataSlots.pack_capacity]
  omega

/-- Logical first-match evidence supplies only the existing split and position. -/
theorem acquisition_from_locate (second : Bool) (key : Nat) (blocks : List Block) (f : Focus)
    (located : locate key blocks=some f) (scratch : Bool) (r : Registers) :
    run second (totalTime f.before f.selected) (initial f.before.length blocks scratch r)=final second f.before f.selected f.after scratch ∧
    Halted (final second f.before f.selected f.after scratch) ∧
    ∀ k<totalTime f.before f.selected,¬Halted (run second k (initial f.before.length blocks scratch r)) := by
  obtain ⟨he,_,_⟩:=PackedMetadataSlots.locate_spec key blocks f located
  rw [he]
  exact machine_result second f.before f.selected f.after scratch r

end CurrentMain.PaidPairedTrackAcquisition
#print axioms CurrentMain.PaidPairedTrackAcquisition.enter_extraction
#print axioms CurrentMain.PaidPairedTrackAcquisition.home_handoff
#print axioms CurrentMain.PaidPairedTrackAcquisition.machine_result
#print axioms CurrentMain.PaidPairedTrackAcquisition.time_eq
#print axioms CurrentMain.PaidPairedTrackAcquisition.initial_cells
#print axioms CurrentMain.PaidPairedTrackAcquisition.acquisition_from_locate
#check @CurrentMain.PaidPairedTrackAcquisition.machine_result
#check @CurrentMain.PaidPairedTrackAcquisition.acquisition_from_locate

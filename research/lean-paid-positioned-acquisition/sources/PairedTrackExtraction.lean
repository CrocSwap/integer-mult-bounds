import MarkedBitDifference
import MarkedBitXorScan

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Finite-alphabet specialization of the accepted MarkedBitDifference copy phase.
The actual source is the existing two-track packed-store alphabet; each read
selects one Boolean at the current cell. The program parameter second chooses
the track. Source writes and whole-tape maps never occur in the transition.

A proof-only embedding places each pair p in the row (p,chosen p), allowing
reuse of the accepted extraction trace, marker handling, return and seven
register clears. Both original pair bits and the source head are preserved.
The output is a separately supplied blank tape; its markers and bits are paid.
Ambient source framing and access/home composition are subsequent obligations.
Old registers are cleared rather than restored. The 6w+16 transition count is
for the declared finite multitape model, not an unbounded-arithmetic invoice.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PairedTrackExtraction
open PairedBitXorScan (Tape Pair)
open SequentialBitAddition (Registers ClearSlot)
abbrev Symbol := MarkedBitXorScan.Symbol
abbrev BitSymbol := MarkedZeroPadding.Symbol

def chosen (second:Bool) (p:Pair) : Bool := if second then p.2 else p.1
inductive Phase where
  | writeOutputLeft | enterOutput | enterInput | copyTest | copyWrite
  | advanceInput | advanceOutput | writeOutputRight | rewindOutput | rewindInput
  | clear (slot:ClearSlot) | halt
  deriving DecidableEq
structure State where
  source : Tape Symbol
  output : Tape BitSymbol
  registers : Registers
  phase : Phase
  deriving DecidableEq

def afterClear : ClearSlot → Phase
  | .x => .clear .y
  | .y => .clear .carry
  | .carry => .clear .xorXY
  | .xorXY => .clear .sum
  | .sum => .clear .andXY
  | .andXY => .clear .andTC
  | .andTC => .halt

/-- A finite current-symbol transition, with one chosen-bit read, output
write or head move in each corresponding inherited phase. -/
def step (second:Bool) (s:State) : State :=
  match s.phase with
  | .halt => s
  | .writeOutputLeft => {s with output:=s.output.writeHead .leftMarker,phase:=.enterOutput}
  | .enterOutput => {s with output:=s.output.moveRight .blank,phase:=.enterInput}
  | .enterInput => {s with source:=s.source.moveRight .blank,phase:=.copyTest}
  | .copyTest => match s.source.readHead .blank with
    | .data a b => {s with registers:={s.registers with sum:=chosen second (a,b)},phase:=.copyWrite}
    | .rightMarker => {s with phase:=.writeOutputRight}
    | _ => {s with phase:=.halt}
  | .copyWrite => {s with output:=s.output.writeHead (.data s.registers.sum),phase:=.advanceInput}
  | .advanceInput => {s with source:=s.source.moveRight .blank,phase:=.advanceOutput}
  | .advanceOutput => {s with output:=s.output.moveRight .blank,phase:=.copyTest}
  | .writeOutputRight => {s with output:=s.output.writeHead .rightMarker,phase:=.rewindOutput}
  | .rewindOutput => if s.output.readHead .blank=.leftMarker then {s with phase:=.rewindInput}
      else {s with output:=s.output.moveLeft .blank}
  | .rewindInput => if s.source.readHead .blank=.leftMarker then {s with phase:=.clear .x}
      else {s with source:=s.source.moveLeft .blank}
  | .clear slot => {s with registers:=SequentialBitAddition.clearSlot slot s.registers,phase:=afterClear slot}

def run (second:Bool) : Nat → State → State
  | 0,s => s
  | k+1,s => run second k (step second s)

/-- Proof-only alphabet map; absent from the executed step. -/
def rowOf (second:Bool) (p:Pair) : SequentialBitAddition.Row := (p,chosen second p)
def symbolOf (second:Bool) : Symbol → MarkedBitAddition.Symbol
  | .blank => .blank
  | .leftMarker => .leftMarker
  | .rightMarker => .rightMarker
  | .data a b => .data (rowOf second (a,b))
def tapeOf (second:Bool) (t:Tape Symbol) : Tape MarkedBitAddition.Symbol :=
  ⟨t.left.map (symbolOf second),t.right.map (symbolOf second)⟩
def phaseOf : Phase → MarkedBitDifference.Phase
  | .writeOutputLeft => .writeOutputLeft
  | .enterOutput => .enterOutput
  | .enterInput => .enterInput
  | .copyTest => .copyTest
  | .copyWrite => .copyWrite
  | .advanceInput => .copyAdvanceInput
  | .advanceOutput => .copyAdvanceOutput
  | .writeOutputRight => .writeOutputRight
  | .rewindOutput => .rewindOutput
  | .rewindInput => .rewindInput
  | .clear slot => .clear slot
  | .halt => .halt
def model (second:Bool) (s:State) : MarkedBitDifference.State :=
  ⟨tapeOf second s.source,s.output,s.registers,false,phaseOf s.phase⟩

private theorem tapeOf_read (second:Bool) (t:Tape Symbol) :
    (tapeOf second t).readHead .blank=symbolOf second (t.readHead .blank) := by
  rcases t with ⟨ls,rs⟩
  cases rs <;> rfl
private theorem tapeOf_right (second:Bool) (t:Tape Symbol) :
    tapeOf second (t.moveRight .blank)=(tapeOf second t).moveRight .blank := by
  rcases t with ⟨ls,rs⟩
  cases rs <;> rfl
private theorem tapeOf_left (second:Bool) (t:Tape Symbol) :
    tapeOf second (t.moveLeft .blank)=(tapeOf second t).moveLeft .blank := by
  rcases t with ⟨ls,rs⟩
  cases ls <;> rfl
private theorem symbolOf_left (second:Bool) (s:Symbol) :
    (symbolOf second s=MarkedBitAddition.Symbol.leftMarker)↔s=.leftMarker := by
  cases s <;> simp [symbolOf]

/-- Every real transition refines the existing extraction phase. -/
theorem model_step (second:Bool) (s:State) :
    model second (step second s)=MarkedBitDifference.step (model second s) := by
  rcases s with ⟨src,out,r,p⟩
  cases p with
  | copyTest =>
      cases h:src.readHead .blank <;>
        simp [step,model,phaseOf,tapeOf_read,h,symbolOf,MarkedBitDifference.step,rowOf]
  | rewindOutput =>
      by_cases h:out.readHead .blank=.leftMarker <;>
        simp [step,model,phaseOf,MarkedBitDifference.step,h]
  | rewindInput =>
      by_cases h:src.readHead .blank=.leftMarker <;>
        simp [step,model,phaseOf,MarkedBitDifference.step,tapeOf_read,symbolOf_left,h,tapeOf_left]
  | clear slot =>
      cases slot <;> rfl
  | _ => simp [step,model,phaseOf,MarkedBitDifference.step,tapeOf_right]

theorem model_run (second:Bool) (s:State) (k:Nat) :
    model second (run second k s)=MarkedBitDifference.run k (model second s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => rw [run,ih,model_step,MarkedBitDifference.run]

private def symbolBack : MarkedBitAddition.Symbol → Symbol
  | .blank => .blank
  | .leftMarker => .leftMarker
  | .rightMarker => .rightMarker
  | .data p => .data p.1.1 p.1.2
private def phaseBack : MarkedBitDifference.Phase → Phase
  | .writeOutputLeft => .writeOutputLeft
  | .enterOutput => .enterOutput
  | .enterInput => .enterInput
  | .copyTest => .copyTest
  | .copyWrite => .copyWrite
  | .copyAdvanceInput => .advanceInput
  | .copyAdvanceOutput => .advanceOutput
  | .writeOutputRight => .writeOutputRight
  | .rewindOutput => .rewindOutput
  | .rewindInput => .rewindInput
  | .clear slot => .clear slot
  | _ => .halt
private def back (s:MarkedBitDifference.State) : State :=
  ⟨⟨s.tape.left.map symbolBack,s.tape.right.map symbolBack⟩,s.output,s.registers,phaseBack s.phase⟩
private theorem symbol_back (second:Bool) (s:Symbol) : symbolBack (symbolOf second s)=s := by
  cases s <;> rfl
private theorem back_model (second:Bool) (s:State) : back (model second s)=s := by
  rcases s with ⟨⟨ls,rs⟩,out,r,p⟩
  cases p <;> simp [back,model,tapeOf,phaseOf,phaseBack,List.map_map,Function.comp_def,symbol_back]
private theorem model_injective (second:Bool) : Function.Injective (model second) := by
  intro s t h
  have hb:=congrArg back h
  simpa only [back_model] using hb
private theorem model_halt (second:Bool) (s:State) :
    (model second s).phase=.halt ↔ s.phase=.halt := by
  cases hp:s.phase <;> simp [model,phaseOf,hp]

def initial (rows:List Pair) (r:Registers) : State :=
  ⟨⟨[],MarkedBitXorScan.marked rows⟩,⟨[],[]⟩,r,.writeOutputLeft⟩
def final (second:Bool) (rows:List Pair) : State :=
  ⟨⟨[],MarkedBitXorScan.marked rows⟩,
    MarkedZeroPadding.marked (MarkedZeroPadding.bits (rows.map (chosen second))),
    SequentialBitAddition.clearRegisters,.halt⟩
private theorem model_initial (second:Bool) (rows:List Pair) (r:Registers) :
    model second (initial rows r)=
      (⟨MarkedBitAddition.marked (rows.map (rowOf second)),⟨[],[]⟩,r,false,.writeOutputLeft⟩:MarkedBitDifference.State) := by
  simp [model,initial,tapeOf,MarkedBitXorScan.marked,MarkedBitAddition.marked,
    List.map_map,Function.comp_def,symbolOf,MarkedBitXorScan.dataSymbol,phaseOf]
private theorem model_final (second:Bool) (rows:List Pair) :
    model second (final second rows)=MarkedBitDifference.copyFinal (rows.map (rowOf second)) false := by
  simp [model,final,tapeOf,MarkedBitXorScan.marked,MarkedBitAddition.marked,
    MarkedBitDifference.copyFinal,List.map_map,Function.comp_def,symbolOf,rowOf,phaseOf,MarkedBitXorScan.dataSymbol]

-- Generic observations of the imported trace are repeated only because
-- those helpers are private; the extraction algorithm/trace is reused.
private theorem trace_sound {k:Nat} {s t:MarkedBitDifference.State}
    (h:MarkedBitDifference.Trace k s t) : MarkedBitDifference.run k s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih
private theorem trace_live {n:Nat} {s t:MarkedBitDifference.State}
    (h:MarkedBitDifference.Trace n s t) (k:Nat) (hk:k<n) : (MarkedBitDifference.run k s).phase≠.halt := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih => cases k with
    | zero => exact live
    | succ k => exact ih k (by omega)

/-- Literal returned source, paid chosen-bit output, first halt and cleared
registers are inherited from the actual refined extraction trace. -/
theorem extraction_result (second:Bool) (rows:List Pair) (r:Registers) :
    run second (6*rows.length+16) (initial rows r)=final second rows ∧
    (final second rows).phase=.halt ∧
    ∀ k<6*rows.length+16,(run second k (initial rows r)).phase≠.halt := by
  have ht:=MarkedBitDifference.extraction_exact (rows.map (rowOf second)) r false
  simp only [List.length_map] at ht
  have hr:=trace_sound ht
  rw [← model_initial,← model_final,← model_run] at hr
  refine ⟨model_injective second hr,rfl,?_⟩
  intro k hk hh
  have hl:=trace_live ht k hk
  rw [← model_initial,← model_run] at hl
  exact hl ((model_halt second _).mpr hh)

def cells (s:State) : Nat :=
  s.source.left.length+s.source.right.length+s.output.left.length+s.output.right.length
private theorem model_cells (second:Bool) (s:State) : MarkedBitDifference.cells (model second s)=cells s := by
  simp [model,tapeOf,cells,MarkedBitDifference.cells,MarkedBitDifference.tapeCells,Nat.add_assoc]
private theorem halt_run (s:MarkedBitDifference.State) (h:s.phase=.halt) (k:Nat) : MarkedBitDifference.run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [MarkedBitDifference.run,MarkedBitDifference.step,h] using ih
private theorem trace_storage {n:Nat} {s t:MarkedBitDifference.State}
    (h:MarkedBitDifference.Trace n s t) (ht:t.phase=.halt) (k:Nat) :
    MarkedBitDifference.cells (MarkedBitDifference.run k s)≤MarkedBitDifference.cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (MarkedBitDifference.step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

theorem extraction_storage (second:Bool) (rows:List Pair) (r:Registers) (k:Nat) :
    cells (run second k (initial rows r))≤2*rows.length+4 := by
  have ht:=MarkedBitDifference.extraction_exact (rows.map (rowOf second)) r false
  have hs:=trace_storage ht rfl k
  rw [← model_initial,← model_final,← model_run,model_cells,model_cells] at hs
  simpa [cells,final,MarkedBitXorScan.marked,MarkedZeroPadding.marked,MarkedZeroPadding.bits,
    Nat.two_mul,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hs

theorem output_value (second:Bool) (rows:List Pair) (r:Registers) :
    (run second (6*rows.length+16) (initial rows r)).source=⟨[],MarkedBitXorScan.marked rows⟩ ∧
    (run second (6*rows.length+16) (initial rows r)).output=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits (rows.map (chosen second))) := by
  rw [(extraction_result second rows r).1]
  exact ⟨rfl,rfl⟩

end CurrentMain.PairedTrackExtraction
#print axioms CurrentMain.PairedTrackExtraction.model_step
#print axioms CurrentMain.PairedTrackExtraction.model_run
#print axioms CurrentMain.PairedTrackExtraction.extraction_result
#print axioms CurrentMain.PairedTrackExtraction.extraction_storage
#print axioms CurrentMain.PairedTrackExtraction.output_value
#check @CurrentMain.PairedTrackExtraction.extraction_result
#check @CurrentMain.PairedTrackExtraction.output_value

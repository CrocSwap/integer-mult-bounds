import CopiedExponentDyadicAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Actual numerator output extraction after copied-exponent dyadic addition.
Reuse the public MarkedBitDifference.extraction_exact trace verbatim: no new
copy implementation or arithmetic kernel is introduced. One charged switch
passes the actual marked sum tape and a new blank output tape to that machine.
Eleven spectators plus its two active tapes make thirteen physical tapes.
The emitted numerator word includes its final sign bit. This is an embedded-
sign output representation, not the separate-sign entrance format; adapting
that format requires an independently paid operation. The preceding twelve
physical tapes and finite fields are restored at the actual final endpoint.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace ExtractedDyadicOutput
open EncodedDyadicAddition (ZTape ATape)
open SequentialBitAddition (Registers Row)

/-- Eleven physical spectator tapes, including the entire three-tape completed
exponent-copy state. The sum source tape alone belongs to extraction. -/
structure Frame where
  exponentCopy : MarkedZeroPadding.State
  otherExponent : ZTape
  paired : ATape
  counter : ZTape
  magnitude : ZTape
  leftData : ZTape
  rightData : ZTape
  paddedLeft : ZTape
  paddedRight : ZTape
  savedRegisters : Registers
  borrow : Bool
  exponentLeftSign : Bool
  exponentRightSign : Bool
  reverse : Bool
  leftScratch : Bool
  rightScratch : Bool
  sumLeftSign : Bool
  sumRightSign : Bool
  sumPhase : MarkedBitAddition.Phase
  deriving DecidableEq

inductive State where
  | running (s:CopiedExponentDyadicAddition.State) (output:ZTape)
  | extracting (frame:Frame) (s:MarkedBitDifference.State)
  deriving DecidableEq

def finished : CopiedExponentDyadicAddition.State → Bool
  | .running _ _ => false
  | .copying _ s => s.phase==.halt
private theorem finished_iff (s:CopiedExponentDyadicAddition.State) :
    finished s=true ↔ CopiedExponentDyadicAddition.Halted s := by
  cases s <;> simp [finished,CopiedExponentDyadicAddition.Halted]

def makeFrame (f:CopiedExponentDyadicAddition.CopyFrame) (c:MarkedZeroPadding.State)
    (l r:ZTape) (sx sy:Bool) (phase:MarkedBitAddition.Phase) : Frame :=
  ⟨c,f.otherExponent,f.paired,f.counter,f.magnitude,f.leftData,f.rightData,l,r,
    f.savedRegisters,f.borrow,f.exponentLeftSign,f.exponentRightSign,f.reverse,
    f.leftScratch,f.rightScratch,sx,sy,phase⟩

def enterExtraction (s:CopiedExponentDyadicAddition.State) (out:ZTape) : State :=
  match s with
  | .copying f c => match f.sumState with
    | .addition l r sx sy a =>
        .extracting (makeFrame f c l r sx sy a.phase)
          ⟨a.tape,out,a.registers,f.reverse,.writeOutputLeft⟩
    | _ => .running s out
  | _ => .running s out

def step : State → State
  | .running s out => if finished s then enterExtraction s out else .running (CopiedExponentDyadicAddition.step s) out
  | .extracting f s => .extracting f (MarkedBitDifference.step s)
def Halted : State → Prop
  | .running _ _ => False
  | .extracting _ s => s.phase=.halt

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
inductive Trace : Nat → State → State → Prop where
  | nil (s:State) : Trace 0 s s
  | next {k:Nat} {s t:State} (live:¬Halted s) (tail:Trace k (step s) t) : Trace (k+1) s t
private theorem trace_trans {m n:Nat} {s u t:State} (h:Trace m s u) (g:Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)
private theorem trace_sound {n:Nat} {s t:State} (h:Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih
private theorem trace_live {n:Nat} {s t:State} (h:Trace n s t) (k:Nat) (hk:k<n) : ¬Halted (run k s) := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih => cases k with
    | zero => exact live
    | succ k => exact ih k (by omega)
private theorem running_trace (out:ZTape) {n:Nat} {s t:CopiedExponentDyadicAddition.State}
    (h:CopiedExponentDyadicAddition.Trace n s t) : Trace n (.running s out) (.running t out) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      refine Trace.next (by simp [Halted]) ?_
      have hn:finished s=false := by
        cases he:finished s
        · rfl
        · exact False.elim (live ((finished_iff s).mp he))
      simpa only [step,hn,Bool.false_eq_true,if_false] using ih
private theorem extracting_trace (f:Frame) {n:Nat} {s t:MarkedBitDifference.State}
    (h:MarkedBitDifference.Trace n s t) : Trace n (.extracting f s) (.extracting f t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def retained : State → CopiedExponentDyadicAddition.State
  | .running s _ => s
  | .extracting f s => .copying
      ⟨f.otherExponent,f.paired,f.counter,f.magnitude,f.leftData,f.rightData,
        .addition f.paddedLeft f.paddedRight f.sumLeftSign f.sumRightSign ⟨s.tape,s.registers,f.sumPhase⟩,
        f.savedRegisters,f.borrow,f.exponentLeftSign,f.exponentRightSign,f.reverse,f.leftScratch,f.rightScratch⟩
      f.exponentCopy
def outputTape : State → ZTape
  | .running _ out => out
  | .extracting _ s => s.output

def sumRows (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : List Row :=
  MarkedLayoutAddition.outputRows
    (MarkedZeroPadding.padded (EncodedDyadicAddition.leftShift xp yp er) xs)
    (MarkedZeroPadding.padded (EncodedDyadicAddition.rightShift xp yp er) ys) sx sy ar

def finalFrame (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Frame :=
  makeFrame (CopiedExponentDyadicAddition.finalFrame xp yp xs ys sx sy er ar)
    (MarkedZeroPadding.final 0 (EncodedDyadicAddition.commonWord xp yp er))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits (MarkedZeroPadding.padded (EncodedDyadicAddition.leftShift xp yp er) xs)))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits (MarkedZeroPadding.padded (EncodedDyadicAddition.rightShift xp yp er) ys)))
    sx sy (.body .halt)

def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) : State :=
  .running (CopiedExponentDyadicAddition.initial xp yp xs ys sx sy bl br er ar) ⟨[],[]⟩
def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .extracting (finalFrame xp yp xs ys sx sy er ar)
    (MarkedBitDifference.copyFinal (sumRows xp yp xs ys sx sy er ar) (EncodedExponentControl.reverseFlag xp yp er))
def totalTime (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  CopiedExponentDyadicAddition.totalTime xp yp xs ys er+1+
    (6*(sumRows xp yp xs ys sx sy er ar).length+16)

theorem handoff (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    step (.running (CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)=
      .extracting (finalFrame xp yp xs ys sx sy er ar)
        ⟨MarkedBitAddition.marked (sumRows xp yp xs ys sx sy er ar),⟨[],[]⟩,
          SequentialBitAddition.clearRegisters,EncodedExponentControl.reverseFlag xp yp er,.writeOutputLeft⟩ := rfl

/-- The actual source sum tape returns, its already-cleared register bank stays
cleared, and all eleven spectators retain their contents, heads and registers. -/
theorem output_and_retained (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    retained (final xp yp xs ys sx sy er ar)=CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar ∧
    outputTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits ((sumRows xp yp xs ys sx sy er ar).map Prod.snd)) := by
  constructor <;> rfl

theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    Trace (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar)
      (final xp yp xs ys sx sy er ar) := by
  have h:=running_trace ⟨[],[]⟩ (CopiedExponentDyadicAddition.machine_exact xp yp xs ys sx sy bl br er ar)
  have hc:Trace 1 (.running (CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)
      (.extracting (finalFrame xp yp xs ys sx sy er ar)
        ⟨MarkedBitAddition.marked (sumRows xp yp xs ys sx sy er ar),⟨[],[]⟩,
          SequentialBitAddition.clearRegisters,EncodedExponentControl.reverseFlag xp yp er,.writeOutputLeft⟩) := by
    refine Trace.next (by simp [Halted]) ?_
    rw [handoff]
    exact Trace.nil _
  exact trace_trans (trace_trans h hc)
    (extracting_trace (finalFrame xp yp xs ys sx sy er ar)
      (MarkedBitDifference.extraction_exact (sumRows xp yp xs ys sx sy er ar)
        SequentialBitAddition.clearRegisters (EncodedExponentControl.reverseFlag xp yp er)))

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    run (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar)=final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    (∀ k<totalTime xp yp xs ys sx sy er ar,¬Halted (run k (initial xp yp xs ys sx sy bl br er ar))) ∧
    retained (final xp yp xs ys sx sy er ar)=CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar ∧
    outputTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits ((sumRows xp yp xs ys sx sy er ar).map Prod.snd)) :=
  ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar),rfl,
    trace_live (machine_exact xp yp xs ys sx sy bl br er ar),output_and_retained xp yp xs ys sx sy er ar⟩

/-- The final sign bit is part of the copied word. No free separate-sign
input adapter is inferred from this value observation. -/
theorem numerator_encoding (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    let dx:=EncodedDyadicAddition.leftShift xp yp er
    let dy:=EncodedDyadicAddition.rightShift xp yp er
    let px:=MarkedZeroPadding.padded dx xs
    let py:=MarkedZeroPadding.padded dy ys
    let p:=SignedWordAlignment.aligned px sx py sy
    let low:=SequentialBitAddition.scan p (SequentialBitAddition.zeroCarry (MarkedPairLayout.clearScratch ar))
    let lastLow:=SequentialBitAddition.sumBit sx sy low.registers.carry
    let sign:=SequentialBitAddition.sumBit sx sy (SequentialBitAddition.carryBit sx sy low.registers.carry)
    (sumRows xp yp xs ys sx sy er ar).map Prod.snd=low.output++[lastLow,sign] ∧
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨SequentialBitAddition.signedValue (low.output++[lastLow]) sign,
        CurrentMain.PairedBitXorScan.value (EncodedDyadicAddition.commonWord xp yp er)⟩ =
      (SequentialBitAddition.signedValue xs sx:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value xp)+
      (SequentialBitAddition.signedValue ys sy:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value yp) :=
  EncodedDyadicAddition.output_value xp yp xs ys sx sy er ar

def frameCells (f:Frame) : Nat :=
  MarkedZeroPadding.cells f.exponentCopy+
  BinaryToUnaryControl.tapeCells f.otherExponent+MarkedBitDifference.tapeCells f.paired+
  BinaryToUnaryControl.tapeCells f.counter+BinaryToUnaryControl.tapeCells f.magnitude+
  BinaryToUnaryControl.tapeCells f.leftData+BinaryToUnaryControl.tapeCells f.rightData+
  BinaryToUnaryControl.tapeCells f.paddedLeft+BinaryToUnaryControl.tapeCells f.paddedRight

def cells : State → Nat
  | .running s out => CopiedExponentDyadicAddition.cells s+BinaryToUnaryControl.tapeCells out
  | .extracting f s => frameCells f+MarkedBitDifference.cells s

theorem extracting_run (f:Frame) (s:MarkedBitDifference.State) (k:Nat) :
    run k (.extracting f s)=.extracting f (MarkedBitDifference.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedBitDifference.step s)

theorem cells_retained (f:Frame) (s:MarkedBitDifference.State) :
    cells (.extracting f s)=CopiedExponentDyadicAddition.cells (retained (.extracting f s))+
      BinaryToUnaryControl.tapeCells s.output := by
  simp [cells,frameCells,retained,CopiedExponentDyadicAddition.cells,CopiedExponentDyadicAddition.frameCells,
    MarkedLayoutAddition.cells,MarkedPairLayout.tapeCells,MarkedBitAddition.cells,
    MarkedBitAddition.tapeCells,MarkedBitDifference.cells,MarkedBitDifference.tapeCells,
    BinaryToUnaryControl.tapeCells]
  omega

theorem final_cells (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    cells (final xp yp xs ys sx sy er ar)=
      CopiedExponentDyadicAddition.cells (CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar)+
      (sumRows xp yp xs ys sx sy er ar).length+2 := by
  change cells (.extracting _ _)=_
  have hr:retained (.extracting (finalFrame xp yp xs ys sx sy er ar)
      (MarkedBitDifference.copyFinal (sumRows xp yp xs ys sx sy er ar) (EncodedExponentControl.reverseFlag xp yp er)))=
      CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar :=
    (output_and_retained xp yp xs ys sx sy er ar).1
  rw [cells_retained,hr]
  simp [MarkedBitDifference.copyFinal,BinaryToUnaryControl.tapeCells,MarkedZeroPadding.marked,
    MarkedZeroPadding.bits]
  omega

private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)
private theorem running_prefix (out:ZTape) {n:Nat} {s t:CopiedExponentDyadicAddition.State}
    (h:CopiedExponentDyadicAddition.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.running s out)=.running (CopiedExponentDyadicAddition.run k s) out := by
  induction h generalizing k with
  | nil s =>
      have he:k=0:=by omega
      subst k
      rfl
  | @next n s t live tail ih => cases k with
    | zero => rfl
    | succ k =>
        have hn:finished s=false := by
          cases he:finished s
          · rfl
          · exact False.elim (live ((finished_iff s).mp he))
        simpa only [run,step,hn,Bool.false_eq_true,if_false,CopiedExponentDyadicAddition.run] using
          ih k (by omega)
private theorem extraction_halt_run (s:MarkedBitDifference.State) (hs:s.phase=.halt) (k:Nat) :
    MarkedBitDifference.run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [MarkedBitDifference.run,MarkedBitDifference.step,hs] using ih
private theorem extraction_trace_storage {n:Nat} {s t:MarkedBitDifference.State}
    (h:MarkedBitDifference.Trace n s t) (ht:t.phase=.halt) (k:Nat) :
    MarkedBitDifference.cells (MarkedBitDifference.run k s)≤MarkedBitDifference.cells t := by
  induction h generalizing k with
  | nil s => rw [extraction_halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (MarkedBitDifference.step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k
private theorem extraction_prefix_storage (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (.extracting (finalFrame xp yp xs ys sx sy er ar)
      ⟨MarkedBitAddition.marked (sumRows xp yp xs ys sx sy er ar),⟨[],[]⟩,
        SequentialBitAddition.clearRegisters,EncodedExponentControl.reverseFlag xp yp er,.writeOutputLeft⟩)) ≤
      cells (final xp yp xs ys sx sy er ar) := by
  rw [extracting_run]
  have h:=extraction_trace_storage
    (MarkedBitDifference.extraction_exact (sumRows xp yp xs ys sx sy er ar)
      SequentialBitAddition.clearRegisters (EncodedExponentControl.reverseFlag xp yp er)) rfl k
  exact Nat.add_le_add_left h _

/-- Full thirteen-tape prefix accounting, including the new output markers,
both completed earlier outputs, every spectator and terminal stuttering. -/
theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar))≤
      EncodedDyadicAdditionSpace.bound xp yp xs ys er+
        (EncodedDyadicAddition.commonWord xp yp er).length+2+
        (sumRows xp yp xs ys sx sy er ar).length+2 := by
  have ha:=CopiedExponentDyadicAddition.machine_exact xp yp xs ys sx sy bl br er ar
  have he:run (CopiedExponentDyadicAddition.totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)=
      .running (CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩ :=
    trace_sound (running_trace ⟨[],[]⟩ ha)
  by_cases hk:k≤CopiedExponentDyadicAddition.totalTime xp yp xs ys er
  · change cells (run k (.running _ _))≤_
    rw [running_prefix _ ha k hk]
    have hs:=CopiedExponentDyadicAddition.machine_prefix_storage xp yp xs ys sx sy bl br er ar k
    simp only [cells,BinaryToUnaryControl.tapeCells,List.length_nil,Nat.add_zero]
    omega
  · have hsplit:k=(CopiedExponentDyadicAddition.totalTime xp yp xs ys er+1)+(k-(CopiedExponentDyadicAddition.totalTime xp yp xs ys er+1)) := by omega
    rw [hsplit,run_add,run_add,he]
    change cells (run _ (step (.running (CopiedExponentDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)))≤_
    rw [handoff]
    have hp:=extraction_prefix_storage xp yp xs ys sx sy er ar (k-(CopiedExponentDyadicAddition.totalTime xp yp xs ys er+1))
    rw [final_cells] at hp
    have hs:=CopiedExponentDyadicAddition.machine_prefix_storage xp yp xs ys sx sy bl br er ar
      (CopiedExponentDyadicAddition.totalTime xp yp xs ys er)
    rw [(CopiedExponentDyadicAddition.machine_result xp yp xs ys sx sy bl br er ar).1] at hs
    omega

end ExtractedDyadicOutput
#print axioms ExtractedDyadicOutput.handoff
#print axioms ExtractedDyadicOutput.output_and_retained
#print axioms ExtractedDyadicOutput.machine_exact
#print axioms ExtractedDyadicOutput.machine_result
#print axioms ExtractedDyadicOutput.numerator_encoding
#print axioms ExtractedDyadicOutput.extracting_run
#print axioms ExtractedDyadicOutput.cells_retained
#print axioms ExtractedDyadicOutput.final_cells
#print axioms ExtractedDyadicOutput.machine_prefix_storage
#check @ExtractedDyadicOutput.machine_result
#check @ExtractedDyadicOutput.numerator_encoding

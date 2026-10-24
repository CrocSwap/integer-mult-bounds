import ExtractedDyadicOutput
import MarkedSignedWordSplit

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
One paid handoff feeds the actual extracted numerator to the accepted delayed-
bit sign splitter. Twelve other tapes remain explicit spectators. The fourteen-
tape machine returns a marked low numerator, its observed Boolean sign, and
the already physically copied common-exponent tape. All thirteen preceding
tapes and finite fields are reconstructed exactly at the endpoint.
No arithmetic kernel, copy scan, sign oracle or free output allocation is
introduced. The two new adapter registers may be dirty and are overwritten;
no arbitrary old scratch inverse is claimed. Initial encoded inputs and fresh
independent output allocation remain supplied. The complete time still contains
numeric-magnitude-dependent unary production. No global selected runtime bound.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace ReusableDyadicOutput
open EncodedDyadicAddition (ZTape ATape)
open SequentialBitAddition (Registers)

/-- The eleven old extraction spectators and its original sum source remain
twelve actual tapes. Registers/reverse/phase are finite saved fields only. -/
structure Frame where
  previous : ExtractedDyadicOutput.Frame
  source : ATape
  registers : Registers
  reverse : Bool
  phase : MarkedBitDifference.Phase
  deriving DecidableEq
inductive State where
  | running (s:ExtractedDyadicOutput.State) (output:ZTape) (held oldSign:Bool)
  | separating (f:Frame) (s:MarkedSignedWordSplit.State)
  deriving DecidableEq

def finished : ExtractedDyadicOutput.State → Bool
  | .running _ _ => false
  | .extracting _ s => s.phase==.halt
private theorem finished_iff (s:ExtractedDyadicOutput.State) :
    finished s=true ↔ ExtractedDyadicOutput.Halted s := by
  cases s <;> simp [finished,ExtractedDyadicOutput.Halted]
def enterSplit (s:ExtractedDyadicOutput.State) (out:ZTape) (held oldSign:Bool) : State :=
  match s with
  | .extracting f a => .separating ⟨f,a.tape,a.registers,a.reverse,a.phase⟩
      ⟨a.output,out,held,oldSign,.setup⟩
  | _ => .running s out held oldSign

def step : State → State
  | .running s out held oldSign =>
      if finished s then enterSplit s out held oldSign
      else .running (ExtractedDyadicOutput.step s) out held oldSign
  | .separating f s => .separating f (MarkedSignedWordSplit.step s)
def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
def Halted : State → Prop
  | .running .. => False
  | .separating _ s => s.phase=.halt
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
private theorem running_trace (out:ZTape) (held oldSign:Bool) {n:Nat} {s t:ExtractedDyadicOutput.State}
    (h:ExtractedDyadicOutput.Trace n s t) : Trace n (.running s out held oldSign) (.running t out held oldSign) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      refine Trace.next (by simp [Halted]) ?_
      have hn:finished s=false := by
        cases he:finished s
        · rfl
        · exact False.elim (live ((finished_iff s).mp he))
      simpa only [step,hn,Bool.false_eq_true,if_false] using ih
private theorem separating_trace (f:Frame) {n:Nat} {s t:MarkedSignedWordSplit.State}
    (h:MarkedSignedWordSplit.Trace n s t) : Trace n (.separating f s) (.separating f t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

/-- These are proof observations of the already executed arithmetic. They
never appear in the transition or determine an uncharged runtime branch. -/
def lowScan (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : SequentialBitAddition.Result :=
  SequentialBitAddition.scan
    (SignedWordAlignment.aligned
      (MarkedZeroPadding.padded (EncodedDyadicAddition.leftShift xp yp er) xs) sx
      (MarkedZeroPadding.padded (EncodedDyadicAddition.rightShift xp yp er) ys) sy)
    (SequentialBitAddition.zeroCarry (MarkedPairLayout.clearScratch ar))
def lowWord (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : List Bool :=
  let low:=lowScan xp yp xs ys sx sy er ar
  low.output++[SequentialBitAddition.sumBit sx sy low.registers.carry]
def signBit (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Bool :=
  SequentialBitAddition.sumBit sx sy
    (SequentialBitAddition.carryBit sx sy (lowScan xp yp xs ys sx sy er ar).registers.carry)

theorem word_eq (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    (ExtractedDyadicOutput.sumRows xp yp xs ys sx sy er ar).map Prod.snd=
      lowWord xp yp xs ys sx sy er ar++[signBit xp yp xs ys sx sy er ar] := by
  simpa only [lowWord,lowScan,signBit,List.append_assoc,List.cons_append,List.nil_append] using
    (ExtractedDyadicOutput.numerator_encoding xp yp xs ys sx sy er ar).1

def finalFrame (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Frame :=
  ⟨ExtractedDyadicOutput.finalFrame xp yp xs ys sx sy er ar,
    MarkedBitAddition.marked (ExtractedDyadicOutput.sumRows xp yp xs ys sx sy er ar),
    SequentialBitAddition.clearRegisters,EncodedExponentControl.reverseFlag xp yp er,.halt⟩
def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) : State :=
  .running (ExtractedDyadicOutput.initial xp yp xs ys sx sy bl br er ar) ⟨[],[]⟩ held oldSign
def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .separating (finalFrame xp yp xs ys sx sy er ar)
    (MarkedSignedWordSplit.final (lowWord xp yp xs ys sx sy er ar) (signBit xp yp xs ys sx sy er ar))
def totalTime (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar+1+
    MarkedSignedWordSplit.totalTime (lowWord xp yp xs ys sx sy er ar)

def retained : State → ExtractedDyadicOutput.State
  | .running s _ _ _ => s
  | .separating f s => .extracting f.previous ⟨f.source,s.input,f.registers,f.reverse,f.phase⟩
def outputTape : State → ZTape
  | .running _ out _ _ => out
  | .separating _ s => s.output
def outputSign : State → Bool
  | .running _ _ _ sign => sign
  | .separating _ s => s.sign
def exponentTape : State → ZTape
  | .running s _ _ _ => CopiedExponentDyadicAddition.outputTape (ExtractedDyadicOutput.retained s)
  | .separating f _ => f.previous.exponentCopy.outputTape

theorem handoff (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) (held oldSign:Bool) :
    step (.running (ExtractedDyadicOutput.final xp yp xs ys sx sy er ar) ⟨[],[]⟩ held oldSign)=
      .separating (finalFrame xp yp xs ys sx sy er ar)
        (MarkedSignedWordSplit.initial (lowWord xp yp xs ys sx sy er ar)
          (signBit xp yp xs ys sx sy er ar) held oldSign) := by
  change State.separating _ ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits
      ((ExtractedDyadicOutput.sumRows xp yp xs ys sx sy er ar).map Prod.snd)),_,_,_,_⟩=_
  rw [word_eq]
  rfl

theorem final_retained (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    retained (final xp yp xs ys sx sy er ar)=ExtractedDyadicOutput.final xp yp xs ys sx sy er ar := by
  change ExtractedDyadicOutput.State.extracting _ ⟨_,MarkedZeroPadding.marked (MarkedZeroPadding.bits
      (lowWord xp yp xs ys sx sy er ar++[signBit xp yp xs ys sx sy er ar])),_,_,_⟩=_
  rw [← word_eq]
  rfl

theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) :
    Trace (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar held oldSign)
      (final xp yp xs ys sx sy er ar) := by
  have h:=running_trace ⟨[],[]⟩ held oldSign (ExtractedDyadicOutput.machine_exact xp yp xs ys sx sy bl br er ar)
  have hc:Trace 1 (.running (ExtractedDyadicOutput.final xp yp xs ys sx sy er ar) ⟨[],[]⟩ held oldSign)
      (.separating (finalFrame xp yp xs ys sx sy er ar)
        (MarkedSignedWordSplit.initial (lowWord xp yp xs ys sx sy er ar)
          (signBit xp yp xs ys sx sy er ar) held oldSign)) := by
    refine Trace.next (by simp [Halted]) ?_
    rw [handoff]
    exact Trace.nil _
  exact trace_trans (trace_trans h hc)
    (separating_trace (finalFrame xp yp xs ys sx sy er ar)
      (MarkedSignedWordSplit.split_exact (lowWord xp yp xs ys sx sy er ar)
        (signBit xp yp xs ys sx sy er ar) held oldSign))

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) :
    run (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar held oldSign)=
      final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    (∀ k<totalTime xp yp xs ys sx sy er ar,
      ¬Halted (run k (initial xp yp xs ys sx sy bl br er ar held oldSign))) ∧
    retained (final xp yp xs ys sx sy er ar)=ExtractedDyadicOutput.final xp yp xs ys sx sy er ar :=
  ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar held oldSign),rfl,
    trace_live (machine_exact xp yp xs ys sx sy bl br er ar held oldSign),final_retained xp yp xs ys sx sy er ar⟩

/-- Three real output fields: a marked low numerator, observed separate sign,
and physically copied denominator exponent. Value is inherited unchanged. -/
theorem output_representation (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    outputTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits (lowWord xp yp xs ys sx sy er ar)) ∧
    outputSign (final xp yp xs ys sx sy er ar)=signBit xp yp xs ys sx sy er ar ∧
    exponentTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits (EncodedDyadicAddition.commonWord xp yp er)) ∧
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨SequentialBitAddition.signedValue (lowWord xp yp xs ys sx sy er ar) (signBit xp yp xs ys sx sy er ar),
        CurrentMain.PairedBitXorScan.value (EncodedDyadicAddition.commonWord xp yp er)⟩ =
      (SequentialBitAddition.signedValue xs sx:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value xp)+
      (SequentialBitAddition.signedValue ys sy:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value yp) := by
  refine ⟨rfl,rfl,?_,?_⟩
  · simp [exponentTape,final,finalFrame,ExtractedDyadicOutput.finalFrame,
      ExtractedDyadicOutput.makeFrame,MarkedZeroPadding.final,MarkedZeroPadding.padded]
  · exact (ExtractedDyadicOutput.numerator_encoding xp yp xs ys sx sy er ar).2

def frameCells (f:Frame) : Nat := ExtractedDyadicOutput.frameCells f.previous+MarkedBitDifference.tapeCells f.source
def cells : State → Nat
  | .running s out _ _ => ExtractedDyadicOutput.cells s+BinaryToUnaryControl.tapeCells out
  | .separating f s => frameCells f+MarkedSignedWordSplit.cells s

theorem separating_run (f:Frame) (s:MarkedSignedWordSplit.State) (k:Nat) :
    run k (.separating f s)=.separating f (MarkedSignedWordSplit.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedSignedWordSplit.step s)
theorem cells_retained (f:Frame) (s:MarkedSignedWordSplit.State) :
    cells (.separating f s)=ExtractedDyadicOutput.cells (retained (.separating f s))+
      BinaryToUnaryControl.tapeCells s.output := by
  simp [cells,frameCells,retained,ExtractedDyadicOutput.cells,MarkedBitDifference.cells,
    MarkedBitDifference.tapeCells,MarkedSignedWordSplit.cells,MarkedSignedWordSplit.tapeCells,
    BinaryToUnaryControl.tapeCells]
  omega

theorem final_cells (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    cells (final xp yp xs ys sx sy er ar)=
      ExtractedDyadicOutput.cells (ExtractedDyadicOutput.final xp yp xs ys sx sy er ar)+
      (lowWord xp yp xs ys sx sy er ar).length+2 := by
  change cells (.separating _ _)=_
  have hr:=final_retained xp yp xs ys sx sy er ar
  change retained (.separating _ _)=_ at hr
  rw [cells_retained,hr]
  simp [MarkedSignedWordSplit.final,BinaryToUnaryControl.tapeCells,MarkedZeroPadding.marked,
    MarkedZeroPadding.bits]
  omega
private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)
private theorem running_prefix (out:ZTape) (held oldSign:Bool) {n:Nat} {s t:ExtractedDyadicOutput.State}
    (h:ExtractedDyadicOutput.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.running s out held oldSign)=.running (ExtractedDyadicOutput.run k s) out held oldSign := by
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
        simpa only [run,step,hn,Bool.false_eq_true,if_false,ExtractedDyadicOutput.run] using ih k (by omega)
private theorem split_prefix_storage (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers)
    (held oldSign:Bool) (k:Nat) :
    cells (run k (.separating (finalFrame xp yp xs ys sx sy er ar)
      (MarkedSignedWordSplit.initial (lowWord xp yp xs ys sx sy er ar)
        (signBit xp yp xs ys sx sy er ar) held oldSign)))≤cells (final xp yp xs ys sx sy er ar) := by
  rw [separating_run]
  have h:=MarkedSignedWordSplit.split_prefix_storage (lowWord xp yp xs ys sx sy er ar)
    (signBit xp yp xs ys sx sy er ar) held oldSign k
  have ht:MarkedSignedWordSplit.cells (MarkedSignedWordSplit.final (lowWord xp yp xs ys sx sy er ar)
      (signBit xp yp xs ys sx sy er ar))=2*(lowWord xp yp xs ys sx sy er ar).length+5 := by
    simp [MarkedSignedWordSplit.cells,MarkedSignedWordSplit.tapeCells,MarkedSignedWordSplit.final,
      MarkedZeroPadding.marked,MarkedZeroPadding.bits]
    omega
  rw [← ht] at h
  exact Nat.add_le_add_left h _

/-- Every physical tape is charged across the original computation, the
finite switch, sign separation and post-halt stuttering. -/
theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign:Bool) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar held oldSign))≤
      EncodedDyadicAdditionSpace.bound xp yp xs ys er+
      (EncodedDyadicAddition.commonWord xp yp er).length+2+
      (ExtractedDyadicOutput.sumRows xp yp xs ys sx sy er ar).length+2+
      (lowWord xp yp xs ys sx sy er ar).length+2 := by
  have ha:=ExtractedDyadicOutput.machine_exact xp yp xs ys sx sy bl br er ar
  have he:run (ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar)
      (initial xp yp xs ys sx sy bl br er ar held oldSign)=
      .running (ExtractedDyadicOutput.final xp yp xs ys sx sy er ar) ⟨[],[]⟩ held oldSign :=
    trace_sound (running_trace ⟨[],[]⟩ held oldSign ha)
  by_cases hk:k≤ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar
  · change cells (run k (.running _ _ _ _))≤_
    rw [running_prefix _ held oldSign ha k hk]
    have hs:=ExtractedDyadicOutput.machine_prefix_storage xp yp xs ys sx sy bl br er ar k
    simp only [cells,BinaryToUnaryControl.tapeCells,List.length_nil,Nat.add_zero]
    omega
  · have hsplit:k=(ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar+1)+
        (k-(ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar+1)) := by omega
    rw [hsplit,run_add,run_add,he]
    change cells (run _ (step (.running (ExtractedDyadicOutput.final xp yp xs ys sx sy er ar)
      ⟨[],[]⟩ held oldSign)))≤_
    rw [handoff]
    have hp:=split_prefix_storage xp yp xs ys sx sy er ar held oldSign
      (k-(ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar+1))
    rw [final_cells] at hp
    have hs:=ExtractedDyadicOutput.machine_prefix_storage xp yp xs ys sx sy bl br er ar
      (ExtractedDyadicOutput.totalTime xp yp xs ys sx sy er ar)
    rw [(ExtractedDyadicOutput.machine_result xp yp xs ys sx sy bl br er ar).1] at hs
    omega

end ReusableDyadicOutput
#print axioms ReusableDyadicOutput.word_eq
#print axioms ReusableDyadicOutput.handoff
#print axioms ReusableDyadicOutput.final_retained
#print axioms ReusableDyadicOutput.machine_exact
#print axioms ReusableDyadicOutput.machine_result
#print axioms ReusableDyadicOutput.output_representation
#print axioms ReusableDyadicOutput.separating_run
#print axioms ReusableDyadicOutput.cells_retained
#print axioms ReusableDyadicOutput.final_cells
#print axioms ReusableDyadicOutput.machine_prefix_storage
#check @ReusableDyadicOutput.machine_result
#check @ReusableDyadicOutput.output_representation

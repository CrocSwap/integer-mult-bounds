import EncodedDyadicAdditionSpace

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Execute the missing common-exponent output copy after the complete eleven-tape
addition. Its retained comparison flag selects the existing exponent word.
One charged switch passes that tape and the already constructed empty unary
control to the unchanged d=0 padder. Nine spectator tapes remain in CopyFrame;
the copy's three active tapes make twelve total. The original eleven tapes
are reconstructed and restored at the actual endpoint; the new tape contains
literal marked bits of the common denominator exponent. No copying, bit
encoding, allocation or comparison is hidden in an endpoint transformation.
Initial independent blank output and encoded input words remain premises.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CopiedExponentDyadicAddition
open EncodedDyadicAddition (ZTape ATape)
open SequentialBitAddition (Registers)

/-- Nine physical spectator tapes. sumState retains its three tapes. -/
structure CopyFrame where
  otherExponent : ZTape
  paired : ATape
  counter : ZTape
  magnitude : ZTape
  leftData : ZTape
  rightData : ZTape
  sumState : MarkedLayoutAddition.State
  savedRegisters : Registers
  borrow : Bool
  exponentLeftSign : Bool
  exponentRightSign : Bool
  reverse : Bool
  leftScratch : Bool
  rightScratch : Bool
  deriving DecidableEq

inductive State where
  | running (s:EncodedDyadicAddition.State) (output:ZTape)
  | copying (frame:CopyFrame) (s:MarkedZeroPadding.State)
  deriving DecidableEq

def finished : EncodedDyadicAddition.State → Bool
  | .adding _ _ (.sum _ _ _ _ _ _ (.addition _ _ _ _ s)) => s.phase==.body .halt
  | _ => false
private theorem finished_iff (s:EncodedDyadicAddition.State) :
    finished s=true ↔ EncodedDyadicAddition.Halted s := by
  cases s with
  | computing | zeroRight | ready => simp [finished,EncodedDyadicAddition.Halted]
  | adding f reverse s => cases s with
    | first | second => simp [finished,EncodedDyadicAddition.Halted,PaddedSignedAddition.Halted]
    | sum ld lc rd rc bl br s => cases s with
      | layout => simp [finished,EncodedDyadicAddition.Halted,PaddedSignedAddition.Halted,MarkedLayoutAddition.Halted]
      | addition => simp [finished,EncodedDyadicAddition.Halted,PaddedSignedAddition.Halted,MarkedLayoutAddition.Halted]

def selectedExponent (f:EncodedDyadicAddition.Frame) (reverse:Bool) : ZTape :=
  if reverse then f.rightExponent else f.leftExponent

def makeFrame (f:EncodedDyadicAddition.Frame) (reverse:Bool) (ld mag rd:ZTape) (bl br:Bool)
    (s:MarkedLayoutAddition.State) : CopyFrame :=
  ⟨if reverse then f.leftExponent else f.rightExponent,f.paired,f.counter,mag,ld,rd,s,
    f.savedRegisters,f.borrow,f.leftSign,f.rightSign,reverse,bl,br⟩

/-- This transition only selects tape ports and initializes finite control.
The following padder steps really read/write every output bit and marker. -/
def enterCopy (s:EncodedDyadicAddition.State) (out:ZTape) : State :=
  match s with
  | .adding f reverse (.sum ld mag rd zero bl br sum) =>
      .copying (makeFrame f reverse ld mag rd bl br sum)
        ⟨selectedExponent f reverse,zero,out,false,.writeLeft⟩
  | _ => .running s out

def step : State → State
  | .running s out => if finished s then enterCopy s out else .running (EncodedDyadicAddition.step s) out
  | .copying f s => .copying f (MarkedZeroPadding.step s)
def Halted : State → Prop
  | .running _ _ => False
  | .copying _ s => s.phase=.halt

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
private theorem running_trace (out:ZTape) {n:Nat} {s t:EncodedDyadicAddition.State}
    (h:EncodedDyadicAddition.Trace n s t) : Trace n (.running s out) (.running t out) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      refine Trace.next (by simp [Halted]) ?_
      have hn:finished s=false := by
        cases he:finished s
        · rfl
        · exact False.elim (live ((finished_iff s).mp he))
      simpa only [step,hn,Bool.false_eq_true,if_false] using ih
private theorem copy_trace (f:CopyFrame) {n:Nat} {s t:MarkedZeroPadding.State}
    (h:MarkedZeroPadding.Trace n s t) : Trace n (.copying f s) (.copying f t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

/-- Observe the same eleven original tapes while selected data/control heads
may be moving. No tape is duplicated inside the actual copy state. -/
def retained : State → EncodedDyadicAddition.State
  | .running s _ => s
  | .copying f s =>
      .adding ⟨if f.reverse then f.otherExponent else s.dataTape,
        if f.reverse then s.dataTape else f.otherExponent,
        f.paired,f.counter,f.savedRegisters,f.borrow,f.exponentLeftSign,f.exponentRightSign⟩ f.reverse
        (.sum f.leftData f.magnitude f.rightData s.controlTape f.leftScratch f.rightScratch f.sumState)
def outputTape : State → ZTape
  | .running _ out => out
  | .copying _ s => s.outputTape

def finalFrame (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : CopyFrame :=
  makeFrame (EncodedDyadicAddition.finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.ticks (EncodedExponentControl.magnitude xp yp er)))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) false false
    (MarkedLayoutAddition.final
      (MarkedZeroPadding.padded (EncodedDyadicAddition.leftShift xp yp er) xs)
      (MarkedZeroPadding.padded (EncodedDyadicAddition.rightShift xp yp er) ys) sx sy ar)

def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) : State :=
  .running (EncodedDyadicAddition.initial xp yp xs ys sx sy bl br er ar) ⟨[],[]⟩
def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .copying (finalFrame xp yp xs ys sx sy er ar)
    (MarkedZeroPadding.final 0 (EncodedDyadicAddition.commonWord xp yp er))
def totalTime (xp yp xs ys:List Bool) (er:Registers) : Nat :=
  EncodedDyadicAddition.totalTime xp yp xs ys er+1+
    (6*(EncodedDyadicAddition.commonWord xp yp er).length+14)

theorem handoff (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    step (.running (EncodedDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)=
      .copying (finalFrame xp yp xs ys sx sy er ar)
        (MarkedZeroPadding.initial 0 (EncodedDyadicAddition.commonWord xp yp er) false) := by
  cases hf:EncodedExponentControl.reverseFlag xp yp er
  all_goals
    simp [step,finished,enterCopy,EncodedDyadicAddition.final,EncodedDyadicAddition.route,
      EncodedDyadicAddition.swapControls,PaddedSignedAddition.final,PaddedSignedAddition.sumFrame,
      EncodedDyadicAddition.leftShift,EncodedDyadicAddition.rightShift,hf,finalFrame,
      EncodedDyadicAddition.commonWord,selectedExponent,EncodedDyadicAddition.finalFrame,
      MarkedLayoutAddition.final,MarkedBitAddition.final,MarkedZeroPadding.initial]

/-- Restore the complete original eleven-tape endpoint, while the twelfth
contains the selected exponent bits and has returned to its own L marker. -/
theorem output_and_retained (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    retained (final xp yp xs ys sx sy er ar)=EncodedDyadicAddition.final xp yp xs ys sx sy er ar ∧
    outputTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits (EncodedDyadicAddition.commonWord xp yp er)) := by
  constructor
  · cases hf:EncodedExponentControl.reverseFlag xp yp er
    all_goals
      simp [retained,final,finalFrame,makeFrame,MarkedZeroPadding.final,
        EncodedDyadicAddition.commonWord,hf,EncodedDyadicAddition.final,
        EncodedDyadicAddition.route,EncodedDyadicAddition.swapControls,
        PaddedSignedAddition.final,PaddedSignedAddition.sumFrame,
        EncodedDyadicAddition.leftShift,EncodedDyadicAddition.rightShift,EncodedDyadicAddition.finalFrame]
  · simp [outputTape,final,MarkedZeroPadding.final,MarkedZeroPadding.padded]

theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    Trace (totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)
      (final xp yp xs ys sx sy er ar) := by
  have h:=running_trace ⟨[],[]⟩ (EncodedDyadicAddition.machine_exact xp yp xs ys sx sy bl br er ar)
  have hc:Trace 1 (.running (EncodedDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)
      (.copying (finalFrame xp yp xs ys sx sy er ar)
        (MarkedZeroPadding.initial 0 (EncodedDyadicAddition.commonWord xp yp er) false)) := by
    refine Trace.next (by simp [Halted]) ?_
    rw [handoff]
    exact Trace.nil _
  have hp:=copy_trace (finalFrame xp yp xs ys sx sy er ar)
    (MarkedZeroPadding.padding_exact 0 (EncodedDyadicAddition.commonWord xp yp er) false)
  simpa only [Nat.zero_add] using trace_trans (trace_trans h hc) hp

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    run (totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)=final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    (∀ k<totalTime xp yp xs ys er,¬Halted (run k (initial xp yp xs ys sx sy bl br er ar))) ∧
    retained (final xp yp xs ys sx sy er ar)=EncodedDyadicAddition.final xp yp xs ys sx sy er ar ∧
    outputTape (final xp yp xs ys sx sy er ar)=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits (EncodedDyadicAddition.commonWord xp yp er)) :=
  ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar),rfl,
    trace_live (machine_exact xp yp xs ys sx sy bl br er ar),output_and_retained xp yp xs ys sx sy er ar⟩

def frameCells (f:CopyFrame) : Nat :=
  BinaryToUnaryControl.tapeCells f.otherExponent+MarkedBitDifference.tapeCells f.paired+
  BinaryToUnaryControl.tapeCells f.counter+BinaryToUnaryControl.tapeCells f.magnitude+
  BinaryToUnaryControl.tapeCells f.leftData+BinaryToUnaryControl.tapeCells f.rightData+
  MarkedLayoutAddition.cells f.sumState
def cells : State → Nat
  | .running s out => EncodedDyadicAddition.cells s+BinaryToUnaryControl.tapeCells out
  | .copying f s => frameCells f+MarkedZeroPadding.cells s

/-- The actual copy step is a delegated padder step with nine fixed spectators. -/
theorem copying_run (f:CopyFrame) (s:MarkedZeroPadding.State) (k:Nat) :
    run k (.copying f s)=.copying f (MarkedZeroPadding.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedZeroPadding.step s)

/-- Twelve distinct tapes are counted: the retained eleven plus the new output. -/
theorem cells_retained (f:CopyFrame) (s:MarkedZeroPadding.State) :
    cells (.copying f s)=EncodedDyadicAddition.cells (retained (.copying f s))+
      BinaryToUnaryControl.tapeCells s.outputTape := by
  cases hf:f.reverse <;>
    simp [cells,frameCells,retained,EncodedDyadicAddition.cells,EncodedDyadicAddition.frameCells,
      PaddedSignedAddition.cells,MarkedZeroPadding.cells,MarkedZeroPadding.tapeCells,
      BinaryToUnaryControl.tapeCells,MarkedBitDifference.tapeCells,MarkedPairLayout.tapeCells,hf] <;> omega

/-- The new output is genuinely allocated and both markers are counted. -/
theorem final_cells (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    cells (final xp yp xs ys sx sy er ar)=
      EncodedDyadicAddition.cells (EncodedDyadicAddition.final xp yp xs ys sx sy er ar)+
      (EncodedDyadicAddition.commonWord xp yp er).length+2 := by
  change cells (.copying _ _)=_
  have hr:retained (.copying (finalFrame xp yp xs ys sx sy er ar)
      (MarkedZeroPadding.final 0 (EncodedDyadicAddition.commonWord xp yp er)))=
      EncodedDyadicAddition.final xp yp xs ys sx sy er ar :=
    (output_and_retained xp yp xs ys sx sy er ar).1
  rw [cells_retained,hr]
  simp [MarkedZeroPadding.final,MarkedZeroPadding.padded,BinaryToUnaryControl.tapeCells,
    MarkedZeroPadding.marked,MarkedZeroPadding.bits]
  omega

private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)

private theorem running_prefix (out:ZTape) {n:Nat} {s t:EncodedDyadicAddition.State}
    (h:EncodedDyadicAddition.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.running s out)=.running (EncodedDyadicAddition.run k s) out := by
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
        simpa only [run,step,hn,Bool.false_eq_true,if_false,EncodedDyadicAddition.run] using
          ih k (by omega)

private theorem copy_prefix_storage (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (.copying (finalFrame xp yp xs ys sx sy er ar)
      (MarkedZeroPadding.initial 0 (EncodedDyadicAddition.commonWord xp yp er) false))) ≤
      cells (final xp yp xs ys sx sy er ar) := by
  rw [copying_run]
  have hp:=MarkedZeroPadding.padding_prefix_storage 0 (EncodedDyadicAddition.commonWord xp yp er) false k
  simp only [cells,final]
  simp only [MarkedZeroPadding.cells,MarkedZeroPadding.final,MarkedZeroPadding.tapeCells,
    MarkedZeroPadding.marked,MarkedZeroPadding.bits,MarkedZeroPadding.ticks,MarkedZeroPadding.padded,
    List.length_nil,List.length_cons,List.length_append,List.length_map,List.length_replicate] at hp ⊢
  omega

/-- All prefixes count the twelfth output tape and the retained eleven tapes,
including the charged switch and the complete copy/rewind/cleanup phase. -/
theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar))≤
      EncodedDyadicAdditionSpace.bound xp yp xs ys er+
        (EncodedDyadicAddition.commonWord xp yp er).length+2 := by
  have ha:=EncodedDyadicAddition.machine_exact xp yp xs ys sx sy bl br er ar
  have he:run (EncodedDyadicAddition.totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)=
      .running (EncodedDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩ :=
    trace_sound (running_trace ⟨[],[]⟩ ha)
  by_cases hk:k≤EncodedDyadicAddition.totalTime xp yp xs ys er
  · change cells (run k (.running _ _))≤_
    rw [running_prefix _ ha k hk]
    have hs:=EncodedDyadicAdditionSpace.machine_prefix_storage xp yp xs ys sx sy bl br er ar k
    simp only [cells,BinaryToUnaryControl.tapeCells,List.length_nil,Nat.add_zero]
    omega
  · have hsplit:k=(EncodedDyadicAddition.totalTime xp yp xs ys er+1)+(k-(EncodedDyadicAddition.totalTime xp yp xs ys er+1)) := by omega
    rw [hsplit,run_add,run_add,he]
    change cells (run _ (step (.running (EncodedDyadicAddition.final xp yp xs ys sx sy er ar) ⟨[],[]⟩)))≤_
    rw [handoff]
    have hp:=copy_prefix_storage xp yp xs ys sx sy er ar (k-(EncodedDyadicAddition.totalTime xp yp xs ys er+1))
    rw [final_cells] at hp
    have hs:=EncodedDyadicAdditionSpace.machine_prefix_storage xp yp xs ys sx sy bl br er ar
      (EncodedDyadicAddition.totalTime xp yp xs ys er)
    rw [(EncodedDyadicAddition.machine_result xp yp xs ys sx sy bl br er ar).1] at hs
    omega

end CopiedExponentDyadicAddition
#print axioms CopiedExponentDyadicAddition.handoff
#print axioms CopiedExponentDyadicAddition.output_and_retained
#print axioms CopiedExponentDyadicAddition.machine_exact
#print axioms CopiedExponentDyadicAddition.machine_result
#print axioms CopiedExponentDyadicAddition.copying_run
#print axioms CopiedExponentDyadicAddition.cells_retained
#print axioms CopiedExponentDyadicAddition.final_cells
#print axioms CopiedExponentDyadicAddition.machine_prefix_storage
#check @CopiedExponentDyadicAddition.machine_result
#check @CopiedExponentDyadicAddition.final_cells

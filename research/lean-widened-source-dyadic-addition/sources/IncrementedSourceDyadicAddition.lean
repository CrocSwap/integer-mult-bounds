import MarkedBinaryIncrement
import ReusableDyadicOutput

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
One charged finite overflow branch joins the actual fixed-width incremented
source-exponent working tape to the accepted fourteen-tape exact adder. The
other thirteen tapes are explicit spectators during increment. The handoff
rearranges only controller records, reusing every physical field exactly once;
it neither decodes a word nor constructs a fresh tape. Overflow halts with the
actual modular counter state retained. Capacity is required only for the
successful half-source result. The convention is numerator / 2^exponent.
The supplied source-exponent working word is changed in place; preservation
of an original packed source requires the separate paid acquisition/caller.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace IncrementedSourceDyadicAddition
open EncodedDyadicAddition (ZTape ATape)
open SequentialBitAddition (Registers)
open CurrentMain.PairedBitXorScan (value)

/-- Thirteen actual spectator tapes: four here, six in cargo, three outputs. -/
structure Frame where
  leftExponent : ZTape
  paired : ATape
  counter : ZTape
  control : ZTape
  cargo : EncodedDyadicAddition.Cargo
  exponentOutput : ZTape
  numeratorOutput : ZTape
  lowOutput : ZTape
  exponentRegisters : Registers
  held : Bool
  oldSign : Bool
  deriving DecidableEq

def enter (f:Frame) (rightExponent:ZTape) : ReusableDyadicOutput.State :=
  .running (.running (.running
    (.computing (.layout
      ⟨f.leftExponent,rightExponent,f.paired,f.exponentRegisters,false,false,.writeLeft⟩
      f.counter f.control) f.cargo)
    f.exponentOutput) f.numeratorOutput) f.lowOutput f.held f.oldSign

inductive State where
  | incrementing (f:Frame) (s:MarkedBinaryIncrement.State)
  | adding (s:ReusableDyadicOutput.State) (overflow:Bool)
  | rejected (f:Frame) (s:MarkedBinaryIncrement.State)
  deriving DecidableEq

def step : State → State
  | .incrementing f s =>
      if s.phase=.halt then
        if s.overflow then .rejected f s else .adding (enter f s.tape) s.overflow
      else .incrementing f (MarkedBinaryIncrement.step s)
  | .adding s flag => .adding (ReusableDyadicOutput.step s) flag
  | .rejected f s => .rejected f s

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
def Halted : State → Prop
  | .incrementing .. => False
  | .adding s _ => ReusableDyadicOutput.Halted s
  | .rejected .. => True
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
private theorem incrementing_trace (f:Frame) {n:Nat} {s t:MarkedBinaryIncrement.State}
    (h:MarkedBinaryIncrement.Trace n s t) : Trace n (.incrementing f s) (.incrementing f t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,live,if_false] using ih
private theorem adding_trace (flag:Bool) {n:Nat} {s t:ReusableDyadicOutput.State}
    (h:ReusableDyadicOutput.Trace n s t) : Trace n (.adding s flag) (.adding t flag) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def initialFrame (xp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) : Frame :=
  ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits xp),⟨[],[]⟩,⟨[],[]⟩,⟨[],[]⟩,
    EncodedDyadicAddition.cargo xs ys sx sy bl br ar,⟨[],[]⟩,⟨[],[]⟩,⟨[],[]⟩,er,held,oldSign⟩
def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) : State :=
  .incrementing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (MarkedBinaryIncrement.initial yp oldFlag)
def incremented (yp:List Bool) : List Bool := RippleCounter.updated true yp
def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .adding (ReusableDyadicOutput.final xp (incremented yp) xs ys sx sy er ar) false
def totalTime (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  MarkedBinaryIncrement.totalTime yp+1+
    ReusableDyadicOutput.totalTime xp (incremented yp) xs ys sx sy er ar

/-- This equality checks actual tape/head compatibility. It is not a runtime
reconstruction from the proof observations xp/yp/xs/ys. -/
theorem enter_initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) :
    enter (initialFrame xp xs ys sx sy bl br er ar held oldSign)
      (MarkedZeroPadding.marked (MarkedZeroPadding.bits yp))=
    ReusableDyadicOutput.initial xp yp xs ys sx sy bl br er ar held oldSign := rfl

theorem handoff (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool)
    (capacity:value yp+1<2^yp.length) :
    step (.incrementing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (MarkedBinaryIncrement.final yp))=
      .adding (ReusableDyadicOutput.initial xp (incremented yp) xs ys sx sy bl br er ar held oldSign) false := by
  have hf:=(MarkedBinaryIncrement.capacity_iff yp).mpr capacity
  simp only [step,MarkedBinaryIncrement.final,if_true,hf,Bool.false_eq_true,if_false]
  exact congrArg (fun s=>State.adding s false) (enter_initial xp (incremented yp) xs ys sx sy bl br er ar held oldSign)

theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) (capacity:value yp+1<2^yp.length) :
    Trace (totalTime xp yp xs ys sx sy er ar)
      (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag) (final xp yp xs ys sx sy er ar) := by
  have hp:=incrementing_trace (initialFrame xp xs ys sx sy bl br er ar held oldSign)
    (MarkedBinaryIncrement.increment_exact yp oldFlag)
  have hs:Trace 1
      (.incrementing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (MarkedBinaryIncrement.final yp))
      (.adding (ReusableDyadicOutput.initial xp (incremented yp) xs ys sx sy bl br er ar held oldSign) false) := by
    apply Trace.next (by simp [Halted])
    rw [handoff xp yp xs ys sx sy bl br er ar held oldSign capacity]
    exact Trace.nil _
  exact trace_trans (trace_trans hp hs)
    (adding_trace false (ReusableDyadicOutput.machine_exact xp (incremented yp) xs ys sx sy bl br er ar held oldSign))

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) (capacity:value yp+1<2^yp.length) :
    run (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
      final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    ∀ k<totalTime xp yp xs ys sx sy er ar,
      ¬Halted (run k (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)) :=
  ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar held oldSign oldFlag capacity),
    rfl,trace_live (machine_exact xp yp xs ys sx sy bl br er ar held oldSign oldFlag capacity)⟩

/-- Overflow is an executed finite branch, not an assumed well-formed exit. -/
theorem overflow_result (f:Frame) (yp:List Bool) (oldFlag:Bool)
    (overflow:RippleCounter.overflow true yp=true) :
    Trace (MarkedBinaryIncrement.totalTime yp+1) (.incrementing f (MarkedBinaryIncrement.initial yp oldFlag))
      (.rejected f (MarkedBinaryIncrement.final yp)) := by
  apply trace_trans (incrementing_trace f (MarkedBinaryIncrement.increment_exact yp oldFlag))
  apply Trace.next (by simp [Halted])
  simpa [step,MarkedBinaryIncrement.final,overflow] using Trace.nil (.rejected f (MarkedBinaryIncrement.final yp))

/-- Exact denominator convention: incrementing the exponent halves the value
while leaving the numerator untouched. Capacity is the actual counter domain. -/
theorem output_value (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers)
    (capacity:value yp+1<2^yp.length) :
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨SequentialBitAddition.signedValue
          (ReusableDyadicOutput.lowWord xp (incremented yp) xs ys sx sy er ar)
          (ReusableDyadicOutput.signBit xp (incremented yp) xs ys sx sy er ar),
        value (EncodedDyadicAddition.commonWord xp (incremented yp) er)⟩ =
      (SequentialBitAddition.signedValue xs sx:Real)/(2:Real)^(value xp)+
      ((SequentialBitAddition.signedValue ys sy:Real)/(2:Real)^(value yp))/2 := by
  have h:=(ReusableDyadicOutput.output_representation xp (incremented yp) xs ys sx sy er ar).2.2.2
  have hv: value (incremented yp)=value yp+1 :=
    (MarkedBinaryIncrement.increment_without_overflow yp false capacity).2.2
  rw [hv,pow_succ,← div_div] at h
  exact h

def frameCells (f:Frame) : Nat :=
  BinaryToUnaryControl.tapeCells f.leftExponent+MarkedBitDifference.tapeCells f.paired+
  BinaryToUnaryControl.tapeCells f.counter+BinaryToUnaryControl.tapeCells f.control+
  EncodedDyadicAddition.cargoCells f.cargo+
  BinaryToUnaryControl.tapeCells f.exponentOutput+BinaryToUnaryControl.tapeCells f.numeratorOutput+
  BinaryToUnaryControl.tapeCells f.lowOutput
def cells : State → Nat
  | .incrementing f s | .rejected f s => frameCells f+MarkedBinaryIncrement.cells s
  | .adding s _ => ReusableDyadicOutput.cells s

theorem enter_cells (f:Frame) (t:ZTape) :
    ReusableDyadicOutput.cells (enter f t)=frameCells f+BinaryToUnaryControl.tapeCells t := by
  simp only [enter,ReusableDyadicOutput.cells,ExtractedDyadicOutput.cells,CopiedExponentDyadicAddition.cells,
    EncodedDyadicAddition.cells,EncodedExponentControl.cells,MarkedPairLayout.cells,frameCells,
    MarkedPairLayout.tapeCells,MarkedBitDifference.tapeCells,BinaryToUnaryControl.tapeCells]
  omega

theorem initial_cells (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign oldFlag:Bool) :
    cells (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
      xp.length+yp.length+xs.length+ys.length+8 := by
  simp [initial,initialFrame,cells,frameCells,EncodedDyadicAddition.cargo,EncodedDyadicAddition.cargoCells,
    MarkedBinaryIncrement.initial,MarkedBinaryIncrement.cells,MarkedZeroPadding.marked,MarkedZeroPadding.bits,
    BinaryToUnaryControl.tapeCells,MarkedBitDifference.tapeCells]
  omega

private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)
private theorem incrementing_prefix (f:Frame) {n:Nat} {s t:MarkedBinaryIncrement.State}
    (h:MarkedBinaryIncrement.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.incrementing f s)=.incrementing f (MarkedBinaryIncrement.run k s) := by
  induction h generalizing k with
  | nil s =>
      have he:k=0:=by omega
      subst k
      rfl
  | next live tail ih => cases k with
    | zero => rfl
    | succ k => simpa only [run,step,live,if_false,MarkedBinaryIncrement.run] using ih k (by omega)
theorem adding_run (s:ReusableDyadicOutput.State) (flag:Bool) (k:Nat) :
    run k (.adding s flag)=.adding (ReusableDyadicOutput.run k s) flag := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (ReusableDyadicOutput.step s)

def additionBound (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  EncodedDyadicAdditionSpace.bound xp (incremented yp) xs ys er+
  (EncodedDyadicAddition.commonWord xp (incremented yp) er).length+2+
  (ExtractedDyadicOutput.sumRows xp (incremented yp) xs ys sx sy er ar).length+2+
  (ReusableDyadicOutput.lowWord xp (incremented yp) xs ys sx sy er ar).length+2

theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) (capacity:value yp+1<2^yp.length) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag))≤
      max (xp.length+yp.length+xs.length+ys.length+8) (additionBound xp yp xs ys sx sy er ar) := by
  have hi:=MarkedBinaryIncrement.increment_exact yp oldFlag
  by_cases hk:k≤MarkedBinaryIncrement.totalTime yp
  · change cells (run k (.incrementing _ _))≤_
    rw [incrementing_prefix _ hi k hk]
    have hb:=MarkedBinaryIncrement.increment_prefix_storage yp oldFlag k
    have he:=initial_cells xp yp xs ys sx sy bl br er ar held oldSign oldFlag
    have hv:MarkedBinaryIncrement.cells (MarkedBinaryIncrement.initial yp oldFlag)=yp.length+2 := by
      simp [MarkedBinaryIncrement.cells,MarkedBinaryIncrement.initial,MarkedZeroPadding.marked,MarkedZeroPadding.bits]
    change frameCells _+MarkedBinaryIncrement.cells _=_ at he
    rw [hv] at he
    apply Nat.le_trans _ (Nat.le_max_left _ _)
    change frameCells _+MarkedBinaryIncrement.cells _≤_
    omega
  · have hp:run (MarkedBinaryIncrement.totalTime yp)
        (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
        .incrementing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (MarkedBinaryIncrement.final yp) :=
      trace_sound (incrementing_trace _ hi)
    have hs:k=(MarkedBinaryIncrement.totalTime yp+1)+(k-(MarkedBinaryIncrement.totalTime yp+1)) := by omega
    rw [hs,run_add,run_add,hp]
    rw [show ∀ s:State,run 1 s=step s from fun _=>rfl]
    rw [handoff xp yp xs ys sx sy bl br er ar held oldSign capacity,adding_run]
    exact (ReusableDyadicOutput.machine_prefix_storage xp (incremented yp) xs ys sx sy bl br er ar held oldSign _).trans
      (Nat.le_max_right _ _)

end IncrementedSourceDyadicAddition
#print axioms IncrementedSourceDyadicAddition.enter_initial
#print axioms IncrementedSourceDyadicAddition.handoff
#print axioms IncrementedSourceDyadicAddition.machine_exact
#print axioms IncrementedSourceDyadicAddition.machine_result
#print axioms IncrementedSourceDyadicAddition.overflow_result
#print axioms IncrementedSourceDyadicAddition.output_value
#print axioms IncrementedSourceDyadicAddition.enter_cells
#print axioms IncrementedSourceDyadicAddition.initial_cells
#print axioms IncrementedSourceDyadicAddition.machine_prefix_storage
#check @IncrementedSourceDyadicAddition.machine_result
#check @IncrementedSourceDyadicAddition.output_value
#check @IncrementedSourceDyadicAddition.machine_prefix_storage

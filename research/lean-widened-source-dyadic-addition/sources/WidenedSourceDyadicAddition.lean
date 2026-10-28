import PaidBinaryIncrement
import IncrementedSourceDyadicAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Capacity-free successor: the paid increment may actually allocate one new
right-marker cell before the same fourteen-tape adder entrance. The accepted
thirteen-tape Frame, physical enter and initialFrame are reused unchanged.
One charged finite phase switch consumes the real increment output tape.
The complete time and adder space bound use its actual possibly increased
exponent width. Initial private working tape/blank exterior remains explicit.
This mutates the source-exponent work copy and does not restore dirty scratch.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace WidenedSourceDyadicAddition
open EncodedDyadicAddition (ZTape)
open SequentialBitAddition (Registers)
open CurrentMain.PairedBitXorScan (value)
open IncrementedSourceDyadicAddition (Frame enter initialFrame frameCells)

inductive State where
  | preparing (f:Frame) (s:PaidBinaryIncrement.State)
  | adding (s:ReusableDyadicOutput.State)
  deriving DecidableEq

def finished : PaidBinaryIncrement.State → Bool
  | .incrementing _ => false
  | .extending s => s.phase==.halt
  | .done .. => true
private theorem finished_iff (s:PaidBinaryIncrement.State) :
    finished s=true ↔ PaidBinaryIncrement.Halted s := by
  cases s <;> simp [finished,PaidBinaryIncrement.Halted]

def step : State → State
  | .preparing f s => if finished s then .adding (enter f (PaidBinaryIncrement.outputTape s))
      else .preparing f (PaidBinaryIncrement.step s)
  | .adding s => .adding (ReusableDyadicOutput.step s)
def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
def Halted : State → Prop
  | .preparing .. => False
  | .adding s => ReusableDyadicOutput.Halted s
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
private theorem preparing_trace (f:Frame) {n:Nat} {s t:PaidBinaryIncrement.State}
    (h:PaidBinaryIncrement.Trace n s t) : Trace n (.preparing f s) (.preparing f t) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      have hn:finished s=false := by
        cases he:finished s
        · rfl
        · exact False.elim (live ((finished_iff s).mp he))
      apply Trace.next (by simp [Halted])
      simpa only [step,hn,Bool.false_eq_true,if_false] using ih
private theorem adding_trace {n:Nat} {s t:ReusableDyadicOutput.State}
    (h:ReusableDyadicOutput.Trace n s t) : Trace n (.adding s) (.adding t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) : State :=
  .preparing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (PaidBinaryIncrement.initial yp oldFlag)
def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .adding (ReusableDyadicOutput.final xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar)
def totalTime (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  PaidBinaryIncrement.totalTime yp+1+
    ReusableDyadicOutput.totalTime xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar

/-- The exact accepted Frame and field-for-field enter are unchanged. -/
theorem handoff (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign:Bool) :
    step (.preparing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (PaidBinaryIncrement.final yp))=
      .adding (ReusableDyadicOutput.initial xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy bl br er ar held oldSign) := by
  have hf:finished (PaidBinaryIncrement.final yp)=true :=
    (finished_iff _).mpr (PaidBinaryIncrement.machine_result yp false).2.1
  simp only [step,hf,if_true,PaidBinaryIncrement.final_output]
  exact congrArg State.adding (IncrementedSourceDyadicAddition.enter_initial
    xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy bl br er ar held oldSign)

theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) :
    Trace (totalTime xp yp xs ys sx sy er ar)
      (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag) (final xp yp xs ys sx sy er ar) := by
  have hp:=preparing_trace (initialFrame xp xs ys sx sy bl br er ar held oldSign)
    (PaidBinaryIncrement.machine_exact yp oldFlag)
  have hs:Trace 1
      (.preparing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (PaidBinaryIncrement.final yp))
      (.adding (ReusableDyadicOutput.initial xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy bl br er ar held oldSign)) := by
    apply Trace.next (by simp [Halted])
    rw [handoff]
    exact Trace.nil _
  exact trace_trans (trace_trans hp hs)
    (adding_trace (ReusableDyadicOutput.machine_exact xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy bl br er ar held oldSign))

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) :
    run (totalTime xp yp xs ys sx sy er ar) (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
      final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    ∀ k<totalTime xp yp xs ys sx sy er ar,
      ¬Halted (run k (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)) :=
  ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar held oldSign oldFlag),
    rfl,trace_live (machine_exact xp yp xs ys sx sy bl br er ar held oldSign oldFlag)⟩

/-- The adder receives the actual width, including the paid overflow high bit. -/
theorem exponent_width (yp:List Bool) :
    (PaidBinaryIncrement.outputWord yp).length=yp.length+(if RippleCounter.overflow true yp then 1 else 0) :=
  PaidBinaryIncrement.output_length yp

theorem output_value (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨SequentialBitAddition.signedValue
          (ReusableDyadicOutput.lowWord xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar)
          (ReusableDyadicOutput.signBit xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar),
        value (EncodedDyadicAddition.commonWord xp (PaidBinaryIncrement.outputWord yp) er)⟩ =
      (SequentialBitAddition.signedValue xs sx:Real)/(2:Real)^(value xp)+
      ((SequentialBitAddition.signedValue ys sy:Real)/(2:Real)^(value yp))/2 := by
  have h:=(ReusableDyadicOutput.output_representation xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar).2.2.2
  rw [PaidBinaryIncrement.output_value,pow_succ,← div_div] at h
  exact h

theorem time_bound (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    totalTime xp yp xs ys sx sy er ar≤4*yp.length+10+
      ReusableDyadicOutput.totalTime xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar := by
  have h:=PaidBinaryIncrement.time_bound yp
  unfold totalTime
  omega

def cells : State → Nat
  | .preparing f s => frameCells f+PaidBinaryIncrement.cells s
  | .adding s => ReusableDyadicOutput.cells s

theorem initial_cells (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (held oldSign oldFlag:Bool) :
    cells (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
      xp.length+yp.length+xs.length+ys.length+8 :=
  IncrementedSourceDyadicAddition.initial_cells xp yp xs ys sx sy bl br er ar held oldSign oldFlag

private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)
private theorem preparing_prefix (f:Frame) {n:Nat} {s t:PaidBinaryIncrement.State}
    (h:PaidBinaryIncrement.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.preparing f s)=.preparing f (PaidBinaryIncrement.run k s) := by
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
        simpa only [run,step,hn,Bool.false_eq_true,if_false,PaidBinaryIncrement.run] using ih k (by omega)
theorem adding_run (s:ReusableDyadicOutput.State) (k:Nat) :
    run k (.adding s)=.adding (ReusableDyadicOutput.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (ReusableDyadicOutput.step s)

def additionBound (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : Nat :=
  EncodedDyadicAdditionSpace.bound xp (PaidBinaryIncrement.outputWord yp) xs ys er+
  (EncodedDyadicAddition.commonWord xp (PaidBinaryIncrement.outputWord yp) er).length+2+
  (ExtractedDyadicOutput.sumRows xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar).length+2+
  (ReusableDyadicOutput.lowWord xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy er ar).length+2

/-- Exactly one extra pre-adder cell is allowed, not a hidden extra tape.
The inherited adder bound is evaluated at the actual widened word. -/
theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers)
    (held oldSign oldFlag:Bool) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag))≤
      max (xp.length+yp.length+xs.length+ys.length+9) (additionBound xp yp xs ys sx sy er ar) := by
  have hi:=PaidBinaryIncrement.machine_exact yp oldFlag
  by_cases hk:k≤PaidBinaryIncrement.totalTime yp
  · change cells (run k (.preparing _ _))≤_
    rw [preparing_prefix _ hi k hk]
    have hb:=PaidBinaryIncrement.machine_prefix_storage yp oldFlag k
    have he:=initial_cells xp yp xs ys sx sy bl br er ar held oldSign oldFlag
    have hv:PaidBinaryIncrement.cells (PaidBinaryIncrement.initial yp oldFlag)=yp.length+2 := by
      simp [PaidBinaryIncrement.cells,PaidBinaryIncrement.outputTape,PaidBinaryIncrement.initial,
        MarkedBinaryIncrement.initial,MarkedZeroPadding.marked,MarkedZeroPadding.bits]
    change frameCells _+PaidBinaryIncrement.cells _=_ at he
    rw [hv] at he
    apply Nat.le_trans _ (Nat.le_max_left _ _)
    change frameCells _+PaidBinaryIncrement.cells _≤_
    omega
  · have hp:run (PaidBinaryIncrement.totalTime yp)
        (initial xp yp xs ys sx sy bl br er ar held oldSign oldFlag)=
        .preparing (initialFrame xp xs ys sx sy bl br er ar held oldSign) (PaidBinaryIncrement.final yp) :=
      trace_sound (preparing_trace _ hi)
    have hs:k=(PaidBinaryIncrement.totalTime yp+1)+(k-(PaidBinaryIncrement.totalTime yp+1)) := by omega
    rw [hs,run_add,run_add,hp]
    rw [show ∀ s:State,run 1 s=step s from fun _=>rfl,handoff,adding_run]
    exact (ReusableDyadicOutput.machine_prefix_storage xp (PaidBinaryIncrement.outputWord yp) xs ys sx sy bl br er ar held oldSign _).trans
      (Nat.le_max_right _ _)

end WidenedSourceDyadicAddition
#print axioms WidenedSourceDyadicAddition.handoff
#print axioms WidenedSourceDyadicAddition.machine_exact
#print axioms WidenedSourceDyadicAddition.machine_result
#print axioms WidenedSourceDyadicAddition.exponent_width
#print axioms WidenedSourceDyadicAddition.output_value
#print axioms WidenedSourceDyadicAddition.time_bound
#print axioms WidenedSourceDyadicAddition.initial_cells
#print axioms WidenedSourceDyadicAddition.machine_prefix_storage
#check @WidenedSourceDyadicAddition.machine_result
#check @WidenedSourceDyadicAddition.output_value
#check @WidenedSourceDyadicAddition.machine_prefix_storage

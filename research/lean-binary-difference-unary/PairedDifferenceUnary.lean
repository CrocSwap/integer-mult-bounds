import MarkedBitDifference
import BinaryToUnaryControl

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Actual three-tape composition of carry-derived exponent difference and its
unary producer. One finite controller transition reuses the produced marked
binary tape as the counter. The paired source tape, direction flag and cleared
adder registers are retained as spectators. No free input conversion, copy,
marker creation or integer subtraction occurs in the handoff.
The magnitude-dependent cost is explicit; this is not linear in encoded width.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace PairedDifferenceUnary
open CurrentMain.PairedBitXorScan (Tape value)
open SequentialBitAddition (Registers Row)

inductive State where
  | difference (s:MarkedBitDifference.State) (unary:Tape MarkedZeroPadding.Symbol)
  | conversion (paired:Tape MarkedBitAddition.Symbol) (savedRegisters:Registers)
      (reverse:Bool) (s:BinaryToUnaryControl.State)
  deriving DecidableEq

/-- The handoff changes finite control and initializes one borrow bit; all
three tape contents and heads are passed literally, without a traversal. -/
def step : State → State
  | .difference s out =>
      if s.phase=.halt then
        .conversion s.tape s.registers s.reverse ⟨s.output,out,false,.setup⟩
      else .difference (MarkedBitDifference.step s) out
  | .conversion paired regs reverse s =>
      .conversion paired regs reverse (BinaryToUnaryControl.step s)

def Halted : State → Prop
  | .difference _ _ => False
  | .conversion _ _ _ s => s.phase=.halt

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
private theorem halt_run (s:State) (hs:Halted s) (k:Nat) : run k s=s := by
  cases s with
  | difference s out => exact False.elim hs
  | conversion paired regs reverse s =>
      change s.phase=BinaryToUnaryControl.Phase.halt at hs
      induction k with
      | zero => rfl
      | succ k ih => simpa [run,step,BinaryToUnaryControl.step,hs] using ih

private theorem difference_trace (out:Tape MarkedZeroPadding.Symbol)
    {n:Nat} {s t:MarkedBitDifference.State} (h:MarkedBitDifference.Trace n s t) :
    Trace n (.difference s out) (.difference t out) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,if_neg live] using ih
private theorem conversion_trace (paired:Tape MarkedBitAddition.Symbol) (regs:Registers) (reverse:Bool)
    {n:Nat} {s t:BinaryToUnaryControl.State} (h:BinaryToUnaryControl.Trace n s t) :
    Trace n (.conversion paired regs reverse s) (.conversion paired regs reverse t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def magnitudeWord (rows:List Row) (r:Registers) : List Bool :=
  (MarkedBitDifference.chosenRows rows r).map Prod.snd
def magnitude (rows:List Row) (r:Registers) : Nat := value (magnitudeWord rows r)
def initial (rows:List Row) (r:Registers) : State :=
  .difference (MarkedBitDifference.initial rows r) ⟨[],[]⟩
def final (rows:List Row) (r:Registers) : State :=
  .conversion (MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows r))
    SequentialBitAddition.clearRegisters (MarkedBitDifference.chosenReverse rows r)
    (BinaryToUnaryControl.final rows.length (magnitude rows r))
def totalTime (rows:List Row) (r:Registers) : Nat :=
  MarkedBitDifference.totalTime rows r+1+BinaryToUnaryControl.totalTime (magnitudeWord rows r)

theorem magnitude_length (rows:List Row) (r:Registers) :
    (magnitudeWord rows r).length=rows.length := by
  simp only [magnitudeWord,List.length_map,MarkedBitDifference.chosen_length]

theorem handoff (rows:List Row) (r:Registers) :
    step (.difference (MarkedBitDifference.final rows r) ⟨[],[]⟩)=
      .conversion (MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows r))
        SequentialBitAddition.clearRegisters (MarkedBitDifference.chosenReverse rows r)
        (BinaryToUnaryControl.initial (magnitudeWord rows r)) := rfl

/-- The inherited concrete traces are composed across one executed switch. -/
theorem machine_exact (rows:List Row) (r:Registers) :
    Trace (totalTime rows r) (initial rows r) (final rows r) := by
  have hd:=difference_trace (⟨[],[]⟩ : Tape MarkedZeroPadding.Symbol)
    (MarkedBitDifference.difference_exact rows r)
  have hh:Trace 1 (.difference (MarkedBitDifference.final rows r) ⟨[],[]⟩)
      (.conversion (MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows r))
        SequentialBitAddition.clearRegisters (MarkedBitDifference.chosenReverse rows r)
        (BinaryToUnaryControl.initial (magnitudeWord rows r))) := by
    apply Trace.next (by simp [Halted])
    rw [handoff]
    exact Trace.nil _
  have hu:=conversion_trace (MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows r))
    SequentialBitAddition.clearRegisters (MarkedBitDifference.chosenReverse rows r)
    (BinaryToUnaryControl.conversion_exact (magnitudeWord rows r))
  rw [magnitude_length] at hu
  exact trace_trans (trace_trans hd hh) hu

theorem machine_result (rows:List Row) (r:Registers) :
    run (totalTime rows r) (initial rows r)=final rows r ∧
    Halted (final rows r) ∧
    ∀ k<totalTime rows r,¬Halted (run k (initial rows r)) :=
  ⟨trace_sound (machine_exact rows r),rfl,trace_live (machine_exact rows r)⟩

/-- Both full subtraction passes, extraction, one switch, all repeated
binary decrements and final unary return are included in this upper bound. -/
theorem time_bound (rows:List Row) (r:Registers) :
    totalTime rows r≤magnitude rows r*(2*rows.length+6)+30*rows.length+37 := by
  have h:=MarkedBitDifference.time_bound rows r
  simp only [totalTime,BinaryToUnaryControl.totalTime,magnitude_length]
  unfold magnitude
  omega

private theorem value_decode (xs:List Bool) : (value xs:Int)=SequentialBitAddition.decode xs := by
  induction xs with
  | nil => rfl
  | cons b xs ih => cases b <;> simp [value,SequentialBitAddition.decode,SequentialBitAddition.bit,ih] <;> omega

/-- Numeric magnitude is an observation of actual produced bits. No Nat
subtraction, order oracle or decoding occurs in the controller. -/
theorem magnitude_order (rows:List Row) (r:Registers) :
    let p:=rows.map Prod.fst
    if MarkedBitDifference.chosenReverse rows r then
      SequentialBitAddition.decode (SequentialBitAddition.leftBits p)<SequentialBitAddition.decode (SequentialBitAddition.rightBits p) ∧
      (magnitude rows r:Int)=SequentialBitAddition.decode (SequentialBitAddition.rightBits p)-SequentialBitAddition.decode (SequentialBitAddition.leftBits p)
    else
      SequentialBitAddition.decode (SequentialBitAddition.rightBits p)≤SequentialBitAddition.decode (SequentialBitAddition.leftBits p) ∧
      (magnitude rows r:Int)=SequentialBitAddition.decode (SequentialBitAddition.leftBits p)-SequentialBitAddition.decode (SequentialBitAddition.rightBits p) := by
  simpa only [magnitude,value_decode,magnitudeWord] using MarkedBitDifference.chosen_value rows r

def cells : State → Nat
  | .difference s out => MarkedBitDifference.cells s+BinaryToUnaryControl.tapeCells out
  | .conversion paired _ _ s => MarkedBitDifference.tapeCells paired+BinaryToUnaryControl.cells s

private theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases s with
  | difference s out =>
      simp only [step];split
      next h => simp [cells,MarkedBitDifference.cells,MarkedBitDifference.tapeCells,
        BinaryToUnaryControl.cells,BinaryToUnaryControl.tapeCells,Nat.add_assoc]
      next h => exact Nat.add_le_add_right (MarkedBitDifference.step_cells s) _
  | conversion paired regs reverse s =>
      exact Nat.add_le_add_left (BinaryToUnaryControl.step_cells s) _
private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t) (ht:Halted t) (k:Nat) :
    cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

/-- Includes the retained paired input, consumed binary counter, actual unary
output and all six markers. Fixed registers/finite control are separate. -/
theorem machine_prefix_storage (rows:List Row) (r:Registers) (k:Nat) :
    cells (run k (initial rows r))≤2*rows.length+magnitude rows r+6 := by
  have h:=trace_storage (machine_exact rows r) rfl k
  simp only [final,cells,MarkedBitDifference.tapeCells,MarkedBitAddition.marked,
    BinaryToUnaryControl.final,BinaryToUnaryControl.cells,BinaryToUnaryControl.tapeCells,
    BinaryToUnaryControl.zeroCounter,MarkedZeroPadding.marked,MarkedZeroPadding.bits,
    MarkedZeroPadding.ticks,List.length_nil,List.length_cons,List.length_append,
    List.length_map,List.length_replicate,MarkedBitDifference.chosen_length] at h ⊢
  omega

/-- The result is the literal padder control layout and both input tracks are
preserved, while the copied binary counter is intentionally consumed to zeros. -/
theorem produced_control (rows:List Row) (r:Registers) :
    run (totalTime rows r) (initial rows r)=
      .conversion (MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows r))
        SequentialBitAddition.clearRegisters (MarkedBitDifference.chosenReverse rows r)
        ⟨BinaryToUnaryControl.zeroCounter rows.length,
          MarkedZeroPadding.marked (MarkedZeroPadding.ticks (magnitude rows r)),false,.halt⟩ ∧
    (MarkedBitDifference.chosenRows rows r).map Prod.fst=rows.map Prod.fst :=
  ⟨(machine_result rows r).1,MarkedBitDifference.chosen_sources rows r⟩

end PairedDifferenceUnary

#print axioms PairedDifferenceUnary.handoff
#print axioms PairedDifferenceUnary.machine_exact
#print axioms PairedDifferenceUnary.machine_result
#print axioms PairedDifferenceUnary.time_bound
#print axioms PairedDifferenceUnary.magnitude_order
#print axioms PairedDifferenceUnary.machine_prefix_storage
#print axioms PairedDifferenceUnary.produced_control
#check @PairedDifferenceUnary.machine_result
#check @PairedDifferenceUnary.magnitude_order

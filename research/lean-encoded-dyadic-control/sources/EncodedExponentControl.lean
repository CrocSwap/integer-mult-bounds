import MarkedPairLayout
import PairedDifferenceUnary

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Unsigned specialization of the accepted paid pair layout, followed by the
accepted subtract/compare/extract/unary controller. Both signs are false; the
builder really writes its two additional zero columns. Original unequal-width
binary input words remain on their tapes. Three work tapes begin blank.
All five tapes persist across the single charged mode switch.
The cost depends on numeric difference as well as input lengths. Actual binary
encoding, independent blank storage and a downstream padding/slot policy remain
caller responsibilities; no Nat-to-word conversion is executed here.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace EncodedExponentControl
open CurrentMain.PairedBitXorScan (Tape)
open SequentialBitAddition (Registers Row decode leftBits rightBits)

inductive State where
  | layout (s:MarkedPairLayout.State) (binary unary:Tape MarkedZeroPadding.Symbol)
  | control (left right:Tape MarkedZeroPadding.Symbol) (sx sy:Bool) (s:PairedDifferenceUnary.State)
  deriving DecidableEq

def step : State → State
  | .layout s binary unary =>
      if s.phase=.halt then
        .control s.leftTape s.rightTape s.leftSign s.rightSign
          (.difference ⟨s.outputTape,binary,s.registers,false,.enter⟩ unary)
      else .layout (MarkedPairLayout.step s) binary unary
  | .control left right sx sy s => .control left right sx sy (PairedDifferenceUnary.step s)
def Halted : State → Prop
  | .layout _ _ _ => False
  | .control _ _ _ _ s => PairedDifferenceUnary.Halted s

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
private theorem step_halted (s:State) (h:Halted s) : step s=s := by
  cases s with
  | layout => exact False.elim h
  | control left right sx sy s =>
      cases s with
      | difference => exact False.elim h
      | conversion paired regs reverse s =>
          change s.phase=BinaryToUnaryControl.Phase.halt at h
          simp [step,PairedDifferenceUnary.step,BinaryToUnaryControl.step,h]
private theorem halt_run (s:State) (h:Halted s) (k:Nat) : run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [run,step_halted s h] using ih
private theorem layout_trace (binary unary:Tape MarkedZeroPadding.Symbol)
    {n:Nat} {s t:MarkedPairLayout.State} (h:MarkedPairLayout.Trace n s t) :
    Trace n (.layout s binary unary) (.layout t binary unary) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,if_neg live] using ih
private theorem control_trace (left right:Tape MarkedZeroPadding.Symbol) (sx sy:Bool)
    {n:Nat} {s t:PairedDifferenceUnary.State} (h:PairedDifferenceUnary.Trace n s t) :
    Trace n (.control left right sx sy s) (.control left right sx sy t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def rows (xs ys:List Bool) : List Row := MarkedPairLayout.rows xs false ys false
def magnitude (xs ys:List Bool) (r:Registers) : Nat :=
  PairedDifferenceUnary.magnitude (rows xs ys) (MarkedPairLayout.clearScratch r)
def reverseFlag (xs ys:List Bool) (r:Registers) : Bool :=
  MarkedBitDifference.chosenReverse (rows xs ys) (MarkedPairLayout.clearScratch r)
def initial (xs ys:List Bool) (r:Registers) : State :=
  .layout (MarkedPairLayout.initial xs false ys false r) ⟨[],[]⟩ ⟨[],[]⟩
def final (xs ys:List Bool) (r:Registers) : State :=
  .control (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) false false
    (PairedDifferenceUnary.final (rows xs ys) (MarkedPairLayout.clearScratch r))
def totalTime (xs ys:List Bool) (r:Registers) : Nat :=
  (8*max xs.length ys.length+xs.length+ys.length+24)+1+
    PairedDifferenceUnary.totalTime (rows xs ys) (MarkedPairLayout.clearScratch r)

/-- Both added zero columns are counted and executed, even for empty input. -/
theorem rows_length (xs ys:List Bool) : (rows xs ys).length=max xs.length ys.length+2 := by
  simp [rows,MarkedPairLayout.rows,SignedWordAlignment.aligned_length,SignedWordAlignment.width]

private theorem pair_projection (xs ys:List Bool) :
    (rows xs ys).map Prod.fst=SignedWordAlignment.aligned xs false ys false++[(false,false),(false,false)] := by
  simp [rows,MarkedPairLayout.rows,List.map_map,Function.comp_def]

/-- Sign=false turns the accepted sign extension into ordinary zero extension.
These value identities concern the actual written rows, without equal widths. -/
theorem rows_values (xs ys:List Bool) :
    decode (leftBits ((rows xs ys).map Prod.fst))=decode xs ∧
    decode (rightBits ((rows xs ys).map Prod.fst))=decode ys := by
  have hx:=SignedWordAlignment.extend_value (SignedWordAlignment.width xs ys) xs false
  have hy:=SignedWordAlignment.extend_value (SignedWordAlignment.width xs ys) ys false
  simp only [SequentialBitAddition.signedValue,SequentialBitAddition.bit,Bool.false_eq_true,if_false,mul_zero,zero_mul,sub_zero] at hx hy
  rw [pair_projection]
  simp only [leftBits,rightBits,List.map_append,List.map_cons,List.map_nil]
  have hl:=SignedWordAlignment.aligned_left xs false ys false
  have hr:=SignedWordAlignment.aligned_right xs false ys false
  constructor
  · change decode ((leftBits (SignedWordAlignment.aligned xs false ys false))++[false,false])=decode xs
    rw [SignedWordAlignment.decode_append,hl,hx]
    simp [decode,SequentialBitAddition.bit]
  · change decode ((rightBits (SignedWordAlignment.aligned xs false ys false))++[false,false])=decode ys
    rw [SignedWordAlignment.decode_append,hr,hy]
    simp [decode,SequentialBitAddition.bit]

theorem handoff (xs ys:List Bool) (r:Registers) :
    step (.layout (MarkedPairLayout.final xs false ys false r) ⟨[],[]⟩ ⟨[],[]⟩)=
      .control (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
        (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) false false
        (PairedDifferenceUnary.initial (rows xs ys) (MarkedPairLayout.clearScratch r)) := rfl

theorem machine_exact (xs ys:List Bool) (r:Registers) :
    Trace (totalTime xs ys r) (initial xs ys r) (final xs ys r) := by
  have hl:=layout_trace ⟨[],[]⟩ ⟨[],[]⟩ (MarkedPairLayout.layout_exact xs ys false false r)
  have hh:Trace 1 (.layout (MarkedPairLayout.final xs false ys false r) ⟨[],[]⟩ ⟨[],[]⟩)
      (.control (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
        (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) false false
        (PairedDifferenceUnary.initial (rows xs ys) (MarkedPairLayout.clearScratch r))) := by
    apply Trace.next (by simp [Halted])
    rw [handoff]
    exact Trace.nil _
  have hc:=control_trace (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) false false
    (PairedDifferenceUnary.machine_exact (rows xs ys) (MarkedPairLayout.clearScratch r))
  exact trace_trans (trace_trans hl hh) hc

theorem machine_result (xs ys:List Bool) (r:Registers) :
    run (totalTime xs ys r) (initial xs ys r)=final xs ys r ∧
    Halted (final xs ys r) ∧ ∀ k<totalTime xs ys r,¬Halted (run k (initial xs ys r)) :=
  ⟨trace_sound (machine_exact xs ys r),rfl,trace_live (machine_exact xs ys r)⟩

/-- Encoding words can have different widths and leading zeros. The actual
comparison branch determines which exponent receives the nonzero shift. -/
theorem magnitude_order (xs ys:List Bool) (r:Registers) :
    if reverseFlag xs ys r then decode xs<decode ys ∧ (magnitude xs ys r:Int)=decode ys-decode xs
    else decode ys≤decode xs ∧ (magnitude xs ys r:Int)=decode xs-decode ys := by
  have h:=PairedDifferenceUnary.magnitude_order (rows xs ys) (MarkedPairLayout.clearScratch r)
  dsimp only at h
  rw [(rows_values xs ys).1,(rows_values xs ys).2] at h
  exact h

theorem time_bound (xs ys:List Bool) (r:Registers) :
    totalTime xs ys r≤magnitude xs ys r*(2*max xs.length ys.length+10)+
      38*max xs.length ys.length+xs.length+ys.length+122 := by
  have h:=PairedDifferenceUnary.time_bound (rows xs ys) (MarkedPairLayout.clearScratch r)
  rw [rows_length] at h
  have he:2*(max xs.length ys.length+2)+6=2*max xs.length ys.length+10 := by omega
  rw [he] at h
  change PairedDifferenceUnary.totalTime (rows xs ys) (MarkedPairLayout.clearScratch r)≤
    magnitude xs ys r*(2*max xs.length ys.length+10)+30*(max xs.length ys.length+2)+37 at h
  unfold totalTime
  omega

def cells : State → Nat
  | .layout s binary unary => MarkedPairLayout.cells s+
      BinaryToUnaryControl.tapeCells binary+BinaryToUnaryControl.tapeCells unary
  | .control left right _ _ s => BinaryToUnaryControl.tapeCells left+
      BinaryToUnaryControl.tapeCells right+PairedDifferenceUnary.cells s

private theorem control_step_cells (s:PairedDifferenceUnary.State) :
    PairedDifferenceUnary.cells s≤PairedDifferenceUnary.cells (PairedDifferenceUnary.step s) := by
  cases s with
  | difference s out =>
      simp only [PairedDifferenceUnary.step];split
      next h => simp [PairedDifferenceUnary.cells,MarkedBitDifference.cells,MarkedBitDifference.tapeCells,
        BinaryToUnaryControl.cells,BinaryToUnaryControl.tapeCells,Nat.add_assoc]
      next h => exact Nat.add_le_add_right (MarkedBitDifference.step_cells s) _
  | conversion paired regs reverse s => exact Nat.add_le_add_left (BinaryToUnaryControl.step_cells s) _
private theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases s with
  | layout s binary unary =>
      simp only [step];split
      next h => simp [cells,MarkedPairLayout.cells,MarkedPairLayout.tapeCells,
        PairedDifferenceUnary.cells,MarkedBitDifference.cells,MarkedBitDifference.tapeCells,
        BinaryToUnaryControl.tapeCells,Nat.add_assoc]
      next h => exact Nat.add_le_add_right (Nat.add_le_add_right (MarkedPairLayout.step_cells s) _) _
  | control left right sx sy s => exact Nat.add_le_add_left (control_step_cells s) _
private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t) (ht:Halted t) (k:Nat) :
    cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

/-- All five tapes and ten real markers remain counted, including both
original input words, extra zero columns and the consumed binary counter. -/
theorem machine_prefix_storage (xs ys:List Bool) (r:Registers) (k:Nat) :
    cells (run k (initial xs ys r))≤xs.length+ys.length+2*max xs.length ys.length+magnitude xs ys r+14 := by
  have h:=trace_storage (machine_exact xs ys r) rfl k
  simp only [final,cells,PairedDifferenceUnary.final,PairedDifferenceUnary.cells,
    BinaryToUnaryControl.final,BinaryToUnaryControl.cells,BinaryToUnaryControl.tapeCells,
    BinaryToUnaryControl.zeroCounter,MarkedBitDifference.tapeCells,MarkedBitAddition.marked,
    MarkedZeroPadding.marked,MarkedZeroPadding.bits,MarkedZeroPadding.ticks,
    List.length_nil,List.length_cons,List.length_append,List.length_map,List.length_replicate,
    MarkedBitDifference.chosen_length,rows_length] at h ⊢
  change _≤xs.length+ys.length+2*max xs.length ys.length+
    PairedDifferenceUnary.magnitude (rows xs ys) (MarkedPairLayout.clearScratch r)+14
  omega

/-- Source tapes and signs are framed throughout the entire arithmetic and
unary stage, so their supplied encodings are not consumed with the work copy. -/
theorem control_run (left right:Tape MarkedZeroPadding.Symbol) (sx sy:Bool)
    (s:PairedDifferenceUnary.State) (k:Nat) :
    run k (.control left right sx sy s)=.control left right sx sy (PairedDifferenceUnary.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (PairedDifferenceUnary.step s)

end EncodedExponentControl

#print axioms EncodedExponentControl.rows_length
#print axioms EncodedExponentControl.rows_values
#print axioms EncodedExponentControl.handoff
#print axioms EncodedExponentControl.machine_exact
#print axioms EncodedExponentControl.machine_result
#print axioms EncodedExponentControl.magnitude_order
#print axioms EncodedExponentControl.time_bound
#print axioms EncodedExponentControl.machine_prefix_storage
#print axioms EncodedExponentControl.control_run
#check @EncodedExponentControl.machine_result
#check @EncodedExponentControl.magnitude_order

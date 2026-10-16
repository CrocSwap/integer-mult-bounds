import EncodedExponentControl
import PaddedSignedAddition
import DyadicCellAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Eleven-tape composition of actually computed exponent controls and paid signed
addition. The semantic convention is numerator / 2^fractionalBits. Hence the
smaller denominator exponent receives the nonnegative numerator shift.
Two actual write/move transitions construct the empty unary control, followed
by one charged finite branch. A retained route flag selects the same physical
magnitude/zero tapes at EVERY delegated step. No comparison, Nat arithmetic,
copy, or endpoint re-encoding is executed in these three transitions.
The common exponent is a view of an unchanged original word. Copying it to a
new result record, initial encodings/allocation, raw2's half-source p+1, and
selected recursive cost remain separate. Runtime still depends on magnitude.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace EncodedDyadicAddition
open CurrentMain.PairedBitXorScan (Tape)
open SequentialBitAddition (Registers decode signedValue)

abbrev ZTape := Tape MarkedZeroPadding.Symbol
abbrev ATape := Tape MarkedBitAddition.Symbol

/-- Only the two control-tape fields are exchanged; data, output, scratch and
finite phases retain their locations. This is a representation permutation. -/
def swapControls : PaddedSignedAddition.State → PaddedSignedAddition.State
  | .first l r o regs sx sy => .first {l with controlTape:=r.controlTape}
      {r with controlTape:=l.controlTape} o regs sx sy
  | .second l r o regs sx sy => .second {l with controlTape:=r.controlTape}
      {r with controlTape:=l.controlTape} o regs sx sy
  | .sum ld lc rd rc bl br s => .sum ld rc rd lc bl br s

theorem swap_involutive (s:PaddedSignedAddition.State) : swapControls (swapControls s)=s := by
  cases s <;> rfl

/-- In physical states control slot one is always magnitude, slot two zero.
True routes magnitude to the left operand; false routes it to the right. -/
def route (reverse:Bool) (s:PaddedSignedAddition.State) : PaddedSignedAddition.State :=
  if reverse then s else swapControls s

theorem route_involutive (reverse:Bool) (s:PaddedSignedAddition.State) : route reverse (route reverse s)=s := by
  cases reverse <;> simp [route,swap_involutive]

def routedStep (reverse:Bool) (s:PaddedSignedAddition.State) : PaddedSignedAddition.State :=
  route reverse (PaddedSignedAddition.step (route reverse s))

/-- The fixed finite tape selector is used at each actual transition, rather
than replacing physical control tapes only at the entrance. -/
theorem routed_step (reverse:Bool) (s:PaddedSignedAddition.State) :
    routedStep reverse (route reverse s)=route reverse (PaddedSignedAddition.step s) := by
  simp only [routedStep,route_involutive]

theorem routed_halted (reverse:Bool) (s:PaddedSignedAddition.State) :
    PaddedSignedAddition.Halted (route reverse s) ↔ PaddedSignedAddition.Halted s := by
  cases reverse <;> cases s <;> rfl

theorem routed_cells (reverse:Bool) (s:PaddedSignedAddition.State) :
    PaddedSignedAddition.cells (route reverse s)=PaddedSignedAddition.cells s := by
  cases reverse <;> cases s <;>
    simp [route,swapControls,PaddedSignedAddition.cells,MarkedZeroPadding.cells,
      MarkedZeroPadding.tapeCells] <;> omega

structure Cargo where
  leftData : ZTape
  rightData : ZTape
  leftPadded : ZTape
  rightPadded : ZTape
  zeroControl : ZTape
  output : ATape
  leftScratch : Bool
  rightScratch : Bool
  registers : Registers
  leftSign : Bool
  rightSign : Bool
  deriving DecidableEq

/-- Four exponent-side spectator tapes and all leftover finite registers. -/
structure Frame where
  leftExponent : ZTape
  rightExponent : ZTape
  paired : ATape
  counter : ZTape
  savedRegisters : Registers
  borrow : Bool
  leftSign : Bool
  rightSign : Bool
  deriving DecidableEq

inductive State where
  | computing (s:EncodedExponentControl.State) (c:Cargo)
  | zeroRight (s:EncodedExponentControl.State) (c:Cargo)
  | ready (s:EncodedExponentControl.State) (c:Cargo)
  | adding (frame:Frame) (reverse:Bool) (s:PaddedSignedAddition.State)
  deriving DecidableEq

def exponentFinished : EncodedExponentControl.State → Bool
  | .control _ _ _ _ (.conversion _ _ _ s) => s.phase==.halt
  | _ => false

private theorem exponentFinished_iff (s:EncodedExponentControl.State) :
    exponentFinished s=true ↔ EncodedExponentControl.Halted s := by
  cases s with
  | layout => simp [exponentFinished,EncodedExponentControl.Halted]
  | control l r sx sy s => cases s with
    | difference => simp [exponentFinished,EncodedExponentControl.Halted,PairedDifferenceUnary.Halted]
    | conversion => simp [exponentFinished,EncodedExponentControl.Halted,PairedDifferenceUnary.Halted]

/-- Construct a physical addition state. Both controls are retained in fixed
physical slots; routedStep connects them to the chosen logical operands. -/
def enterAddition (e:EncodedExponentControl.State) (c:Cargo) : State :=
  match e with
  | .control l r sx sy (.conversion pair regs reverse b) =>
      .adding ⟨l,r,pair,b.counter,regs,b.borrow,sx,sy⟩ reverse
        (.first ⟨c.leftData,b.output,c.leftPadded,c.leftScratch,.writeLeft⟩
          ⟨c.rightData,c.zeroControl,c.rightPadded,c.rightScratch,.writeLeft⟩
          c.output c.registers c.leftSign c.rightSign)
  | _ => .ready e c

def step : State → State
  | .computing e c =>
      if exponentFinished e then
        .zeroRight e {c with zeroControl:=(c.zeroControl.writeHead .leftMarker).moveRight .blank}
      else .computing (EncodedExponentControl.step e) c
  | .zeroRight e c =>
      .ready e {c with zeroControl:=(c.zeroControl.writeHead .rightMarker).moveLeft .blank}
  | .ready e c => enterAddition e c
  | .adding f reverse s => .adding f reverse (routedStep reverse s)

def Halted : State → Prop
  | .adding _ _ s => PaddedSignedAddition.Halted s
  | _ => False

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

private theorem computing_trace (c:Cargo) {n:Nat} {s t:EncodedExponentControl.State}
    (h:EncodedExponentControl.Trace n s t) : Trace n (.computing s c) (.computing t c) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      apply Trace.next (by simp [Halted])
      have hn:exponentFinished s=false := by
        cases h:exponentFinished s
        · rfl
        · exact False.elim (live ((exponentFinished_iff s).mp h))
      simpa only [step,hn,Bool.false_eq_true,if_false] using ih

private theorem adding_trace (f:Frame) (reverse:Bool) {n:Nat} {s t:PaddedSignedAddition.State}
    (h:PaddedSignedAddition.Trace n s t) :
    Trace n (.adding f reverse (route reverse s)) (.adding f reverse (route reverse t)) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n s t live tail ih =>
      refine Trace.next ?_ ?_
      · change ¬PaddedSignedAddition.Halted (route reverse s)
        exact fun h=>live ((routed_halted reverse s).mp h)
      · simpa only [step,routed_step] using ih

def leftShift (xp yp:List Bool) (r:Registers) : Nat :=
  if EncodedExponentControl.reverseFlag xp yp r then EncodedExponentControl.magnitude xp yp r else 0

def rightShift (xp yp:List Bool) (r:Registers) : Nat :=
  if EncodedExponentControl.reverseFlag xp yp r then 0 else EncodedExponentControl.magnitude xp yp r

def commonWord (xp yp:List Bool) (r:Registers) : List Bool :=
  if EncodedExponentControl.reverseFlag xp yp r then yp else xp

def cargo (xs ys:List Bool) (sx sy bl br:Bool) (r:Registers) : Cargo :=
  ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits xs),
   MarkedZeroPadding.marked (MarkedZeroPadding.bits ys),⟨[],[]⟩,⟨[],[]⟩,⟨[],[]⟩,⟨[],[]⟩,bl,br,r,sx,sy⟩

def finalFrame (xp yp:List Bool) (r:Registers) : Frame :=
  let rows:=EncodedExponentControl.rows xp yp
  let regs:=MarkedPairLayout.clearScratch r
  ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits xp),
    MarkedZeroPadding.marked (MarkedZeroPadding.bits yp),
    MarkedBitAddition.marked (MarkedBitDifference.chosenRows rows regs),
    BinaryToUnaryControl.zeroCounter rows.length,SequentialBitAddition.clearRegisters,false,false,false⟩

def initial (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) : State :=
  .computing (EncodedExponentControl.initial xp yp er) (cargo xs ys sx sy bl br ar)

def final (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) : State :=
  .adding (finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
    (route (EncodedExponentControl.reverseFlag xp yp er)
      (PaddedSignedAddition.final (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy ar))

def totalTime (xp yp xs ys:List Bool) (er:Registers) : Nat :=
  EncodedExponentControl.totalTime xp yp er+3+
    PaddedSignedAddition.totalTime (leftShift xp yp er) xs (rightShift xp yp er) ys

/-- Exactly two marker writes/head movements and one routing transition.
Both heads return to L, and the generated magnitude tape is never copied. -/
theorem control_handoff (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    Trace 3 (.computing (EncodedExponentControl.final xp yp er) (cargo xs ys sx sy bl br ar))
      (.adding (finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
        (route (EncodedExponentControl.reverseFlag xp yp er)
          (PaddedSignedAddition.initial (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy bl br ar))) := by
  apply Trace.next (by simp [Halted])
  apply Trace.next (by simp [step,exponentFinished,EncodedExponentControl.final,PairedDifferenceUnary.final,
    BinaryToUnaryControl.final,Halted])
  apply Trace.next (by simp [step,exponentFinished,EncodedExponentControl.final,PairedDifferenceUnary.final,
    BinaryToUnaryControl.final,Halted])
  change Trace 0
    (enterAddition (EncodedExponentControl.final xp yp er)
      {cargo xs ys sx sy bl br ar with zeroControl:=MarkedZeroPadding.marked []}) _
  cases hf:EncodedExponentControl.reverseFlag xp yp er
  all_goals
    have hf' := hf
    dsimp only [EncodedExponentControl.reverseFlag] at hf'
    simp only [enterAddition,EncodedExponentControl.final,PairedDifferenceUnary.final,
      BinaryToUnaryControl.final,cargo,finalFrame,leftShift,rightShift,hf,route,
      Bool.false_eq_true,if_false,if_true,swapControls,PaddedSignedAddition.initial,
      MarkedZeroPadding.initial,EncodedExponentControl.magnitude] 
    simp only [hf',MarkedZeroPadding.ticks,List.replicate_zero]
    exact Trace.nil _

/-- The complete executable trace has no supplied order/control or endpoint
premise. The initial words, signs and independent blank allocations are inputs. -/
theorem machine_exact (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    Trace (totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)
      (final xp yp xs ys sx sy er ar) := by
  exact trace_trans (trace_trans
    (computing_trace (cargo xs ys sx sy bl br ar) (EncodedExponentControl.machine_exact xp yp er))
    (control_handoff xp yp xs ys sx sy bl br er ar))
    (adding_trace (finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
      (PaddedSignedAddition.machine_exact (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy bl br ar))

theorem machine_result (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    run (totalTime xp yp xs ys er) (initial xp yp xs ys sx sy bl br er ar)=final xp yp xs ys sx sy er ar ∧
    Halted (final xp yp xs ys sx sy er ar) ∧
    ∀ k<totalTime xp yp xs ys er,¬Halted (run k (initial xp yp xs ys sx sy bl br er ar)) := by
  refine ⟨trace_sound (machine_exact xp yp xs ys sx sy bl br er ar),?_,trace_live (machine_exact xp yp xs ys sx sy bl br er ar)⟩
  exact (routed_halted _ _).mpr rfl

/-- Unbounded execution is only an external mathematical observer. Physical
routing commutes with every delegated step and preserves the four spectators. -/
theorem adding_run (f:Frame) (reverse:Bool) (s:PaddedSignedAddition.State) (k:Nat) :
    run k (.adding f reverse (route reverse s))=
      .adding f reverse (route reverse (PaddedSignedAddition.run k s)) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => simpa only [run,step,routed_step,PaddedSignedAddition.run] using ih (PaddedSignedAddition.step s)

/-- Both exponents plus their derived shift reach the unchanged larger word.
No comparator or Nat subtraction is supplied as an execution premise. -/
theorem exponent_alignment (xp yp:List Bool) (r:Registers) :
    decode xp+(leftShift xp yp r:Int)=decode (commonWord xp yp r) ∧
    decode yp+(rightShift xp yp r:Int)=decode (commonWord xp yp r) ∧
    decode (commonWord xp yp r)=max (decode xp) (decode yp) := by
  have h:=EncodedExponentControl.magnitude_order xp yp r
  cases hf:EncodedExponentControl.reverseFlag xp yp r <;>
    simp only [leftShift,rightShift,commonWord,hf,Bool.false_eq_true,if_false,if_true,Nat.cast_zero] at h ⊢
  · rw [max_eq_left h.1];omega
  · rw [max_eq_right (le_of_lt h.1)];omega

private theorem value_decode (xs:List Bool) :
    (CurrentMain.PairedBitXorScan.value xs:Int)=decode xs := by
  induction xs with
  | nil => rfl
  | cons b xs ih => cases b <;> simp [CurrentMain.PairedBitXorScan.value,decode,SequentialBitAddition.bit,ih] <;> omega

/-- Explicit semantic adapter to the accepted denominator-exponent Cell.
The computed shifts are exactly those of addCell, with no global grid shift. -/
theorem denominator_alignment (xp yp:List Bool) (r:Registers) (zx zy:Int) :
    let px:=CurrentMain.PairedBitXorScan.value xp
    let py:=CurrentMain.PairedBitXorScan.value yp
    let q:=CurrentMain.PairedBitXorScan.value (commonWord xp yp r)
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨(2:Int)^(leftShift xp yp r)*zx+(2:Int)^(rightShift xp yp r)*zy,q⟩ =
      (zx:Real)/(2:Real)^px+(zy:Real)/(2:Real)^py := by
  have h:=exponent_alignment xp yp r
  rw [←value_decode xp,←value_decode yp,←value_decode (commonWord xp yp r)] at h
  have hx:CurrentMain.PairedBitXorScan.value xp+leftShift xp yp r=
      CurrentMain.PairedBitXorScan.value (commonWord xp yp r) := by omega
  have hy:CurrentMain.PairedBitXorScan.value yp+rightShift xp yp r=
      CurrentMain.PairedBitXorScan.value (commonWord xp yp r) := by omega
  have hq:CurrentMain.PairedBitXorScan.value (commonWord xp yp r)=
      max (CurrentMain.PairedBitXorScan.value xp) (CurrentMain.PairedBitXorScan.value yp) := by omega
  have hdx:CurrentMain.PairedBitXorScan.value (commonWord xp yp r)-CurrentMain.PairedBitXorScan.value xp=leftShift xp yp r := by omega
  have hdy:CurrentMain.PairedBitXorScan.value (commonWord xp yp r)-CurrentMain.PairedBitXorScan.value yp=rightShift xp yp r := by omega
  have hv:=CurrentMain.DyadicCellAddition.addCell_value
    ⟨zx,CurrentMain.PairedBitXorScan.value xp⟩ ⟨zy,CurrentMain.PairedBitXorScan.value yp⟩
  simpa only [CurrentMain.DyadicCellAddition.addCell,CurrentMain.DyadicCellAddition.commonExponent,
    ←hq,CurrentMain.DyadicCellAddition.alignedNumerator,hdx,hdy,mul_comm,
    CurrentMain.Current1094Row1DyadicReference.value] using hv

/-- The sum bits in the actual final marked output encode the denominator-
aligned sum. The common exponent is still the unchanged selected input word. -/
theorem output_value (xp yp xs ys:List Bool) (sx sy:Bool) (er ar:Registers) :
    let dx:=leftShift xp yp er
    let dy:=rightShift xp yp er
    let px:=MarkedZeroPadding.padded dx xs
    let py:=MarkedZeroPadding.padded dy ys
    let p:=SignedWordAlignment.aligned px sx py sy
    let low:=SequentialBitAddition.scan p (SequentialBitAddition.zeroCarry (MarkedPairLayout.clearScratch ar))
    let lastLow:=SequentialBitAddition.sumBit sx sy low.registers.carry
    let sign:=SequentialBitAddition.sumBit sx sy (SequentialBitAddition.carryBit sx sy low.registers.carry)
    (MarkedLayoutAddition.outputRows px py sx sy ar).map Prod.snd=low.output++[lastLow,sign] ∧
    CurrentMain.Current1094Row1DyadicReference.value
      ⟨signedValue (low.output++[lastLow]) sign,CurrentMain.PairedBitXorScan.value (commonWord xp yp er)⟩ =
      (signedValue xs sx:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value xp)+
      (signedValue ys sy:Real)/(2:Real)^(CurrentMain.PairedBitXorScan.value yp) := by
  have h:=PaddedSignedAddition.output_scaled_sum (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy ar
  dsimp only at h ⊢
  refine ⟨h.1,?_⟩
  rw [h.2]
  exact denominator_alignment xp yp er (signedValue xs sx) (signedValue ys sy)

def cargoCells (c:Cargo) : Nat :=
  BinaryToUnaryControl.tapeCells c.leftData+BinaryToUnaryControl.tapeCells c.rightData+
  BinaryToUnaryControl.tapeCells c.leftPadded+BinaryToUnaryControl.tapeCells c.rightPadded+
  BinaryToUnaryControl.tapeCells c.zeroControl+MarkedBitDifference.tapeCells c.output

def frameCells (f:Frame) : Nat :=
  BinaryToUnaryControl.tapeCells f.leftExponent+BinaryToUnaryControl.tapeCells f.rightExponent+
  MarkedBitDifference.tapeCells f.paired+BinaryToUnaryControl.tapeCells f.counter

/-- Every physical tape is counted once, in every finite phase. -/
def cells : State → Nat
  | .computing e c | .zeroRight e c | .ready e c => EncodedExponentControl.cells e+cargoCells c
  | .adding f _ s => frameCells f+PaddedSignedAddition.cells s

theorem routed_adding_cells (f:Frame) (reverse:Bool) (s:PaddedSignedAddition.State) (k:Nat) :
    cells (run k (.adding f reverse (route reverse s)))=
      frameCells f+PaddedSignedAddition.cells (PaddedSignedAddition.run k s) := by
  rw [adding_run];simp only [cells,routed_cells]

/-- All eleven entrance tapes, including four real input blocks and their
markers. Seven work tapes are physically blank at the entrance. -/
theorem entrance_cells (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    cells (initial xp yp xs ys sx sy bl br er ar)=xp.length+yp.length+xs.length+ys.length+8 := by
  simp [cells,initial,EncodedExponentControl.initial,EncodedExponentControl.cells,MarkedPairLayout.initial,
    MarkedPairLayout.cells,MarkedPairLayout.tapeCells,cargoCells,cargo,BinaryToUnaryControl.tapeCells,
    MarkedBitDifference.tapeCells,MarkedZeroPadding.marked,MarkedZeroPadding.bits]
  omega

/-- The entire delegated addition prefix retains all four exponent-side tapes
and both physically routed control tapes. No buffer is omitted from this bound. -/
theorem addition_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (.adding (finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
      (route (EncodedExponentControl.reverseFlag xp yp er)
        (PaddedSignedAddition.initial (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy bl br ar)))) ≤
      frameCells (finalFrame xp yp er)+
        2*((leftShift xp yp er+xs.length)+(rightShift xp yp er+ys.length))+
        max (leftShift xp yp er+xs.length) (rightShift xp yp er+ys.length)+16 := by
  rw [routed_adding_cells]
  have h:=PaddedSignedAddition.machine_prefix_storage (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy bl br ar k
  omega

end EncodedDyadicAddition

#print axioms EncodedDyadicAddition.swap_involutive
#print axioms EncodedDyadicAddition.routed_step
#print axioms EncodedDyadicAddition.routed_cells
#print axioms EncodedDyadicAddition.control_handoff
#print axioms EncodedDyadicAddition.machine_exact
#print axioms EncodedDyadicAddition.machine_result
#print axioms EncodedDyadicAddition.adding_run
#print axioms EncodedDyadicAddition.exponent_alignment
#print axioms EncodedDyadicAddition.denominator_alignment
#print axioms EncodedDyadicAddition.output_value
#print axioms EncodedDyadicAddition.addition_prefix_storage
#print axioms EncodedDyadicAddition.routed_adding_cells
#print axioms EncodedDyadicAddition.entrance_cells
#check @EncodedDyadicAddition.machine_result
#check @EncodedDyadicAddition.denominator_alignment

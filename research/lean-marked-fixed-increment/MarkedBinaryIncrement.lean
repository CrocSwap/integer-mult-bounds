import CounterArithmetic
import MarkedZeroPadding

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Marked-zipper/head-layout refinement of the existing fixed-width RippleCounter.
The carry table is the same local bit complement/propagate/stop table, with one
charged entrance move and return to the left marker. Existing updated/overflow
and modular arithmetic proofs are imported unchanged. No new counter algorithm.
Every input width, including zero, has an executed overflow result. Capacity
value(word)+1<2^width is necessary for a genuine p+1 exponent at unchanged width.
No high-bit allocation or silent overflow widening occurs. Initial marked word
and its reserved capacity are supplied; the old overflow register is overwritten.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace MarkedBinaryIncrement
open CurrentMain.PairedBitXorScan (Tape value)
open MarkedZeroPadding (Symbol marked bits)

inductive Phase where
  | enter | carry | rewind | halt
  deriving DecidableEq
structure State where
  tape : Tape Symbol
  overflow : Bool
  phase : Phase
  deriving DecidableEq

def step (s:State) : State :=
  match s.phase with
  | .halt => s
  | .enter =>
      if s.tape.readHead .blank=.leftMarker then
        {s with tape:=s.tape.moveRight .blank,overflow:=false,phase:=.carry}
      else {s with phase:=.halt}
  | .carry => match s.tape.readHead .blank with
      | .data true => {s with tape:=(s.tape.writeHead (.data false)).moveRight .blank}
      | .data false => ⟨(s.tape.writeHead (.data true)).moveLeft .blank,false,.rewind⟩
      | .rightMarker => {s with tape:=s.tape.moveLeft .blank,overflow:=true,phase:=.rewind}
      | _ => {s with phase:=.halt}
  | .rewind =>
      if s.tape.readHead .blank=.leftMarker then {s with phase:=.halt}
      else {s with tape:=s.tape.moveLeft .blank}

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
inductive Trace : Nat → State → State → Prop where
  | nil (s:State) : Trace 0 s s
  | next {k:Nat} {s t:State} (live:s.phase≠.halt) (tail:Trace k (step s) t) : Trace (k+1) s t
private theorem trace_trans {m n:Nat} {s u t:State} (h:Trace m s u) (g:Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)
private theorem trace_sound {n:Nat} {s t:State} (h:Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih
private theorem trace_live {n:Nat} {s t:State} (h:Trace n s t) (k:Nat) (hk:k<n) : (run k s).phase≠.halt := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih => cases k with
    | zero => exact live
    | succ k => exact ih k (by omega)
private theorem halt_run (s:State) (h:s.phase=.halt) (k:Nat) : run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run,step,h] using ih

/-- Proof observation only: left bits are nearest first. -/
def position (left rest:List Bool) : Tape Symbol :=
  ⟨bits left++[.leftMarker],bits rest++[.rightMarker]⟩
def rewinding (left right:List Bool) : Tape Symbol :=
  match left with
  | [] => ⟨[],.leftMarker::(bits right++[.rightMarker])⟩
  | b::rest => ⟨bits rest++[.leftMarker],.data b::(bits right++[.rightMarker])⟩

private theorem write_right (left rest:List Bool) :
    ((position left (true::rest)).writeHead (.data false)).moveRight .blank=
      position (false::left) rest := by
  simp [position,bits,Tape.writeHead,Tape.moveRight]
private theorem write_left (left rest:List Bool) :
    ((position left (false::rest)).writeHead (.data true)).moveLeft .blank=
      rewinding left (true::rest) := by
  cases left <;> simp [position,rewinding,bits,Tape.writeHead,Tape.moveLeft]
private theorem delimiter_left (left:List Bool) :
    (position left []).moveLeft .blank=rewinding left [] := by
  cases left <;> simp [position,rewinding,bits,Tape.moveLeft]
private theorem rewind_left (b:Bool) (left right:List Bool) :
    (rewinding (b::left) right).moveLeft .blank=rewinding left (b::right) := by
  cases left <;> simp [rewinding,bits,Tape.moveLeft]

/-- The local return is the accepted counter's rewind pattern, ending on L. -/
private theorem rewind_exact (left right:List Bool) (flag:Bool) :
    Trace (left.length+1) ⟨rewinding left right,flag,.rewind⟩
      ⟨marked (bits (left.reverse++right)),flag,.halt⟩ := by
  induction left generalizing right with
  | nil =>
      apply Trace.next (by simp)
      simpa [step,rewinding,Tape.readHead,marked] using
        Trace.nil (⟨marked (bits right),flag,.halt⟩:State)
  | cons b rest ih =>
      apply Trace.next (by simp)
      have hs:step (⟨rewinding (b::rest) right,flag,.rewind⟩:State)=
          ⟨rewinding rest (b::right),flag,.rewind⟩ := by
        simp only [step,rewinding,Tape.readHead,reduceCtorEq,if_false]
        rw [show (⟨bits rest++[.leftMarker],.data b::(bits right++[.rightMarker])⟩:Tape Symbol).moveLeft .blank=
          rewinding rest (b::right) from rewind_left b rest right]
        rfl
      rw [hs]
      simpa [List.reverse_cons,List.append_assoc] using ih (b::right)

/-- Actual carry scan uses the existing carryLength/stopTail/overflow data.
Those recursive observations never run as bulk list operations in step. -/
private theorem carry_exact (xs left:List Bool) :
    Trace (RippleCounter.carryLength true xs+1) ⟨position left xs,false,.carry⟩
      ⟨rewinding (List.replicate (RippleCounter.carryLength true xs) false++left)
          (RippleCounter.stopTail true xs),RippleCounter.overflow true xs,.rewind⟩ := by
  induction xs generalizing left with
  | nil =>
      apply Trace.next (by simp)
      change Trace 0 ⟨(position left []).moveLeft .blank,true,.rewind⟩
        ⟨rewinding left [],true,.rewind⟩
      rw [delimiter_left]
      exact Trace.nil _
  | cons b xs ih => cases b with
    | false =>
        apply Trace.next (by simp)
        change Trace 0 ⟨((position left (false::xs)).writeHead (.data true)).moveLeft .blank,false,.rewind⟩
          ⟨rewinding left (true::xs),false,.rewind⟩
        rw [write_left]
        exact Trace.nil _
    | true =>
        have h:=ih (false::left)
        apply Trace.next (by simp)
        simpa [step,position,bits,Tape.readHead,Tape.writeHead,Tape.moveRight,
          RippleCounter.carryLength,RippleCounter.stopTail,RippleCounter.overflow,
          List.replicate_succ',List.append_assoc] using h

def initial (xs:List Bool) (oldFlag:Bool) : State:=⟨marked (bits xs),oldFlag,.enter⟩
def final (xs:List Bool) : State:=
  ⟨marked (bits (RippleCounter.updated true xs)),RippleCounter.overflow true xs,.halt⟩
def totalTime (xs:List Bool) : Nat:=RippleCounter.steps true xs+1

theorem increment_exact (xs:List Bool) (oldFlag:Bool) :
    Trace (totalTime xs) (initial xs oldFlag) (final xs) := by
  have hs:Trace 1 (initial xs oldFlag) ⟨position [] xs,false,.carry⟩ := by
    apply Trace.next (by simp [initial])
    simpa [initial,step,marked,position,Tape.readHead,Tape.moveRight,bits] using
      Trace.nil (⟨position [] xs,false,.carry⟩:State)
  have hc:=carry_exact xs []
  simp only [List.append_nil] at hc
  have hr:=rewind_exact (List.replicate (RippleCounter.carryLength true xs) false)
    (RippleCounter.stopTail true xs) (RippleCounter.overflow true xs)
  have h:=trace_trans (trace_trans hs hc) hr
  have ht : 1 + (RippleCounter.carryLength true xs+1) +
      ((List.replicate (RippleCounter.carryLength true xs) false).length+1)=totalTime xs := by
    simp only [List.length_replicate,totalTime,RippleCounter.steps]
    omega
  rw [ht] at h
  simpa [final,RippleCounter.updated,List.reverse_replicate] using h

theorem increment_result (xs:List Bool) (oldFlag:Bool) :
    run (totalTime xs) (initial xs oldFlag)=final xs ∧
    (final xs).phase=.halt ∧ ∀ k<totalTime xs,(run k (initial xs oldFlag)).phase≠.halt :=
  ⟨trace_sound (increment_exact xs oldFlag),rfl,trace_live (increment_exact xs oldFlag)⟩

/-- The two imported little-endian numeral conventions coincide. -/
theorem value_compat (xs:List Bool) : CounterArithmetic.value xs=value xs := by
  induction xs with
  | nil => rfl
  | cons b xs ih => cases b <;> simp [CounterArithmetic.value,value,ih,Nat.add_comm]

theorem modular_value (xs:List Bool) :
    value (RippleCounter.updated true xs)+(if RippleCounter.overflow true xs then 2^xs.length else 0)=value xs+1 := by
  simpa only [value_compat] using CounterArithmetic.increment_value xs

theorem capacity_iff (xs:List Bool) :
    RippleCounter.overflow true xs=false ↔ value xs+1<2^xs.length := by
  have hm:=CounterArithmetic.increment_overflow_iff_max xs
  have hv:=CounterArithmetic.value_bound xs
  rw [value_compat] at hm hv
  cases hf:RippleCounter.overflow true xs <;> simp [hf] at hm ⊢ <;> omega

/-- Exact exponent p+1 is conditional on actual available fixed-width capacity.
Overflow is still executed and reported for every other word, including []. -/
theorem increment_without_overflow (xs:List Bool) (oldFlag:Bool)
    (capacity:value xs+1<2^xs.length) :
    (run (totalTime xs) (initial xs oldFlag)).tape=marked (bits (RippleCounter.updated true xs)) ∧
    (run (totalTime xs) (initial xs oldFlag)).overflow=false ∧
    value (RippleCounter.updated true xs)=value xs+1 := by
  have hf:=(capacity_iff xs).mpr capacity
  have hv:=modular_value xs
  rw [(increment_result xs oldFlag).1]
  exact ⟨rfl,hf,by simpa [hf] using hv⟩

theorem time_bound (xs:List Bool) : totalTime xs≤2*xs.length+3 := by
  have h:=CounterArithmetic.carryLength_le_length true xs
  unfold totalTime RippleCounter.steps
  omega

def cells (s:State) : Nat:=s.tape.left.length+s.tape.right.length
private theorem right_cells (t:Tape Symbol) :
    t.left.length+t.right.length≤(t.moveRight .blank).left.length+(t.moveRight .blank).right.length := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [Tape.moveRight,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem left_cells (t:Tape Symbol) :
    t.left.length+t.right.length≤(t.moveLeft .blank).left.length+(t.moveLeft .blank).right.length := by
  rcases t with ⟨ls,rs⟩;cases ls <;> simp [Tape.moveLeft,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem write_cells (t:Tape Symbol) (b:Bool) :
    t.left.length+t.right.length≤(t.writeHead (.data b)).left.length+(t.writeHead (.data b)).right.length := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [Tape.writeHead]
theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases hp:s.phase with
  | halt => simp [step,hp]
  | enter =>
      have h:=right_cells s.tape
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | carry =>
      have hl:=left_cells s.tape
      have hw0:=(write_cells s.tape false).trans (right_cells _)
      have hw1:=(write_cells s.tape true).trans (left_cells _)
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | rewind =>
      have h:=left_cells s.tape
      simp only [step,hp];split <;> simp only [cells] <;> omega
private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t) (ht:t.phase=.halt) (k:Nat) :
    cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

theorem increment_prefix_storage (xs:List Bool) (oldFlag:Bool) (k:Nat) :
    cells (run k (initial xs oldFlag))≤xs.length+2 := by
  have h:=trace_storage (increment_exact xs oldFlag) rfl k
  simpa [final,cells,marked,bits,CounterArithmetic.updated_length,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using h

end MarkedBinaryIncrement
#print axioms MarkedBinaryIncrement.increment_exact
#print axioms MarkedBinaryIncrement.increment_result
#print axioms MarkedBinaryIncrement.value_compat
#print axioms MarkedBinaryIncrement.modular_value
#print axioms MarkedBinaryIncrement.capacity_iff
#print axioms MarkedBinaryIncrement.increment_without_overflow
#print axioms MarkedBinaryIncrement.time_bound
#print axioms MarkedBinaryIncrement.step_cells
#print axioms MarkedBinaryIncrement.increment_prefix_storage
#check @MarkedBinaryIncrement.increment_without_overflow
#check @MarkedBinaryIncrement.increment_prefix_storage

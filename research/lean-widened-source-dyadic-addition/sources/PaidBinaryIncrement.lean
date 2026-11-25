import MarkedBinaryIncrement

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Paid overflow widening after the unchanged accepted fixed-width counter.
A charged finite branch either halts or scans the actual updated work tape to
R, overwrites R with high bit1, allocates the new R in the adjacent blank cell,
and returns to L. No high bit is appended by a runtime list operation.
The input is an independent marked working tape with blank exterior. This is
not an in-place operation on a packed slot whose right neighbor may be data.
The old word/flag are overwritten; no inverse or input encoder is claimed.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace PaidBinaryIncrement
open CurrentMain.PairedBitXorScan (Tape value)
open MarkedZeroPadding (Symbol marked bits)
open MarkedBinaryIncrement (position rewinding)

namespace Extension
inductive Phase where
  | enter | scan | placeEnd | rewind | halt
  deriving DecidableEq
structure State where
  tape : Tape Symbol
  phase : Phase
  deriving DecidableEq

def step (s:State) : State :=
  match s.phase with
  | .halt => s
  | .enter => if s.tape.readHead .blank=.leftMarker then
      ⟨s.tape.moveRight .blank,.scan⟩ else {s with phase:=.halt}
  | .scan => match s.tape.readHead .blank with
      | .data _ => {s with tape:=s.tape.moveRight .blank}
      | .rightMarker => ⟨(s.tape.writeHead (.data true)).moveRight .blank,.placeEnd⟩
      | _ => {s with phase:=.halt}
  | .placeEnd => if s.tape.readHead .blank=.blank then
      ⟨(s.tape.writeHead .rightMarker).moveLeft .blank,.rewind⟩ else {s with phase:=.halt}
  | .rewind => if s.tape.readHead .blank=.leftMarker then
      {s with phase:=.halt} else {s with tape:=s.tape.moveLeft .blank}
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
private theorem rewind_exact (left right:List Bool) :
    Trace (left.length+1) ⟨rewinding left right,.rewind⟩
      ⟨marked (bits (left.reverse++right)),.halt⟩ := by
  induction left generalizing right with
  | nil =>
      apply Trace.next (by simp)
      simpa [step,rewinding,Tape.readHead,marked] using
        Trace.nil (⟨marked (bits right),.halt⟩:State)
  | cons b rest ih =>
      apply Trace.next (by simp)
      have hs:step (⟨rewinding (b::rest) right,.rewind⟩:State)=
          ⟨rewinding rest (b::right),.rewind⟩ := by
        cases rest <;> simp [step,rewinding,bits,Tape.readHead,Tape.moveLeft]
      rw [hs]
      simpa [List.reverse_cons,List.append_assoc] using ih (b::right)

/-- The old R cell becomes high1; the next genuinely blank cell gets new R. -/
private theorem scan_exact (xs left:List Bool) :
    Trace (xs.length+2) ⟨position left xs,.scan⟩
      ⟨rewinding (true::(xs.reverse++left)) [],.rewind⟩ := by
  induction xs generalizing left with
  | nil =>
      apply Trace.next (by simp)
      apply Trace.next (by simp [step,position,bits,Tape.readHead])
      simpa [step,position,rewinding,bits,Tape.readHead,Tape.writeHead,Tape.moveRight,Tape.moveLeft] using
        Trace.nil (⟨rewinding (true::left) [],.rewind⟩:State)
  | cons b xs ih =>
      apply Trace.next (by simp)
      have hs:step (⟨position left (b::xs),.scan⟩:State)=⟨position (b::left) xs,.scan⟩ := by
        simp [step,position,bits,Tape.readHead,Tape.moveRight]
      rw [hs]
      simpa [List.reverse_cons,List.append_assoc] using ih (b::left)

def initial (xs:List Bool) : State:=⟨marked (bits xs),.enter⟩
def final (xs:List Bool) : State:=⟨marked (bits (xs++[true])),.halt⟩

theorem extension_exact (xs:List Bool) : Trace (2*xs.length+5) (initial xs) (final xs) := by
  have he:Trace 1 (initial xs) ⟨position [] xs,.scan⟩ := by
    apply Trace.next (by simp [initial])
    simpa [initial,step,position,marked,bits,Tape.readHead,Tape.moveRight] using
      Trace.nil (⟨position [] xs,.scan⟩:State)
  have hs:=scan_exact xs []
  simp only [List.append_nil] at hs
  have hr:=rewind_exact (true::xs.reverse) []
  have h:=trace_trans (trace_trans he hs) hr
  have ht:1+(xs.length+2)+((true::xs.reverse).length+1)=2*xs.length+5 := by
    simp only [List.length_cons,List.length_reverse]
    omega
  rw [ht] at h
  simpa [final,List.reverse_cons] using h

def cells (s:State) : Nat:=s.tape.left.length+s.tape.right.length
private theorem right_cells (t:Tape Symbol) :
    t.left.length+t.right.length≤(t.moveRight .blank).left.length+(t.moveRight .blank).right.length := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [Tape.moveRight,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem left_cells (t:Tape Symbol) :
    t.left.length+t.right.length≤(t.moveLeft .blank).left.length+(t.moveLeft .blank).right.length := by
  rcases t with ⟨ls,rs⟩;cases ls <;> simp [Tape.moveLeft,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem write_cells (t:Tape Symbol) (a:Symbol) :
    t.left.length+t.right.length≤(t.writeHead a).left.length+(t.writeHead a).right.length := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [Tape.writeHead]
theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases hp:s.phase with
  | halt => simp [step,hp]
  | enter =>
      have h:=right_cells s.tape
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | scan =>
      have h:=right_cells s.tape
      have hw:=(write_cells s.tape (.data true)).trans (right_cells _)
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | placeEnd =>
      have hw:=(write_cells s.tape .rightMarker).trans (left_cells _)
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | rewind =>
      have h:=left_cells s.tape
      simp only [step,hp];split <;> simp only [cells] <;> omega
end Extension

inductive State where
  | incrementing (s:MarkedBinaryIncrement.State)
  | extending (s:Extension.State)
  | done (tape:Tape Symbol) (widened:Bool)
  deriving DecidableEq

def step : State → State
  | .incrementing s => if s.phase=.halt then
      if s.overflow then .extending ⟨s.tape,.enter⟩ else .done s.tape s.overflow
      else .incrementing (MarkedBinaryIncrement.step s)
  | .extending s => .extending (Extension.step s)
  | .done t b => .done t b

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
def Halted : State → Prop
  | .incrementing _ => False
  | .extending s => s.phase=.halt
  | .done .. => True
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
private theorem incrementing_trace {n:Nat} {s t:MarkedBinaryIncrement.State}
    (h:MarkedBinaryIncrement.Trace n s t) : Trace n (.incrementing s) (.incrementing t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,live,if_false] using ih
private theorem extending_trace {n:Nat} {s t:Extension.State}
    (h:Extension.Trace n s t) : Trace n (.extending s) (.extending t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def initial (xs:List Bool) (oldFlag:Bool) : State:=.incrementing (MarkedBinaryIncrement.initial xs oldFlag)
def outputWord (xs:List Bool) : List Bool :=
  if RippleCounter.overflow true xs then RippleCounter.updated true xs++[true] else RippleCounter.updated true xs
def final (xs:List Bool) : State :=
  if RippleCounter.overflow true xs then .extending (Extension.final (RippleCounter.updated true xs))
  else .done (marked (bits (RippleCounter.updated true xs))) false
def totalTime (xs:List Bool) : Nat :=
  MarkedBinaryIncrement.totalTime xs+1+(if RippleCounter.overflow true xs then 2*xs.length+5 else 0)
def outputTape : State → Tape Symbol
  | .incrementing s => s.tape
  | .extending s => s.tape
  | .done t _ => t

theorem machine_exact (xs:List Bool) (oldFlag:Bool) : Trace (totalTime xs) (initial xs oldFlag) (final xs) := by
  have hi:=incrementing_trace (MarkedBinaryIncrement.increment_exact xs oldFlag)
  cases hf:RippleCounter.overflow true xs with
  | false =>
      have hb:Trace 1 (.incrementing (MarkedBinaryIncrement.final xs)) (final xs) := by
        apply Trace.next (by simp [Halted])
        simpa [step,MarkedBinaryIncrement.final,final,hf] using Trace.nil (final xs)
      simpa [initial,totalTime,hf] using trace_trans hi hb
  | true =>
      have hb:Trace 1 (.incrementing (MarkedBinaryIncrement.final xs))
          (.extending (Extension.initial (RippleCounter.updated true xs))) := by
        apply Trace.next (by simp [Halted])
        simpa [step,MarkedBinaryIncrement.final,Extension.initial,hf] using
          Trace.nil (.extending (Extension.initial (RippleCounter.updated true xs)))
      have h:=trace_trans (trace_trans hi hb) (extending_trace (Extension.extension_exact (RippleCounter.updated true xs)))
      simpa [initial,totalTime,final,hf,CounterArithmetic.updated_length] using h

theorem machine_result (xs:List Bool) (oldFlag:Bool) :
    run (totalTime xs) (initial xs oldFlag)=final xs ∧ Halted (final xs) ∧
    ∀ k<totalTime xs,¬Halted (run k (initial xs oldFlag)) := by
  refine ⟨trace_sound (machine_exact xs oldFlag),?_,trace_live (machine_exact xs oldFlag)⟩
  cases hf:RippleCounter.overflow true xs <;> simp [final,hf,Halted,Extension.final]

theorem final_output (xs:List Bool) : outputTape (final xs)=marked (bits (outputWord xs)) := by
  cases hf:RippleCounter.overflow true xs <;> simp [outputTape,final,outputWord,Extension.final,hf]

private theorem value_high (xs:List Bool) : value (xs++[true])=value xs+2^xs.length := by
  induction xs with
  | nil => rfl
  | cons b xs ih => cases b <;> simp [value,ih,pow_succ] <;> omega

/-- No capacity or canonical-width premise: the actual output encodes p+1. -/
theorem output_value (xs:List Bool) : value (outputWord xs)=value xs+1 := by
  have h:=MarkedBinaryIncrement.modular_value xs
  cases hf:RippleCounter.overflow true xs with
  | false => simpa [outputWord,hf] using h
  | true =>
      simp only [outputWord,hf,if_true,value_high,CounterArithmetic.updated_length]
      simpa [hf] using h

theorem output_length (xs:List Bool) :
    (outputWord xs).length=xs.length+(if RippleCounter.overflow true xs then 1 else 0) := by
  cases hf:RippleCounter.overflow true xs <;> simp [outputWord,hf,CounterArithmetic.updated_length]

theorem time_bound (xs:List Bool) : totalTime xs≤4*xs.length+9 := by
  have h:=MarkedBinaryIncrement.time_bound xs
  unfold totalTime
  split <;> omega

def cells (s:State) : Nat:=(outputTape s).left.length+(outputTape s).right.length
theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases s with
  | incrementing s =>
      have h:=MarkedBinaryIncrement.step_cells s
      simp only [step];split
      · split <;> simp [cells,outputTape]
      · exact h
  | extending s => exact Extension.step_cells s
  | done t flag => exact Nat.le_refl _
private theorem halt_step (s:State) (h:Halted s) : step s=s := by
  cases s with
  | incrementing s => exact False.elim h
  | extending s => simp [step,Extension.step,show s.phase=.halt from h]
  | done t b => rfl
private theorem halt_run (s:State) (h:Halted s) (k:Nat) : run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [run,halt_step s h] using ih
private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t) (ht:Halted t) (k:Nat) : cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

theorem machine_prefix_storage (xs:List Bool) (oldFlag:Bool) (k:Nat) :
    cells (run k (initial xs oldFlag))≤xs.length+3 := by
  have h:=trace_storage (machine_exact xs oldFlag) (machine_result xs oldFlag).2.1 k
  have he:cells (final xs)=(outputWord xs).length+2 := by
    simp [cells,final_output,marked,bits]
  rw [he,output_length] at h
  split at h <;> omega

end PaidBinaryIncrement
#print axioms PaidBinaryIncrement.Extension.extension_exact
#print axioms PaidBinaryIncrement.machine_exact
#print axioms PaidBinaryIncrement.machine_result
#print axioms PaidBinaryIncrement.final_output
#print axioms PaidBinaryIncrement.output_value
#print axioms PaidBinaryIncrement.output_length
#print axioms PaidBinaryIncrement.time_bound
#print axioms PaidBinaryIncrement.step_cells
#print axioms PaidBinaryIncrement.machine_prefix_storage
#check @PaidBinaryIncrement.machine_result
#check @PaidBinaryIncrement.output_value
#check @PaidBinaryIncrement.machine_prefix_storage

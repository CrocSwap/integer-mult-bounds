import BinaryToUnaryControl

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
A paid two-tape adapter from an embedded final sign bit to a separate-sign
entrance. The source is preserved. A one-bit delayed scan copies only data
whose successor is another data symbol, and obtains the sign only by reading
the final data bit before the actual right marker. Both output markers are
written, both heads return, and the held-bit scratch is cleared. Initial
scratch/sign registers may be dirty and are overwritten, not restored.
The low word may be empty: its input then contains the single sign bit.
Actual first halt is 5*n+10 finite multitape transitions; every prefix has at
most 2*n+5 represented cells. No list/Nat operation appears in step.
The supplied marked source and independent blank output remain inputs.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace MarkedSignedWordSplit
open CurrentMain.PairedBitXorScan (Tape)
open MarkedZeroPadding (Symbol bits marked)

inductive Phase where
  | setup | enter | readCurrent | look | emit | writeRight | rewindInput | rewindOutput | halt
  deriving DecidableEq
structure State where
  input : Tape Symbol
  output : Tape Symbol
  held : Bool
  sign : Bool
  phase : Phase
  deriving DecidableEq

/-- Each branch inspects only a current symbol and finite control. Reads,
writes and one-cell head motions are the declared finite transition actions. -/
def step (s:State) : State :=
  match s.phase with
  | .halt => s
  | .setup => {s with output:=(s.output.writeHead .leftMarker).moveRight .blank,phase:=.enter}
  | .enter =>
      if s.input.readHead .blank=.leftMarker then
        {s with input:=s.input.moveRight .blank,phase:=.readCurrent}
      else {s with phase:=.halt}
  | .readCurrent => match s.input.readHead .blank with
      | .data b => {s with input:=s.input.moveRight .blank,held:=b,phase:=.look}
      | _ => {s with phase:=.halt}
  | .look => match s.input.readHead .blank with
      | .data _ => {s with phase:=.emit}
      | .rightMarker => {s with sign:=s.held,phase:=.writeRight}
      | _ => {s with phase:=.halt}
  | .emit => {s with output:=(s.output.writeHead (.data s.held)).moveRight .blank,phase:=.readCurrent}
  | .writeRight => {s with output:=s.output.writeHead .rightMarker,phase:=.rewindInput}
  | .rewindInput =>
      if s.input.readHead .blank=.leftMarker then {s with phase:=.rewindOutput}
      else {s with input:=s.input.moveLeft .blank}
  | .rewindOutput =>
      if s.output.readHead .blank=.leftMarker then {s with held:=false,phase:=.halt}
      else {s with output:=s.output.moveLeft .blank}

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

/-- Proof observation of the delayed scan, absent from the transition. -/
def reading (low:List Bool) (sign:Bool) (ls os:List Symbol) (held oldSign:Bool) : State :=
  ⟨⟨ls,bits (low++[sign])++[.rightMarker]⟩,⟨os,[]⟩,held,oldSign,.readCurrent⟩
private theorem scan_exact (low:List Bool) (sign:Bool) (ls os:List Symbol) (held oldSign:Bool) :
    Trace (3*low.length+2) (reading low sign ls os held oldSign)
      (⟨⟨.data sign::((bits low).reverse++ls),[.rightMarker]⟩,
        ⟨(bits low).reverse++os,[]⟩,sign,sign,.writeRight⟩:State) := by
  induction low generalizing ls os held with
  | nil =>
      apply Trace.next (by simp [reading])
      apply Trace.next (by simp [step,reading,bits,Tape.readHead,Tape.moveRight])
      simpa [step,reading,bits,Tape.readHead,Tape.moveRight] using
        Trace.nil (⟨⟨.data sign::ls,[.rightMarker]⟩,⟨os,[]⟩,sign,sign,.writeRight⟩:State)
  | cons b low ih =>
      have h:=ih (.data b::ls) (.data b::os) b
      have hdata:∃ z zs,low++[sign]=z::zs := by cases low <;> simp
      rcases hdata with ⟨z,zs,hz⟩
      apply Trace.next (by simp [reading])
      apply Trace.next (by simp [step,reading,bits,Tape.readHead,Tape.moveRight,hz])
      apply Trace.next (by simp [step,reading,bits,Tape.readHead,Tape.moveRight,hz])
      simpa [step,reading,bits,Tape.readHead,Tape.writeHead,Tape.moveRight,
        List.reverse_cons,List.append_assoc,hz,Nat.mul_add,Nat.add_assoc] using h

private theorem rewind_input (ls rs:List Symbol) (hls:∀ x∈ls,x≠.leftMarker)
    (hrs:rs.head?≠some .leftMarker) (out:Tape Symbol) (held sign:Bool) :
    Trace (ls.length+2)
      (⟨⟨ls++[.leftMarker],rs⟩,out,held,sign,.rewindInput⟩:State)
      (⟨⟨[],.leftMarker::(ls.reverse++rs)⟩,out,held,sign,.rewindOutput⟩:State) := by
  induction ls generalizing rs with
  | nil =>
      have hr:(⟨[.leftMarker],rs⟩:Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      change Trace 2 (⟨⟨[.leftMarker],rs⟩,out,held,sign,.rewindInput⟩:State)
        (⟨⟨[],.leftMarker::rs⟩,out,held,sign,.rewindOutput⟩:State)
      apply Trace.next (by simp)
      simp only [step,hr,if_false,Tape.moveLeft]
      apply Trace.next (by simp)
      simp only [step,Tape.readHead,if_true]
      exact Trace.nil _
  | cons b ls ih =>
      have hr:(⟨(b::ls)++[.leftMarker],rs⟩:Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      have hb:b≠.leftMarker:=hls b (by simp)
      have h:=ih (b::rs) (by intro x hx;exact hls x (by simp [hx])) (by simpa using hb)
      apply Trace.next (by simp)
      simp only [Tape.readHead] at hr
      simpa [step,hr,Tape.readHead,Tape.moveLeft,List.reverse_cons,List.append_assoc,Nat.add_assoc] using h

private theorem rewind_output (ls rs:List Symbol) (hls:∀ x∈ls,x≠.leftMarker)
    (hrs:rs.head?≠some .leftMarker) (inp:Tape Symbol) (held sign:Bool) :
    Trace (ls.length+2)
      (⟨inp,⟨ls++[.leftMarker],rs⟩,held,sign,.rewindOutput⟩:State)
      (⟨inp,⟨[],.leftMarker::(ls.reverse++rs)⟩,false,sign,.halt⟩:State) := by
  induction ls generalizing rs with
  | nil =>
      have hr:(⟨[.leftMarker],rs⟩:Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      change Trace 2 (⟨inp,⟨[.leftMarker],rs⟩,held,sign,.rewindOutput⟩:State)
        (⟨inp,⟨[],.leftMarker::rs⟩,false,sign,.halt⟩:State)
      apply Trace.next (by simp)
      simp only [step,hr,if_false,Tape.moveLeft]
      apply Trace.next (by simp)
      simp only [step,Tape.readHead,if_true]
      exact Trace.nil _
  | cons b ls ih =>
      have hr:(⟨(b::ls)++[.leftMarker],rs⟩:Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      have hb:b≠.leftMarker:=hls b (by simp)
      have h:=ih (b::rs) (by intro x hx;exact hls x (by simp [hx])) (by simpa using hb)
      apply Trace.next (by simp)
      simp only [Tape.readHead] at hr
      simpa [step,hr,Tape.readHead,Tape.moveLeft,List.reverse_cons,List.append_assoc,Nat.add_assoc] using h

private theorem bits_not_left (xs:List Bool) (x:Symbol) (h:x∈(bits xs).reverse) : x≠.leftMarker := by
  simp only [List.mem_reverse,bits,List.mem_map] at h
  rcases h with ⟨b,hb,rfl⟩
  simp

def initial (low:List Bool) (sign held oldSign:Bool) : State :=
  ⟨marked (bits (low++[sign])),⟨[],[]⟩,held,oldSign,.setup⟩
def final (low:List Bool) (sign:Bool) : State :=
  ⟨marked (bits (low++[sign])),marked (bits low),false,sign,.halt⟩
def totalTime (low:List Bool) : Nat := 5*low.length+10

/-- Complete execution includes both marker writes, actual final-bit read,
all return moves, scratch clearing and the nonempty sign-only case. -/
theorem split_exact (low:List Bool) (sign held oldSign:Bool) :
    Trace (totalTime low) (initial low sign held oldSign) (final low sign) := by
  have hs:Trace 2 (initial low sign held oldSign)
      (reading low sign [.leftMarker] [.leftMarker] held oldSign) := by
    apply Trace.next (by simp [initial])
    apply Trace.next (by simp [initial,step])
    simpa [initial,step,marked,reading,Tape.writeHead,Tape.moveRight,Tape.readHead] using
      Trace.nil (reading low sign [.leftMarker] [.leftMarker] held oldSign)
  have hm:=scan_exact low sign [.leftMarker] [.leftMarker] held oldSign
  let mid:State:=⟨⟨.data sign::((bits low).reverse++[.leftMarker]),[.rightMarker]⟩,
    ⟨(bits low).reverse++[.leftMarker],[]⟩,sign,sign,.writeRight⟩
  have hw:Trace 1 mid (step mid):=Trace.next (by simp [mid]) (Trace.nil _)
  have hi:=rewind_input (.data sign::(bits low).reverse) [.rightMarker]
    (by intro x hx;rcases List.mem_cons.mp hx with h|h;subst x;simp;exact bits_not_left low x h)
    (by simp) ⟨(bits low).reverse++[.leftMarker],[.rightMarker]⟩ sign sign
  have ho:=rewind_output (bits low).reverse [.rightMarker] (bits_not_left low) (by simp)
    (marked (bits (low++[sign]))) sign sign
  have hi':Trace (low.length+1+2) (step mid)
      (⟨marked (bits (low++[sign])),⟨(bits low).reverse++[.leftMarker],[.rightMarker]⟩,
        sign,sign,.rewindOutput⟩:State) := by
    simpa [mid,step,Tape.writeHead,marked,bits,List.reverse_cons,List.reverse_append,
      List.append_assoc,Nat.add_assoc] using hi
  have ho':Trace (low.length+2)
      (⟨marked (bits (low++[sign])),⟨(bits low).reverse++[.leftMarker],[.rightMarker]⟩,
        sign,sign,.rewindOutput⟩:State) (final low sign) := by
    simpa [final,marked,bits] using ho
  have hf:=trace_trans (trace_trans hw hi') ho'
  have h:=trace_trans (trace_trans hs hm) hf
  have he:2+(3*low.length+2)+(1+(low.length+1+2)+(low.length+2))=totalTime low := by
    unfold totalTime;omega
  rw [he] at h
  exact h

theorem split_result (low:List Bool) (sign held oldSign:Bool) :
    run (totalTime low) (initial low sign held oldSign)=final low sign ∧
    (final low sign).phase=.halt ∧
    ∀ k<totalTime low,(run k (initial low sign held oldSign)).phase≠.halt :=
  ⟨trace_sound (split_exact low sign held oldSign),rfl,trace_live (split_exact low sign held oldSign)⟩

/-- Endpoint is exactly the separate-sign consumer layout; the original
embedded word and its head are preserved. -/
theorem split_layout (low:List Bool) (sign held oldSign:Bool) :
    let s:=run (totalTime low) (initial low sign held oldSign)
    s.input=marked (bits (low++[sign])) ∧ s.output=marked (bits low) ∧
    s.sign=sign ∧ s.held=false := by
  rw [(split_result low sign held oldSign).1]
  exact ⟨rfl,rfl,rfl,rfl⟩

def tapeCells (t:Tape Symbol) : Nat:=t.left.length+t.right.length
def cells (s:State) : Nat:=tapeCells s.input+tapeCells s.output
private theorem write_cells (t:Tape Symbol) (x:Symbol) : tapeCells t≤tapeCells (t.writeHead x) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.writeHead]
private theorem right_cells (t:Tape Symbol) : tapeCells t≤tapeCells (t.moveRight .blank) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.moveRight,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem left_cells (t:Tape Symbol) : tapeCells t≤tapeCells (t.moveLeft .blank) := by
  rcases t with ⟨ls,rs⟩;cases ls <;> simp [tapeCells,Tape.moveLeft,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases hp:s.phase with
  | halt => simp [step,hp]
  | setup =>
      have h:=(write_cells s.output .leftMarker).trans (right_cells _)
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.input)
  | enter =>
      have h:=right_cells s.input
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | readCurrent =>
      have h:=right_cells s.input
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | look => simp only [step,hp];split <;> simp [cells]
  | emit =>
      have h:=(write_cells s.output (.data s.held)).trans (right_cells _)
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.input)
  | writeRight =>
      have h:=write_cells s.output .rightMarker
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.input)
  | rewindInput =>
      have h:=left_cells s.input
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | rewindOutput =>
      have h:=left_cells s.output
      simp only [step,hp];split <;> simp only [cells] <;> omega
private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t) (ht:t.phase=.halt) (k:Nat) :
    cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih => cases k with
    | zero => exact (step_cells s).trans (ih ht 0)
    | succ k => exact ih ht k

theorem split_prefix_storage (low:List Bool) (sign held oldSign:Bool) (k:Nat) :
    cells (run k (initial low sign held oldSign))≤2*low.length+5 := by
  have h:=trace_storage (split_exact low sign held oldSign) rfl k
  simpa [final,cells,tapeCells,marked,bits,Nat.mul_add,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm,
    Nat.two_mul] using h

end MarkedSignedWordSplit
#print axioms MarkedSignedWordSplit.split_exact
#print axioms MarkedSignedWordSplit.split_result
#print axioms MarkedSignedWordSplit.split_layout
#print axioms MarkedSignedWordSplit.step_cells
#print axioms MarkedSignedWordSplit.split_prefix_storage
#check @MarkedSignedWordSplit.split_result
#check @MarkedSignedWordSplit.split_layout

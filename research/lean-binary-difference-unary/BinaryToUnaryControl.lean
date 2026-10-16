import MarkedZeroPadding

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Two-tape, explicit-symbol binary-to-unary control production. The supplied
little-endian marked binary counter is consumed to zeros of the same width.
The initially blank second tape becomes exactly the padder's marked unary
control. Each full borrow sweep, rewind, tick write and final return is an
actual bounded finite-alphabet transition. No Nat arithmetic, list length,
random address or zipper boundary test appears in step.

For input width w and numeric value d, the first halt takes
  d*(2*w+6)+2*w+8
transitions and every prefix uses at most w+d+4 represented tape cells.
This is a bound in numeric magnitude, not linear time in encoded bit length.
The initial binary encoding, subtraction of two exponents, fresh independent
output storage and physical tape allocation remain supplied. The counter is
zeroed, not restored; no dirty-storage inverse is claimed.
Author-checked context kappa=836330098538459/500000000000000000.
Source candidate; actual acceptance is recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace BinaryToUnaryControl
open CurrentMain.PairedBitXorScan (Tape value)
open MarkedZeroPadding (Symbol bits ticks marked)

/-- Finite Boolean borrow update. These functions specify the trace; only
one Boolean instance is evaluated by any actual scan transition. -/
def nextBorrow (borrow bit : Bool) : Bool := borrow && !bit

def decrement : Bool → List Bool → List Bool
  | _, [] => []
  | b, x::xs => (x ^^ b) :: decrement (nextBorrow b x) xs

def borrowOut : Bool → List Bool → Bool
  | b, [] => b
  | b, x::xs => borrowOut (nextBorrow b x) xs

@[simp] theorem decrement_length (b : Bool) (xs : List Bool) :
    (decrement b xs).length=xs.length := by
  induction xs generalizing b with
  | nil => rfl
  | cons x xs ih => simp [decrement,ih]

private theorem decrement_false (xs : List Bool) : decrement false xs=xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => cases x <;> simp [decrement,nextBorrow,ih]

private theorem borrow_false (xs : List Bool) : borrowOut false xs=false := by
  induction xs with
  | nil => rfl
  | cons x xs ih => cases x <;> simp [borrowOut,nextBorrow,ih]

/-- Overflow is exactly the zero-input case, including an empty counter. -/
theorem borrow_zero_iff (xs : List Bool) : borrowOut true xs=true ↔ value xs=0 := by
  induction xs with
  | nil => simp [borrowOut,value]
  | cons x xs ih =>
      cases x <;> simp [borrowOut,nextBorrow,borrow_false,value,ih]

/-- The executed low-bit-first borrow scan decreases every positive value by
one without changing the represented bit width. -/
theorem decrement_value (xs : List Bool) (h : 0<value xs) :
    value (decrement true xs)+1=value xs := by
  induction xs with
  | nil => simp [value] at h
  | cons x xs ih =>
      cases x with
      | false =>
          have hp:0<value xs := by simpa [value] using h
          have hv:=ih hp
          simp [decrement,nextBorrow,value]
          omega
      | true => simp [decrement,nextBorrow,decrement_false,value,Nat.add_comm]

inductive Phase where
  | setup | enter | scan | rewindCounter | emit | writeRight | rewindOutput | halt
  deriving DecidableEq

structure State where
  counter : Tape Symbol
  output : Tape Symbol
  borrow : Bool
  phase : Phase
  deriving DecidableEq

/-- A finite multitape transition. A scan may write and move its one current
counter head; emit may write and move its one current output head. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .setup => {s with output := (s.output.writeHead .leftMarker).moveRight .blank, phase := .enter}
  | .enter =>
      match s.counter.readHead .blank with
      | .leftMarker => {s with counter := s.counter.moveRight .blank, borrow := true, phase := .scan}
      | _ => {s with phase := .halt}
  | .scan =>
      match s.counter.readHead .blank with
      | .data x => {s with counter := (s.counter.writeHead (.data (x ^^ s.borrow))).moveRight .blank, borrow := nextBorrow s.borrow x}
      | .rightMarker => {s with phase := .rewindCounter}
      | _ => {s with phase := .halt}
  | .rewindCounter =>
      match s.counter.readHead .blank with
      | .rightMarker => {s with counter := s.counter.moveLeft .blank}
      | .data x => {s with counter :=
          (s.counter.writeHead (.data (if s.borrow then false else x))).moveLeft .blank}
      | .leftMarker => {s with borrow := false, phase := if s.borrow then .writeRight else .emit}
      | _ => {s with phase := .halt}
  | .emit => {s with output := (s.output.writeHead .tick).moveRight .blank, phase := .enter}
  | .writeRight => {s with output := s.output.writeHead .rightMarker, phase := .rewindOutput}
  | .rewindOutput =>
      if s.output.readHead .blank = .leftMarker then {s with phase := .halt}
      else {s with output := s.output.moveLeft .blank}

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : s.phase ≠ .halt)
      (tail : Trace k (step s) t) : Trace (k+1) s t

private theorem trace_one (s : State) (h:s.phase≠.halt) : Trace 1 s (step s) :=
  Trace.next h (Trace.nil _)
private theorem trace_trans {m n : Nat} {s u t : State}
    (h:Trace m s u) (g:Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)
private theorem trace_sound {n : Nat} {s t : State} (h:Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih
private theorem trace_live {n : Nat} {s t : State} (h:Trace n s t)
    (k : Nat) (hk:k<n) : (run k s).phase≠.halt := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih => cases k with
    | zero => exact live
    | succ k => exact ih k (by omega)
private theorem halt_run (s : State) (h:s.phase=.halt) (k : Nat) : run k s=s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run,step,h] using ih

/-- Observation states do not occur as bulk operations in step. -/
def scanning (xs : List Bool) (ls : List Symbol) (out : Tape Symbol) (b : Bool) : State :=
  ⟨⟨ls,bits xs++[.rightMarker]⟩,out,b,.scan⟩

private theorem scan_exact (xs : List Bool) (ls : List Symbol) (out : Tape Symbol) (b : Bool) :
    Trace xs.length (scanning xs ls out b)
      (scanning [] ((bits (decrement b xs)).reverse++ls) out (borrowOut b xs)) := by
  induction xs generalizing ls b with
  | nil => simpa [scanning,decrement,borrowOut,bits] using Trace.nil (scanning [] ls out b)
  | cons x xs ih =>
      have ht:=ih (.data (x ^^ b)::ls) (nextBorrow b x)
      apply Trace.next (by simp [scanning])
      simpa [scanning,step,Tape.readHead,Tape.writeHead,Tape.moveRight,bits,
        decrement,borrowOut,List.append_assoc] using ht

/-- Counter return transforms data only in the underflow case; it restores
zero cells instead of leaving the modular all-ones underflow result. -/
def cleared (b : Bool) (xs : List Bool) : List Bool := xs.map (fun x => if b then false else x)

def cleanSymbol (b : Bool) : Symbol → Symbol
  | .data x => .data (if b then false else x)
  | a => a

private theorem rewind_counter (ls : List Bool) (a : Symbol) (rs : List Symbol)
    (ha : a=.rightMarker ∨ ∃ x, a=.data x) (out : Tape Symbol) (b : Bool) :
    Trace (ls.length+2)
      (⟨⟨bits ls++[.leftMarker],a::rs⟩,out,b,.rewindCounter⟩ : State)
      (⟨⟨[],.leftMarker::(bits (cleared b ls.reverse)++cleanSymbol b a::rs)⟩,
        out,false,if b then .writeRight else .emit⟩ : State) := by
  induction ls generalizing a rs with
  | nil =>
      rcases ha with rfl | ⟨x,rfl⟩ <;> cases b <;>
        apply Trace.next (by simp) <;>
        apply Trace.next (by simp [step,Tape.readHead,Tape.writeHead,Tape.moveLeft,bits]) <;>
        simp only [step,Tape.readHead,Tape.writeHead,Tape.moveLeft,bits,
          List.map_nil,List.nil_append,cleared,cleanSymbol,Bool.false_eq_true,
          if_false,if_true]
      all_goals exact Trace.nil _
  | cons x ls ih =>
      have ht:=ih (.data x) (cleanSymbol b a::rs) (Or.inr ⟨x,rfl⟩)
      rcases ha with rfl | ⟨y,rfl⟩ <;>
        apply Trace.next (by simp) <;>
        simpa [step,Tape.readHead,Tape.writeHead,Tape.moveLeft,bits,cleared,
          cleanSymbol,List.map_append,List.append_assoc] using ht

def roundStart (xs : List Bool) (out : Tape Symbol) : State :=
  ⟨marked (bits xs),out,false,.enter⟩

private theorem counter_round (xs : List Bool) (out : Tape Symbol) :
    Trace (2*xs.length+4) (roundStart xs out)
      (⟨marked (bits (cleared (borrowOut true xs) (decrement true xs))),out,false,
        if borrowOut true xs then .writeRight else .emit⟩ : State) := by
  have he:=trace_one (roundStart xs out) (by simp [roundStart])
  have hs:=scan_exact xs [.leftMarker] out true
  have hswitch:=trace_one
    (scanning [] ((bits (decrement true xs)).reverse++[.leftMarker]) out (borrowOut true xs))
    (by simp [scanning])
  have hr:=rewind_counter (decrement true xs).reverse .rightMarker [] (Or.inl rfl)
    out (borrowOut true xs)
  have hfirst:Trace (1+xs.length+1) (roundStart xs out)
      (⟨⟨bits (decrement true xs).reverse++[.leftMarker],[.rightMarker]⟩,
        out,borrowOut true xs,.rewindCounter⟩ : State) := by
    simpa [roundStart,step,marked,bits,scanning,Tape.readHead,Tape.moveRight,
      List.map_reverse] using trace_trans (trace_trans he hs) hswitch
  have h:=trace_trans hfirst hr
  have hc:1+xs.length+1+((decrement true xs).reverse.length+2)=2*xs.length+4 := by simp;omega
  rw [hc] at h
  simpa [marked,List.reverse_reverse] using h

def pending (k : Nat) : Tape Symbol := ⟨ticks k++[.leftMarker],[]⟩

def zeroCounter (w : Nat) : Tape Symbol := marked (bits (List.replicate w false))

private theorem counter_positive (xs : List Bool) (h:0<value xs) (k : Nat) :
    Trace (2*xs.length+5) (roundStart xs (pending k))
      (roundStart (decrement true xs) (pending (k+1))) := by
  have hb:borrowOut true xs=false := by
    cases he:borrowOut true xs with
    | false => rfl
    | true => have hz: value xs=0 := (borrow_zero_iff xs).mp he;omega
  have hr:=counter_round xs (pending k)
  rw [hb] at hr
  simp only [cleared, Bool.false_eq_true, if_false, List.map_id'] at hr
  have he:=trace_one
    (⟨marked (bits (decrement true xs)),pending k,false,.emit⟩ : State) (by simp)
  have hh:Trace (2*xs.length+4+1) (roundStart xs (pending k))
      (roundStart (decrement true xs) (pending (k+1))) := by
    simpa [cleared,step,pending,ticks,roundStart,Tape.writeHead,Tape.moveRight,
      List.replicate_succ,List.append_assoc] using trace_trans hr he
  simpa only [Nat.add_assoc] using hh

private theorem counter_zero (xs : List Bool) (h:value xs=0) (k : Nat) :
    Trace (2*xs.length+4) (roundStart xs (pending k))
      (⟨zeroCounter xs.length,pending k,false,.writeRight⟩ : State) := by
  have hb:= (borrow_zero_iff xs).mpr h
  have hr:=counter_round xs (pending k)
  simpa [hb,cleared,zeroCounter,List.map_const'] using hr

/-- The induction is a proof about the actual repeated sweeps, not a Nat
loop inside the implementation. Each successful sweep emits one real tick. -/
private theorem loop_exact (d : Nat) (xs : List Bool) (hd:value xs=d) (k : Nat) :
    Trace (d*(2*xs.length+5)+2*xs.length+4) (roundStart xs (pending k))
      (⟨zeroCounter xs.length,pending (k+d),false,.writeRight⟩ : State) := by
  induction d generalizing xs k with
  | zero => simpa using counter_zero xs hd k
  | succ d ih =>
      have hp:0<value xs := by omega
      have hv:=decrement_value xs hp
      have hdec:value (decrement true xs)=d := by omega
      have hc:=counter_positive xs hp k
      have ht:=ih (decrement true xs) hdec (k+1)
      have hall:=trace_trans hc ht
      have he:(2*xs.length+5)+(d*(2*(decrement true xs).length+5)+2*(decrement true xs).length+4)
          =(d+1)*(2*xs.length+5)+2*xs.length+4 := by rw [decrement_length];ring
      rw [he] at hall
      simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hall

private theorem rewind_output (ls : List Symbol) (rs : List Symbol)
    (hls:∀ x∈ls, x≠.leftMarker) (hrs:rs.head?≠some .leftMarker)
    (counter:Tape Symbol) :
    Trace (ls.length+2)
      (⟨counter,⟨ls++[.leftMarker],rs⟩,false,.rewindOutput⟩ : State)
      (⟨counter,⟨[],.leftMarker::(ls.reverse++rs)⟩,false,.halt⟩ : State) := by
  induction ls generalizing rs with
  | nil =>
      have hr:(⟨[.leftMarker],rs⟩ : Tape Symbol).readHead .blank ≠ .leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      change Trace 2 (⟨counter,⟨[.leftMarker],rs⟩,false,.rewindOutput⟩ : State)
        (⟨counter,⟨[],.leftMarker::rs⟩,false,.halt⟩ : State)
      apply Trace.next (by simp)
      simp only [step,hr,if_false,Tape.moveLeft]
      apply Trace.next (by simp)
      simp only [step,Tape.readHead,if_true]
      exact Trace.nil _
  | cons a ls ih =>
      have hr:(⟨(a::ls)++[.leftMarker],rs⟩ : Tape Symbol).readHead .blank ≠ .leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      have ha:a≠.leftMarker:=hls a (by simp)
      have ht:=ih (a::rs) (by intro x hx;exact hls x (by simp [hx])) (by simpa using ha)
      apply Trace.next (by simp)
      simp only [Tape.readHead] at hr
      simpa [step,Tape.readHead,hr,Tape.moveLeft,List.reverse_cons,List.append_assoc,
        Nat.add_assoc] using ht

def initial (xs : List Bool) : State := ⟨marked (bits xs),⟨[],[]⟩,false,.setup⟩
def final (w d : Nat) : State := ⟨zeroCounter w,marked (ticks d),false,.halt⟩
def totalTime (xs : List Bool) : Nat := value xs*(2*xs.length+6)+2*xs.length+8

private theorem finish (w d : Nat) :
    Trace (d+3) (⟨zeroCounter w,pending d,false,.writeRight⟩ : State) (final w d) := by
  have hw:=trace_one (⟨zeroCounter w,pending d,false,.writeRight⟩ : State) (by simp)
  have hr:=rewind_output (ticks d) [.rightMarker]
    (by intro x hx;have he: x=Symbol.tick := (List.mem_replicate.mp hx).2;simp [he])
    (by simp) (zeroCounter w)
  have h:=trace_trans hw hr
  simpa [step,pending,Tape.writeHead,ticks,final,marked,List.reverse_replicate,
    Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using h

/-- Complete control production from an actual encoded binary magnitude. -/
theorem conversion_exact (xs : List Bool) :
    Trace (totalTime xs) (initial xs) (final xs.length (value xs)) := by
  have hs:=trace_one (initial xs) (by simp [initial])
  have hl:=loop_exact (value xs) xs rfl 0
  simp only [Nat.zero_add] at hl
  have hf:=finish xs.length (value xs)
  have h:Trace (1+(value xs*(2*xs.length+5)+2*xs.length+4)+(value xs+3))
      (initial xs) (final xs.length (value xs)) := by
    simpa [step,initial,roundStart,pending,ticks,Tape.writeHead,Tape.moveRight]
      using trace_trans (trace_trans hs hl) hf
  have hc:1+(value xs*(2*xs.length+5)+2*xs.length+4)+(value xs+3)=totalTime xs := by
    unfold totalTime;ring
  rw [hc] at h
  exact h

theorem conversion_result (xs : List Bool) :
    run (totalTime xs) (initial xs)=final xs.length (value xs) ∧
    (final xs.length (value xs)).phase=.halt ∧
    ∀ k<totalTime xs, (run k (initial xs)).phase≠.halt :=
  ⟨trace_sound (conversion_exact xs),rfl,trace_live (conversion_exact xs)⟩

def tapeCells (t : Tape Symbol) : Nat := t.left.length+t.right.length
def cells (s : State) : Nat := tapeCells s.counter+tapeCells s.output

private theorem write_cells (t:Tape Symbol) (a:Symbol) : tapeCells t≤tapeCells (t.writeHead a) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.writeHead]
private theorem right_cells (t:Tape Symbol) : tapeCells t≤tapeCells (t.moveRight .blank) := by
  rcases t with ⟨ls,rs⟩;cases rs <;>
    simp [tapeCells,Tape.moveRight,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem left_cells (t:Tape Symbol) : tapeCells t≤tapeCells (t.moveLeft .blank) := by
  rcases t with ⟨ls,rs⟩;cases ls <;>
    simp [tapeCells,Tape.moveLeft,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem write_right_cells (t:Tape Symbol) (a:Symbol) :
    tapeCells t≤tapeCells ((t.writeHead a).moveRight .blank) :=
  (write_cells t a).trans (right_cells (t.writeHead a))
private theorem write_left_cells (t:Tape Symbol) (a:Symbol) :
    tapeCells t≤tapeCells ((t.writeHead a).moveLeft .blank) :=
  (write_cells t a).trans (left_cells (t.writeHead a))

/-- The actual transition never discards represented cells. Its final-state
size therefore bounds every prefix, including partial sweeps and dirty borrow. -/
theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases hp:s.phase with
  | halt => simp [step,hp]
  | setup =>
      have h:=write_right_cells s.output .leftMarker
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.counter)
  | enter =>
      have h:=right_cells s.counter
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | scan =>
      simp only [step,hp];split
      next x _ =>
        have h:=write_right_cells s.counter (.data (x ^^ s.borrow))
        simp only [cells];omega
      all_goals simp [cells]
  | rewindCounter =>
      simp only [step,hp];split
      next => have h:=left_cells s.counter;simp only [cells];omega
      next x _ =>
        have h:=write_left_cells s.counter (.data (if s.borrow then false else x))
        simp only [cells];omega
      all_goals simp [cells]
  | emit =>
      have h:=write_right_cells s.output .tick
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.counter)
  | writeRight =>
      have h:=write_cells s.output .rightMarker
      simpa [step,hp,cells] using Nat.add_le_add_left h (tapeCells s.counter)
  | rewindOutput =>
      have h:=left_cells s.output
      simp only [step,hp];split <;> simp only [cells] <;> omega

private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t)
    (ht:t.phase=.halt) (k:Nat) : cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih =>
      cases k with
      | zero => exact (step_cells s).trans (ih ht 0)
      | succ k => exact ih ht k

/-- Includes both actual counter markers and both newly written unary markers.
Fixed finite control and the one Boolean register are separate constant space. -/
theorem conversion_prefix_storage (xs:List Bool) (k:Nat) :
    cells (run k (initial xs))≤xs.length+value xs+4 := by
  have h:=trace_storage (conversion_exact xs) rfl k
  simp [final,zeroCounter,cells,tapeCells,marked,bits,ticks] at h ⊢
  omega

/-- Literal padder-compatible output; no copying or Nat-to-list operation is
hidden in the transition. This is an observation of the produced tape. -/
theorem produces_padding_control (xs:List Bool) :
    (run (totalTime xs) (initial xs)).output=MarkedZeroPadding.marked (MarkedZeroPadding.ticks (value xs)) := by
  rw [(conversion_result xs).1]
  rfl

end BinaryToUnaryControl

#print axioms BinaryToUnaryControl.decrement_length
#print axioms BinaryToUnaryControl.borrow_zero_iff
#print axioms BinaryToUnaryControl.decrement_value
#print axioms BinaryToUnaryControl.conversion_exact
#print axioms BinaryToUnaryControl.conversion_result
#check @BinaryToUnaryControl.conversion_result

#print axioms BinaryToUnaryControl.step_cells
#print axioms BinaryToUnaryControl.conversion_prefix_storage
#print axioms BinaryToUnaryControl.produces_padding_control
#check @BinaryToUnaryControl.conversion_prefix_storage

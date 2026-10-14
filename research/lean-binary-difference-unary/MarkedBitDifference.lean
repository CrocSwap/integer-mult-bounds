import PairedDifferenceArithmetic
import MarkedBitAddition
import MarkedZeroPadding

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
A symbol-only subtract/compare controller on an already paired, marked row
word. Seven-gate columns reuse SequentialBitAddition exactly, with complemented
operand reads and an executed carry-in true. Actual carry-out selects the
order branch. Underflow executes a paid rewind and opposite-direction pass.
The selected output is then physically copied to a fresh one-bit L/data/R tape;
its markers and both final head returns are charged. Scratch is cleared, and
the direction flag says whether the original left input was smaller.
Paired equal-width input formatting is supplied here; the existing paid layout
can provide it, but its enclosing handoff is not assumed free. No decoding,
Nat comparison/subtraction, zip or list copy is an instruction. Input encoding,
physical allocation and dirty-output inversion remain separate.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace MarkedBitDifference
open CurrentMain.PairedBitXorScan (Tape)
open SequentialBitAddition (PairBit Registers Gate Row)
open PairedDifferenceArithmetic
abbrev Symbol := MarkedBitAddition.Symbol
abbrev BitSymbol := MarkedZeroPadding.Symbol

inductive Phase where
  | enter | initialize | test | gate (g : Gate) | write | advance | rewind | branch
  | writeOutputLeft | enterOutput | enterInput | copyTest | copyWrite | copyAdvanceInput | copyAdvanceOutput
  | writeOutputRight | rewindOutput | rewindInput | clear (slot : SequentialBitAddition.ClearSlot) | halt
  deriving DecidableEq
structure State where
  tape : Tape Symbol
  output : Tape BitSymbol
  registers : Registers
  reverse : Bool
  phase : Phase
  deriving DecidableEq

def afterGate : Gate → Phase
  | .readLeft => .gate .readRight
  | .readRight => .gate .xorInputs
  | .xorInputs => .gate .xorCarry
  | .xorCarry => .gate .andInputs
  | .andInputs => .gate .andCarry
  | .andCarry => .gate .orCarry
  | .orCarry => .write
  | .clearCarry => .test

def afterClear : SequentialBitAddition.ClearSlot → Phase
  | .x => .clear .y
  | .y => .clear .carry
  | .carry => .clear .xorXY
  | .xorXY => .clear .sum
  | .sum => .clear .andXY
  | .andXY => .clear .andTC
  | .andTC => .halt

/-- One finite-symbol transition; each gate is the inherited Boolean gate.
The branch reads only two Boolean registers, never an integer relation. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .enter => match s.tape.readHead .blank with
    | .leftMarker => {s with tape := s.tape.moveRight .blank, phase := .initialize}
    | _ => {s with phase := .halt}
  | .initialize => {s with registers := oneCarry s.registers, phase := .test}
  | .test => match s.tape.readHead .blank with
    | .data _ => {s with phase := .gate .readLeft}
    | .rightMarker => {s with phase := .rewind}
    | _ => {s with phase := .halt}
  | .gate g => match s.tape.readHead .blank with
    | .data row => {s with registers := SequentialBitAddition.gateStep (operands s.reverse row.1) g s.registers, phase := afterGate g}
    | _ => {s with phase := .halt}
  | .write => match s.tape.readHead .blank with
    | .data row => {s with tape := s.tape.writeHead (MarkedBitAddition.Symbol.data (row.1,s.registers.sum)), phase := .advance}
    | _ => {s with phase := .halt}
  | .advance => {s with tape := s.tape.moveRight .blank, phase := .test}
  | .rewind => if s.tape.readHead .blank = .leftMarker then {s with phase := .branch}
      else {s with tape := s.tape.moveLeft .blank}
  | .branch => if s.reverse = false ∧ s.registers.carry = false then
      {s with reverse := true, phase := .enter} else {s with phase := .writeOutputLeft}
  | .writeOutputLeft => {s with output := s.output.writeHead .leftMarker, phase := .enterOutput}
  | .enterOutput => {s with output := s.output.moveRight .blank, phase := .enterInput}
  | .enterInput => {s with tape := s.tape.moveRight .blank, phase := .copyTest}
  | .copyTest => match s.tape.readHead .blank with
    | .data row => {s with registers := {s.registers with sum := row.2}, phase := .copyWrite}
    | .rightMarker => {s with phase := .writeOutputRight}
    | _ => {s with phase := .halt}
  | .copyWrite => {s with output := s.output.writeHead (MarkedZeroPadding.Symbol.data s.registers.sum), phase := .copyAdvanceInput}
  | .copyAdvanceInput => {s with tape := s.tape.moveRight .blank, phase := .copyAdvanceOutput}
  | .copyAdvanceOutput => {s with output := s.output.moveRight .blank, phase := .copyTest}
  | .writeOutputRight => {s with output := s.output.writeHead .rightMarker, phase := .rewindOutput}
  | .rewindOutput => if s.output.readHead .blank = .leftMarker then {s with phase := .rewindInput}
      else {s with output := s.output.moveLeft .blank}
  | .rewindInput => if s.tape.readHead .blank = .leftMarker then {s with phase := .clear .x}
      else {s with tape := s.tape.moveLeft .blank}
  | .clear slot => {s with registers := SequentialBitAddition.clearSlot slot s.registers, phase := afterClear slot}

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)
inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : s.phase≠.halt)
      (tail : Trace k (step s) t) : Trace (k+1) s t
private theorem trace_one (s:State) (h:s.phase≠.halt) : Trace 1 s (step s) := Trace.next h (Trace.nil _)
private theorem trace_trans {m n:Nat} {s u t:State} (h:Trace m s u) (g:Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)
private theorem trace_sound {k:Nat} {s t:State} (h:Trace k s t) : run k s=t := by
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

def transformed (reverse : Bool) : List Row → Registers → List Row
  | [],_ => []
  | row::rows,r =>
      let next:=SequentialBitAddition.column (operands reverse row.1) r
      (row.1,next.sum)::transformed reverse rows next

theorem transformed_sources (reverse:Bool) (rows:List Row) (r:Registers) :
    (transformed reverse rows r).map Prod.fst=rows.map Prod.fst := by
  induction rows generalizing r with
  | nil => rfl
  | cons row rows ih => simp only [transformed,List.map_cons,ih]

theorem transformed_output (reverse:Bool) (rows:List Row) (r:Registers) :
    (transformed reverse rows r).map Prod.snd=
      (SequentialBitAddition.scan (inputPairs reverse (rows.map Prod.fst)) r).output := by
  induction rows generalizing r with
  | nil => rfl
  | cons row rows ih => simp only [transformed,List.map_cons,inputPairs,SequentialBitAddition.scan,ih]

theorem transformed_length (reverse:Bool) (rows:List Row) (r:Registers) :
    (transformed reverse rows r).length=rows.length := by
  simpa only [List.length_map] using congrArg List.length (transformed_sources reverse rows r)

/-- The concrete output scratch word is initially supplied; subtraction
preserves input tracks and overwrites exactly this row's output track. -/
private theorem column_ten (reverse:Bool) (row:Row) (ls rs:List Symbol) (out:Tape BitSymbol)
    (r:Registers) {n:Nat} {t:State}
    (h:Trace n
      (⟨⟨MarkedBitAddition.Symbol.data (row.1,(SequentialBitAddition.column (operands reverse row.1) r).sum)::ls,rs⟩,
        out,SequentialBitAddition.column (operands reverse row.1) r,reverse,.test⟩ : State) t) :
    Trace (n+10) (⟨⟨ls,MarkedBitAddition.Symbol.data row::rs⟩,out,r,reverse,.test⟩ : State) t := by
  apply Trace.next (by simp)
  apply Trace.next (by simp [step,Tape.readHead])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  apply Trace.next (by simp [step,Tape.readHead,afterGate])
  simpa only [step,Tape.readHead,Tape.writeHead,Tape.moveRight,afterGate,
    SequentialBitAddition.column,SequentialBitAddition.runGates,
    SequentialBitAddition.columnGates,SequentialBitAddition.gateStep] using h

private theorem scan_rows (reverse:Bool) (rows:List Row) (ls:List Symbol)
    (out:Tape BitSymbol) (r:Registers) :
    Trace (10*rows.length)
      (⟨⟨ls,rows.map MarkedBitAddition.Symbol.data++[.rightMarker]⟩,out,r,reverse,.test⟩ : State)
      (⟨⟨(transformed reverse rows r).reverse.map MarkedBitAddition.Symbol.data++ls,[.rightMarker]⟩,
        out,(SequentialBitAddition.scan (inputPairs reverse (rows.map Prod.fst)) r).registers,
        reverse,.test⟩ : State) := by
  induction rows generalizing ls r with
  | nil => simpa [transformed,inputPairs,SequentialBitAddition.scan] using
      Trace.nil (⟨⟨ls,[.rightMarker]⟩,out,r,reverse,.test⟩ : State)
  | cons row rows ih =>
      let next:=SequentialBitAddition.column (operands reverse row.1) r
      have h:=column_ten reverse row ls
        (rows.map MarkedBitAddition.Symbol.data++[.rightMarker]) out r
        (ih (MarkedBitAddition.Symbol.data (row.1,next.sum)::ls) next)
      have hc:10*rows.length+10=10*(row::rows).length := by simp;omega
      rw [hc] at h
      simpa [transformed,inputPairs,SequentialBitAddition.scan,next,List.reverse_cons,
        List.map_append,List.append_assoc] using h

def inputRewindPhase (finish:Bool) : Phase := if finish then .rewindInput else .rewind
def inputRewindNext (finish:Bool) : Phase := if finish then .clear .x else .branch

private theorem rewind_input (ls rs:List Symbol)
    (hls:∀ x∈ls,x≠.leftMarker) (hrs:rs.head?≠some .leftMarker)
    (out:Tape BitSymbol) (r:Registers) (reverse finish:Bool) :
    Trace (ls.length+2)
      (⟨⟨ls++[.leftMarker],rs⟩,out,r,reverse,inputRewindPhase finish⟩ : State)
      (⟨⟨[],.leftMarker::(ls.reverse++rs)⟩,out,r,reverse,inputRewindNext finish⟩ : State) := by
  induction ls generalizing rs with
  | nil =>
      have hr:(⟨[.leftMarker],rs⟩ : Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      change Trace 2 (⟨⟨[.leftMarker],rs⟩,out,r,reverse,inputRewindPhase finish⟩ : State)
        (⟨⟨[],.leftMarker::rs⟩,out,r,reverse,inputRewindNext finish⟩ : State)
      cases finish <;> apply Trace.next (by simp [inputRewindPhase]) <;>
        simp only [inputRewindPhase,if_true,if_false,step,hr,Tape.moveLeft] <;>
        apply Trace.next (by simp) <;>
        simp only [step,Tape.readHead,if_true,inputRewindNext,if_false]
      all_goals exact Trace.nil _
  | cons a ls ih =>
      have hr:(⟨(a::ls)++[.leftMarker],rs⟩ : Tape Symbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      have ha:a≠.leftMarker:=hls a (by simp)
      have ht:=ih (a::rs) (by intro x hx;exact hls x (by simp [hx])) (by simpa using ha)
      simp only [Tape.readHead] at hr
      cases finish <;> apply Trace.next (by simp [inputRewindPhase]) <;>
        simpa [inputRewindPhase,inputRewindNext,step,Tape.readHead,hr,Tape.moveLeft,
          List.reverse_cons,List.append_assoc,Nat.add_assoc] using ht

private theorem no_left_rows (rows:List Row) :
    ∀ x∈rows.map MarkedBitAddition.Symbol.data,x≠MarkedBitAddition.Symbol.leftMarker := by
  intro x hx
  obtain ⟨r,_,rfl⟩:=List.mem_map.mp hx
  simp

/-- One actual full directed subtract scan, including carry initialization
and paid head return, with final carry retained for the next branch. -/
theorem pass_exact (reverse:Bool) (rows:List Row) (out:Tape BitSymbol) (r:Registers) :
    Trace (11*rows.length+5)
      (⟨MarkedBitAddition.marked rows,out,r,reverse,.enter⟩ : State)
      (⟨MarkedBitAddition.marked (transformed reverse rows (oneCarry r)),out,
        (result reverse (rows.map Prod.fst) r).registers,reverse,.branch⟩ : State) := by
  have hs:=scan_rows reverse rows [.leftMarker] out (oneCarry r)
  have he:Trace 2 (⟨MarkedBitAddition.marked rows,out,r,reverse,.enter⟩ : State)
      (⟨⟨[.leftMarker],rows.map MarkedBitAddition.Symbol.data++[.rightMarker]⟩,
        out,oneCarry r,reverse,.test⟩ : State) := by
    apply Trace.next (by simp)
    apply Trace.next (by simp [step,MarkedBitAddition.marked,Tape.readHead])
    simp only [step,MarkedBitAddition.marked,Tape.readHead,Tape.moveRight]
    exact Trace.nil _
  let done:=transformed reverse rows (oneCarry r)
  let rf:=(result reverse (rows.map Prod.fst) r).registers
  have hr:=rewind_input (done.reverse.map MarkedBitAddition.Symbol.data) [.rightMarker]
    (no_left_rows done.reverse) (by simp) out rf reverse false
  have ht:=trace_one (⟨⟨done.reverse.map MarkedBitAddition.Symbol.data++[.leftMarker],
    [.rightMarker]⟩,out,rf,reverse,.test⟩ : State) (by simp)
  have all:=trace_trans (trace_trans (trace_trans he hs) ht) hr
  have hc:2+10*rows.length+1+((done.reverse.map MarkedBitAddition.Symbol.data).length+2)
      =11*rows.length+5 := by simp [done,transformed_length];omega
  rw [hc] at all
  simpa [done,rf,result,inputRewindPhase,inputRewindNext,step,Tape.readHead,
    MarkedBitAddition.marked,List.map_reverse] using all

/-- Copy reads the actually written output bit; other register fields are
retained until the explicit seven-register clear at the end. -/
def copyRegisters : List Row → Registers → Registers
  | [],r => r
  | row::rows,r => copyRegisters rows {r with sum := row.2}

private theorem copy_four (row:Row) (ls rs:List Symbol) (os:List BitSymbol)
    (r:Registers) (reverse:Bool) {n:Nat} {t:State}
    (h:Trace n
      (⟨⟨MarkedBitAddition.Symbol.data row::ls,rs⟩,
        ⟨MarkedZeroPadding.Symbol.data row.2::os,[]⟩,{r with sum:=row.2},reverse,.copyTest⟩ : State) t) :
    Trace (n+4)
      (⟨⟨ls,MarkedBitAddition.Symbol.data row::rs⟩,⟨os,[]⟩,r,reverse,.copyTest⟩ : State) t := by
  apply Trace.next (by simp)
  apply Trace.next (by simp [step,Tape.readHead])
  apply Trace.next (by simp [step,Tape.readHead])
  apply Trace.next (by simp [step,Tape.readHead])
  simpa only [step,Tape.readHead,Tape.writeHead,Tape.moveRight] using h

private theorem copy_rows (rows:List Row) (ls:List Symbol) (os:List BitSymbol)
    (r:Registers) (reverse:Bool) :
    Trace (4*rows.length)
      (⟨⟨ls,rows.map MarkedBitAddition.Symbol.data++[.rightMarker]⟩,⟨os,[]⟩,r,reverse,.copyTest⟩ : State)
      (⟨⟨rows.reverse.map MarkedBitAddition.Symbol.data++ls,[.rightMarker]⟩,
        ⟨(rows.map Prod.snd).reverse.map MarkedZeroPadding.Symbol.data++os,[]⟩,
        copyRegisters rows r,reverse,.copyTest⟩ : State) := by
  induction rows generalizing ls os r with
  | nil => simpa [copyRegisters] using (Trace.nil
      (⟨⟨ls,[.rightMarker]⟩,⟨os,[]⟩,r,reverse,.copyTest⟩ : State))
  | cons row rows ih =>
      have h:=copy_four row ls (rows.map MarkedBitAddition.Symbol.data++[.rightMarker]) os r reverse
        (ih (MarkedBitAddition.Symbol.data row::ls) (MarkedZeroPadding.Symbol.data row.2::os) {r with sum:=row.2})
      have hc:4*rows.length+4=4*(row::rows).length := by simp;omega
      rw [hc] at h
      simpa [copyRegisters,List.reverse_cons,List.map_append,List.append_assoc] using h

private theorem rewind_output (ls rs:List BitSymbol)
    (hls:∀ x∈ls,x≠.leftMarker) (hrs:rs.head?≠some .leftMarker)
    (input:Tape Symbol) (r:Registers) (reverse:Bool) :
    Trace (ls.length+2)
      (⟨input,⟨ls++[.leftMarker],rs⟩,r,reverse,.rewindOutput⟩ : State)
      (⟨input,⟨[],.leftMarker::(ls.reverse++rs)⟩,r,reverse,.rewindInput⟩ : State) := by
  induction ls generalizing rs with
  | nil =>
      have hr:(⟨[.leftMarker],rs⟩ : Tape BitSymbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      change Trace 2 (⟨input,⟨[.leftMarker],rs⟩,r,reverse,.rewindOutput⟩ : State)
        (⟨input,⟨[],.leftMarker::rs⟩,r,reverse,.rewindInput⟩ : State)
      apply Trace.next (by simp)
      simp only [step,hr,if_false,Tape.moveLeft]
      apply Trace.next (by simp)
      simp only [step,Tape.readHead,if_true]
      exact Trace.nil _
  | cons a ls ih =>
      have hr:(⟨(a::ls)++[.leftMarker],rs⟩ : Tape BitSymbol).readHead .blank≠.leftMarker := by
        cases rs with
        | nil => simp [Tape.readHead]
        | cons x xs => simpa [Tape.readHead] using hrs
      have ha:a≠.leftMarker:=hls a (by simp)
      have ht:=ih (a::rs) (by intro x hx;exact hls x (by simp [hx])) (by simpa using ha)
      simp only [Tape.readHead] at hr
      apply Trace.next (by simp)
      simpa [step,Tape.readHead,hr,Tape.moveLeft,List.reverse_cons,List.append_assoc,Nat.add_assoc] using ht

private theorem clear_seven (input:Tape Symbol) (out:Tape BitSymbol) (r:Registers) (reverse:Bool) :
    Trace 7 (⟨input,out,r,reverse,.clear .x⟩ : State)
      (⟨input,out,SequentialBitAddition.clearRegisters,reverse,.halt⟩ : State) := by
  apply Trace.next (by simp)
  apply Trace.next (by simp [step,afterClear])
  apply Trace.next (by simp [step,afterClear])
  apply Trace.next (by simp [step,afterClear])
  apply Trace.next (by simp [step,afterClear])
  apply Trace.next (by simp [step,afterClear])
  apply Trace.next (by simp [step,afterClear])
  simp only [step,afterClear,SequentialBitAddition.clearSlot,SequentialBitAddition.clearRegisters]
  exact Trace.nil _

def copyFinal (rows:List Row) (reverse:Bool) : State :=
  ⟨MarkedBitAddition.marked rows,MarkedZeroPadding.marked (MarkedZeroPadding.bits (rows.map Prod.snd)),
    SequentialBitAddition.clearRegisters,reverse,.halt⟩

/-- All one-bit output cells and markers are produced by a paid copy; both
heads return and all seven scratch registers are cleared. -/
theorem extraction_exact (rows:List Row) (r:Registers) (reverse:Bool) :
    Trace (6*rows.length+16)
      (⟨MarkedBitAddition.marked rows,⟨[],[]⟩,r,reverse,.writeOutputLeft⟩ : State)
      (copyFinal rows reverse) := by
  let data:=rows.map Prod.snd
  let rf:=copyRegisters rows r
  have setup:Trace 3
      (⟨MarkedBitAddition.marked rows,⟨[],[]⟩,r,reverse,.writeOutputLeft⟩ : State)
      (⟨⟨[.leftMarker],rows.map MarkedBitAddition.Symbol.data++[.rightMarker]⟩,
        ⟨[.leftMarker],[]⟩,r,reverse,.copyTest⟩ : State) := by
    apply Trace.next (by simp)
    apply Trace.next (by simp [step])
    apply Trace.next (by simp [step])
    simp only [step,MarkedBitAddition.marked,Tape.writeHead,Tape.moveRight]
    exact Trace.nil _
  have scan:=copy_rows rows [.leftMarker] [.leftMarker] r reverse
  let inp:Tape Symbol:=⟨rows.reverse.map MarkedBitAddition.Symbol.data++[.leftMarker],[.rightMarker]⟩
  let out:Tape BitSymbol:=⟨data.reverse.map MarkedZeroPadding.Symbol.data++[.leftMarker],[]⟩
  have stop:Trace 2 (⟨inp,out,rf,reverse,.copyTest⟩ : State)
      (⟨inp,⟨out.left,[.rightMarker]⟩,rf,reverse,.rewindOutput⟩ : State) := by
    apply Trace.next (by simp)
    apply Trace.next (by simp [step,inp,Tape.readHead])
    simp only [step,inp,Tape.readHead,out,Tape.writeHead]
    exact Trace.nil _
  have ho:=rewind_output (data.reverse.map MarkedZeroPadding.Symbol.data) [.rightMarker]
    (by intro x hx;obtain ⟨a,_,rfl⟩:=List.mem_map.mp hx;simp) (by simp) inp rf reverse
  have hi:=rewind_input (rows.reverse.map MarkedBitAddition.Symbol.data) [.rightMarker]
    (no_left_rows rows.reverse) (by simp) (MarkedZeroPadding.marked (MarkedZeroPadding.bits data)) rf reverse true
  have hc:=clear_seven (MarkedBitAddition.marked rows)
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits data)) rf reverse
  have ho':Trace (data.length+2)
      (⟨inp,⟨out.left,[.rightMarker]⟩,rf,reverse,.rewindOutput⟩ : State)
      (⟨inp,MarkedZeroPadding.marked (MarkedZeroPadding.bits data),rf,reverse,.rewindInput⟩ : State) := by
    simpa [out,MarkedZeroPadding.marked,MarkedZeroPadding.bits,List.map_reverse] using ho
  have hi':Trace (rows.length+2)
      (⟨inp,MarkedZeroPadding.marked (MarkedZeroPadding.bits data),rf,reverse,.rewindInput⟩ : State)
      (⟨MarkedBitAddition.marked rows,MarkedZeroPadding.marked (MarkedZeroPadding.bits data),rf,reverse,.clear .x⟩ : State) := by
    simpa [inp,inputRewindPhase,inputRewindNext,MarkedBitAddition.marked,List.map_reverse] using hi
  have h:=trace_trans (trace_trans (trace_trans (trace_trans (trace_trans setup scan) stop) ho') hi') hc
  have count:3+4*rows.length+2+(data.length+2)+(rows.length+2)+7=6*rows.length+16 := by
    simp [data];omega
  rw [count] at h
  simpa [inp,out,rf,data,copyFinal,inputRewindPhase,inputRewindNext,
    MarkedBitAddition.marked,MarkedZeroPadding.marked,MarkedZeroPadding.bits,List.map_reverse] using h

def firstRows (rows:List Row) (r:Registers) := transformed false rows (oneCarry r)
def firstRegisters (rows:List Row) (r:Registers) := (result false (rows.map Prod.fst) r).registers
def chosenReverse (rows:List Row) (r:Registers) : Bool := !(firstRegisters rows r).carry
def chosenRows (rows:List Row) (r:Registers) : List Row :=
  if (firstRegisters rows r).carry then firstRows rows r
  else transformed true (firstRows rows r) (oneCarry (firstRegisters rows r))
def totalTime (rows:List Row) (r:Registers) : Nat :=
  if (firstRegisters rows r).carry then 17*rows.length+22 else 28*rows.length+28
def initial (rows:List Row) (r:Registers) : State :=
  ⟨MarkedBitAddition.marked rows,⟨[],[]⟩,r,false,.enter⟩
def final (rows:List Row) (r:Registers) : State :=
  copyFinal (chosenRows rows r) (chosenReverse rows r)

/-- Complete executed pass/branch/extraction composition. A false first carry
executes the entire second pass; neither direction is chosen by a Nat oracle. -/
theorem difference_exact (rows:List Row) (r:Registers) :
    Trace (totalTime rows r) (initial rows r) (final rows r) := by
  have h1:=pass_exact false rows (⟨[],[]⟩ : Tape BitSymbol) r
  cases hc:(firstRegisters rows r).carry with
  | true =>
      have hb:Trace 1
          (⟨MarkedBitAddition.marked (firstRows rows r),⟨[],[]⟩,
            firstRegisters rows r,false,.branch⟩ : State)
          (⟨MarkedBitAddition.marked (firstRows rows r),⟨[],[]⟩,
            firstRegisters rows r,false,.writeOutputLeft⟩ : State) := by
        apply Trace.next (by simp)
        simp only [step,hc,Bool.true_eq_false,and_false,if_false]
        exact Trace.nil _
      have he:=extraction_exact (firstRows rows r) (firstRegisters rows r) false
      have h:=trace_trans (trace_trans h1 hb) he
      have hn:(firstRows rows r).length=rows.length:=transformed_length _ _ _
      rw [hn] at h
      have count:(11*rows.length+5)+1+(6*rows.length+16)=17*rows.length+22 := by omega
      rw [count] at h
      simpa [initial,final,totalTime,chosenRows,chosenReverse,hc] using h
  | false =>
      have hb:Trace 1
          (⟨MarkedBitAddition.marked (firstRows rows r),⟨[],[]⟩,
            firstRegisters rows r,false,.branch⟩ : State)
          (⟨MarkedBitAddition.marked (firstRows rows r),⟨[],[]⟩,
            firstRegisters rows r,true,.enter⟩ : State) := by
        apply Trace.next (by simp)
        simp only [step,hc,and_self,if_true]
        exact Trace.nil _
      let second:=transformed true (firstRows rows r) (oneCarry (firstRegisters rows r))
      let rf:=(result true ((firstRows rows r).map Prod.fst) (firstRegisters rows r)).registers
      have h2:=pass_exact true (firstRows rows r) (⟨[],[]⟩ : Tape BitSymbol) (firstRegisters rows r)
      have hb2:Trace 1 (⟨MarkedBitAddition.marked second,⟨[],[]⟩,rf,true,.branch⟩ : State)
          (⟨MarkedBitAddition.marked second,⟨[],[]⟩,rf,true,.writeOutputLeft⟩ : State) := by
        apply Trace.next (by simp)
        simp only [step,Bool.true_eq_false,false_and,if_false]
        exact Trace.nil _
      have he:=extraction_exact second rf true
      have h:=trace_trans (trace_trans (trace_trans (trace_trans h1 hb) h2) hb2) he
      have hn:(firstRows rows r).length=rows.length:=transformed_length _ _ _
      have hs:second.length=rows.length := (transformed_length _ _ _).trans hn
      rw [hn,hs] at h
      have count:(11*rows.length+5)+1+(11*rows.length+5)+1+(6*rows.length+16)=28*rows.length+28 := by omega
      rw [count] at h
      simpa [initial,final,totalTime,chosenRows,chosenReverse,hc,second,rf] using h

theorem difference_result (rows:List Row) (r:Registers) :
    run (totalTime rows r) (initial rows r)=final rows r ∧
    (final rows r).phase=.halt ∧
    ∀ k<totalTime rows r,(run k (initial rows r)).phase≠.halt :=
  ⟨trace_sound (difference_exact rows r),rfl,trace_live (difference_exact rows r)⟩

theorem time_bound (rows:List Row) (r:Registers) : totalTime rows r≤28*rows.length+28 := by
  unfold totalTime
  split <;> omega

theorem chosen_sources (rows:List Row) (r:Registers) :
    (chosenRows rows r).map Prod.fst=rows.map Prod.fst := by
  unfold chosenRows
  split <;> simp only [firstRows,transformed_sources]

theorem chosen_length (rows:List Row) (r:Registers) :
    (chosenRows rows r).length=rows.length := by
  simpa only [List.length_map] using congrArg List.length (chosen_sources rows r)

/-- Actual direction and copied bits derive order and magnitude. Leading-zero
input words and width zero are allowed. No nonnegative-order premise is used. -/
theorem chosen_value (rows:List Row) (r:Registers) :
    let p:=rows.map Prod.fst
    let out:=(chosenRows rows r).map Prod.snd
    if chosenReverse rows r then
      SequentialBitAddition.decode (SequentialBitAddition.leftBits p)<SequentialBitAddition.decode (SequentialBitAddition.rightBits p) ∧
      SequentialBitAddition.decode out=SequentialBitAddition.decode (SequentialBitAddition.rightBits p)-SequentialBitAddition.decode (SequentialBitAddition.leftBits p)
    else
      SequentialBitAddition.decode (SequentialBitAddition.rightBits p)≤SequentialBitAddition.decode (SequentialBitAddition.leftBits p) ∧
      SequentialBitAddition.decode out=SequentialBitAddition.decode (SequentialBitAddition.leftBits p)-SequentialBitAddition.decode (SequentialBitAddition.rightBits p) := by
  cases hc:(firstRegisters rows r).carry with
  | true =>
      have h:=forward_shift (rows.map Prod.fst) r hc
      simpa [chosenReverse,chosenRows,hc,firstRows,transformed_output,result] using And.intro h.2 h.1
  | false =>
      have h:=reverse_shift (rows.map Prod.fst) r (firstRegisters rows r) hc
      simpa [chosenReverse,chosenRows,hc,firstRows,transformed_output,transformed_sources,result] using And.intro h.2 h.1

def tapeCells {α:Type} (t:Tape α) : Nat := t.left.length+t.right.length
def cells (s:State) : Nat := tapeCells s.tape+tapeCells s.output
private theorem write_cells {α:Type} (t:Tape α) (a:α) : tapeCells t≤tapeCells (t.writeHead a) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.writeHead]
private theorem right_cells {α:Type} (t:Tape α) (blank:α) : tapeCells t≤tapeCells (t.moveRight blank) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.moveRight,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem left_cells {α:Type} (t:Tape α) (blank:α) : tapeCells t≤tapeCells (t.moveLeft blank) := by
  rcases t with ⟨ls,rs⟩;cases ls <;> simp [tapeCells,Tape.moveLeft,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem step_cells (s:State) : cells s≤cells (step s) := by
  cases hp:s.phase with
  | halt => simp [step,hp]
  | enter =>
      have h:=right_cells s.tape MarkedBitAddition.Symbol.blank
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | «initialize» => simp [step,hp,cells]
  | test => simp only [step,hp];split <;> simp [cells]
  | gate g => simp only [step,hp];split <;> simp [cells]
  | write =>
      simp only [step,hp];split
      next row _ =>
        have h:=write_cells s.tape (MarkedBitAddition.Symbol.data (row.1,s.registers.sum))
        simp only [cells];omega
      all_goals simp [cells]
  | advance => simpa [step,hp,cells] using Nat.add_le_add_right (right_cells s.tape MarkedBitAddition.Symbol.blank) (tapeCells s.output)
  | rewind =>
      have h:=left_cells s.tape MarkedBitAddition.Symbol.blank
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | branch => simp only [step,hp];split <;> simp [cells]
  | writeOutputLeft => simpa [step,hp,cells] using Nat.add_le_add_left (write_cells s.output MarkedZeroPadding.Symbol.leftMarker) (tapeCells s.tape)
  | enterOutput => simpa [step,hp,cells] using Nat.add_le_add_left (right_cells s.output MarkedZeroPadding.Symbol.blank) (tapeCells s.tape)
  | enterInput => simpa [step,hp,cells] using Nat.add_le_add_right (right_cells s.tape MarkedBitAddition.Symbol.blank) (tapeCells s.output)
  | copyTest => simp only [step,hp];split <;> simp [cells]
  | copyWrite => simpa [step,hp,cells] using Nat.add_le_add_left (write_cells s.output (MarkedZeroPadding.Symbol.data s.registers.sum)) (tapeCells s.tape)
  | copyAdvanceInput => simpa [step,hp,cells] using Nat.add_le_add_right (right_cells s.tape MarkedBitAddition.Symbol.blank) (tapeCells s.output)
  | copyAdvanceOutput => simpa [step,hp,cells] using Nat.add_le_add_left (right_cells s.output MarkedZeroPadding.Symbol.blank) (tapeCells s.tape)
  | writeOutputRight => simpa [step,hp,cells] using Nat.add_le_add_left (write_cells s.output MarkedZeroPadding.Symbol.rightMarker) (tapeCells s.tape)
  | rewindOutput =>
      have h:=left_cells s.output MarkedZeroPadding.Symbol.blank
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | rewindInput =>
      have h:=left_cells s.tape MarkedBitAddition.Symbol.blank
      simp only [step,hp];split <;> simp only [cells] <;> omega
  | clear slot => simp [step,hp,cells]

private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t)
    (ht:t.phase=.halt) (k:Nat) : cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih =>
      cases k with
      | zero => exact (step_cells s).trans (ih ht 0)
      | succ k => exact ih ht k

theorem difference_prefix_storage (rows:List Row) (r:Registers) (k:Nat) :
    cells (run k (initial rows r))≤2*rows.length+4 := by
  have h:=trace_storage (difference_exact rows r) rfl k
  simp only [final,copyFinal,cells,tapeCells,MarkedBitAddition.marked,
    MarkedZeroPadding.marked,MarkedZeroPadding.bits,List.length_nil,List.length_cons,
    List.length_append,List.length_map,chosen_length] at h ⊢
  omega

/-- Output has exactly the unary producer's binary input alphabet and marker
layout. Running that next controller still requires a charged enclosing switch. -/
theorem produces_binary_magnitude (rows:List Row) (r:Registers) :
    (run (totalTime rows r) (initial rows r)).output=
      MarkedZeroPadding.marked (MarkedZeroPadding.bits ((chosenRows rows r).map Prod.snd)) ∧
    (run (totalTime rows r) (initial rows r)).reverse=chosenReverse rows r ∧
    (run (totalTime rows r) (initial rows r)).registers=SequentialBitAddition.clearRegisters := by
  rw [(difference_result rows r).1]
  exact ⟨rfl,rfl,rfl⟩

end MarkedBitDifference

#print axioms MarkedBitDifference.pass_exact
#print axioms MarkedBitDifference.extraction_exact
#print axioms MarkedBitDifference.difference_exact
#print axioms MarkedBitDifference.difference_result
#print axioms MarkedBitDifference.time_bound
#print axioms MarkedBitDifference.chosen_sources
#print axioms MarkedBitDifference.chosen_value
#print axioms MarkedBitDifference.step_cells
#print axioms MarkedBitDifference.difference_prefix_storage
#print axioms MarkedBitDifference.produces_binary_magnitude
#check @MarkedBitDifference.difference_result
#check @MarkedBitDifference.chosen_value

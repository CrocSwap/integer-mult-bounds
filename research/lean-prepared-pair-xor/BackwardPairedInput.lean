import BinaryInputPreparation
import MarkedBitXorScan

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

A paid adapter for the exact right-blank work-copy endpoint of public PR488.
It reuses that package's zero padding and reversal, rather than constructing
another width/preparation routine. Two equal-width work copies are read toward
their left blanks; an actual L/pair/R word is written on a fresh output tape.
The output head returns to L and two Boolean scratch fields are cleared.
The two input work heads remain at their visited left blanks; their complete
final representations are stated and no input-head restoration is claimed.

Every step reads current finite symbols, changes bounded control/Boolean
registers, writes one output symbol, or moves one head one position. Width and
list zip appear only in specifications/proofs. No Nat-to-bits conversion,
physical family allocation, free pairing, or whole selected implementation is
assumed. The existing PR488 endpoint is joined literally below; transferring
its four-tape controller into this three-tape adapter still requires a charged
phase handoff/framing in an enclosing machine.
Author-checked context kappa=836330098538459/500000000000000000.
Uncompiled source candidate; acceptance is recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.BackwardPairedInput
open FixedTapeMachine (bitSymbol wordValue)
open PairedBitXorScan (Tape Pair)

abbrev InputTape := FixedTapeMachine.Tape
abbrev OutputTape := Tape MarkedBitXorScan.Symbol

inductive Phase where
  | writeLeft | enterOutput | enterLeft | enterRight
  | readLeft | readRight | writePair | moveOutput | moveLeft | moveRight
  | checkEnd | writeRight | rewind | clearLeft | clearRight | halt
  deriving DecidableEq

structure State where
  leftInput : InputTape
  rightInput : InputTape
  output : OutputTape
  leftBit : Bool
  rightBit : Bool
  phase : Phase
  deriving DecidableEq

def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .writeLeft => { s with output := s.output.writeHead .leftMarker, phase := .enterOutput }
  | .enterOutput => { s with output := s.output.moveRight .blank, phase := .enterLeft }
  | .enterLeft => { s with leftInput := s.leftInput.move .left, phase := .enterRight }
  | .enterRight => { s with rightInput := s.rightInput.move .left, phase := .readLeft }
  | .readLeft => match s.leftInput.head with
    | .blank => { s with leftBit := false, phase := .checkEnd }
    | .zero => { s with leftBit := false, phase := .readRight }
    | .one => { s with leftBit := true, phase := .readRight }
  | .readRight => match s.rightInput.head with
    | .blank => { s with phase := .halt }
    | .zero => { s with rightBit := false, phase := .writePair }
    | .one => { s with rightBit := true, phase := .writePair }
  | .writePair => { s with output := s.output.writeHead (.data s.leftBit s.rightBit), phase := .moveOutput }
  | .moveOutput => { s with output := s.output.moveRight .blank, phase := .moveLeft }
  | .moveLeft => { s with leftInput := s.leftInput.move .left, phase := .moveRight }
  | .moveRight => { s with rightInput := s.rightInput.move .left, phase := .readLeft }
  | .checkEnd => match s.rightInput.head with
    | .blank => { s with rightBit := false, phase := .writeRight }
    | _ => { s with phase := .halt }
  | .writeRight => { s with output := s.output.writeHead .rightMarker, phase := .rewind }
  | .rewind =>
      if s.output.readHead .blank = .leftMarker then { s with phase := .clearLeft }
      else { s with output := s.output.moveLeft .blank }
  | .clearLeft => { s with leftBit := false, phase := .clearRight }
  | .clearRight => { s with rightBit := false, phase := .halt }

def run : Nat → State → State
  | 0, s => s
  | k+1, s => run k (step s)

/-- Literal PR488 endTape entrance, with an initially empty output. -/
def initial (xs ys : List Bool) (a b : Bool) : State :=
  ⟨BinaryWordReversal.endTape (xs.map bitSymbol),
    BinaryWordReversal.endTape (ys.map bitSymbol), ⟨[],[]⟩, a, b, .writeLeft⟩

def finalInput (xs : List Bool) : InputTape :=
  ⟨[], .blank, xs.reverse.map bitSymbol ++ [.blank]⟩

def final (xs ys : List Bool) : State :=
  ⟨finalInput xs, finalInput ys, ⟨[], MarkedBitXorScan.marked (xs.zip ys)⟩, false, false, .halt⟩

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {n : Nat} {s t : State} (live : s.phase ≠ .halt)
      (tail : Trace n (step s) t) : Trace (n+1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)

private theorem trace_sound {n : Nat} {s t : State} (h : Trace n s t) : run n s = t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem trace_live {n : Nat} {s t : State} (h : Trace n s t)
    (k : Nat) (hk : k<n) : (run k s).phase ≠ .halt := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih =>
      cases k with
      | zero => exact live
      | succ k => exact ih k (by omega)

private theorem halt_run (s : State) (hs : s.phase = .halt) (k : Nat) : run k s = s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run,step,hs] using ih

def symbols (ps : List Pair) : List MarkedBitXorScan.Symbol :=
  ps.map MarkedBitXorScan.dataSymbol

def scanning (xs ys : List Bool) (rx ry : List FixedTapeMachine.Symbol)
    (ps : List Pair) (a b : Bool) : State :=
  ⟨BinaryWordReversal.fromLeft (xs.map bitSymbol) rx,
    BinaryWordReversal.fromLeft (ys.map bitSymbol) ry,
    ⟨symbols ps ++ [.leftMarker], []⟩, a,b,.readLeft⟩

private theorem scan_pair (x y a b : Bool) (xs ys : List Bool)
    (rx ry : List FixedTapeMachine.Symbol) (ps : List Pair) :
    Trace 6 (scanning (x::xs) (y::ys) rx ry ps a b)
      (scanning xs ys (bitSymbol x::rx) (bitSymbol y::ry) ((x,y)::ps) x y) := by
  cases x <;> cases y <;> cases xs <;> cases ys
  all_goals
    iterate 6 apply Trace.next (by simp [scanning,step,bitSymbol,BinaryWordReversal.fromLeft,
      FixedTapeMachine.Tape.move,Tape.writeHead,Tape.moveRight,symbols,MarkedBitXorScan.dataSymbol])
    simp [scanning,step,bitSymbol,BinaryWordReversal.fromLeft,
      FixedTapeMachine.Tape.move,Tape.writeHead,Tape.moveRight,symbols,MarkedBitXorScan.dataSymbol]
    exact Trace.nil _

private theorem scan_empty (rx ry : List FixedTapeMachine.Symbol) (ps : List Pair) (a b : Bool) :
    Trace 2 (scanning [] [] rx ry ps a b)
      { scanning [] [] rx ry ps false false with phase := .writeRight } := by
  apply Trace.next (by simp [scanning])
  apply Trace.next (by simp [scanning,step,BinaryWordReversal.fromLeft])
  simpa [scanning,step,BinaryWordReversal.fromLeft] using
    Trace.nil { scanning [] [] rx ry ps false false with phase := .writeRight }

private theorem scan_words (xs ys : List Bool) (h : xs.length=ys.length)
    (rx ry : List FixedTapeMachine.Symbol) (ps : List Pair) (a b : Bool) :
    Trace (6*xs.length+2) (scanning xs ys rx ry ps a b)
      { scanning [] [] (xs.reverse.map bitSymbol ++ rx) (ys.reverse.map bitSymbol ++ ry)
          ((xs.zip ys).reverse ++ ps) false false with phase := .writeRight } := by
  induction xs generalizing ys rx ry ps a b with
  | nil =>
      have hy : ys=[] := List.length_eq_zero_iff.mp h.symm
      subst ys
      simpa using scan_empty rx ry ps a b
  | cons x xs ih =>
      cases ys with
      | nil => simp at h
      | cons y ys =>
          have ht : xs.length=ys.length := Nat.succ.inj h
          have g := trace_trans (scan_pair x y a b xs ys rx ry ps)
            (ih ys ht (bitSymbol x::rx) (bitSymbol y::ry) ((x,y)::ps) x y)
          have hc : 6+(6*xs.length+2)=6*(x::xs).length+2 := by simp; omega
          rw [hc] at g
          simpa [List.reverse_cons,List.map_append,List.append_assoc] using g

private theorem setup (xs ys : List Bool) (a b : Bool) :
    Trace 4 (initial xs ys a b) (scanning xs ys [.blank] [.blank] [] a b) := by
  cases xs <;> cases ys
  all_goals
    iterate 4 apply Trace.next (by simp [initial,step,BinaryWordReversal.endTape,
      FixedTapeMachine.Tape.move,Tape.writeHead,Tape.moveRight])
    simp [initial,scanning,step,BinaryWordReversal.endTape,BinaryWordReversal.fromLeft,
      FixedTapeMachine.Tape.move,Tape.writeHead,Tape.moveRight,symbols]
    exact Trace.nil _

private theorem rewind (base : State) (ls rs : List MarkedBitXorScan.Symbol)
    (hls : ∀ a ∈ ls, a ≠ .leftMarker)
    (hrs : (⟨[],rs⟩ : OutputTape).readHead .blank ≠ .leftMarker) :
    Trace (ls.length+2) {base with output:=⟨ls++[.leftMarker],rs⟩,phase:=.rewind}
      {base with output:=⟨[],.leftMarker::(ls.reverse++rs)⟩,phase:=.clearLeft} := by
  revert hls hrs
  induction ls generalizing rs with
  | nil =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp)
      simp [step,Tape.moveLeft,Tape.readHead]
      exact Trace.nil _
  | cons a ls ih =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      have g := ih (a::rs) (by intro b hb; exact hls b (by simp [hb]))
        (by simpa [Tape.readHead] using hls a (by simp))
      simpa [Tape.moveLeft,List.reverse_cons,List.append_assoc] using g

private theorem finish (xs ys : List Bool) :
    Trace ((xs.zip ys).length+5)
      {scanning [] [] (xs.reverse.map bitSymbol++[.blank]) (ys.reverse.map bitSymbol++[.blank])
        (xs.zip ys).reverse false false with phase:=.writeRight}
      (final xs ys) := by
  let ps := xs.zip ys
  let before := {scanning [] [] (xs.reverse.map bitSymbol++[.blank]) (ys.reverse.map bitSymbol++[.blank])
    ps.reverse false false with phase:=.writeRight}
  let written : State := {before with output:=⟨symbols ps.reverse++[.leftMarker],[.rightMarker]⟩,phase:=.rewind}
  have hw : Trace 1 before written := by
    apply Trace.next (by simp [before])
    simpa [before,written,step,scanning,Tape.writeHead] using Trace.nil written
  have hr := rewind written (symbols ps.reverse) [.rightMarker]
    (by intro z hz; obtain ⟨p,_,rfl⟩ := List.mem_map.mp hz; cases p; simp [MarkedBitXorScan.dataSymbol])
    (by simp [Tape.readHead])
  let returned : State := {written with output:=⟨[], MarkedBitXorScan.marked ps⟩,phase:=.clearLeft}
  have hr' : Trace (ps.length+2) written returned := by
    simpa [written,returned,symbols,MarkedBitXorScan.marked,List.map_reverse] using hr
  have hc : Trace 2 returned (final xs ys) := by
    apply Trace.next (by simp [returned])
    apply Trace.next (by simp [returned,step])
    simpa [returned,written,before,step,scanning,BinaryWordReversal.fromLeft,
      final,finalInput,ps] using Trace.nil (final xs ys)
  have g := trace_trans (trace_trans hw hr') hc
  have hn : 1+(ps.length+2)+2=ps.length+5 := by omega
  rw [hn] at g
  exact g

/-- Exact paid transition trace from the existing prepared work-copy layout. -/
theorem pair_exact (xs ys : List Bool) (h : xs.length=ys.length) (a b : Bool) :
    Trace (7*xs.length+11) (initial xs ys a b) (final xs ys) := by
  have hs := scan_words xs ys h [.blank] [.blank] [] a b
  have hs' : Trace (6*xs.length+2) (scanning xs ys [.blank] [.blank] [] a b)
      {scanning [] [] (xs.reverse.map bitSymbol++[.blank]) (ys.reverse.map bitSymbol++[.blank])
        (xs.zip ys).reverse false false with phase:=.writeRight} := by simpa using hs
  have g := trace_trans (trace_trans (setup xs ys a b) hs') (finish xs ys)
  have hc : 4+(6*xs.length+2)+((xs.zip ys).length+5)=7*xs.length+11 := by
    rw [List.length_zip,h];simp [Nat.min_self];omega
  rw [hc] at g
  exact g

theorem pair_result (xs ys : List Bool) (h : xs.length=ys.length) (a b : Bool) :
    run (7*xs.length+11) (initial xs ys a b)=final xs ys := trace_sound (pair_exact xs ys h a b)

theorem pair_first_halt (xs ys : List Bool) (h : xs.length=ys.length) (a b : Bool) :
    (run (7*xs.length+11) (initial xs ys a b)).phase=.halt ∧
    ∀ k<7*xs.length+11, (run k (initial xs ys a b)).phase≠.halt := by
  constructor
  · rw [pair_result xs ys h];rfl
  · exact trace_live (pair_exact xs ys h a b)

def inputCells (t : InputTape) : Nat := t.left.length+1+t.right.length

def outputCells (t : OutputTape) : Nat := t.left.length+t.right.length

def cells (s : State) : Nat := inputCells s.leftInput+inputCells s.rightInput+outputCells s.output

private theorem input_move_cells (t : InputTape) : inputCells t ≤ inputCells (t.move .left) := by
  rcases t with ⟨ls,a,rs⟩
  cases ls <;> simp [inputCells,FixedTapeMachine.Tape.move] <;> omega

private theorem write_cells (t : OutputTape) (a : MarkedBitXorScan.Symbol) :
    outputCells t ≤ outputCells (t.writeHead a) := by
  rcases t with ⟨ls,rs⟩
  cases rs <;> simp [outputCells,Tape.writeHead]

private theorem move_cells (t : OutputTape) :
    outputCells t ≤ outputCells (t.moveLeft .blank) ∧ outputCells t ≤ outputCells (t.moveRight .blank) := by
  rcases t with ⟨ls,rs⟩
  cases ls <;> cases rs <;> simp [outputCells,Tape.moveLeft,Tape.moveRight] <;> omega

private theorem step_cells (s : State) : cells s ≤ cells (step s) := by
  have hl:=input_move_cells s.leftInput
  have hr:=input_move_cells s.rightInput
  have ho:=move_cells s.output
  have hwL:=write_cells s.output .leftMarker
  have hwR:=write_cells s.output .rightMarker
  have hwD:=write_cells s.output (.data s.leftBit s.rightBit)
  cases hp:s.phase <;> simp only [step,hp]
  all_goals (repeat' split) <;> simp only [cells] at * <;> omega

private theorem trace_storage {n : Nat} {s t : State} (h : Trace n s t)
    (ht:t.phase=.halt) (k:Nat) : cells (run k s) ≤ cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]; exact Nat.le_refl _
  | @next n s t live tail ih =>
      cases k with
      | zero => exact Nat.le_trans (step_cells s) (ih ht 0)
      | succ k => exact ih ht k

/-- Includes both newly visited input blanks and the actual paired output. -/
theorem pair_prefix_storage (xs ys : List Bool) (h:xs.length=ys.length) (a b:Bool) (k:Nat) :
    cells (run k (initial xs ys a b)) ≤ 3*xs.length+6 := by
  have g:=trace_storage (pair_exact xs ys h a b) (by rfl) k
  simpa [cells,inputCells,outputCells,final,finalInput,MarkedBitXorScan.marked,
    List.length_zip,h,Nat.min_self,Nat.mul_succ,Nat.succ_mul,Nat.add_assoc,
    Nat.add_comm,Nat.add_left_comm] using g

/-- A projection of the exact output and cleared scratch, not a free phase switch. -/
def xorEntrance (s : State) : MarkedBitXorScan.State := ⟨s.output,s.leftBit,.enter⟩

theorem pair_xor_entrance (xs ys : List Bool) (h:xs.length=ys.length) (a b:Bool) :
    xorEntrance (run (7*xs.length+11) (initial xs ys a b))=MarkedBitXorScan.initial (xs.zip ys) := by
  rw [pair_result xs ys h]
  rfl

/-- Literal source-to-adapter boundary. Only work tapes 2/3 are selected;
framing the other two PR488 tapes remains an enclosing-controller obligation. -/
def fromPrepared (c : FixedTapeMachine.Configuration BinaryInputPreparation.machine) (a b:Bool) : State :=
  ⟨c.tapes (2 : Fin 4),c.tapes (3 : Fin 4),⟨[],[]⟩,a,b,.writeLeft⟩

theorem prepared_entrance (xs ys:List Bool) (a b:Bool) :
    fromPrepared (BinaryInputPreparation.finalConfiguration xs ys) a b =
      initial (BinaryInputPreparation.pad (max xs.length ys.length) xs)
        (BinaryInputPreparation.pad (max xs.length ys.length) ys) a b := rfl

private theorem word_value (xs:List Bool) : wordValue xs=PairedBitXorScan.value xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      cases x <;> simp_all [wordValue,FixedTapeMachine.wordValue,IntegerConvolution.binaryValue,
        IntegerConvolution.value,PairedBitXorScan.value] <;> omega

/-- Existing PR488 paid width/reversal provides these literal inputs. Numeric
values are preserved; the starting words are supplied bits, not converted Nats. -/
theorem prepared_pair (xs ys:List Bool) (a b:Bool) :
    ∃ t, t≤6*(max xs.length ys.length)+7 ∧
      let c:=FixedTapeMachine.run BinaryInputPreparation.machine t
        (BinaryInputPreparation.initialConfiguration xs ys)
      let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
      let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
      fromPrepared c a b=initial px py a b ∧
      run (7*(max xs.length ys.length)+11) (fromPrepared c a b)=final px py ∧
      PairedBitXorScan.value ((px.zip py).map Prod.fst)=wordValue xs ∧
      PairedBitXorScan.value ((px.zip py).map Prod.snd)=wordValue ys := by
  obtain ⟨t,ht,hc⟩:=BinaryInputPreparation.prepare_run xs ys
  refine ⟨t,ht,?_⟩
  dsimp only
  rw [hc,prepared_entrance]
  have hx:=BinaryInputPreparation.pad_length (max xs.length ys.length) xs (Nat.le_max_left _ _)
  have hy:=BinaryInputPreparation.pad_length (max xs.length ys.length) ys (Nat.le_max_right _ _)
  have hxy:=hx.trans hy.symm
  refine ⟨rfl,?_,?_,?_⟩
  · simpa only [hx] using pair_result _ _ hxy a b
  · rw [List.map_fst_zip (by omega),←word_value,BinaryInputPreparation.pad_value]
  · rw [List.map_snd_zip (by omega),←word_value,BinaryInputPreparation.pad_value]

end CurrentMain.BackwardPairedInput

#print axioms CurrentMain.BackwardPairedInput.pair_exact
#print axioms CurrentMain.BackwardPairedInput.pair_result
#print axioms CurrentMain.BackwardPairedInput.pair_first_halt
#print axioms CurrentMain.BackwardPairedInput.pair_prefix_storage
#print axioms CurrentMain.BackwardPairedInput.pair_xor_entrance
#print axioms CurrentMain.BackwardPairedInput.prepared_entrance
#print axioms CurrentMain.BackwardPairedInput.prepared_pair
#check @CurrentMain.BackwardPairedInput.pair_exact
#check @CurrentMain.BackwardPairedInput.prepared_pair

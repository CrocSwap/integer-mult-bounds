import MarkedBitXorScan

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Paid equal-width write-back into an existing marked paired block. The source
is another marked paired word. One current source target bit is read into a
Boolean register; one actual destination target cell is overwritten while its
other bit is retained. The source tape is never written. Both heads return to
L and scratch clears. Width equality and both existing marked allocations are
caller inputs, not a free resizing or memory-address operation.

This controller is distinct from fresh-output extraction and packed-slot seek:
it neither chooses a slot nor constructs a blank output. Overwritten destination
target bits and arbitrary incoming scratch are not restored. It can be joined
later to the already derived prepared-metadata result; this file proves the
actual local copy/update rather than assuming its endpoint.
Author-checked context kappa=836330098538459/500000000000000000.
Fresh compiler acceptance is recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.MarkedTrackWriteback
open PairedBitXorScan (Tape Pair value)
open MarkedBitXorScan (Symbol dataSymbol marked)

inductive Phase where
  | enterSource | enterDestination | load | write | clear | advanceSource
  | advanceDestination | checkEnd | rewindSource | rewindDestination | clearScratch | halt
  deriving DecidableEq

structure State where
  source : Tape Symbol
  destination : Tape Symbol
  scratch : Bool
  phase : Phase
  deriving DecidableEq

/-- Only finite symbols and one Boolean register are inspected. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .enterSource => match s.source.readHead .blank with
    | .leftMarker => {s with source := s.source.moveRight .blank, phase := .enterDestination}
    | _ => {s with phase := .halt}
  | .enterDestination => match s.destination.readHead .blank with
    | .leftMarker => {s with destination := s.destination.moveRight .blank, phase := .load}
    | _ => {s with phase := .halt}
  | .load => match s.source.readHead .blank with
    | .data x _ => {s with scratch := x, phase := .write}
    | .rightMarker => {s with phase := .checkEnd}
    | _ => {s with phase := .halt}
  | .write => match s.destination.readHead .blank with
    | .data _ b => {s with destination := s.destination.writeHead (.data s.scratch b), phase := .clear}
    | _ => {s with phase := .halt}
  | .clear => match s.source.readHead .blank with
    | .data x _ => {s with scratch := s.scratch ^^ x, phase := .advanceSource}
    | _ => {s with phase := .halt}
  | .advanceSource => {s with source := s.source.moveRight .blank, phase := .advanceDestination}
  | .advanceDestination => {s with destination := s.destination.moveRight .blank, phase := .load}
  | .checkEnd => match s.destination.readHead .blank with
    | .rightMarker => {s with phase := .rewindSource}
    | _ => {s with phase := .halt}
  | .rewindSource =>
      if s.source.readHead .blank = .leftMarker then {s with phase := .rewindDestination}
      else {s with source := s.source.moveLeft .blank}
  | .rewindDestination =>
      if s.destination.readHead .blank = .leftMarker then {s with phase := .clearScratch}
      else {s with destination := s.destination.moveLeft .blank}
  | .clearScratch => {s with scratch := false, phase := .halt}

def run : Nat → State → State
  | 0,s => s
  | k+1,s => run k (step s)

/-- The desired data word is a specification, never a bulk step operation. -/
def updated : List Pair → List Pair → List Pair
  | x::xs,y::ys => (x.1,y.2)::updated xs ys
  | _,_ => []

def initial (src dst : List Pair) (b : Bool) : State :=
  ⟨⟨[],marked src⟩,⟨[],marked dst⟩,b,.enterSource⟩

def final (src dst : List Pair) : State :=
  ⟨⟨[],marked src⟩,⟨[],marked (updated src dst)⟩,false,.halt⟩

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : s.phase ≠ .halt)
      (tail : Trace k (step s) t) : Trace (k+1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)
private theorem trace_sound {n : Nat} {s t : State} (h : Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih
private theorem trace_live {n : Nat} {s t : State} (h : Trace n s t)
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

private theorem updated_length (src dst : List Pair) (h:src.length=dst.length) :
    (updated src dst).length=src.length := by
  induction src generalizing dst with
  | nil => simp [updated]
  | cons x xs ih =>
      cases dst with
      | nil => simp at h
      | cons y ys => simp [updated,ih ys (Nat.succ.inj h)]

/-- The source target bits are copied exactly; destination source bits remain
literal old bits, with no numeric decoding/canonical-width premise. -/
theorem updated_tracks (src dst : List Pair) (h:src.length=dst.length) :
    (updated src dst).map Prod.fst=src.map Prod.fst ∧
      (updated src dst).map Prod.snd=dst.map Prod.snd := by
  induction src generalizing dst with
  | nil =>
      have hd:dst=[]:=List.length_eq_zero_iff.mp h.symm
      subst dst
      exact ⟨rfl,rfl⟩
  | cons x xs ih =>
      cases dst with
      | nil => simp at h
      | cons y ys =>
          obtain ⟨ha,hb⟩:=ih ys (Nat.succ.inj h)
          exact ⟨congrArg (x.1 :: ·) ha,congrArg (y.2 :: ·) hb⟩

def scanning (src dst : List Pair) (ls ld : List Symbol) (b : Bool) : State :=
  ⟨⟨ls,src.map dataSymbol++[.rightMarker]⟩,
    ⟨ld,dst.map dataSymbol++[.rightMarker]⟩,b,.load⟩

private theorem column_five (x y : Pair) (src dst : List Pair)
    (ls ld : List Symbol) (b : Bool) :
    Trace 5 (scanning (x::src) (y::dst) ls ld b)
      (scanning src dst (dataSymbol x::ls) (dataSymbol (x.1,y.2)::ld) false) := by
  rcases x with ⟨x,u⟩
  rcases y with ⟨y,v⟩
  cases x <;> cases u <;> cases y <;> cases v
  all_goals
    iterate 5 apply Trace.next (by simp [scanning,step,dataSymbol,Tape.readHead,
      Tape.writeHead,Tape.moveRight])
    simp [scanning,step,dataSymbol,Tape.readHead,Tape.writeHead,Tape.moveRight]
    exact Trace.nil _

private theorem scan_words (src dst : List Pair) (h:src.length=dst.length)
    (ls ld : List Symbol) (b : Bool) :
    Trace (5*src.length) (scanning src dst ls ld b)
      (scanning [] [] ((src.map dataSymbol).reverse++ls)
        (((updated src dst).map dataSymbol).reverse++ld) (if src=[] then b else false)) := by
  induction src generalizing dst ls ld b with
  | nil =>
      have hd:dst=[]:=List.length_eq_zero_iff.mp h.symm
      subst dst
      simpa [updated,scanning] using Trace.nil (scanning [] [] ls ld b)
  | cons x xs ih =>
      cases dst with
      | nil => simp at h
      | cons y ys =>
          have hc:=column_five x y xs ys ls ld b
          have ht:=ih ys (Nat.succ.inj h) (dataSymbol x::ls) (dataSymbol (x.1,y.2)::ld) false
          have hall:=trace_trans hc ht
          have count:5+5*xs.length=5*(x::xs).length:=by simp;omega
          rw [count] at hall
          simpa [updated,List.reverse_cons,List.append_assoc] using hall

/-- Shared proof for the two actual rewind phases; which head is selected is
finite control, not a computed address or a hidden multi-cell movement. -/
private theorem rewind_source (base : State) (ls rs : List Symbol)
    (hls:∀ a∈ls,a≠.leftMarker)
    (hrs:(⟨[],rs⟩:Tape Symbol).readHead .blank≠.leftMarker) :
    Trace (ls.length+2) {base with source:=⟨ls++[.leftMarker],rs⟩,phase:=.rewindSource}
      {base with source:=⟨[],.leftMarker::(ls.reverse++rs)⟩,phase:=.rewindDestination} := by
  induction ls generalizing rs with
  | nil =>
      change Trace 2 {base with source:=⟨[.leftMarker],rs⟩,phase:=.rewindSource}
        {base with source:=⟨[],.leftMarker::rs⟩,phase:=.rewindDestination}
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp [Tape.moveLeft])
      simp only [step,Tape.moveLeft,Tape.readHead,if_true]
      exact Trace.nil _
  | cons a ls ih =>
      have ht:=ih (a::rs) (by intro c hc;exact hls c (by simp [hc]))
        (by simpa [Tape.readHead] using hls a (by simp))
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      simpa [Tape.moveLeft,List.reverse_cons,List.append_assoc] using ht

private theorem rewind_destination (base : State) (ls rs : List Symbol)
    (hls:∀ a∈ls,a≠.leftMarker)
    (hrs:(⟨[],rs⟩:Tape Symbol).readHead .blank≠.leftMarker) :
    Trace (ls.length+2) {base with destination:=⟨ls++[.leftMarker],rs⟩,phase:=.rewindDestination}
      {base with destination:=⟨[],.leftMarker::(ls.reverse++rs)⟩,phase:=.clearScratch} := by
  induction ls generalizing rs with
  | nil =>
      change Trace 2 {base with destination:=⟨[.leftMarker],rs⟩,phase:=.rewindDestination}
        {base with destination:=⟨[],.leftMarker::rs⟩,phase:=.clearScratch}
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp [Tape.moveLeft])
      simp only [step,Tape.moveLeft,Tape.readHead,if_true]
      exact Trace.nil _
  | cons a ls ih =>
      have ht:=ih (a::rs) (by intro c hc;exact hls c (by simp [hc]))
        (by simpa [Tape.readHead] using hls a (by simp))
      apply Trace.next (by simp)
      simp only [step,Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      simpa [Tape.moveLeft,List.reverse_cons,List.append_assoc] using ht

private theorem finish (src dst : List Pair) (h:src.length=dst.length) (b:Bool) :
    Trace (2*src.length+7)
      (scanning [] [] ((src.map dataSymbol).reverse++[.leftMarker])
        (((updated src dst).map dataSymbol).reverse++[.leftMarker]) b)
      (final src dst) := by
  let start:=scanning [] [] ((src.map dataSymbol).reverse++[.leftMarker])
    (((updated src dst).map dataSymbol).reverse++[.leftMarker]) b
  let returning:State:={start with phase:=.rewindSource}
  have he:Trace 2 start returning := by
    iterate 2 apply Trace.next (by simp [start,returning,scanning,step,Tape.readHead])
    simp [start,returning,scanning,step,Tape.readHead]
    exact Trace.nil _
  have hrs:=rewind_source returning (src.map dataSymbol).reverse [.rightMarker]
    (by intro a ha; have hmem:=List.mem_reverse.mp ha; obtain ⟨p,_,rfl⟩:=List.mem_map.mp hmem;cases p;simp [dataSymbol])
    (by simp [Tape.readHead])
  let middle:State:={returning with source:=⟨[],marked src⟩,phase:=.rewindDestination}
  have hrs':Trace (src.length+2) returning middle := by
    simpa [returning,start,scanning,middle,marked,List.length_reverse,List.length_map,
      List.reverse_reverse] using hrs
  have hrd:=rewind_destination middle ((updated src dst).map dataSymbol).reverse [.rightMarker]
    (by intro a ha;have hmem:=List.mem_reverse.mp ha;obtain ⟨p,_,rfl⟩:=List.mem_map.mp hmem;cases p;simp [dataSymbol])
    (by simp [Tape.readHead])
  let clearing:State:={middle with destination:=⟨[],marked (updated src dst)⟩,phase:=.clearScratch}
  have hrd':Trace (src.length+2) middle clearing := by
    simpa [clearing,middle,returning,start,scanning,marked,List.length_reverse,List.length_map,
      List.reverse_reverse,updated_length src dst h] using hrd
  have hc:Trace 1 clearing (final src dst) := by
    apply Trace.next (by simp [clearing])
    simp [step,clearing,middle,returning,start,scanning,final]
    exact Trace.nil _
  have hall:=trace_trans (trace_trans (trace_trans he hrs') hrd') hc
  have count:2+(src.length+2)+(src.length+2)+1=2*src.length+7:=by omega
  rw [count] at hall
  exact hall

/-- Exact first-halt trace includes both marker entries, all writes and both
head returns. Empty equal-width blocks take nine actual transitions. -/
theorem writeback_exact (src dst : List Pair) (h:src.length=dst.length) (b:Bool) :
    Trace (7*src.length+9) (initial src dst b) (final src dst) := by
  have setup:Trace 2 (initial src dst b) (scanning src dst [.leftMarker] [.leftMarker] b) := by
    iterate 2 apply Trace.next (by simp [initial,step,marked,Tape.readHead,Tape.moveRight])
    simp [initial,step,marked,Tape.readHead,Tape.moveRight,scanning]
    exact Trace.nil _
  have hs:=scan_words src dst h [.leftMarker] [.leftMarker] b
  have hf:=finish src dst h (if src=[] then b else false)
  have hall:=trace_trans (trace_trans setup hs) hf
  have count:2+5*src.length+(2*src.length+7)=7*src.length+9:=by omega
  rw [count] at hall
  exact hall

theorem writeback_result (src dst : List Pair) (h:src.length=dst.length) (b:Bool) :
    run (7*src.length+9) (initial src dst b)=final src dst ∧
      (final src dst).phase=.halt ∧
      ∀ k<7*src.length+9,(run k (initial src dst b)).phase≠.halt :=
  ⟨trace_sound (writeback_exact src dst h b),rfl,trace_live (writeback_exact src dst h b)⟩

def tapeCells (t:Tape Symbol) : Nat:=t.left.length+t.right.length
def cells (s:State) : Nat:=tapeCells s.source+tapeCells s.destination

private theorem write_cells (t:Tape Symbol) (a:Symbol) : tapeCells t≤tapeCells (t.writeHead a) := by
  rcases t with ⟨ls,rs⟩;cases rs <;> simp [tapeCells,Tape.writeHead]
private theorem move_cells (t:Tape Symbol) :
    tapeCells t≤tapeCells (t.moveRight .blank) ∧ tapeCells t≤tapeCells (t.moveLeft .blank) := by
  rcases t with ⟨ls,rs⟩;cases ls <;> cases rs <;> simp [tapeCells,Tape.moveRight,Tape.moveLeft] <;> omega

private theorem step_cells (s:State) : cells s≤cells (step s) := by
  have hs:=move_cells s.source
  have hd:=move_cells s.destination
  cases hp:s.phase <;> simp only [step,hp]
  all_goals repeat first | split
  all_goals simp only [cells] at *
  all_goals first | exact Nat.add_le_add_left (write_cells s.destination _) _ | omega

private theorem trace_storage {n:Nat} {s t:State} (h:Trace n s t)
    (ht:t.phase=.halt) (k:Nat) : cells (run k s)≤cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]; exact Nat.le_refl _
  | @next n s t live tail ih =>
      cases k with
      | zero => exact Nat.le_trans (step_cells s) (ih ht 0)
      | succ k => exact ih ht k

/-- Both existing blocks and all four markers are counted. No extra output
capacity is supplied for free, and no unrepresented width change occurs. -/
theorem writeback_storage (src dst:List Pair) (h:src.length=dst.length) (b:Bool) (k:Nat) :
    cells (run k (initial src dst b))≤2*src.length+4 := by
  have g:=trace_storage (writeback_exact src dst h b) rfl k
  simp [cells,tapeCells,final,marked,updated_length src dst h] at g ⊢
  omega

/-- Full source tape/head and destination other-track preservation at the
actual endpoint, with arbitrary incoming scratch explicitly cleared. -/
theorem writeback_tracks (src dst:List Pair) (h:src.length=dst.length) (b:Bool) :
    (run (7*src.length+9) (initial src dst b)).source=⟨[],marked src⟩ ∧
      (run (7*src.length+9) (initial src dst b)).destination=⟨[],marked (updated src dst)⟩ ∧
      (updated src dst).map Prod.fst=src.map Prod.fst ∧
      (updated src dst).map Prod.snd=dst.map Prod.snd ∧
      (run (7*src.length+9) (initial src dst b)).scratch=false := by
  rw [(writeback_result src dst h b).1]
  exact ⟨rfl,rfl,(updated_tracks src dst h).1,(updated_tracks src dst h).2,rfl⟩

end CurrentMain.MarkedTrackWriteback

#print axioms CurrentMain.MarkedTrackWriteback.updated_tracks
#print axioms CurrentMain.MarkedTrackWriteback.writeback_exact
#print axioms CurrentMain.MarkedTrackWriteback.writeback_result
#print axioms CurrentMain.MarkedTrackWriteback.writeback_storage
#print axioms CurrentMain.MarkedTrackWriteback.writeback_tracks
#check @CurrentMain.MarkedTrackWriteback.writeback_result
#check @CurrentMain.MarkedTrackWriteback.writeback_tracks

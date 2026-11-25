import PreparedPairXorSpace
import MarkedTrackWriteback

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Six-tape controller: the accepted PR488 preparation/pairing/XOR pipeline,
then one charged control handoff to the accepted existing-slot write-back.
The four original/work tapes remain explicit spectators during write-back.
The actual computed paired word becomes the source tape without copying or
reformatting it. The destination is an existing independently allocated marked
block of the computed width; only its target track is overwritten.

The explicit equal-capacity premise is not a width-selection, resize, address
lookup, ambient allocation or Nat-to-bits conversion. Old destination target
bits and dirty scratch are not restored. Constants count the inherited finite
symbol transitions and represented cells; they are not a whole selected
multiplier theorem or a free coordinate-to-bit encoding claim.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.PreparedXorWriteback
open PairedBitXorScan (Tape Pair xorPair value)
abbrev InputTape := PreparedPairXor.InputTape
abbrev OutputTape := PreparedPairXor.OutputTape

inductive State where
  | preparing (p : PreparedPairXor.State) (destination : OutputTape) (scratch : Bool)
  | writing (left right workLeft workRight : InputTape) (spare : Bool) (w : MarkedTrackWriteback.State)

/-- The single extra transition merely changes finite control and retains
all six tape fields. It executes no copying or arithmetic. -/
def step : State → State
  | .preparing (.xor left right wl wr spare s) destination b =>
      if s.phase = .halt then
        .writing left right wl wr spare ⟨s.tape,destination,b,.enterSource⟩
      else .preparing (PreparedPairXor.step (.xor left right wl wr spare s)) destination b
  | .preparing p destination b => .preparing (PreparedPairXor.step p) destination b
  | .writing left right wl wr spare w => .writing left right wl wr spare (MarkedTrackWriteback.step w)

def Halted : State → Prop
  | .preparing .. => False
  | .writing _ _ _ _ _ w => w.phase = .halt

def run : Nat → State → State
  | 0,s => s
  | n+1,s => run n (step s)
inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {n : Nat} {s t : State} (live : ¬ Halted s)
      (tail : Trace n (step s) t) : Trace (n+1) s t

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
    (k : Nat) (hk:k<n) : ¬ Halted (run k s) := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih => cases k with
    | zero => exact live
    | succ k => exact ih k (by omega)
private theorem run_add (m n : Nat) (s : State) : run (m+n) s=run n (run m s) := by
  induction m generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ m ih => simpa only [Nat.succ_add,run] using ih (step s)

private theorem preparing_step (p:PreparedPairXor.State) (d:OutputTape) (b:Bool) (h:¬PreparedPairXor.Halted p) :
    step (.preparing p d b)=.preparing (PreparedPairXor.step p) d b := by
  cases p with
  | prepare => rfl
  | pairing => rfl
  | xor left right wl wr spare s =>
      change s.phase≠.halt at h
      simp only [step,if_neg h]

private theorem preparing_trace {n:Nat} {p q:PreparedPairXor.State} (h:PreparedPairXor.Trace n p q)
    (d:OutputTape) (b:Bool) : Trace n (.preparing p d b) (.preparing q d b) := by
  induction h with
  | nil => exact Trace.nil _
  | @next n p q live tail ih =>
      apply Trace.next (by simp [Halted])
      rw [preparing_step p d b live]
      exact ih

private theorem preparing_prefix {n:Nat} {p q:PreparedPairXor.State} (h:PreparedPairXor.Trace n p q)
    (d:OutputTape) (b:Bool) (k:Nat) (hk:k≤n) :
    run k (.preparing p d b)=.preparing (PreparedPairXor.run k p) d b := by
  induction h generalizing k with
  | nil =>
      have hz:k=0:=by omega
      subst k
      rfl
  | @next n p q live tail ih =>
      cases k with
      | zero => rfl
      | succ k =>
          change run k (step (.preparing p d b))=.preparing (PreparedPairXor.run k (PreparedPairXor.step p)) d b
          rw [preparing_step p d b live]
          exact ih k (by omega)

private theorem writing_trace (l r wl wr:InputTape) (spare:Bool)
    {n:Nat} {s t:MarkedTrackWriteback.State} (h:MarkedTrackWriteback.Trace n s t) :
    Trace n (.writing l r wl wr spare s) (.writing l r wl wr spare t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

/-- Complete four-tape spectator equality at every write-back prefix. -/
theorem writing_run (l r wl wr:InputTape) (spare:Bool) (s:MarkedTrackWriteback.State) (k:Nat) :
    run k (.writing l r wl wr spare s)=.writing l r wl wr spare (MarkedTrackWriteback.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedTrackWriteback.step s)

def rows (xs ys:List Bool) : List Pair := (PreparedPairXor.pairedRows xs ys).map xorPair

theorem rows_length (xs ys:List Bool) : (rows xs ys).length=max xs.length ys.length := by
  simp only [rows,PreparedPairXor.pairedRows,List.length_map,List.length_zip]
  rw [BinaryInputPreparation.pad_length _ _ (Nat.le_max_left _ _),
    BinaryInputPreparation.pad_length _ _ (Nat.le_max_right _ _),Nat.min_self]

def initial (xs ys:List Bool) (dst:List Pair) (a b scratch:Bool) : State :=
  .preparing (PreparedPairXor.initial xs ys a b) ⟨[],MarkedBitXorScan.marked dst⟩ scratch

def writingEntrance (xs ys:List Bool) (dst:List Pair) (scratch:Bool) : State :=
  let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
  let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
  .writing (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false
    (MarkedTrackWriteback.initial (rows xs ys) dst scratch)

def final (xs ys:List Bool) (dst:List Pair) : State :=
  let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
  let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
  .writing (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false
    (MarkedTrackWriteback.final (rows xs ys) dst)

/-- Exact endpoint alignment of the two existing implementations. -/
theorem handoff (xs ys:List Bool) (dst:List Pair) (scratch:Bool) :
    step (.preparing (PreparedPairXor.final xs ys) ⟨[],MarkedBitXorScan.marked dst⟩ scratch)=
      writingEntrance xs ys dst scratch := rfl

private theorem joined_trace (xs ys:List Bool) (dst:List Pair)
    (capacity:dst.length=max xs.length ys.length) (a b scratch:Bool)
    {t:Nat} (hp:PreparedPairXor.Trace t (PreparedPairXor.initial xs ys a b) (PreparedPairXor.final xs ys)) :
    Trace (t+1+(7*(max xs.length ys.length)+9))
      (initial xs ys dst a b scratch) (final xs ys dst) := by
  have prep:=preparing_trace hp ⟨[],MarkedBitXorScan.marked dst⟩ scratch
  have switch:Trace 1
      (.preparing (PreparedPairXor.final xs ys) ⟨[],MarkedBitXorScan.marked dst⟩ scratch)
      (writingEntrance xs ys dst scratch) := by
    apply Trace.next (by simp [Halted])
    rw [handoff]
    exact Trace.nil _
  have hw:=MarkedTrackWriteback.writeback_exact (rows xs ys) dst ((rows_length xs ys).trans capacity.symm) scratch
  let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
  let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
  have write:=writing_trace (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false hw
  rw [rows_length] at write
  exact trace_trans (trace_trans prep switch) write

/-- The actual first halt includes the charged handoff and all writes/returns.
The old preparation's existential duration remains existential. -/
theorem machine_result (xs ys:List Bool) (dst:List Pair)
    (capacity:dst.length=max xs.length ys.length) (a b scratch:Bool) :
    ∃ t≤25*(max xs.length ys.length)+34,
      run t (initial xs ys dst a b scratch)=final xs ys dst ∧
      Halted (final xs ys dst) ∧
      ∀ k<t,¬Halted (run k (initial xs ys dst a b scratch)) := by
  obtain ⟨k,hk,hp⟩:=PreparedPairXor.machine_exact xs ys a b
  have h:=joined_trace xs ys dst capacity a b scratch hp
  exact ⟨_,by omega,trace_sound h,rfl,trace_live h⟩

/-- Actual installed target bits have the already proved XOR value. The
existing other track is retained literally, without a canonical-width premise. -/
theorem installed_tracks (xs ys:List Bool) (dst:List Pair)
    (capacity:dst.length=max xs.length ys.length) :
    (MarkedTrackWriteback.updated (rows xs ys) dst).map Prod.fst=(rows xs ys).map Prod.fst ∧
    (MarkedTrackWriteback.updated (rows xs ys) dst).map Prod.snd=dst.map Prod.snd ∧
    value ((MarkedTrackWriteback.updated (rows xs ys) dst).map Prod.fst)=
      FixedTapeMachine.wordValue xs ^^^ FixedTapeMachine.wordValue ys := by
  obtain ⟨ht,ho⟩:=MarkedTrackWriteback.updated_tracks (rows xs ys) dst ((rows_length xs ys).trans capacity.symm)
  exact ⟨ht,ho,by rw [ht];exact (PreparedPairXor.output_values xs ys).1⟩

def cells : State → Nat
  | .preparing p d _ => PreparedPairXorSpace.cells p+MarkedTrackWriteback.tapeCells d
  | .writing l r wl wr _ s => BackwardPairedInput.inputCells l+
      BackwardPairedInput.inputCells r+BackwardPairedInput.inputCells wl+
      BackwardPairedInput.inputCells wr+MarkedTrackWriteback.cells s

theorem initial_cells (xs ys:List Bool) (dst:List Pair) (a b scratch:Bool) :
    cells (initial xs ys dst a b scratch)=
      max 1 xs.length+max 1 ys.length+2+dst.length+2 := by
  simp only [initial,cells,PreparedPairXorSpace.initial_cells,MarkedTrackWriteback.tapeCells,MarkedBitXorScan.marked,
    List.length_nil,List.length_cons,List.length_append,List.length_map]
  omega

private theorem write_prefix_bound (xs ys:List Bool) (dst:List Pair)
    (capacity:dst.length=max xs.length ys.length) (scratch:Bool) (k:Nat) :
    cells (run k (writingEntrance xs ys dst scratch))≤
      cells (.preparing (PreparedPairXor.final xs ys) ⟨[],MarkedBitXorScan.marked dst⟩ scratch) := by
  have h:=MarkedTrackWriteback.writeback_storage (rows xs ys) dst ((rows_length xs ys).trans capacity.symm) scratch k
  rw [rows_length] at h
  simp only [writingEntrance,writing_run,cells]
  simp only [PreparedPairXor.final,PreparedPairXorSpace.cells,MarkedBitXorScan.final,MarkedBitXorScan.cells,
    PreparedPairXor.pairedRows,MarkedBitXorScan.marked,MarkedTrackWriteback.tapeCells,List.length_nil,List.length_cons,
    List.length_append,List.length_map,List.length_zip]
  rw [BinaryInputPreparation.pad_length _ _ (Nat.le_max_left _ _),
    BinaryInputPreparation.pad_length _ _ (Nat.le_max_right _ _),Nat.min_self]
  omega

/-- Derived six-tape entrance-volume bound. Preparation reuses its actual
four-cell growth law; write-back reuses its no-extra-block prefix bound.
All fuel, including post-halt observation, is covered. -/
theorem machine_resources (xs ys:List Bool) (dst:List Pair)
    (capacity:dst.length=max xs.length ys.length) (a b scratch:Bool) :
    ∃ t≤25*cells (initial xs ys dst a b scratch),
      run t (initial xs ys dst a b scratch)=final xs ys dst ∧
      Halted (final xs ys dst) ∧
      (∀ k<t,¬Halted (run k (initial xs ys dst a b scratch))) ∧
      ∀ k,cells (run k (initial xs ys dst a b scratch))≤
        73*cells (initial xs ys dst a b scratch) := by
  obtain ⟨q,hq,hp⟩:=PreparedPairXor.machine_exact xs ys a b
  let pt:=q+12*(max xs.length ys.length)+17
  have hp':PreparedPairXor.Trace pt (PreparedPairXor.initial xs ys a b) (PreparedPairXor.final xs ys):=hp
  have h:=joined_trace xs ys dst capacity a b scratch hp'
  have hv:=initial_cells xs ys dst a b scratch
  have hvP:=PreparedPairXorSpace.initial_cells xs ys a b
  have ht:pt≤18*PreparedPairXorSpace.cells (PreparedPairXor.initial xs ys a b) := by dsimp [pt];omega
  have htV:pt+1+(7*(max xs.length ys.length)+9)≤25*cells (initial xs ys dst a b scratch) := by
    dsimp [pt];omega
  refine ⟨_,htV,trace_sound h,rfl,trace_live h,?_⟩
  intro k
  by_cases hk:k≤pt
  · rw [show initial xs ys dst a b scratch=
      .preparing (PreparedPairXor.initial xs ys a b) ⟨[],MarkedBitXorScan.marked dst⟩ scratch from rfl,
      preparing_prefix hp' _ scratch k hk]
    have g:=PreparedPairXorSpace.run_growth k (PreparedPairXor.initial xs ys a b)
    change PreparedPairXorSpace.cells (PreparedPairXor.run k (PreparedPairXor.initial xs ys a b))+
      MarkedTrackWriteback.tapeCells ⟨[],MarkedBitXorScan.marked dst⟩≤
      73*cells (initial xs ys dst a b scratch)
    have hi:cells (initial xs ys dst a b scratch)=
      PreparedPairXorSpace.cells (PreparedPairXor.initial xs ys a b)+
        MarkedTrackWriteback.tapeCells ⟨[],MarkedBitXorScan.marked dst⟩:=rfl
    have hd:MarkedTrackWriteback.tapeCells (⟨[],MarkedBitXorScan.marked dst⟩ : OutputTape)=dst.length+2 := by
      simp [MarkedTrackWriteback.tapeCells,MarkedBitXorScan.marked]
    omega
  · have he:k=pt+1+(k-(pt+1)):=by omega
    have prep:=trace_sound (preparing_trace hp' ⟨[],MarkedBitXorScan.marked dst⟩ scratch)
    have prep':run pt (initial xs ys dst a b scratch)=
      .preparing (PreparedPairXor.final xs ys) ⟨[],MarkedBitXorScan.marked dst⟩ scratch:=prep
    rw [he,run_add,run_add,prep']
    change cells (run (k-(pt+1)) (step
      (.preparing (PreparedPairXor.final xs ys) ⟨[],MarkedBitXorScan.marked dst⟩ scratch)))≤_
    rw [handoff]
    have hw:=write_prefix_bound xs ys dst capacity scratch (k-(pt+1))
    have gp:=PreparedPairXorSpace.run_growth pt (PreparedPairXor.initial xs ys a b)
    have pp:PreparedPairXor.run pt (PreparedPairXor.initial xs ys a b)=PreparedPairXor.final xs ys := by
      have p:=preparing_prefix hp' ⟨[],MarkedBitXorScan.marked dst⟩ scratch pt (Nat.le_refl _)
      rw [prep] at p
      exact (State.preparing.inj p.symm).1
    rw [pp] at gp
    have hd:MarkedTrackWriteback.tapeCells (⟨[],MarkedBitXorScan.marked dst⟩ : OutputTape)=dst.length+2 := by
      simp [MarkedTrackWriteback.tapeCells,MarkedBitXorScan.marked]
    change cells (run (k-(pt+1)) (writingEntrance xs ys dst scratch))≤_
    change cells (run (k-(pt+1)) (writingEntrance xs ys dst scratch))≤
      PreparedPairXorSpace.cells (PreparedPairXor.final xs ys)+MarkedTrackWriteback.tapeCells ⟨[],MarkedBitXorScan.marked dst⟩ at hw
    omega

end CurrentMain.PreparedXorWriteback

#print axioms CurrentMain.PreparedXorWriteback.writing_run
#print axioms CurrentMain.PreparedXorWriteback.rows_length
#print axioms CurrentMain.PreparedXorWriteback.handoff
#print axioms CurrentMain.PreparedXorWriteback.machine_result
#print axioms CurrentMain.PreparedXorWriteback.installed_tracks
#print axioms CurrentMain.PreparedXorWriteback.initial_cells
#print axioms CurrentMain.PreparedXorWriteback.machine_resources
#check @CurrentMain.PreparedXorWriteback.machine_result
#check @CurrentMain.PreparedXorWriteback.machine_resources

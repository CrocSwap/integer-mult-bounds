import PositionalMetadataAccess

/-!
Actual reverse block traversal from a supplied marked-block focus to global
packed home, using the same finite unary positional control. Each tick crosses
one preceding block in reverse physical order. The transition reads finite
L/data/R and control symbols only; it never inspects zipper emptiness or a Nat
position. It rewinds the unary head and preserves all symbols and arbitrary
Boolean scratch. The count is derived from the transition trace.

Reuses the accepted tape operations and unary convention. The unary rewind
proof follows PositionalMetadataAccess with the identical rewind transition;
the reverse data traversal is new. James Chang with OpenAI assistance,
Apache-2.0. Pinned conditional context:
kappa=836330098538459/500000000000000000. Uncompiled candidate.
Key-to-position, unary preparation, allocation and source refresh stay external.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PositionalMetadataReturn
open PairedBitXorScan (Tape Pair)
open MarkedBitXorScan (Symbol marked dataSymbol)
open PackedMetadataSlots (Block Focus pack capacity)
open PositionalMetadataAccess (ControlSymbol)

inductive Phase where
  | enterControl | choose | scan | rewindControl | halt
  deriving DecidableEq

structure State where
  dataTape : Tape Symbol
  controlTape : Tape ControlSymbol
  scratch : Bool
  phase : Phase

def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .enterControl =>
      match s.controlTape.readHead .blank with
      | .leftMarker => { s with controlTape := s.controlTape.moveRight .blank, phase := .choose }
      | _ => { s with phase := .halt }
  | .choose =>
      match s.controlTape.readHead .blank, s.dataTape.readHead .blank with
      | .tick, .leftMarker => { s with dataTape := s.dataTape.moveLeft .blank, phase := .scan }
      | .rightMarker, .leftMarker => { s with phase := .rewindControl }
      | _, _ => { s with phase := .halt }
  | .scan =>
      match s.dataTape.readHead .blank with
      | .data _ _ => { s with dataTape := s.dataTape.moveLeft .blank }
      | .rightMarker => { s with dataTape := s.dataTape.moveLeft .blank }
      | .leftMarker => { s with controlTape := s.controlTape.moveRight .blank, phase := .choose }
      | .blank => { s with phase := .halt }
  | .rewindControl =>
      match s.controlTape.readHead .blank with
      | .leftMarker => { s with phase := .halt }
      | _ => { s with controlTape := s.controlTape.moveLeft .blank }

def run : Nat → State → State
  | 0, s => s
  | k+1, s => run k (step s)

def tapeCells {α : Type} (t : Tape α) : Nat := t.left.length + t.right.length

def cells (s : State) : Nat := tapeCells s.dataTape + tapeCells s.controlTape

/-- Actual live transitions, each with its proved no-allocation equation. -/
inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {n : Nat} {s t : State} (live : s.phase ≠ .halt)
      (size : cells (step s) = cells s) (tail : Trace n (step s) t) : Trace (n+1) s t

private theorem trace_one (s : State) (h : s.phase ≠ .halt)
    (hs : cells (step s) = cells s) : Trace 1 s (step s) :=
  Trace.next h hs (Trace.nil _)

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa only [Nat.zero_add] using g
  | next live size tail ih => simpa only [Nat.succ_add] using Trace.next live size (ih g)

private theorem trace_sound {n : Nat} {s t : State} (h : Trace n s t) : run n s = t := by
  induction h with
  | nil => rfl
  | next _ _ _ ih => exact ih

private theorem trace_live {n : Nat} {s t : State} (h : Trace n s t)
    (k : Nat) (hk : k < n) : (run k s).phase ≠ .halt := by
  induction h generalizing k with
  | nil => omega
  | next live _ _ ih =>
      cases k with
      | zero => exact live
      | succ k => exact ih k (by omega)

private theorem halt_run (s : State) (h : s.phase = .halt) (k : Nat) : run k s = s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [run, step, h] using ih

private theorem trace_storage {n : Nat} {s t : State} (h : Trace n s t)
    (ht : t.phase = .halt) (k : Nat) : cells (run k s) = cells s := by
  induction h generalizing k with
  | nil => rw [halt_run _ ht]
  | next _ size _ ih =>
      cases k with
      | zero => rfl
      | succ k => exact (ih ht k).trans size

def snapshot (dl dr : List Symbol) (cl cr : List ControlSymbol)
    (scratch : Bool) (phase : Phase) : State :=
  ⟨⟨dl,dr⟩,⟨cl,cr⟩,scratch,phase⟩

private theorem scan_move (dl dr : List Symbol) (cl cr : List ControlSymbol) (scratch : Bool)
    (hl : (⟨[],dr⟩ : Tape Symbol).readHead .blank ≠ .leftMarker)
    (hb : (⟨[],dr⟩ : Tape Symbol).readHead .blank ≠ .blank) :
    step (snapshot dl dr cl cr scratch .scan) =
      ⟨(⟨dl,dr⟩ : Tape Symbol).moveLeft .blank,⟨cl,cr⟩,scratch,.scan⟩ := by
  cases hh : (⟨[],dr⟩ : Tape Symbol).readHead .blank <;>
    simp_all [snapshot, step, Tape.readHead]

/-- Rewind the remaining reversed payload and its L, then advance one control
 tick. The right-hand word, including the already updated selected block, is
 carried verbatim through each real move. -/
private theorem rewind_data (ls : List Pair) (dl dr : List Symbol)
    (cl cr : List ControlSymbol) (scratch : Bool)
    (hl : (⟨[],dr⟩ : Tape Symbol).readHead .blank ≠ .leftMarker)
    (hb : (⟨[],dr⟩ : Tape Symbol).readHead .blank ≠ .blank) :
    Trace (ls.length+2)
      (snapshot (ls.map dataSymbol ++ .leftMarker :: dl) dr cl (.tick :: cr) scratch .scan)
      (snapshot dl (.leftMarker :: (ls.reverse.map dataSymbol ++ dr)) (.tick :: cl) cr scratch .choose) := by
  induction ls generalizing dr with
  | nil =>
      simp only [List.map_nil, List.nil_append, List.reverse_nil]
      have hm := scan_move (.leftMarker :: dl) dr cl (.tick :: cr) scratch hl hb
      apply Trace.next (by intro h; cases h)
      · rw [hm]
        simp [snapshot, cells, tapeCells, Tape.moveLeft]
        omega
      · rw [hm]
        apply Trace.next (by intro h; cases h)
        · simp [snapshot, cells, tapeCells, step, Tape.readHead, Tape.moveLeft, Tape.moveRight]
          omega
        · exact Trace.nil _
  | cons row ls ih =>
      have hm := scan_move ((row :: ls).map dataSymbol ++ .leftMarker :: dl) dr cl (.tick :: cr) scratch hl hb
      apply Trace.next (by intro h; cases h)
      · rw [hm]
        simp [snapshot, cells, tapeCells, Tape.moveLeft]
        omega
      · rw [hm]
        have ht := ih (dataSymbol row :: dr) (by simp [Tape.readHead, dataSymbol])
          (by simp [Tape.readHead, dataSymbol])
        simpa [snapshot, Tape.moveLeft, List.reverse_cons, List.map_append, List.append_assoc] using ht

private theorem skip_block (rows : List Pair) (dl dr : List Symbol)
    (cl cr : List ControlSymbol) (scratch : Bool)
    (hh : (⟨[],dr⟩ : Tape Symbol).readHead .blank = .leftMarker) :
    Trace (rows.length+3)
      (snapshot ((marked rows).reverse ++ dl) dr cl (.tick :: cr) scratch .choose)
      (snapshot dl (marked rows ++ dr) (.tick :: cl) cr scratch .choose) := by
  simp only [Tape.readHead] at hh
  have hd := rewind_data rows.reverse dl (.rightMarker :: dr) cl cr scratch
    (by intro h; cases h) (by intro h; cases h)
  have hn : rows.reverse.length + 2 + 1 = rows.length + 3 := by simp
  rw [← hn]
  apply Trace.next (by intro h; cases h)
  · simp [snapshot, cells, tapeCells, step, Tape.readHead, hh, marked,
      List.reverse_append, List.map_reverse, Tape.moveLeft]
    omega
  · simpa [snapshot, step, Tape.readHead, hh, marked, List.reverse_append,
      List.map_reverse, Tape.moveLeft, List.append_assoc] using hd

private theorem ticks_cons (n : Nat) (tail : List ControlSymbol) :
    List.replicate n .tick ++ .tick :: tail = .tick :: (List.replicate n .tick ++ tail) := by
  induction n with
  | zero => rfl
  | succ n ih => simpa only [List.replicate_succ, List.cons_append] using congrArg (ControlSymbol.tick :: ·) ih

private theorem pack_append (xs ys : List Block) : pack (xs ++ ys) = pack xs ++ pack ys := by
  induction xs with
  | nil => rfl
  | cons b xs ih => simp only [List.cons_append, pack, ih, List.append_assoc]

private theorem pack_head (pre : List Block) (dr : List Symbol)
    (hh : (⟨[],dr⟩ : Tape Symbol).readHead .blank = .leftMarker) :
    (⟨[],pack pre ++ dr⟩ : Tape Symbol).readHead .blank = .leftMarker := by
  cases pre with
  | nil => exact hh
  | cons b pre => rfl

/-- Normal list induction executes the tail first, which is the actual reverse
order stored in the left zipper. No right-suffix symbols are overwritten. -/
private theorem skip_blocks (pre : List Block) (dl dr : List Symbol)
    (cl cr : List ControlSymbol) (scratch : Bool)
    (hh : (⟨[],dr⟩ : Tape Symbol).readHead .blank = .leftMarker) :
    Trace (capacity pre + pre.length)
      (snapshot ((pack pre).reverse ++ dl) dr cl
        (List.replicate pre.length .tick ++ cr) scratch .choose)
      (snapshot dl (pack pre ++ dr)
        (List.replicate pre.length .tick ++ cl) cr scratch .choose) := by
  induction pre generalizing dl cl cr with
  | nil => simpa [capacity, pack, snapshot] using Trace.nil (snapshot dl dr cl cr scratch .choose)
  | cons block pre ih =>
      have ht := ih ((marked block.rows).reverse ++ dl) cl (.tick :: cr)
      have hb := skip_block block.rows dl (pack pre ++ dr)
        (List.replicate pre.length .tick ++ cl) cr scratch (pack_head pre dr hh)
      have h := trace_trans ht hb
      have hn : (capacity pre + pre.length) + (block.rows.length + 3) =
          capacity (block :: pre) + (block :: pre).length := by
        simp only [capacity, List.length_cons]
        omega
      rw [hn] at h
      simpa only [pack, List.length_cons, List.replicate_succ, List.cons_append,
        List.reverse_append, List.append_assoc, ticks_cons] using h

/-- Rewind only supplied unary ticks. The actual control head returns to L;
the reached packed-data focus and arbitrary carried scratch stay fixed. -/
private theorem rewind_ticks (n : Nat) (data : Tape Symbol) (rs : List ControlSymbol)
    (scratch : Bool) (hr : (⟨[],rs⟩ : Tape ControlSymbol).readHead .blank ≠ .leftMarker) :
    Trace (n+2)
      ⟨data,⟨List.replicate n .tick ++ [.leftMarker],rs⟩,scratch,.rewindControl⟩
      ⟨data,⟨[],.leftMarker :: (List.replicate n .tick ++ rs)⟩,scratch,.halt⟩ := by
  induction n generalizing rs with
  | zero =>
      apply Trace.next (by intro h; cases h)
      · cases hrs : rs with
        | nil => simp [cells, tapeCells, step, Tape.readHead, Tape.moveLeft]
        | cons x xs =>
            cases x <;> simp_all [cells, tapeCells, step, Tape.readHead, Tape.moveLeft]
            all_goals omega
      · have hx : step (⟨data,⟨List.replicate 0 .tick ++ [.leftMarker],rs⟩,scratch,.rewindControl⟩ : State) =
          ⟨data,⟨[],.leftMarker :: rs⟩,scratch,.rewindControl⟩ := by
          cases rs with
          | nil => rfl
          | cons x xs => cases x <;> simp_all [step, Tape.readHead, Tape.moveLeft]
        rw [hx]
        apply Trace.next (by intro h; cases h)
        · rfl
        · exact Trace.nil _
  | succ n ih =>
      have hx : step (⟨data,⟨List.replicate (n+1) .tick ++ [.leftMarker],rs⟩,scratch,.rewindControl⟩ : State) =
          ⟨data,⟨List.replicate n .tick ++ [.leftMarker],.tick :: rs⟩,scratch,.rewindControl⟩ := by
        cases rs with
        | nil => simp [step, Tape.readHead, Tape.moveLeft, List.replicate_succ]
        | cons x xs => cases x <;> simp_all [step, Tape.readHead, Tape.moveLeft, List.replicate_succ]
      apply Trace.next (by intro h; cases h)
      · rw [hx]
        simp [cells, tapeCells, List.replicate_succ]
        omega
      · rw [hx]
        have h := ih (.tick :: rs) (by intro h; cases h)
        simpa only [List.replicate_succ, List.cons_append, ticks_cons] using h

abbrev unary := PositionalMetadataAccess.unary

def initial (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) : State :=
  ⟨⟨(pack pre).reverse,pack (selected :: post)⟩,unary pre.length,scratch,.enterControl⟩

def final (n : Nat) (blocks : List Block) (scratch : Bool) : State :=
  ⟨⟨[],pack blocks⟩,unary n,scratch,.halt⟩

theorem return_exact (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    Trace (capacity pre + 2*pre.length + 4)
      (initial pre selected post scratch)
      (final pre.length (pre ++ selected :: post) scratch) := by
  have hs := skip_blocks pre [] (pack (selected :: post)) [.leftMarker] [.rightMarker] scratch rfl
  simp only [List.append_nil] at hs
  have hr := rewind_ticks pre.length
    (⟨[],pack pre ++ pack (selected :: post)⟩ : Tape Symbol) [.rightMarker] scratch
    (by intro h; cases h)
  have hh := pack_head pre (pack (selected :: post)) rfl
  simp only [Tape.readHead] at hh
  have hc : Trace (pre.length+3)
      (snapshot [] (pack pre ++ pack (selected :: post))
        (List.replicate pre.length .tick ++ [.leftMarker]) [.rightMarker] scratch .choose)
      (final pre.length (pre ++ selected :: post) scratch) := by
    apply Trace.next (by intro h; cases h)
    · simp [snapshot, step, Tape.readHead, hh, cells]
    · simpa [snapshot, step, hh,
        Tape.readHead, final, unary, PositionalMetadataAccess.unary, pack_append] using hr
  have ht := trace_trans hs hc
  have hn : capacity pre + pre.length + (pre.length+3) + 1 = capacity pre + 2*pre.length + 4 := by omega
  rw [← hn]
  apply Trace.next (by intro h; cases h)
  · simp [initial, unary, PositionalMetadataAccess.unary, cells, tapeCells, step, Tape.readHead, Tape.moveRight]
    omega
  · simpa [initial, unary, PositionalMetadataAccess.unary, snapshot, step, Tape.readHead, Tape.moveRight] using ht

theorem return_result (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    run (capacity pre + 2*pre.length + 4) (initial pre selected post scratch) =
      final pre.length (pre ++ selected :: post) scratch :=
  trace_sound (return_exact pre selected post scratch)

theorem return_first_halt (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    (run (capacity pre + 2*pre.length + 4) (initial pre selected post scratch)).phase = .halt ∧
    ∀ k, k < capacity pre + 2*pre.length + 4 →
      (run k (initial pre selected post scratch)).phase ≠ .halt :=
  ⟨by rw [return_result]; rfl, trace_live (return_exact pre selected post scratch)⟩

theorem return_storage (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (k : Nat) :
    cells (run k (initial pre selected post scratch)) =
      capacity (pre ++ selected :: post) + (pre.length+2) := by
  rw [trace_storage (return_exact pre selected post scratch) rfl k]
  have hp := PackedMetadataSlots.pack_capacity (pre ++ selected :: post)
  rw [pack_append, List.length_append] at hp
  simp [initial, unary, PositionalMetadataAccess.unary, cells, tapeCells]
  omega

end CurrentMain.PositionalMetadataReturn
#print axioms CurrentMain.PositionalMetadataReturn.return_exact
#print axioms CurrentMain.PositionalMetadataReturn.return_result
#print axioms CurrentMain.PositionalMetadataReturn.return_first_halt
#print axioms CurrentMain.PositionalMetadataReturn.return_storage
#check @CurrentMain.PositionalMetadataReturn.return_result

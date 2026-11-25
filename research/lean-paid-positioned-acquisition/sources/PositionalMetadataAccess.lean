import PackedMetadataSlots

/-!
Paid positional access to a supplied finite packed metadata store. A marked
unary control supplies one tick per preceding block. The actual finite-symbol
controller reads only current symbols, traverses every preceding L/data/R cell,
and rewinds the unary-control head. The data head remains at the selected L.
No Nat decrement, key comparison, list-length test, or hidden boundary sensor
occurs in step. External run fuel and input constructors are observations.

Successful access consumes the exact valid packed/control entrance, and the
locate corollary binds its unary length to the executable lookup's before list.
Missing/malformed inputs do not acquire a successful-lookup theorem from the
total fallback transitions. All supplied packed and unary cells are counted.
Arbitrary carried Boolean scratch and the complete packed/control words are
returned unchanged at the proved endpoint. Global data-head return, computing
key-to-position, key encoding, unary preparation, allocation, source refresh
and handoff into another controller remain separate costs.

James Chang with OpenAI assistance; Apache-2.0. Reuses accepted Tape head/move
operations, packed-slot decomposition and ambient XOR interface. The accepted
marked-padding machine motivates the supplied unary-control convention; its
padding-specific execution is not relabelled as this new seek controller.
Pinned conditional context: kappa=836330098538459/500000000000000000.
Uncompiled candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PositionalMetadataAccess
open PairedBitXorScan (Tape Pair)
open MarkedBitXorScan (Symbol marked dataSymbol)
open PackedMetadataSlots (Block Focus pack capacity)

inductive ControlSymbol where
  | blank | leftMarker | rightMarker | tick
  deriving DecidableEq

inductive Phase where
  | enterControl | choose | scan | advanceControl | rewindControl | halt
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
      | .tick, .leftMarker => { s with dataTape := s.dataTape.moveRight .blank, phase := .scan }
      | .rightMarker, .leftMarker => { s with phase := .rewindControl }
      | _, _ => { s with phase := .halt }
  | .scan =>
      match s.dataTape.readHead .blank with
      | .data _ _ => { s with dataTape := s.dataTape.moveRight .blank }
      | .rightMarker => { s with dataTape := s.dataTape.moveRight .blank, phase := .advanceControl }
      | _ => { s with phase := .halt }
  | .advanceControl => { s with controlTape := s.controlTape.moveRight .blank, phase := .choose }
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

/-- Cross every real payload cell and its R marker, never inspecting a list
length in the transition function. Left/right remaining data are spectators. -/
private theorem scan_data (rows : List Pair) (dl dr : List Symbol)
    (cl cr : List ControlSymbol) (scratch : Bool) :
    Trace (rows.length+1)
      (snapshot dl (rows.map dataSymbol ++ .rightMarker :: dr) cl cr scratch .scan)
      (snapshot (.rightMarker :: (rows.reverse.map dataSymbol ++ dl)) dr cl cr scratch .advanceControl) := by
  induction rows generalizing dl with
  | nil =>
      apply Trace.next (by intro h; cases h)
      · simp [snapshot, cells, tapeCells, step, Tape.readHead, Tape.moveRight]
        omega
      · exact Trace.nil _
  | cons row rows ih =>
      apply Trace.next (by intro h; cases h)
      · simp [snapshot, cells, tapeCells, step, Tape.readHead, Tape.moveRight, dataSymbol]
        omega
      · simpa [snapshot, step, Tape.readHead, Tape.moveRight, dataSymbol,
          List.reverse_cons, List.map_append, List.append_assoc] using ih (dataSymbol row :: dl)

/-- One skip consumes one control tick and moves across one complete block. -/
private theorem skip_block (rows : List Pair) (dl dr : List Symbol)
    (cl cr : List ControlSymbol) (scratch : Bool) :
    Trace (rows.length+3)
      (snapshot dl (marked rows ++ dr) cl (.tick :: cr) scratch .choose)
      (snapshot ((marked rows).reverse ++ dl) dr (.tick :: cl) cr scratch .choose) := by
  have hs := scan_data rows (.leftMarker :: dl) dr cl (.tick :: cr) scratch
  let middle := snapshot (.rightMarker :: (rows.reverse.map dataSymbol ++ (.leftMarker :: dl)))
    dr cl (.tick :: cr) scratch .advanceControl
  have ha : Trace 1 middle (step middle) := trace_one middle (by intro h; cases h) (by
    simp [middle, snapshot, step, cells, tapeCells, Tape.moveRight]
    omega)
  have ht := trace_trans hs ha
  have hsum : rows.length + 1 + 1 + 1 = rows.length + 3 := by omega
  rw [← hsum]
  apply Trace.next (by intro h; cases h)
  · simp [snapshot, marked, cells, tapeCells, step, Tape.readHead, Tape.moveRight]
    omega
  · simpa [snapshot, marked, middle, step, Tape.readHead, Tape.moveRight,
      List.reverse_append, List.map_reverse, List.append_assoc] using ht

private theorem ticks_cons (n : Nat) (tail : List ControlSymbol) :
    List.replicate n .tick ++ .tick :: tail = .tick :: (List.replicate n .tick ++ tail) := by
  induction n with
  | zero => rfl
  | succ n ih => simpa only [List.replicate_succ, List.cons_append] using congrArg (ControlSymbol.tick :: ·) ih

private theorem skip_blocks (pre : List Block) (selected : Block) (post : List Block)
    (dl : List Symbol) (cl : List ControlSymbol) (scratch : Bool) :
    Trace (capacity pre + pre.length)
      (snapshot dl (pack (pre ++ selected :: post)) cl
        (List.replicate pre.length .tick ++ [.rightMarker]) scratch .choose)
      (snapshot ((pack pre).reverse ++ dl) (pack (selected :: post))
        (List.replicate pre.length .tick ++ cl) [.rightMarker] scratch .choose) := by
  induction pre generalizing dl cl with
  | nil => simpa [capacity, pack, snapshot] using
      Trace.nil (snapshot dl (pack (selected :: post)) cl [.rightMarker] scratch .choose)
  | cons block pre ih =>
      have hb := skip_block block.rows dl (pack (pre ++ selected :: post)) cl
        (List.replicate pre.length .tick ++ [.rightMarker]) scratch
      have ht := ih ((marked block.rows).reverse ++ dl) (.tick :: cl)
      have h := trace_trans hb ht
      have hc : block.rows.length + 3 + (capacity pre + pre.length) =
          capacity (block :: pre) + (block :: pre).length := by
        simp only [capacity, List.length_cons]
        omega
      rw [hc] at h
      simpa only [List.cons_append, pack, List.length_cons, List.replicate_succ,
        List.cons_append, List.reverse_append, List.append_assoc,
        ticks_cons] using h

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

def unary (n : Nat) : Tape ControlSymbol :=
  ⟨[],.leftMarker :: (List.replicate n .tick ++ [.rightMarker])⟩

def initial (n : Nat) (blocks : List Block) (scratch : Bool) : State :=
  ⟨⟨[],pack blocks⟩,unary n,scratch,.enterControl⟩

def final (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) : State :=
  ⟨⟨(pack pre).reverse,pack (selected :: post)⟩,unary pre.length,scratch,.halt⟩

/-- Count derived from the actual transitions: skip cost is capacity(pre)+n;
entry, endpoint detection and control rewind add another n+4. -/
theorem access_exact (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    Trace (capacity pre + 2*pre.length + 4)
      (initial pre.length (pre ++ selected :: post) scratch)
      (final pre selected post scratch) := by
  have hs := skip_blocks pre selected post [] [.leftMarker] scratch
  simp only [List.append_nil] at hs
  have hr := rewind_ticks pre.length
    (⟨(pack pre).reverse,pack (selected :: post)⟩ : Tape Symbol) [.rightMarker] scratch
    (by intro h; cases h)
  have hc : Trace (pre.length+3)
      (snapshot (pack pre).reverse (pack (selected :: post))
        (List.replicate pre.length .tick ++ [.leftMarker]) [.rightMarker] scratch .choose)
      (final pre selected post scratch) := by
    apply Trace.next (by intro h; cases h)
    · rfl
    · simpa [snapshot, step, pack, marked, Tape.readHead, final, unary] using hr
  have ht := trace_trans hs hc
  have hn : capacity pre + pre.length + (pre.length+3) + 1 = capacity pre + 2*pre.length + 4 := by omega
  rw [← hn]
  apply Trace.next (by intro h; cases h)
  · simp [initial, unary, cells, tapeCells, step, Tape.readHead, Tape.moveRight]
    omega
  · simpa [initial, unary, snapshot, step, Tape.readHead, Tape.moveRight] using ht

theorem access_result (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    run (capacity pre + 2*pre.length + 4)
      (initial pre.length (pre ++ selected :: post) scratch) = final pre selected post scratch :=
  trace_sound (access_exact pre selected post scratch)

theorem access_first_halt (pre : List Block) (selected : Block) (post : List Block) (scratch : Bool) :
    (run (capacity pre + 2*pre.length + 4)
      (initial pre.length (pre ++ selected :: post) scratch)).phase = .halt ∧
    ∀ k, k < capacity pre + 2*pre.length + 4 →
      (run k (initial pre.length (pre ++ selected :: post) scratch)).phase ≠ .halt :=
  ⟨by rw [access_result]; rfl, trace_live (access_exact pre selected post scratch)⟩

/-- Both full packed storage and the entire supplied unary tape are charged;
the one carried Boolean scratch and finite control are separate fixed fields. -/
theorem access_storage (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (k : Nat) :
    cells (run k (initial pre.length (pre ++ selected :: post) scratch)) =
      capacity (pre ++ selected :: post) + (pre.length + 2) := by
  rw [trace_storage (access_exact pre selected post scratch) rfl k]
  simp [initial, unary, cells, tapeCells, PackedMetadataSlots.pack_capacity, Nat.add_assoc]

/-- Locate success supplies the valid slot and positional index. The paid
controller, rather than a chosen zipper endpoint, then reaches that exact focus.
The logical key-to-index search and unary construction are still not priced. -/
theorem access_from_locate (key : Nat) (blocks : List Block) (f : Focus)
    (h : PackedMetadataSlots.locate key blocks = some f) (scratch : Bool) :
    let out := run (capacity f.before + 2*f.before.length + 4)
      (initial f.before.length blocks scratch)
    out.dataTape = (PackedMetadataSlots.focusState f).tape ∧
      out.controlTape = unary f.before.length ∧ out.scratch = scratch ∧ out.phase = .halt := by
  obtain ⟨he, _, _⟩ := PackedMetadataSlots.locate_spec key blocks f h
  rw [he, access_result]
  exact ⟨rfl,rfl,rfl,rfl⟩

end CurrentMain.PositionalMetadataAccess
#print axioms CurrentMain.PositionalMetadataAccess.access_exact
#print axioms CurrentMain.PositionalMetadataAccess.access_result
#print axioms CurrentMain.PositionalMetadataAccess.access_first_halt
#print axioms CurrentMain.PositionalMetadataAccess.access_storage
#print axioms CurrentMain.PositionalMetadataAccess.access_from_locate
#check @CurrentMain.PositionalMetadataAccess.access_from_locate
#check @CurrentMain.PositionalMetadataAccess.access_storage

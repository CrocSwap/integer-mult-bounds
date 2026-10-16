import MarkedBitXorScan
import SequentialBitAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. Prepared with OpenAI assistance.

A sequential three-tape implementation of little-endian zero padding and copy.
The data and unary-control tapes have explicit left/right marker symbols. The
output starts entirely blank: the machine writes both output markers and every
output data cell. Tests inspect the current symbol only. Each transition reads
or changes a bounded number of finite-alphabet cells/registers and moves at most
one head by one cell. No Nat/Int arithmetic, variable shift, random access or
zipper-boundary sensor occurs in the transition function.

The unary control of length d is supplied, as is the marked source. Producing
that control from encoded exponents, installing input markers, transporting
three tapes into a single tape, and arbitrary dirty-output restoration are
separate tasks. The one Boolean scratch register is explicitly cleared, not
reversibly restored when initially dirty. The external run fuel is an observer.

The intended exact first-halt count is 6*(d+n)+14, including d=n=0. Output
allocation is d+n+2 actual cells. This is a generic implementation and contains
no selected numerical table; the surrounding author-checked context remains
kappa=836330098538459/500000000000000000. UNCOMPILED source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace MarkedZeroPadding
open CurrentMain.PairedBitXorScan (Tape)

inductive Symbol where
  | blank | leftMarker | rightMarker | tick | data (b : Bool)
  deriving DecidableEq

inductive Input where
  | control | data
  deriving DecidableEq

inductive WhichTape where
  | output | control | data
  deriving DecidableEq

inductive Phase where
  | writeLeft | enterControl | enterData | enterOutput
  | test (which : Input) | write (which : Input)
  | advanceInput (which : Input) | advanceOutput (which : Input)
  | writeRight | rewind (which : WhichTape) | clear | halt
  deriving DecidableEq

structure State where
  dataTape : Tape Symbol
  controlTape : Tape Symbol
  outputTape : Tape Symbol
  scratch : Bool
  phase : Phase
  deriving DecidableEq

def getInput (s : State) : Input → Tape Symbol
  | .control => s.controlTape
  | .data => s.dataTape

def putInput (s : State) : Input → Tape Symbol → State
  | .control, t => { s with controlTape := t }
  | .data, t => { s with dataTape := t }

def getTape (s : State) : WhichTape → Tape Symbol
  | .output => s.outputTape
  | .control => s.controlTape
  | .data => s.dataTape

def putTape (s : State) : WhichTape → Tape Symbol → State
  | .output, t => { s with outputTape := t }
  | .control, t => { s with controlTape := t }
  | .data, t => { s with dataTape := t }

/-- A finite decoding table, evaluated on one current input symbol. -/
def inputBit : Input → Symbol → Option Bool
  | .control, .tick => some false
  | .data, .data b => some b
  | _, _ => none

def afterInput : Input → Phase
  | .control => .test .data
  | .data => .writeRight

def afterRewind : WhichTape → Phase
  | .output => .rewind .control
  | .control => .rewind .data
  | .data => .clear

/-- One finite-alphabet multi-tape transition. No step observes a list length
or asks whether a zipper component is empty. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .writeLeft =>
      { s with outputTape := s.outputTape.writeHead .leftMarker, phase := .enterControl }
  | .enterControl =>
      { s with controlTape := s.controlTape.moveRight .blank, phase := .enterData }
  | .enterData =>
      { s with dataTape := s.dataTape.moveRight .blank, phase := .enterOutput }
  | .enterOutput =>
      { s with outputTape := s.outputTape.moveRight .blank, phase := .test .control }
  | .test w =>
      match inputBit w ((getInput s w).readHead .blank) with
      | some b => { s with scratch := b, phase := .write w }
      | none =>
          if (getInput s w).readHead .blank = .rightMarker then
            { s with phase := afterInput w }
          else { s with phase := .halt }
  | .write w =>
      { s with outputTape := s.outputTape.writeHead (.data s.scratch), phase := .advanceInput w }
  | .advanceInput w =>
      { putInput s w ((getInput s w).moveRight .blank) with phase := .advanceOutput w }
  | .advanceOutput w =>
      { s with outputTape := s.outputTape.moveRight .blank, phase := .test w }
  | .writeRight =>
      { s with outputTape := s.outputTape.writeHead .rightMarker, phase := .rewind .output }
  | .rewind w =>
      if (getTape s w).readHead .blank = .leftMarker then
        { s with phase := afterRewind w }
      else putTape s w ((getTape s w).moveLeft .blank)
  | .clear => { s with scratch := false, phase := .halt }

def run : Nat → State → State
  | 0, s => s
  | k + 1, s => run k (step s)

/-- Exact execution with no halted padding. This is an observation relation,
not an instruction or a supplied program behavior. -/
inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : s.phase ≠ .halt)
      (tail : Trace k (step s) t) : Trace (k + 1) s t

private theorem trace_one (s : State) (h : s.phase ≠ .halt) : Trace 1 s (step s) :=
  Trace.next h (Trace.nil _)

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m + n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih =>
      simpa only [Nat.succ_add] using Trace.next live (ih g)

private theorem trace_sound {k : Nat} {s t : State} (h : Trace k s t) : run k s = t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem trace_live {k : Nat} {s t : State} (h : Trace k s t)
    (j : Nat) (hj : j < k) : (run j s).phase ≠ .halt := by
  induction h generalizing j with
  | nil => omega
  | next live tail ih =>
      cases j with
      | zero => exact live
      | succ j => exact ih j (by omega)

private theorem halt_run (s : State) (h : s.phase = .halt) (k : Nat) : run k s = s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run, step, h] using ih

/-- The current input and output heads after any whole four-step scan block. -/
def scanState (base : State) (w : Input) (ls rs os : List Symbol) (b : Bool) : State :=
  { putInput base w ⟨ls, rs⟩ with outputTape := ⟨os, []⟩, scratch := b, phase := .test w }

private theorem scan_four (base : State) (w : Input) (a : Symbol) (b c : Bool)
    (ls rs os : List Symbol) (ha : inputBit w a = some b) :
    Trace 4 (scanState base w ls (a :: rs) os c)
      (scanState base w (a :: ls) rs (.data b :: os) b) := by
  cases w <;>
    apply Trace.next (by simp [scanState]) <;>
    simp only [scanState, putInput, step, getInput, Tape.readHead] at *
  all_goals
    rw [ha]
    apply Trace.next (by simp)
    apply Trace.next (by simp [step])
    apply Trace.next (by simp [step, putInput, getInput])
    simp only [step, putInput, getInput, Tape.writeHead, Tape.moveRight, scanState]
    exact Trace.nil _

def finalScratch : List (Symbol × Bool) → Bool → Bool
  | [], b => b
  | row :: rows, _ => finalScratch rows row.2

private theorem scan_rows (base : State) (w : Input) (rows : List (Symbol × Bool))
    (hrows : ∀ row ∈ rows, inputBit w row.1 = some row.2)
    (ls os : List Symbol) (b : Bool) :
    Trace (4 * rows.length)
      (scanState base w ls (rows.map Prod.fst ++ [.rightMarker]) os b)
      (scanState base w (rows.reverse.map Prod.fst ++ ls) [.rightMarker]
        (rows.reverse.map (fun row => Symbol.data row.2) ++ os) (finalScratch rows b)) := by
  induction rows generalizing ls os b with
  | nil => simpa [scanState, finalScratch] using
      Trace.nil (scanState base w ls [.rightMarker] os b)
  | cons row rows ih =>
      have h1 := scan_four base w row.1 row.2 b ls
        (rows.map Prod.fst ++ [.rightMarker]) os (hrows row (by simp))
      have h2 := ih (by intro a ha; exact hrows a (by simp [ha]))
        (row.1 :: ls) (Symbol.data row.2 :: os) row.2
      have h := trace_trans h1 h2
      have hc : 4 + 4 * rows.length = 4 * (row :: rows).length := by
        simp only [List.length_cons]
        omega
      rw [hc] at h
      simpa [List.reverse_cons, List.map_append, List.append_assoc, finalScratch] using h

private theorem scan_end (base : State) (w : Input) (ls os : List Symbol) (b : Bool) :
    Trace 1 (scanState base w ls [.rightMarker] os b)
      { scanState base w ls [.rightMarker] os b with phase := afterInput w } := by
  have h := trace_one (scanState base w ls [.rightMarker] os b) (by simp [scanState])
  cases w <;> simpa [scanState, putInput, step, getInput, inputBit, Tape.readHead] using h

/-- Replace one tape and its phase without changing any other field. -/
def rewindState (base : State) (w : WhichTape) (t : Tape Symbol) (p : Phase) : State :=
  { putTape base w t with phase := p }

private theorem rewind_step (base : State) (w : WhichTape) (t : Tape Symbol) :
    step (rewindState base w t (.rewind w)) =
      if t.readHead .blank = .leftMarker then rewindState base w t (afterRewind w)
      else rewindState base w (t.moveLeft .blank) (.rewind w) := by
  cases w <;> rfl

private theorem rewind_exact (base : State) (w : WhichTape) (ls rs : List Symbol)
    (hls : ∀ a ∈ ls, a ≠ .leftMarker)
    (hrs : (⟨[], rs⟩ : Tape Symbol).readHead .blank ≠ .leftMarker) :
    Trace (ls.length + 2)
      (rewindState base w ⟨ls ++ [.leftMarker], rs⟩ (.rewind w))
      (rewindState base w ⟨[], .leftMarker :: (ls.reverse ++ rs)⟩ (afterRewind w)) := by
  revert hls hrs
  induction ls generalizing rs with
  | nil =>
      intro hls hrs
      apply Trace.next (by simp [rewindState])
      rw [rewind_step]
      simp only [List.nil_append, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp [rewindState])
      rw [rewind_step]
      simp [Tape.moveLeft, Tape.readHead]
      exact Trace.nil _
  | cons a ls ih =>
      intro hls hrs
      apply Trace.next (by simp [rewindState])
      rw [rewind_step]
      have hhead : (⟨(a :: ls) ++ [.leftMarker], rs⟩ : Tape Symbol).readHead .blank ≠
          .leftMarker := hrs
      rw [if_neg hhead]
      have h := ih (a :: rs)
        (by intro b hb; exact hls b (by simp [hb]))
        (by simpa [Tape.readHead] using hls a (by simp))
      simpa [Tape.moveLeft, List.reverse_cons, List.append_assoc] using h

def bits (xs : List Bool) : List Symbol := xs.map Symbol.data

def ticks (d : Nat) : List Symbol := List.replicate d .tick

def marked (xs : List Symbol) : Tape Symbol := ⟨[], .leftMarker :: xs ++ [.rightMarker]⟩

def initial (d : Nat) (xs : List Bool) (scratch : Bool) : State :=
  ⟨marked (bits xs), marked (ticks d), ⟨[], []⟩, scratch, .writeLeft⟩

def padded (d : Nat) (xs : List Bool) : List Bool := List.replicate d false ++ xs

def final (d : Nat) (xs : List Bool) : State :=
  ⟨marked (bits xs), marked (ticks d), marked (bits (padded d xs)), false, .halt⟩

private theorem setup (d : Nat) (xs : List Bool) (b : Bool) :
    Trace 4 (initial d xs b)
      ⟨⟨[.leftMarker], bits xs ++ [.rightMarker]⟩,
        ⟨[.leftMarker], ticks d ++ [.rightMarker]⟩,
        ⟨[.leftMarker], []⟩, b, .test .control⟩ := by
  apply Trace.next (by simp [initial])
  apply Trace.next (by simp [step, initial])
  apply Trace.next (by simp [step, initial])
  apply Trace.next (by simp [step, initial])
  simpa [step, initial, marked, Tape.writeHead, Tape.moveRight] using
    Trace.nil (⟨⟨[.leftMarker], bits xs ++ [.rightMarker]⟩,
      ⟨[.leftMarker], ticks d ++ [.rightMarker]⟩,
      ⟨[.leftMarker], []⟩, b, .test .control⟩ : State)

private theorem no_left_bits (xs : List Bool) :
    ∀ a ∈ bits xs, a ≠ Symbol.leftMarker := by
  intro a ha
  obtain ⟨b, _, rfl⟩ := List.mem_map.mp ha
  simp

private theorem no_left_ticks (d : Nat) :
    ∀ a ∈ ticks d, a ≠ Symbol.leftMarker := by
  intro a ha
  have he : a = Symbol.tick := (List.mem_replicate.mp ha).2
  simp [he]

private theorem finish (d : Nat) (xs : List Bool) (b : Bool) :
    Trace (2 * (d + xs.length) + 8)
      ⟨⟨(bits xs).reverse ++ [.leftMarker], [.rightMarker]⟩,
        ⟨ticks d ++ [.leftMarker], [.rightMarker]⟩,
        ⟨(bits (padded d xs)).reverse ++ [.leftMarker], []⟩, b, .writeRight⟩
      (final d xs) := by
  let s : State :=
    ⟨⟨(bits xs).reverse ++ [.leftMarker], [.rightMarker]⟩,
      ⟨ticks d ++ [.leftMarker], [.rightMarker]⟩,
      ⟨(bits (padded d xs)).reverse ++ [.leftMarker], []⟩, b, .writeRight⟩
  have hw := trace_one s (by simp [s])
  have ho := rewind_exact (step s) .output (bits (padded d xs)).reverse [.rightMarker]
    (by simpa using no_left_bits (padded d xs)) (by simp [Tape.readHead])
  have hc := rewind_exact
    ⟨s.dataTape, s.controlTape, marked (bits (padded d xs)), b, .rewind .control⟩
    .control (ticks d) [.rightMarker] (no_left_ticks d) (by simp [Tape.readHead])
  have hd := rewind_exact
    ⟨s.dataTape, marked (ticks d), marked (bits (padded d xs)), b, .rewind .data⟩
    .data (bits xs).reverse [.rightMarker]
    (by simpa using no_left_bits xs) (by simp [Tape.readHead])
  have hb := trace_one
    (⟨marked (bits xs), marked (ticks d), marked (bits (padded d xs)), b, .clear⟩ : State)
    (by simp)
  have hwo : Trace (1 + (bits (padded d xs)).reverse.length + 2) s
      ⟨s.dataTape, s.controlTape, marked (bits (padded d xs)), b, .rewind .control⟩ := by
    simpa [rewindState, putTape, step, s, Tape.writeHead, marked, Nat.add_assoc] using
      trace_trans hw ho
  have hctrl : Trace ((ticks d).length + 2)
      (⟨s.dataTape, s.controlTape, marked (bits (padded d xs)), b, .rewind .control⟩ : State)
      ⟨s.dataTape, marked (ticks d), marked (bits (padded d xs)), b, .rewind .data⟩ := by
    simpa [rewindState, putTape, s, marked, ticks] using hc
  have hdata : Trace ((bits xs).reverse.length + 2)
      (⟨s.dataTape, marked (ticks d), marked (bits (padded d xs)), b, .rewind .data⟩ : State)
      ⟨marked (bits xs), marked (ticks d), marked (bits (padded d xs)), b, .clear⟩ := by
    simpa [rewindState, putTape, s, marked] using hd
  have hclear : Trace 1
      (⟨marked (bits xs), marked (ticks d), marked (bits (padded d xs)), b, .clear⟩ : State)
      (final d xs) := by simpa [step, final] using hb
  have h := trace_trans (trace_trans (trace_trans hwo hctrl) hdata) hclear
  have he : 1 + (bits (padded d xs)).reverse.length + 2 + ((ticks d).length + 2) +
      ((bits xs).reverse.length + 2) + 1 = 2 * (d + xs.length) + 8 := by
    simp only [bits, padded, ticks, List.length_reverse, List.length_map,
      List.length_append, List.length_replicate]
    omega
  rw [he] at h
  exact h

def tapeCells (t : Tape Symbol) : Nat := t.left.length + t.right.length

def cells (s : State) : Nat :=
  tapeCells s.dataTape + tapeCells s.controlTape + tapeCells s.outputTape

private theorem write_cells (t : Tape Symbol) (a : Symbol) :
    tapeCells t ≤ tapeCells (t.writeHead a) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.writeHead]

private theorem right_cells (t : Tape Symbol) :
    tapeCells t ≤ tapeCells (t.moveRight .blank) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.moveRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem left_cells (t : Tape Symbol) :
    tapeCells t ≤ tapeCells (t.moveLeft .blank) := by
  rcases t with ⟨ls, rs⟩
  cases ls <;> simp [tapeCells, Tape.moveLeft, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem replacement_cells (s : State) (w : WhichTape) (t : Tape Symbol)
    (h : tapeCells (getTape s w) ≤ tapeCells t) : cells s ≤ cells (putTape s w t) := by
  cases w <;> simp only [getTape, putTape, cells] at * <;> omega

/-- Allocation is monotone: overwrites and one-cell moves never discard a
represented cell. This applies even to malformed states, not just the trace. -/
theorem step_cells (s : State) : cells s ≤ cells (step s) := by
  cases hp : s.phase with
  | halt => simp [step, hp]
  | writeLeft =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .output (s.outputTape.writeHead .leftMarker)
          (write_cells s.outputTape .leftMarker)
  | enterControl =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .control (s.controlTape.moveRight .blank) (right_cells s.controlTape)
  | enterData =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .data (s.dataTape.moveRight .blank) (right_cells s.dataTape)
  | enterOutput =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .output (s.outputTape.moveRight .blank) (right_cells s.outputTape)
  | test w =>
      cases hb : inputBit w ((getInput s w).readHead .blank) with
      | none => simp only [step, hp, hb]; split <;> simp [cells]
      | some b => simp [step, hp, hb, cells]
  | write w =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .output (s.outputTape.writeHead (.data s.scratch))
          (write_cells s.outputTape (.data s.scratch))
  | advanceInput w =>
      cases w with
      | control =>
          simpa [step, hp, getInput, putInput, cells, putTape] using
            replacement_cells s .control (s.controlTape.moveRight .blank)
              (right_cells s.controlTape)
      | data =>
          simpa [step, hp, getInput, putInput, cells, putTape] using
            replacement_cells s .data (s.dataTape.moveRight .blank) (right_cells s.dataTape)
  | advanceOutput w =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .output (s.outputTape.moveRight .blank) (right_cells s.outputTape)
  | writeRight =>
      simpa [step, hp, cells, putTape] using
        replacement_cells s .output (s.outputTape.writeHead .rightMarker)
          (write_cells s.outputTape .rightMarker)
  | rewind w =>
      simp only [step, hp]
      split
      · simp [cells]
      · exact replacement_cells s w ((getTape s w).moveLeft .blank) (left_cells (getTape s w))
  | clear => simp [step, hp, cells]

private theorem trace_storage {n : Nat} {s t : State} (h : Trace n s t)
    (ht : t.phase = .halt) (k : Nat) : cells (run k s) ≤ cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih =>
      cases k with
      | zero => exact (step_cells s).trans (ih ht 0)
      | succ k => exact ih ht k

/-- The source and unary shift control are preserved, both output markers and
all output data are written, all three heads return, and scratch is cleared.
The trace has no halted suffix, so its transition invoice is a first-halt count. -/
theorem padding_exact (d : Nat) (xs : List Bool) (b : Bool) :
    Trace (6 * (d + xs.length) + 14) (initial d xs b) (final d xs) := by
  let s : State :=
    ⟨⟨[.leftMarker], bits xs ++ [.rightMarker]⟩,
      ⟨[.leftMarker], ticks d ++ [.rightMarker]⟩,
      ⟨[.leftMarker], []⟩, b, .test .control⟩
  let controlRows : List (Symbol × Bool) := List.replicate d (.tick, false)
  let dataRows : List (Symbol × Bool) := xs.map (fun a => (Symbol.data a, a))
  let b₁ := finalScratch controlRows b
  let b₂ := finalScratch dataRows b₁
  have hp := scan_rows s .control controlRows
    (by intro row hr; have he := (List.mem_replicate.mp hr).2; simp [he, inputBit])
    [.leftMarker] [.leftMarker] b
  have hpe := scan_end s .control (ticks d ++ [.leftMarker])
    (bits (List.replicate d false) ++ [.leftMarker]) b₁
  have hp0 : Trace (4 * d) s
      (scanState s .control (ticks d ++ [.leftMarker])
        [.rightMarker] (bits (List.replicate d false) ++ [.leftMarker]) b₁) := by
    simpa [s, controlRows, scanState, putInput, bits, ticks, b₁,
      List.map_replicate] using hp
  have hp' : Trace (4 * d + 1) s
      ⟨s.dataTape, ⟨ticks d ++ [.leftMarker], [.rightMarker]⟩,
        ⟨bits (List.replicate d false) ++ [.leftMarker], []⟩, b₁, .test .data⟩ := by
    simpa [s, controlRows, scanState, putInput, bits, ticks, b₁, afterInput,
      List.map_replicate] using trace_trans hp0 hpe
  let t : State :=
    ⟨s.dataTape, ⟨ticks d ++ [.leftMarker], [.rightMarker]⟩,
      ⟨bits (List.replicate d false) ++ [.leftMarker], []⟩, b₁, .test .data⟩
  have hd := scan_rows t .data dataRows
    (by intro row hr; obtain ⟨a, _, rfl⟩ := List.mem_map.mp hr; rfl)
    [.leftMarker] (bits (List.replicate d false) ++ [.leftMarker]) b₁
  have hde := scan_end t .data ((bits xs).reverse ++ [.leftMarker])
    ((bits (padded d xs)).reverse ++ [.leftMarker]) b₂
  have hd0 : Trace (4 * xs.length) t
      (scanState t .data ((bits xs).reverse ++ [.leftMarker]) [.rightMarker]
        ((bits (padded d xs)).reverse ++ [.leftMarker]) b₂) := by
    simpa [t, s, dataRows, scanState, putInput, bits, padded, b₂,
      List.map_map, List.reverse_append, List.map_append, List.append_assoc,
      List.map_replicate] using hd
  have hd' : Trace (4 * xs.length + 1) t
      ⟨⟨(bits xs).reverse ++ [.leftMarker], [.rightMarker]⟩,
        ⟨ticks d ++ [.leftMarker], [.rightMarker]⟩,
        ⟨(bits (padded d xs)).reverse ++ [.leftMarker], []⟩, b₂, .writeRight⟩ := by
    simpa [t, s, dataRows, scanState, putInput, bits, padded, b₂, afterInput,
      List.map_map, List.reverse_append, List.map_append, List.append_assoc,
      List.map_replicate] using trace_trans hd0 hde
  have h := trace_trans (trace_trans (trace_trans (setup d xs b) hp') hd') (finish d xs b₂)
  have he : 4 + (4 * d + 1) + (4 * xs.length + 1) +
      (2 * (d + xs.length) + 8) = 6 * (d + xs.length) + 14 := by omega
  rw [he] at h
  exact h

theorem padding_result (d : Nat) (xs : List Bool) (b : Bool) :
    run (6 * (d + xs.length) + 14) (initial d xs b) = final d xs :=
  trace_sound (padding_exact d xs b)

theorem padding_first_halt (d : Nat) (xs : List Bool) (b : Bool) :
    (run (6 * (d + xs.length) + 14) (initial d xs b)).phase = .halt ∧
      ∀ k < 6 * (d + xs.length) + 14,
        (run k (initial d xs b)).phase ≠ .halt := by
  constructor
  · rw [padding_result]; rfl
  · exact trace_live (padding_exact d xs b)

/-- A concrete allocation statement: the initially empty output representation
now contains its two freshly written markers and d+n data cells. -/
theorem output_allocation (d : Nat) (xs : List Bool) (b : Bool) :
    (initial d xs b).outputTape.left.length + (initial d xs b).outputTape.right.length = 0 ∧
    let s := run (6 * (d + xs.length) + 14) (initial d xs b)
    s.outputTape.left.length + s.outputTape.right.length = d + xs.length + 2 := by
  constructor
  · rfl
  · rw [padding_result]
    simp [final, marked, bits, padded, Nat.add_assoc]

private theorem padded_eq_zeroShift (d : Nat) (xs : List Bool) :
    padded d xs = SequentialBitAddition.zeroShift d xs := by
  induction d with
  | zero => rfl
  | succ d ih =>
      simpa [padded, List.replicate_succ, SequentialBitAddition.zeroShift] using
        congrArg (fun ys => false :: ys) ih

/-- Sharp represented-tape footprint at every actual prefix, including time
after halting. Input/control cells and both new output markers are included;
one Boolean scratch register and fixed finite control are separate. -/
theorem padding_prefix_storage (d : Nat) (xs : List Bool) (b : Bool) (k : Nat) :
    cells (run k (initial d xs b)) ≤ 2 * (d + xs.length) + 6 := by
  have h := trace_storage (padding_exact d xs b) (by rfl) k
  simpa [cells, tapeCells, final, marked, bits, padded, ticks,
    Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, Nat.mul_add, Nat.two_mul] using h

/-- The output word is exactly the accepted low-zero-prefix specification. -/
theorem padding_value (d : Nat) (xs : List Bool) :
    SequentialBitAddition.decode (padded d xs) =
      (2 : Int) ^ d * SequentialBitAddition.decode xs := by
  rw [padded_eq_zeroShift]
  exact SequentialBitAddition.zero_shift_value d xs

/-- Signed shift retains the supplied sign bit. Width and value change are
proved; creating the source sign-format remains a separate implementation. -/
theorem signed_padding_value (d : Nat) (xs : List Bool) (sign : Bool) :
    SequentialBitAddition.signedValue (padded d xs) sign =
      (2 : Int) ^ d * SequentialBitAddition.signedValue xs sign := by
  rw [SequentialBitAddition.signedValue, padding_value]
  simp only [padded, List.length_append, List.length_replicate]
  rw [pow_add]
  simp only [SequentialBitAddition.signedValue]
  ring

end MarkedZeroPadding

#print axioms MarkedZeroPadding.padding_exact
#print axioms MarkedZeroPadding.padding_result
#print axioms MarkedZeroPadding.padding_first_halt
#print axioms MarkedZeroPadding.output_allocation
#print axioms MarkedZeroPadding.step_cells
#print axioms MarkedZeroPadding.padding_prefix_storage
#print axioms MarkedZeroPadding.padding_value
#print axioms MarkedZeroPadding.signed_padding_value
#check @MarkedZeroPadding.padding_exact
#check @MarkedZeroPadding.padding_first_halt

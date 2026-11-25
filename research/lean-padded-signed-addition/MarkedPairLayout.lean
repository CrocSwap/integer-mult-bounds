import MarkedBitAddition
import SignedWordAlignment

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

A paid layout builder from two actual one-bit marked tapes to the marked
adder's exact three-track input alphabet. Each source is read sequentially;
a source at R contributes its separately supplied sign bit while the other
source continues. Both sign rows, the output bits and the two output markers
are written explicitly into blank workspace. Heads return to L.

The seven-register bank is shared with MarkedBitAddition. x/y hold current
bits, andXY/andTC hold exhaustion flags. These four registers are cleared;
carry/xorXY/sum and the two input signs are preserved. No claim of restoring
old overwritten scratch or output is made. The controller uses no runtime
length/maximum/shift/zip or unbounded arithmetic primitive.

The source signs, marked input words, blank workspace and disjoint tapes are
explicit entrance data. Exponent arithmetic, unary-control generation, tape
format installation and selected Cell encoding remain separate tasks.
Author-checked context: kappa=836330098538459/500000000000000000.
Uncompiled source candidate; acceptance is recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace MarkedPairLayout
open CurrentMain.PairedBitXorScan (Tape)
abbrev BitSymbol := MarkedZeroPadding.Symbol
abbrev RowSymbol := MarkedBitAddition.Symbol
abbrev Row := SequentialBitAddition.Row
abbrev Registers := SequentialBitAddition.Registers

inductive Phase where
  | writeLeft | enterLeft | enterRight | enterOutput
  | readLeft | readRight | test | writeRow | moveLeftInput | moveRightInput | moveOutput
  | writeSignOne | advanceSignOne | writeSignTwo | advanceSignTwo | writeRight
  | rewindOutput | rewindLeft | rewindRight
  | clearX | clearY | clearLeftDone | clearRightDone | halt
  deriving DecidableEq

structure State where
  leftTape : Tape BitSymbol
  rightTape : Tape BitSymbol
  outputTape : Tape RowSymbol
  registers : Registers
  leftSign : Bool
  rightSign : Bool
  phase : Phase
  deriving DecidableEq

def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .writeLeft => { s with outputTape := s.outputTape.writeHead .leftMarker, phase := .enterLeft }
  | .enterLeft => { s with leftTape := s.leftTape.moveRight .blank, phase := .enterRight }
  | .enterRight => { s with rightTape := s.rightTape.moveRight .blank, phase := .enterOutput }
  | .enterOutput => { s with outputTape := s.outputTape.moveRight .blank, phase := .readLeft }
  | .readLeft => match s.leftTape.readHead .blank with
    | .data b => { s with registers := { s.registers with x := b, andXY := false }, phase := .readRight }
    | .rightMarker => { s with registers := { s.registers with x := s.leftSign, andXY := true }, phase := .readRight }
    | _ => { s with phase := .halt }
  | .readRight => match s.rightTape.readHead .blank with
    | .data b => { s with registers := { s.registers with y := b, andTC := false }, phase := .test }
    | .rightMarker => { s with registers := { s.registers with y := s.rightSign, andTC := true }, phase := .test }
    | _ => { s with phase := .halt }
  | .test =>
      if s.registers.andXY && s.registers.andTC then { s with phase := .writeSignOne }
      else { s with phase := .writeRow }
  | .writeRow =>
      { s with outputTape := s.outputTape.writeHead (.data ((s.registers.x, s.registers.y), false)), phase := .moveLeftInput }
  | .moveLeftInput =>
      if s.registers.andXY then { s with phase := .moveRightInput }
      else { s with leftTape := s.leftTape.moveRight .blank, phase := .moveRightInput }
  | .moveRightInput =>
      if s.registers.andTC then { s with phase := .moveOutput }
      else { s with rightTape := s.rightTape.moveRight .blank, phase := .moveOutput }
  | .moveOutput => { s with outputTape := s.outputTape.moveRight .blank, phase := .readLeft }
  | .writeSignOne =>
      { s with outputTape := s.outputTape.writeHead (.data ((s.leftSign, s.rightSign), false)), phase := .advanceSignOne }
  | .advanceSignOne => { s with outputTape := s.outputTape.moveRight .blank, phase := .writeSignTwo }
  | .writeSignTwo =>
      { s with outputTape := s.outputTape.writeHead (.data ((s.leftSign, s.rightSign), false)), phase := .advanceSignTwo }
  | .advanceSignTwo => { s with outputTape := s.outputTape.moveRight .blank, phase := .writeRight }
  | .writeRight => { s with outputTape := s.outputTape.writeHead .rightMarker, phase := .rewindOutput }
  | .rewindOutput =>
      if s.outputTape.readHead .blank = .leftMarker then { s with phase := .rewindLeft }
      else { s with outputTape := s.outputTape.moveLeft .blank }
  | .rewindLeft =>
      if s.leftTape.readHead .blank = .leftMarker then { s with phase := .rewindRight }
      else { s with leftTape := s.leftTape.moveLeft .blank }
  | .rewindRight =>
      if s.rightTape.readHead .blank = .leftMarker then { s with phase := .clearX }
      else { s with rightTape := s.rightTape.moveLeft .blank }
  | .clearX => { s with registers := { s.registers with x := false }, phase := .clearY }
  | .clearY => { s with registers := { s.registers with y := false }, phase := .clearLeftDone }
  | .clearLeftDone => { s with registers := { s.registers with andXY := false }, phase := .clearRightDone }
  | .clearRightDone => { s with registers := { s.registers with andTC := false }, phase := .halt }

def run : Nat → State → State
  | 0, s => s
  | k + 1, s => run k (step s)

def clearScratch (r : Registers) : Registers :=
  { r with x := false, y := false, andXY := false, andTC := false }

def rows (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) : List Row :=
  (SignedWordAlignment.aligned xs sx ys sy ++ [(sx, sy), (sx, sy)]).map (fun ab => (ab, false))

def initial (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) (r : Registers) : State :=
  ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits xs),
    MarkedZeroPadding.marked (MarkedZeroPadding.bits ys), ⟨[], []⟩, r, sx, sy, .writeLeft⟩

def final (xs : List Bool) (sx : Bool) (ys : List Bool) (sy : Bool) (r : Registers) : State :=
  ⟨MarkedZeroPadding.marked (MarkedZeroPadding.bits xs),
    MarkedZeroPadding.marked (MarkedZeroPadding.bits ys), MarkedBitAddition.marked (rows xs sx ys sy),
    clearScratch r, sx, sy, .halt⟩

/-- Exact projected adder entrance. This definition alone is not an execution
or a free physical handoff; the composed controller must make that switch. -/
def adderEntrance (s : State) : MarkedBitAddition.State :=
  ⟨s.outputTape, s.registers, .enter⟩

theorem final_adder_entrance (xs : List Bool) (sx : Bool) (ys : List Bool)
    (sy : Bool) (r : Registers) :
    adderEntrance (final xs sx ys sy r) =
      MarkedBitAddition.initial (rows xs sx ys sy) (clearScratch r) := rfl


/-- Exact live transition trace; fuel and list lengths are observers only. -/
inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : s.phase ≠ .halt)
      (tail : Trace k (step s) t) : Trace (k + 1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m + n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)

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

private theorem aligned_nil (sx sy : Bool) :
    SignedWordAlignment.aligned [] sx [] sy = [] := rfl

private theorem aligned_left_cons (x : Bool) (xs : List Bool) (sx sy : Bool) :
    SignedWordAlignment.aligned (x :: xs) sx [] sy =
      (x, sy) :: SignedWordAlignment.aligned xs sx [] sy := by
  simp [SignedWordAlignment.aligned, SignedWordAlignment.extendTo,
    SignedWordAlignment.width, List.replicate_succ]

private theorem aligned_right_cons (y : Bool) (ys : List Bool) (sx sy : Bool) :
    SignedWordAlignment.aligned [] sx (y :: ys) sy =
      (sx, y) :: SignedWordAlignment.aligned [] sx ys sy := by
  simp [SignedWordAlignment.aligned, SignedWordAlignment.extendTo,
    SignedWordAlignment.width, List.replicate_succ]

private theorem aligned_cons (x y : Bool) (xs ys : List Bool) (sx sy : Bool) :
    SignedWordAlignment.aligned (x :: xs) sx (y :: ys) sy =
      (x, y) :: SignedWordAlignment.aligned xs sx ys sy := by
  simp [SignedWordAlignment.aligned, SignedWordAlignment.extendTo,
    SignedWordAlignment.width, Nat.succ_max_succ]

def bitSymbols (xs : List Bool) : List BitSymbol := xs.map MarkedZeroPadding.Symbol.data

def rowSymbols (ps : List (Bool × Bool)) : List RowSymbol :=
  ps.map (fun p => MarkedBitAddition.Symbol.data (p, false))

def loaded (r : Registers) (x y dx dy : Bool) : Registers :=
  { r with x := x, y := y, andXY := dx, andTC := dy }

/-- Histories are reversed; remaining source words are at the heads. -/
def scanState (r : Registers) (sx sy : Bool) (lx xs ly ys : List Bool)
    (os : List (Bool × Bool)) : State :=
  ⟨⟨bitSymbols lx ++ [.leftMarker], bitSymbols xs ++ [.rightMarker]⟩,
    ⟨bitSymbols ly ++ [.leftMarker], bitSymbols ys ++ [.rightMarker]⟩,
    ⟨rowSymbols os ++ [.leftMarker], []⟩, r, sx, sy, .readLeft⟩

private theorem scan_both (r : Registers) (sx sy x y : Bool)
    (lx xs ly ys : List Bool) (os : List (Bool × Bool)) :
    Trace 7 (scanState r sx sy lx (x :: xs) ly (y :: ys) os)
      (scanState (loaded r x y false false) sx sy (x :: lx) xs (y :: ly) ys ((x,y) :: os)) := by
  iterate 7 apply Trace.next (by simp [scanState, step, Tape.readHead, Tape.writeHead,
    Tape.moveRight, bitSymbols, rowSymbols, loaded])
  simpa [scanState, step, Tape.readHead, Tape.writeHead, Tape.moveRight,
    bitSymbols, rowSymbols, loaded] using Trace.nil
      (scanState (loaded r x y false false) sx sy (x :: lx) xs (y :: ly) ys ((x,y) :: os))

private theorem scan_left (r : Registers) (sx sy x : Bool)
    (lx xs ly : List Bool) (os : List (Bool × Bool)) :
    Trace 7 (scanState r sx sy lx (x :: xs) ly [] os)
      (scanState (loaded r x sy false true) sx sy (x :: lx) xs ly [] ((x,sy) :: os)) := by
  iterate 7 apply Trace.next (by simp [scanState, step, Tape.readHead, Tape.writeHead,
    Tape.moveRight, bitSymbols, rowSymbols, loaded])
  simpa [scanState, step, Tape.readHead, Tape.writeHead, Tape.moveRight,
    bitSymbols, rowSymbols, loaded] using Trace.nil
      (scanState (loaded r x sy false true) sx sy (x :: lx) xs ly [] ((x,sy) :: os))

private theorem scan_right (r : Registers) (sx sy y : Bool)
    (lx ly ys : List Bool) (os : List (Bool × Bool)) :
    Trace 7 (scanState r sx sy lx [] ly (y :: ys) os)
      (scanState (loaded r sx y true false) sx sy lx [] (y :: ly) ys ((sx,y) :: os)) := by
  iterate 7 apply Trace.next (by simp [scanState, step, Tape.readHead, Tape.writeHead,
    Tape.moveRight, bitSymbols, rowSymbols, loaded])
  simpa [scanState, step, Tape.readHead, Tape.writeHead, Tape.moveRight,
    bitSymbols, rowSymbols, loaded] using Trace.nil
      (scanState (loaded r sx y true false) sx sy lx [] (y :: ly) ys ((sx,y) :: os))

private theorem scan_empty (r : Registers) (sx sy : Bool)
    (lx ly : List Bool) (os : List (Bool × Bool)) :
    Trace 3 (scanState r sx sy lx [] ly [] os)
      { scanState (loaded r sx sy true true) sx sy lx [] ly [] os with phase := .writeSignOne } := by
  iterate 3 apply Trace.next (by simp [scanState, step, Tape.readHead, bitSymbols])
  simpa [scanState, step, Tape.readHead, bitSymbols, loaded] using Trace.nil
    { scanState (loaded r sx sy true true) sx sy lx [] ly [] os with phase := .writeSignOne }

private theorem scan_words (xs ys : List Bool) (r : Registers) (sx sy : Bool)
    (lx ly : List Bool) (os : List (Bool × Bool)) :
    Trace (7 * max xs.length ys.length + 3) (scanState r sx sy lx xs ly ys os)
      { scanState (loaded r sx sy true true) sx sy (xs.reverse ++ lx) []
          (ys.reverse ++ ly) [] ((SignedWordAlignment.aligned xs sx ys sy).reverse ++ os)
        with phase := .writeSignOne } := by
  induction xs generalizing ys r lx ly os with
  | nil =>
      induction ys generalizing r ly os with
      | nil => simpa [aligned_nil] using scan_empty r sx sy lx ly os
      | cons y ys ih =>
          have h := trace_trans (scan_right r sx sy y lx ly ys os)
            (ih (loaded r sx y true false) (y :: ly) ((sx,y) :: os))
          have hc : 7 + (7 * max 0 ys.length + 3) = 7 * max 0 (y :: ys).length + 3 := by
            simp only [List.length_cons, Nat.zero_max]; omega
          simp only [List.length_nil] at h
          rw [hc] at h
          simpa [aligned_right_cons, List.reverse_cons, List.append_assoc, loaded,
            scanState] using h
  | cons x xs ih =>
      cases ys with
      | nil =>
          have h := trace_trans (scan_left r sx sy x lx xs ly os)
            (ih [] (loaded r x sy false true) (x :: lx) ly ((x,sy) :: os))
          have hc : 7 + (7 * max xs.length 0 + 3) = 7 * max (x :: xs).length 0 + 3 := by
            simp only [List.length_cons, Nat.max_zero]; omega
          simp only [List.length_nil] at h
          rw [hc] at h
          simpa [aligned_left_cons, List.reverse_cons, List.append_assoc, loaded,
            scanState] using h
      | cons y ys =>
          have h := trace_trans (scan_both r sx sy x y lx xs ly ys os)
            (ih ys (loaded r x y false false) (x :: lx) (y :: ly) ((x,y) :: os))
          have hc : 7 + (7 * max xs.length ys.length + 3) =
              7 * max (x :: xs).length (y :: ys).length + 3 := by
            simp only [List.length_cons, Nat.succ_max_succ]; omega
          rw [hc] at h
          simpa [aligned_cons, List.reverse_cons, List.append_assoc, loaded,
            scanState] using h

private theorem rewind_output (base : State) (ls rs : List RowSymbol)
    (hls : ∀ a ∈ ls, a ≠ .leftMarker)
    (hrs : (⟨[], rs⟩ : Tape RowSymbol).readHead .blank ≠ .leftMarker) :
    Trace (ls.length + 2)
      { base with outputTape := ⟨ls ++ [.leftMarker], rs⟩, phase := .rewindOutput }
      { base with outputTape := ⟨[], .leftMarker :: (ls.reverse ++ rs)⟩, phase := .rewindLeft } := by
  revert hls hrs
  induction ls generalizing rs with
  | nil =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp)
      simp [step, Tape.moveLeft, Tape.readHead]
      exact Trace.nil _
  | cons a ls ih =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      have h := ih (a :: rs)
        (by intro b hb; exact hls b (by simp [hb]))
        (by simpa [Tape.readHead] using hls a (by simp))
      simpa [Tape.moveLeft, List.reverse_cons, List.append_assoc] using h

private theorem rewind_left (base : State) (ls rs : List BitSymbol)
    (hls : ∀ a ∈ ls, a ≠ .leftMarker)
    (hrs : (⟨[], rs⟩ : Tape BitSymbol).readHead .blank ≠ .leftMarker) :
    Trace (ls.length + 2)
      { base with leftTape := ⟨ls ++ [.leftMarker], rs⟩, phase := .rewindLeft }
      { base with leftTape := ⟨[], .leftMarker :: (ls.reverse ++ rs)⟩, phase := .rewindRight } := by
  revert hls hrs
  induction ls generalizing rs with
  | nil =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp)
      simp [step, Tape.moveLeft, Tape.readHead]
      exact Trace.nil _
  | cons a ls ih =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      have h := ih (a :: rs)
        (by intro b hb; exact hls b (by simp [hb]))
        (by simpa [Tape.readHead] using hls a (by simp))
      simpa [Tape.moveLeft, List.reverse_cons, List.append_assoc] using h

private theorem rewind_right (base : State) (ls rs : List BitSymbol)
    (hls : ∀ a ∈ ls, a ≠ .leftMarker)
    (hrs : (⟨[], rs⟩ : Tape BitSymbol).readHead .blank ≠ .leftMarker) :
    Trace (ls.length + 2)
      { base with rightTape := ⟨ls ++ [.leftMarker], rs⟩, phase := .rewindRight }
      { base with rightTape := ⟨[], .leftMarker :: (ls.reverse ++ rs)⟩, phase := .clearX } := by
  revert hls hrs
  induction ls generalizing rs with
  | nil =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      apply Trace.next (by simp)
      simp [step, Tape.moveLeft, Tape.readHead]
      exact Trace.nil _
  | cons a ls ih =>
      intro hls hrs
      apply Trace.next (by simp)
      simp only [step, Tape.readHead] at hrs ⊢
      rw [if_neg hrs]
      have h := ih (a :: rs)
        (by intro b hb; exact hls b (by simp [hb]))
        (by simpa [Tape.readHead] using hls a (by simp))
      simpa [Tape.moveLeft, List.reverse_cons, List.append_assoc] using h

private theorem no_left_bits (xs : List Bool) :
    ∀ a ∈ bitSymbols xs, a ≠ MarkedZeroPadding.Symbol.leftMarker := by
  intro a ha
  obtain ⟨b, _, rfl⟩ := List.mem_map.mp ha
  simp

private theorem no_left_rows (ps : List (Bool × Bool)) :
    ∀ a ∈ rowSymbols ps, a ≠ MarkedBitAddition.Symbol.leftMarker := by
  intro a ha
  obtain ⟨b, _, rfl⟩ := List.mem_map.mp ha
  simp

/-- Completed physical layout for an arbitrary already-emitted pair word. -/
def completed (r : Registers) (sx sy : Bool) (xs ys : List Bool)
    (ps : List (Bool × Bool)) : State :=
  ⟨MarkedZeroPadding.marked (bitSymbols xs), MarkedZeroPadding.marked (bitSymbols ys),
    ⟨[], .leftMarker :: rowSymbols (ps ++ [(sx,sy),(sx,sy)]) ++ [.rightMarker]⟩,
    clearScratch r, sx, sy, .halt⟩

private theorem finish (r : Registers) (sx sy : Bool) (xs ys : List Bool)
    (ps : List (Bool × Bool)) :
    Trace (ps.length + xs.length + ys.length + 17)
      { scanState r sx sy xs.reverse [] ys.reverse [] ps.reverse with phase := .writeSignOne }
      (completed r sx sy xs ys ps) := by
  let ss := (sx, sy)
  let out := ps ++ [ss, ss]
  let before : State :=
    { scanState r sx sy xs.reverse [] ys.reverse [] ps.reverse with phase := .writeSignOne }
  let written : State :=
    { before with outputTape := ⟨(rowSymbols out).reverse ++ [.leftMarker], [.rightMarker]⟩, phase := .rewindOutput }
  have hw : Trace 5 before written := by
    iterate 5 apply Trace.next (by simp [before, scanState, step, Tape.writeHead, Tape.moveRight])
    simpa [before, written, out, ss, scanState, step, Tape.writeHead, Tape.moveRight,
      rowSymbols, List.reverse_append, List.map_append, List.reverse_cons,
      List.append_assoc] using Trace.nil written
  have ho := rewind_output written (rowSymbols out).reverse [.rightMarker]
    (by simpa using no_left_rows out) (by simp [Tape.readHead])
  let so : State := { written with
    outputTape := ⟨[], .leftMarker :: rowSymbols out ++ [.rightMarker]⟩, phase := .rewindLeft }
  have ho' : Trace ((rowSymbols out).length + 2) written so := by
    simpa [written, so] using ho
  have hl := rewind_left so (bitSymbols xs).reverse [.rightMarker]
    (by simpa using no_left_bits xs) (by simp [Tape.readHead])
  let sl : State := { so with leftTape := MarkedZeroPadding.marked (bitSymbols xs), phase := .rewindRight }
  have hl' : Trace ((bitSymbols xs).length + 2) so sl := by
    simpa [sl, so, written, before, scanState, MarkedZeroPadding.marked,
      bitSymbols, List.map_reverse] using hl
  have hr := rewind_right sl (bitSymbols ys).reverse [.rightMarker]
    (by simpa using no_left_bits ys) (by simp [Tape.readHead])
  let sr : State := { sl with rightTape := MarkedZeroPadding.marked (bitSymbols ys), phase := .clearX }
  have hr' : Trace ((bitSymbols ys).length + 2) sl sr := by
    simpa [sr, sl, so, written, before, scanState, MarkedZeroPadding.marked,
      bitSymbols, List.map_reverse] using hr
  have hc : Trace 4 sr (completed r sx sy xs ys ps) := by
    iterate 4 apply Trace.next (by simp [sr, sl, so, step])
    simpa [sr, sl, so, written, before, scanState, step, completed, clearScratch, out, ss] using
      Trace.nil (completed r sx sy xs ys ps)
  have h := trace_trans (trace_trans (trace_trans (trace_trans hw ho') hl') hr') hc
  have he : 5 + ((rowSymbols out).length + 2) + ((bitSymbols xs).length + 2) +
      ((bitSymbols ys).length + 2) + 4 = ps.length + xs.length + ys.length + 17 := by
    simp only [rowSymbols, bitSymbols, out, List.length_map, List.length_append,
      List.length_cons, List.length_nil]; omega
  rw [he] at h
  exact h

private theorem setup (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    Trace 4 (initial xs sx ys sy r) (scanState r sx sy [] xs [] ys []) := by
  iterate 4 apply Trace.next (by simp [initial, step])
  simpa [initial, scanState, step, MarkedZeroPadding.marked, MarkedZeroPadding.bits,
    Tape.writeHead, Tape.moveRight, rowSymbols, bitSymbols] using
      Trace.nil (scanState r sx sy [] xs [] ys [])

/-- Paid pairing, unequal-width sign extension, both sign columns and both
output markers, with source preservation, all heads returned and four scratch
bits cleared. No output-ready premise or length oracle is used. -/
theorem layout_exact (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    Trace (8 * max xs.length ys.length + xs.length + ys.length + 24)
      (initial xs sx ys sy r) (final xs sx ys sy r) := by
  have hscan := scan_words xs ys r sx sy [] [] []
  have hfinish := finish (loaded r sx sy true true) sx sy xs ys
    (SignedWordAlignment.aligned xs sx ys sy)
  have hscan' : Trace (7 * max xs.length ys.length + 3) (scanState r sx sy [] xs [] ys [])
      { scanState (loaded r sx sy true true) sx sy xs.reverse [] ys.reverse []
        (SignedWordAlignment.aligned xs sx ys sy).reverse with phase := .writeSignOne } := by
    simpa using hscan
  have h := trace_trans (trace_trans (setup xs ys sx sy r) hscan') hfinish
  have he : 4 + (7 * max xs.length ys.length + 3) +
      ((SignedWordAlignment.aligned xs sx ys sy).length + xs.length + ys.length + 17) =
      8 * max xs.length ys.length + xs.length + ys.length + 24 := by
    rw [SignedWordAlignment.aligned_length]
    simp only [SignedWordAlignment.width]; omega
  rw [he] at h
  simpa [completed, final, rows, loaded, clearScratch, bitSymbols, MarkedZeroPadding.bits,
    MarkedBitAddition.marked, rowSymbols, List.map_map] using h

theorem layout_result (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    run (8 * max xs.length ys.length + xs.length + ys.length + 24)
      (initial xs sx ys sy r) = final xs sx ys sy r := trace_sound (layout_exact xs ys sx sy r)

theorem layout_first_halt (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    (run (8 * max xs.length ys.length + xs.length + ys.length + 24)
      (initial xs sx ys sy r)).phase = .halt ∧
    ∀ k < 8 * max xs.length ys.length + xs.length + ys.length + 24,
      (run k (initial xs sx ys sy r)).phase ≠ .halt := by
  constructor
  · rw [layout_result]; rfl
  · exact trace_live (layout_exact xs ys sx sy r)

def tapeCells {α : Type} (t : Tape α) : Nat := t.left.length + t.right.length

def cells (s : State) : Nat :=
  tapeCells s.leftTape + tapeCells s.rightTape + tapeCells s.outputTape

private theorem write_cells {α : Type} (t : Tape α) (a : α) :
    tapeCells t ≤ tapeCells (t.writeHead a) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.writeHead]

private theorem right_cells {α : Type} (t : Tape α) (blank : α) :
    tapeCells t ≤ tapeCells (t.moveRight blank) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.moveRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem left_cells {α : Type} (t : Tape α) (blank : α) :
    tapeCells t ≤ tapeCells (t.moveLeft blank) := by
  rcases t with ⟨ls, rs⟩
  cases ls <;> simp [tapeCells, Tape.moveLeft, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem step_cells (s : State) : cells s ≤ cells (step s) := by
  have hwL := write_cells s.outputTape MarkedBitAddition.Symbol.leftMarker
  have hwR := write_cells s.outputTape MarkedBitAddition.Symbol.rightMarker
  have hwD := write_cells s.outputTape (MarkedBitAddition.Symbol.data ((s.registers.x,s.registers.y),false))
  have hwS := write_cells s.outputTape (MarkedBitAddition.Symbol.data ((s.leftSign,s.rightSign),false))
  have hxl := left_cells s.leftTape MarkedZeroPadding.Symbol.blank
  have hxr := right_cells s.leftTape MarkedZeroPadding.Symbol.blank
  have hyl := left_cells s.rightTape MarkedZeroPadding.Symbol.blank
  have hyr := right_cells s.rightTape MarkedZeroPadding.Symbol.blank
  have hol := left_cells s.outputTape MarkedBitAddition.Symbol.blank
  have hor := right_cells s.outputTape MarkedBitAddition.Symbol.blank
  cases hp : s.phase <;> simp only [step, hp]
  all_goals (repeat' split) <;> simp only [cells] at * <;> omega

private theorem trace_storage {n : Nat} {s t : State} (h : Trace n s t)
    (ht : t.phase = .halt) (k : Nat) : cells (run k s) ≤ cells t := by
  induction h generalizing k with
  | nil s => rw [halt_run s ht]
  | @next n s t live tail ih =>
      cases k with
      | zero => exact (step_cells s).trans (ih ht 0)
      | succ k => exact ih ht k

/-- All three represented tapes, including the newly written L/R and two
sign columns. Seven Boolean registers, two signs and finite control are extra. -/
theorem layout_prefix_storage (xs ys : List Bool) (sx sy : Bool) (r : Registers) (k : Nat) :
    cells (run k (initial xs sx ys sy r)) ≤
      xs.length + ys.length + max xs.length ys.length + 8 := by
  have h := trace_storage (layout_exact xs ys sx sy r) (by rfl) k
  simpa [cells, tapeCells, final, rows, MarkedZeroPadding.marked, MarkedZeroPadding.bits,
    MarkedBitAddition.marked, SignedWordAlignment.aligned_length, SignedWordAlignment.width,
    Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h

/-- No assumption that the output already exists: its allocation grows from
zero to max(input lengths)+4, including both explicit sign rows and markers. -/
theorem layout_output_allocation (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    tapeCells (initial xs sx ys sy r).outputTape = 0 ∧
    tapeCells (run (8 * max xs.length ys.length + xs.length + ys.length + 24)
      (initial xs sx ys sy r)).outputTape = max xs.length ys.length + 4 := by
  constructor
  · rfl
  · rw [layout_result]
    simp [tapeCells, final, rows, MarkedBitAddition.marked,
      SignedWordAlignment.aligned_length, SignedWordAlignment.width, Nat.add_assoc]

/-- The produced output and preserved register bank meet the actual accepted
marked-adder entrance exactly. The equation prices the layout construction;
a sequential controller's phase handoff is a separate one-step refinement. -/
theorem layout_adder_entrance (xs ys : List Bool) (sx sy : Bool) (r : Registers) :
    adderEntrance (run (8 * max xs.length ys.length + xs.length + ys.length + 24)
      (initial xs sx ys sy r)) = MarkedBitAddition.initial (rows xs sx ys sy) (clearScratch r) := by
  rw [layout_result, final_adder_entrance]

end MarkedPairLayout

#print axioms MarkedPairLayout.final_adder_entrance
#print axioms MarkedPairLayout.layout_exact
#print axioms MarkedPairLayout.layout_result
#print axioms MarkedPairLayout.layout_first_halt
#print axioms MarkedPairLayout.step_cells
#print axioms MarkedPairLayout.layout_prefix_storage
#print axioms MarkedPairLayout.layout_output_allocation
#print axioms MarkedPairLayout.layout_adder_entrance
#check @MarkedPairLayout.layout_exact
#check @MarkedPairLayout.layout_prefix_storage

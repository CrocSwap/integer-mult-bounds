import MarkedBitXorScan
import DyadicAddExponentCleanup

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

A strict marked-word decoder connects the accepted finite Boolean XOR scan to
the existing exponent metadata instruction. Input rows are actual paired bits,
not a unit-cost Nat XOR or a width oracle. The complete marked execution and
its 5w+4 transitions / w+2 cells are imported unchanged. Equal restored
exponents imply that every target bit is literally false at the endpoint.

BoundaryState's other fields are immutable parameters of this projection,
not newly implemented physical storage. Paid width selection, encoding/pairing,
ambient-state framing, and arbitrary dirty auxiliary scratch remain separate.
The scan entrance requires its own one Boolean scratch to be false.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.ExponentMetadataBitAdapter
open PairedBitXorScan (Pair Tape value xorPair)
open DyadicAddExponentCleanup (BoundaryState)

/-- Strict tail parser: exactly one final R, data pairs only before it.
This is a semantic observer, not a priced execution or layout constructor. -/
def parseTail : List MarkedBitXorScan.Symbol → Option (List Pair)
  | [.rightMarker] => some []
  | .data a b :: rest => (parseTail rest).map ((a, b) :: ·)
  | _ => none

/-- Only a returned head at an actual L marker is decoded. -/
def readTape (t : Tape MarkedBitXorScan.Symbol) : Option (List Pair) :=
  match t.left, t.right with
  | [], .leftMarker :: rest => parseTail rest
  | _, _ => none

private theorem parse_data (rows : List Pair) :
    parseTail (rows.map MarkedBitXorScan.dataSymbol ++ [.rightMarker]) = some rows := by
  induction rows with
  | nil => rfl
  | cons row rows ih =>
      rcases row with ⟨a, b⟩
      simp [MarkedBitXorScan.dataSymbol, parseTail, ih]

theorem read_marked (rows : List Pair) :
    readTape ⟨[], MarkedBitXorScan.marked rows⟩ = some rows := by
  simpa only [readTape, MarkedBitXorScan.marked] using parse_data rows

/-- The first track stores saved exponent bits; the second stores the current
restored target exponent. Other fields are parameters of the semantic view. -/
def view (base : BoundaryState) (rows : List Pair) : BoundaryState :=
  { base with
    target := { base.target with fractionalBits := value (rows.map Prod.snd) }
    savedExponent := value (rows.map Prod.fst) }

def Matches (base : BoundaryState) (rows : List Pair) : Prop :=
  value (rows.map Prod.fst) = base.savedExponent ∧
    value (rows.map Prod.snd) = base.target.fractionalBits

private theorem view_matches (base : BoundaryState) (rows : List Pair)
    (h : Matches base rows) : view base rows = base := by
  rcases base with ⟨⟨z, p⟩, source, accumulator, saved⟩
  rcases h with ⟨ha, hb⟩
  simp only [view] at *
  rw [ha, hb]

/-- Direct reuse of decoded XOR and unchanged source track; no desired
endpoint equation is supplied as a premise. -/
theorem view_toggle (base : BoundaryState) (rows : List Pair) :
    view base (rows.map xorPair) =
      DyadicAddExponentCleanup.step .toggleExponent (view base rows) := by
  simp only [view, PairedBitXorScan.source_preserved,
    PairedBitXorScan.value_xor, DyadicAddExponentCleanup.step]

def observe (base : BoundaryState) (t : Tape MarkedBitXorScan.Symbol) :
    Option BoundaryState := (readTape t).map (view base)

private theorem observe_final (base : BoundaryState) (rows : List Pair) :
    observe base (MarkedBitXorScan.final rows).tape = some (view base rows) := by
  simp only [observe, MarkedBitXorScan.final, read_marked, Option.map_some]

/-- The actual finite-symbol execution implements the previously abstract
metadata XOR on the two represented exponent fields. -/
theorem scan_refines_toggle (base : BoundaryState) (rows : List Pair)
    (h : Matches base rows) :
    observe base (MarkedBitXorScan.run (5 * rows.length + 4)
      (MarkedBitXorScan.initial rows)).tape =
        some (DyadicAddExponentCleanup.step .toggleExponent base) := by
  rw [MarkedBitXorScan.marked_scan_result, observe_final, view_toggle,
    view_matches base rows h]

/-- Exact zero decoding forces every finite target bit to be false, including
leading zero slots. No canonical-width or leading-one premise is needed. -/
private theorem zero_word (bits : List Bool) (h : value bits = 0) :
    bits = List.replicate bits.length false := by
  revert h
  induction bits with
  | nil => intro _; rfl
  | cons bit bits ih =>
      intro h
      cases bit with
      | false =>
          have ht : value bits = 0 := by simpa [value] using h
          simpa [List.replicate_succ] using congrArg (false :: ·) (ih ht)
      | true => simp [value] at h

/-- Numeric equality after raw Cell restoration yields literal all-zero
metadata bits, not just an assumed cleanup predicate. -/
theorem xor_targets_clear (rows : List Pair)
    (h : value (rows.map Prod.fst) = value (rows.map Prod.snd)) :
    (rows.map xorPair).map Prod.fst = List.replicate rows.length false := by
  have hz : value ((rows.map xorPair).map Prod.fst) = 0 := by
    rw [PairedBitXorScan.value_xor, h, Nat.xor_self]
  simpa only [List.length_map] using zero_word ((rows.map xorPair).map Prod.fst) hz

/-- Strict decoding of the actual halted tape exposes both cleared target
cells and unchanged current-exponent source bits. -/
theorem scan_clears_restored (base : BoundaryState) (rows : List Pair)
    (h : Matches base rows) (hrestored : base.savedExponent = base.target.fractionalBits) :
    ∃ out : List Pair,
      readTape (MarkedBitXorScan.run (5 * rows.length + 4)
        (MarkedBitXorScan.initial rows)).tape = some out ∧
      out.map Prod.fst = List.replicate rows.length false ∧
      out.map Prod.snd = rows.map Prod.snd := by
  refine ⟨rows.map xorPair, ?_, ?_, PairedBitXorScan.source_preserved rows⟩
  · rw [MarkedBitXorScan.marked_scan_result]
    exact read_marked _
  · apply xor_targets_clear
    exact h.1.trans (hrestored.trans h.2.symm)

/-- The exact inherited first-halt and every-prefix storage invoices are
attached to the semantic refinement, with no free encoding/pairing step. -/
theorem scan_resources (base : BoundaryState) (rows : List Pair)
    (h : Matches base rows) :
    MarkedBitXorScan.RunsToHalt (5 * rows.length + 4)
      (MarkedBitXorScan.initial rows) (MarkedBitXorScan.final (rows.map xorPair)) ∧
    observe base (MarkedBitXorScan.run (5 * rows.length + 4)
      (MarkedBitXorScan.initial rows)).tape =
        some (DyadicAddExponentCleanup.step .toggleExponent base) ∧
    ∀ k, MarkedBitXorScan.cells
      (MarkedBitXorScan.run k (MarkedBitXorScan.initial rows)) = rows.length + 2 :=
  ⟨MarkedBitXorScan.marked_scan_exact rows, scan_refines_toggle base rows h,
    MarkedBitXorScan.marked_scan_storage rows⟩

end CurrentMain.ExponentMetadataBitAdapter

#print axioms CurrentMain.ExponentMetadataBitAdapter.read_marked
#print axioms CurrentMain.ExponentMetadataBitAdapter.view_toggle
#print axioms CurrentMain.ExponentMetadataBitAdapter.scan_refines_toggle
#print axioms CurrentMain.ExponentMetadataBitAdapter.xor_targets_clear
#print axioms CurrentMain.ExponentMetadataBitAdapter.scan_clears_restored
#print axioms CurrentMain.ExponentMetadataBitAdapter.scan_resources
#check @CurrentMain.ExponentMetadataBitAdapter.scan_clears_restored
#check @CurrentMain.ExponentMetadataBitAdapter.scan_resources

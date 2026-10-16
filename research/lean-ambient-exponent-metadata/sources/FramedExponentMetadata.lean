import MarkedXorFraming
import ExponentMetadataBitAdapter

/-!
Ambient marked-segment consequences for the accepted exponent metadata adapter.
The strict readTape decoder remains unchanged and is used only on the explicit
local segment witness. Ambient spectators are not fed to that decoder. Actual
framed execution supplies the segment relation, exact returned head and literal
cleared bits; no desired endpoint is assumed. Width selection, paired encoding,
segment installation and Nat-address slot layout remain explicit caller work.
James Chang with OpenAI assistance; Apache-2.0. Reuses the accepted marked XOR
and metadata interpretation. Pinned conditional context only:
kappa=836330098538459/500000000000000000. Uncompiled candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.FramedExponentMetadata
open PairedBitXorScan (Pair Tape xorPair)
open MarkedBitXorScan
open ExponentMetadataBitAdapter
open DyadicAddExponentCleanup (BoundaryState)

/-- Semantic segment observation with the supplied contexts. This is not a
new ambient parser or a priced boundary-search operation. -/
def Observes (left right : List Symbol) (base : BoundaryState)
    (ambient : Tape Symbol) (out : BoundaryState) : Prop :=
  ∃ segment : Tape Symbol,
    ambient = ⟨segment.left ++ left, segment.right ++ right⟩ ∧
      observe base segment = some out

/-- The real framed scan implements the old metadata toggle on its represented
fields and preserves the complete local/ambient segment relation. -/
theorem framed_toggle (left right : List Symbol) (base : BoundaryState)
    (rows : List Pair) (h : Matches base rows) :
    Observes left right base
      (run (5 * rows.length + 4) (MarkedXorFraming.embed left right (initial rows))).tape
      (DyadicAddExponentCleanup.step .toggleExponent base) := by
  refine ⟨(run (5 * rows.length + 4) (initial rows)).tape, ?_, scan_refines_toggle base rows h⟩
  rw [MarkedXorFraming.framed_scan_result, marked_scan_result]
  rfl

/-- Equality of the represented restored exponents yields literal zero target
bits in the actual framed endpoint, with source bits and spectators retained. -/
theorem framed_clear (left right : List Symbol) (base : BoundaryState)
    (rows : List Pair) (h : Matches base rows)
    (hrestored : base.savedExponent = base.target.fractionalBits) :
    ∃ out : List Pair,
      run (5 * rows.length + 4) (MarkedXorFraming.embed left right (initial rows)) =
        ⟨⟨left, marked out ++ right⟩, false, .halt⟩ ∧
      out.map Prod.fst = List.replicate rows.length false ∧
      out.map Prod.snd = rows.map Prod.snd := by
  refine ⟨rows.map xorPair, ?_, ?_, PairedBitXorScan.source_preserved rows⟩
  · rw [MarkedXorFraming.framed_scan_result]
    rfl
  · exact xor_targets_clear rows (h.1.trans (hrestored.trans h.2.symm))

end CurrentMain.FramedExponentMetadata
#print axioms CurrentMain.FramedExponentMetadata.framed_toggle
#print axioms CurrentMain.FramedExponentMetadata.framed_clear
#check @CurrentMain.FramedExponentMetadata.framed_toggle
#check @CurrentMain.FramedExponentMetadata.framed_clear

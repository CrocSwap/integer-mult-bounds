import Current1094CallSequenceRouting
import Current1094CallHelperRuns
import StructuralOwnerCertificate

/-!
Shared exact owner-row interface for bounded block certificates after the
single all144 kernel predicate reached its 3.5GiB review threshold.
Every decoder, bounded lookup, RowOK and structural SortedRowOK clause below
is copied byte-for-byte from the preserved all144 candidate. Only proof
partitioning changes. No row is omitted: Fin36 x Fin4 covers Fin144 through
the explicit div/mod inverse proved here. A final certificate must supply
every one of those 36 block theorems; this generic join assumes none silently.

This module deliberately owns the same namespace as the rejected monolithic
source and must never be loaded alongside a later object of that source.
Selected PR1094 context kappa=836330098538459/500000000000000000;
physical projection, charts, actual executor and precision remain separate.
Preserve Rohan Arun PR1094, Jeremy Kothe T16, Hao Yan PR514/484/507,
columbia-git PR1553, DreamingOfClouds realization and Lean library credits.
Apache-2.0; prepared with OpenAI assistance. Source-only, uncompiled.
-/
set_option Elab.async false
namespace CurrentMain.Current1094CallSequenceHelpersStructural
open Current1094CallSequenceRouting

/-- Saturating Nat subtraction is explicit. The source generator separately
checks that every emitted run is nonempty and never underflows. -/
def decodeRun (r : Nat × Nat) : List Nat :=
  (List.range r.2).map (fun i => r.1 - i)

private theorem encoded_length : Current1094CallHelperRuns.encoded.length = 144 := by
  decide +kernel

def helperNats (c : Fin 144) : List Nat :=
  (Current1094CallHelperRuns.encoded[c.val]'(by
    simpa only [encoded_length] using c.isLt)).flatMap decodeRun

/-- Each clause is a genuine proposed finite obligation over the exact decoded row. -/
def RowOK (c : Fin 144) : Prop :=
  (helperNats c).length = 480 ∧
    (∀ f ∈ helperNats c, f < 14336) ∧
    (helperNats c).Nodup ∧
    (∀ f ∈ helperNats c, f < dataBase c ∨ dataBase c + 224 ≤ f)

/-- Same length, range and active-interval exclusion as RowOK. Only the
duplicate check uses sorting plus a linear adjacent scan. -/
def SortedRowOK (c : Fin 144) : Prop :=
  (helperNats c).length = 480 ∧
    (∀ f ∈ helperNats c, f < 14336) ∧
    SortedOwnerCertificate.strictAdjacent
      (StructuralOwnerCertificate.structuralSort (helperNats c)) = true ∧
    (∀ f ∈ helperNats c, f < dataBase c ∨ dataBase c + 224 ≤ f)

/-- The fixed block layout covers all 144 calls with four consecutive rows. -/
def blockRow (block : Fin 36) (offset : Fin 4) : Fin 144 :=
  ⟨4 * block.val + offset.val, by
    have hb := block.isLt
    have hi := offset.isLt
    omega⟩

theorem blockRow_decompose (c : Fin 144) :
    ∃ block : Fin 36, ∃ offset : Fin 4, blockRow block offset = c := by
  let block : Fin 36 := ⟨c.val / 4, by have hc := c.isLt; omega⟩
  let offset : Fin 4 := ⟨c.val % 4, by omega⟩
  refine ⟨block, offset, ?_⟩
  apply Fin.ext
  change 4 * (c.val / 4) + c.val % 4 = c.val
  omega

/-- This theorem is conditional on every block, with no missing-row default. -/
theorem sorted_all_of_blocks
    (hblocks : ∀ block : Fin 36, ∀ offset : Fin 4,
      SortedRowOK (blockRow block offset)) :
    ∀ c : Fin 144, SortedRowOK c := by
  intro c
  obtain ⟨block, offset, hrow⟩ := blockRow_decompose c
  simpa only [hrow] using hblocks block offset

theorem rowOK_of_sorted (c : Fin 144) (h : SortedRowOK c) : RowOK c := by
  obtain ⟨hlen, hrange, hsorted, houtside⟩ := h
  exact ⟨hlen, hrange,
    StructuralOwnerCertificate.nodup_of_structural_scan _ hsorted, houtside⟩

end CurrentMain.Current1094CallSequenceHelpersStructural
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.blockRow_decompose
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.sorted_all_of_blocks
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.rowOK_of_sorted

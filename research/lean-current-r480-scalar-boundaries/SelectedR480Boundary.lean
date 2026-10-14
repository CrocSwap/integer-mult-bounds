import SelectedBitCarrierPhaseBCheck

/-! Exact R480 boundary for the selected7dfa22b snapshot. The B/scatter/frame
literals are byte-equal to the accepted R489 source projection; the bound,
retained IDs and endpoint lengths are new. This is a raw domain certificate.
No rank, label chronology, physical transport or A/C/D semantics is inferred.
Supplier eumemic, with Anthropic Claude assistance; Apache-2.0.
Finite adaptation and proofs prepared with OpenAI assistance. -/
namespace CurrentMain.SelectedR480Boundary
namespace Data
abbrev h := SelectedBitCarrierBoundary.Data.h
abbrev v := SelectedBitCarrierBoundary.Data.v
def R : Nat := 480
def registers : Nat := 2*v+R
abbrev format := SelectedBitCarrierBoundary.Data.format
abbrev form := SelectedBitCarrierBoundary.Data.form
abbrev lines := SelectedBitCarrierBoundary.Data.lines
abbrev frames := SelectedBitCarrierBoundary.Data.frames
def start : List Nat := SelectedBitCarrierBoundary.Data.start.take 720
def final : List Nat := SelectedBitCarrierBoundary.Data.final.take 720
def ret : List Nat := [701,682,693,700,661,695,717,675,706]
def phaseB := SelectedBitCarrierPhaseB.Data.phaseB
abbrev scatter := SelectedBitCarrierPhaseB.Data.scatter
end Data
namespace Boundary
abbrev v := Data.v
abbrev registers := Data.registers
abbrev ret := Data.ret
end Boundary
open Data
set_option Elab.async false

theorem selected_shape :
    h = 8 ∧ v = 120 ∧ R = 480 ∧ registers = 720 ∧
    format = "bitE8/1+mut" ∧ form = "<x,y>/2" := by decide +kernel

theorem line_shape :
    lines.length = 120 ∧ lines.all (fun row => row.length == 8) = true :=
  SelectedBitCarrierBoundary.line_shape

theorem frame_domain :
    frames.length = 672 ∧
    frames.all (fun row => row.all (fun i => decide (i < 120))) = true :=
  SelectedBitCarrierBoundary.frame_domain

theorem boundary_domain :
    start.length = 720 ∧ final.length = 720 ∧
    start.all (fun f => decide (f < 672)) = true ∧
    final.all (fun f => decide (f < 672)) = true := by decide +kernel

theorem zero_full_rows :
    frames[0]? = some [] ∧ frames[1]? = some (List.range 120) :=
  SelectedBitCarrierBoundary.zero_full_rows

theorem source_entrances :
    (List.range 120).all (fun r =>
      match start[r]? with
      | none => false
      | some f => frames[f]? == some [r]) = true := by decide +kernel

theorem nonsource_entrances : start.drop 120 = List.replicate 600 0 := by
  decide +kernel

theorem source_helper_final_full :
    final.take 120 = List.replicate 120 1 ∧
    final.drop 240 = List.replicate 480 1 := by decide +kernel

theorem retained_helper_ids :
    ret.length = 9 ∧ ret.Nodup ∧
    ret.all (fun r => decide (240 ≤ r ∧ r < 720)) = true := by decide +kernel

theorem phase_shape :
    phaseB.length = 240 ∧
    (phaseB.map (fun g => g.2.2.length)).foldl Nat.add 0 = 600 :=
  SelectedBitCarrierPhaseB.phase_shape

/-- The smaller register bound is checked afresh on the same exact B tuples. -/
theorem phase_domains :
    phaseB.all (fun g => decide (g.1 < 672 ∧ g.2.1 < 720) &&
      g.2.2.all (fun r => decide (r < 720))) = true := by decide +kernel

theorem target_destinations :
    phaseB.all (fun g => decide (120 ≤ g.2.1 ∧ g.2.1 < 240)) = true :=
  SelectedBitCarrierPhaseB.target_destinations

theorem no_target_operands :
    phaseB.all (fun g => g.2.2.all (fun r => decide (r < 120 ∨ 240 ≤ r))) = true :=
  SelectedBitCarrierPhaseB.no_target_operands

theorem no_self_reads :
    phaseB.all (fun g => g.2.2.all (fun r => decide (r ≠ g.2.1))) = true :=
  SelectedBitCarrierPhaseB.no_self_reads

theorem scatter_shape :
    scatter.length = 120 ∧ (scatter.map List.length).foldl Nat.add 0 = 568 :=
  SelectedBitCarrierPhaseB.scatter_shape

theorem scatter_index_domain :
    scatter.all (fun row => row.all (fun k => decide (k < ret.length))) = true := by
  decide +kernel

theorem scatter_helpers :
    scatter.all (fun row => row.all (fun k =>
      match ret[k]? with
      | none => false
      | some r => decide (240 ≤ r ∧ r < 720))) = true := by decide +kernel

end CurrentMain.SelectedR480Boundary
#print axioms CurrentMain.SelectedR480Boundary.selected_shape
#print axioms CurrentMain.SelectedR480Boundary.line_shape
#print axioms CurrentMain.SelectedR480Boundary.frame_domain
#print axioms CurrentMain.SelectedR480Boundary.boundary_domain
#print axioms CurrentMain.SelectedR480Boundary.zero_full_rows
#print axioms CurrentMain.SelectedR480Boundary.source_entrances
#print axioms CurrentMain.SelectedR480Boundary.nonsource_entrances
#print axioms CurrentMain.SelectedR480Boundary.source_helper_final_full
#print axioms CurrentMain.SelectedR480Boundary.retained_helper_ids
#print axioms CurrentMain.SelectedR480Boundary.phase_shape
#print axioms CurrentMain.SelectedR480Boundary.phase_domains
#print axioms CurrentMain.SelectedR480Boundary.target_destinations
#print axioms CurrentMain.SelectedR480Boundary.no_target_operands
#print axioms CurrentMain.SelectedR480Boundary.no_self_reads
#print axioms CurrentMain.SelectedR480Boundary.scatter_shape
#print axioms CurrentMain.SelectedR480Boundary.scatter_index_domain
#print axioms CurrentMain.SelectedR480Boundary.scatter_helpers

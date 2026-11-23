import SelectedBitCarrierBoundaryData

/-! The selected #493 decoder/domain boundary only. These finite statements are
about the exact source projection. They do not establish any frame rank, Gram
nondegeneracy, actual label chronology, mutable-bit word semantics or physical
operator. In particular the integer rows 2I are not asserted invertible in an
arbitrary characteristic. Every lookup below is optional, never default-valued.
Supplier attribution and immutable byte pins are in SOURCE_BINDING.json.
Prepared with OpenAI assistance; Apache-2.0. -/
namespace CurrentMain.SelectedBitCarrierBoundary
open Data
set_option Elab.async false

theorem selected_shape :
    h = 8 ∧ v = 120 ∧ R = 489 ∧ registers = 729 ∧
    format = "bitE8/1+mut" ∧ form = "<x,y>/2" := by
  decide +kernel

theorem line_shape :
    lines.length = 120 ∧ lines.all (fun row => row.length == 8) = true := by
  decide +kernel

theorem frame_domain :
    frames.length = 672 ∧
    frames.all (fun row => row.all (fun i => decide (i < 120))) = true := by
  decide +kernel

theorem boundary_domain :
    start.length = 729 ∧ final.length = 729 ∧
    start.all (fun f => decide (f < 672)) = true ∧
    final.all (fun f => decide (f < 672)) = true := by
  decide +kernel

theorem zero_full_rows :
    frames[0]? = some [] ∧ frames[1]? = some (List.range 120) := by
  decide +kernel

theorem coordinate_prefix :
    lines.take 8 = (List.range 8).map (fun i =>
      (List.range 8).map (fun j => (if i == j then 2 else 0 : Int))) := by
  decide +kernel

theorem source_entrances :
    (List.range 120).all (fun r =>
      match start[r]? with
      | none => false
      | some f => frames[f]? == some [r]) = true := by
  decide +kernel

theorem nonsource_entrances : start.drop 120 = List.replicate 609 0 := by
  decide +kernel

theorem source_helper_final_full :
    final.take 120 = List.replicate 120 1 ∧
    final.drop 240 = List.replicate 489 1 := by
  decide +kernel

theorem retained_helper_ids :
    ret = List.range' 720 9 ∧
    ret.all (fun r => decide (240 ≤ r ∧ r < 729)) = true := by
  decide +kernel

end CurrentMain.SelectedBitCarrierBoundary
#print axioms CurrentMain.SelectedBitCarrierBoundary.selected_shape
#print axioms CurrentMain.SelectedBitCarrierBoundary.line_shape
#print axioms CurrentMain.SelectedBitCarrierBoundary.frame_domain
#print axioms CurrentMain.SelectedBitCarrierBoundary.boundary_domain
#print axioms CurrentMain.SelectedBitCarrierBoundary.zero_full_rows
#print axioms CurrentMain.SelectedBitCarrierBoundary.coordinate_prefix
#print axioms CurrentMain.SelectedBitCarrierBoundary.source_entrances
#print axioms CurrentMain.SelectedBitCarrierBoundary.nonsource_entrances
#print axioms CurrentMain.SelectedBitCarrierBoundary.source_helper_final_full
#print axioms CurrentMain.SelectedBitCarrierBoundary.retained_helper_ids

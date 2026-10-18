import CurrentR420FrameIndexCheck

/-! Seven current R420 frame/boundary facts, separated from B/scatter checks.
The frame-table bound reuses the accepted old table and current index permutation
through the bound-carrying frameAt lookup; no reordered full-table reduction.
All original public statements are retained. Physical transport is separate.
Prepared with OpenAI assistance; supplier and core attribution retained. -/
namespace CurrentMain.CurrentR420Boundary
open Data
set_option Elab.async false

theorem frame_domain : frames.length = 672 ∧
    frames.all (fun row => row.all (fun i => decide (i < 120))) = true := by
  have hlen := congrArg List.length frame_index_permutation
  simp only [List.length_mergeSort, List.length_map, List.length_range] at hlen
  have hrow (i : Fin 672) :
      (frameAt i).all (fun j => decide (j < 120)) = true := by
    have hm : frameAt i ∈ SelectedBitCarrierBoundary.Data.frames := by
      unfold frameAt
      exact List.getElem_mem _
    exact List.all_eq_true.mp SelectedBitCarrierBoundary.frame_domain.2 _ hm
  constructor
  · simpa only [frames, List.length_map] using hlen
  · apply List.all_eq_true.mpr
    intro row hr
    change row ∈ frameOrder.map frameAt at hr
    obtain ⟨i, _, rfl⟩ := List.mem_map.mp hr
    exact hrow i
#print axioms CurrentMain.CurrentR420Boundary.frame_domain

theorem zero_full_rows : frames[0]? = some [] ∧
    frames[1]? = some (List.range 120) := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.zero_full_rows

theorem boundary_domain : start.length = 660 ∧ final.length = 660 ∧
    start.all (fun f => decide (f < 672)) = true ∧
    final.all (fun f => decide (f < 672)) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.boundary_domain

theorem source_entrances : (List.range 120).all (fun r =>
    match start[r]? with
    | none => false
    | some f => frames[f]? == some [r]) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.source_entrances

theorem nonsource_entrances : start.drop 120 = List.replicate 540 0 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.nonsource_entrances

theorem source_helper_final_full : final.take 120 = List.replicate 120 1 ∧
    final.drop 240 = List.replicate 420 1 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.source_helper_final_full

theorem retained_helper_ids : ret.length = 9 ∧ ret.Nodup ∧
    ret.all (fun r => decide (240 ≤ r ∧ r < 660)) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.retained_helper_ids

end CurrentMain.CurrentR420Boundary

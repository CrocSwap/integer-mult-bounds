import CoordinateSwap
import Hosting
import PhysicalHosting
import PinnedWindow
import PinnedHosting
import BoundaryExamples
import PhysicalExample

-- Audit every named theorem, including supporting and boundary results.
#print axioms WholeHosting.masksDisjoint_symm
#print axioms WholeHosting.swapAddress_involution
#print axioms WholeHosting.swapAddress_commute
#print axioms WholeHosting.swapAddress_disjoint_union
#print axioms WholeHosting.bitAction_involution
#print axioms WholeHosting.bitAction_commute
#print axioms WholeHosting.bitAction_disjoint_comp
#print axioms WholeHosting.remainder_disjoint
#print axioms WholeHosting.union_remainder
#print axioms WholeHosting.bitAction_complete
#print axioms WholeHosting.bitAction_empty
#print axioms WholeHosting.bitFactors_union
#print axioms WholeHosting.bitFactors_complete
#print axioms WholeHosting.base_commutes
#print axioms WholeHosting.runBase_commutes
#print axioms WholeHosting.delay_residuals
#print axioms WholeHosting.whole_hosting
#print axioms WholeHosting.whole_hosting_in_context
#print axioms WholeHosting.Implementations.original_eq
#print axioms WholeHosting.Implementations.relocated_eq
#print axioms WholeHosting.implementation_whole_hosting
#print axioms WholeHosting.PhysicalImplementations.original_projection
#print axioms WholeHosting.PhysicalImplementations.relocated_projection
#print axioms WholeHosting.physical_whole_hosting
#print axioms WholeHosting.physical_hosting_in_context
#print axioms WholeHosting.PinnedBitWindow.disjoint
#print axioms WholeHosting.PinnedBitWindow.subset
#print axioms WholeHosting.PinnedBitWindow.coverage
#print axioms WholeHosting.PinnedBitWindow.same_stage_reorder
#print axioms WholeHosting.PinnedBitWindow.remainder_empty
#print axioms WholeHosting.PinnedBitWindow.complete
#print axioms WholeHosting.PinnedBitWindow.complete_with_remainder
#print axioms WholeHosting.PinnedBitWindow.selected_window_hosting
#print axioms WholeHosting.PinnedBitWindow.selected_physical_hosting
#print axioms WholeHosting.Boundary.readHost_preserves_host
#print axioms WholeHosting.Boundary.host_preservation_not_commutation
#print axioms WholeHosting.Boundary.overlapping_masks_not_disjoint
#print axioms WholeHosting.Boundary.overlapping_masks_not_union
#print axioms WholeHosting.Boundary.outside_pending_not_completion
#print axioms WholeHosting.Boundary.swapAB_involution
#print axioms WholeHosting.Boundary.swapCD_involution
#print axioms WholeHosting.Boundary.chartBC_involution
#print axioms WholeHosting.Boundary.same_chart_commute
#print axioms WholeHosting.Boundary.different_charts_not_commute
#print axioms WholeHosting.PhysicalExample.old_output_is_threaded
#print axioms WholeHosting.PhysicalExample.relocated_output_is_threaded
#print axioms WholeHosting.PhysicalExample.absorption

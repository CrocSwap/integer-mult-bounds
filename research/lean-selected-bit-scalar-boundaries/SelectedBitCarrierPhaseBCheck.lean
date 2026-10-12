import SelectedBitCarrierPhaseBData

/-! Exact finite B-phase/scatter shape for PR493. A target destination with no
explicit target operands is the syntactic hypothesis for an additive target
update y[d] := y[d] + sum(non-target values). Since these gates do not modify
non-target registers, their raw additive interpretation has identity linear
part on initial target values. That semantic implication is not proved here:
we still need the actual XOR/update interpreter, ordered-word correspondence
and physical common-frame/label transport. In particular no dirty-helper
compensation, source restoration, target shear operator or price follows.
Scatter is a table, not a row-major execution. The actual retained-major
COPY/ADD/ERASE sequence uses temporary register729 and needs a separate
730-register lifecycle argument. All lookups here are optional. -/
namespace CurrentMain.SelectedBitCarrierPhaseB
open Data
namespace Boundary
abbrev v := SelectedBitCarrierBoundary.Data.v
abbrev registers := SelectedBitCarrierBoundary.Data.registers
abbrev ret := SelectedBitCarrierBoundary.Data.ret
end Boundary
set_option Elab.async false

theorem phase_shape :
    phaseB.length = 240 ∧
    (phaseB.map (fun g => g.2.2.length)).foldl Nat.add 0 = 600 := by
  decide +kernel

theorem phase_domains :
    phaseB.all (fun g => decide (g.1 < 672 ∧ g.2.1 < Boundary.registers) &&
      g.2.2.all (fun r => decide (r < Boundary.registers))) = true := by
  decide +kernel

theorem target_destinations :
    phaseB.all (fun g => decide (Boundary.v ≤ g.2.1 ∧ g.2.1 < 2*Boundary.v)) = true := by
  decide +kernel

theorem no_target_operands :
    phaseB.all (fun g => g.2.2.all (fun r =>
      decide (r < Boundary.v ∨ 2*Boundary.v ≤ r))) = true := by
  decide +kernel

theorem no_self_reads :
    phaseB.all (fun g => g.2.2.all (fun r => decide (r ≠ g.2.1))) = true := by
  decide +kernel

theorem scatter_shape :
    scatter.length = 120 ∧
    (scatter.map List.length).foldl Nat.add 0 = 568 := by
  decide +kernel

theorem scatter_index_domain :
    scatter.all (fun row => row.all (fun k => decide (k < Boundary.ret.length))) = true := by
  decide +kernel

theorem scatter_helpers :
    scatter.all (fun row => row.all (fun k =>
      match Boundary.ret[k]? with
      | none => false
      | some r => decide (2*Boundary.v ≤ r ∧ r < Boundary.registers))) = true := by
  decide +kernel

theorem retained_boundary :
    Boundary.ret = List.range' 720 9 ∧
    Boundary.ret.all (fun r => decide (240 ≤ r ∧ r < 729)) = true :=
  SelectedBitCarrierBoundary.retained_helper_ids

end CurrentMain.SelectedBitCarrierPhaseB
#print axioms CurrentMain.SelectedBitCarrierPhaseB.phase_shape
#print axioms CurrentMain.SelectedBitCarrierPhaseB.phase_domains
#print axioms CurrentMain.SelectedBitCarrierPhaseB.target_destinations
#print axioms CurrentMain.SelectedBitCarrierPhaseB.no_target_operands
#print axioms CurrentMain.SelectedBitCarrierPhaseB.no_self_reads
#print axioms CurrentMain.SelectedBitCarrierPhaseB.scatter_shape
#print axioms CurrentMain.SelectedBitCarrierPhaseB.scatter_index_domain
#print axioms CurrentMain.SelectedBitCarrierPhaseB.scatter_helpers
#print axioms CurrentMain.SelectedBitCarrierPhaseB.retained_boundary

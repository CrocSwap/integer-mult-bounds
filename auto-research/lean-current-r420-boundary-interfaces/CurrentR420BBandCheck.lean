import CurrentR420FrameBoundaryCheck

/-! Eleven exact current R420 B-band finite facts, preserving original predicates
and proof bodies. The ordered bands contain120 target,597 source,120 target
writes and1077 operands. The final band retains120 source plus240 helper reads.
No-target reads do not imply preservation of the source registers. Current
scalar interpretation, A/C,D,scatter lifecycle and physical transport are separate.
Prepared with OpenAI assistance; supplier and core attribution retained. -/
namespace CurrentMain.CurrentR420Boundary
open Data
set_option Elab.async false

theorem phase_shape : phaseB.length = 837 ∧
    (phaseB.map (fun g => g.2.2.length)).foldl Nat.add 0 = 1077 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.phase_shape

theorem phase_domains : phaseB.all (fun g =>
    decide (g.1 < 672 ∧ g.2.1 < 660) &&
    g.2.2.all (fun r => decide (r < 660))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.phase_domains

theorem band_order : phaseB = firstTargets ++ sourceMiddle ++ lastTargets := rfl
#print axioms CurrentMain.CurrentR420Boundary.band_order

theorem band_lengths : firstTargets.length = 120 ∧ sourceMiddle.length = 597 ∧
    lastTargets.length = 120 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.band_lengths

theorem first_target_band : firstTargets.all (fun g =>
    decide (120 ≤ g.2.1 ∧ g.2.1 < 240 ∧ g.2.2.length = 1) &&
    g.2.2.all (fun r => decide (r < 120))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.first_target_band

theorem middle_source_band : sourceMiddle.all (fun g =>
    decide (g.2.1 < 120 ∧ g.2.2.length = 1)) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.middle_source_band

theorem middle_operand_bands :
    (sourceMiddle.take 477).all (fun g => g.2.2.all (fun r => decide (r < 120))) = true ∧
    (sourceMiddle.drop 477).length = 120 ∧
    (sourceMiddle.drop 477).all (fun g => g.2.2.all (fun r => decide (240 ≤ r))) = true := by
  decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.middle_operand_bands

theorem last_target_band : lastTargets.all (fun g =>
    decide (120 ≤ g.2.1 ∧ g.2.1 < 240 ∧ g.2.2.length = 3) &&
    g.2.2.all (fun r => decide (r < 120 ∨ 240 ≤ r))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.last_target_band

theorem final_target_frames : lastTargets.all (fun g =>
    final[g.2.1]? == some g.1) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.final_target_frames

theorem no_target_operands : phaseB.all (fun g =>
    g.2.2.all (fun r => decide (r < 120 ∨ 240 ≤ r))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.no_target_operands

theorem no_self_reads : phaseB.all (fun g =>
    g.2.2.all (fun r => decide (r ≠ g.2.1))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.no_self_reads

end CurrentMain.CurrentR420Boundary

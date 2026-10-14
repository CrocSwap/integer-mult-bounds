import CurrentPR589BData

/-! Fresh PR589 B finite facts. The 499 middle gates include sixteen writes to
helpers465,466,468, so no unconditional helper-preservation claim is made.
Every ordered gate/operand occurrence is retained; frame numbers remain metadata.
Physical geometry, full A/C/D cleanup and scatter lifecycle are separate.
Prepared with OpenAI assistance; original package attribution is retained. -/
namespace CurrentMain.CurrentPR589B
open Data
set_option Elab.async false

theorem dimensions : ports = 111 ∧ helpers = 439 ∧ registers = 661 ∧ frameCount = 636 := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.dimensions

theorem phase_shape : phaseB.length = 712 ∧
    (phaseB.map (fun g => g.2.2.length)).foldl Nat.add 0 = 934 := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.phase_shape

theorem phase_domains : phaseB.all (fun g =>
    decide (g.1 < 636 ∧ g.2.1 < 661) &&
    g.2.2.all (fun r => decide (r < 661))) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.phase_domains

theorem band_order : phaseB = firstTargets ++ offTargetMiddle ++ lastTargets := rfl
#print axioms CurrentMain.CurrentPR589B.band_order

theorem band_lengths : firstTargets.length = 102 ∧ offTargetMiddle.length = 499 ∧
    lastTargets.length = 111 := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.band_lengths

theorem first_target_band : firstTargets.all (fun g =>
    decide (111 ≤ g.2.1 ∧ g.2.1 < 222 ∧ g.2.2.length = 1) &&
    g.2.2.all (fun r => decide (r < 111))) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.first_target_band

theorem middle_off_target_band : offTargetMiddle.all (fun g =>
    decide ((g.2.1 < 111 ∨ 222 ≤ g.2.1) ∧ g.2.2.length = 1)) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.middle_off_target_band

theorem middle_write_counts : (offTargetMiddle.filter (fun g => decide (g.2.1 < 111))).length = 483 ∧
    (offTargetMiddle.filter (fun g => decide (222 ≤ g.2.1))).length = 16 := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.middle_write_counts

theorem last_target_band : lastTargets.all (fun g =>
    decide (111 ≤ g.2.1 ∧ g.2.1 < 222 ∧ g.2.2.length = 3) &&
    g.2.2.all (fun r => decide (r < 111 ∨ 222 ≤ r))) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.last_target_band

theorem write_region : phaseB.all (fun g =>
    decide (g.2.1 < 222 ∨ g.2.1 = 465 ∨ g.2.1 = 466 ∨ g.2.1 = 468)) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.write_region

theorem no_target_operands : phaseB.all (fun g =>
    g.2.2.all (fun r => decide (r < 111 ∨ 222 ≤ r))) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.no_target_operands

theorem no_self_reads : phaseB.all (fun g =>
    g.2.2.all (fun r => decide (r ≠ g.2.1))) = true := by decide +kernel
#print axioms CurrentMain.CurrentPR589B.no_self_reads

end CurrentMain.CurrentPR589B

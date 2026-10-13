import PhysicalCostTransfer
import Pr73ProfileReal

namespace Pr73PhysicalCost
open Pr73ProfileCertificate
open scoped BigOperators

noncomputable def costConstant (B C : ℝ) : ℝ :=
  PhysicalCostTransfer.uniformConstant B C Pr73ProfileReal.powerCharacteristic

/-- The pinned PR73 actual characteristic is already proved. Every member of
every state family obeys this unnormalized bound under uniform physical
contracts; the family can contain arbitrarily many volumes and spectators. -/
theorem state_cost_bound {S : Type}
    (width : S → ℕ) (volume cost : S → ℝ)
    (child : S → (r : Row) → Fin r.multiplicity → S)
    (B C : ℝ) (hvolume : ∀ s, 0 ≤ volume s)
    (child_width : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      width (child s r j) = r.width * (width s / m))
    (child_volume : ∀ s, m ≤ width s → ∀ r ∈ rows, ∀ j,
      volume (child s r j) = volume s / W)
    (uniform_base : ∀ s, 0 < width s → width s < m → cost s ≤ B * volume s)
    (physical_recurrence : ∀ s, m ≤ width s → cost s ≤ C * volume s +
      (rows.map (fun r => ∑ j : Fin r.multiplicity, cost (child s r j))).sum) :
    ∀ s, 0 < width s → cost s ≤ costConstant B C * volume s *
      (width s : ℝ) ^ (1 - (saving : ℝ)) := by
  apply PhysicalCostTransfer.state_all_width_bound rows (fun r => r.width) (fun r => r.multiplicity) m W
    width volume cost child (1 - (saving : ℝ)) (costConstant B C) B C
    Pr73ProfileReal.powerCharacteristic
  · norm_num [m]
  · norm_num [W]
  · norm_num [saving]
  · exact PhysicalCostTransfer.uniformConstant_nonneg B C _ Pr73ProfileReal.actual_power_characteristic_lt_one
  · exact PhysicalCostTransfer.uniformConstant_base B C _ Pr73ProfileReal.actual_power_characteristic_lt_one
  · exact PhysicalCostTransfer.uniformConstant_overhead B C _ Pr73ProfileReal.actual_power_characteristic_lt_one
  · exact hvolume
  · intro r hr; exact (Pr73ProfileReal.row_valid r hr).1
  · intro r hr; exact (Pr73ProfileReal.row_valid r hr).2.1
  · rfl
  · exact Pr73ProfileReal.actual_power_characteristic_lt_one
  · exact child_width
  · exact child_volume
  · exact uniform_base
  · exact physical_recurrence


end Pr73PhysicalCost

#print axioms Pr73PhysicalCost.state_cost_bound

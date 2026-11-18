/-
WholeFloorEnd : R3's whole-word D0 floor 155,730.99 on the 17-call invoice
(caller #7113 = C(8|9) fixed), assembled from WholeFloorPrice.d0_floor (pricing step) and
WholeFloorLogs.key (kernel-checked caller D0 and numerics), with the owned-LATERAL correction.
-/
import Nov15.WholeFloorLogs

set_option linter.unusedSectionVars false

namespace WholeFloorEnd
open CallerCost WholeFloorPrice

/-- **R3 floor**: for every priced native word WITHOUT lateral owned MOVEs (lat = 0), the 17-call invoice D0
is >= 155,730.9 (R3: 155,730.99). -/
theorem d0_whole_floor (w : Word) (hP : Priced w) (hlat : w.lat = 0) (n : Inv)
    (hn : Dinv n = w.hD0 + w.mD0 + w.oD0) :
    (155730.9 : ℝ) ≤ Dinv (invoice (caller 6 7) n 17) := by
  have h1 := d0_floor w hP
  rw [hlat] at h1
  have hmax : max 0 (88 - ((0 : ℕ) : ℝ)) = 88 := by norm_num
  rw [hmax] at h1
  have h2 := WholeFloorLogs.floor_ge
  rw [invoice_D0, hn]
  push_cast
  nlinarith

/-- **corrected unconditional floor** (any number of lateral owned MOVEs): D0 >= 153,656.9, R2's value.
The extra 2,073.9 of R3 is available only when lat = 0 (see r3_stops_not_forced). -/
theorem d0_whole_floor_any_lat (w : Word) (hP : Priced w) (n : Inv)
    (hn : Dinv n = w.hD0 + w.mD0 + w.oD0) :
    (153656.9 : ℝ) ≤ Dinv (invoice (caller 6 7) n 17) := by
  have h1 := d0_floor w hP
  have hM : (0 : ℝ) ≤ 2 * Real.log 2 * max 0 (88 - (w.lat : ℝ)) :=
    mul_nonneg (by have := Real.log_pos (show (1 : ℝ) < 2 by norm_num); linarith) (le_max_left _ _)
  have h2 := WholeFloorLogs.floor_ge
  have h3 := Real.log_two_lt_d9
  rw [invoice_D0, hn]
  nlinarith

end WholeFloorEnd

#print axioms WholeFloorEnd.d0_whole_floor
#print axioms WholeFloorEnd.d0_whole_floor_any_lat
#print axioms WholeFloorLogs.key

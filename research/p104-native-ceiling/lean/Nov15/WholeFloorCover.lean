import Nov15.WholeFloorCoverData
import Nov15.JointCeiling

/-! WholeFloorCover : the cover F < 0 on [.0204110964, 1] for (caller 6 7) + 17 * natFloor; data in WholeFloorCoverData. -/
namespace WholeFloorCover
open NumCertK JointCeiling CallerCost

theorem invoice_eq_Fc (s : ℝ) : Finv s (invoice (caller 6 7) natFloor 17) = Fc cfW s := by
  simp only [Finv, Fh, invoice, caller, callerT, callerP, armT, armP, natFloor, scale, Fc, cfW,
    List.range_succ, List.range_zero]
  norm_num
  ring

/-- **the cover**: F < 0 on [.0204110964, 1] (t = 1 - s) for the floor-native invoice. -/
theorem cover (t : ℝ) (ht : (204110965 : ℝ) / 10 ^ 10 ≤ t) (ht1 : t ≤ 1) :
    Finv (1 - t) (invoice (caller 6 7) natFloor 17) < 0 := by
  rw [invoice_eq_Fc]
  apply cfW_neg _ (by linarith)
  push_cast
  linarith

end WholeFloorCover

#print axioms WholeFloorCover.cover

import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC4
import Nov15.CongestionI3NumA

namespace CongestionI3Dual
open NumCertK CongestionI3

/-- the tail pieces are covered by the F1 theorems `cfB_neg` / `cfC_neg` -/
theorem LA3_ge : liftA ≤ 17 * LA3 := by unfold liftA sigma0 LA3 lcpA3 sgA3; norm_num
theorem LC3_ge : liftC ≤ 17 * LC3 := by unfold liftC LcC LC3 lcpC3 sgC3; norm_num

end CongestionI3Dual

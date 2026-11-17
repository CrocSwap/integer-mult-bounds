import Nov15.V2FloorDefs_b

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem sum_b_500 : tsumb 500 250 = 156368891133 := by decide +kernel

end V2Floor

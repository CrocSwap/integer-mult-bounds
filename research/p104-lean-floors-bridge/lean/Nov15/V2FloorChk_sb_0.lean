import Nov15.V2FloorDefs_b

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem sum_b_0 : tsumb 0 250 = 132262509117 := by decide +kernel

end V2Floor

import Nov15.V2FloorDefs_j

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem sum_j_1000 : tsumj 1000 250 = 62349480754 := by decide +kernel

end V2Floor

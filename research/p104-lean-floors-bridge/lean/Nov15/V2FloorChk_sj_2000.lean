import Nov15.V2FloorDefs_j

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem sum_j_2000 : tsumj 2000 250 = 196288062025 := by decide +kernel

end V2Floor

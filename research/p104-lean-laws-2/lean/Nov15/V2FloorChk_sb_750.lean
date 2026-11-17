import Nov15.V2FloorDefs_b

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem sum_b_750 : tsumb 750 250 = 181785912002 := by decide +kernel

end V2Floor

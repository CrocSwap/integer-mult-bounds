import Nov15.V2FloorDefs_j

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem ok_j_2000 : ∀ i < 250, okj (2000 + i) = true := by decide +kernel

end V2Floor

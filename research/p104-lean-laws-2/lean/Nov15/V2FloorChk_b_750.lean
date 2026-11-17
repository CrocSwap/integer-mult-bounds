import Nov15.V2FloorDefs_b

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset

theorem ok_b_750 : ∀ i < 250, okb (750 + i) = true := by decide +kernel

end V2Floor

import Nov15.DecoderWall4Defs

open Matrix
set_option maxHeartbeats 0
namespace DW4

theorem cats_ok_3 : ∀ k ∈ List.range' 90 30, catOK k := by decide +kernel

end DW4

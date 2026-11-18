import Nov15.CongestionTreeCertCGDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unCG0 : Fup [(8, 1), (9, -1)] (1 - tCG1) (1 - tCG1) < -unLoCG0 := by unfold tCG1 unLoCG0; decide +kernel
end CongestionNative

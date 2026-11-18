import Nov15.CongestionTreeCertCGDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unCG1 : Fup [(8, 1), (9, -1)] (1 - tCG2) (1 - tCG2) < -unLoCG1 := by unfold tCG2 unLoCG1; decide +kernel
end CongestionNative

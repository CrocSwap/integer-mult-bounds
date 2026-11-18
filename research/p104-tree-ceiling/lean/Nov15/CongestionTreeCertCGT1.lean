import Nov15.CongestionTreeCertCGDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptCG1 : Fup cfC (1 - tCG1) (1 - tCG1) < 17 * (lcpCG1 - 5 * sgCG1) := by unfold tCG1 lcpCG1 sgCG1; decide +kernel
end CongestionNative

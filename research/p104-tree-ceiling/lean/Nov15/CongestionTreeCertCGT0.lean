import Nov15.CongestionTreeCertCGDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptCG0 : Fup cfC (1 - tCG0) (1 - tCG0) < 17 * (lcpCG0 - 5 * sgCG0) := by unfold tCG0 lcpCG0 sgCG0; decide +kernel
end CongestionNative

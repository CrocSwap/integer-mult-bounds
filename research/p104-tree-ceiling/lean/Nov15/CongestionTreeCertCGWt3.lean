import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionTreeW
import Nov15.CTreecgDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtCG_1_8 : CTree.wtPair CTree.cgW (1 - tTJ0) (1 - a0CG) (1, 8) = true := by unfold tTJ0 a0CG; decide +kernel
theorem wtCG_2_3 : CTree.wtPair CTree.cgW (1 - tTJ0) (1 - a0CG) (2, 3) = true := by unfold tTJ0 a0CG; decide +kernel
end CongestionNative

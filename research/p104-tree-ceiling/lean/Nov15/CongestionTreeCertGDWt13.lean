import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionTreeW
import Nov15.CTreegaDefs
import Nov15.CTreegbDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtGD_6_8 : CTree.wtPair CTree.gaW (1 - tTJ0GD) (1 - a0GD) (6, 8) = true := by unfold tTJ0GD a0GD; decide +kernel
theorem wtGD_7_8 : CTree.wtPair CTree.gaW (1 - tTJ0GD) (1 - a0GD) (7, 8) = true := by unfold tTJ0GD a0GD; decide +kernel
end CongestionNative

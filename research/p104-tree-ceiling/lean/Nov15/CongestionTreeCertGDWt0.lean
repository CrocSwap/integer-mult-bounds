import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionTreeW
import Nov15.CTreegaDefs
import Nov15.CTreegbDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtGD_1_2 : CTree.wtPair CTree.gaW (1 - tTJ0GD) (1 - a0GD) (1, 2) = true := by unfold tTJ0GD a0GD; decide +kernel
theorem wtGD_1_3 : CTree.wtPair CTree.gaW (1 - tTJ0GD) (1 - a0GD) (1, 3) = true := by unfold tTJ0GD a0GD; decide +kernel
end CongestionNative

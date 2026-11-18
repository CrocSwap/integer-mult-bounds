import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionTreeCore
import Nov15.CTreegaDefs
import Nov15.CTreegbDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineGD0 : CTree.lineOK CTree.gar0 CTree.gbr0 capIGD0 lamGD0 gAGD0 gBGD0 = true := by unfold capIGD0 lamGD0 gAGD0 gBGD0; decide +kernel
theorem numGD0 : lcpGD0 + 8 * cHGD0 ≤ (((lamGD0 : ℚ) * 4962 - ((gAGD0 : ℚ) * 104 - ((gAGD0 : ℚ) - gBGD0) * 48)) / 10 ^ 14) := by
  unfold lcpGD0 cHGD0 lamGD0 gAGD0 gBGD0; norm_num
theorem capGD0 : (capIGD0 : ℚ) ≤ unLoGD0 * 10 ^ 14 / 48 := by unfold capIGD0 unLoGD0; norm_num
end CongestionNative

import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionTreeCore
import Nov15.CTreegaDefs
import Nov15.CTreegbDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineGD1 : CTree.lineOK CTree.gar0 CTree.gbr0 capIGD1 lamGD1 gAGD1 gBGD1 = true := by unfold capIGD1 lamGD1 gAGD1 gBGD1; decide +kernel
theorem numGD1 : lcpGD1 + 8 * cHGD1 ≤ (((lamGD1 : ℚ) * 4962 - ((gAGD1 : ℚ) * 104 - ((gAGD1 : ℚ) - gBGD1) * 48)) / 10 ^ 14) := by
  unfold lcpGD1 cHGD1 lamGD1 gAGD1 gBGD1; norm_num
theorem capGD1 : (capIGD1 : ℚ) ≤ unLoGD1 * 10 ^ 14 / 48 := by unfold capIGD1 unLoGD1; norm_num
end CongestionNative

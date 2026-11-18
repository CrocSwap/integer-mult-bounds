import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionReaderTree
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineRD0 : CTree.lineOKR CTree.rdar0 CTree.rdir0 capIRD0 dIRD lamRD0 gARD0 gBRD0 = true := by unfold capIRD0 dIRD lamRD0 gARD0 gBRD0; decide +kernel
theorem numRD0 : lcpRD0 + 8 * cHRD0 ≤ (((lamRD0 : ℚ) * 4962 - ((gARD0 : ℚ) * 104 - ((gARD0 : ℚ) - gBRD0) * 48) - ((15 : ℕ) : ℚ) * dIRD) / 10 ^ 14) := by
  unfold lcpRD0 cHRD0 lamRD0 gARD0 gBRD0 dIRD; norm_num
theorem capRD0 : (capIRD0 : ℚ) ≤ unLoRD0 * 10 ^ 14 / 48 := by unfold capIRD0 unLoRD0; norm_num
end CongestionNative

import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionReaderTree
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineRD1 : CTree.lineOKR CTree.rdar0 CTree.rdir0 capIRD1 dIRD lamRD1 gARD1 gBRD1 = true := by unfold capIRD1 dIRD lamRD1 gARD1 gBRD1; decide +kernel
theorem numRD1 : lcpRD1 + 8 * cHRD1 ≤ (((lamRD1 : ℚ) * 4962 - ((gARD1 : ℚ) * 104 - ((gARD1 : ℚ) - gBRD1) * 48) - ((15 : ℕ) : ℚ) * dIRD) / 10 ^ 14) := by
  unfold lcpRD1 cHRD1 lamRD1 gARD1 gBRD1 dIRD; norm_num
theorem capRD1 : (capIRD1 : ℚ) ≤ unLoRD1 * 10 ^ 14 / 48 := by unfold capIRD1 unLoRD1; norm_num
end CongestionNative

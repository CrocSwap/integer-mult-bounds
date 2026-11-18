import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionTreeCore
import Nov15.CTreecgDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineCG1 : CTree.lineOK CTree.cgr0 CTree.cgr0 capICG1 lamCG1 gACG1 gBCG1 = true := by unfold capICG1 lamCG1 gACG1 gBCG1; decide +kernel
theorem numCG1 : lcpCG1 + 8 * cHCG1 ≤ (((lamCG1 : ℚ) * 4962 - ((gACG1 : ℚ) * 104 - ((gACG1 : ℚ) - gBCG1) * 0)) / 10 ^ 14) := by
  unfold lcpCG1 cHCG1 lamCG1 gACG1 gBCG1; norm_num
theorem capCG1 : (capICG1 : ℚ) ≤ unLoCG1 * 10 ^ 14 / 48 := by unfold capICG1 unLoCG1; norm_num
end CongestionNative

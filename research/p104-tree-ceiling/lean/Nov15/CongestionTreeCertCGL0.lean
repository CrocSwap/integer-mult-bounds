import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionTreeCore
import Nov15.CTreecgDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineCG0 : CTree.lineOK CTree.cgr0 CTree.cgr0 capICG0 lamCG0 gACG0 gBCG0 = true := by unfold capICG0 lamCG0 gACG0 gBCG0; decide +kernel
theorem numCG0 : lcpCG0 + 8 * cHCG0 ≤ (((lamCG0 : ℚ) * 4962 - ((gACG0 : ℚ) * 104 - ((gACG0 : ℚ) - gBCG0) * 0)) / 10 ^ 14) := by
  unfold lcpCG0 cHCG0 lamCG0 gACG0 gBCG0; norm_num
theorem capCG0 : (capICG0 : ℚ) ≤ unLoCG0 * 10 ^ 14 / 48 := by unfold capICG0 unLoCG0; norm_num
end CongestionNative

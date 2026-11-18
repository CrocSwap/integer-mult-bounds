import Nov15.CongestionTreeCertCGWt0
import Nov15.CongestionTreeCertCGWt1
import Nov15.CongestionTreeCertCGWt2
import Nov15.CongestionTreeCertCGWt3
import Nov15.CongestionTreeCertCGWt4
import Nov15.CongestionTreeCertCGWt5
import Nov15.CongestionTreeCertCGWt6
import Nov15.CongestionTreeCertCGWt7
import Nov15.CongestionTreeCertCGWt8
import Nov15.CongestionTreeCertCGWt9
import Nov15.CongestionTreeCertCGWt10
import Nov15.CongestionTreeCertCGWt11
import Nov15.CongestionTreeCertCGWt12
import Nov15.CongestionTreeCertCGWt13
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtCG : CTree.wtOK CTree.cgW (1 - tTJ0) (1 - a0CG) = true := by
  unfold CTree.wtOK
  rw [List.all_eq_true]
  intro p hp
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact wtCG_1_2
  · exact wtCG_1_3
  · exact wtCG_1_4
  · exact wtCG_1_5
  · exact wtCG_1_6
  · exact wtCG_1_7
  · exact wtCG_1_8
  · exact wtCG_2_3
  · exact wtCG_2_4
  · exact wtCG_2_5
  · exact wtCG_2_6
  · exact wtCG_2_7
  · exact wtCG_2_8
  · exact wtCG_3_4
  · exact wtCG_3_5
  · exact wtCG_3_6
  · exact wtCG_3_7
  · exact wtCG_3_8
  · exact wtCG_4_5
  · exact wtCG_4_6
  · exact wtCG_4_7
  · exact wtCG_4_8
  · exact wtCG_5_6
  · exact wtCG_5_7
  · exact wtCG_5_8
  · exact wtCG_6_7
  · exact wtCG_6_8
  · exact wtCG_7_8
end CongestionNative

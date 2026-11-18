import Nov15.CongestionTreeCertGDWt0
import Nov15.CongestionTreeCertGDWt1
import Nov15.CongestionTreeCertGDWt2
import Nov15.CongestionTreeCertGDWt3
import Nov15.CongestionTreeCertGDWt4
import Nov15.CongestionTreeCertGDWt5
import Nov15.CongestionTreeCertGDWt6
import Nov15.CongestionTreeCertGDWt7
import Nov15.CongestionTreeCertGDWt8
import Nov15.CongestionTreeCertGDWt9
import Nov15.CongestionTreeCertGDWt10
import Nov15.CongestionTreeCertGDWt11
import Nov15.CongestionTreeCertGDWt12
import Nov15.CongestionTreeCertGDWt13
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtGD : CTree.wtOK CTree.gaW (1 - tTJ0GD) (1 - a0GD) = true := by
  unfold CTree.wtOK
  rw [List.all_eq_true]
  intro p hp
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact wtGD_1_2
  · exact wtGD_1_3
  · exact wtGD_1_4
  · exact wtGD_1_5
  · exact wtGD_1_6
  · exact wtGD_1_7
  · exact wtGD_1_8
  · exact wtGD_2_3
  · exact wtGD_2_4
  · exact wtGD_2_5
  · exact wtGD_2_6
  · exact wtGD_2_7
  · exact wtGD_2_8
  · exact wtGD_3_4
  · exact wtGD_3_5
  · exact wtGD_3_6
  · exact wtGD_3_7
  · exact wtGD_3_8
  · exact wtGD_4_5
  · exact wtGD_4_6
  · exact wtGD_4_7
  · exact wtGD_4_8
  · exact wtGD_5_6
  · exact wtGD_5_7
  · exact wtGD_5_8
  · exact wtGD_6_7
  · exact wtGD_6_8
  · exact wtGD_7_8
end CongestionNative

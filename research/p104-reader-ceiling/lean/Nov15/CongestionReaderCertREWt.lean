import Nov15.CongestionReaderCertREWt0
import Nov15.CongestionReaderCertREWt1
import Nov15.CongestionReaderCertREWt2
import Nov15.CongestionReaderCertREWt3
import Nov15.CongestionReaderCertREWt4
import Nov15.CongestionReaderCertREWt5
import Nov15.CongestionReaderCertREWt6
import Nov15.CongestionReaderCertREWt7
import Nov15.CongestionReaderCertREWt8
import Nov15.CongestionReaderCertREWt9
import Nov15.CongestionReaderCertREWt10
import Nov15.CongestionReaderCertREWt11
import Nov15.CongestionReaderCertREWt12
import Nov15.CongestionReaderCertREWt13
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRE : CTree.wtOK CTree.reaW (1 - tTJ0RE) (1 - a0RE) = true := by
  unfold CTree.wtOK
  rw [List.all_eq_true]
  intro p hp
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact wtRE_1_2
  · exact wtRE_1_3
  · exact wtRE_1_4
  · exact wtRE_1_5
  · exact wtRE_1_6
  · exact wtRE_1_7
  · exact wtRE_1_8
  · exact wtRE_2_3
  · exact wtRE_2_4
  · exact wtRE_2_5
  · exact wtRE_2_6
  · exact wtRE_2_7
  · exact wtRE_2_8
  · exact wtRE_3_4
  · exact wtRE_3_5
  · exact wtRE_3_6
  · exact wtRE_3_7
  · exact wtRE_3_8
  · exact wtRE_4_5
  · exact wtRE_4_6
  · exact wtRE_4_7
  · exact wtRE_4_8
  · exact wtRE_5_6
  · exact wtRE_5_7
  · exact wtRE_5_8
  · exact wtRE_6_7
  · exact wtRE_6_8
  · exact wtRE_7_8
end CongestionNative

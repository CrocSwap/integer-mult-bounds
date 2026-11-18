import Nov15.CongestionReaderCertRFWt0
import Nov15.CongestionReaderCertRFWt1
import Nov15.CongestionReaderCertRFWt2
import Nov15.CongestionReaderCertRFWt3
import Nov15.CongestionReaderCertRFWt4
import Nov15.CongestionReaderCertRFWt5
import Nov15.CongestionReaderCertRFWt6
import Nov15.CongestionReaderCertRFWt7
import Nov15.CongestionReaderCertRFWt8
import Nov15.CongestionReaderCertRFWt9
import Nov15.CongestionReaderCertRFWt10
import Nov15.CongestionReaderCertRFWt11
import Nov15.CongestionReaderCertRFWt12
import Nov15.CongestionReaderCertRFWt13
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRF : CTree.wtOK CTree.rfaW (1 - tTJ0RF) (1 - a0RF) = true := by
  unfold CTree.wtOK
  rw [List.all_eq_true]
  intro p hp
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact wtRF_1_2
  · exact wtRF_1_3
  · exact wtRF_1_4
  · exact wtRF_1_5
  · exact wtRF_1_6
  · exact wtRF_1_7
  · exact wtRF_1_8
  · exact wtRF_2_3
  · exact wtRF_2_4
  · exact wtRF_2_5
  · exact wtRF_2_6
  · exact wtRF_2_7
  · exact wtRF_2_8
  · exact wtRF_3_4
  · exact wtRF_3_5
  · exact wtRF_3_6
  · exact wtRF_3_7
  · exact wtRF_3_8
  · exact wtRF_4_5
  · exact wtRF_4_6
  · exact wtRF_4_7
  · exact wtRF_4_8
  · exact wtRF_5_6
  · exact wtRF_5_7
  · exact wtRF_5_8
  · exact wtRF_6_7
  · exact wtRF_6_8
  · exact wtRF_7_8
end CongestionNative

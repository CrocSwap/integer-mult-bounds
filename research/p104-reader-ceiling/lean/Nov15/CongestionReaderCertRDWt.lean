import Nov15.CongestionReaderCertRDWt0
import Nov15.CongestionReaderCertRDWt1
import Nov15.CongestionReaderCertRDWt2
import Nov15.CongestionReaderCertRDWt3
import Nov15.CongestionReaderCertRDWt4
import Nov15.CongestionReaderCertRDWt5
import Nov15.CongestionReaderCertRDWt6
import Nov15.CongestionReaderCertRDWt7
import Nov15.CongestionReaderCertRDWt8
import Nov15.CongestionReaderCertRDWt9
import Nov15.CongestionReaderCertRDWt10
import Nov15.CongestionReaderCertRDWt11
import Nov15.CongestionReaderCertRDWt12
import Nov15.CongestionReaderCertRDWt13
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRD : CTree.wtOK CTree.rdaW (1 - tTJ0RD) (1 - a0RD) = true := by
  unfold CTree.wtOK
  rw [List.all_eq_true]
  intro p hp
  simp only [pairs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact wtRD_1_2
  · exact wtRD_1_3
  · exact wtRD_1_4
  · exact wtRD_1_5
  · exact wtRD_1_6
  · exact wtRD_1_7
  · exact wtRD_1_8
  · exact wtRD_2_3
  · exact wtRD_2_4
  · exact wtRD_2_5
  · exact wtRD_2_6
  · exact wtRD_2_7
  · exact wtRD_2_8
  · exact wtRD_3_4
  · exact wtRD_3_5
  · exact wtRD_3_6
  · exact wtRD_3_7
  · exact wtRD_3_8
  · exact wtRD_4_5
  · exact wtRD_4_6
  · exact wtRD_4_7
  · exact wtRD_4_8
  · exact wtRD_5_6
  · exact wtRD_5_7
  · exact wtRD_5_8
  · exact wtRD_6_7
  · exact wtRD_6_8
  · exact wtRD_7_8
end CongestionNative

import CGInputAddressCheck000
import CGInputAddressCheck001
import CGInputAddressCheck002
import CGInputAddressCheck003
import CGInputAddressCheck004
import CGInputAddressCheck005
import CGInputAddressCheck006
import CGInputAddressCheck007
import CGInputAddressCheck008
import CGInputAddressCheck009
import CGInputAddressCheck010
import CGInputAddressCheck011
import CGInputAddressCheck012
import CGInputAddressCheck013
import CGInputAddressCheck014
import CGInputAddressCheck015
import CGInputAddressCheck016
import CGInputAddressCheck017
import CGInputAddressCheck018
import CGInputAddressCheck019
import CGInputAddressCheck020
namespace CurrentMain.ComplexGeometryInputCertificates
open CurrentMain.ComplexGeometry CurrentMain.ComplexGeometryData CurrentMain.SignedTrace CurrentMain.BinaryFrame
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
theorem address_checked : rangeCheck (fun i => decide (inputMask i<2^22 ∧ get CurrentMain.ComplexGeometryInputs.inverseTable (inputMask i)=i)) 0 1320=true := by
  exact (rangeCheck_join _ 0 640 680 (rangeCheck_join _ 0 320 320 (rangeCheck_join _ 0 128 192 (rangeCheck_join _ 0 64 64 CurrentMain.CGInputAddressCheck000.checked CurrentMain.CGInputAddressCheck001.checked) (rangeCheck_join _ 128 64 128 CurrentMain.CGInputAddressCheck002.checked (rangeCheck_join _ 192 64 64 CurrentMain.CGInputAddressCheck003.checked CurrentMain.CGInputAddressCheck004.checked))) (rangeCheck_join _ 320 128 192 (rangeCheck_join _ 320 64 64 CurrentMain.CGInputAddressCheck005.checked CurrentMain.CGInputAddressCheck006.checked) (rangeCheck_join _ 448 64 128 CurrentMain.CGInputAddressCheck007.checked (rangeCheck_join _ 512 64 64 CurrentMain.CGInputAddressCheck008.checked CurrentMain.CGInputAddressCheck009.checked)))) (rangeCheck_join _ 640 320 360 (rangeCheck_join _ 640 128 192 (rangeCheck_join _ 640 64 64 CurrentMain.CGInputAddressCheck010.checked CurrentMain.CGInputAddressCheck011.checked) (rangeCheck_join _ 768 64 128 CurrentMain.CGInputAddressCheck012.checked (rangeCheck_join _ 832 64 64 CurrentMain.CGInputAddressCheck013.checked CurrentMain.CGInputAddressCheck014.checked))) (rangeCheck_join _ 960 192 168 (rangeCheck_join _ 960 64 128 CurrentMain.CGInputAddressCheck015.checked (rangeCheck_join _ 1024 64 64 CurrentMain.CGInputAddressCheck016.checked CurrentMain.CGInputAddressCheck017.checked)) (rangeCheck_join _ 1152 64 104 CurrentMain.CGInputAddressCheck018.checked (rangeCheck_join _ 1216 64 40 CurrentMain.CGInputAddressCheck019.checked CurrentMain.CGInputAddressCheck020.checked)))))
end CurrentMain.ComplexGeometryInputCertificates
#print axioms CurrentMain.ComplexGeometryInputCertificates.address_checked

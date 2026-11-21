import Nov15.BlockLaw2Key
namespace BlockLaw2Pl0
open FrameCert BlockComplete BlockLaw BlockLaw2Key
theorem pl0 : certs0.all planeChk = true := by decide +kernel
theorem pl1 : certs1.all planeChk = true := by decide +kernel
theorem pl2 : certs2.all planeChk = true := by decide +kernel
theorem pl3 : certs3.all planeChk = true := by decide +kernel
theorem pl4 : certs4.all planeChk = true := by decide +kernel
theorem pl5 : certs5.all planeChk = true := by decide +kernel
theorem pl6 : certs6.all planeChk = true := by decide +kernel
theorem pl7 : certs7.all planeChk = true := by decide +kernel
end BlockLaw2Pl0

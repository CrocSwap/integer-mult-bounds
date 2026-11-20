import Nov15.BlockLaw2Par
namespace BlockLaw2Ev0
open FrameCert BlockComplete BlockLaw BlockLaw2Par
theorem ev0 : certs0.all evenChk = true := by decide +kernel
theorem ev1 : certs1.all evenChk = true := by decide +kernel
theorem ev2 : certs2.all evenChk = true := by decide +kernel
theorem ev3 : certs3.all evenChk = true := by decide +kernel
theorem ev4 : certs4.all evenChk = true := by decide +kernel
theorem ev5 : certs5.all evenChk = true := by decide +kernel
theorem ev6 : certs6.all evenChk = true := by decide +kernel
theorem ev7 : certs7.all evenChk = true := by decide +kernel
end BlockLaw2Ev0

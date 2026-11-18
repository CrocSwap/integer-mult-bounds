import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigGD1 : sigOK (1 - tGD2) (1 - tGD1) sgGD1 = true := by unfold tGD1 tGD2 sgGD1; decide +kernel
end CongestionNative

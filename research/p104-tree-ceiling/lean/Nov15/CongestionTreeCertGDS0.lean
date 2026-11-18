import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigGD0 : sigOK (1 - tGD1) (1 - tGD0) sgGD0 = true := by unfold tGD0 tGD1 sgGD0; decide +kernel
end CongestionNative

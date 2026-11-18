import Nov15.CongestionReaderCertREDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRE1 : sigOK (1 - tRE2) (1 - tRE1) sgRE1 = true := by unfold tRE1 tRE2 sgRE1; decide +kernel
end CongestionNative

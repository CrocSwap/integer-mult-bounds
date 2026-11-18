import Nov15.CongestionReaderCertREDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRE0 : sigOK (1 - tRE1) (1 - tRE0) sgRE0 = true := by unfold tRE0 tRE1 sgRE0; decide +kernel
end CongestionNative

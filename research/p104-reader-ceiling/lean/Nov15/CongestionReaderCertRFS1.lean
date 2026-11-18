import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRF1 : sigOK (1 - tRF2) (1 - tRF1) sgRF1 = true := by unfold tRF1 tRF2 sgRF1; decide +kernel
end CongestionNative

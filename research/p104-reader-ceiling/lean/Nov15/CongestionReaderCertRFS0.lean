import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRF0 : sigOK (1 - tRF1) (1 - tRF0) sgRF0 = true := by unfold tRF0 tRF1 sgRF0; decide +kernel
end CongestionNative

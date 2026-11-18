import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRD2 : sigOK (1 - tRD3) (1 - tRD2) sgRD2 = true := by unfold tRD2 tRD3 sgRD2; decide +kernel
end CongestionNative

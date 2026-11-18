import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRD0 : sigOK (1 - tRD1) (1 - tRD0) sgRD0 = true := by unfold tRD0 tRD1 sgRD0; decide +kernel
end CongestionNative

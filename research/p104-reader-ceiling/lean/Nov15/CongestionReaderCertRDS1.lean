import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigRD1 : sigOK (1 - tRD2) (1 - tRD1) sgRD1 = true := by unfold tRD1 tRD2 sgRD1; decide +kernel
end CongestionNative

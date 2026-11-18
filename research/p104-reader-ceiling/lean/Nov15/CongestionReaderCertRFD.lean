import Nov15.CongestionReaderCertRFDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem cfC_dRF : 0 < dLo cfC (93 / 100) (1 - a0RF) := by unfold a0RF; decide +kernel
end CongestionNative

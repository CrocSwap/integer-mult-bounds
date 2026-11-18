import Nov15.CongestionReaderCertRFDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRF1 : Fup cfC (1 - tRF1) (1 - tRF1) < 17 * (lcpRF1 - 5 * sgRF1) := by unfold tRF1 lcpRF1 sgRF1; decide +kernel
end CongestionNative

import Nov15.CongestionReaderCertRFDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRF0 : Fup cfC (1 - tRF0) (1 - tRF0) < 17 * (lcpRF0 - 5 * sgRF0) := by unfold tRF0 lcpRF0 sgRF0; decide +kernel
end CongestionNative

import Nov15.CongestionReaderCertRFDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unRF0 : Fup [(8, 1), (9, -1)] (1 - tRF1) (1 - tRF1) < -unLoRF0 := by unfold tRF1 unLoRF0; decide +kernel
end CongestionNative

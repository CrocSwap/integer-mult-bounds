import Nov15.CongestionReaderCertRFDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unRF1 : Fup [(8, 1), (9, -1)] (1 - tRF2) (1 - tRF2) < -unLoRF1 := by unfold tRF2 unLoRF1; decide +kernel
end CongestionNative

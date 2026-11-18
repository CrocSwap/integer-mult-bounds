import Nov15.CongestionReaderCertRDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unRD2 : Fup [(8, 1), (9, -1)] (1 - tRD3) (1 - tRD3) < -unLoRD2 := by unfold tRD3 unLoRD2; decide +kernel
end CongestionNative

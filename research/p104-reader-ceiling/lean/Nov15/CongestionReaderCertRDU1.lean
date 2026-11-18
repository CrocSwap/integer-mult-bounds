import Nov15.CongestionReaderCertRDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem unRD1 : Fup [(8, 1), (9, -1)] (1 - tRD2) (1 - tRD2) < -unLoRD1 := by unfold tRD2 unLoRD1; decide +kernel
end CongestionNative

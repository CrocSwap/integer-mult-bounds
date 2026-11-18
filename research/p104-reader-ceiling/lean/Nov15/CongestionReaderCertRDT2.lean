import Nov15.CongestionReaderCertRDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRD2 : Fup cfC (1 - tRD2) (1 - tRD2) < 17 * (lcpRD2 - 5 * sgRD2) := by unfold tRD2 lcpRD2 sgRD2; decide +kernel
end CongestionNative

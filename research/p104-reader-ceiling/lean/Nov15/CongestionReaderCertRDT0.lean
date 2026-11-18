import Nov15.CongestionReaderCertRDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRD0 : Fup cfC (1 - tRD0) (1 - tRD0) < 17 * (lcpRD0 - 5 * sgRD0) := by unfold tRD0 lcpRD0 sgRD0; decide +kernel
end CongestionNative

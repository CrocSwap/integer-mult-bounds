import Nov15.CongestionReaderCertRDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRD1 : Fup cfC (1 - tRD1) (1 - tRD1) < 17 * (lcpRD1 - 5 * sgRD1) := by unfold tRD1 lcpRD1 sgRD1; decide +kernel
end CongestionNative

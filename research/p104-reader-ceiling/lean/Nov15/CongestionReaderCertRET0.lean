import Nov15.CongestionReaderCertREDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRE0 : Fup cfC (1 - tRE0) (1 - tRE0) < 17 * (lcpRE0 - 5 * sgRE0) := by unfold tRE0 lcpRE0 sgRE0; decide +kernel
end CongestionNative

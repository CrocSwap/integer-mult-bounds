import Nov15.CongestionReaderCertREDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptRE1 : Fup cfC (1 - tRE1) (1 - tRE1) < 17 * (lcpRE1 - 5 * sgRE1) := by unfold tRE1 lcpRE1 sgRE1; decide +kernel
end CongestionNative

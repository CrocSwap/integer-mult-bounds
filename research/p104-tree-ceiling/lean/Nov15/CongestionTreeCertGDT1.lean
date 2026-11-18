import Nov15.CongestionTreeCertGDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptGD1 : Fup cfC (1 - tGD1) (1 - tGD1) < 17 * (lcpGD1 - 5 * sgGD1) := by unfold tGD1 lcpGD1 sgGD1; decide +kernel
end CongestionNative

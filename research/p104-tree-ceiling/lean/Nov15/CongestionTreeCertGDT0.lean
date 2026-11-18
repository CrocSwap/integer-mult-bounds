import Nov15.CongestionTreeCertGDDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem ptGD0 : Fup cfC (1 - tGD0) (1 - tGD0) < 17 * (lcpGD0 - 5 * sgGD0) := by unfold tGD0 lcpGD0 sgGD0; decide +kernel
end CongestionNative

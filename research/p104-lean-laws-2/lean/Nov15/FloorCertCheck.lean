/-
FloorCertCheck (lane LEAN-NEXT14, Nov 16): the four integer checks of the class-K certificate, by
kernel evaluation (`decide +kernel`; no `native_decide`, no `Lean.ofReduceBool`). Separate file so
the kernel run does not share memory with Mathlib elaboration. See FloorCert.md.
-/
import Nov15.FloorCertData

set_option maxHeartbeats 0

namespace FloorCert

/-! ## 1. The integer checks, by kernel evaluation -/

theorem len_ok : colList.length = nCols ∧ bList.length = nRows := by decide +kernel

theorem Y_nonneg_ok : ∀ i : Fin nRows, 0 ≤ Ytree.get i := by decide +kernel

theorem bDot_ok : bDot Ytree.get bList 0 = 780 * den := by decide +kernel

theorem cols_ok : colList.all (colOK nRows Ytree.get den) = true := by decide +kernel

end FloorCert

#print axioms FloorCert.len_ok
#print axioms FloorCert.Y_nonneg_ok
#print axioms FloorCert.bDot_ok
#print axioms FloorCert.cols_ok

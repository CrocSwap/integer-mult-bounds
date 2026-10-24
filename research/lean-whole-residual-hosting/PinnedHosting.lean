import PhysicalHosting
import PinnedWindow

/-!
Connect the source-derived interval certificate to the window theorem.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

This is a conditional instantiation on retained endpoints whose residual
list matches the four selected masks. It does not identify every raw gate
or cover-class occurrence in the source with these four endpoint events.
Intervening operations can be absorbed into the complete endpoint contracts
only after their required independence and common-chart properties are proved.
-/
namespace WholeHosting.PinnedBitWindow

/-- The selected rank-28 child has empty remainder. For any complete window
with precisely these four residual masks, the hosted window already includes
the child's entire action on the retained state. -/
theorem selected_window_hosting {K A R}
    (events : List (WindowEvent (Fin 64) R))
    (selected : residuals events = residualMasks)
    (s : WindowState (Fin 64) K A R) :
    runHosted events s = onHost pending (runBase events s) := by
  have hd : DisjointMasks (residuals events) := by rw [selected]; exact disjoint
  have hs : MaskSubset (maskUnion (residuals events)) pending := by rw [selected]; exact subset
  have h := whole_hosting events pending hd hs s
  rw [selected, remainder_empty] at h
  exact h

/-- The same selected child result for two different auxiliary-bank layouts.
The physical endpoint contracts, universal in both banks' dirt, remain
premises. The conclusion compares exactly the retained state. -/
theorem selected_physical_hosting {K A R B C}
    {events : List (WindowEvent (Fin 64) R)}
    (program : PhysicalImplementations (K := K) (A := A) B C events)
    (selected : residuals events = residualMasks)
    (s : WindowState (Fin 64) K A R) (oldBank : B) (newBank : C) :
    (program.runRelocated (s, newBank)).1 =
      onHost pending (program.runOriginal (s, oldBank)).1 := by
  rw [program.original_projection, program.relocated_projection]
  exact selected_window_hosting events selected s

end WholeHosting.PinnedBitWindow

#print axioms WholeHosting.PinnedBitWindow.selected_window_hosting
#print axioms WholeHosting.PinnedBitWindow.selected_physical_hosting

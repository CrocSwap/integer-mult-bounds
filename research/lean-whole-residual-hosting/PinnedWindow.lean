import CoordinateSwap

/-!
One literal whole-hosting window selected from PR442's bit template.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

The pinned source and extraction receipt identify idle child 2, copy 27,
replica 0, family 507. Its pending rank is 28. The four whole helper
residuals have intervals [24,28), [0,8), [8,16), [16,24), in stage order
0,1,1,2. The two stage-1 factors have different helper-route selectors;
their order at a fixed physical stream depends on cover enumeration. We check both
representative orders and their equality. This module checks Fin 64 masks.

The interval indices are coordinates in the inherited pending-child chart,
not a proof of that chart's physical address realization. The macro/window
theorem separately handles the intervening program.
-/

namespace WholeHosting.PinnedBitWindow

def interval (lo hi : Nat) : Mask (Fin 64) :=
  fun i => decide (lo ≤ i.val ∧ i.val < hi)

def pending : Mask (Fin 64) := interval 0 28

def residualMasks : List (Mask (Fin 64)) :=
  [interval 24 28, interval 0 8, interval 8 16, interval 16 24]

theorem disjoint : DisjointMasks residualMasks := by
  simp only [DisjointMasks, residualMasks, MasksDisjoint, maskUnion, unionMask, interval]
  decide

theorem subset : MaskSubset (maskUnion residualMasks) pending := by
  simp only [MaskSubset, maskUnion, residualMasks, unionMask, pending, interval]
  decide

theorem coverage : maskUnion residualMasks = pending := by
  funext i
  have h : ∀ j : Fin 64, maskUnion residualMasks j = pending j := by
    simp only [maskUnion, residualMasks, unionMask, interval, pending]
    decide
  exact h i

def reorderedMasks : List (Mask (Fin 64)) :=
  [interval 24 28, interval 8 16, interval 0 8, interval 16 24]

/-- The two same-stage residuals may occur in either cover-class order. -/
theorem same_stage_reorder {K : Type v} {A : Type w}
    (value : Stream (Fin 64) K A) :
    bitFactors residualMasks value = bitFactors reorderedMasks value := by
  simp only [residualMasks, reorderedMasks, bitFactors]
  rw [bitAction_commute (interval 0 8) (interval 8 16)]

theorem remainder_empty : remainderMask pending (maskUnion residualMasks) =
    (fun _ => false) := by
  rw [coverage]
  funext i
  simp [remainderMask]

/-- The four actual interval factors together give the entire pending
rank-28 child for every stream, without any payload cleanliness premise. -/
theorem complete {K : Type v} {A : Type w} (value : Stream (Fin 64) K A) :
    bitFactors residualMasks value = bitAction pending value := by
  rw [bitFactors_union residualMasks disjoint, coverage]

/-- The generic completion theorem also verifies that the emitted zero
remainder has exactly the same action. -/
theorem complete_with_remainder {K : Type v} {A : Type w}
    (value : Stream (Fin 64) K A) :
    bitAction (remainderMask pending (maskUnion residualMasks))
        (bitFactors residualMasks value) = bitAction pending value :=
  bitFactors_complete pending residualMasks disjoint subset value

end WholeHosting.PinnedBitWindow

#print axioms WholeHosting.PinnedBitWindow.disjoint
#print axioms WholeHosting.PinnedBitWindow.subset
#print axioms WholeHosting.PinnedBitWindow.coverage
#print axioms WholeHosting.PinnedBitWindow.same_stage_reorder
#print axioms WholeHosting.PinnedBitWindow.complete
#print axioms WholeHosting.PinnedBitWindow.complete_with_remainder

import Current1094Row1FlatReference

/-!
Consecutive-block family views for the newly defined flat-memory reference.
Family f owns the half-open interval [f*(2*n), (f+1)*(2*n)). This allocation is
an explicit new reference convention. The selected source supplies ordinary
family119 for L119, but does not supply this numeric layout or a primitive tape.

The complete family-view update is derived from actual inside/outside laws of
the reference program, rather than assumed as a projection equality. Every
other family view is preserved. The scalar chart cancellation theorem can then
consume this update once the appropriate Hosting owner map is supplied.

No selected-runtime equivalence, C-token allocation, rounding, scratch cleanup,
physical partial-store norm bound or bit-level instruction cost is claimed.
Prepared with OpenAI assistance. Apache-2.0. Uncompiled source proposal.
-/
set_option Elab.async false
noncomputable section
namespace CurrentMain.Current1094Row1FamilyBlocks

open ComponentStoreFoldRefinement ReferenceMinusHalfStore
open Current1094Row1FlatReference

def familyBase (n f : ℕ) : ℕ := f * (2 * n)

def familyViews (n : ℕ) (memory : ℕ → ℝ) : ℕ → EuclideanSpace ℂ (Fin n) :=
  fun f => decode (fun slot : Slot (Fin n) => memory (flatAddress (familyBase n f) slot))

def executeFamily (n f : ℕ) (s : RefState ℕ) : RefState ℕ :=
  execute (program n (familyBase n f)) s

/-- A slot of any distinct family lies outside the target family's interval.
The n=0 case needs no special assumption: there is then no slot to supply. -/
theorem other_block_outside (n f g : ℕ) (hgf : g ≠ f) (slot : Slot (Fin n)) :
    flatAddress (familyBase n g) slot < familyBase n f ∨
      familyBase n f + 2 * n ≤ flatAddress (familyBase n g) slot := by
  have hb := flatAddress_bounds n (familyBase n g) slot
  by_cases hlt : g < f
  · left
    have hstep : g + 1 ≤ f := by omega
    have hm := Nat.mul_le_mul_right (2 * n) hstep
    simp only [Nat.add_mul, Nat.one_mul] at hm
    unfold familyBase at hb ⊢
    omega
  · right
    have hstep : f + 1 ≤ g := by omega
    have hm := Nat.mul_le_mul_right (2 * n) hstep
    simp only [Nat.add_mul, Nat.one_mul] at hm
    unfold familyBase at hb ⊢
    omega

/-- Actual off-block preservation of the reference instructions lifts to every
other complex family view. No projection or final-state equality is supplied. -/
theorem other_family_unchanged (n f g : ℕ) (hgf : g ≠ f) (s : RefState ℕ) :
    familyViews n (executeFamily n f s).memory g = familyViews n s.memory g := by
  apply PiLp.ext
  intro i
  apply Complex.ext
  · exact program_outside n (familyBase n f) s
      (flatAddress (familyBase n g) (.inl i))
      (other_block_outside n f g hgf (.inl i))
  · exact program_outside n (familyBase n f) s
      (flatAddress (familyBase n g) (.inr i))
      (other_block_outside n f g hgf (.inr i))

/-- The full function of family views changes at exactly one family. The
inside case uses the checked scalar program; the outside case uses disjoint
address intervals. Scratch is still separately visible in executeFamily. -/
theorem familyViews_update (n f : ℕ) (s : RefState ℕ) :
    familyViews n (executeFamily n f s).memory =
      Function.update (familyViews n s.memory) f
        (((-1 / 2 : ℝ) : ℂ) • familyViews n s.memory f) := by
  funext g
  by_cases hgf : g = f
  · subst g
    rw [Function.update_self]
    exact program_complex n (familyBase n f) s
  · rw [Function.update_of_ne hgf]
    exact other_family_unchanged n f g hgf s

/-- Selected raw1's source family number119, under the new explicit consecutive
allocation. This does not identify that allocation with the selected runtime. -/
theorem selected_family119_update (n : ℕ) (s : RefState ℕ) :
    familyViews n (execute (program n (selectedBase n)) s).memory =
      Function.update (familyViews n s.memory) 119
        (((-1 / 2 : ℝ) : ℂ) • familyViews n s.memory 119) := by
  exact familyViews_update n 119 s

end CurrentMain.Current1094Row1FamilyBlocks

#print axioms CurrentMain.Current1094Row1FamilyBlocks.other_block_outside
#print axioms CurrentMain.Current1094Row1FamilyBlocks.other_family_unchanged
#print axioms CurrentMain.Current1094Row1FamilyBlocks.familyViews_update
#print axioms CurrentMain.Current1094Row1FamilyBlocks.selected_family119_update
#check @CurrentMain.Current1094Row1FamilyBlocks.selected_family119_update

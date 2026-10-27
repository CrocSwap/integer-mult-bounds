import SourceInvocationState

/-!
One physical native-coordinate convention for both executions. The two
active owner images overlap exactly on their common data roles. In
particular the hosted private key 9457 is outside the selected original
bank families, whose literal maximum is 9315. A shared cover extension is
essential: choosing identity independently on each inactive image would
give different native interpretations to the same retained host payload.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceInvocation
open SourceConnection FramedReplay
set_option maxRecDepth 100000
set_option maxHeartbeats 0

variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)

theorem parent_family_lt_private : ∀ r : ParentOwnership.Role,
    ParentOwnership.family r < 9457 := by decide

/-- Equality of actual owner keys forces the same data role on both sides;
no original helper or either private temporary participates in an overlap. -/
theorem owner_overlap_data (r s : SourceRaw.Role)
    (he : oldOwner K h2 d r = newOwner K h2 d s) :
    ∃ i : Data, r = SourceLayouts.dataRole i ∧ s = SourceLayouts.dataRole i := by
  have hf := congrArg Prod.fst he
  by_cases hr : r.val < 987
  · by_cases hs : s.val < 987
    · simp only [oldOwner, newOwner, ParentOwnership.sourceActiveOwner,
        SourceOwnership.sourceActiveOwner, SourceOwnership.activeOwner,
        dif_pos hr, dif_pos hs, ParentOwnership.physicalOwner, ParentOwnership.owner,
        SourceOwnership.physicalOwner, SourceOwnership.owner] at hf
      have hn := SourceOwnership.family_lt (⟨s.val, hs⟩ : SourceOwnership.Role)
      have hrd : r.val < 240 := by
        by_contra nh
        have ho := (ParentOwnership.helper_range ⟨r.val, hr⟩
          (show 240 ≤ r.val from Nat.le_of_not_lt nh)).1
        omega
      rw [ParentOwnership.family_data_general _ hrd] at hf
      have hsd : s.val < 240 := by
        by_contra nh
        have ho := (SourceOwnership.helper_range ⟨s.val, hs⟩
          (show 240 ≤ s.val from Nat.le_of_not_lt nh)).1
        change r.val = SourceOwnership.family ⟨s.val, hs⟩ at hf
        omega
      rw [SourceOwnership.family_data_general _ hsd] at hf
      refine ⟨⟨r.val, hrd⟩, ?_, ?_⟩
      · apply Fin.ext; rfl
      · apply Fin.ext; exact hf.symm
    · simp only [oldOwner, newOwner, ParentOwnership.sourceActiveOwner,
        SourceOwnership.sourceActiveOwner, SourceOwnership.activeOwner,
        dif_pos hr, dif_neg hs, ParentOwnership.physicalOwner, ParentOwnership.owner] at hf
      have hp := parent_family_lt_private ⟨r.val, hr⟩
      omega
  · by_cases hs : s.val < 987
    · simp only [oldOwner, newOwner, ParentOwnership.sourceActiveOwner,
        SourceOwnership.sourceActiveOwner, SourceOwnership.activeOwner,
        dif_neg hr, dif_pos hs, SourceOwnership.physicalOwner, SourceOwnership.owner] at hf
      have hn := SourceOwnership.family_lt (⟨s.val, hs⟩ : SourceOwnership.Role)
      omega
    · simp only [oldOwner, newOwner, ParentOwnership.sourceActiveOwner,
        SourceOwnership.sourceActiveOwner, SourceOwnership.activeOwner,
        dif_neg hr, dif_neg hs] at hf
      omega

theorem owner_overlap_charts (r s : SourceRaw.Role)
    (he : oldOwner K h2 d r = newOwner K h2 d s) :
    oldChart K h2 r = newChart K h2 s := by
  obtain ⟨i, rfl, rfl⟩ := owner_overlap_data K h2 d r s he
  exact SourceLayouts.data_chart_eq K h2 i

noncomputable def commonNativeCover :
    Slot K → Gauge (WholeHosting.Address SourceOwnership.Axis K) := by
  classical
  exact fun p => if ∃ r, newOwner K h2 d r = p then
    SourceOwnership.sourceNativeCover K h2 d p
  else ParentOwnership.sourceNativeCover K h2 d p

theorem commonNativeCover_new (r : SourceRaw.Role) :
    commonNativeCover K h2 d (newOwner K h2 d r) =
      SourceOwnership.sourceNativeCover K h2 d (newOwner K h2 d r) := by
  classical
  exact if_pos ⟨r, rfl⟩

theorem new_common_cover (r : SourceRaw.Role)
    (a : WholeHosting.Address SourceOwnership.Axis K) :
    (commonNativeCover K h2 d (newOwner K h2 d r)).forward
      ((newChart K h2 r).forward a) =
      (AddressPairs.gauge (SourceOwnership.pairGauge d)).forward a := by
  rw [commonNativeCover_new]
  exact SourceOwnership.source_common_cover K h2 d r a

theorem old_common_cover (r : SourceRaw.Role)
    (a : WholeHosting.Address SourceOwnership.Axis K) :
    (commonNativeCover K h2 d (oldOwner K h2 d r)).forward
      ((oldChart K h2 r).forward a) =
      (AddressPairs.gauge (SourceOwnership.pairGauge d)).forward a := by
  classical
  unfold commonNativeCover
  split
  · next h =>
      obtain ⟨s, he⟩ := h
      rw [owner_overlap_charts K h2 d r s he.symm, ← he]
      exact SourceOwnership.source_common_cover K h2 d s a
  · exact ParentOwnership.source_common_cover K h2 d r a

#print axioms parent_family_lt_private
#print axioms owner_overlap_data
#print axioms old_common_cover
#print axioms new_common_cover

end SourceInvocation

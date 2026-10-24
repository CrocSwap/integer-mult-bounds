import ParentOwnership
import SourceConnection

/-!
Relations between the two literal owner layouts for the selected invocation.
The 240 data owners and their actual route charts agree. Every one of the
747 hosted helper owners lies outside the entire original active owner
image, including its private temporary. No descriptor-uniqueness premise
or assumed physical nonaliasing is used.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceLayouts
open SourceConnection

def dataRole (i : Data) : SourceOwnership.ActiveRole := ⟨i.val, by omega⟩
def hostRole (h : Host) : SourceOwnership.ActiveRole := ⟨240 + h.val, by omega⟩

theorem data_owner_eq (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K) (i : Data) :
    ParentOwnership.sourceActiveOwner K h2 d (dataRole i) =
      SourceOwnership.sourceActiveOwner K h2 d (dataRole i) := by
  have hi : (dataRole i).val < 987 := by simp only [dataRole]; omega
  have hid : (dataRole i).val < 240 := i.isLt
  simp only [ParentOwnership.sourceActiveOwner, SourceOwnership.sourceActiveOwner,
    SourceOwnership.activeOwner, dif_pos hi,
    ParentOwnership.physicalOwner, ParentOwnership.owner,
    SourceOwnership.physicalOwner, SourceOwnership.owner,
    ParentOwnership.sigmaInverse, SourceOwnership.sigmaInverse, if_pos hid,
    ParentOwnership.sourceDataCharts]
  rw [ParentOwnership.family_data_general _ hid,
    SourceOwnership.family_data_general _ hid]

theorem data_chart_eq (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (i : Data) :
    ParentOwnership.sourceActiveAddressChart K h2 (dataRole i) =
      SourceOwnership.sourceActiveAddressChart K h2 (dataRole i) := by
  have hi : (dataRole i).val < 987 := by simp only [dataRole]; omega
  have hid : (dataRole i).val < 240 := i.isLt
  simp only [ParentOwnership.sourceActiveAddressChart,
    SourceOwnership.sourceActiveAddressChart, ParentOwnership.sourceActiveChart,
    SourceOwnership.sourceActiveChart, ParentOwnership.sourceActiveSigma,
    SourceOwnership.activeSigma, dif_pos hi, ParentOwnership.actualSigma,
    SourceOwnership.actualSigma, if_pos hid, ParentOwnership.sourceDataCharts]

theorem host_family (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K) (h : Host) :
    (SourceOwnership.sourceActiveOwner K h2 d (hostRole h)).1 =
      SourceOwnership.family (role h) := by
  have hh : (hostRole h).val < 987 := by simp only [hostRole]; omega
  simp only [SourceOwnership.sourceActiveOwner, SourceOwnership.activeOwner,
    dif_pos hh, SourceOwnership.physicalOwner, SourceOwnership.owner]
  rfl

theorem parent_owner_ne_host (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
    (r : ParentOwnership.ActiveRole) (h : Host) :
    ParentOwnership.sourceActiveOwner K h2 d r ≠
      SourceOwnership.sourceActiveOwner K h2 d (hostRole h) := by
  have hr : 240 ≤ (role h).val := by simp only [role]; omega
  have hf := SourceOwnership.helper_range (role h) hr
  have hn := ParentOwnership.sourceActiveOwner_avoids_host_families K h2 d r
    (SourceOwnership.family (role h)) hf.1 (by omega)
  intro he
  apply hn
  exact (congrArg Prod.fst he).trans (host_family K h2 d h)

theorem host_ne_parent_owner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
    (h : Host) (r : ParentOwnership.ActiveRole) :
    SourceOwnership.sourceActiveOwner K h2 d (hostRole h) ≠
      ParentOwnership.sourceActiveOwner K h2 d r :=
  Ne.symm (parent_owner_ne_host K h2 d r h)

theorem host_chart_forward (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (h : Host) (a : WholeHosting.Address SourceOwnership.Axis K) :
    (SourceOwnership.sourceActiveAddressChart K h2 (hostRole h)).forward a =
      (SourceOwnership.familyAddressChart K h2 (SourceOwnership.family (role h))).forward
        (SourceOwnership.reindex (SourceOwnership.tag (role h)) a) := by
  exact SourceOwnership.helper_address_forward K h2 (hostRole h)
    (by simp only [hostRole]; omega) (by simp only [hostRole]; omega) a

theorem host_chart_inverse (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (h : Host) (a : WholeHosting.Address SourceOwnership.Axis K) :
    (SourceOwnership.sourceActiveAddressChart K h2 (hostRole h)).inverse a =
      SourceOwnership.unindex (SourceOwnership.tag (role h))
        ((SourceOwnership.familyAddressChart K h2 (SourceOwnership.family (role h))).inverse a) := by
  exact SourceOwnership.helper_address_inverse K h2 (hostRole h)
    (by simp only [hostRole]; omega) (by simp only [hostRole]; omega) a

#print axioms data_owner_eq
#print axioms data_chart_eq
#print axioms parent_owner_ne_host

end SourceLayouts

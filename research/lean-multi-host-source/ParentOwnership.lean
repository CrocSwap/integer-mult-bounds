import ParentOwnershipData
import OwnershipGeometry

/-!
Actual original-bank owners of the selected PR442 forward invocation.
The 59 permutation charts are checked, not assumed distinct. The 61 route
slots are separate: different residual subspaces can share one permutation.
Data roles use the same literal source port charts as the hosted invocation.
Private role 987 belongs to the original template's family 14259.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace ParentOwnership
open SourceOwnership (lookup)
open scoped BigOperators

abbrev Vec (K : Type) := Axis → K

def reindex {K : Type} (t : Tag) (v : Vec K) : Vec K := fun i => v (invPerm t i)
def unindex {K : Type} (t : Tag) (v : Vec K) : Vec K := fun i => v (perm t i)

theorem unindex_reindex {K : Type} (t : Tag) (v : Vec K) :
    unindex t (reindex t v) = v := by
  funext i
  simp only [unindex, reindex, perm_inverse]

theorem reindex_unindex {K : Type} (t : Tag) (v : Vec K) :
    reindex t (unindex t v) = v := by
  funext i
  simp only [unindex, reindex, inverse_perm]

/-- The support statement is indexed by route slot, not permutation tag. -/
theorem residual_projector_transport {K : Type} (zero : K) (s : Slot) (v : Vec K) :
    reindex (slotTag s) (fun i => if sourceMask s i then v i else zero) =
      fun i => if targetMask s i then reindex (slotTag s) v i else zero := by
  funext i
  have hm := perm_support s (invPerm (slotTag s) i)
  rw [inverse_perm] at hm
  simp only [reindex, ← hm]

theorem perm_tag_injective {a b : Tag} (h : perm a = perm b) : a = b := by
  apply fingerprint_injective a b
  unfold fingerprint
  rw [h]

theorem unindex_tag_injective {K : Type} (lo hi : K) (hne : lo ≠ hi)
    {a b : Tag} (h : @unindex K a = @unindex K b) : a = b := by
  apply perm_tag_injective
  funext i
  apply Classical.byContradiction
  intro hn
  let v : Vec K := fun j => if j = perm a i then lo else hi
  have he := congrFun (congrFun h v) i
  have hn' : perm b i ≠ perm a i := fun hh => hn hh.symm
  simp only [unindex, v, if_pos rfl, if_neg hn'] at he
  exact hne he

theorem family_data_general (r : Role) (hr : r.val < 240) : family r = r.val :=
  family_data ⟨r.val, hr⟩

theorem same_family_data {r s : Role} (hf : family r = family s)
    (hr : r.val < 240) : r = s := by
  have hfr := family_data_general r hr
  by_cases hs : s.val < 240
  · apply Fin.ext
    rw [← hfr, hf, family_data_general s hs]
  · have hfs := (helper_range s (Nat.le_of_not_lt hs)).1
    omega

def sigmaInverse {K : Type} (dataInverse : Role → Vec K → Vec K)
    (r : Role) : Vec K → Vec K :=
  if r.val < 240 then dataInverse r else unindex (tag r)

def owner {K : Type} (dataInverse : Role → Vec K → Vec K)
    (d : Vec K → Vec K) (r : Role) : Nat × (Vec K → Vec K) :=
  (family r, fun v => d (sigmaInverse dataInverse r v))

/-- No nonaliasing premise: literal family/tag inversion and faithful
permutation actions establish injectivity for every fixed injective d. -/
theorem owners_injective {K : Type} (lo hi : K) (hne : lo ≠ hi)
    (dataInverse : Role → Vec K → Vec K)
    (d : Vec K → Vec K) (hd : ∀ {x y}, d x = d y → x = y)
    {r s : Role} (h : owner dataInverse d r = owner dataInverse d s) : r = s := by
  have hf : family r = family s := congrArg Prod.fst h
  by_cases hr : r.val < 240
  · exact same_family_data hf hr
  by_cases hs : s.val < 240
  · exact (same_family_data hf.symm hs).symm
  apply family_tag_injective hf
  apply unindex_tag_injective lo hi hne
  funext v
  have ho := congrFun (congrArg Prod.snd h) v
  have he := hd ho
  simpa only [sigmaInverse, if_neg hr, if_neg hs] using he

def axisEquiv (t : Tag) : Axis ≃ Axis where
  toFun := perm t
  invFun := invPerm t
  left_inv := perm_inverse t
  right_inv := inverse_perm t

def slotChart (K : Type) (t : Tag) : Vec K ≃ Vec K where
  toFun := reindex t
  invFun := unindex t
  left_inv := unindex_reindex t
  right_inv := reindex_unindex t

theorem slotChart_dot (K : Type) [CommSemiring K] (t : Tag) (v w : Vec K) :
    (∑ i, slotChart K t v i * slotChart K t w i) = ∑ i, v i * w i := by
  exact (axisEquiv t).symm.sum_comp (fun i => v i * w i)

theorem slotChart_add (K : Type) [Add K] (t : Tag) (v w : Vec K) :
    slotChart K t (v + w) = slotChart K t v + slotChart K t w := rfl

theorem slotChart_smul (K : Type) [Mul K] (t : Tag) (c : K) (v : Vec K) :
    slotChart K t (fun i => c * v i) = fun i => c * slotChart K t v i := rfl

def sourceDataCharts (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) : Vec K ≃ Vec K := SourceOwnership.sourceDataCharts K h2 r

def actualSigma (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) : Vec K ≃ Vec K :=
  if r.val < 240 then sourceDataCharts K h2 r else slotChart K (tag r)

theorem helper_sigma_dot (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) (hr : 240 ≤ r.val) (v w : Vec K) :
    (∑ i, actualSigma K h2 r v i * actualSigma K h2 r w i) = ∑ i, v i * w i := by
  rw [actualSigma, if_neg (Nat.not_lt.mpr hr)]
  exact slotChart_dot K (tag r) v w

theorem helper_sigma_add (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) (hr : 240 ≤ r.val) (v w : Vec K) :
    actualSigma K h2 r (v + w) = actualSigma K h2 r v + actualSigma K h2 r w := by
  simp only [actualSigma, if_neg (Nat.not_lt.mpr hr), slotChart_add]

theorem helper_sigma_smul (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) (hr : 240 ≤ r.val) (c : K) (v : Vec K) :
    actualSigma K h2 r (fun i => c * v i) = fun i => c * actualSigma K h2 r v i := by
  simp only [actualSigma, if_neg (Nat.not_lt.mpr hr), slotChart_smul]

theorem helper_residual_transport (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) (hr : 240 ≤ r.val) (v : Vec K) :
    actualSigma K h2 r (fun i => if sourceMask (slot r) i then v i else 0) =
      fun i => if targetMask (slot r) i then actualSigma K h2 r v i else 0 := by
  simp only [actualSigma, if_neg (Nat.not_lt.mpr hr)]
  exact residual_projector_transport 0 (slot r) v

def physicalOwner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) : Role → Nat × (Vec K → Vec K) :=
  owner (fun r => (sourceDataCharts K h2 r).symm) d

theorem physicalOwner_formula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : Role) :
    physicalOwner K h2 d r = (family r, fun v => d ((actualSigma K h2 r).symm v)) := by
  unfold physicalOwner owner sigmaInverse actualSigma
  split <;> rfl

theorem physicalOwner_injective (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) : Function.Injective (physicalOwner K h2 d) := by
  intro r s h
  exact owners_injective (0 : K) 1 zero_ne_one
    (fun r => (sourceDataCharts K h2 r).symm) d (fun h => d.injective h) h

theorem family_lt (r : Role) : family r < 14259 := by
  by_cases hr : r.val < 240
  · rw [family_data_general r hr]
    omega
  · exact (helper_range r (Nat.le_of_not_lt hr)).2

abbrev ActiveRole := Fin 988

def sourceActiveOwner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) : Nat × (Vec K → Vec K) :=
  if hr : r.val < 987 then physicalOwner K h2 d ⟨r.val, hr⟩ else (14259, id)

/-- Every active parent owner avoids the families used for retained hosts. -/
theorem sourceActiveOwner_avoids_host_families (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) (f : Nat)
    (hf : 240 ≤ f) (hf' : f < 7680) :
    (sourceActiveOwner K h2 d r).1 ≠ f := by
  by_cases hr : r.val < 987
  · simp only [sourceActiveOwner, dif_pos hr, physicalOwner, owner]
    by_cases hd : r.val < 240
    · rw [family_data_general ⟨r.val, hr⟩ hd]
      change r.val ≠ f
      omega
    · have hb := (helper_range ⟨r.val, hr⟩ (Nat.le_of_not_lt hd)).1
      omega
  · simp only [sourceActiveOwner, dif_neg hr]
    omega

def sourceActiveSigma (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) : Vec K ≃ Vec K :=
  if hr : r.val < 987 then actualSigma K h2 ⟨r.val, hr⟩ else Equiv.refl _

def sourceActiveChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) : FramedReplay.Gauge (Vec K × Vec K) :=
  SourceOwnership.pairGauge (sourceActiveSigma K h2 r)

theorem sourceActiveOwner_injective (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) : Function.Injective (sourceActiveOwner K h2 d) := by
  intro r s h
  by_cases hr : r.val < 987
  · by_cases hs : s.val < 987
    · simp only [sourceActiveOwner, dif_pos hr, dif_pos hs] at h
      have he := physicalOwner_injective K h2 d h
      exact Fin.ext (congrArg (fun t : Role => t.val) he)
    · have hf := congrArg Prod.fst h
      simp only [sourceActiveOwner, dif_pos hr, dif_neg hs, physicalOwner, owner] at hf
      have hl := family_lt (⟨r.val, hr⟩ : Role)
      omega
  · by_cases hs : s.val < 987
    · have hf := congrArg Prod.fst h
      simp only [sourceActiveOwner, dif_neg hr, dif_pos hs, physicalOwner, owner] at hf
      have hl := family_lt (⟨s.val, hs⟩ : Role)
      omega
    · apply Fin.ext
      omega

/-- Original-bank charts instantiate the raw-word ownership refinement for
all 988 roles. The event trace and its initial-state relation are arguments. -/
theorem source_gather_run (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K)
    (events : List (OwnerTransport.RouteEvent ActiveRole (Vec K × Vec K)))
    (raw : OwnerTransport.Raw (Nat × (Vec K → Vec K)) (Vec K × Vec K))
    (s : FramedReplay.Store (Vec K × Vec K))
    (full : TreeReplay.Tree.Full 10 s)
    (rel : ∀ r, OwnerTransport.gather (sourceActiveOwner K h2 d)
      (sourceActiveChart K h2) raw r = s.get r.val) :
    ∀ r, OwnerTransport.gather (sourceActiveOwner K h2 d) (sourceActiveChart K h2)
      (OwnerTransport.runRaw (sourceActiveOwner K h2 d) (sourceActiveChart K h2) events raw) r =
      (FramedReplay.runPhysical (events.map OwnerTransport.RouteEvent.framed) s).get r.val :=
  OwnerTransport.gather_run_framed _ _
    (fun h => sourceActiveOwner_injective K h2 d h) events raw s 10 full (by decide) rel

def sourceActiveAddressChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) : FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  AddressPairs.gauge (sourceActiveChart K h2 r)

theorem helper_address_forward (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) (hr : 240 ≤ r.val) (hl : r.val < 987)
    (a : WholeHosting.Address Axis K) :
    (sourceActiveAddressChart K h2 r).forward a = reindex (tag ⟨r.val, hl⟩) a := by
  simp only [sourceActiveAddressChart, sourceActiveChart, sourceActiveSigma, dif_pos hl,
    actualSigma, if_neg (Nat.not_lt.mpr hr), AddressPairs.gauge,
    SourceOwnership.pairGauge, slotChart]
  rfl

theorem helper_address_inverse (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) (hr : 240 ≤ r.val) (hl : r.val < 987)
    (a : WholeHosting.Address Axis K) :
    (sourceActiveAddressChart K h2 r).inverse a = unindex (tag ⟨r.val, hl⟩) a := by
  simp only [sourceActiveAddressChart, sourceActiveChart, sourceActiveSigma, dif_pos hl,
    actualSigma, if_neg (Nat.not_lt.mpr hr), AddressPairs.gauge,
    SourceOwnership.pairGauge, slotChart]
  rfl

theorem source_address_gather_run (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K)
    (events : List (OwnerTransport.RouteEvent ActiveRole (WholeHosting.Address Axis K)))
    (raw : OwnerTransport.Raw (Nat × (Vec K → Vec K)) (WholeHosting.Address Axis K))
    (s : FramedReplay.Store (WholeHosting.Address Axis K))
    (full : TreeReplay.Tree.Full 10 s)
    (rel : ∀ r, OwnerTransport.gather (sourceActiveOwner K h2 d)
      (sourceActiveAddressChart K h2) raw r = s.get r.val) :
    ∀ r, OwnerTransport.gather (sourceActiveOwner K h2 d) (sourceActiveAddressChart K h2)
      (OwnerTransport.runRaw (sourceActiveOwner K h2 d) (sourceActiveAddressChart K h2) events raw) r =
      (FramedReplay.runPhysical (events.map OwnerTransport.RouteEvent.framed) s).get r.val :=
  OwnerTransport.gather_run_framed _ _
    (fun h => sourceActiveOwner_injective K h2 d h) events raw s 10 full (by decide) rel

/-- The reserved private identifier names family14259; its native chart is d.
Every live role uses the actual common-cover chart d ∘ sigma⁻¹. -/
def sourceRoleCover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) :
    FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  AddressPairs.gauge
    (SourceOwnership.pairGauge ((sourceActiveSigma K h2 r).symm.trans d))

noncomputable def sourceNativeCover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) :
    (Nat × (Vec K → Vec K)) → FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  OwnerTransport.extendCover (sourceActiveOwner K h2 d) (sourceRoleCover K h2 d)

theorem source_common_cover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) (a : WholeHosting.Address Axis K) :
    (sourceNativeCover K h2 d (sourceActiveOwner K h2 d r)).forward
      ((sourceActiveAddressChart K h2 r).forward a) =
      (AddressPairs.gauge (SourceOwnership.pairGauge d)).forward a := by
  rw [sourceNativeCover, OwnerTransport.extendCover_owner _
    (fun h => sourceActiveOwner_injective K h2 d h)]
  simp only [sourceRoleCover, sourceActiveAddressChart, sourceActiveChart,
    AddressPairs.gauge, AddressPairs.split_join, SourceOwnership.pairGauge, Equiv.trans_apply,
    Equiv.symm_apply_apply]

theorem source_native_run (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K)
    (events : List (OwnerTransport.RouteEvent ActiveRole (WholeHosting.Address Axis K)))
    (native : OwnerTransport.Raw (Nat × (Vec K → Vec K)) (WholeHosting.Address Axis K)) :
    OwnerTransport.runRaw (sourceActiveOwner K h2 d) (sourceActiveAddressChart K h2)
      events (OwnerTransport.fromNative (sourceNativeCover K h2 d) native) =
      OwnerTransport.fromNative (sourceNativeCover K h2 d)
        (OwnerTransport.runNative (sourceActiveOwner K h2 d)
          (AddressPairs.gauge (SourceOwnership.pairGauge d)) events native) :=
  OwnerTransport.runRaw_fromNative _ _ _ _ (source_common_cover K h2 d) events native

end ParentOwnership
#print axioms ParentOwnership.unindex_tag_injective
#print axioms ParentOwnership.owners_injective
#print axioms ParentOwnership.helper_residual_transport
#print axioms ParentOwnership.sourceActiveOwner_injective
#print axioms ParentOwnership.source_gather_run

#print axioms ParentOwnership.source_common_cover
#print axioms ParentOwnership.source_native_run

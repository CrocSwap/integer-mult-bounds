import Ownership
import PortGeometry
import OwnerTransport
import AddressPairs

/-!
Actual admissible slot charts for every helper of PR442 stage2/replica0.
The source allows a slot isometry followed, when necessary, by U_q ⊕ I.
We construct this choice explicitly: one of the 16 checked permutations,
then the literal source port basis for families 480..719. The inverse
family-chart premise of Ownership.owners_injective is discharged here.

The generic intermediate theorem allows arbitrary bijective data charts,
since their families are separate. The exported source construction fixes
all 240 charts to the literal stage-2 data route from PortGeometry.
This file does not infer any global bound from ownership.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceOwnership
open scoped BigOperators

/-- Literal permutation, including its checked inverse on all 64 axes. -/
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

/-- Child1's pending block is wholly exterior. Child2 uses the actual port
basis on U0; the table theorem helper_child binds this branch to the source. -/
def familyChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (f : Nat) :
    Vec K ≃ Vec K :=
  if 480 ≤ f then PortGeometry.chart64 K h2 ⟨f % 120, Nat.mod_lt _ (by decide)⟩
  else Equiv.refl _

theorem familyChart_dot (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Nat) (v w : Vec K) :
    (∑ i, familyChart K h2 f v i * familyChart K h2 f w i) = ∑ i, v i * w i := by
  unfold familyChart
  split
  · exact PortGeometry.chart64_dot K h2 _ v w
  · rfl

theorem familyChart_add (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Nat) (v w : Vec K) :
    familyChart K h2 f (v + w) = familyChart K h2 f v + familyChart K h2 f w := by
  unfold familyChart
  split
  · exact PortGeometry.chart64_add K h2 _ v w
  · rfl

theorem familyChart_smul (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Nat) (c : K) (v : Vec K) :
    familyChart K h2 f (fun i => c * v i) = fun i => c * familyChart K h2 f v i := by
  unfold familyChart
  split
  · exact PortGeometry.chart64_smul K h2 _ c v
  · rfl

def actualSigma (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (r : Role) : Vec K ≃ Vec K :=
  if r.val < 240 then dataCharts r
  else (slotChart K (tag r)).trans (familyChart K h2 (family r))

theorem helper_sigma_dot (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (r : Role) (hr : 240 ≤ r.val)
    (v w : Vec K) :
    (∑ i, actualSigma K h2 dataCharts r v i * actualSigma K h2 dataCharts r w i) =
      ∑ i, v i * w i := by
  rw [actualSigma, if_neg (Nat.not_lt.mpr hr)]
  change (∑ i, familyChart K h2 (family r) (slotChart K (tag r) v) i *
    familyChart K h2 (family r) (slotChart K (tag r) w) i) = _
  rw [familyChart_dot, slotChart_dot]

theorem helper_sigma_add (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (r : Role) (hr : 240 ≤ r.val)
    (v w : Vec K) :
    actualSigma K h2 dataCharts r (v + w) =
      actualSigma K h2 dataCharts r v + actualSigma K h2 dataCharts r w := by
  simp only [actualSigma, if_neg (Nat.not_lt.mpr hr), Equiv.trans_apply,
    slotChart_add, familyChart_add]

theorem helper_sigma_smul (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (r : Role) (hr : 240 ≤ r.val)
    (c : K) (v : Vec K) :
    actualSigma K h2 dataCharts r (fun i => c * v i) =
      fun i => c * actualSigma K h2 dataCharts r v i := by
  simp only [actualSigma, if_neg (Nat.not_lt.mpr hr), Equiv.trans_apply,
    slotChart_smul, familyChart_smul]

/-- Forward stage2 uses the same literal rho on source and target ports.
The owner formula is d rho, hence sigma is rho inverse. -/
def sourceDataCharts (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : Role) : Vec K ≃ Vec K :=
  (PortGeometry.dataRoute64 K h2 ⟨r.val % 120, Nat.mod_lt _ (by decide)⟩).symm

def physicalOwner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K) :
    Role → Nat × (Vec K → Vec K) :=
  owner (fun r => (dataCharts r).symm) (fun f => (familyChart K h2 f).symm) d

theorem physicalOwner_formula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K) (r : Role) :
    physicalOwner K h2 dataCharts d r =
      (family r, fun v => d ((actualSigma K h2 dataCharts r).symm v)) := by
  unfold physicalOwner owner sigmaInverse actualSigma
  split <;> rfl

theorem physicalOwner_common (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K) (r : Role) (v : Vec K) :
    (physicalOwner K h2 dataCharts d r).2 (actualSigma K h2 dataCharts r v) = d v := by
  rw [physicalOwner_formula]
  exact congrArg d ((actualSigma K h2 dataCharts r).symm_apply_apply v)

/-- Source-specific nonaliasing of every one of the 987 actual live roles,
for every fixed invertible cover element d and every admitted odd field.
The helper sigma maps are constructed, not assumed distinct. -/
theorem physicalOwner_injective (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K) :
    Function.Injective (physicalOwner K h2 dataCharts d) := by
  intro r s h
  exact owners_injective (0 : K) 1 zero_ne_one
    (fun r => (dataCharts r).symm)
    (fun f => familyChart K h2 f) (fun f => (familyChart K h2 f).symm)
    (fun f v => (familyChart K h2 f).symm_apply_apply v) d
    (fun h => d.injective h) h

/-- Gauge for simultaneous transport of the two address halves. -/
def pairGauge {K : Type} (e : Vec K ≃ Vec K) : FramedReplay.Gauge (Vec K × Vec K) where
  forward p := (e p.1, e p.2)
  inverse p := (e.symm p.1, e.symm p.2)
  inverse_forward p := by simp only [Equiv.symm_apply_apply]
  forward_inverse p := by simp only [Equiv.apply_symm_apply]

theorem family_lt (r : Role) : family r < 720 := by
  by_cases hr : r.val < 240
  · rw [family_data_general r hr]
    omega
  · exact (helper_range r (Nat.le_of_not_lt hr)).2

abbrev ActiveRole := Fin 988

/-- The source mapper uses `[LIVE, ['private',0]]` for local register987.
The hosted template has LIVE9457 and explicitly reserves nine private rows;
this invocation uses one such row. Its frame is still tracked separately. -/
def activeOwner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K)
    (r : ActiveRole) : Nat × (Vec K → Vec K) :=
  if hr : r.val < 987 then physicalOwner K h2 dataCharts d ⟨r.val, hr⟩
  else (9457, id)

def activeSigma (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (r : ActiveRole) : Vec K ≃ Vec K :=
  if hr : r.val < 987 then actualSigma K h2 dataCharts ⟨r.val, hr⟩
  else Equiv.refl _

theorem activeOwner_injective (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K) :
    Function.Injective (activeOwner K h2 dataCharts d) := by
  intro r s h
  by_cases hr : r.val < 987
  · by_cases hs : s.val < 987
    · simp only [activeOwner, dif_pos hr, dif_pos hs] at h
      have he := physicalOwner_injective K h2 dataCharts d h
      exact Fin.ext (congrArg (fun t : Role => t.val) he)
    · have hf := congrArg Prod.fst h
      simp only [activeOwner, dif_pos hr, dif_neg hs, physicalOwner, owner] at hf
      have hl := family_lt (⟨r.val, hr⟩ : Role)
      omega
  · by_cases hs : s.val < 987
    · have hf := congrArg Prod.fst h
      simp only [activeOwner, dif_neg hr, dif_pos hs, physicalOwner, owner] at hf
      have hl := family_lt (⟨s.val, hs⟩ : Role)
      omega
    · apply Fin.ext
      omega

/-- The generic raw-to-common-chart event theorem with all ownership and
slot-chart nonaliasing premises discharged for the selected source call. -/
theorem active_gather_step (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (dataCharts : Role → Vec K ≃ Vec K) (d : Vec K ≃ Vec K)
    (raw : OwnerTransport.Raw (Nat × (Vec K → Vec K)) (Vec K × Vec K))
    (op : Nat) (x y : ActiveRole) (odd : Bool)
    (newFrame : FramedReplay.Gauge (Vec K × Vec K)) :
    let own := activeOwner K h2 dataCharts d
    let charts := fun r => pairGauge (activeSigma K h2 dataCharts r)
    OwnerTransport.gather own charts
      (OwnerTransport.rawStep own charts raw op x y odd newFrame) =
      OwnerTransport.logicalStep (OwnerTransport.gather own charts raw)
        op x y odd newFrame := by
  exact OwnerTransport.gather_step _ _
    (fun h => activeOwner_injective K h2 dataCharts d h) _ _ _ _ _ _

def sourceActiveOwner (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) := activeOwner K h2 (sourceDataCharts K h2) d

def sourceActiveChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) : FramedReplay.Gauge (Vec K × Vec K) :=
  pairGauge (activeSigma K h2 (sourceDataCharts K h2) r)

theorem sourceActiveOwner_injective (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) : Function.Injective (sourceActiveOwner K h2 d) :=
  activeOwner_injective K h2 (sourceDataCharts K h2) d

/-- All 988 actual role charts and owners instantiate the whole raw-word
refinement. Only the chosen framed event list and matching initial data are
arguments; no owner or slot-chart hypothesis remains. -/
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

/-- Exact zip/unzip conjugation places the same literal charts on the
pointwise paired-address type used by MultiHosting. -/
def sourceActiveAddressChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) : FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  AddressPairs.gauge (sourceActiveChart K h2 r)

def familyAddressChart (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Nat) : FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  AddressPairs.gauge (pairGauge (familyChart K h2 f))

theorem helper_address_forward (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) (hr : 240 ≤ r.val) (hl : r.val < 987)
    (a : WholeHosting.Address Axis K) :
    (sourceActiveAddressChart K h2 r).forward a =
      (familyAddressChart K h2 (family ⟨r.val, hl⟩)).forward
        (reindex (tag ⟨r.val, hl⟩) a) := by
  simp only [sourceActiveAddressChart, sourceActiveChart, activeSigma, dif_pos hl,
    actualSigma, if_neg (Nat.not_lt.mpr hr), familyAddressChart,
    AddressPairs.gauge, pairGauge, Equiv.trans_apply, slotChart]
  rfl

theorem helper_address_inverse (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (r : ActiveRole) (hr : 240 ≤ r.val) (hl : r.val < 987)
    (a : WholeHosting.Address Axis K) :
    (sourceActiveAddressChart K h2 r).inverse a =
      unindex (tag ⟨r.val, hl⟩)
        ((familyAddressChart K h2 (family ⟨r.val, hl⟩)).inverse a) := by
  simp only [sourceActiveAddressChart, sourceActiveChart, activeSigma, dif_pos hl,
    actualSigma, if_neg (Nat.not_lt.mpr hr), familyAddressChart,
    AddressPairs.gauge, pairGauge, Equiv.symm_trans_apply, slotChart]
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

/-- On live owners this is exactly their cover element g=d sigma⁻¹.
The private identifier `(9457,id)` names reserved private0, not a cover class:
its per-invocation native chart is d, while its local slot chart is identity.
This states that convention explicitly rather than inferring d from id. -/
def sourceRoleCover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) :
    FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  AddressPairs.gauge
    (pairGauge ((activeSigma K h2 (sourceDataCharts K h2) r).symm.trans d))

noncomputable def sourceNativeCover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) :
    (Nat × (Vec K → Vec K)) → FramedReplay.Gauge (WholeHosting.Address Axis K) :=
  OwnerTransport.extendCover (sourceActiveOwner K h2 d) (sourceRoleCover K h2 d)

/-- Actual common-cover cancellation, including the private scratch row. -/
theorem source_common_cover (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K) (r : ActiveRole) (a : WholeHosting.Address Axis K) :
    (sourceNativeCover K h2 d (sourceActiveOwner K h2 d r)).forward
      ((sourceActiveAddressChart K h2 r).forward a) =
      (AddressPairs.gauge (pairGauge d)).forward a := by
  rw [sourceNativeCover, OwnerTransport.extendCover_owner _
    (fun h => sourceActiveOwner_injective K h2 d h)]
  simp only [sourceRoleCover, sourceActiveAddressChart, sourceActiveChart,
    AddressPairs.gauge, AddressPairs.split_join, pairGauge, Equiv.trans_apply,
    Equiv.symm_apply_apply]

/-- The exact same complete raw word is a native word whose XOR operations
read the same native address and whose transports are conjugated only by d.
Owner-chart routing is a coordinate description, not an uncharged interface. -/
theorem source_native_run (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : Vec K ≃ Vec K)
    (events : List (OwnerTransport.RouteEvent ActiveRole (WholeHosting.Address Axis K)))
    (native : OwnerTransport.Raw (Nat × (Vec K → Vec K)) (WholeHosting.Address Axis K)) :
    OwnerTransport.runRaw (sourceActiveOwner K h2 d) (sourceActiveAddressChart K h2)
      events (OwnerTransport.fromNative (sourceNativeCover K h2 d) native) =
      OwnerTransport.fromNative (sourceNativeCover K h2 d)
        (OwnerTransport.runNative (sourceActiveOwner K h2 d)
          (AddressPairs.gauge (pairGauge d)) events native) :=
  OwnerTransport.runRaw_fromNative _ _ _ _ (source_common_cover K h2 d) events native

end SourceOwnership
#print axioms SourceOwnership.slotChart_dot
#print axioms SourceOwnership.helper_sigma_dot
#print axioms SourceOwnership.physicalOwner_injective
#print axioms SourceOwnership.activeOwner_injective
#print axioms SourceOwnership.active_gather_step
#print axioms SourceOwnership.sourceActiveOwner_injective
#print axioms SourceOwnership.source_address_gather_run
#print axioms SourceOwnership.source_common_cover
#print axioms SourceOwnership.source_native_run

import SourceConnection
import SourceFramed

/-!
An endpoint contract for the actual framed invocation, retaining all 747
host streams, all 240 data streams and arbitrary untouched exterior state.
The old helper bank is threaded through its actual outputs. COPY/ERASE
guards and clean-temporary restoration follow from SourceFramed for every
dirty input.

`HelperRelative` is an explicit remaining geometry obligation in this file:
the source's actual initial/final gauges must compose to its declared
residual swap. Distinct physical ownership and the identification of the
gather/scatter maps with source charts are also supplied separately. No
claim that an arbitrary supplied gauge family is the source's geometry is
made here.
-/
namespace PhysicalSourceConnection
open TreeReplay WholeHosting SourceConnection
set_option maxRecDepth 100000
set_option maxHeartbeats 0

-- Prevent elaboration from reducing the full literal execution or frame tables.
-- These remain ordinary transparent definitions checked by the kernel.
attribute [local irreducible] SourceFramed.final SourceFrameTrace.state0 SourceFrameTrace.state96

abbrev Address64 (K : Type) := Address SourceOwnership.Axis K
abbrev Gauges (K : Type) := Nat → FramedReplay.Gauge (Address64 K)

def relative {K : Type} (gauges : Gauges K) (h : Host) (a : Address64 K) : Address64 K :=
  (gauges (SourceFrameTrace.state0.frames.get (240 + h.val))).forward
    ((gauges (SourceFrameTrace.state96.frames.get (240 + h.val))).inverse a)

def HelperRelative {K : Type} (gauges : Gauges K) : Prop :=
  ∀ h a, relative gauges h a =
    swapAddress (SourceOwnership.sourceMask (SourceOwnership.tag (role h))) a

def physicalData {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) : Data → Streams K :=
  fun i => ((SourceFramed.final gauges (packed data helpers)).get i.val).2

def physicalHelpers {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) : Host → Streams K :=
  fun h => ((SourceFramed.final gauges (packed data helpers)).get (240 + h.val)).2

theorem helper_endpoints {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) :
    physicalHelpers gauges data helpers = fun h a => helpers h (relative gauges h a) := by
  have he := congrArg
    (fun values : Fin 1024 → Streams K => fun h : Host => values ⟨240 + h.val, by omega⟩)
    (SourceFramed.all_physical_endpoints gauges (packed data helpers))
  apply he.trans
  funext h a
  have hr : 240 + h.val < 987 := by omega
  have ht : ¬ 240 + h.val < 240 := by omega
  simp only [SourceMatrix.endpointPayload, hr, ht, and_false, ↓reduceIte,
    SourceFramed.normalizedInput, packed_helper, relative]

theorem helper_endpoint {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) (h : Host) :
    physicalHelpers gauges data helpers h = fun a => helpers h (relative gauges h a) :=
  congrFun (helper_endpoints gauges data helpers) h

#print axioms helper_endpoints
#print axioms helper_endpoint

theorem physical_data_endpoints {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) :
    physicalData gauges data helpers = fun i a =>
      SourceMatrix.endpointPayload (SourceFramed.normalizedInput gauges (packed data helpers))
        i.val ((gauges (SourceFrameTrace.state96.frames.get i.val)).inverse a) := by
  exact congrArg
    (fun values : Fin 1024 → Streams K => fun i : Data => values ⟨i.val, by omega⟩)
    (SourceFramed.all_physical_endpoints gauges (packed data helpers))

/-- Independence is proved from the literal word for every dirty bank.
The zero bank below is only a name for the resulting data-only function. -/
theorem data_independent {K : Type} (gauges : Gauges K) (data : Data → Streams K)
    (left right : Host → Streams K) : physicalData gauges data left = physicalData gauges data right := by
  rw [physical_data_endpoints, physical_data_endpoints]
  funext i a
  have hi : i.val < 987 := by omega
  by_cases ht : 120 ≤ i.val
  · have hs : i.val - 120 < 240 := by omega
    simp [SourceMatrix.endpointPayload, SourceFramed.normalizedInput,
      packed, hi, ht, i.isLt, hs]
  · simp [SourceMatrix.endpointPayload, SourceFramed.normalizedInput,
      packed, hi, ht, i.isLt]

#print axioms physical_data_endpoints
#print axioms data_independent

def dataEndpoint {K : Type} (gauges : Gauges K) (data : Data → Streams K) : Data → Streams K :=
  physicalData gauges data (fun _ _ => false)

theorem data_endpoint {K : Type} (gauges : Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) :
    physicalData gauges data helpers = dataEndpoint gauges data :=
  data_independent gauges data helpers (fun _ _ => false)

def scatterHost {K : Type} (h : Host) (v : Streams K) : Streams K :=
  fun a => v (SourceOwnership.unindex (SourceOwnership.tag (role h)) a)

/-- This uses arbitrary-helper endpoint identity first, then the actual
relative frame equation. It does not equate physical initial data with the
convenient normalized input used by SourceConnection.invoke. -/
theorem hosted_endpoint {K : Type} (gauges : Gauges K) (geometry : HelperRelative gauges)
    (data : Data → Streams K) (hosts : Host → Streams K) (h : Host) :
    scatterHost h (physicalHelpers gauges data (fun j => hostInput j (hosts j)) h) =
      bitAction (residual h) (hosts h) := by
  rw [helper_endpoint]
  funext a
  change hosts h (SourceOwnership.reindex (SourceOwnership.tag (role h))
    (relative gauges h (SourceOwnership.unindex (SourceOwnership.tag (role h)) a))) = _
  rw [geometry]
  exact congrArg (hosts h) (swap_conjugacy _ a)

def event {K : Type} {Tail : Type v} (gauges : Gauges K)
    (dataInput dataOutput : Data → Streams K → Streams K) :
    MultiHosting.WindowEvent Host SourceOwnership.Axis (Retained K Tail) where
  idle := fun _ _ => false
  residual := residual
  other s := (fun i => dataOutput i (dataEndpoint gauges (fun j => dataInput j (s.1 j)) i), s.2)

def original {K : Type} {Tail : Type v} (gauges : Gauges K)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail) ×
      (Host → Streams K)) :=
  let data := fun i => dataInput i (s.1.2.1 i)
  let helpers := fun h => oldInput h (s.2 h)
  ((s.1.1, (fun i : Data => dataOutput i (physicalData gauges data helpers i), s.1.2.2)),
    fun h : Host => oldOutput h (physicalHelpers gauges data helpers h))

def relocated {K : Type} {Tail : Type v} (gauges : Gauges K)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail) × Unit) :=
  let data := fun i => dataInput i (s.1.2.1 i)
  let helpers := fun h => hostInput h (s.1.1 h)
  ((fun h : Host => scatterHost h (physicalHelpers gauges data helpers h),
    (fun i : Data => dataOutput i (physicalData gauges data helpers i), s.1.2.2)), s.2)

theorem original_retained {K : Type} {Tail : Type v} (gauges : Gauges K)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (bank : Host → Streams K) :
    (original gauges dataInput dataOutput oldInput oldOutput (s, bank)).1 =
      (event gauges dataInput dataOutput).base s := by
  apply Prod.ext
  · funext h; exact (bitAction_empty (s.1 h)).symm
  · apply Prod.ext
    · funext i
      exact congrArg (dataOutput i) (congrFun
        (data_endpoint gauges (fun j => dataInput j (s.2.1 j))
          (fun h => oldInput h (bank h))) i)
    · rfl

theorem relocated_retained {K : Type} {Tail : Type v} (gauges : Gauges K)
    (geometry : HelperRelative gauges)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (bank : Unit) :
    (relocated gauges dataInput dataOutput (s, bank)).1 =
      (event gauges dataInput dataOutput).hosted s := by
  apply Prod.ext
  · funext h
    change scatterHost h (physicalHelpers gauges _ _ h) =
      bitAction (residual h) (bitAction (fun _ => false) (s.1 h))
    rw [bitAction_empty]
    exact hosted_endpoint gauges geometry _ s.1 h
  · apply Prod.ext
    · funext i
      exact congrArg (dataOutput i) (congrFun
        (data_endpoint gauges (fun j => dataInput j (s.2.1 j))
          (fun h => hostInput h (s.1 h))) i)
    · rfl

def contract {K : Type} {Tail : Type v} (gauges : Gauges K) (geometry : HelperRelative gauges)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K) :
    MultiHosting.PhysicalContract (K := K) (A := Bool)
      (event (Tail := Tail) gauges dataInput dataOutput) (Host → Streams K) Unit where
  original := original gauges dataInput dataOutput oldInput oldOutput
  relocated := relocated gauges dataInput dataOutput
  original_retained := original_retained gauges dataInput dataOutput oldInput oldOutput
  relocated_retained := relocated_retained gauges geometry dataInput dataOutput

/-- Actual child pending coordinates in the selected stage-2 invocation.
Child 1 has coordinates 15..21; child 2 has coordinates 1..28. -/
def pendingTag (t : SourceOwnership.Tag) : Mask SourceOwnership.Axis := fun i =>
  if SourceOwnership.lookup SourceOwnership.tagChild t.val = 1 then
    decide (15 ≤ i.val ∧ i.val < 22)
  else decide (1 ≤ i.val ∧ i.val < 29)

theorem tag_child_cases : ∀ t : SourceOwnership.Tag,
    SourceOwnership.lookup SourceOwnership.tagChild t.val = 1 ∨
      SourceOwnership.lookup SourceOwnership.tagChild t.val = 2 := by decide

theorem tag_pending_contains : ∀ (t : SourceOwnership.Tag) (i : SourceOwnership.Axis),
    SourceOwnership.targetMask t i = true → pendingTag t i = true := by decide

def pending : MultiHosting.HostMask Host SourceOwnership.Axis :=
  fun h => pendingTag (SourceOwnership.tag (role h))

/-- Application to this one invocation. The remaining pending swap is
explicitly charged on each affected host. This is not a whole-cover sweep
or an asymptotic cost/bound theorem. `geometry` is discharged by the concrete
source gauge connector, not by this abstract application. -/
theorem selected_invocation_completion {K : Type} {Tail : Type v} (gauges : Gauges K)
    (geometry : HelperRelative gauges)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (oldBank : Host → Streams K) (newBank : Unit) :
    MultiHosting.onHosts (MultiHosting.remainders pending [event (Tail := Tail) gauges dataInput dataOutput])
      (relocated gauges dataInput dataOutput (s, newBank)).1 =
    MultiHosting.onHosts pending
      (original gauges dataInput dataOutput oldInput oldOutput (s, oldBank)).1 := by
  have hd : ∀ h, DisjointMasks
      (MultiHosting.residuals [event (Tail := Tail) gauges dataInput dataOutput] h) := by
    intro h
    simp [MultiHosting.residuals, DisjointMasks, MasksDisjoint, maskUnion]
  have hs : ∀ h, MaskSubset
      (MultiHosting.masksUnion [event (Tail := Tail) gauges dataInput dataOutput] h) (pending h) := by
    intro h i hi
    have ht : SourceOwnership.targetMask (SourceOwnership.tag (role h)) i = true := by
      simpa [MultiHosting.masksUnion, MultiHosting.residuals, event, maskUnion,
        unionMask, residual] using hi
    exact tag_pending_contains _ i ht
  exact MultiHosting.physical_multi_hosting
    (.cons (contract gauges geometry dataInput dataOutput oldInput oldOutput) .nil)
    pending hd hs s oldBank newBank

#print axioms data_endpoint
#print axioms hosted_endpoint
#print axioms original_retained
#print axioms relocated_retained
#print axioms tag_child_cases
#print axioms tag_pending_contains
#print axioms selected_invocation_completion

end PhysicalSourceConnection

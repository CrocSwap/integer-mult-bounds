import SourceInvocationComparison
import SourceInitialPayload
import SourceNativeInvocation
import SelectedGeometry
import SourceMoveGeometry
import SourceDataBehavior

/-!
The selected PR442 stage2/replica0 invocation, connected to MultiHosting.

The maps below are the literal source data routes, the 747 constructed host
owners/charts, the original parent-bank owners/charts, and all 19,002 source
events. No geometry, ownership, clean-work or input-matching premise is
assumed. Every retained host, all 240 data streams, the exterior of both
active owner images, and all 747 old-bank inputs are arbitrary Boolean
functions on paired 64-dimensional addresses.

This is one local invocation. The displayed completion applies the remaining
pending swaps immediately in the abstract window. It does not prove their
later positions in the real recursive schedule, a whole-cover sweep, a global
bank renumbering, a register-cost saving, or a new kappa bound.
-/
namespace SourceInvocation
open SourceConnection FramedReplay
variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
set_option maxRecDepth 100000
set_option maxHeartbeats 0
attribute [local irreducible] SourceRaw.final SourceFramed.final

/-- A concrete physical contract for the actual old and relocated raw
instruction folds. Even the original-bank outputs are the actual outputs
of that fold; they have not been replaced with their initial values. -/
noncomputable def actualContract :
    MultiHosting.PhysicalContract (K := K) (A := Bool)
      (PhysicalSourceConnection.event (Tail := Tail K h2 d)
        (SelectedGeometry.gauges K h2) (dataInput K h2) (dataOutput K h2))
      (Host → Streams K) Unit where
  original := oldResult K h2 d (SelectedGeometry.gauges K h2)
  relocated := newResult K h2 d (SelectedGeometry.gauges K h2)
  original_retained s bank :=
    (congrArg Prod.fst (oldResult_framed K h2 d (SelectedGeometry.gauges K h2) s bank)).trans
      (PhysicalSourceConnection.original_retained _ _ _ _ _ s bank)
  relocated_retained s bank :=
    (congrArg Prod.fst (newResult_framed K h2 d (SelectedGeometry.gauges K h2) s bank)).trans
      (PhysicalSourceConnection.relocated_retained _ (SelectedGeometry.helper_relative K h2)
        _ _ s bank)

/-- All retained outputs of this actual invocation satisfy the multi-host
completion equation, for arbitrary dirty input. The only algebraic condition
is characteristic different from two; d is any invertible cover map.
Child-1 pending coordinates are 15..21 and child-2 coordinates are 1..28. -/
theorem selected_call_completion (s : State K h2 d) (oldBank : Host → Streams K) :
    MultiHosting.onHosts
      (MultiHosting.remainders PhysicalSourceConnection.pending
        [PhysicalSourceConnection.event (Tail := Tail K h2 d) (SelectedGeometry.gauges K h2)
          (dataInput K h2) (dataOutput K h2)])
      (newResult K h2 d (SelectedGeometry.gauges K h2) (s, ())).1 =
    MultiHosting.onHosts PhysicalSourceConnection.pending
      (oldResult K h2 d (SelectedGeometry.gauges K h2) (s, oldBank)).1 := by
  have hn := congrArg
    (fun out : State K h2 d × Unit =>
      MultiHosting.onHosts
        (MultiHosting.remainders PhysicalSourceConnection.pending
          [PhysicalSourceConnection.event (Tail := Tail K h2 d) (SelectedGeometry.gauges K h2)
            (dataInput K h2) (dataOutput K h2)]) out.1)
    (newResult_framed K h2 d (SelectedGeometry.gauges K h2) s ())
  have ho := congrArg
    (fun out : State K h2 d × (Host → Streams K) =>
      MultiHosting.onHosts PhysicalSourceConnection.pending out.1)
    (oldResult_framed K h2 d (SelectedGeometry.gauges K h2) s oldBank)
  exact hn.trans ((PhysicalSourceConnection.selected_invocation_completion
    (SelectedGeometry.gauges K h2) (SelectedGeometry.helper_relative K h2)
    (dataInput K h2) (dataOutput K h2) (oldInput K h2) (oldOutput K h2)
    s oldBank ()).trans ho.symm)

/-- The same completion equation for the native source folds themselves,
read in the common retained coordinate charts. The preceding input identity
lemmas guarantee that these runs start with the same retained native data. -/
theorem selected_native_completion (s : State K h2 d) (oldBank : Host → Streams K) :
    MultiHosting.onHosts
      (MultiHosting.remainders PhysicalSourceConnection.pending
        [PhysicalSourceConnection.event (Tail := Tail K h2 d) (SelectedGeometry.gauges K h2)
          (dataInput K h2) (dataOutput K h2)])
      (newNativeResult K h2 d (SelectedGeometry.gauges K h2) (s, ())).1 =
    MultiHosting.onHosts PhysicalSourceConnection.pending
      (oldNativeResult K h2 d (SelectedGeometry.gauges K h2) (s, oldBank)).1 := by
  have hn := congrArg
    (fun out : State K h2 d × Unit =>
      MultiHosting.onHosts
        (MultiHosting.remainders PhysicalSourceConnection.pending
          [PhysicalSourceConnection.event (Tail := Tail K h2 d) (SelectedGeometry.gauges K h2)
            (dataInput K h2) (dataOutput K h2)]) out.1)
    (newResult_native K h2 d (SelectedGeometry.gauges K h2) s ())
  have ho := congrArg
    (fun out : State K h2 d × (Host → Streams K) =>
      MultiHosting.onHosts PhysicalSourceConnection.pending out.1)
    (oldResult_native K h2 d (SelectedGeometry.gauges K h2) s oldBank)
  exact hn.symm.trans ((selected_call_completion K h2 d s oldBank).trans ho)

/-- Concrete data behavior, including each port's actual initial/final
frame and its literal rho chart. The target term is XOR source; the displayed
coordinate pullbacks are retained rather than silently made identities. -/
theorem selected_data_formula (s : State K h2 d) (oldBank : Host → Streams K) (i : Data) :
    (oldRaw K h2 d (SelectedGeometry.gauges K h2) s oldBank
      (oldOwner K h2 d (SourceLayouts.dataRole i))).2 =
      SourceDataBehavior.dataFormula K h2 (SelectedGeometry.gauges K h2) s.2.1 i ∧
    (newRaw K h2 d (SelectedGeometry.gauges K h2) s
      (newOwner K h2 d (SourceLayouts.dataRole i))).2 =
      SourceDataBehavior.dataFormula K h2 (SelectedGeometry.gauges K h2) s.2.1 i :=
  ⟨SourceDataBehavior.old_data_formula K h2 d _ s oldBank i,
    SourceDataBehavior.new_data_formula K h2 d _ s i⟩

/-- These are two coordinate descriptions of the very same native source
fold, with all initial payloads constructed explicitly. Thus the contract
above does not posit an extra routed interface for the physical XOR gates. -/
theorem selected_native_realization (s : State K h2 d) (oldBank : Host → Streams K) :
    oldRaw K h2 d (SelectedGeometry.gauges K h2) s oldBank =
      OwnerTransport.fromNative (commonNativeCover K h2 d)
        (oldNative K h2 d (SelectedGeometry.gauges K h2) s oldBank) ∧
    newRaw K h2 d (SelectedGeometry.gauges K h2) s =
      OwnerTransport.fromNative (commonNativeCover K h2 d)
        (newNative K h2 d (SelectedGeometry.gauges K h2) s) :=
  ⟨old_native_realization K h2 d _ s oldBank, new_native_realization K h2 d _ s⟩

/-- COPY blankness and ERASE equality follow the actual native trajectories;
there is no clean assumption on any of the 987 original streams. -/
theorem selected_native_clean (s : State K h2 d) (oldBank : Host → Streams K) :
    SourceRawGuards.NativeCleanRun (oldOwner K h2 d) (nativeGauge K d)
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2)))
      (SourceRaw.initial (oldOwner K h2 d) (SelectedGeometry.gauges K h2)
        (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s oldBank))) ∧
    SourceRawGuards.NativeCleanRun (newOwner K h2 d) (nativeGauge K d)
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2)))
      (SourceRaw.initial (newOwner K h2 d) (SelectedGeometry.gauges K h2)
        (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s))) :=
  ⟨old_native_clean K h2 d _ s oldBank, new_native_clean K h2 d _ s⟩

/-- The complete actual relocated raw invocation also realizes the literal
matrix operators: every MOVE is D_(Pnew-Pold), and COPY uses the full local
8-coordinate transport. This equality includes frame metadata and payloads. -/
theorem selected_matrix_realization (s : State K h2 d) :
    (fun r => OwnerTransport.gather (newOwner K h2 d) (newChart K h2)
      (newRaw K h2 d (SelectedGeometry.gauges K h2) s) r) =
    fun r => (SourceMoveGeometry.matrixRun K h2 SourceFrameTrace.forward
      (SourceFramed.initial (SelectedGeometry.gauges K h2)
        (packed (fun i => dataInput K h2 i (s.2.1 i))
          (fun h => hostInput h (s.1 h))))).get r.val := by
  have hg := funext (InvocationPayload.realized_gather (newOwner K h2 d) (newChart K h2)
    (fun h => newOwner_injective K h2 d h) (SelectedGeometry.gauges K h2)
    (fun i => dataInput K h2 i (s.2.1 i)) (fun h => hostInput h (s.1 h))
    (tailPayload K h2 d s))
  exact hg.trans (congrArg
    (fun store : FramedReplay.Store (WholeHosting.Address SourceOwnership.Axis K) =>
      fun r : SourceRaw.Role => store.get r.val)
    (SourceMoveGeometry.actual_matrix_run K h2 _).symm)

/-- The original-bank invocation uses the same certified matrix word. -/
theorem selected_original_matrix_realization (s : State K h2 d)
    (bank : Host → Streams K) :
    (fun r => OwnerTransport.gather (oldOwner K h2 d) (oldChart K h2)
      (oldRaw K h2 d (SelectedGeometry.gauges K h2) s bank) r) =
    fun r => (SourceMoveGeometry.matrixRun K h2 SourceFrameTrace.forward
      (SourceFramed.initial (SelectedGeometry.gauges K h2)
        (packed (fun i => dataInput K h2 i (s.2.1 i))
          (fun h => oldInput K h2 h (bank h))))).get r.val := by
  have hg := funext (InvocationPayload.realized_gather (oldOwner K h2 d) (oldChart K h2)
    (fun h => oldOwner_injective K h2 d h) (SelectedGeometry.gauges K h2)
    (fun i => dataInput K h2 i (s.2.1 i)) (fun h => oldInput K h2 h (bank h))
    (hostPayload K h2 d s))
  exact hg.trans (congrArg
    (fun store : FramedReplay.Store (WholeHosting.Address SourceOwnership.Axis K) =>
      fun r : SourceRaw.Role => store.get r.val)
    (SourceMoveGeometry.actual_matrix_run K h2 _).symm)

/-- Both physical private temporaries are returned blank. -/
theorem selected_temporary_restoration (s : State K h2 d) (oldBank : Host → Streams K) :
    (oldNative K h2 d (SelectedGeometry.gauges K h2) s oldBank
      (oldOwner K h2 d SourceRaw.privateRow)).2 = (fun _ => false) ∧
    (newNative K h2 d (SelectedGeometry.gauges K h2) s
      (newOwner K h2 d SourceRaw.privateRow)).2 = (fun _ => false) :=
  ⟨old_native_temporary_restored K h2 d _ s oldBank,
    new_native_temporary_restored K h2 d _ s⟩

end SourceInvocation

#print axioms SourceInvocation.selected_call_completion
#print axioms SourceInvocation.selected_native_realization
#print axioms SourceInvocation.selected_native_clean
#print axioms SourceInvocation.selected_matrix_realization
#print axioms SourceInvocation.selected_original_matrix_realization
#print axioms SourceInvocation.selected_temporary_restoration

#print axioms SourceInvocation.selected_native_completion
#print axioms SourceInvocation.selected_data_formula

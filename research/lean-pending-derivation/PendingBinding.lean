import PhysicalSourceConnection
import PendingDerivation

/-!
Binds PR540's hand-supplied `PhysicalSourceConnection.pendingTag` to the
schedule-derived pending sets of `PendingDerivation`. It restates the
selected-invocation completion theorem with the derived mask. No existing
definition or theorem is changed.

Apache-2.0. Douglas Colkitt, with Claude (Anthropic) assistance.
-/
namespace PendingBinding
open TreeReplay WholeHosting SourceConnection PhysicalSourceConnection

/-- The hand-supplied ranges `[15,22)` and `[1,29)` are exactly the derived sets. -/
theorem pendingTag_derived : ∀ (t : SourceOwnership.Tag) (i : SourceOwnership.Axis),
    pendingTag t i = PendingDerivation.derivedPendingTag t i := by
  decide +kernel

/-- Pending mask of every host, derived from the source schedule. -/
def derivedPending : MultiHosting.HostMask Host SourceOwnership.Axis :=
  fun h => PendingDerivation.derivedPendingTag (SourceOwnership.tag (role h))

theorem pending_eq_derived : pending = derivedPending := by
  funext h i
  exact pendingTag_derived _ _

/-- `selected_invocation_completion` with the schedule-derived pending mask. -/
theorem selected_invocation_completion_derived {K : Type} {Tail : Type v}
    (gauges : Gauges K) (geometry : HelperRelative gauges)
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (oldBank : Host → Streams K) (newBank : Unit) :
    MultiHosting.onHosts
        (MultiHosting.remainders derivedPending [event (Tail := Tail) gauges dataInput dataOutput])
        (relocated gauges dataInput dataOutput (s, newBank)).1 =
      MultiHosting.onHosts derivedPending
        (original gauges dataInput dataOutput oldInput oldOutput (s, oldBank)).1 := by
  rw [← pending_eq_derived]
  exact selected_invocation_completion gauges geometry dataInput dataOutput oldInput oldOutput
    s oldBank newBank

end PendingBinding

#print axioms PendingBinding.pendingTag_derived
#print axioms PendingBinding.pending_eq_derived
#print axioms PendingBinding.selected_invocation_completion_derived

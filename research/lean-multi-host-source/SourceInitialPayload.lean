import SourceInvocationState

/-!
The explicit raw input constructions preserve all displayed arbitrary inputs.
The 240 data streams and all 747 retained hosts agree between the original
and relocated calls. The original helper bank remains an independent,
arbitrary input. These identities concern physical owner-cover payloads,
before any framed instruction executes.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceInvocation
open SourceConnection FramedReplay

variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)

theorem newPayload_host (s : State K h2 d) (h : Host) :
    newPayload K h2 d s (hostOwner K h2 d h) =
      fun a => s.1 h ((hostChart K h2 h).inverse a) := by
  unfold newPayload hostOwner
  rw [InvocationPayload.realize_owner _ (newChart K h2)
    (fun he => newOwner_injective K h2 d he)]
  funext a
  change packed _ _ (240 + h.val) _ = _
  rw [packed_helper]
  change s.1 h (SourceOwnership.reindex (SourceOwnership.tag (role h))
    ((SourceOwnership.sourceActiveAddressChart K h2 (SourceLayouts.hostRole h)).inverse a)) = _
  rw [SourceLayouts.host_chart_inverse, SourceOwnership.reindex_unindex]
  rfl

theorem oldPayload_data (s : State K h2 d) (bank : Host → Streams K) (i : Data) :
    oldPayload K h2 d s bank (oldOwner K h2 d (SourceLayouts.dataRole i)) = s.2.1 i := by
  unfold oldPayload
  rw [InvocationPayload.realize_owner _ (oldChart K h2)
    (fun he => oldOwner_injective K h2 d he)]
  funext a
  change packed _ _ i.val _ = _
  rw [packed_data]
  change s.2.1 i ((SourceOwnership.sourceActiveAddressChart K h2
    (SourceLayouts.dataRole i)).forward
      ((ParentOwnership.sourceActiveAddressChart K h2 (SourceLayouts.dataRole i)).inverse a)) = _
  rw [SourceLayouts.data_chart_eq]
  exact congrArg (s.2.1 i) (Gauge.forward_inverse _ a)

theorem newPayload_data (s : State K h2 d) (i : Data) :
    newPayload K h2 d s (newOwner K h2 d (SourceLayouts.dataRole i)) = s.2.1 i := by
  unfold newPayload
  rw [InvocationPayload.realize_owner _ (newChart K h2)
    (fun he => newOwner_injective K h2 d he)]
  funext a
  change packed _ _ i.val _ = _
  rw [packed_data]
  exact congrArg (s.2.1 i) ((newChart K h2 (SourceLayouts.dataRole i)).forward_inverse a)

theorem oldPayload_bank (s : State K h2 d) (bank : Host → Streams K) (h : Host) :
    oldPayload K h2 d s bank (oldOwner K h2 d (SourceLayouts.hostRole h)) = bank h := by
  unfold oldPayload
  rw [InvocationPayload.realize_owner _ (oldChart K h2)
    (fun he => oldOwner_injective K h2 d he)]
  funext a
  change packed _ _ (240 + h.val) _ = _
  rw [packed_helper]
  exact congrArg (bank h) ((oldChart K h2 (SourceLayouts.hostRole h)).forward_inverse a)

theorem shared_host_input (s : State K h2 d) (bank : Host → Streams K) (h : Host) :
    oldPayload K h2 d s bank (hostOwner K h2 d h) =
      newPayload K h2 d s (hostOwner K h2 d h) := by
  rw [oldPayload_host, newPayload_host]

theorem shared_data_input (s : State K h2 d) (bank : Host → Streams K) (i : Data) :
    oldPayload K h2 d s bank (oldOwner K h2 d (SourceLayouts.dataRole i)) =
      newPayload K h2 d s (newOwner K h2 d (SourceLayouts.dataRole i)) := by
  rw [oldPayload_data, newPayload_data]

#print axioms newPayload_host
#print axioms oldPayload_data
#print axioms newPayload_data
#print axioms oldPayload_bank
#print axioms shared_host_input

end SourceInvocation

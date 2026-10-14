/- Complete one-owner interface for the selected PR531 invocation registers.
Apache-2.0. Rohan Arun with substantial OpenAI Codex assistance.
This proves ownership within an atomic invocation. It does not yet establish
physical charts, exact recipes, or the execution/scheduling model itself. -/
import PR531TableCertificate
import PR531DataWindows
namespace OwnerTransport.PR531InvocationOwners
open OwnerTable OwnerSeparation PR531Table PR531DataWindows

/-- All 224 data wires and 504 helpers have distinct owners in each of 72 calls. -/
theorem one_owner_per_invocation (t : Nat) (ht : t < witness.calls) :
    ∀ a b : Sum (Fin 2 × Fin witness.ports) (Fin witness.helpers),
      invocationOwner witness stagePair t a = invocationOwner witness stagePair t b → a = b :=
  invocation_owners_injective witness accepted stagePair windows_avoid_data t ht (active_pair_fits t ht)

/-- No selected helper is hosted by an active data wire of the same invocation. -/
theorem no_helper_on_active_data (t : Nat) (ht : t < witness.calls)
    (helper : Fin witness.helpers) (bank : Fin 2) (port : Fin witness.ports) :
    helperOwner witness t helper ≠ mainOwner witness stagePair t bank port :=
  helper_main_distinct witness accepted stagePair windows_avoid_data t ht
    (active_pair_fits t ht) helper bank port

end OwnerTransport.PR531InvocationOwners

/- Controller-backed one-owner theorem for the selected finite construction.
Apache-2.0. Rohan Arun with substantial OpenAI Codex assistance.
The source controller is certified as a finite trace. Relating its touches,
charts and atomic events to the fixed-tape machine remains unproved. -/
import PR531TableCertificate
import PR531Controller
namespace OwnerTransport.PR531ScheduledOwners
open OwnerTable OwnerSeparation PR531Table PR531DataWindows

/-- The traced controller discharges the one-owner premise for every register. -/
theorem one_owner_per_call (t : Nat) (ht : t < witness.calls) :
    ∀ a b : Sum (Fin 2 × Fin witness.ports) (Fin witness.helpers),
      invocationOwner witness stagePair t a = invocationOwner witness stagePair t b → a = b :=
  invocation_owners_injective witness PR531Table.accepted stagePair
    PR531Controller.controller_windows_avoid_data t ht (active_pair_fits t ht)

/-- Every actual helper call occurs strictly inside its traced borrowing window. -/
theorem every_helper_inside_controller_window (i : Nat) (hi : i < rowCount witness) :
    let g := (witness.row i).ownerReplica * witness.children + (witness.row i).child
    (PR531Controller.trace.bounds g).1 < PR531Controller.trace.callPosition (witness.row i).time ∧
      PR531Controller.trace.callPosition (witness.row i).time < (PR531Controller.trace.bounds g).2 :=
  BorrowSchedule.helper_inside_window witness PR531Controller.trace stagePair
    PR531Controller.accepted PR531Table.accepted i hi

/-- A register's owner as an element of the finite 7,168-family live stock. -/
def finiteOwner (t : Nat) (ht : t < witness.calls)
    (register : Sum (Fin 2 × Fin witness.ports) (Fin witness.helpers)) :
    Fin (witness.replicas * witness.lanes * witness.ports) :=
  ⟨invocationOwner witness stagePair t register,
    invocation_owner_lt witness PR531Table.accepted stagePair t ht
      (call_replica_fits t ht) (active_pair_fits t ht) register⟩

/-- The finite owner map supplies the injectivity part of a hosting interface. -/
theorem finite_owners_injective (t : Nat) (ht : t < witness.calls)
    (a b : Sum (Fin 2 × Fin witness.ports) (Fin witness.helpers))
    (heq : finiteOwner t ht a = finiteOwner t ht b) : a = b :=
  one_owner_per_call t ht a b (congrArg Fin.val heq)

end OwnerTransport.PR531ScheduledOwners

import SourceLayouts
import InvocationPayload

/-! Concrete raw input and output layouts for the single selected call.
Both embeddings expose every retained host, all data and the entire exterior
of the union of the two active owner images. The old bank is an arbitrary
separate input and an actual returned output. This common universe is a
local comparison device, not a global allocation or bank-renumbering claim. -/
namespace SourceInvocation
open SourceConnection FramedReplay

abbrev Slot (K : Type) := Nat × (SourceOwnership.Vec K → SourceOwnership.Vec K)
abbrev RawPayload (K : Type) := Slot K → Streams K
abbrev Gauges (K : Type) := Nat → Gauge (WholeHosting.Address SourceOwnership.Axis K)

variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)

def oldOwner := ParentOwnership.sourceActiveOwner K h2 d
def newOwner := SourceOwnership.sourceActiveOwner K h2 d
def oldChart := ParentOwnership.sourceActiveAddressChart K h2
def newChart := SourceOwnership.sourceActiveAddressChart K h2

def hostOwner (h : Host) : Slot K := newOwner K h2 d (SourceLayouts.hostRole h)
def hostChart (h : Host) := SourceOwnership.familyAddressChart K h2
  (SourceOwnership.family (role h))

def Outside (p : Slot K) : Prop :=
  (∀ r, p ≠ oldOwner K h2 d r) ∧ (∀ r, p ≠ newOwner K h2 d r)
abbrev TailKey := {p : Slot K // Outside K h2 d p}
abbrev Tail := TailKey K h2 d → Streams K
abbrev State := MultiHosting.WindowState Host SourceOwnership.Axis K Bool
  (Retained K (Tail K h2 d))

noncomputable def tailPayload (s : State K h2 d) : RawPayload K := by
  classical
  exact fun p => if hp : Outside K h2 d p then s.2.2 ⟨p, hp⟩ else fun _ => false

noncomputable def hostPayload (s : State K h2 d) : RawPayload K :=
  InvocationPayload.extend (hostOwner K h2 d)
    (fun h a => s.1 h ((hostChart K h2 h).inverse a)) (tailPayload K h2 d s)

def dataInput (i : Data) (v : Streams K) : Streams K :=
  fun a => v ((newChart K h2 (SourceLayouts.dataRole i)).forward a)
def dataOutput (i : Data) (v : Streams K) : Streams K :=
  fun a => v ((newChart K h2 (SourceLayouts.dataRole i)).inverse a)
def oldInput (h : Host) (v : Streams K) : Streams K :=
  fun a => v ((oldChart K h2 (SourceLayouts.hostRole h)).forward a)
def oldOutput (h : Host) (v : Streams K) : Streams K :=
  fun a => v ((oldChart K h2 (SourceLayouts.hostRole h)).inverse a)

noncomputable def oldPayload (s : State K h2 d) (bank : Host → Streams K) : RawPayload K :=
  InvocationPayload.realize (oldOwner K h2 d) (oldChart K h2)
    (packed (fun i => dataInput K h2 i (s.2.1 i))
      (fun h => oldInput K h2 h (bank h))) (hostPayload K h2 d s)

noncomputable def newPayload (s : State K h2 d) : RawPayload K :=
  InvocationPayload.realize (newOwner K h2 d) (newChart K h2)
    (packed (fun i => dataInput K h2 i (s.2.1 i))
      (fun h => hostInput h (s.1 h))) (tailPayload K h2 d s)

noncomputable def oldRaw (gauges : Gauges K) (s : State K h2 d) (bank : Host → Streams K) :=
  SourceRaw.final (oldOwner K h2 d) (oldChart K h2) gauges (oldPayload K h2 d s bank)
noncomputable def newRaw (gauges : Gauges K) (s : State K h2 d) :=
  SourceRaw.final (newOwner K h2 d) (newChart K h2) gauges (newPayload K h2 d s)

noncomputable def oldResult (gauges : Gauges K)
    (sb : State K h2 d × (Host → Streams K)) : State K h2 d × (Host → Streams K) :=
  let raw := oldRaw K h2 d gauges sb.1 sb.2
  ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
    (fun i => (raw (oldOwner K h2 d (SourceLayouts.dataRole i))).2,
      fun t => (raw t.val).2)),
    fun h => (raw (oldOwner K h2 d (SourceLayouts.hostRole h))).2)

noncomputable def newResult (gauges : Gauges K)
    (sb : State K h2 d × Unit) : State K h2 d × Unit :=
  let raw := newRaw K h2 d gauges sb.1
  ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
    (fun i => (raw (newOwner K h2 d (SourceLayouts.dataRole i))).2,
      fun t => (raw t.val).2)), sb.2)

theorem oldOwner_injective : Function.Injective (oldOwner K h2 d) :=
  ParentOwnership.sourceActiveOwner_injective K h2 d
theorem newOwner_injective : Function.Injective (newOwner K h2 d) :=
  SourceOwnership.sourceActiveOwner_injective K h2 d

theorem hostOwner_injective : Function.Injective (hostOwner K h2 d) := by
  intro r s h
  have he := newOwner_injective K h2 d h
  apply Fin.ext
  have hv := congrArg Fin.val he
  change 240 + r.val = 240 + s.val at hv
  omega

theorem host_not_old (h : Host) (r : SourceRaw.Role) :
    hostOwner K h2 d h ≠ oldOwner K h2 d r := by
  exact fun he => SourceLayouts.parent_owner_ne_host K h2 d r h he.symm

theorem tailPayload_outside (s : State K h2 d) (t : TailKey K h2 d) :
    tailPayload K h2 d s t.val = s.2.2 t := by
  classical
  simp only [tailPayload, dif_pos t.property]

theorem hostPayload_host (s : State K h2 d) (h : Host) :
    hostPayload K h2 d s (hostOwner K h2 d h) =
      fun a => s.1 h ((hostChart K h2 h).inverse a) :=
  InvocationPayload.extend_owner _ (fun he => hostOwner_injective K h2 d he) _ _ h

theorem hostPayload_outside (s : State K h2 d) (t : TailKey K h2 d) :
    hostPayload K h2 d s t.val = s.2.2 t := by
  rw [hostPayload, InvocationPayload.extend_outside]
  · exact tailPayload_outside K h2 d s t
  · intro h
    exact t.property.2 (SourceLayouts.hostRole h)

theorem oldPayload_host (s : State K h2 d) (bank : Host → Streams K) (h : Host) :
    oldPayload K h2 d s bank (hostOwner K h2 d h) =
      fun a => s.1 h ((hostChart K h2 h).inverse a) := by
  rw [oldPayload, InvocationPayload.realize, InvocationPayload.extend_outside]
  · exact hostPayload_host K h2 d s h
  · exact host_not_old K h2 d h

theorem oldPayload_outside (s : State K h2 d) (bank : Host → Streams K)
    (t : TailKey K h2 d) : oldPayload K h2 d s bank t.val = s.2.2 t := by
  rw [oldPayload, InvocationPayload.realize, InvocationPayload.extend_outside]
  · exact hostPayload_outside K h2 d s t
  · exact t.property.1

theorem newPayload_outside (s : State K h2 d) (t : TailKey K h2 d) :
    newPayload K h2 d s t.val = s.2.2 t := by
  rw [newPayload, InvocationPayload.realize, InvocationPayload.extend_outside]
  · exact tailPayload_outside K h2 d s t
  · exact t.property.2

end SourceInvocation

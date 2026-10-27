import SourceEndpoint
import MultiHosting
import Ownership

/-!
The literal normalized invocation supplies the complete, arbitrary-input
endpoint for all 747 helper roles and all 240 data roles. The adapters below
express gather/scatter in the fixed owner charts. Their identification with
the physical source execution is a separate theorem: in particular, the
actual initial/final frames must implement `hostOutput`, and the source's
owner charts must implement `hostInput`. The adapter must not be reported
as that physical identification by itself.

In particular, the literal physical initial decoder also contains its
initial frame. `hostInput` below is a convenient normalized representative,
not a claim about intermediate physical inputs. Connecting the two uses the
proved independence of data outputs from every dirty helper and the proved
identity on every normalized helper, followed by the actual initial/final
frame composition. The clean temporary is restored by
`SourceMatrix.arbitrary_dirty_temp_restored` and its chronological guards by
`SourceMatrix.actual_payload_clean`.
-/
namespace SourceConnection
open TreeReplay WholeHosting
set_option maxRecDepth 100000
set_option maxHeartbeats 0

abbrev Host := Fin 747
abbrev Data := Fin 240
abbrev Values (X : Type u) := X → Bool

def packed {X : Type u} (data : Data → Values X) (helpers : Host → Values X)
    (i : Nat) : Values X :=
  if hi : i < 240 then data ⟨i, hi⟩
  else if hr : i < 987 then helpers ⟨i - 240, by omega⟩
  else fun _ => false

theorem packed_data {X : Type u} (data : Data → Values X) (helpers : Host → Values X)
    (i : Data) : packed data helpers i.val = data i := by
  simp [packed, i.isLt]

theorem packed_helper {X : Type u} (data : Data → Values X) (helpers : Host → Values X)
    (h : Host) : packed data helpers (240 + h.val) = helpers h := by
  have hi : ¬ 240 + h.val < 240 := by omega
  have hr : 240 + h.val < 987 := by omega
  simp [packed, hi, hr]

def dataOther {X : Type u} (data : Data → Values X) : Data → Values X :=
  fun i => if hi : 120 ≤ i.val then
    fun x => data i x ^^ data ⟨i.val - 120, by omega⟩ x
  else data i

/-- This actually evaluates the certified literal word, not an assumed
closed-form endpoint. The clean temporary is included in the tree. -/
def invoke {X : Type u} (data : Data → Values X) (helpers : Host → Values X) :
    (Data → Values X) × (Host → Values X) :=
  let input := packed data helpers
  let output := runPayloads SourceMatrix.forwardWord
    (Tree.tabulate 10 (fun i => if i < 987 then input i else fun _ => false))
  (fun i => output.get i.val, fun h => output.get (240 + h.val))

theorem invoke_endpoint {X : Type u} (data : Data → Values X) (helpers : Host → Values X) :
    invoke data helpers = (dataOther data, helpers) := by
  have hwhole := SourceMatrix.arbitrary_dirty_payloads (packed data helpers)
  have hprojected := congrArg (fun output : Tree (Values X) =>
    ((fun i : Data => output.get i.val), (fun h : Host => output.get (240 + h.val)))) hwhole
  apply hprojected.trans
  apply Prod.ext
  · funext i
    change (Tree.tabulate 10 (SourceMatrix.endpointPayload (packed data helpers))).get i.val = _
    rw [Tree.get_tabulate 10 _ i.val (by omega)]
    unfold SourceMatrix.endpointPayload
    have hir : i.val < 987 := by omega
    by_cases hi : 120 ≤ i.val
    · have hs : i.val - 120 < 240 := by omega
      simp [dataOther, hi, hir, i.isLt, packed, hs]
    · simp [dataOther, hi, hir, i.isLt, packed]
  · funext h
    change (Tree.tabulate 10 (SourceMatrix.endpointPayload (packed data helpers))).get (240 + h.val) = _
    rw [Tree.get_tabulate 10 _ (240 + h.val) (by omega)]
    have hr : 240 + h.val < 987 := by omega
    have hn : ¬ 240 + h.val < 240 := by omega
    simp only [SourceMatrix.endpointPayload, hr, hn, and_false, ↓reduceIte, packed_helper]

def role (h : Host) : SourceOwnership.Role := ⟨240 + h.val, by omega⟩
def residual (h : Host) : Mask SourceOwnership.Axis :=
  SourceOwnership.targetMask (SourceOwnership.tag (role h))

/-- Complete paired-address conjugacy, including both entries at every
coordinate. This is stronger than just matching mask descriptors. -/
theorem swap_conjugacy {K : Type} (t : SourceOwnership.Tag)
    (a : Address SourceOwnership.Axis K) :
    SourceOwnership.reindex t
      (swapAddress (SourceOwnership.sourceMask t) (SourceOwnership.unindex t a)) =
      swapAddress (SourceOwnership.targetMask t) a := by
  funext i
  have hm := SourceOwnership.perm_support t (SourceOwnership.invPerm t i)
  rw [SourceOwnership.inverse_perm] at hm
  simp only [SourceOwnership.reindex, SourceOwnership.unindex, swapAddress,
    SourceOwnership.inverse_perm, ← hm]

def hostInput {K : Type} (h : Host) (v : Stream SourceOwnership.Axis K Bool) :
    Stream SourceOwnership.Axis K Bool :=
  fun a => v (SourceOwnership.reindex (SourceOwnership.tag (role h)) a)

def hostOutput {K : Type} (h : Host) (v : Stream SourceOwnership.Axis K Bool) :
    Stream SourceOwnership.Axis K Bool :=
  fun a => v (swapAddress (SourceOwnership.sourceMask (SourceOwnership.tag (role h)))
    (SourceOwnership.unindex (SourceOwnership.tag (role h)) a))

theorem host_transport {K : Type} (h : Host) (v : Stream SourceOwnership.Axis K Bool) :
    hostOutput h (hostInput h v) = bitAction (residual h) v := by
  funext a
  exact congrArg v (swap_conjugacy (SourceOwnership.tag (role h)) a)

abbrev Streams (K : Type) := Stream SourceOwnership.Axis K Bool
abbrev Retained (K : Type) (Tail : Type v) := (Data → Streams K) × Tail

/-- Data gather/scatter maps are common to the original and relocated
layouts. All data outputs and the untouched exterior state are retained. -/
def event {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K) :
    MultiHosting.WindowEvent Host SourceOwnership.Axis (Retained K Tail) where
  idle := fun _ _ => false
  residual := residual
  other s := (fun i => dataOutput i (dataOther (fun j => dataInput j (s.1 j)) i), s.2)

/-- Old helpers are a separate bank; its actual normalized endpoint and
chosen physical output charts are returned, not reset between invocations. -/
def original {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail) ×
      (Host → Streams K)) :=
  let result := invoke (fun i => dataInput i (s.1.2.1 i)) (fun h => oldInput h (s.2 h))
  ((s.1.1, (fun i => dataOutput i (result.1 i), s.1.2.2)),
    fun h => oldOutput h (result.2 h))

def relocated {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail) × Unit) :=
  let result := invoke (fun i => dataInput i (s.1.2.1 i)) (fun h => hostInput h (s.1.1 h))
  ((fun h => hostOutput h (result.2 h), (fun i => dataOutput i (result.1 i), s.1.2.2)), s.2)

theorem original_retained {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (bank : Host → Streams K) :
    (original dataInput dataOutput oldInput oldOutput (s, bank)).1 =
      (event dataInput dataOutput).base s := by
  simp only [original, invoke_endpoint, event, MultiHosting.WindowEvent.base]
  apply Prod.ext
  · funext h; exact (bitAction_empty (s.1 h)).symm
  · rfl

theorem original_bank_output {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (bank : Host → Streams K) :
    (original dataInput dataOutput oldInput oldOutput (s, bank)).2 =
      fun h => oldOutput h (oldInput h (bank h)) := by
  simp only [original, invoke_endpoint]

theorem relocated_retained {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (s : MultiHosting.WindowState Host SourceOwnership.Axis K Bool (Retained K Tail))
    (bank : Unit) :
    (relocated dataInput dataOutput (s, bank)).1 = (event dataInput dataOutput).hosted s := by
  simp only [relocated, invoke_endpoint, event, MultiHosting.WindowEvent.hosted,
    MultiHosting.WindowEvent.base, MultiHosting.onHosts]
  apply Prod.ext
  · funext h
    change hostOutput h (hostInput h (s.1 h)) =
      bitAction (residual h) (bitAction (fun _ => false) (s.1 h))
    rw [host_transport, bitAction_empty]
  · rfl

/-- A contract for the literal normalized word with the displayed coordinate
adapters. It is a physical source contract only after those adapters and the
987 distinct role owners are identified with the actual source execution. -/
def normalizedContract {K : Type} {Tail : Type v}
    (dataInput dataOutput : Data → Streams K → Streams K)
    (oldInput oldOutput : Host → Streams K → Streams K) :
    MultiHosting.PhysicalContract (K := K) (A := Bool) (event (Tail := Tail) dataInput dataOutput)
      (Host → Streams K) Unit where
  original := original dataInput dataOutput oldInput oldOutput
  relocated := relocated dataInput dataOutput
  original_retained := original_retained dataInput dataOutput oldInput oldOutput
  relocated_retained := relocated_retained dataInput dataOutput

end SourceConnection

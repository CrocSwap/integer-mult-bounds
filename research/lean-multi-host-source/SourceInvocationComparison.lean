import SourceInvocationState
import PhysicalSourceConnection

/-! Comparison of actual raw outputs with the framed hosting contract.
All maps and owner layouts are concrete. These lemmas expose every output
class, including the original bank, instead of discarding affected rows. -/
namespace SourceInvocation
open SourceConnection FramedReplay
variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
set_option maxRecDepth 100000
set_option maxHeartbeats 0
attribute [local irreducible] SourceRaw.final SourceFramed.final

theorem oldRaw_data (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) (i : Data) :
    (oldRaw K h2 d gauges s bank (oldOwner K h2 d (SourceLayouts.dataRole i))).2 =
      dataOutput K h2 i
        (PhysicalSourceConnection.physicalData gauges
          (fun j => dataInput K h2 j (s.2.1 j))
          (fun h => oldInput K h2 h (bank h)) i) := by
  -- Rewrite whole-function wrappers before projecting a literal execution.
  have raw_eq : oldRaw K h2 d gauges s bank =
      SourceRaw.final (oldOwner K h2 d) (oldChart K h2) gauges
        (InvocationPayload.realize (oldOwner K h2 d) (oldChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j))) (hostPayload K h2 d s)) := rfl
  rw [raw_eq]
  have select (L : SourceRaw.Role → Streams K) (R : Nat → Streams K)
      (chart : SourceRaw.Role → Gauge (WholeHosting.Address SourceOwnership.Axis K))
      (he : L = fun r a => R r.val ((chart r).inverse a))
      (hc : chart (SourceLayouts.dataRole i) = newChart K h2 (SourceLayouts.dataRole i)) :
      L (SourceLayouts.dataRole i) = fun a =>
        R i.val ((newChart K h2 (SourceLayouts.dataRole i)).inverse a) := by
    have h := congrFun he (SourceLayouts.dataRole i)
    rw [hc] at h
    exact h
  have he := InvocationPayload.realized_payloads
    (oldOwner K h2 d) (oldChart K h2) (fun h => oldOwner_injective K h2 d h)
    gauges (fun j => dataInput K h2 j (s.2.1 j))
    (fun j => oldInput K h2 j (bank j)) (hostPayload K h2 d s)
  have he' := select
    (fun r => (SourceRaw.final (oldOwner K h2 d) (oldChart K h2) gauges
        (InvocationPayload.realize (oldOwner K h2 d) (oldChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j))) (hostPayload K h2 d s))
      (oldOwner K h2 d r)).2)
    (fun n => ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j)))).get n).2)
    (oldChart K h2) he (SourceLayouts.data_chart_eq K h2 i)
  have out_eq : dataOutput K h2 i = fun v a =>
      v ((newChart K h2 (SourceLayouts.dataRole i)).inverse a) := rfl
  have phys_eq : PhysicalSourceConnection.physicalData gauges
      (fun j => dataInput K h2 j (s.2.1 j))
      (fun j => oldInput K h2 j (bank j)) = fun i =>
      ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j)))).get i.val).2 := rfl
  rw [out_eq, phys_eq]
  exact he'

theorem newRaw_data (gauges : Gauges K) (s : State K h2 d) (i : Data) :
    (newRaw K h2 d gauges s (newOwner K h2 d (SourceLayouts.dataRole i))).2 =
      dataOutput K h2 i
        (PhysicalSourceConnection.physicalData gauges
          (fun j => dataInput K h2 j (s.2.1 j))
          (fun h => hostInput h (s.1 h)) i) := by
  -- Rewrite whole-function wrappers before projecting a literal execution.
  have raw_eq : newRaw K h2 d gauges s =
      SourceRaw.final (newOwner K h2 d) (newChart K h2) gauges
        (InvocationPayload.realize (newOwner K h2 d) (newChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j))) (tailPayload K h2 d s)) := rfl
  rw [raw_eq]
  have select (L : SourceRaw.Role → Streams K) (R : Nat → Streams K)
      (chart : SourceRaw.Role → Gauge (WholeHosting.Address SourceOwnership.Axis K))
      (he : L = fun r a => R r.val ((chart r).inverse a))
      (hc : chart (SourceLayouts.dataRole i) = newChart K h2 (SourceLayouts.dataRole i)) :
      L (SourceLayouts.dataRole i) = fun a =>
        R i.val ((newChart K h2 (SourceLayouts.dataRole i)).inverse a) := by
    have h := congrFun he (SourceLayouts.dataRole i)
    rw [hc] at h
    exact h
  have he := InvocationPayload.realized_payloads
    (newOwner K h2 d) (newChart K h2) (fun h => newOwner_injective K h2 d h)
    gauges (fun j => dataInput K h2 j (s.2.1 j))
    (fun j => hostInput j (s.1 j)) (tailPayload K h2 d s)
  have he' := select
    (fun r => (SourceRaw.final (newOwner K h2 d) (newChart K h2) gauges
        (InvocationPayload.realize (newOwner K h2 d) (newChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j))) (tailPayload K h2 d s))
      (newOwner K h2 d r)).2)
    (fun n => ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j)))).get n).2)
    (newChart K h2) he rfl
  have out_eq : dataOutput K h2 i = fun v a =>
      v ((newChart K h2 (SourceLayouts.dataRole i)).inverse a) := rfl
  have phys_eq : PhysicalSourceConnection.physicalData gauges
      (fun j => dataInput K h2 j (s.2.1 j))
      (fun j => hostInput j (s.1 j)) = fun i =>
      ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j)))).get i.val).2 := rfl
  rw [out_eq, phys_eq]
  exact he'

theorem oldRaw_bank (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) (h : Host) :
    (oldRaw K h2 d gauges s bank (oldOwner K h2 d (SourceLayouts.hostRole h))).2 =
      oldOutput K h2 h
        (PhysicalSourceConnection.physicalHelpers gauges
          (fun j => dataInput K h2 j (s.2.1 j))
          (fun j => oldInput K h2 j (bank j)) h) := by
  -- Rewrite whole-function wrappers before projecting a literal execution.
  have raw_eq : oldRaw K h2 d gauges s bank =
      SourceRaw.final (oldOwner K h2 d) (oldChart K h2) gauges
        (InvocationPayload.realize (oldOwner K h2 d) (oldChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j))) (hostPayload K h2 d s)) := rfl
  rw [raw_eq]
  have select (L : SourceRaw.Role → Streams K) (R : Nat → Streams K)
      (chart : SourceRaw.Role → Gauge (WholeHosting.Address SourceOwnership.Axis K))
      (he : L = fun r a => R r.val ((chart r).inverse a))
      : L (SourceLayouts.hostRole h) = fun a =>
        R (240 + h.val) ((chart (SourceLayouts.hostRole h)).inverse a) := by
    exact congrFun he (SourceLayouts.hostRole h)
  have he := InvocationPayload.realized_payloads
    (oldOwner K h2 d) (oldChart K h2) (fun h => oldOwner_injective K h2 d h)
    gauges (fun j => dataInput K h2 j (s.2.1 j))
    (fun j => oldInput K h2 j (bank j)) (hostPayload K h2 d s)
  have he' := select
    (fun r => (SourceRaw.final (oldOwner K h2 d) (oldChart K h2) gauges
        (InvocationPayload.realize (oldOwner K h2 d) (oldChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j))) (hostPayload K h2 d s))
      (oldOwner K h2 d r)).2)
    (fun n => ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j)))).get n).2)
    (oldChart K h2) he
  have out_eq : oldOutput K h2 h = fun v a =>
      v ((oldChart K h2 (SourceLayouts.hostRole h)).inverse a) := rfl
  have phys_eq : PhysicalSourceConnection.physicalHelpers gauges
      (fun j => dataInput K h2 j (s.2.1 j))
      (fun j => oldInput K h2 j (bank j)) = fun h =>
      ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => oldInput K h2 j (bank j)))).get (240 + h.val)).2 := rfl
  rw [out_eq, phys_eq]
  exact he'

theorem oldRaw_host (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) (h : Host) :
    (oldRaw K h2 d gauges s bank (hostOwner K h2 d h)).2 =
      fun a => s.1 h ((hostChart K h2 h).inverse a) := by
  exact (SourceRaw.other_payload_preserved (oldOwner K h2 d) (oldChart K h2)
    gauges (oldPayload K h2 d s bank) (hostOwner K h2 d h)
    (host_not_old K h2 d h)).trans (oldPayload_host K h2 d s bank h)

theorem newRaw_host (gauges : Gauges K) (s : State K h2 d) (h : Host)
    (a : WholeHosting.Address SourceOwnership.Axis K) :
    (newRaw K h2 d gauges s (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a) =
      PhysicalSourceConnection.scatterHost h
        (PhysicalSourceConnection.physicalHelpers gauges
          (fun j => dataInput K h2 j (s.2.1 j))
          (fun j => hostInput j (s.1 j)) h) a := by
  -- Rewrite whole-function wrappers before projecting a literal execution.
  have raw_eq : newRaw K h2 d gauges s =
      SourceRaw.final (newOwner K h2 d) (newChart K h2) gauges
        (InvocationPayload.realize (newOwner K h2 d) (newChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j))) (tailPayload K h2 d s)) := rfl
  rw [raw_eq]
  have owner_eq : hostOwner K h2 d = fun h =>
      newOwner K h2 d (SourceLayouts.hostRole h) := rfl
  rw [owner_eq]
  have select (L : SourceRaw.Role → Streams K) (R : Nat → Streams K)
      (chart : SourceRaw.Role → Gauge (WholeHosting.Address SourceOwnership.Axis K))
      (he : L = fun r a => R r.val ((chart r).inverse a))
      (hc : (chart (SourceLayouts.hostRole h)).inverse ((hostChart K h2 h).forward a) =
        SourceOwnership.unindex (SourceOwnership.tag (role h)) a) :
      L (SourceLayouts.hostRole h) ((hostChart K h2 h).forward a) =
        R (240 + h.val) (SourceOwnership.unindex (SourceOwnership.tag (role h)) a) := by
    exact (congrFun (congrFun he (SourceLayouts.hostRole h))
      ((hostChart K h2 h).forward a)).trans
      (congrArg (R (240 + h.val)) hc)
  have he := InvocationPayload.realized_payloads
    (newOwner K h2 d) (newChart K h2) (fun h => newOwner_injective K h2 d h)
    gauges (fun j => dataInput K h2 j (s.2.1 j))
    (fun j => hostInput j (s.1 j)) (tailPayload K h2 d s)
  have hc : (newChart K h2 (SourceLayouts.hostRole h)).inverse
      ((hostChart K h2 h).forward a) =
      SourceOwnership.unindex (SourceOwnership.tag (role h)) a := by
    exact (SourceLayouts.host_chart_inverse K h2 h _).trans
      (congrArg (SourceOwnership.unindex (SourceOwnership.tag (role h)))
        ((hostChart K h2 h).inverse_forward a))
  have he' := select
    (fun r => (SourceRaw.final (newOwner K h2 d) (newChart K h2) gauges
        (InvocationPayload.realize (newOwner K h2 d) (newChart K h2)
          (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j))) (tailPayload K h2 d s))
      (newOwner K h2 d r)).2)
    (fun n => ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j)))).get n).2)
    (newChart K h2) he hc
  have out_eq : PhysicalSourceConnection.scatterHost h = fun (v : Streams K) a =>
      v (SourceOwnership.unindex (SourceOwnership.tag (role h)) a) := rfl
  have phys_eq : PhysicalSourceConnection.physicalHelpers gauges
      (fun j => dataInput K h2 j (s.2.1 j))
      (fun j => hostInput j (s.1 j)) = fun h =>
      ((SourceFramed.final gauges (packed (fun j => dataInput K h2 j (s.2.1 j)) (fun j => hostInput j (s.1 j)))).get (240 + h.val)).2 := rfl
  rw [out_eq, phys_eq]
  exact he'

theorem oldRaw_outside (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) (t : TailKey K h2 d) :
    (oldRaw K h2 d gauges s bank t.val).2 = s.2.2 t :=
  (SourceRaw.other_payload_preserved (oldOwner K h2 d) (oldChart K h2)
    gauges (oldPayload K h2 d s bank) t.val t.property.1).trans
    (oldPayload_outside K h2 d s bank t)

theorem newRaw_outside (gauges : Gauges K) (s : State K h2 d)
    (t : TailKey K h2 d) : (newRaw K h2 d gauges s t.val).2 = s.2.2 t :=
  (SourceRaw.other_payload_preserved (newOwner K h2 d) (newChart K h2)
    gauges (newPayload K h2 d s) t.val t.property.2).trans
    (newPayload_outside K h2 d s t)

/-- Equality includes the actual old-bank outputs as well as all retained
rows. No dirty-bank output is silently removed from this correspondence. -/
theorem oldResult_framed (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) :
    oldResult K h2 d gauges (s, bank) =
      PhysicalSourceConnection.original gauges (dataInput K h2) (dataOutput K h2)
        (oldInput K h2) (oldOutput K h2) (s, bank) := by
  apply Prod.ext
  · apply Prod.ext
    · funext h a
      exact (congrFun (oldRaw_host K h2 d gauges s bank h)
        ((hostChart K h2 h).forward a)).trans
        (congrArg (s.1 h) ((hostChart K h2 h).inverse_forward a))
    · apply Prod.ext
      · funext i
        exact oldRaw_data K h2 d gauges s bank i
      · funext t
        exact oldRaw_outside K h2 d gauges s bank t
  · funext h
    exact oldRaw_bank K h2 d gauges s bank h

theorem newResult_framed (gauges : Gauges K) (s : State K h2 d) (bank : Unit) :
    newResult K h2 d gauges (s, bank) =
      PhysicalSourceConnection.relocated gauges (dataInput K h2) (dataOutput K h2)
        (s, bank) := by
  apply Prod.ext
  · apply Prod.ext
    · funext h a
      exact newRaw_host K h2 d gauges s h a
    · apply Prod.ext
      · funext i
        exact newRaw_data K h2 d gauges s i
      · funext t
        exact newRaw_outside K h2 d gauges s t
  · rfl

end SourceInvocation

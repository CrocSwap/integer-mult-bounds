import FrameTraceLiterals
import OwnerTransport

/-! Exact finite-role encoding of the source trace for the independently
proved physical-owner routing interpreter. Only roles0..987 occur. -/
namespace SourceFrameTrace
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def indicesOK (e : FrameTrace.Entry) : Bool := e.scalar.x < 988 && e.scalar.y < 988

theorem indices_checked : forward.all indicesOK = true := by
  rw [forward, List.all_flatten]
  decide +kernel

theorem indices_bound (e : FrameTrace.Entry) (he : e ∈ forward) :
    e.scalar.x < 988 ∧ e.scalar.y < 988 := by
  have h := List.all_eq_true.mp indices_checked e he
  simpa only [indicesOK, Bool.and_eq_true, decide_eq_true_eq] using h

def toRoute {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (e : FrameTrace.Entry) : OwnerTransport.RouteEvent (Fin 988) X :=
  ⟨e.scalar.op, ⟨e.scalar.x % 988, Nat.mod_lt _ (by decide)⟩,
    ⟨e.scalar.y % 988, Nat.mod_lt _ (by decide)⟩,
    e.scalar.odd, gauges (if e.scalar.op < 3 then e.newFrame else 0)⟩

theorem route_projection {X : Type} (gauges : Nat → FramedReplay.Gauge X) :
    (forward.map (toRoute gauges)).map OwnerTransport.RouteEvent.framed =
      forward.map (FrameTrace.toPhysical gauges) := by
  rw [List.map_map]
  apply List.map_congr_left
  intro e he
  obtain ⟨hx, hy⟩ := indices_bound e he
  simp only [Function.comp_apply, toRoute, OwnerTransport.RouteEvent.framed,
    FrameTrace.toPhysical, Nat.mod_eq_of_lt hx, Nat.mod_eq_of_lt hy]

#print axioms indices_checked
#print axioms indices_bound
#print axioms route_projection
end SourceFrameTrace

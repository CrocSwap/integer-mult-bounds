import SourceFramed
import FrameTraceRoutes
import OwnerTransport

/-!
Whole-word realization on distinct raw physical owners, with arbitrary
payloads on every original and exterior stream. There is one designated
initially blank private row987. Frame labels are initialized metadata, not
constraints on dirty contents. The final SourceInvocation module supplies
the source-specific owner/chart maps; this module assumes their injectivity.
-/
namespace SourceRaw
open TreeReplay (Tree)
open FramedReplay OwnerTransport
set_option maxRecDepth 100000
set_option maxHeartbeats 0

abbrev Role := Fin 988
def privateRow : Role := ⟨987, by decide⟩

def frames {X : Type} (gauges : Nat → Gauge X) (r : Role) : Gauge X :=
  gauges (SourceFrameTrace.state0.frames.get r.val)

def input {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (payload : S → X → Bool) (i : Nat) : X → Bool :=
  if hi : i < 988 then fun a => payload (owner ⟨i, hi⟩) ((chart ⟨i, hi⟩).forward a)
  else fun _ => false

noncomputable def initial {S X : Type} (owner : Role → S)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) : Raw S X :=
  initialRaw owner (frames gauges) privateRow payload

noncomputable def final {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) : Raw S X :=
  runRaw owner chart (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
    (initial owner gauges payload)

theorem gather_initial {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) (r : Role) :
    gather owner chart (initial owner gauges payload) r =
      (SourceFramed.initial gauges (input owner chart payload)).get r.val := by
  rw [initial, gather_initialRaw owner chart hinj]
  rw [SourceFramed.initial, Tree.get_tabulate 10 _ r.val (by omega)]
  by_cases hr : r = privateRow
  · subst r
    simp only [privateRow, frames, ↓reduceIte, Nat.lt_irrefl]
  · have hval : r.val < 987 := by
      have hn : r.val ≠ 987 := fun h => hr (Fin.ext h)
      omega
    simp only [frames, if_neg hr, if_pos hval, input, dif_pos r.isLt]

/-- Every physical role follows the exact chronological framed source word.
The finite-role projection is an equality of the literal event lists. -/
theorem gather_final {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) (r : Role) :
    gather owner chart (final owner chart gauges payload) r =
      (SourceFramed.final gauges (input owner chart payload)).get r.val := by
  have h := gather_run_framed owner chart hinj
    (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
    (initial owner gauges payload)
    (SourceFramed.initial gauges (input owner chart payload)) 10
    (Tree.full_tabulate _ _) (by decide)
    (gather_initial owner chart hinj gauges payload) r
  rw [SourceFrameTrace.route_projection] at h
  exact h

/-- The same execution satisfies every COPY/ERASE guard for arbitrary dirty
payloads, including correlations among original and retained exterior rows. -/
theorem actual_valid {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) :
    FramedReplay.ValidTrace
      (SourceFrameTrace.forward.map (FrameTrace.toPhysical gauges))
      (SourceFramed.initial gauges (input owner chart payload)) :=
  SourceFramed.actual_valid gauges _

/-- Exact raw payload endpoint. The inverse chart is the proved scatter
map; all dirty inputs remain universally quantified. -/
theorem payload_endpoint {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) (r : Role) (a : X) :
    (final owner chart gauges payload (owner r)).2 a =
      SourceMatrix.endpointPayload
        (SourceFramed.normalizedInput gauges (input owner chart payload)) r.val
        ((gauges (SourceFrameTrace.state96.frames.get r.val)).inverse
          ((chart r).inverse a)) := by
  have h := congrArg Prod.snd (gather_final owner chart hinj gauges payload r)
  have ha := congrFun h ((chart r).inverse a)
  simp only [gather, (chart r).forward_inverse] at ha
  rw [ha]
  exact SourceFramed.actual_physical_endpoint gauges _ r.val (by omega) _

theorem private_restored {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) :
    (final owner chart gauges payload (owner privateRow)).2 = fun _ => false := by
  funext a
  rw [payload_endpoint owner chart hinj gauges payload privateRow a]
  rfl

/-- Every row outside the actual owner image is preserved, including its
payload and metadata. This supplies the retained exterior state. -/
theorem other_preserved {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) (s : S)
    (outside : ∀ r, s ≠ owner r) :
    final owner chart gauges payload s = initial owner gauges payload s :=
  runRaw_other owner chart _ _ s outside

theorem other_payload_preserved {S X : Type} (owner : Role → S) (chart : Role → Gauge X)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) (s : S)
    (outside : ∀ r, s ≠ owner r) :
    (final owner chart gauges payload s).2 = payload s := by
  rw [other_preserved owner chart gauges payload s outside]
  exact initialRaw_other owner (frames gauges) privateRow payload s (outside privateRow)

#print axioms gather_initial
#print axioms gather_final
#print axioms actual_valid
#print axioms payload_endpoint
#print axioms private_restored
#print axioms other_preserved
#print axioms other_payload_preserved
end SourceRaw

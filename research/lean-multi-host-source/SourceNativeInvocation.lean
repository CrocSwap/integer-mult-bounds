import SourceCommonCover
import SourceInitialPayload
import SourceRawGuards

/-! The concrete owner-coordinate executions are the literal native
instruction sequence in different coordinates. In particular ADD reads
one native address in both physical streams; COPY/ERASE legality is proved
along that same trajectory. Private scratch uses the explicit cover chart d.
-/
namespace SourceInvocation
open SourceConnection FramedReplay OwnerTransport
variable (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
variable (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)

noncomputable def nativePayload (cover : Slot K → Gauge (WholeHosting.Address SourceOwnership.Axis K))
    (payload : RawPayload K) : RawPayload K := fun s a => payload s ((cover s).inverse a)

def nativeGauge := AddressPairs.gauge (SourceOwnership.pairGauge d)

noncomputable def oldNative (gauges : Gauges K) (s : State K h2 d) (bank : Host → Streams K) :=
  runNative (oldOwner K h2 d) (nativeGauge K d)
    (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
    (SourceRaw.initial (oldOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank)))

noncomputable def newNative (gauges : Gauges K) (s : State K h2 d) :=
  runNative (newOwner K h2 d) (nativeGauge K d)
    (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
    (SourceRaw.initial (newOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s)))

omit [Field K] in
theorem native_payload_roundtrip
    (cover : Slot K → Gauge (WholeHosting.Address SourceOwnership.Axis K)) (payload : RawPayload K) :
    (fun s a => nativePayload K cover payload s ((cover s).forward a)) = payload := by
  funext s a
  exact congrArg (payload s) ((cover s).inverse_forward a)

theorem old_native_realization (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) :
    oldRaw K h2 d gauges s bank =
      fromNative (commonNativeCover K h2 d)
        (oldNative K h2 d gauges s bank) := by
  have h := SourceRawGuards.native_run_refines (oldOwner K h2 d) (oldChart K h2)
    gauges (commonNativeCover K h2 d) (nativeGauge K d)
    (old_common_cover K h2 d)
    (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank))
  rw [native_payload_roundtrip] at h
  exact h

theorem new_native_realization (gauges : Gauges K) (s : State K h2 d) :
    newRaw K h2 d gauges s =
      fromNative (commonNativeCover K h2 d)
        (newNative K h2 d gauges s) := by
  have h := SourceRawGuards.native_run_refines (newOwner K h2 d) (newChart K h2)
    gauges (commonNativeCover K h2 d) (nativeGauge K d)
    (new_common_cover K h2 d)
    (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s))
  rw [native_payload_roundtrip] at h
  exact h

theorem old_native_clean (gauges : Gauges K) (s : State K h2 d) (bank : Host → Streams K) :
    SourceRawGuards.NativeCleanRun (oldOwner K h2 d) (nativeGauge K d)
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial (oldOwner K h2 d) gauges
        (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank))) :=
  SourceRawGuards.actual_native_clean (oldOwner K h2 d) (oldChart K h2)
    (fun h => oldOwner_injective K h2 d h) gauges
    (commonNativeCover K h2 d) (nativeGauge K d)
    (old_common_cover K h2 d) _

theorem new_native_clean (gauges : Gauges K) (s : State K h2 d) :
    SourceRawGuards.NativeCleanRun (newOwner K h2 d) (nativeGauge K d)
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial (newOwner K h2 d) gauges
        (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s))) :=
  SourceRawGuards.actual_native_clean (newOwner K h2 d) (newChart K h2)
    (fun h => newOwner_injective K h2 d h) gauges
    (commonNativeCover K h2 d) (nativeGauge K d)
    (new_common_cover K h2 d) _

theorem old_native_temporary_restored (gauges : Gauges K) (s : State K h2 d)
    (bank : Host → Streams K) :
    (oldNative K h2 d gauges s bank (oldOwner K h2 d SourceRaw.privateRow)).2 = fun _ => false :=
  SourceRawGuards.native_private_restored (oldOwner K h2 d) (oldChart K h2)
    (fun h => oldOwner_injective K h2 d h) gauges
    (commonNativeCover K h2 d) (nativeGauge K d)
    (old_common_cover K h2 d) _

theorem new_native_temporary_restored (gauges : Gauges K) (s : State K h2 d) :
    (newNative K h2 d gauges s (newOwner K h2 d SourceRaw.privateRow)).2 = fun _ => false :=
  SourceRawGuards.native_private_restored (newOwner K h2 d) (newChart K h2)
    (fun h => newOwner_injective K h2 d h) gauges
    (commonNativeCover K h2 d) (nativeGauge K d)
    (new_common_cover K h2 d) _

/-- The original and hosted native executions start from the same dirty
physical payload at every retained host. A single cover chart is essential
here; independent extensions outside each active image would not suffice. -/
theorem native_shared_host_input (s : State K h2 d) (bank : Host → Streams K) (h : Host) :
    nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank)
      (hostOwner K h2 d h) =
    nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s)
      (hostOwner K h2 d h) := by
  funext a
  exact congrFun (shared_host_input K h2 d s bank h) _

theorem native_shared_data_input (s : State K h2 d) (bank : Host → Streams K) (i : Data) :
    nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank)
      (oldOwner K h2 d (SourceLayouts.dataRole i)) =
    nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s)
      (newOwner K h2 d (SourceLayouts.dataRole i)) := by
  have ho : oldOwner K h2 d (SourceLayouts.dataRole i) =
      newOwner K h2 d (SourceLayouts.dataRole i) := SourceLayouts.data_owner_eq K h2 d i
  funext a
  change oldPayload K h2 d s bank _ ((commonNativeCover K h2 d _).inverse a) =
    newPayload K h2 d s _ ((commonNativeCover K h2 d _).inverse a)
  rw [oldPayload_data, newPayload_data, ho]

theorem native_shared_tail_input (s : State K h2 d) (bank : Host → Streams K)
    (t : TailKey K h2 d) :
    nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank) t.val =
    nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s) t.val := by
  funext a
  exact congrFun ((oldPayload_outside K h2 d s bank t).trans
    (newPayload_outside K h2 d s t).symm) _

/-- The private-row initialization also preserves those shared retained
inputs. This statement concerns the actual initialized native states. -/
theorem initialized_native_host_input (gauges : Gauges K)
    (s : State K h2 d) (bank : Host → Streams K) (h : Host) :
    (SourceRaw.initial (oldOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank))
      (hostOwner K h2 d h)).2 =
    (SourceRaw.initial (newOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s))
      (hostOwner K h2 d h)).2 := by
  have hn : hostOwner K h2 d h ≠ newOwner K h2 d SourceRaw.privateRow := by
    intro he
    have hv := congrArg Fin.val (newOwner_injective K h2 d he)
    change 240 + h.val = 987 at hv
    omega
  exact (OwnerTransport.initialRaw_other (oldOwner K h2 d) (SourceRaw.frames gauges)
    SourceRaw.privateRow _ _ (host_not_old K h2 d h SourceRaw.privateRow)).trans
      ((native_shared_host_input K h2 d s bank h).trans
        (OwnerTransport.initialRaw_other (newOwner K h2 d) (SourceRaw.frames gauges)
          SourceRaw.privateRow _ _ hn).symm)

theorem initialized_native_data_input (gauges : Gauges K)
    (s : State K h2 d) (bank : Host → Streams K) (i : Data) :
    (SourceRaw.initial (oldOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank))
      (oldOwner K h2 d (SourceLayouts.dataRole i))).2 =
    (SourceRaw.initial (newOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s))
      (newOwner K h2 d (SourceLayouts.dataRole i))).2 := by
  have ho : oldOwner K h2 d (SourceLayouts.dataRole i) ≠
      oldOwner K h2 d SourceRaw.privateRow := by
    intro he
    have hv := congrArg Fin.val (oldOwner_injective K h2 d he)
    change i.val = 987 at hv
    omega
  have hn : newOwner K h2 d (SourceLayouts.dataRole i) ≠
      newOwner K h2 d SourceRaw.privateRow := by
    intro he
    have hv := congrArg Fin.val (newOwner_injective K h2 d he)
    change i.val = 987 at hv
    omega
  exact (OwnerTransport.initialRaw_other (oldOwner K h2 d) (SourceRaw.frames gauges)
    SourceRaw.privateRow _ _ ho).trans
      ((native_shared_data_input K h2 d s bank i).trans
        (OwnerTransport.initialRaw_other (newOwner K h2 d) (SourceRaw.frames gauges)
          SourceRaw.privateRow _ _ hn).symm)

theorem initialized_native_tail_input (gauges : Gauges K)
    (s : State K h2 d) (bank : Host → Streams K) (t : TailKey K h2 d) :
    (SourceRaw.initial (oldOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (oldPayload K h2 d s bank)) t.val).2 =
    (SourceRaw.initial (newOwner K h2 d) gauges
      (nativePayload K (commonNativeCover K h2 d) (newPayload K h2 d s)) t.val).2 := by
  exact (OwnerTransport.initialRaw_other (oldOwner K h2 d) (SourceRaw.frames gauges)
    SourceRaw.privateRow _ _ (t.property.1 SourceRaw.privateRow)).trans
      ((native_shared_tail_input K h2 d s bank t).trans
        (OwnerTransport.initialRaw_other (newOwner K h2 d) (SourceRaw.frames gauges)
          SourceRaw.privateRow _ _ (t.property.2 SourceRaw.privateRow)).symm)

/-- Native outputs are read in the same fixed retained coordinate charts.
The definition spells out the read-back from the native instruction fold. -/
noncomputable def oldNativeResult (gauges : Gauges K)
    (sb : State K h2 d × (Host → Streams K)) : State K h2 d × (Host → Streams K) :=
  let raw := fromNative (commonNativeCover K h2 d) (oldNative K h2 d gauges sb.1 sb.2)
  ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
    (fun i => (raw (oldOwner K h2 d (SourceLayouts.dataRole i))).2,
      fun t => (raw t.val).2)),
    fun h => (raw (oldOwner K h2 d (SourceLayouts.hostRole h))).2)

noncomputable def newNativeResult (gauges : Gauges K)
    (sb : State K h2 d × Unit) : State K h2 d × Unit :=
  let raw := fromNative (commonNativeCover K h2 d) (newNative K h2 d gauges sb.1)
  ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
    (fun i => (raw (newOwner K h2 d (SourceLayouts.dataRole i))).2,
      fun t => (raw t.val).2)), sb.2)

theorem oldResult_native (gauges : Gauges K) (s : State K h2 d) (bank : Host → Streams K) :
    oldResult K h2 d gauges (s, bank) = oldNativeResult K h2 d gauges (s, bank) := by
  exact congrArg (fun raw : Raw (Slot K) (WholeHosting.Address SourceOwnership.Axis K) =>
    ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
      (fun i => (raw (oldOwner K h2 d (SourceLayouts.dataRole i))).2,
        fun t : TailKey K h2 d => (raw t.val).2)),
      fun h => (raw (oldOwner K h2 d (SourceLayouts.hostRole h))).2))
    (old_native_realization K h2 d gauges s bank)

theorem newResult_native (gauges : Gauges K) (s : State K h2 d) (bank : Unit) :
    newResult K h2 d gauges (s, bank) = newNativeResult K h2 d gauges (s, bank) := by
  exact congrArg (fun raw : Raw (Slot K) (WholeHosting.Address SourceOwnership.Axis K) =>
    ((fun h a => (raw (hostOwner K h2 d h)).2 ((hostChart K h2 h).forward a),
      (fun i => (raw (newOwner K h2 d (SourceLayouts.dataRole i))).2,
        fun t : TailKey K h2 d => (raw t.val).2)), bank))
    (new_native_realization K h2 d gauges s)

end SourceInvocation

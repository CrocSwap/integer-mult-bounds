import SourceRaw

/-! COPY blankness and ERASE uncomputation guards along the actual raw and
native executions. Guards follow each preceding physical output; no fresh
reinitialization or endpoint assumption is inserted between events. -/
namespace SourceRawGuards
open FramedReplay OwnerTransport
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def RawClean {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (e : RouteEvent R X) : Prop :=
  (e.op = 2 → (raw (owner e.y)).2 = fun _ => false) ∧
  (e.op = 3 → ∀ a, (raw (owner e.y)).2 a =
    (raw (owner e.x)).2 ((chart e.x).forward
      ((raw (owner e.x)).1.forward ((raw (owner e.y)).1.inverse
        ((chart e.y).inverse a)))))

noncomputable def RawCleanRun {R S X : Type} (owner : R → S) (chart : R → Gauge X) :
    List (RouteEvent R X) → Raw S X → Prop
  | [], _ => True
  | e :: es, raw => RawClean owner chart raw e ∧ RawCleanRun owner chart es
      (rawStep owner chart raw e.op e.x e.y e.odd e.newFrame)

theorem raw_clean_of_framed {n : Nat} {S X : Type} (owner : Fin n → S)
    (chart : Fin n → Gauge X) (raw : Raw S X) (s : Store X)
    (rel : ∀ r, gather owner chart raw r = s.get r.val)
    (e : RouteEvent (Fin n) X) (valid : ValidStep s e.framed) :
    RawClean owner chart raw e := by
  constructor
  · intro hop
    have hv : decodeRow (s.get e.y.val) = fun _ => false := by
      simpa only [ValidStep, RouteEvent.framed, hop] using valid
    have hg : decodeRow (gather owner chart raw e.y) = fun _ => false := by
      rw [rel]; exact hv
    funext a
    have h := physical_blank_of_decoded_blank _ hg ((chart e.y).inverse a)
    simpa only [gather, (chart e.y).forward_inverse] using h
  · intro hop a
    have hv : decodeRow (s.get e.x.val) = decodeRow (s.get e.y.val) := by
      simpa only [ValidStep, RouteEvent.framed, hop] using valid
    have hg : decodeRow (gather owner chart raw e.x) =
        decodeRow (gather owner chart raw e.y) := by
      rw [rel, rel]; exact hv
    have h := erase_guard_transport _ _ hg ((chart e.y).inverse a)
    simpa only [gather, (chart e.y).forward_inverse] using h

theorem raw_clean_run_of_framed {n : Nat} {S X : Type} (owner : Fin n → S)
    (chart : Fin n → Gauge X) (hinj : ∀ {r s}, owner r = owner s → r = s)
    (events : List (RouteEvent (Fin n) X)) (raw : Raw S X)
    (s : Store X) (depth : Nat) (full : TreeReplay.Tree.Full depth s)
    (bound : n ≤ 2 ^ depth) (rel : ∀ r, gather owner chart raw r = s.get r.val)
    (valid : ValidTrace (events.map RouteEvent.framed) s) :
    RawCleanRun owner chart events raw := by
  induction events generalizing raw s with
  | nil => trivial
  | cons e es ih =>
      refine ⟨raw_clean_of_framed owner chart raw s rel e valid.1, ?_⟩
      apply ih _ _ (physicalStep_full s depth full e.framed) _ valid.2
      intro r
      rw [congrFun (gather_step owner chart hinj raw e.op e.x e.y e.odd e.newFrame) r]
      exact logicalStep_fin_tree s depth full bound _ rel e r

def NativeClean {R S X : Type} (owner : R → S) (d : Gauge X)
    (native : Raw S X) (e : RouteEvent R X) : Prop :=
  (e.op = 2 → (native (owner e.y)).2 = fun _ => false) ∧
  (e.op = 3 → ∀ a, (native (owner e.y)).2 a =
    (native (owner e.x)).2 (d.forward
      ((native (owner e.x)).1.forward ((native (owner e.y)).1.inverse (d.inverse a)))))

noncomputable def NativeCleanRun {R S X : Type} (owner : R → S) (d : Gauge X) :
    List (RouteEvent R X) → Raw S X → Prop
  | [], _ => True
  | e :: es, native => NativeClean owner d native e ∧ NativeCleanRun owner d es
      (nativeStep owner d native e.op e.x e.y e.odd e.newFrame)

theorem native_clean_of_raw {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (native : Raw S X) (e : RouteEvent R X)
    (clean : RawClean owner chart (fromNative cover native) e) :
    NativeClean owner d native e := by
  constructor
  · intro hop
    funext a
    have h := congrFun (clean.1 hop) ((cover (owner e.y)).inverse a)
    simpa only [fromNative, (cover (owner e.y)).forward_inverse] using h
  · intro hop a
    have h := clean.2 hop ((cover (owner e.y)).inverse a)
    simp only [fromNative, (cover (owner e.y)).forward_inverse] at h
    rw [common, inverse_common_cover owner chart cover d common e.y a] at h
    exact h

theorem native_clean_run_of_raw {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (events : List (RouteEvent R X)) (native : Raw S X)
    (clean : RawCleanRun owner chart events (fromNative cover native)) :
    NativeCleanRun owner d events native := by
  induction events generalizing native with
  | nil => trivial
  | cons e es ih =>
      refine ⟨native_clean_of_raw owner chart cover d common native e clean.1, ?_⟩
      apply ih
      have h := clean.2
      rw [rawStep_fromNative owner chart cover d common] at h
      exact h

theorem actual_raw_clean {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (payload : S → X → Bool) :
    RawCleanRun owner chart (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial owner gauges payload) := by
  apply raw_clean_run_of_framed owner chart hinj _ _
    (SourceFramed.initial gauges (SourceRaw.input owner chart payload)) 10
    (TreeReplay.Tree.full_tabulate _ _) (by decide)
    (SourceRaw.gather_initial owner chart hinj gauges payload)
  rw [SourceFrameTrace.route_projection]
  exact SourceFramed.actual_valid gauges _

/-- Preparing a blank private row and the fixed frame metadata commutes
with expressing all physical streams in their cover charts. -/
theorem initial_fromNative {S X : Type} (owner : SourceRaw.Role → S)
    (gauges : Nat → Gauge X) (cover : S → Gauge X) (payload : S → X → Bool) :
    SourceRaw.initial owner gauges (fun s a => payload s ((cover s).forward a)) =
      fromNative cover (SourceRaw.initial owner gauges payload) := by
  classical
  funext s
  by_cases hs : s = owner SourceRaw.privateRow <;>
    simp only [SourceRaw.initial, initialRaw, fromNative, hs, ↓reduceIte]

theorem actual_native_clean {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (payload : S → X → Bool) :
    NativeCleanRun owner d (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial owner gauges payload) := by
  apply native_clean_run_of_raw owner chart cover d common
  rw [← initial_fromNative]
  exact actual_raw_clean owner chart hinj gauges _

theorem native_run_refines {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (gauges : Nat → Gauge X)
    (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (payload : S → X → Bool) :
    SourceRaw.final owner chart gauges (fun s a => payload s ((cover s).forward a)) =
      fromNative cover (runNative owner d
        (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
        (SourceRaw.initial owner gauges payload)) := by
  unfold SourceRaw.final
  rw [initial_fromNative, runRaw_fromNative owner chart cover d common]

/-- Exact source-native endpoint, derived from the same native execution
whose physical COPY/ERASE guards were checked above. -/
theorem native_payload_endpoint {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (payload : S → X → Bool) (r : SourceRaw.Role) (a : X) :
    ((runNative owner d
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial owner gauges payload)) (owner r)).2 a =
    SourceMatrix.endpointPayload
      (SourceFramed.normalizedInput gauges (SourceRaw.input owner chart
        (fun s a => payload s ((cover s).forward a)))) r.val
      ((gauges (SourceFrameTrace.state96.frames.get r.val)).inverse (d.inverse a)) := by
  have h := SourceRaw.payload_endpoint owner chart hinj gauges
    (fun s a => payload s ((cover s).forward a)) r ((cover (owner r)).inverse a)
  rw [native_run_refines owner chart gauges cover d common] at h
  simp only [fromNative, (cover (owner r)).forward_inverse] at h
  rw [inverse_common_cover owner chart cover d common] at h
  exact h

theorem native_private_restored {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (hinj : ∀ {r s}, owner r = owner s → r = s)
    (gauges : Nat → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (payload : S → X → Bool) :
    ((runNative owner d
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial owner gauges payload)) (owner SourceRaw.privateRow)).2 =
        fun _ => false := by
  funext a
  rw [native_payload_endpoint owner chart hinj gauges cover d common payload
    SourceRaw.privateRow a]
  rfl

theorem native_other_preserved {S X : Type} (owner : SourceRaw.Role → S)
    (chart : SourceRaw.Role → Gauge X) (gauges : Nat → Gauge X)
    (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (payload : S → X → Bool) (s : S) (outside : ∀ r, s ≠ owner r) :
    ((runNative owner d
      (SourceFrameTrace.forward.map (SourceFrameTrace.toRoute gauges))
      (SourceRaw.initial owner gauges payload)) s).2 = payload s := by
  have h := SourceRaw.other_payload_preserved owner chart gauges
    (fun s a => payload s ((cover s).forward a)) s outside
  rw [native_run_refines owner chart gauges cover d common] at h
  funext a
  have ha := congrFun h ((cover s).inverse a)
  simpa only [fromNative, (cover s).forward_inverse] using ha

#print axioms raw_clean_of_framed
#print axioms raw_clean_run_of_framed
#print axioms native_clean_of_raw
#print axioms native_clean_run_of_raw
#print axioms actual_raw_clean
#print axioms initial_fromNative
#print axioms actual_native_clean
#print axioms native_run_refines
#print axioms native_payload_endpoint
#print axioms native_private_restored
#print axioms native_other_preserved
end SourceRawGuards

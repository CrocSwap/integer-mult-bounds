import FramedReplay

/-!
Raw owner-chart routing for the source-permitted owner `(F,d sigma⁻¹)`.
A logical address a in a role is represented at sigma(a) in the owner
cover chart. Thus its chart-relative read from source s while writing
destination t uses sigma_s ∘ sigma_t⁻¹. The native-coordinate bridge below
proves that g_r sigma_r=d makes this a same-native-address XOR, not an
additional physical routing layer. The theorems below use actual inverse laws and
physical owner injectivity; frame-label equality cannot imply them.

This is the coordinate realization permitted by PR442 PROOF.md §2 (whole
residual isometry plus the charged slot permutation and U_q). It does not
assert that the symbolic JSON contains numerical routing matrices.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace OwnerTransport
open FramedReplay

abbrev Raw (S X : Type) := S → Row X
abbrev Logical (R X : Type) := R → Row X

def gather {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) : Logical R X :=
  fun r => ((raw (owner r)).1, fun a => (raw (owner r)).2 ((chart r).forward a))

noncomputable def write {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (r : R) (row : Row X) : Raw S X := by
  classical
  exact fun s => if s = owner r then
    (row.1, fun a => row.2 ((chart r).inverse a)) else raw s

noncomputable def replace {R X : Type} (s : Logical R X) (r : R) (row : Row X) : Logical R X := by
  classical
  exact fun t => if t = r then row else s t

/-- All other physical streams, including retained streams outside the
local role image, survive every routed write unchanged. -/
theorem write_other {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (r : R) (row : Row X) (s : S) (hne : s ≠ owner r) :
    write owner chart raw r row s = raw s := by
  classical
  simp only [write, if_neg hne]

theorem gather_write {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (raw : Raw S X) (r : R) (row : Row X) :
    gather owner chart (write owner chart raw r row) =
      replace (gather owner chart raw) r row := by
  classical
  funext s
  by_cases hs : s = r
  · subst s
    simp only [gather, write, replace]
    congr 1
    funext a
    exact congrArg row.2 ((chart r).inverse_forward a)
  · have ho : owner s ≠ owner r := fun h => hs (hinj h)
    simp only [gather, write, replace, if_neg ho, if_neg hs]

/-- Raw XOR has the literal source-to-destination chart route. -/
noncomputable def rawXor {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (x y : R) : Raw S X := by
  classical
  exact fun s => if s = owner x then
    ((raw s).1, fun a => (raw s).2 a ^^
      (raw (owner y)).2 ((chart y).forward ((chart x).inverse a)))
    else raw s

theorem rawXor_write {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (x y : R) :
    rawXor owner chart raw x y = write owner chart raw x
      ((gather owner chart raw x).1,
       fun a => (gather owner chart raw x).2 a ^^ (gather owner chart raw y).2 a) := by
  classical
  funext s
  by_cases hs : s = owner x
  · subst s
    simp only [rawXor, write, gather, (chart x).forward_inverse]
  · simp only [rawXor, write, if_neg hs]

/-- Raw MOVE/COPY routing also transports the old and new local frame
operators. Omitting the owner charts from this expression changes the map. -/
noncomputable def rawTransport {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (source dest : R) (newFrame : Gauge X) : Raw S X := by
  classical
  exact fun s => if s = owner dest then
    (newFrame, fun a => (raw (owner source)).2
      ((chart source).forward ((raw (owner source)).1.forward
        (newFrame.inverse ((chart dest).inverse a)))))
    else raw s

theorem rawTransport_write {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (source dest : R) (newFrame : Gauge X) :
    rawTransport owner chart raw source dest newFrame =
      write owner chart raw dest (reframe newFrame (gather owner chart raw source)) := by
  classical
  rfl

noncomputable def rawStep {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X) : Raw S X :=
  match op with
  | 0 => rawTransport owner chart raw x x newFrame
  | 1 => if odd then rawXor owner chart raw x y else raw
  | 2 => rawTransport owner chart raw x y newFrame
  | _ => write owner chart raw y (newFrame, fun _ => false)

noncomputable def logicalStep {R X : Type} (s : Logical R X)
    (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X) : Logical R X :=
  match op with
  | 0 => replace s x (reframe newFrame (s x))
  | 1 => if odd then replace s x ((s x).1, fun a => (s x).2 a ^^ (s y).2 a) else s
  | 2 => replace s y (reframe newFrame (s x))
  | _ => replace s y (newFrame, fun _ => false)

/-- Every raw event refines the common-chart FramedReplay row operation;
this theorem includes address routing and all retained non-owner streams. -/
theorem gather_step {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (raw : Raw S X) (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X) :
    gather owner chart (rawStep owner chart raw op x y odd newFrame) =
      logicalStep (gather owner chart raw) op x y odd newFrame := by
  cases op with
  | zero =>
      simp only [rawStep, logicalStep, rawTransport_write, gather_write owner chart hinj]
  | succ op =>
      cases op with
      | zero =>
          cases odd <;> simp only [rawStep, logicalStep, Bool.false_eq_true, ↓reduceIte,
            rawXor_write, gather_write owner chart hinj]
      | succ op =>
          cases op with
          | zero =>
              simp only [rawStep, logicalStep, rawTransport_write, gather_write owner chart hinj]
          | succ op =>
              simp only [rawStep, logicalStep, gather_write owner chart hinj]

/-- The function-store operation above is exactly the tree-store operation
used by the checked literal framed replay, within its actual index bound. -/
theorem logicalStep_tree {X : Type} (s : Store X) (depth : Nat)
    (full : TreeReplay.Tree.Full depth s) (e : Event X) (i : Nat)
    (hx : e.scalar.x < 2 ^ depth) (hy : e.scalar.y < 2 ^ depth)
    (hi : i < 2 ^ depth) :
    logicalStep (fun j => s.get j) e.scalar.op e.scalar.x e.scalar.y
      e.scalar.odd e.newFrame i = (physicalStep s e).get i := by
  classical
  obtain ⟨⟨op, x, y, odd⟩, newFrame⟩ := e
  cases op with
  | zero =>
      simp only [logicalStep, physicalStep, replace,
        TreeReplay.Tree.get_put depth s full x i _ hx hi]
      simp only [eq_comm]
  | succ op =>
      cases op with
      | zero =>
          cases odd <;> simp only [logicalStep, physicalStep, replace,
            Bool.false_eq_true, ↓reduceIte,
            TreeReplay.Tree.get_put depth s full x i _ hx hi] <;>
              simp only [eq_comm]
      | succ op =>
          cases op with
          | zero =>
              simp only [logicalStep, physicalStep, replace,
                TreeReplay.Tree.get_put depth s full y i _ hy hi]
              simp only [eq_comm]
          | succ op =>
              simp only [logicalStep, physicalStep, replace,
                TreeReplay.Tree.get_put depth s full y i _ hy hi]
              simp only [eq_comm]

theorem rawStep_other {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (raw : Raw S X) (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X)
    (s : S) (hx : s ≠ owner x) (hy : s ≠ owner y) :
    rawStep owner chart raw op x y odd newFrame s = raw s := by
  classical
  cases op with
  | zero => simp only [rawStep, rawTransport, if_neg hx]
  | succ op =>
      cases op with
      | zero => cases odd <;> simp [rawStep, rawXor, hx]
      | succ op =>
          cases op with
          | zero => simp only [rawStep, rawTransport, if_neg hy]
          | succ op => simp only [rawStep, write, if_neg hy]

structure RouteEvent (R X : Type) where
  op : Nat
  x : R
  y : R
  odd : Bool
  newFrame : Gauge X

def RouteEvent.framed {n : Nat} {X : Type} (e : RouteEvent (Fin n) X) : Event X :=
  ⟨⟨e.op, e.x.val, e.y.val, e.odd⟩, e.newFrame⟩

noncomputable def runRaw {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (events : List (RouteEvent R X)) (raw : Raw S X) : Raw S X :=
  events.foldl (fun s e => rawStep owner chart s e.op e.x e.y e.odd e.newFrame) raw

theorem replace_fin_tree {n : Nat} {X : Type} (s : Store X) (depth : Nat)
    (full : TreeReplay.Tree.Full depth s) (bound : n ≤ 2 ^ depth)
    (f : Logical (Fin n) X) (rel : ∀ r, f r = s.get r.val)
    (x r : Fin n) (row : Row X) :
    replace f x row r = (s.put x.val row).get r.val := by
  classical
  rw [TreeReplay.Tree.get_put depth s full x.val r.val row
    (Nat.lt_of_lt_of_le x.isLt bound) (Nat.lt_of_lt_of_le r.isLt bound)]
  by_cases he : r = x
  · subst r
    simp [replace]
  · have hv : x.val ≠ r.val := fun h => he (Fin.ext h.symm)
    simp only [replace, if_neg he, if_neg hv, rel]

theorem logicalStep_fin_tree {n : Nat} {X : Type} (s : Store X) (depth : Nat)
    (full : TreeReplay.Tree.Full depth s) (bound : n ≤ 2 ^ depth)
    (f : Logical (Fin n) X) (rel : ∀ r, f r = s.get r.val)
    (e : RouteEvent (Fin n) X) (r : Fin n) :
    logicalStep f e.op e.x e.y e.odd e.newFrame r =
      (physicalStep s e.framed).get r.val := by
  have hp := replace_fin_tree s depth full bound f rel
  obtain ⟨op, x, y, odd, frame⟩ := e
  cases op with
  | zero => simpa only [logicalStep, RouteEvent.framed, physicalStep, rel] using
      (hp x r (reframe frame (f x)))
  | succ op =>
      cases op with
      | zero =>
          cases odd
          · exact rel r
          · simpa only [logicalStep, RouteEvent.framed, physicalStep, ↓reduceIte, rel] using
              (hp x r ((f x).1, fun a => (f x).2 a ^^ (f y).2 a))
      | succ op =>
          cases op with
          | zero => simpa only [logicalStep, RouteEvent.framed, physicalStep, rel] using
              (hp y r (reframe frame (f x)))
          | succ op => simpa only [logicalStep, RouteEvent.framed, physicalStep, rel] using
              (hp y r (frame, fun _ => false))

theorem physicalStep_full {X : Type} (s : Store X) (depth : Nat)
    (full : TreeReplay.Tree.Full depth s) (e : Event X) :
    TreeReplay.Tree.Full depth (physicalStep s e) := by
  obtain ⟨⟨op, x, y, odd⟩, frame⟩ := e
  cases op with
  | zero => exact TreeReplay.Tree.full_put _ _ full _ _
  | succ op =>
      cases op with
      | zero => cases odd <;> first | exact full | exact TreeReplay.Tree.full_put _ _ full _ _
      | succ op => cases op <;> exact TreeReplay.Tree.full_put _ _ full _ _

/-- A complete sequence of physically routed operations, retaining all
non-owner streams, refines the exact framed tree interpreter used by the
source-word certificate. This is an execution equality, not a postulated
endpoint contract. The clean-work guards remain those of FramedReplay. -/
theorem gather_run_framed {n : Nat} {S X : Type}
    (owner : Fin n → S) (chart : Fin n → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (events : List (RouteEvent (Fin n) X)) (raw : Raw S X)
    (s : Store X) (depth : Nat) (full : TreeReplay.Tree.Full depth s)
    (bound : n ≤ 2 ^ depth)
    (rel : ∀ r, gather owner chart raw r = s.get r.val) :
    ∀ r, gather owner chart (runRaw owner chart events raw) r =
      (runPhysical (events.map RouteEvent.framed) s).get r.val := by
  induction events generalizing raw s with
  | nil => exact rel
  | cons e es ih =>
      apply ih _ _ (physicalStep_full s depth full e.framed)
      intro r
      rw [congrFun (gather_step owner chart hinj raw e.op e.x e.y e.odd e.newFrame) r]
      exact logicalStep_fin_tree s depth full bound _ rel e r

/-- Every retained physical stream outside this invocation's actual owner
image survives the entire same chronological routed word unchanged. -/
theorem runRaw_other {R S X : Type} (owner : R → S) (chart : R → Gauge X)
    (events : List (RouteEvent R X)) (raw : Raw S X) (s : S)
    (outside : ∀ r, s ≠ owner r) :
    runRaw owner chart events raw s = raw s := by
  induction events generalizing raw with
  | nil => rfl
  | cons e es ih =>
      change runRaw owner chart es
        (rawStep owner chart raw e.op e.x e.y e.odd e.newFrame) s = raw s
      rw [ih]
      exact rawStep_other owner chart raw e.op e.x e.y e.odd e.newFrame s
        (outside e.x) (outside e.y)

def identityGauge (X : Type) : Gauge X := ⟨id, id, fun _ => rfl, fun _ => rfl⟩

/-- Extend the actual charts of the selected owners to a coordinate chart
on every retained stream. Other streams use their native coordinates. -/
noncomputable def extendCover {R S X : Type} (owner : R → S)
    (cover : R → Gauge X) (s : S) : Gauge X := by
  classical
  exact if h : ∃ r, owner r = s then cover h.choose else identityGauge X

theorem extendCover_owner {R S X : Type} (owner : R → S)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (cover : R → Gauge X) (r : R) :
    extendCover owner cover (owner r) = cover r := by
  classical
  have h : ∃ t, owner t = owner r := ⟨r, rfl⟩
  simp only [extendCover, dif_pos h]
  exact congrArg cover (hinj h.choose_spec)

/-- Arbitrary dirty original/retained payloads and one designated initially
blank private row. This describes allowed initial data; it does not erase
an arbitrary dirty private row during execution. Frame labels are metadata. -/
noncomputable def initialRaw {R S X : Type} (owner : R → S)
    (frames : R → Gauge X) (privateRow : R) (payload : S → X → Bool) : Raw S X := by
  classical
  exact fun s => (extendCover owner frames s,
    if s = owner privateRow then fun _ => false else payload s)

theorem initialRaw_other {R S X : Type} (owner : R → S)
    (frames : R → Gauge X) (privateRow : R) (payload : S → X → Bool)
    (s : S) (hs : s ≠ owner privateRow) :
    (initialRaw owner frames privateRow payload s).2 = payload s := by
  classical
  simp only [initialRaw, if_neg hs]

theorem gather_initialRaw {R S X : Type} [DecidableEq R] (owner : R → S) (chart : R → Gauge X)
    (hinj : ∀ {r s}, owner r = owner s → r = s)
    (frames : R → Gauge X) (privateRow : R) (payload : S → X → Bool) (r : R) :
    gather owner chart (initialRaw owner frames privateRow payload) r =
      (frames r, if r = privateRow then fun _ => false
        else fun a => payload (owner r) ((chart r).forward a)) := by
  classical
  simp only [gather, initialRaw, extendCover_owner owner hinj]
  by_cases hr : r = privateRow
  · subst r
    simp only [↓reduceIte]
  · have ho : owner r ≠ owner privateRow := fun h => hr (hinj h)
    simp only [if_neg hr, if_neg ho]

def fromNative {S X : Type} (cover : S → Gauge X) (native : Raw S X) : Raw S X :=
  fun s => ((native s).1, fun a => (native s).2 ((cover s).forward a))

/-- When g_r sigma_r=d, the apparent raw chart route is precisely a
same-native-address read; it is not a second physical routing layer. -/
theorem route_native_address {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (x y : R) (a : X) :
    (cover (owner y)).forward ((chart y).forward ((chart x).inverse a)) =
      (cover (owner x)).forward a := by
  rw [common, ← common x ((chart x).inverse a), (chart x).forward_inverse]

theorem inverse_common_cover {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (r : R) (a : X) :
    (chart r).inverse ((cover (owner r)).inverse a) = d.inverse a := by
  have h := common r ((chart r).inverse ((cover (owner r)).inverse a))
  rw [(chart r).forward_inverse, (cover (owner r)).forward_inverse] at h
  have hi := congrArg d.inverse h
  rw [d.inverse_forward] at hi
  exact hi.symm

noncomputable def nativeXor {R S X : Type} (owner : R → S)
    (native : Raw S X) (x y : R) : Raw S X := by
  classical
  exact fun s => if s = owner x then
    ((native s).1, fun a => (native s).2 a ^^ (native (owner y)).2 a)
    else native s

theorem rawXor_fromNative {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (native : Raw S X) (x y : R) :
    rawXor owner chart (fromNative cover native) x y =
      fromNative cover (nativeXor owner native x y) := by
  classical
  funext s
  by_cases hs : s = owner x
  · subst s
    simp only [rawXor, nativeXor, fromNative, ↓reduceIte]
    rw [show (fun a => (native (owner x)).2 ((cover (owner x)).forward a) ^^
      (native (owner y)).2 ((cover (owner y)).forward ((chart y).forward ((chart x).inverse a)))) =
      (fun a => (native (owner x)).2 ((cover (owner x)).forward a) ^^
      (native (owner y)).2 ((cover (owner x)).forward a)) by
        funext a
        rw [route_native_address owner chart cover d common]]
  · simp only [rawXor, nativeXor, fromNative, if_neg hs]

noncomputable def nativeTransport {R S X : Type} (owner : R → S)
    (d : Gauge X) (native : Raw S X) (source dest : R) (newFrame : Gauge X) : Raw S X := by
  classical
  exact fun s => if s = owner dest then
    (newFrame, fun a => (native (owner source)).2
      (d.forward ((native (owner source)).1.forward (newFrame.inverse (d.inverse a)))))
    else native s

/-- Raw MOVE/COPY is the source's native D_d-frame transport. This removes
both cover-class chart maps and leaves the actual common invocation d. -/
theorem rawTransport_fromNative {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (native : Raw S X) (source dest : R) (newFrame : Gauge X) :
    rawTransport owner chart (fromNative cover native) source dest newFrame =
      fromNative cover (nativeTransport owner d native source dest newFrame) := by
  classical
  funext s
  by_cases hs : s = owner dest
  · subst s
    simp only [rawTransport, nativeTransport, fromNative, ↓reduceIte]
    apply Prod.ext
    · rfl
    · funext a
      dsimp only
      rw [common]
      have h := inverse_common_cover owner chart cover d common dest
        ((cover (owner dest)).forward a)
      rw [(cover (owner dest)).inverse_forward] at h
      rw [h]
  · simp only [rawTransport, nativeTransport, fromNative, if_neg hs]

noncomputable def nativeStep {R S X : Type} (owner : R → S) (d : Gauge X)
    (native : Raw S X) (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X) : Raw S X :=
  match op with
  | 0 => nativeTransport owner d native x x newFrame
  | 1 => if odd then nativeXor owner native x y else native
  | 2 => nativeTransport owner d native x y newFrame
  | _ => write owner (fun _ => identityGauge X) native y (newFrame, fun _ => false)

theorem rawStep_fromNative {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (native : Raw S X) (op : Nat) (x y : R) (odd : Bool) (newFrame : Gauge X) :
    rawStep owner chart (fromNative cover native) op x y odd newFrame =
      fromNative cover (nativeStep owner d native op x y odd newFrame) := by
  classical
  cases op with
  | zero => exact rawTransport_fromNative owner chart cover d common native x x newFrame
  | succ op =>
      cases op with
      | zero =>
          cases odd
          · rfl
          · exact rawXor_fromNative owner chart cover d common native x y
      | succ op =>
          cases op with
          | zero => exact rawTransport_fromNative owner chart cover d common native x y newFrame
          | succ op =>
              funext s
              by_cases hs : s = owner y <;>
                simp only [rawStep, nativeStep, write, fromNative, hs, ↓reduceIte]

noncomputable def runNative {R S X : Type} (owner : R → S) (d : Gauge X)
    (events : List (RouteEvent R X)) (native : Raw S X) : Raw S X :=
  events.foldl (fun s e => nativeStep owner d s e.op e.x e.y e.odd e.newFrame) native

/-- Complete-word native/raw equality, including the private copied row.
Only the actual common-cover equation is required, not an endpoint premise. -/
theorem runRaw_fromNative {R S X : Type} (owner : R → S)
    (chart : R → Gauge X) (cover : S → Gauge X) (d : Gauge X)
    (common : ∀ r a, (cover (owner r)).forward ((chart r).forward a) = d.forward a)
    (events : List (RouteEvent R X)) (native : Raw S X) :
    runRaw owner chart events (fromNative cover native) =
      fromNative cover (runNative owner d events native) := by
  induction events generalizing native with
  | nil => rfl
  | cons e es ih =>
      change runRaw owner chart es
        (rawStep owner chart (fromNative cover native) e.op e.x e.y e.odd e.newFrame) = _
      rw [rawStep_fromNative owner chart cover d common, ih]
      rfl

end OwnerTransport
#print axioms OwnerTransport.write_other
#print axioms OwnerTransport.gather_write
#print axioms OwnerTransport.rawXor_write
#print axioms OwnerTransport.gather_step
#print axioms OwnerTransport.logicalStep_tree
#print axioms OwnerTransport.rawStep_other
#print axioms OwnerTransport.gather_run_framed
#print axioms OwnerTransport.runRaw_other
#print axioms OwnerTransport.route_native_address
#print axioms OwnerTransport.rawXor_fromNative
#print axioms OwnerTransport.rawTransport_fromNative
#print axioms OwnerTransport.runRaw_fromNative

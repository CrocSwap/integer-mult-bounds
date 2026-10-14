import SignedWord

/-! Binary-table proof architecture adapted from the immutable old suite;
signed destination semantics and signed graph compatibility are new here. -/
namespace CurrentMain.SignedTrace
open Lean.Grind CurrentMain.SignedWord
inductive Table (α : Type u) where
  | leaf : α → Table α
  | fork : Table α → Table α → Table α
  deriving DecidableEq

def get : Table α → Nat → α
  | .leaf a, _ => a
  | .fork l r, k => if k % 2 = 0 then get l (k/2) else get r (k/2)

def put : Nat → Table α → Nat → α → Table α
  | 0, _, _, value => .leaf value
  | depth+1, .leaf old, key, value =>
    if key%2=0 then .fork (put depth (.leaf old) (key/2) value) (.leaf old)
    else .fork (.leaf old) (put depth (.leaf old) (key/2) value)
  | depth+1, .fork l r, key, value =>
    if key%2=0 then .fork (put depth l (key/2) value) r
    else .fork l (put depth r (key/2) value)

theorem get_put (depth : Nat) (t : Table α) (key index : Nat) (value : α)
    (hk : key < 2^depth) (hi : index < 2^depth) :
    get (put depth t key value) index = if index=key then value else get t index := by
  induction depth generalizing t key index with
  | zero =>
    have hk0 : key=0 := by simpa using hk
    have hi0 : index=0 := by simpa using hi
    subst key; subst index; rfl
  | succ depth ih =>
    have hk' : key/2 < 2^depth := by simp only [Nat.pow_succ] at hk; omega
    have hi' : index/2 < 2^depth := by simp only [Nat.pow_succ] at hi; omega
    by_cases hke : key%2=0 <;> by_cases hie : index%2=0
    · have heq : index/2=key/2 ↔ index=key := by omega
      cases t <;> simp [put, get, hke, hie, ih _ _ _ hk' hi', heq]
    · have hne : index ≠ key := by omega
      cases t <;> simp [put, get, hke, hie, hne]
    · have hne : index ≠ key := by omega
      cases t <;> simp [put, get, hke, hie, hne]
    · have heq : index/2=key/2 ↔ index=key := by omega
      cases t <;> simp [put, get, hke, hie, ih _ _ _ hk' hi', heq]


inductive Spec where
  | zero
  | input (index : Nat)
  | add (left right : Nat) (negative : Bool)
  deriving DecidableEq, Repr

abbrev Graph := Nat → Spec

structure Annotation where
  step : Step
  oldDst : Nat
  oldSrc : Nat
  result : Nat
  deriving DecidableEq, Repr

def stepCheck (depth : Nat) (t : Table Nat) (a : Annotation) : Bool :=
  decide (a.step.dst < 2^depth ∧ a.step.src < 2^depth ∧ a.step.dst ≠ a.step.src ∧
    get t a.step.dst = a.oldDst ∧ get t a.step.src = a.oldSrc)

def traceCheck (depth : Nat) : Table Nat → List Annotation → Bool
  | _, [] => true
  | t, a :: rest => stepCheck depth t a &&
      traceCheck depth (put depth t a.step.dst a.result) rest

def replay (depth : Nat) : Table Nat → List Annotation → Table Nat
  | t, [] => t
  | t, a :: rest => replay depth (put depth t a.step.dst a.result) rest

def compatible (node : Graph) (a : Annotation) : Bool :=
  decide (a.oldDst = 0 ∧ a.oldSrc = a.result ∧ a.step.srcNegative = false) ||
  match node a.result with
  | .add l r neg =>
    decide (a.oldDst = l ∧ a.oldSrc = r ∧ a.step.dstNegative = false ∧ a.step.srcNegative = neg) ||
    decide (a.oldDst = r ∧ a.oldSrc = l ∧ a.step.dstNegative = neg ∧ a.step.srcNegative = false)
  | _ => false

variable {F : Type u} [Ring F]

def localIdentity (value : Nat → F) (a : Annotation) : Prop :=
  value a.result = signed a.step.dstNegative (value a.oldDst) +
    signed a.step.srcNegative (value a.oldSrc)

theorem compatible_sound (node : Graph) (value : Nat → F) (a : Annotation)
    (hz : value 0 = 0)
    (ha : ∀ n l r neg, node n = .add l r neg → value n = value l + signed neg (value r))
    (hc : compatible node a = true) : localIdentity value a := by
  rcases Bool.or_eq_true_iff.mp hc with hcopy | hadd
  · have hh : a.oldDst = 0 ∧ a.oldSrc = a.result ∧ a.step.srcNegative = false := of_decide_eq_true hcopy
    cases hn : a.step.dstNegative <;>
      simp [localIdentity, hh.1, hh.2.1, hh.2.2, hn, signed, hz, Ring.neg_zero, Semiring.zero_add]
  · cases hn : node a.result with
    | zero => simp [hn] at hadd
    | input i => simp [hn] at hadd
    | add l r neg =>
      simp only [hn] at hadd
      have hv := ha a.result l r neg hn
      rcases Bool.or_eq_true_iff.mp hadd with hd | hs
      · have hh : a.oldDst = l ∧ a.oldSrc = r ∧ a.step.dstNegative = false ∧ a.step.srcNegative = neg := of_decide_eq_true hd
        simpa only [localIdentity, hh.1, hh.2.1, hh.2.2.1, hh.2.2.2, signed, Bool.false_eq_true, ↓reduceIte] using hv
      · have hh : a.oldDst = r ∧ a.oldSrc = l ∧ a.step.dstNegative = neg ∧ a.step.srcNegative = false := of_decide_eq_true hs
        simp only [localIdentity, hh.1, hh.2.1, hh.2.2.1, hh.2.2.2, signed, Bool.false_eq_true, ↓reduceIte]
        exact hv.trans (Semiring.add_comm _ _)

theorem step_sound (depth : Nat) (t : Table Nat) (a : Annotation)
    (value : Nat → F) (state : State F)
    (hc : stepCheck depth t a = true) (hl : localIdentity value a)
    (hs : ∀ i, i < 2^depth → value (get t i) = state i) :
    ∀ i, i < 2^depth →
      value (get (put depth t a.step.dst a.result) i) = forward a.step state i := by
  have hh : a.step.dst < 2^depth ∧ a.step.src < 2^depth ∧ a.step.dst ≠ a.step.src ∧
      get t a.step.dst = a.oldDst ∧ get t a.step.src = a.oldSrc := of_decide_eq_true hc
  have hd : value a.oldDst = state a.step.dst := by rw [← hh.2.2.2.1]; exact hs _ hh.1
  have hr : value a.oldSrc = state a.step.src := by rw [← hh.2.2.2.2]; exact hs _ hh.2.1
  intro i hi
  rw [get_put depth t a.step.dst i a.result hh.1 hi]
  by_cases he : i = a.step.dst
  · subst i
    simp only [if_pos rfl, forward]
    change value a.result = signed a.step.dstNegative (state a.step.dst) + _
    simpa only [localIdentity, hd, hr] using hl
  · simp only [if_neg he, forward]
    exact hs i hi

theorem trace_sound (depth : Nat) (t : Table Nat) (as : List Annotation)
    (value : Nat → F) (state : State F)
    (hc : traceCheck depth t as = true)
    (hl : ∀ a ∈ as, localIdentity value a)
    (hs : ∀ i, i < 2^depth → value (get t i) = state i) :
    ∀ i, i < 2^depth →
      value (get (replay depth t as) i) = run (as.map Annotation.step) state i := by
  induction as generalizing t state with
  | nil => exact hs
  | cons a rest ih =>
    have hh := Bool.and_eq_true_iff.mp hc
    have hstep := step_sound depth t a value state hh.1 (hl a (by simp)) hs
    exact ih (put depth t a.step.dst a.result) (forward a.step state) hh.2
      (fun b hb => hl b (by simp [hb])) hstep

theorem traceCheck_append (depth : Nat) (t : Table Nat) (as bs : List Annotation) :
    traceCheck depth t (as ++ bs) =
      (traceCheck depth t as && traceCheck depth (replay depth t as) bs) := by
  induction as generalizing t with
  | nil => simp [traceCheck, replay]
  | cons a rest ih => simp [traceCheck, replay, ih, Bool.and_assoc]

theorem replay_append (depth : Nat) (t : Table Nat) (as bs : List Annotation) :
    replay depth t (as ++ bs) = replay depth (replay depth t as) bs := by
  induction as generalizing t with
  | nil => rfl
  | cons a rest ih => exact ih _

structure Certificate (depth : Nat) (node : Graph) (start finish : Table Nat)
    (annotations : List Annotation) : Prop where
  traced : traceCheck depth start annotations = true
  compatible : annotations.all (CurrentMain.SignedTrace.compatible node) = true
  replayed : replay depth start annotations = finish

theorem append_certificate (depth : Nat) (node : Graph) (start middle finish : Table Nat)
    (a b : List Annotation) (ha : Certificate depth node start middle a)
    (hb : Certificate depth node middle finish b) : Certificate depth node start finish (a++b) := by
  constructor
  · rw [traceCheck_append, ha.traced, ha.replayed, hb.traced]; rfl
  · rw [List.all_append, ha.compatible, hb.compatible]; rfl
  · rw [replay_append, ha.replayed, hb.replayed]

theorem certificate_sound (depth : Nat) (node : Graph) (start finish : Table Nat)
    (annotations : List Annotation) (hc : Certificate depth node start finish annotations)
    (value : Nat → F) (state : State F) (hz : value 0 = 0)
    (ha : ∀ n l r neg, node n = .add l r neg → value n = value l + signed neg (value r))
    (hs : ∀ i, i < 2^depth → value (get start i) = state i)
    (i : Nat) (hi : i < 2^depth) :
    value (get finish i) = run (annotations.map Annotation.step) state i := by
  rw [← hc.replayed]
  exact trace_sound depth start annotations value state hc.traced
    (fun a ha' => compatible_sound node value a hz ha (List.all_eq_true.mp hc.compatible a ha')) hs i hi

theorem trace_check_legal (depth : Nat) (t : Table Nat) (as : List Annotation)
    (hc : traceCheck depth t as = true) : Legal (as.map Annotation.step) := by
  induction as generalizing t with
  | nil => rfl
  | cons a as ih =>
    have hh := Bool.and_eq_true_iff.mp hc
    have hs : a.step.dst < 2^depth ∧ a.step.src < 2^depth ∧ a.step.dst ≠ a.step.src ∧
      get t a.step.dst = a.oldDst ∧ get t a.step.src = a.oldSrc := of_decide_eq_true hh.1
    have hgood : good a.step = true := by unfold good; exact decide_eq_true hs.2.2.1
    change (good a.step && (as.map Annotation.step).all good) = true
    rw [hgood, ih _ hh.2]; rfl

end CurrentMain.SignedTrace

#print axioms CurrentMain.SignedTrace.get_put
#print axioms CurrentMain.SignedTrace.compatible_sound
#print axioms CurrentMain.SignedTrace.step_sound
#print axioms CurrentMain.SignedTrace.trace_sound
#print axioms CurrentMain.SignedTrace.traceCheck_append
#print axioms CurrentMain.SignedTrace.replay_append
#print axioms CurrentMain.SignedTrace.append_certificate
#print axioms CurrentMain.SignedTrace.certificate_sound
#print axioms CurrentMain.SignedTrace.trace_check_legal

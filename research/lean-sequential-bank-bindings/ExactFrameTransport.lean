import Lean

/-!
Dimension-free exact operator transport.  These are reusable algebraic theorems,
not a verification of the selected h=22/h=24 finite word or its compiler costs.
An exact frame is retained as an invertible function, not a binary label.
-/
namespace CurrentMain.FrameTransport

universe u v w

structure Frame (V : Type u) where
  encode : V → V
  decode : V → V
  left_inverse : ∀ x, decode (encode x) = x
  right_inverse : ∀ x, encode (decode x) = x

namespace Frame
variable {V : Type u}

def identity : Frame V where
  encode := id
  decode := id
  left_inverse := fun _ => rfl
  right_inverse := fun _ => rfl

def inverse (A : Frame V) : Frame V where
  encode := A.decode
  decode := A.encode
  left_inverse := A.right_inverse
  right_inverse := A.left_inverse

/-- `compose A B` executes B first, then A. -/
def compose (A B : Frame V) : Frame V where
  encode x := A.encode (B.encode x)
  decode x := B.decode (A.decode x)
  left_inverse := by intro x; simp only [A.left_inverse, B.left_inverse]
  right_inverse := by intro x; simp only [B.right_inverse, A.right_inverse]

/-- Complete spectator values are transported unchanged, even when correlated
with the active state.  No independence or clean-value premise appears. -/
def withSpectator {S : Type v} (C : Frame V) : Frame (V × S) where
  encode x := (C.encode x.1, x.2)
  decode x := (C.decode x.1, x.2)
  left_inverse := by intro x; simp only [C.left_inverse]
  right_inverse := by intro x; simp only [C.right_inverse]

end Frame

variable {V : Type u}

def adapter (A B : Frame V) (x : V) : V := B.encode (A.decode x)
def conjugate (C : Frame V) (op : V → V) (x : V) : V := C.encode (op (C.decode x))

/-- Lists execute chronologically, from their head onward. -/
def run : List (V → V) → V → V
  | [], x => x
  | op :: rest, x => run rest (op x)

theorem adapter_encoded (A B : Frame V) (x : V) :
    adapter A B (A.encode x) = B.encode x := by
  simp only [adapter, A.left_inverse]

theorem adapter_inverse (A B : Frame V) (x : V) :
    adapter B A (adapter A B x) = x := by
  simp only [adapter, B.left_inverse, A.right_inverse]

theorem adapter_transitive (A B C : Frame V) (x : V) :
    adapter B C (adapter A B x) = adapter A C x := by
  simp only [adapter, B.left_inverse]

theorem adapter_identity (A : Frame V) (x : V) :
    adapter A A x = x := A.right_inverse x

theorem conjugate_comp (C : Frame V) (f g : V → V) (x : V) :
    conjugate C f (conjugate C g x) = conjugate C (fun y => f (g y)) x := by
  simp only [conjugate, C.left_inverse]

theorem conjugate_run (C : Frame V) (ops : List (V → V)) (x : V) :
    run (ops.map (conjugate C)) x = conjugate C (run ops) x := by
  induction ops generalizing x with
  | nil => exact (C.right_inverse x).symm
  | cons op rest ih =>
    simp only [List.map_cons, run]
    rw [ih]
    simp only [conjugate, C.left_inverse]

/-- A selected core must separately provide its whole-word raw endpoint.
No cleanliness restriction on x and no erasure of D_S inverse is imposed. -/
theorem raw_endpoint_transport (C D_A D_S : Frame V) (ops : List (V → V))
    (raw : ∀ x, run ops x = D_A.encode (D_S.decode x)) (x : V) :
    run (ops.map (conjugate C)) x =
      C.encode (D_A.encode (D_S.decode (C.decode x))) := by
  rw [conjugate_run]
  exact congrArg C.encode (raw (C.decode x))

/-- Exact transition invariance for the reverse/complement convention
D_U = T_U F inverse.  It does not assert F = F inverse. -/
theorem reverse_complement_transition (T_U T_V F : Frame V) (x : V) :
    adapter (Frame.compose T_V F.inverse) (Frame.compose T_U F.inverse) x =
      adapter T_V T_U x := by
  simp only [adapter, Frame.compose, Frame.inverse, F.left_inverse]

/-- A path of exact adapters telescopes without any commutativity premise. -/
def transportPath (first : Frame V) : List (Frame V) → V → V
  | [], x => x
  | next :: rest, x => transportPath next rest (adapter first next x)

def lastFrame (first : Frame V) : List (Frame V) → Frame V
  | [] => first
  | next :: rest => lastFrame next rest

theorem transportPath_exact (first : Frame V) (rest : List (Frame V)) (x : V) :
    transportPath first rest x = adapter first (lastFrame first rest) x := by
  induction rest generalizing first x with
  | nil => exact (adapter_identity first x).symm
  | cons next rest ih =>
    change transportPath next rest (adapter first next x) = _
    rw [ih, adapter_transitive]
    rfl

open Lean.Grind
attribute [local instance] Semiring.natCast Ring.intCast

structure ExactFrame (X : Type u) (F : Type v) [Ring F] extends Frame (X → F) where
  encode_add : ∀ f g, encode (fun x => f x + g x) = fun x => encode f x + encode g x
  encode_scale : ∀ a f, encode (fun x => a * f x) = fun x => a * encode f x

section Linear
variable {X : Type u} {F : Type v} [Ring F]

def mix (a b : F) (f g : X → F) : X → F := fun x => a * f x + b * g x

theorem common_mix (C : ExactFrame X F) (a b : F) (f g : X → F) :
    mix a b (C.encode f) (C.encode g) = C.encode (mix a b f g) := by
  unfold mix
  rw [C.encode_add, C.encode_scale, C.encode_scale]

theorem adapted_mix (A B C : ExactFrame X F) (a b : F) (f g : X → F) :
    mix a b (adapter A.toFrame C.toFrame (A.encode f))
      (adapter B.toFrame C.toFrame (B.encode g)) = C.encode (mix a b f g) := by
  rw [adapter_encoded, adapter_encoded, common_mix]

theorem decoded_adapted_mix (A B C : ExactFrame X F) (a b : F) (f g : X → F) :
    C.decode (mix a b (adapter A.toFrame C.toFrame (A.encode f))
      (adapter B.toFrame C.toFrame (B.encode g))) = mix a b f g := by
  rw [adapted_mix, C.left_inverse]

theorem decode_add (C : ExactFrame X F) (f g : X → F) :
    C.decode (fun x => f x + g x) = fun x => C.decode f x + C.decode g x := by
  have h := C.encode_add (C.decode f) (C.decode g)
  rw [C.right_inverse, C.right_inverse] at h
  exact (congrArg C.decode h).symm.trans (C.left_inverse _)

theorem decode_scale (C : ExactFrame X F) (a : F) (f : X → F) :
    C.decode (fun x => a * f x) = fun x => a * C.decode f x := by
  have h := C.encode_scale a (C.decode f)
  rw [C.right_inverse] at h
  exact (congrArg C.decode h).symm.trans (C.left_inverse _)

def linearCompose (A B : ExactFrame X F) : ExactFrame X F where
  toFrame := Frame.compose A.toFrame B.toFrame
  encode_add := by intro f g; simp only [Frame.compose, B.encode_add, A.encode_add]
  encode_scale := by intro a f; simp only [Frame.compose, B.encode_scale, A.encode_scale]

/-- Weight/frame selection depends on ancestors, not fresh role fields.
The type enforces the stated independence; realization of a selected compiler's
selector by this interface is a separate concrete obligation. -/
def ancestorSelector {Ancestor : Type w} {Fresh : Type} (select : Ancestor → ExactFrame X F)
    (a : Ancestor) (_r : Fresh) : ExactFrame X F := select a

theorem ancestor_selector_common {Ancestor : Type w} {Fresh : Type}
    (select : Ancestor → ExactFrame X F) (a : Ancestor) (r s : Fresh)
    (p q : F) (f g : X → F) :
    mix p q ((ancestorSelector select a r).encode f)
      ((ancestorSelector select a s).encode g) = (select a).encode (mix p q f g) :=
  common_mix (select a) p q f g

/-- Exact frame changes commute with routing that changes only fresh roles.
No identification of charts across distinct ancestor contexts is made. -/
theorem fresh_routing_commutes {Ancestor : Type w} {Fresh : Type}
    (select : Ancestor → ExactFrame X F) (route : Ancestor → Fresh → Fresh)
    (values : Ancestor → Fresh → X → F) :
    (fun a r => (select a).encode (values a (route a r))) =
      (fun a r => (fun a r => (select a).encode (values a r)) a (route a r)) := rfl

end Linear

section Phase
variable {X : Type u} {F : Type v} [CommRing F]

/-- Pointwise inverse data are explicit.  No division or characteristic
assumption, and no phase equality inferred from binary labels, is used. -/
structure UnitWeight (X : Type u) (F : Type v) [CommRing F] where
  value : X → F
  inverse : X → F
  reciprocal : ∀ x, inverse x * value x = 1

def weightFrame (w : UnitWeight X F) : ExactFrame X F where
  encode f x := w.value x * f x
  decode f x := w.inverse x * f x
  left_inverse := by
    intro f; funext x
    change w.inverse x * (w.value x * f x) = f x
    rw [← Semiring.mul_assoc, w.reciprocal, Semiring.one_mul]
  right_inverse := by
    intro f; funext x
    have h := w.reciprocal x
    change w.value x * (w.inverse x * f x) = f x
    grind
  encode_add := by intro f g; funext x; exact Semiring.left_distrib _ _ _
  encode_scale := by intro a f; funext x; change _ = a * (w.value x * f x); grind

/-- Rephasing is an actual exact representative change, with a real inverse. -/
def rephase (C : ExactFrame X F) (w : UnitWeight X F) : ExactFrame X F :=
  linearCompose (weightFrame w) C

theorem phase_adapter_formula (C : ExactFrame X F) (u v : UnitWeight X F) (f : X → F) :
    adapter (rephase C u).toFrame (rephase C v).toFrame f =
      fun x => v.value x * (u.inverse x * f x) := by
  simp only [adapter, rephase, linearCompose, Frame.compose, weightFrame, C.right_inverse]

theorem phase_normalized_mix (C : ExactFrame X F) (u v w : UnitWeight X F)
    (a b : F) (f g : X → F) :
    mix a b (adapter (rephase C u).toFrame (rephase C w).toFrame ((rephase C u).encode f))
      (adapter (rephase C v).toFrame (rephase C w).toFrame ((rephase C v).encode g)) =
      (rephase C w).encode (mix a b f g) :=
  adapted_mix (rephase C u) (rephase C v) (rephase C w) a b f g

/-- The scalar phase in a projective pullthrough is retained when normalizing
an exact operator.  hphase is explicit exact operator evidence, not a label. -/
theorem normalize_projective_identity (C : ExactFrame X F) (w : UnitWeight X F)
    (raw target : (X → F) → X → F)
    (hphase : ∀ f, C.encode (raw (C.decode f)) =
      fun x => w.value x * target f x) (f : X → F) :
    (weightFrame w).decode (C.encode (raw (C.decode f))) = target f := by
  rw [hphase]
  exact (weightFrame w).left_inverse (target f)

end Phase

end CurrentMain.FrameTransport

#print axioms CurrentMain.FrameTransport.adapter_encoded
#print axioms CurrentMain.FrameTransport.adapter_inverse
#print axioms CurrentMain.FrameTransport.adapter_transitive
#print axioms CurrentMain.FrameTransport.adapter_identity
#print axioms CurrentMain.FrameTransport.conjugate_comp
#print axioms CurrentMain.FrameTransport.conjugate_run
#print axioms CurrentMain.FrameTransport.raw_endpoint_transport
#print axioms CurrentMain.FrameTransport.reverse_complement_transition
#print axioms CurrentMain.FrameTransport.transportPath_exact
#print axioms CurrentMain.FrameTransport.common_mix
#print axioms CurrentMain.FrameTransport.adapted_mix
#print axioms CurrentMain.FrameTransport.decoded_adapted_mix
#print axioms CurrentMain.FrameTransport.decode_add
#print axioms CurrentMain.FrameTransport.decode_scale
#print axioms CurrentMain.FrameTransport.fresh_routing_commutes
#print axioms CurrentMain.FrameTransport.Frame.withSpectator
#print axioms CurrentMain.FrameTransport.ancestor_selector_common
#print axioms CurrentMain.FrameTransport.phase_adapter_formula
#print axioms CurrentMain.FrameTransport.phase_normalized_mix
#print axioms CurrentMain.FrameTransport.normalize_projective_identity

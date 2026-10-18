import Std
set_option maxHeartbeats 4000000
namespace SplitResidual
open Lean.Grind
variable {A M : Type} [IntModule A] [IntModule M]

structure AddMap (X Y : Type) [IntModule X] [IntModule Y] where
  apply : X → Y
  zero : apply 0 = 0
  add : ∀ x y, apply (x+y) = apply x + apply y
  neg : ∀ x, apply (-x) = -apply x

theorem map_sub (f : AddMap A M) (x y : A) :
    f.apply (x-y) = f.apply x - f.apply y := by
  simp only [AddCommGroup.sub_eq_add_neg, f.add, f.neg]

def proj (B : AddMap A M) (V : AddMap M A) (x : M) := B.apply (V.apply x)
def lifted (B : AddMap A M) (C : AddMap M M) (a : A) : M × M :=
  (-B.apply a, C.apply (B.apply a))
def lowered (V : AddMap M A) (C : AddMap M M) (z : M × M) : A :=
  V.apply z.1 - V.apply (C.apply z.2)
def undoLift (V : AddMap M A) (z : M × M) : A := -V.apply z.1
def embed (B : AddMap A M) (a : A) : M × M := (B.apply a, 0)
def d (B : AddMap A M) (V : AddMap M A) (C : AddMap M M) (z : M × M) : M × M :=
  (z.1 - proj B V z.1 + proj B V (C.apply z.2),
   C.apply (proj B V z.1) + z.2 - C.apply (proj B V (C.apply z.2)))
def residual (B : AddMap A M) (V : AddMap M A) (C : AddMap M M) (z : M × M) : M × M :=
  ((d B V C z).1-z.1, (d B V C z).2-z.2)

theorem factorization (B : AddMap A M) (V : AddMap M A) (C : AddMap M M) (z : M × M) :
    residual B V C z = lifted B C (lowered V C z) := by
  apply Prod.ext
  · simp only [residual,d,proj,lifted,lowered,map_sub]
    grind
  · simp only [residual,d,proj,lifted,lowered,map_sub]
    grind

theorem left_inverse (B : AddMap A M) (V : AddMap M A) (C : AddMap M M)
    (hVB : ∀ a, V.apply (B.apply a) = a) (a : A) :
    undoLift V (lifted B C a) = a := by
  simp only [undoLift,lifted,V.neg,hVB]
  grind

theorem right_inverse (B : AddMap A M) (V : AddMap M A) (C : AddMap M M)
    (hVB : ∀ a, V.apply (B.apply a) = a) (a : A) :
    lowered V C (embed B a) = a := by
  simp only [lowered,embed,C.zero,V.zero,hVB]
  grind

theorem projection_idempotent (B : AddMap A M) (V : AddMap M A)
    (hVB : ∀ a, V.apply (B.apply a) = a) (x : M) :
    proj B V (proj B V x) = proj B V x := by
  simp only [proj,hVB]

theorem image_iff (B : AddMap A M) (V : AddMap M A) (C : AddMap M M)
    (hVB : ∀ a, V.apply (B.apply a) = a) (z : M × M) :
    (∃ x, residual B V C x = z) ↔ (∃ a, lifted B C a = z) := by
  constructor
  · rintro ⟨x,hx⟩
    exact ⟨lowered V C x, (factorization B V C x).symm.trans hx⟩
  · rintro ⟨a,ha⟩
    refine ⟨embed B a, ?_⟩
    rw [factorization,right_inverse B V C hVB,ha]

theorem lifted_injective (B : AddMap A M) (V : AddMap M A) (C : AddMap M M)
    (hVB : ∀ a, V.apply (B.apply a) = a) {a b : A}
    (h : lifted B C a = lifted B C b) : a = b := by
  have h' := congrArg (undoLift V) h
  simpa only [left_inverse B V C hVB] using h'
theorem involution (B : AddMap A M) (V : AddMap M A) (C : AddMap M M)
    (hVB : ∀ a, V.apply (B.apply a) = a)
    (hCC : ∀ x, C.apply (C.apply x) = x) (z : M × M) :
    d B V C (d B V C z) = z := by
  apply Prod.ext <;>
    simp only [d,proj,map_sub,B.add,V.add,C.add,hVB,hCC] <;> grind

structure Bijection (X : Type) where
  forward : X → X
  backward : X → X
  back_forward : ∀ x, backward (forward x) = x
  forward_back : ∀ x, forward (backward x) = x

theorem conjugate_factorization {X Y : Type} (F : X → X) (U : Y → X)
    (W : X → Y) (h : ∀ x, F x = U (W x)) (T : Bijection X) (x : X) :
    T.forward (F (T.backward x)) = T.forward (U (W (T.backward x))) := by
  rw [h]

theorem conjugate_left_inverse {X Y : Type} (U : Y → X) (L : X → Y)
    (h : ∀ y, L (U y) = y) (T : Bijection X) (y : Y) :
    L (T.backward (T.forward (U y))) = y := by
  rw [T.back_forward,h]

theorem conjugate_right_inverse {X Y : Type} (W : X → Y) (R : Y → X)
    (h : ∀ y, W (R y) = y) (T : Bijection X) (y : Y) :
    W (T.backward (T.forward (R y))) = y := by
  rw [T.back_forward,h]

theorem conjugate_residual {X : Type} [IntModule X] (F : X → X)
    (T : Bijection X) (hsub : ∀ x y, T.forward (x-y) = T.forward x - T.forward y)
    (x : X) :
    T.forward (F (T.backward x)) - x =
      T.forward (F (T.backward x) - T.backward x) := by
  rw [hsub,T.forward_back]

def intIdentity : AddMap Int Int := ⟨id, rfl, by intros; rfl, by intros; rfl⟩
def intNegative : AddMap Int Int := ⟨fun x => -x, by decide,
  by intros; grind, by intros; rfl⟩

theorem integer_example (x y : Int) :
    d intIdentity intIdentity intNegative (x,y) = (-y,-x) := by
  apply Prod.ext <;> simp only [d,proj,intIdentity,intNegative,id] <;> grind

theorem integer_split_example (a : Int) :
    undoLift intIdentity (lifted intIdentity intNegative a) = a ∧
    lowered intIdentity intNegative (embed intIdentity a) = a := by
  constructor
  · exact left_inverse intIdentity intIdentity intNegative (fun _ => rfl) a
  · exact right_inverse intIdentity intIdentity intNegative (fun _ => rfl) a
end SplitResidual

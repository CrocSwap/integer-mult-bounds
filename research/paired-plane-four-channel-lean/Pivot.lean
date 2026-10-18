import Algebra
import Schur

namespace Four
open Lean.Grind
variable {K : Type} [CommRing K]

theorem reverse_inverse (a b : M K) (h : mul a b = one) : mul b a = one := by
  have hu : det b * det a = 1 := by
    have hd := congrArg det h
    rw [det_mul, det_one] at hd
    grind
  have hs : scale (det a) b = adj a := by
    calc
      scale (det a) b = mul (scale (det a) one) b := by rw [scale_mul, one_mul]
      _ = mul (mul (adj a) a) b := by rw [adj_left]
      _ = mul (adj a) (mul a b) := mul_assoc _ _ _
      _ = adj a := by rw [h, mul_one]
  have hb : b = scale (det b) (adj a) := by
    calc
      b = scale (det b * det a) b := by rw [hu, scale_one]
      _ = scale (det b) (scale (det a) b) := (scale_scale _ _ _).symm
      _ = scale (det b) (adj a) := by rw [hs]
  calc
    mul b a = mul (scale (det b) (adj a)) a := by rw [← hb]
    _ = scale (det b) (mul (adj a) a) := scale_mul _ _ _
    _ = scale (det b) (scale (det a) one) := by rw [adj_left]
    _ = one := by rw [scale_scale, hu, scale_one]

theorem sandwich (x q p y : M K) (h : mul q p = one) :
    mul (mul x q) (mul p y) = mul x y := by
  calc
    mul (mul x q) (mul p y) = mul x (mul q (mul p y)) := mul_assoc _ _ _
    _ = mul x (mul (mul q p) y) := by rw [mul_assoc]
    _ = mul x y := by rw [h, one_mul]
end Four

namespace Pivot
open Lean.Grind
open PairedC5
variable {K : Type} [CommRing K]

def blocks (a b c d : Mat2 K) : Four.M K :=
  ⟨a.a, a.b, b.a, b.b, a.c, a.d, b.c, b.d,
   c.a, c.b, d.a, d.b, c.c, c.d, d.c, d.d⟩
def upper (a : Four.M K) : Mat2 K := ⟨a.e00,a.e01,a.e10,a.e11⟩

omit [CommRing K] in
@[simp] theorem upper_blocks (a b c d : Mat2 K) : upper (blocks a b c d) = a := by
  cases a; rfl

theorem blocks_mul (a b c d e f g h : Mat2 K) :
    Four.mul (blocks a b c d) (blocks e f g h) =
      blocks (add (mul a e) (mul b g)) (add (mul a f) (mul b h))
             (add (mul c e) (mul d g)) (add (mul c f) (mul d h)) := by
  cases a; cases b; cases c; cases d; cases e; cases f; cases g; cases h
  simp only [Four.mul, blocks, mul, add, Four.M.mk.injEq]
  refine ⟨?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_,?_⟩ <;> grind

def ThroughFour (m : BlockMatrix K) (u v : Fin 5 → Fin 2 → Mat2 K) : Prop :=
  ∀ i j, m i j = add (mul (u i 0) (v j 0)) (mul (u i 1) (v j 1))

theorem factor_to_pivot (m : BlockMatrix K) (u v : Fin 5 → Fin 2 → Mat2 K)
    (hf : ThroughFour m u v)
    (h00 : m 0 0 = one) (h22 : m 2 2 = one)
    (h02 : m 0 2 = zero) (h20 : m 2 0 = zero) : FourPivot m := by
  let p := blocks (u 0 0) (u 0 1) (u 2 0) (u 2 1)
  let q := blocks (v 0 0) (v 2 0) (v 0 1) (v 2 1)
  have hpq : Four.mul p q = Four.one := by
    dsimp [p,q]
    rw [blocks_mul, ← hf 0 0, ← hf 0 2, ← hf 2 0, ← hf 2 2]
    rw [h00,h02,h20,h22]
    rfl
  have hqp := Four.reverse_inverse p q hpq
  intro i j
  have hx := Four.sandwich (blocks (u i 0) (u i 1) zero zero)
      q p (blocks (v j 0) zero (v j 1) zero) hqp
  dsimp [p,q] at hx
  rw [blocks_mul, blocks_mul, blocks_mul, blocks_mul] at hx
  have he := congrArg upper hx
  simp only [upper_blocks, mul_zero, zero_mul, add_zero] at he
  rw [← hf i 0, ← hf i 2, ← hf 0 j, ← hf 2 j, ← hf i j] at he
  exact he.symm

theorem no_four_channels (hne : (0 : K) ≠ 1) (m : BlockMatrix K)
    (u v : Fin 5 → Fin 2 → Mat2 K) (hfit : Fits m) (hf : ThroughFour m u v) : False := by
  have hz02 : m 0 2 = zero := hfit.2 0 2 (by unfold Far; decide)
  have hz20 : m 2 0 = zero := hfit.2 2 0 (by unfold Far; decide)
  exact no_four_pivot hne m hfit (factor_to_pivot m u v hf (hfit.1 0) (hfit.1 2) hz02 hz20)

/-- Four explicit scalar channels do realize the predecessor's one-edge-relaxed mask. -/
def relaxedFactor (i : Fin 5) (k : Fin 2) : Mat2 Int :=
  if (group i && k.val == 0) || (!group i && k.val == 1) then one else zero

theorem relaxed_through_four : ThroughFour relaxed relaxedFactor relaxedFactor := by
  unfold ThroughFour
  decide
end Pivot

#print axioms Four.reverse_inverse
#print axioms Pivot.factor_to_pivot
#print axioms Pivot.no_four_channels
#print axioms Pivot.relaxed_through_four

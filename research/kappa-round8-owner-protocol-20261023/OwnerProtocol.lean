/- Arbitrary-input dirty-helper returns and order-three owner completion.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
Only generic algebra, not a native compiler or recursive supplier theorem. -/
import Mathlib.Algebra.Group.Hom.Basic
import Mathlib.Tactic.Abel

namespace OwnerProtocol

variable {V W : Type*} [AddCommGroup V] [AddCommGroup W]

theorem dirty_return (F : V ≃+ V) (x y h : V) :
    (y + F (h + x)) - F ((F.symm (F (h + x))) - x) = y + F x ∧
    F ((F.symm (F (h + x))) - x) = F h := by
  simp only [AddEquiv.symm_apply_apply, add_sub_cancel_right, map_add]
  constructor
  · abel
  · trivial

def response (B : W →+ V) (C : V →+ W) (x : V) (z w : W) : V × (W × W) :=
  (x - B (C x) - B z + 26 • B w,
   (-(16 • C x) - 15 • z + 449 • w, -(C x) - z + 28 • w))

theorem first_query (B : W →+ V) (C : V →+ W)
    (h : ∀ z, C (B z) = 14 • z) (x : V) (z w : W) :
    C (response B C x z w).1 = -(13 • C x) - 14 • z + 364 • w := by
  simp only [response, map_add, map_sub, map_nsmul, h]
  abel

theorem order_three (B : W →+ V) (C : V →+ W)
    (h : ∀ z, C (B z) = 14 • z) (x : V) (z w : W) :
    let a := response B C x z w
    let b := response B C a.1 a.2.1 a.2.2
    response B C b.1 b.2.1 b.2.2 = (x,(z,w)) := by
  dsimp
  apply Prod.ext
  · simp only [response, map_add, map_sub, map_neg, map_nsmul, h]
    abel
  · apply Prod.ext <;>
      simp only [response, map_add, map_sub, map_neg, map_nsmul, h] <;> abel

#print axioms dirty_return
#print axioms first_query
#print axioms order_three
end OwnerProtocol

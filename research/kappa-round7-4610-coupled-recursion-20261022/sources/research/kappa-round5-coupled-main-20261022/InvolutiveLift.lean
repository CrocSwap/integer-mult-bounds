/- Universal algebra for the new dyadic involutive native response.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
The actual rectangular matrices and native word are bound in exact Python.
This proves no recursive caller or kappa claim. -/
import Mathlib.Algebra.Group.Hom.Basic
import Mathlib.Tactic.Abel

namespace InvolutiveLift

variable {V W : Type*} [AddCommGroup V] [AddCommGroup W]

def response (B : W →+ V) (C : V →+ W) (x : V) (z : W) : V × W :=
  (x - B (C x) - B z, 12 • C x + 13 • z)

theorem firstQuery (B : W →+ V) (C : V →+ W)
    (h : ∀ z, C (B z) = 14 • z) (x : V) (z : W) :
    C (x - B (C x) - B z) = -(13 • C x) - 14 • z := by
  simp only [map_sub,h]
  abel

theorem involutive (B : W →+ V) (C : V →+ W)
    (h : ∀ z, C (B z) = 14 • z) (x : V) (z : W) :
    response B C (response B C x z).1 (response B C x z).2 = (x,z) := by
  apply Prod.ext
  · change (x - B (C x) - B z) - B (C (x - B (C x) - B z)) -
      B (12 • C x + 13 • z) = x
    rw [firstQuery B C h]
    simp only [map_sub,map_neg,map_add,map_nsmul]
    abel
  · change 12 • C (x - B (C x) - B z) + 13 • (12 • C x + 13 • z) = z
    rw [firstQuery B C h]
    abel

#print axioms firstQuery
#print axioms involutive
end InvolutiveLift

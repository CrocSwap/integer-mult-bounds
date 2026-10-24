/- intqwq; substantial OpenAI Codex assistance. Apache-2.0.
   Generic all-input row/column query producer algebra. This does not assign
   eight Gaussian calls to an eight-output query. Its paid implementation is
   a separate obligation recorded in README.md. -/
import Mathlib.Algebra.Group.Hom.Basic
import Mathlib.Tactic.Abel

namespace RecursiveQueryProducer

variable {X Z : Type*} [AddCommGroup X] [AddCommGroup Z]

def row (V : X →+ Z) (s : X × Z) : X × Z := (s.1, s.2 + V s.1)
def col (U : Z →+ X) (s : X × Z) : X × Z := (s.1 + U s.2, s.2)
def lift (q : X ≃+ X) (s : X × Z) : X × Z := (q s.1, s.2)

theorem reflection_involutive (U : Z →+ X) (V : X →+ Z)
    (h : ∀ z, V (U z) = -(z+z)) (x : X) :
    (x + U (V x)) + U (V (x + U (V x))) = x := by
  simp only [map_add, h, map_neg]
  abel

/-- Four query shears return arbitrary workspace with only a sign change. -/
theorem four_shear_dirty_returns (U : Z →+ X) (V : X →+ Z)
    (h : ∀ z, V (U z) = -(z+z)) (x : X) (z : Z) :
    col U (row V (col U (row V (x,z)))) = (x + U (V x), -z) := by
  apply Prod.ext
  · simp only [row, col, map_add, h, map_neg]
    abel
  · simp only [row, col, map_add, h, map_neg]
    abel

/-- The same producer computes a conjugated reflection, with no zero-input
    promise on its auxiliary bank. -/
theorem conjugated_four_shear (U : Z →+ X) (V : X →+ Z)
    (h : ∀ z, V (U z) = -(z+z)) (q : X ≃+ X) (x : X) (z : Z) :
    col (q.symm.toAddMonoidHom.comp U)
      (row (V.comp q.toAddMonoidHom)
        (col (q.symm.toAddMonoidHom.comp U)
          (row (V.comp q.toAddMonoidHom) (x,z)))) =
      (q.symm (q x + U (V (q x))), -z) := by
  have hc : ∀ w, (V.comp q.toAddMonoidHom)
      ((q.symm.toAddMonoidHom.comp U) w) = -(w+w) := by
    intro w
    simpa only [AddMonoidHom.comp_apply, AddEquiv.toAddMonoidHom_eq_coe,
      AddMonoidHom.coe_coe, AddEquiv.apply_symm_apply] using h w
  have hf := four_shear_dirty_returns (q.symm.toAddMonoidHom.comp U)
    (V.comp q.toAddMonoidHom) hc x z
  simpa only [AddMonoidHom.comp_apply, AddEquiv.toAddMonoidHom_eq_coe,
    AddMonoidHom.coe_coe, map_add, AddEquiv.symm_apply_apply] using hf

/-- Exact row-query split. Applying qb and its inverse to every source
    field is a paid part of this implementation, not an eight-row credit. -/
theorem row_split (V : X →+ Z) (qa qb : X ≃+ X) (s : X × Z) :
    lift qb.symm (row (V.comp qa.toAddMonoidHom) (lift qb s)) =
      row (V.comp (qa.toAddMonoidHom.comp qb.toAddMonoidHom)) s := by
  apply Prod.ext <;> simp [lift, row]

theorem col_split (U : Z →+ X) (qa qb : X ≃+ X) (s : X × Z) :
    lift qb.symm (col (qa.symm.toAddMonoidHom.comp U) (lift qb s)) =
      col ((qb.symm.toAddMonoidHom.comp qa.symm.toAddMonoidHom).comp U) s := by
  apply Prod.ext <;> simp [lift, col, map_add]

end RecursiveQueryProducer

#print axioms RecursiveQueryProducer.reflection_involutive
#print axioms RecursiveQueryProducer.four_shear_dirty_returns
#print axioms RecursiveQueryProducer.conjugated_four_shear
#print axioms RecursiveQueryProducer.row_split
#print axioms RecursiveQueryProducer.col_split

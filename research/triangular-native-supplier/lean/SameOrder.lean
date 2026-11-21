import Mathlib.Algebra.Module.Equiv.Basic
import Mathlib.Tactic

namespace SameOrder

section Body

variable {R M : Type*} [CommRing R] [AddCommGroup M] [Module R M]

def weighted (A : M ≃ₗ[R] M) (P : M →ₗ[R] M) (z : M × M) : M × M :=
  let h := A.symm z.1
  let d := P (z.2 - h)
  (A (h + d), z.2 - d)

def route (A S : M ≃ₗ[R] M) (z : M × M) : M × M :=
  (A (S.symm (A.symm z.1)), S.symm z.2)

theorem restore (A S : M ≃ₗ[R] M) (z : M × M) :
    route A S.symm (route A S z) = z := by
  simp [route]

theorem followWord (A S T : M ≃ₗ[R] M) (z : M × M) :
    route A T (route A S z) = route A (T.trans S) z := by
  simp [route]

theorem matchProjector (A S : M ≃ₗ[R] M) (P Q : M →ₗ[R] M)
    (matchPQ : ∀ x, P (S x) = S (Q x)) (z : M × M) :
    route A S.symm (weighted A Q (route A S z)) = weighted A P z := by
  have transported (x : M) : S (Q (S.symm x)) = P x := by
    rw [← matchPQ, S.apply_symm_apply]
  simp only [route, weighted, LinearEquiv.symm_apply_apply, LinearEquiv.symm_symm,
    ← map_sub, transported, map_add, LinearEquiv.apply_symm_apply]
  simp only [map_sub, transported, LinearEquiv.apply_symm_apply]

theorem singleReturn (A : M ≃ₗ[R] M) (z : M × M) :
    weighted A LinearMap.id z = (A z.2, A.symm z.1) := by
  simp only [weighted, LinearMap.id_coe, id_eq]
  have h : A.symm z.1 + (z.2 - A.symm z.1) = z.2 := by abel
  have t : z.2 - (z.2 - A.symm z.1) = A.symm z.1 := by abel
  rw [h,t]

theorem independentPayload {V : Type*} (F : M × M → V) (A S : M ≃ₗ[R] M)
    (P Q : M →ₗ[R] M) (h : ∀ x, P (S x) = S (Q x)) (z : M × M) :
    F (route A S.symm (weighted A Q (route A S z))) = F (weighted A P z) :=
  congrArg F (matchProjector A S P Q h z)

end Body

section Coordinates

variable {R ι : Type*} [CommRing R] [DecidableEq ι]

def shear (v : ι → R) (source target : ι) (k : R) : ι → R :=
  fun i => if i = target then v i + k * v source else v i

def applyWeight (a : ι → Rˣ) (v : ι → R) : ι → R :=
  fun i => (a i : R) * v i

theorem conjugateShear (a : ι → Rˣ) (v : ι → R) (source target : ι) (k : R) :
    applyWeight a (shear (applyWeight (fun i => (a i)⁻¹) v) source target (-k)) =
      shear v source target (-k * (a target : R) * ((a source)⁻¹ : Rˣ)) := by
  funext i
  by_cases h : i = target
  · subst i
    simp only [applyWeight, shear, ite_true, mul_add, ← mul_assoc, Units.mul_inv, one_mul]
    ring
  · simp [applyWeight, shear, h, ← mul_assoc]

theorem undoShear (v : ι → R) {source target : ι} (h : source ≠ target) (k : R) :
    shear (shear v source target k) source target (-k) = v := by
  funext i
  by_cases hit : i = target
  · subst i
    simp [shear, h]
  · simp [shear, hit]

end Coordinates

section Pivots

variable {X : Type*}

structure Ends (X : Type*) where
  h0 : X
  hp : X
  tp : X
  tl : X

def ac (z : Ends X) : Ends X := ⟨z.tp, z.hp, z.h0, z.tl⟩
def bd (z : Ends X) : Ends X := ⟨z.h0, z.tl, z.tp, z.hp⟩
def ad (z : Ends X) : Ends X := ⟨z.tl, z.hp, z.tp, z.h0⟩
def bc (z : Ends X) : Ends X := ⟨z.h0, z.tp, z.hp, z.tl⟩

theorem bothPivots (z : Ends X) :
    bc (ad (bd (ac z))) = ⟨z.hp, z.h0, z.tl, z.tp⟩ := rfl

theorem onlyHead (z : Ends X) :
    ad (bd (ad z)) = ⟨z.hp, z.h0, z.tp, z.tl⟩ := rfl

theorem onlyTail (z : Ends X) :
    ac (ad (ac z)) = ⟨z.h0, z.hp, z.tl, z.tp⟩ := rfl

end Pivots

#print axioms restore
#print axioms followWord
#print axioms matchProjector
#print axioms singleReturn
#print axioms independentPayload
#print axioms conjugateShear
#print axioms undoShear
#print axioms bothPivots
#print axioms onlyHead
#print axioms onlyTail

end SameOrder

import BooleanGauss

/-! The leaf evaluator is applied to two masks extracted from the supplied
operand words. Each free variable represents exactly one mixed input pair. -/
namespace QuadraticProduct
open Finset TernaryCollect BooleanGauss
open scoped BigOperators

def leftForm {m : ℕ} (t : TritWord m) (i : Fin m) : Aff (Free t) :=
  if h : t i = none then .var ⟨i,h⟩ else .const ((t i).getD false)

def rightForm {m : ℕ} (t : TritWord m) (i : Fin m) : Aff (Free t) :=
  if h : t i = none then .plus (.const true) (.var ⟨i,h⟩) else .const ((t i).getD false)

theorem leftForm_eval {m} (t : TritWord m) (u : Free t → Bool) :
    (fun i ↦ (leftForm t i).eval u) = left t u := by
  funext i
  by_cases h : t i = none <;> simp [h,leftForm,left,Aff.eval]

theorem rightForm_eval {m} (t : TritWord m) (u : Free t → Bool) :
    (fun i ↦ (rightForm t i).eval u) = right t u := by
  funext i
  by_cases h : t i = none <;> simp [h,rightForm,right,Aff.eval]

def takePhase {ι} (f : Bool) (q : Quad ι) : Quad ι := if f then q else .affine (.const false)

def restricted {m} (t : TritWord m) (A B : Model (Fin m)) (a b : Bool) : Model (Free t) :=
  let L := A.sub (leftForm t)
  let R := B.sub (rightForm t)
  ⟨L.rows ++ R.rows, .plus (takePhase a L.phase) (takePhase b R.phase)⟩

theorem energy_leaf {m} (t : TritWord m) (A B : Model (Fin m)) (a b : Bool) :
    mass (restricted t A B a b) = signedLeaf t (support A.rows) A.phase.eval
      (support B.rows) B.phase.eval a b := by
  unfold mass signedLeaf leaf
  apply Finset.sum_congr rfl
  intro u _
  have he {ι} (f : Bool) (q : Quad ι) (u : ι → Bool) : (takePhase f q).eval u = (f && q.eval u) := by
    cases f <;> simp [takePhase,Quad.eval,Aff.eval]
  have hh {ι} (r s : List (Aff ι)) (u : ι → Bool) :
      support (r++s) u = (support r u && support s u) := by simp [support,List.all_append]
  simp only [weight, restricted, Model.sub, hh, support_sub, Quad.eval, he, Quad.eval_sub,
    leftForm_eval, rightForm_eval]

/-- Renaming the surviving positions does not charge or assume a named
Clifford decoder. The recursive evaluator eliminates them in this order. -/
noncomputable def gauss {ι : Type} [Fintype ι] [DecidableEq ι] (M : Model ι) : ℤ :=
  evaluate (Fintype.card ι) (M.sub (fun i ↦ .var (Fintype.equivFin ι i)))

theorem gauss_eq_mass {ι : Type} [Fintype ι] [DecidableEq ι] (M : Model ι) : gauss M = mass M := by
  rw [gauss, evaluate_correct]
  let e := Fintype.equivFin ι
  refine Fintype.sum_equiv (e.symm.arrowCongr (Equiv.refl Bool)) _ _ ?_
  intro x
  rw [weight_sub]
  rfl

theorem leaf_outputs {m} (t : TritWord m) (A B : Model (Fin m)) (a b : Bool) :
    gauss (restricted t A B a b) = 0 ∨ ∃ k ≤ Fintype.card (Free t),
      gauss (restricted t A B a b) = (2:ℤ)^k ∨ gauss (restricted t A B a b) = -(2:ℤ)^k :=
  signed_power _ _

noncomputable def numerator {m} (t : TritWord m) (A B : Model (Fin m)) : ℤ :=
  let g := fun a b ↦ gauss (restricted t A B a b)
  g false false - g true false - g false true + g true true

def mask {m} (M : Model (Fin m)) (x : Bits m) := support M.rows x && M.phase.eval x

theorem numerator_correct {m} (t : TritWord m) (A B : Model (Fin m)) :
    numerator t A B = 4*(coeff (mask A) (mask B) t : ℤ) := by
  unfold numerator
  simp only [gauss_eq_mass, energy_leaf]
  exact (four_at t (support A.rows) A.phase.eval (support B.rows) B.phase.eval).symm

noncomputable def fromGauss {m} (A B : Model (Fin m)) : ℕ :=
  ((∑ t : TritWord m, (2:ℤ)^(exponent t)*numerator t A B) / 4).toNat

/-- The raw bits are arbitrary. Each reported mask must agree at every
physical input position. Division by four is exact before conversion. -/
theorem from_operand_bits {m} (a b : Bits m → Bool) (A B : Model (Fin m))
    (ha : ∀ x, a x = mask A x) (hb : ∀ y, b y = mask B y) :
    fromGauss A B = operand a * operand b := by
  rw [funext ha, funext hb, fromGauss]
  have h := four_product (support A.rows) A.phase.eval (support B.rows) B.phase.eval
  simp only [numerator, gauss_eq_mass, energy_leaf]
  rw [← h, Int.mul_ediv_cancel_left _ (by decide : (4:ℤ) ≠ 0), Int.toNat_natCast]
  rfl

#print axioms energy_leaf
#print axioms leaf_outputs
#print axioms numerator_correct
#print axioms from_operand_bits
end QuadraticProduct

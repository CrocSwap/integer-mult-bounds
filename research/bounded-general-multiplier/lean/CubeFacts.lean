import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Card
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

namespace CubeFacts
open Finset
open scoped BigOperators MatrixGroups

private theorem product_bound {ι : Type*} (s : Finset ι) (f : ι→ℚ)
    (good : ∀ i, 0≤f i ∧ f i≤1) :
    1 - ∑ i ∈ s, f i ≤ ∏ i ∈ s, (1-f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    rw [Finset.sum_insert ha, Finset.prod_insert ha]
    have hs : 0≤∑ i ∈ s, f i := Finset.sum_nonneg fun i _ ↦ (good i).1
    calc
      _ ≤ (1-f a)*(1-∑ i ∈ s, f i) := by nlinarith [mul_nonneg (good a).1 hs]
      _ ≤ _ := mul_le_mul_of_nonneg_left ih (by linarith [(good a).2])

private theorem ternary_sum (n : ℕ) :
    (∑ i:Fin n, (3:ℚ)^(i:ℕ)) = ((3:ℚ)^n-1)/2 := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Fin.sum_univ_castSucc]
    simp only [Fin.val_castSucc,Fin.val_last,ih,pow_succ]
    ring

/-- The physical ternary cube adds strictly less than one zero fibre per
genuine invertible low fibre, in every matrix dimension. -/
theorem cube_padding (n : ℕ) :
    Nat.card (Matrix (Fin n) (Fin n) (ZMod 3)) < 2 * Nat.card (GL (Fin n) (ZMod 3)) := by
  let f := fun i : Fin n ↦ (3:ℚ)^(i:ℕ)/3^n
  have hpos : (0:ℚ)<3^n := by positivity
  have good (i : Fin n) : 0≤ f i ∧ f i≤1 := by
    refine ⟨by dsimp [f]; positivity,?_⟩
    dsimp [f]
    rw [div_le_one hpos]
    exact pow_le_pow_right₀ (by norm_num) i.isLt.le
  have hprod := product_bound (Finset.univ:Finset (Fin n)) f good
  have hsum : (∑ i : Fin n, f i) = ((3:ℚ)^n-1)/(2*(3:ℚ)^n) := by
    dsimp [f]
    simp only [div_eq_mul_inv,←Finset.sum_mul,ternary_sum]
    ring
  have room : (1:ℚ)/2 < ∏ i:Fin n, (1-f i) := by
    apply lt_of_lt_of_le _ hprod
    rw [hsum]
    have h : ((3:ℚ)^n-1)/(2*(3:ℚ)^n) < 1/2 := by
      apply (div_lt_div_iff₀ (by positivity : (0:ℚ)<2*3^n) (by norm_num)).mpr
      linarith
    linarith
  have restore : (∏ i:Fin n, ((3:ℚ)^n-3^(i:ℕ))) =
      (3:ℚ)^(n*n)*(∏ i:Fin n, (1-f i)) := by
    calc
      _ = ∏ i:Fin n, (3:ℚ)^n*(1-f i) := by
        apply Finset.prod_congr rfl
        intro i _
        dsimp [f]
        field_simp
      _ = _ := by rw [Finset.prod_mul_distrib]; simp [pow_mul]
  have lower : (3:ℚ)^(n*n) < 2*(∏ i:Fin n, ((3:ℚ)^n-3^(i:ℕ))) := by
    rw [restore]
    nlinarith [mul_lt_mul_of_pos_left room (show (0:ℚ)<3^(n*n) by positivity)]
  have nums (i:Fin n) : (3:ℕ)^(i:ℕ) ≤ 3^n := Nat.pow_le_pow_right (by decide) i.isLt.le
  have casted : (3:ℚ)^(n*n) < 2 * (↑(∏ i:Fin n, ((3:ℕ)^n-3^(i:ℕ))):ℚ) := by
    simpa only [Nat.cast_prod,Nat.cast_sub (nums _),Nat.cast_pow,Nat.cast_ofNat] using lower
  rw [Matrix.card_matrix,Matrix.card_GL_field (𝔽:=ZMod 3) n]
  simp only [Nat.card_eq_fintype_card, Fintype.card_fin, ZMod.card]
  exact_mod_cast casted

/-- A unit right factor preserves exactly the rows that survive extraction. -/
theorem same_low {R : Type*} [Monoid R] (g : R) (s : Rˣ) :
    IsUnit (g*s.val) ↔ IsUnit g := by
  constructor
  · intro h
    simpa [mul_assoc] using h.mul s⁻¹.isUnit
  · exact fun h ↦ h.mul s.isUnit

noncomputable def pad {R : Type*} [Monoid R] {α : Type*} [Zero α]
    (f : {g : R // IsUnit g} → α) (g : R) : α := by
  classical
  exact if h : IsUnit g then f ⟨g,h⟩ else 0

/-- Apply the real high-fibre operation and the low right matcher on the
cube. Restriction after the operation gives exactly the genuine fields. -/
theorem padded_route {R : Type*} [Monoid R] {α : Type*} [Zero α] (s : Rˣ)
    (f : {g : R // IsUnit g} → α) (high : R → α → α) (hz : ∀ g, high g 0=0) (g : R) :
    pad (fun i ↦ high i.val (f ⟨i.val*s.val,(same_low i.val s).mpr i.property⟩)) g =
       high g (pad f (g*s.val)) := by
  by_cases h : IsUnit g
  · simp [pad,h,(same_low g s).mpr h]
  · have bad : ¬IsUnit (g*s.val) := fun hs ↦ h ((same_low g s).mp hs)
    simp [pad,h,bad,hz]

#print axioms padded_route
#print axioms cube_padding
#print axioms same_low
end CubeFacts

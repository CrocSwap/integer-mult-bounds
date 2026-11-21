import PaddedGrid
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace TriangularPaddedTensor

open Finset CirculantTraceProduct
open scoped BigOperators

variable {d : ℕ} (s t : Fin d → ℕ) [∀ i, NeZero (s i)]

noncomputable def wire (p : Bool) (A : Finset (Fin d)) (i : Fin d) (j k : Fin (t i)) : ℂ :=
  if i ∈ A then paddedEntry (r := s i) p j k else if j = k then 1 else 0

noncomputable def step (p : Bool) (A : Finset (Fin d)) (x : Field t) (k : Carrier t) : ℂ :=
  ∑ j : Carrier t, (∏ i, wire s t p A i (j i) (k i))*x j

theorem sum_of_products {α : Fin d → Type*} [∀ i, Fintype (α i)]
    {R : Type*} [CommSemiring R] (f : (i : Fin d) → α i → R) :
    ∑ x : (i : Fin d) → α i, (∏ i, f i (x i)) = ∏ i, ∑ a, f i a := by
  simpa using (Finset.prod_univ_sum (fun _ ↦ Finset.univ) f).symm

theorem one_wire (p : Bool) (A B : Finset (Fin d)) (h : Disjoint A B)
    (i : Fin d) (j k : Fin (t i)) :
    ∑ a, wire s t p A i j a * wire s t p B i a k = wire s t p (A ∪ B) i j k := by
  classical
  by_cases ia : i ∈ A
  · have ib : i ∉ B := fun ib ↦ Finset.disjoint_left.mp h ia ib
    simp [wire, ia, ib, mul_ite]
  · by_cases ib : i ∈ B
    · simp [wire, ia, ib]
    · simp [wire, ia, ib]

/-- Two disjoint complete mask steps equal the single tensor on their union. -/
theorem disjoint_steps (p : Bool) (A B : Finset (Fin d)) (h : Disjoint A B)
    (x : Field t) : step s t p B (step s t p A x) = step s t p (A ∪ B) x := by
  classical
  funext k
  simp only [step, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  calc
    _ = ∑ a : Carrier t, (∏ i, wire s t p A i (j i) (a i) *
                            wire s t p B i (a i) (k i)) * x j := by
      apply Finset.sum_congr rfl
      intro a _
      rw [Finset.prod_mul_distrib]
      ring
    _ = _ := by
      rw [← Finset.sum_mul, sum_of_products (fun i a ↦
        wire s t p A i (j i) a * wire s t p B i a (k i))]
      simp_rw [one_wire s t p A B h]

theorem empty_step (p : Bool) (x : Field t) : step s t p ∅ x = x := by
  classical
  funext k
  have delta (j : Carrier t) : (∏ i, wire s t p ∅ i (j i) (k i)) = if j=k then 1 else 0 := by
    by_cases h : j=k
    · subst j
      simp [wire]
    · obtain ⟨i,hi⟩ : ∃ i, j i ≠ k i := by simpa [funext_iff] using h
      simp only [h, ite_false]
      exact Finset.prod_eq_zero (Finset.mem_univ i) (by simp [wire,hi])
  simp [step, delta, ite_mul]

theorem full_step (p : Bool) (x : Field t) :
    step s t p Finset.univ x = paddedMean s t p x := by
  funext k
  simp [step, paddedMean, wire]

def seenAxes (mask : ℕ → Finset (Fin d)) : ℕ → Finset (Fin d)
  | 0 => ∅
  | k+1 => seenAxes mask k ∪ mask k

theorem wire_mass (p : Bool) (A : Finset (Fin d)) (i : Fin d) (ht : s i ≤ t i)
    (k : Fin (t i)) : (∑ j, ‖wire s t p A i j k‖) = 1 := by
  classical
  by_cases ia : i ∈ A
  · by_cases hk : k.val < s i
    · have coeff (j : Fin (t i)) : ‖wire s t p A i j k‖ =
          if j.val < s i then (s i : ℝ)⁻¹ else 0 := by
        by_cases hj : j.val < s i
        · simp [wire, ia, paddedEntry, hk, hj, CirculantGridBridge.entry, ZMod.stdAddChar_apply]
        · have ne : j ≠ k := fun eq ↦ hj (eq ▸ hk)
          simp [wire, ia, paddedEntry, hk, hj, ne]
      let embed := Fin.castLE ht
      have image : Finset.univ.filter (fun j : Fin (t i) ↦ j.val < s i) =
          Finset.univ.image embed := by
        ext j
        simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_image]
        constructor
        · exact fun hj ↦ ⟨⟨j.val,hj⟩, rfl⟩
        · rintro ⟨z,rfl⟩
          exact z.isLt
      simp_rw [coeff, ← Finset.sum_filter]
      rw [image, Finset.sum_const, Finset.card_image_of_injective _ (Fin.castLE_injective ht)]
      have hr : (s i : ℝ) ≠ 0 := NeZero.ne _
      simp [nsmul_eq_mul,hr]
    · simp [wire, ia, paddedEntry, hk, apply_ite]
  · simp [wire, ia, apply_ite]

theorem step_contracts (p : Bool) (A : Finset (Fin d)) (ht : ∀ i, s i ≤ t i)
    {r : ℝ} {x y : Field t} (hxy : ∀ j, ‖x j - y j‖ ≤ r) (k : Carrier t) :
    ‖step s t p A x k - step s t p A y k‖ ≤ r := by
  classical
  let weight (j : Carrier t) := ∏ i, wire s t p A i (j i) (k i)
  change ‖∑ j, weight j * x j - ∑ j, weight j * y j‖ ≤ r
  rw [← Finset.sum_sub_distrib]
  simp_rw [← mul_sub]
  have total : (∑ j, ‖weight j‖) = 1 := by
    simp only [weight, norm_prod]
    rw [sum_of_products (fun i a ↦ ‖wire s t p A i a (k i)‖)]
    simp [wire_mass s t p A _ (ht _)]
  calc
    _ ≤ ∑ j, ‖weight j * (x j-y j)‖ := norm_sum_le _ _
    _ ≤ ∑ j, ‖weight j‖ * r := Finset.sum_le_sum fun j _ ↦ by
      rw [norm_mul]
      exact mul_le_mul_of_nonneg_left (hxy j) (norm_nonneg _)
    _ = r := by rw [← Finset.sum_mul,total,one_mul]

#print axioms disjoint_steps
#print axioms empty_step
#print axioms full_step
#print axioms wire_mass
#print axioms step_contracts

end TriangularPaddedTensor

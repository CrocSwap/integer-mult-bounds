import TernaryCollect
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Algebra.BigOperators.Fin

/-! Pair a ternary observation with the actual tensor Pauli matrices.
The integer identity applies to arbitrary joint tables. -/
namespace PauliReadout
open TernaryCollect
open scoped BigOperators

variable {R : Type*} [CommRing R]

abbrev Label := Fin 3

/-- The labels 0, 1 and 2 denote I, X and Z. -/
def pauli (w : Label) : Matrix Bool Bool R := fun x y ↦
  if w = 0 then (if x = y then 1 else 0) else
  if w = 1 then (if x = y then 0 else 1) else
  if x = y then (if x then -1 else 1) else 0

/-- A fixed trit reads 00 or 11. The middle trit reads 01 and 10. -/
def observe (d : Trit) : Matrix Bool Bool R :=
  fun x y ↦ if trit x y = d then 1 else 0

theorem cleared_observations :
    (2:R) • (observe (some false) : Matrix Bool Bool R) = pauli 0 + pauli 2 ∧
    (observe none : Matrix Bool Bool R) = pauli 1 ∧
    (2:R) • (observe (some true) : Matrix Bool Bool R) = pauli 0 - pauli 2 := by
  refine ⟨?_,?_,?_⟩ <;> ext x y <;> cases x <;> cases y <;>
    norm_num [observe, pauli, trit]

def pairing {α : Type*} [Fintype α] (U Y : Matrix α α R) : R :=
  (U.transpose * Y).trace

theorem pairing_entries {α : Type*} [Fintype α] (U Y : Matrix α α R) :
    pairing U Y = ∑ v : α × α, U v.1 v.2 * Y v.1 v.2 := by
  classical
  simp only [pairing, Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.transpose_apply, Fintype.sum_prod_type]
  exact Finset.sum_comm

theorem local_resolution (d : Trit) (x y : Bool) :
    (∑ w : Label, pairing (observe d : Matrix Bool Bool R) (pauli w) * pauli w x y) =
      2 * observe d x y := by
  rcases d with _ | c <;> try cases c
  all_goals cases x <;> cases y <;>
    norm_num [pairing, Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, Matrix.transpose_apply,
      Fin.sum_univ_three, Fintype.sum_bool, pauli, observe, trit]

def word {m : ℕ} (w : Fin m → Label) : Matrix (Bits m) (Bits m) R :=
  fun x y ↦ ∏ i, pauli (w i) (x i) (y i)

def weight {m : ℕ} (t : TritWord m) (w : Fin m → Label) : R :=
  ∏ i, pairing (observe (t i) : Matrix Bool Bool R) (pauli (w i))

theorem tensor_resolution {m : ℕ} (t : TritWord m) (x y : Bits m) :
    (∑ w : Fin m → Label, weight t w * word w x y : R) =
      (2:R)^m * (if classify x y = t then 1 else 0) := by
  classical
  simp only [weight, word, ← Finset.prod_mul_distrib]
  rw [← Fintype.prod_sum (fun (i : Fin m) (v : Label) ↦
    pairing (observe (t i) : Matrix Bool Bool R) (pauli v) * pauli v (x i) (y i))]
  simp_rw [local_resolution]
  rw [Finset.prod_mul_distrib]
  simp only [Finset.prod_const, Finset.card_univ, Fintype.card_fin]
  congr 1
  by_cases h : classify x y = t
  · have he (i : Fin m) : trit (x i) (y i) = t i := congrFun h i
    simp [observe, he, h]
  · obtain ⟨i,hi⟩ : ∃ i, trit (x i) (y i) ≠ t i := by
      by_contra! bad
      exact h (funext bad)
    simp only [h,↓reduceIte]
    exact Finset.prod_eq_zero (Finset.mem_univ i) (by simp [observe,hi])

theorem selected_pairs {m : ℕ} (t : TritWord m) (Y : Matrix (Bits m) (Bits m) R) :
    (∑ p : Bits m × Bits m, if classify p.1 p.2 = t then Y p.1 p.2 else 0) = leaf t Y := by
  classical
  rw [← (pairChart m).sum_comp, Fintype.sum_sigma]
  change (∑ s, ∑ u : Free s → Bool,
    if classify (left s u) (right s u) = t then Y (left s u) (right s u) else 0) = _
  simp_rw [classify_expand]
  simp [Finset.sum_ite_irrel, leaf]

/-- The raw Pauli trace reconstruction equals 2^m times the caller's own leaf. -/
theorem pauli_readout {m : ℕ} (t : TritWord m) (Y : Matrix (Bits m) (Bits m) R) :
    (∑ w : Fin m → Label, weight t w * pairing (word w) Y) = (2:R)^m * leaf t Y := by
  classical
  simp_rw [pairing_entries, Finset.mul_sum, ← mul_assoc]
  rw [Finset.sum_comm]
  simp_rw [← Finset.sum_mul, tensor_resolution, mul_assoc]
  rw [← Finset.mul_sum]
  congr 1
  simpa [ite_mul] using selected_pairs t Y

/-- Integer Pauli traces recover each literal coefficient in `raw_product`. -/
theorem pauli_product_coefficient {m : ℕ} (t : TritWord m) (a b : Bits m → Bool) :
    (∑ w : Fin m → Label, weight (R:=ℤ) t w * pairing (word w)
      (fun x y ↦ (value (a x) : ℤ) * (value (b y) : ℤ))) =
      (2:ℤ)^m * (coeff a b t : ℤ) := by
  simpa [coeff, leaf] using
    (pauli_readout t (fun x y ↦ (value (a x) : ℤ) * (value (b y) : ℤ)))

/-- The weighted readouts give the product of the two binary integers. -/
theorem pauli_product {m : ℕ} (a b : Bits m → Bool) :
    (2:ℤ)^m * ((operand a * operand b : ℕ) : ℤ) =
      ∑ t : TritWord m, (2:ℤ)^(exponent t) *
        (∑ w : Fin m → Label, weight (R:=ℤ) t w * pairing (word w)
          (fun x y ↦ (value (a x) : ℤ) * (value (b y) : ℤ))) := by
  rw [raw_product, Nat.cast_sum, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro t _
  rw [Nat.cast_mul, Nat.cast_pow, Nat.cast_ofNat, pauli_product_coefficient t a b]
  ring

#print axioms cleared_observations
#print axioms local_resolution
#print axioms tensor_resolution
#print axioms pauli_readout
#print axioms pauli_product_coefficient
#print axioms pauli_product
end PauliReadout

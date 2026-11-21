import Mathlib.Analysis.Fourier.ZMod
import Mathlib.Data.Nat.GCD.BigOperators
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

namespace MixedRankCoordinates

open Finset
open scoped BigOperators Real

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def cofactor (s : ι → ℕ) (i : ι) : ℕ := ∏ j ∈ univ.erase i, s j
def weight (s m : ι → ℕ) : ℕ := ∑ i, cofactor s i * m i

theorem cofactor_mul (s : ι → ℕ) (i : ι) : cofactor s i * s i = ∏ j, s j :=
  Finset.prod_erase_mul _ _ (mem_univ i)

theorem admissible_weight (s m : ι → ℕ)
    (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
    (hm : ∀ i, Nat.Coprime (m i) (s i)) : Nat.Coprime (weight s m) (∏ i, s i) := by
  apply Nat.coprime_fintype_prod_right_iff.mpr
  intro i
  have hc : Nat.Coprime (cofactor s i) (s i) := by
    apply Nat.Coprime.prod_left
    intro j hj
    exact hs (mem_erase.mp hj).1
  apply (ZMod.isUnit_iff_coprime _ _).mp
  have he : (weight s m : ZMod (s i)) = (cofactor s i * m i : ℕ) := by
    simp only [weight, Nat.cast_sum, Nat.cast_mul]
    apply Finset.sum_eq_single i
    · intro j _ hji
      have hd : s i ∣ cofactor s j := Finset.dvd_prod_of_mem _ (mem_erase.mpr ⟨Ne.symm hji, mem_univ _⟩)
      rw [(ZMod.natCast_eq_zero_iff _ _).mpr hd, zero_mul]
    · simp
  rw [he, Nat.cast_mul]
  exact ((ZMod.unitOfCoprime _ hc).isUnit.mul (ZMod.unitOfCoprime _ (hm i)).isUnit)

theorem physical_kernel (s m : ι → ℕ) [∀ i, NeZero (s i)] [NeZero (∏ i, s i)] (v : ℤ) :
    (∏ i, ZMod.stdAddChar (((v * (m i : ℤ) : ℤ) : ZMod (s i)))) =
      ZMod.stdAddChar (((v * (weight s m : ℤ) : ℤ) : ZMod (∏ i, s i))) := by
  simp only [ZMod.stdAddChar_coe]
  simp only [Int.cast_mul, Int.cast_natCast, ← Complex.exp_sum]
  congr 1
  simp only [weight, Nat.cast_sum, Nat.cast_mul, Finset.mul_sum, Finset.sum_div]
  apply Finset.sum_congr rfl
  intro i _
  have hp : ((cofactor s i : ℕ) : ℂ) * (s i : ℂ) = ((∏ j, s j : ℕ) : ℂ) := by
    exact_mod_cast cofactor_mul s i
  have hi : (s i : ℂ) ≠ 0 := NeZero.ne _
  have hS : (((∏ j, s j : ℕ) : ℂ)) ≠ 0 := NeZero.ne _
  field_simp
  rw [← hp]
  ring

#print axioms admissible_weight
#print axioms physical_kernel
end MixedRankCoordinates

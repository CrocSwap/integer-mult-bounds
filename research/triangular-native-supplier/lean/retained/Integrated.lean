import Coordinates
import Recovery
import Mathlib.Tactic.NormNum

namespace MixedRankIntegrated

open Finset MixedRankCoordinates MixedRankRecovery

variable {d : ℕ} (s t : Fin d → ℕ)
  (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  (ht : ∀ i, Nat.Coprime (t i) (s i))
  [∀ i, NeZero (s i)] [NeZero (∏ i, s i)]

def prefixProduct (s : Fin d → ℕ) (i : Fin d) := ∏ j ∈ univ.filter (· < i), s j

omit [∀ i, NeZero (s i)] [NeZero (∏ i, s i)] in
include hs in
theorem prefix_coprime (i : Fin d) : Nat.Coprime (prefixProduct s i) (s i) := by
  apply Nat.Coprime.prod_left
  intro j hj
  exact hs (ne_of_lt (mem_filter.mp hj).2)

def mu (i : Fin d) : (ZMod (s i))ˣ := (ZMod.unitOfCoprime _ (prefix_coprime s hs i))⁻¹

omit [∀ i, NeZero (s i)] [NeZero (∏ i, s i)] in
theorem prefix_inverse (i : Fin d) : ((prefixProduct s i : ℕ) : ZMod (s i)) * (mu s hs i).val = 1 := by
  change ((ZMod.unitOfCoprime _ (prefix_coprime s hs i)).val) *
    ((ZMod.unitOfCoprime _ (prefix_coprime s hs i))⁻¹).val = 1
  simp

def factor (i : Fin d) : ℕ := t i * (mu s hs i).val.val ^ 2

omit [NeZero (∏ i, s i)] in
include ht in
theorem factor_coprime (i : Fin d) : Nat.Coprime (factor s t hs i) (s i) := by
  apply (ZMod.isUnit_iff_coprime _ _).mp
  simp only [factor, Nat.cast_mul, Nat.cast_pow, ZMod.natCast_zmod_val]
  exact ((ZMod.unitOfCoprime _ (ht i)).isUnit.mul ((mu s hs i).isUnit.pow 2))

def sourceUnit : (ZMod (∏ i, s i))ˣ :=
  ZMod.unitOfCoprime _ (admissible_weight s (factor s t hs) hs (factor_coprime s t hs ht))

theorem physical_character (v : ℤ) :
    (∏ i, ZMod.stdAddChar (((v * (factor s t hs i : ℤ) : ℤ) : ZMod (s i)))) =
      ZMod.stdAddChar ((v : ZMod (∏ i, s i)) * (sourceUnit s t hs ht).val) := by
  rw [physical_kernel]
  simp [sourceUnit]

abbrev SourceSignal (s : Fin d → ℕ) := Signal (∏ i, s i)

theorem product_at_physical_coordinates (B : ℕ) (hB : 32 ≤ B) (hbnd : ∏ i, s i ≤ B)
    (fw bw : SourceSignal s → SourceSignal s) (mul : ℂ → ℂ → ℂ)
    (e : ℝ) (he : 0 ≤ e) (herr : e ≤ 3 / (B : ℝ)^6)
    (hfw : ∀ x, disk x (1/2) → ∀ j, ‖fw x j - forward (sourceUnit s t hs ht) x j‖ ≤ e)
    (hbw : ∀ x, disk x (1/2) → ∀ j, ‖bw x j - opposite (sourceUnit s t hs ht) x j‖ ≤ e)
    (hm : ∀ x y, ‖x‖ ≤ 1/2 → ‖y‖ ≤ 1/2 → ‖mul x y - x*y‖ ≤ e)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val + j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (decode B fw bw mul a b))) =
      radixValue B a * radixValue B b :=
  recovered_product B hB hbnd (sourceUnit s t hs ht) fw bw mul e he herr hfw hbw hm a b ha hb hspan

#print axioms prefix_inverse
#print axioms physical_character
#print axioms product_at_physical_coordinates
end MixedRankIntegrated

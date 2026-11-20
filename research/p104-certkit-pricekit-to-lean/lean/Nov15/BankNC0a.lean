/-
BankNC0a (lane LEAN-NC0, Nov 18).  See cards/WILD/LEANSWARM/NC0.md.
(a) Decomposition of a concave nondecreasing price g (g 0 = 0) on {0..H} into min(L,.) pieces:
    g d = Σ_{L=1..H} c_L · min(L,d),  c_L = g'(L-1) - g'(L) ≥ 0  (the L=H piece is the c_∞·d piece).
Kernel only: no sorry, no native_decide.
-/
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

namespace BankNC0
open Finset

/-- slope sequence, extended by 0 at and beyond H -/
def slope (H : ℕ) (g : ℕ → ℝ) (j : ℕ) : ℝ := if j < H then g (j+1) - g j else 0

theorem slope_succ_le (H : ℕ) (g : ℕ → ℝ) (hmono : ∀ j, j < H → g j ≤ g (j+1))
    (hconc : ∀ j, j + 1 < H → g (j+2) - g (j+1) ≤ g (j+1) - g j) (j : ℕ) :
    slope H g (j+1) ≤ slope H g j := by
  unfold slope
  by_cases h1 : j + 1 < H
  · have h0 : j < H := by omega
    simp only [h1, h0, if_true]
    have := hconc j h1
    linarith
  · by_cases h0 : j < H
    · simp only [h1, h0, if_true, if_false]
      have := hmono j h0
      linarith
    · simp [h1, h0]

theorem slope_nonneg (H : ℕ) (g : ℕ → ℝ) (hmono : ∀ j, j < H → g j ≤ g (j+1)) (j : ℕ) :
    0 ≤ slope H g j := by
  unfold slope
  by_cases h : j < H
  · simp only [h, if_true]; have := hmono j h; linarith
  · simp [h]

theorem telescope (t : ℕ → ℝ) (j : ℕ) : ∀ n, j ≤ n →
    ∑ L ∈ Ioc j n, (t (L-1) - t L) = t j - t n := by
  intro n
  induction n with
  | zero => intro h; have : j = 0 := by omega
            subst this; simp
  | succ n ih =>
    intro h
    rcases Nat.eq_or_lt_of_le h with h' | h'
    · subst h'; simp
    · rw [Finset.sum_Ioc_succ_top (by omega), ih (by omega)]
      simp

theorem g_eq_sum_slope (H : ℕ) (g : ℕ → ℝ) (g0 : g 0 = 0) :
    ∀ d, d ≤ H → g d = ∑ j ∈ range d, slope H g j := by
  intro d
  induction d with
  | zero => intro _; simp [g0]
  | succ d ih =>
    intro h
    rw [Finset.sum_range_succ, ← ih (by omega)]
    unfold slope
    simp only [show d < H by omega, if_true]; ring

theorem card_lt_filter (L d : ℕ) : ∑ j ∈ range d, (if j < L then (1:ℝ) else 0) = (min L d : ℕ) := by
  induction d with
  | zero => simp
  | succ d ih =>
    rw [Finset.sum_range_succ, ih]
    by_cases h : d < L
    · have : min L (d+1) = d + 1 := by omega
      have h2 : min L d = d := by omega
      rw [this]; simp [h, h2]
    · have : min L (d+1) = L := by omega
      have h2 : min L d = L := by omega
      rw [this]; simp [h, h2]

/-- (a) decomposition. -/
theorem decomp (H : ℕ) (g : ℕ → ℝ) (g0 : g 0 = 0)
    (hmono : ∀ j, j < H → g j ≤ g (j+1))
    (hconc : ∀ j, j + 1 < H → g (j+2) - g (j+1) ≤ g (j+1) - g j) :
    ∃ c : ℕ → ℝ, (∀ L, 0 ≤ c L) ∧
      ∀ d, d ≤ H → g d = ∑ L ∈ Icc 1 H, c L * (min L d : ℕ) := by
  set t := slope H g with ht
  have tanti : Antitone t := antitone_nat_of_succ_le (slope_succ_le H g hmono hconc)
  have tH : t H = 0 := by simp [ht, slope]
  refine ⟨fun L => t (L-1) - t L, fun L => ?_, ?_⟩
  · have := tanti (show L - 1 ≤ L by omega); linarith
  · intro d hd
    rw [g_eq_sum_slope H g g0 d hd]
    simp_rw [← card_lt_filter, Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro j hj
    have hjH : j < H := lt_of_lt_of_le (Finset.mem_range.mp hj) hd
    have : ∑ L ∈ Icc 1 H, (t (L-1) - t L) * (if j < L then (1:ℝ) else 0)
        = ∑ L ∈ Ioc j H, (t (L-1) - t L) := by
      rw [← Finset.sum_filter_add_sum_filter_not (Icc 1 H) (fun L => j < L)]
      have e : (Icc 1 H).filter (fun L => j < L) = Ioc j H := by
        ext L; simp [Finset.mem_Icc, Finset.mem_Ioc]; omega
      rw [e]
      have : ∑ L ∈ (Icc 1 H).filter (fun L => ¬ j < L), (t (L-1) - t L) * (if j < L then (1:ℝ) else 0) = 0 :=
        Finset.sum_eq_zero (fun L hL => by simp at hL; simp [hL.2])
      rw [this, add_zero]
      exact Finset.sum_congr rfl (fun L hL => by simp at hL; simp [hL.1])
    rw [this, telescope t j H hjH.le, tH]; ring

end BankNC0

import RoundedRecurrence

/-!
Source-only existential threshold and budget bridge. UNCOMPILED.

This reuses the preserved RoundedRecurrence induction. Strict characteristic
slack and a strictly positive power permit a sufficiently large natural
threshold. For a real-valued sequence, finitely many initial values then admit
one finite coefficient paying both the base cases and fixed overhead.

For a physical normalized-cost envelope, real-valued notation alone does NOT
prove boundedness of the underlying state family. The independently reviewed
NormalizedCostEnvelopeDescent must first receive its full-family base bounds,
positive volumes, exact child closure/volume ratios and complete uniform
physical decomposition. This file supplies none of those implementation facts.
It does not infer a recurrence for an arbitrary majorant or assume an attained
supremum. Its recurrence input can be the one actually derived by that chain.

Current intended context: PR1094, source applicability preserved at
main d78fe4bbb6f6b769e39586f8bb3ba8c31a31fd3a, selected outer
kappa = 836330098538459/500000000000000000. The exponent here is
1-a (intended a=bCurrent), distinct from outer kappa. No working precision,
selected physical base program or full multiplication theorem is supplied.

Attribution: the preserved ranked-pair RoundedRecurrence formalization,
Mathlib real powers/Archimedean order/finite sums, and the reviewed PR1379
normalization and normalized-envelope source chain. Apache-2.0.
Prepared with OpenAI assistance. No compiler or supplier execution.
-/

set_option Elab.async false

namespace RoundedRecurrenceExistentialBudget
open scoped BigOperators

/-- One natural threshold lies above a prior recurrence threshold, makes all
finite child ratios strictly descend, and leaves positive rounding slack.
The strict positivity of p is essential to this construction. -/
theorem exists_threshold {ι : Type} (s : Finset ι) (r : ι → ℝ)
    (p δ M : ℝ) (N₀ : ℕ) (hp : 0 < p) (hδ : 0 < δ)
    (hr : ∀ i ∈ s, r i < 1) :
    ∃ N : ℕ, N₀ ≤ N ∧ 0 < N ∧
      (∀ i ∈ s, r i * N + 1 < N) ∧ M < δ * (N : ℝ) ^ p := by
  classical
  let K : ℝ := ∑ i ∈ s, 1 / (1 - r i)
  let Y : ℝ := max 1 ((M + 1) / δ)
  let R : ℝ := Y ^ (1 / p)
  have hY : 0 ≤ Y := le_trans (by norm_num) (le_max_left _ _)
  have hR : 0 ≤ R := Real.rpow_nonneg hY _
  obtain ⟨N, hN⟩ := exists_nat_gt (max (max 1 (N₀ : ℝ)) (max K R))
  have hN₀ : (N₀ : ℝ) < N :=
    lt_of_le_of_lt ((le_max_right _ _).trans (le_max_left _ _)) hN
  have hN1 : (1 : ℝ) < N :=
    lt_of_le_of_lt ((le_max_left _ _).trans (le_max_left _ _)) hN
  have hNK : K < N :=
    lt_of_le_of_lt ((le_max_left _ _).trans (le_max_right _ _)) hN
  have hNR : R < N :=
    lt_of_le_of_lt ((le_max_right _ _).trans (le_max_right _ _)) hN
  have hNpos : 0 < N := by exact_mod_cast (lt_trans zero_lt_one hN1)
  refine ⟨N, (by exact_mod_cast hN₀.le), hNpos, ?_, ?_⟩
  · intro i hi
    have hiK : 1 / (1 - r i) ≤ K :=
      Finset.single_le_sum
        (fun j hj => (div_pos zero_lt_one (sub_pos.mpr (hr j hj))).le) hi
    have hdrop : 1 < (N : ℝ) * (1 - r i) :=
      (div_lt_iff₀ (sub_pos.mpr (hr i hi))).mp (hiK.trans_lt hNK)
    nlinarith
  · have hpow : Y < (N : ℝ) ^ p := by
      have H := Real.rpow_lt_rpow hR hNR hp
      have hRp : R ^ p = Y := by
        dsimp [R]
        rw [← Real.rpow_mul hY, one_div_mul_cancel hp.ne', Real.rpow_one]
      rwa [hRp] at H
    have hdiv : (M + 1) / δ < (N : ℝ) ^ p :=
      lt_of_le_of_lt (le_max_right _ _) hpow
    have H := (div_lt_iff₀ hδ).mp hdiv
    nlinarith

/-- All finitely many real base values and fixed overhead admit a common
finite A once the threshold has positive slack. No bound on an infinite
physical state family is manufactured here: f must already be the relevant
well-defined real sequence, with any envelope interpretation proved first. -/
theorem exists_base_budget (f : ℕ → ℝ) (p C δ M : ℝ) (N : ℕ)
    (hgap : 0 < δ * (N : ℝ) ^ p - M) :
    ∃ A : ℝ, 0 ≤ A ∧
      (∀ n, 0 < n → n ≤ N → f n ≤ A * (n : ℝ) ^ p) ∧
      C + A * M ≤ A * δ * (N : ℝ) ^ p := by
  classical
  let S : ℝ := ∑ n ∈ Finset.range (N + 1), max 0 (f n / (n : ℝ) ^ p)
  let D : ℝ := δ * (N : ℝ) ^ p - M
  let A : ℝ := max 0 (C / D) + S
  have hS : 0 ≤ S := Finset.sum_nonneg (fun _ _ => le_max_left _ _)
  have hA : 0 ≤ A := add_nonneg (le_max_left _ _) hS
  have hCD : C / D ≤ A := (le_max_right _ _).trans (le_add_of_nonneg_right hS)
  have hC : C ≤ A * D := (div_le_iff₀ hgap).mp hCD
  refine ⟨A, hA, ?_, ?_⟩
  · intro n hn hnN
    have hmem : n ∈ Finset.range (N + 1) :=
      Finset.mem_range.mpr (Nat.lt_succ_iff.mpr hnN)
    have hnS : max 0 (f n / (n : ℝ) ^ p) ≤ S :=
      Finset.single_le_sum (f := fun j : ℕ => max 0 (f j / (j : ℝ) ^ p))
        (fun _ _ => le_max_left _ _) hmem
    have hratio : f n / (n : ℝ) ^ p ≤ A :=
      (le_max_right _ _).trans
        (hnS.trans (le_add_of_nonneg_left (le_max_left _ _)))
    exact (div_le_iff₀ (Real.rpow_pos_of_pos (by exact_mod_cast hn) p)).mp hratio
  · dsimp [D] at hC
    nlinarith

/-- The existing network all-width theorem needs no separately guessed A or
budget once a<1, its characteristic is strictly below one, and the actual
real sequence obeys the supplied recurrence above some N₀. The finitely many
base values are bounded by construction. No new induction is introduced. -/
theorem exists_network_power_majorant {ι : Type} (s : Finset ι)
    (multiplicity width : ι → ℝ) (m W a C : ℝ) (N₀ : ℕ) (f : ℕ → ℝ)
    (hm : 0 < m) (hW : 0 < W) (ha : 0 ≤ a) (ha1 : a < 1)
    (hc : ∀ i ∈ s, 0 ≤ multiplicity i)
    (ht : ∀ i ∈ s, 0 < width i) (htm : ∀ i ∈ s, width i < m)
    (hcharacteristic : RoundedRecurrence.expCharacteristic s multiplicity width m W a < 1)
    (actual_recurrence : ∀ n, N₀ < n → f n ≤ C +
      ∑ i ∈ s, (multiplicity i / W) * f ⌈(width i / m) * n⌉₊) :
    ∃ A : ℝ, 0 ≤ A ∧ ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ (1 - a) := by
  let δ : ℝ := 1 - RoundedRecurrence.expCharacteristic s multiplicity width m W a
  let M : ℝ := ∑ i ∈ s, multiplicity i / W
  have hp : 0 < 1 - a := sub_pos.mpr ha1
  have hδ : 0 < δ := sub_pos.mpr hcharacteristic
  obtain ⟨N, hN₀, _hNpos, hthreshold, hslack⟩ :=
    exists_threshold s (fun i => width i / m) (1 - a) δ M N₀ hp hδ
      (fun i hi => (div_lt_one hm).mpr (htm i hi))
  obtain ⟨A, hA, hbase, hbudget⟩ :=
    exists_base_budget f (1 - a) C δ M N (sub_pos.mpr hslack)
  refine ⟨A, hA, ?_⟩
  apply RoundedRecurrence.network_all_width_bound s multiplicity width m W a A C N f
    hm hW ha ha1.le hA hc ht htm hcharacteristic hthreshold hbudget hbase
  intro n hn
  exact actual_recurrence n (lt_of_le_of_lt hN₀ hn)

end RoundedRecurrenceExistentialBudget

#print axioms RoundedRecurrenceExistentialBudget.exists_threshold
#print axioms RoundedRecurrenceExistentialBudget.exists_base_budget
#print axioms RoundedRecurrenceExistentialBudget.exists_network_power_majorant

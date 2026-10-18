import StoppedRecurrence

/-!
Literal PR2234/selected-PR589 instantiation. The fractional moment inequality
is retained as an explicit formal hypothesis; the recurrence theorem does not
establish the full-machine local charge or completed-child contract.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
-/

open scoped BigOperators
open StoppedRecurrence

namespace SelectedStoppedRecurrence

def ranks : Fin 8 → ℕ := ![1, 2, 3, 4, 5, 6, 7, 42]
def counts : Fin 8 → ℕ := ![381024, 400416, 22752, 26880, 29376, 17376, 26784, 288]
noncomputable def weight (r : Fin 8) : ℝ := counts r / 28416
noncomputable def bad : ℝ := 118606528512 / (10000000000000000 * 28416)
noncomputable def exponent : ℝ := 9983 / 10000

noncomputable def fractionalMoment : ℝ :=
  (∑ r, weight r * ((ranks r : ℝ) / 64) ^ exponent) + bad * (1 / 64) ^ exponent

theorem proper_ranks : ∀ r, 0 < ranks r ∧ ranks r < 64 := by
  intro r
  fin_cases r <;> norm_num [ranks]

theorem exact_linear_moment :
    (∑ r, weight r * ((ranks r : ℝ) / 64)) + bad * (1 / 64) =
      2874298095721977 / 2890625000000000 := by
  norm_num [Fin.sum_univ_succ, weight, counts, ranks, bad]

theorem linear_margin :
    (∑ r, weight r * ((ranks r : ℝ) / 64)) + bad * (1 / 64) ≤ 199 / 200 := by
  rw [exact_linear_moment]
  norm_num

theorem selected_bound (limit : ℕ) (C w : ℝ) (hC : 0 ≤ C) (hw : 0 ≤ w)
    (fractional_margin : fractionalMoment ≤ 9999 / 10000)
    (T : ℕ → ℝ) (zero : T 0 ≤ 0)
    (leaf : ∀ n, n ≤ limit → 0 < n → n < 64 → T n ≤ C * w)
    (step : ∀ n, n ≤ limit → 64 ≤ n → T n ≤
      (∑ r, weight r * T (ranks r * (n / 64))) + bad * worst T (n / 64) + C * (n + w)) :
    ∀ n, n ≤ limit → T n ≤ 200 * C * n + 10000 * C * (n : ℝ) ^ (9983 / 10000 : ℝ) * w := by
  exact stopped_bound limit 64 (by decide) ranks proper_ranks weight
    (fun r => by unfold weight; positivity) bad C w exponent
    (by norm_num [bad]) hC hw (by norm_num [exponent]) linear_margin
    fractional_margin T zero leaf step

noncomputable def positiveWorst (T : ℕ → ℝ) (f : ℕ) (hf : 1 ≤ f) : ℝ :=
  (Finset.Icc 1 f).sup' (by exact ⟨1, by simp [hf]⟩) T

/-- A bookkeeping extension, not a constraint on the source's width-zero cost. -/
noncomputable def zeroed (T : ℕ → ℝ) (n : ℕ) : ℝ := if n = 0 then 0 else T n

theorem worst_zeroed (T : ℕ → ℝ) (f : ℕ) (hf : 1 ≤ f) (h1 : 0 ≤ T 1) :
    worst (zeroed T) f = positiveWorst T f hf := by
  rw [worst_eq_positive (zeroed T) f hf (by simpa [zeroed] using h1)]
  apply Finset.sup'_congr (by exact ⟨1, by simp [hf]⟩) rfl
  intro j hj
  have hj0 : j ≠ 0 := by have := (Finset.mem_Icc.mp hj).1; omega
  simp [zeroed, hj0]

/-- The source's literal positive-width fallback maximum, not a hidden
monotonicity assumption on `T`. Only its proved majorant is monotone.
Width zero is outside the conclusion, as in PR2234, and `T 0` is unrestricted. -/
theorem selected_positive_bound (limit : ℕ) (C w : ℝ) (hC : 0 ≤ C) (hw : 0 ≤ w)
    (fractional_margin : fractionalMoment ≤ 9999 / 10000)
    (T : ℕ → ℝ) (one_nonnegative : 0 ≤ T 1)
    (leaf : ∀ n, n ≤ limit → 0 < n → n < 64 → T n ≤ C * w)
    (step : ∀ n, n ≤ limit → ∀ (hn : 64 ≤ n), T n ≤
      (∑ r, weight r * T (ranks r * (n / 64))) +
      bad * positiveWorst T (n / 64) (by omega) + C * (n + w)) :
    ∀ n, n ≤ limit → 0 < n → T n ≤ 200 * C * n + 10000 * C * (n : ℝ) ^ (9983 / 10000 : ℝ) * w := by
  have leaves : ∀ n, n ≤ limit → 0 < n → n < 64 → zeroed T n ≤ C * w := by
    intro n hnlimit hn hsmall
    simpa only [zeroed, if_neg (Nat.ne_of_gt hn)] using leaf n hnlimit hn hsmall
  have steps : ∀ n, n ≤ limit → 64 ≤ n → zeroed T n ≤
      (∑ r, weight r * zeroed T (ranks r * (n / 64))) +
      bad * worst (zeroed T) (n / 64) + C * (n + w) := by
    intro n hnlimit hn
    have hn0 : n ≠ 0 := by omega
    have child_pos : ∀ r, ranks r * (n / 64) ≠ 0 := by
      intro r
      exact Nat.ne_of_gt (Nat.mul_pos (proper_ranks r).1 (by omega))
    rw [worst_zeroed T (n / 64) (by omega) one_nonnegative]
    simpa only [zeroed, hn0, child_pos, if_false] using step n hnlimit hn
  have bound := selected_bound limit C w hC hw fractional_margin (zeroed T)
    (by simp [zeroed]) leaves steps
  intro n hnlimit hn
  simpa only [zeroed, if_neg (Nat.ne_of_gt hn)] using bound n hnlimit

/-- A single local-charge constant serves the whole root-indexed family.
The allowed root width/atom-width pairs may be coupled; no recurrence is
required outside each root's descendant-width domain. -/
theorem selected_uniform_bound {Root : Type*} (limit : Root → ℕ) (w : Root → ℝ)
    (C : ℝ) (hC : 0 ≤ C) (hw : ∀ root, 0 ≤ w root)
    (fractional_margin : fractionalMoment ≤ 9999 / 10000)
    (T : Root → ℕ → ℝ) (one_nonnegative : ∀ root, 0 ≤ T root 1)
    (leaf : ∀ root n, n ≤ limit root → 0 < n → n < 64 → T root n ≤ C * w root)
    (step : ∀ root n, n ≤ limit root → ∀ (hn : 64 ≤ n), T root n ≤
      (∑ r, weight r * T root (ranks r * (n / 64))) +
      bad * positiveWorst (T root) (n / 64) (by omega) + C * (n + w root)) :
    ∀ root n, n ≤ limit root → 0 < n →
      T root n ≤ 200 * C * n + 10000 * C * (n : ℝ) ^ (9983 / 10000 : ℝ) * w root := by
  intro root
  exact selected_positive_bound (limit root) C (w root) hC (hw root) fractional_margin
    (T root) (one_nonnegative root) (leaf root) (step root)

end SelectedStoppedRecurrence

#print axioms SelectedStoppedRecurrence.exact_linear_moment
#print axioms SelectedStoppedRecurrence.selected_bound
#print axioms SelectedStoppedRecurrence.selected_positive_bound
#print axioms SelectedStoppedRecurrence.selected_uniform_bound

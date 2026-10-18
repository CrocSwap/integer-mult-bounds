import SelectedMoment

/-!
Compose the newly proved numerical bound with PR2289's unchanged recurrence.
The physical hypotheses remain visible; no full-machine admission is inferred.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
-/

open scoped BigOperators
open SelectedStoppedRecurrence SelectedBitMoment

namespace ClosedBitRecurrence

/-- The root-family conclusion has no numerical moment hypothesis. -/
theorem uniform_bound {Root : Type*} (limit : Root → ℕ) (w : Root → ℝ)
    (C : ℝ) (hC : 0 ≤ C) (hw : ∀ root, 0 ≤ w root)
    (T : Root → ℕ → ℝ) (one_nonnegative : ∀ root, 0 ≤ T root 1)
    (leaf : ∀ root n, n ≤ limit root → 0 < n → n < 64 → T root n ≤ C * w root)
    (step : ∀ root n, n ≤ limit root → ∀ (hn : 64 ≤ n), T root n ≤
      (∑ r, weight r * T root (ranks r * (n / 64))) +
      bad * positiveWorst (T root) (n / 64) (by omega) + C * (n + w root)) :
    ∀ root n, n ≤ limit root → 0 < n →
      T root n ≤ 200 * C * n + 10000 * C * (n : ℝ) ^ (9983 / 10000 : ℝ) * w root :=
  selected_uniform_bound limit w C hC hw fractional_moment_strict.le T one_nonnegative leaf step

end ClosedBitRecurrence

#print axioms ClosedBitRecurrence.uniform_bound

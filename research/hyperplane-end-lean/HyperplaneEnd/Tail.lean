/-
Hyperplane-ended helpers, the word: the `cleanup_tail` segment and the helper's terminal label.

In the HPE word, helper `h` and its partner `p` climb to the join `U` of their frames, the single
cleanup gate `h -= p` runs there (both operands at `U`: clause G0), the remaining cleanup never
moves `h`, and the post wrapper takes `h` from `U` to `(done, h)`.

* `tail_labels`        the tail is well labelled and ends with `h` and `p` both at `U`;
* `hpe_labels`         the whole word `a ++ tail ++ b ++ [post wrapper]` is well labelled and the
                       helper's terminal extended label is `(done, h)`;
* `residual_block`     the unwrapped helper block of a unit row is `T_U T_E⁻¹` (Lemma G, (C)).
Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
-/
import HyperplaneEnd.Labels
import LemmaG.Stream

namespace HyperplaneEnd

open LemmaG LemmaG.Stream

variable {ι Fr K : Type*} [DecidableEq ι]

/-- The `cleanup_tail` segment of one HPE helper `h` with partner `p`: both climb to `U`, then
the gate `h += q • p` (in the word `q = -1`) runs at `U`. -/
def tail (h p : ι) (Ah Ap U : Fr) (q : K) : List (Event ι (XLab ι Fr) K) :=
  [.relabel h (.frame Ah) (.frame U), .relabel p (.frame Ap) (.frame U), .add h p q]

/-- The tail is well labelled (the gate runs with both operands at `U`) and leaves both
registers at `U`; every other register keeps its label. -/
theorem tail_labels (h p : ι) (hp : h ≠ p) (Ah Ap U : Fr) (q : K) (l : ι → XLab ι Fr)
    (lh : l h = .frame Ah) (lp : l p = .frame Ap) :
    WellLabelled (tail h p Ah Ap U q) l ∧
      labRun (tail h p Ah Ap U q) l =
        Function.update (Function.update l h (.frame U)) p (.frame U) := by
  refine ⟨?_, rfl⟩
  simp [tail, WellLabelled, Event.Admissible, Event.lab, Function.update_apply, lh, lp, hp,
    Ne.symm hp]

/-- **The terminal label of an HPE helper.**  Let the word be `a ++ tail ++ b ++ [post]`, where
`a` brings `h` and `p` to `A_h` and `A_p`, `b` (the remaining FULL cleanup) never relabels `h`,
and `post` is the post wrapper `relabel h U (done h)`.  If `a` and `b` are well labelled, the whole
word is well labelled and `h` ends at `(done, h)`: the post wrapper is admissible because `h`
is still at `U`. -/
theorem hpe_labels (h p : ι) (hp : h ≠ p) (Ah Ap U : Fr) (q : K) (l : ι → XLab ι Fr)
    (a b : List (Event ι (XLab ι Fr) K))
    (ha : WellLabelled a l) (lh : labRun a l h = .frame Ah) (lp : labRun a l p = .frame Ap)
    (hb : WellLabelled b (labRun (a ++ tail h p Ah Ap U q) l))
    (hmv : ∀ e ∈ b, ¬ e.moves h) :
    WellLabelled (a ++ tail h p Ah Ap U q ++ b ++ [.relabel h (.frame U) (.done h)]) l ∧
      labRun (a ++ tail h p Ah Ap U q ++ b ++ [.relabel h (.frame U) (.done h)]) l h = .done h := by
  obtain ⟨ht, hlt⟩ := tail_labels h p hp Ah Ap U q (labRun a l) lh lp
  have hU : labRun (a ++ tail h p Ah Ap U q ++ b) l h = .frame U := by
    rw [labRun_append, labRun_untouched b _ h hmv, labRun_append, hlt]
    simp [Function.update_apply, hp]
  have hat : WellLabelled (a ++ tail h p Ah Ap U q) l := (wellLabelled_append _ _ _).2 ⟨ha, ht⟩
  have hatb : WellLabelled (a ++ tail h p Ah Ap U q ++ b) l :=
    (wellLabelled_append _ _ _).2 ⟨hat, hb⟩
  refine ⟨(wellLabelled_append _ _ _).2 ⟨hatb, ?_⟩, ?_⟩
  · simp only [WellLabelled, Event.Admissible, and_true]
    exact hU
  · rw [labRun_append]
    simp [labRun, Event.lab]

variable [Semiring K] {M : Type*} [AddCommMonoid M] [Module K M] [Fintype ι]

/-- **(C) for a hyperplane end.**  In frame labels (no wrappers), a helper with a unit row whose
label runs from `E` to `U` ends as `T_U T_E⁻¹` of its own input, for any frame `U`. -/
theorem residual_block (T : Fr → M ≃ₗ[K] M) (rec : Fr → Fr → M → M) (es : List (Event ι Fr K))
    (l : ι → Fr) (x : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (j : ι)
    (hS : ∀ s, S es j s = if s = j then 1 else 0) (E U : Fr) (hE : l j = E)
    (hU : labRun es l j = U) :
    physRun rec es x j = T U ((T E).symm (x j)) := by
  rw [row_unit T rec es l x hrec hw j hS, hE, hU]

end HyperplaneEnd

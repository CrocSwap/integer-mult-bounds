import PR516Realize
import SequentialCompleteBank

/-!
Full-state supplier adapter for the local endpoint premise of
CurrentMain.SequentialCompleteBank.completed_words_separate and
CurrentMain.SequentialCompleteBank.sequential_complete_bank.

Reuse: PR516 at 1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814, LemmaA.Realize,
by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code;
Apache-2.0, with its full NOTICE retained beside the source audit. The two
upstream endpoint results are applied directly. No realization or sequential
composition induction is repeated here. Existing Mathlib Equiv.funSplitAt
provides the exact complete-state split.

The selected source must still supply full register-owner injectivity, its
actual complete physical word/execution equality, exact recipes and labels,
the entire scalar unit row and zero off-diagonal helper column, and the
helper operator identification. For sequential_complete_bank, bankStep is
its conjugated partial swap; common chart, all-replica partition, source order,
global boundaries and physical costs remain separate caller obligations.
-/
namespace CurrentMain.PR516CompleteBankEndpoint

open LemmaG LemmaG.Stream
open CurrentMain.FrameTransport

variable {ι Φ Λ K W M : Type*}
variable [DecidableEq ι] [DecidableEq Φ] [Fintype ι] [Semiring K]
variable [AddCommMonoid W] [Module K W] [AddCommMonoid M] [Module K M]

/-- All other physical families, with no cleanliness or independence restriction. -/
abbrev Rest (f : Φ) (W : Type*) := {g : Φ // g ≠ f} → W

/-- The actual rest evolution, evaluated with a reference helper value of zero.
The theorem below proves that choosing this reference loses no dependence:
zero is not a premise on the real initial helper or on any rest family. -/
def restOutput (σ : LemmaA.Hosting ι Φ K W M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (f : Φ) (s : Rest f W) : Rest f W :=
  fun g => LemmaA.realizeRun σ rec es ((Equiv.funSplitAt f W).symm (0, s)) g

/-- Supply the exact universal separated endpoint expected by the accepted
sequential interface. The physical-word equality binds executions, rather
than assuming the desired separated bank/rest endpoint.

The bank operator is derived from the unit row; rest independence is derived
separately from the zero column. Both hold for every complete initial state. -/
theorem full_state_endpoint
    (T : Λ → M ≃ₗ[K] M) (σ : LemmaA.Hosting ι Φ K W M)
    (hinj : Function.Injective σ.own) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (l : ι → Λ)
    (hrec : RecipesExact T rec es) (hw : WellLabelled es l)
    (j : ι) (f : Φ) (howner : σ.own j = f)
    (hrow : ∀ k, S es j k = if k = j then 1 else 0)
    (hcol : ∀ r, r ≠ j → S es r j = 0)
    (bankStep : W → W)
    (hoperator : ∀ b,
      (σ.chart j).symm (T (labRun es l j) ((T (l j)).symm (σ.chart j b))) =
        bankStep b)
    (word : List ((W × Rest f W) → (W × Rest f W)))
    (hphysical : ∀ z,
      run word z = Equiv.funSplitAt f W
        (LemmaA.realizeRun σ rec es ((Equiv.funSplitAt f W).symm z))) :
    ∀ b s, run word (b, s) = (bankStep b, restOutput σ rec es f s) := by
  intro b s
  let split := Equiv.funSplitAt f W
  let y := split.symm (b, s)
  let y0 := split.symm (0, s)
  have hy : y f = b := congrArg Prod.fst (split.apply_symm_apply (b, s))
  have hy_rest : (fun g : {g : Φ // g ≠ f} => y g) = s :=
    congrArg Prod.snd (split.apply_symm_apply (b, s))
  have hzero_rest : (fun g : {g : Φ // g ≠ f} => y0 g) = s :=
    congrArg Prod.snd (split.apply_symm_apply (0, s))
  have hupdate : Function.update y0 f b = y := by
    apply split.injective
    apply Prod.ext
    · change Function.update y0 f b f = y f
      rw [Function.update_self, hy]
    · change (fun g : {g : Φ // g ≠ f} => Function.update y0 f b g) =
        (fun g : {g : Φ // g ≠ f} => y g)
      funext g
      rw [Function.update_of_ne g.property]
      exact (congrFun hzero_rest g).trans (congrFun hy_rest g).symm
  rw [hphysical]
  apply Prod.ext
  · change LemmaA.realizeRun σ rec es y f = bankStep b
    have hbank := LemmaA.family_endpoint T σ hinj rec es l y hrec hw j hrow
    rw [howner, hy] at hbank
    exact hbank.trans (hoperator b)
  · change (fun g : {g : Φ // g ≠ f} => LemmaA.realizeRun σ rec es y g) =
      restOutput σ rec es f s
    funext g
    change LemmaA.realizeRun σ rec es y g = LemmaA.realizeRun σ rec es y0 g
    have hf : (g : Φ) ≠ σ.own j := by simpa only [howner] using g.property
    have hrest := LemmaA.endpoint_indep T σ hinj rec es l y0 hrec hw j hcol b g hf
    rw [howner, hupdate] at hrest
    exact hrest

end CurrentMain.PR516CompleteBankEndpoint

#print axioms LemmaA.family_endpoint
#print axioms LemmaA.endpoint_indep
#print axioms CurrentMain.PR516CompleteBankEndpoint.full_state_endpoint

/-
Lemma A, stream units: owners are physical streams (family, cover class), as in the cover model
of #442/#458.  An invocation at cover class `d` realizes register `r` on the stream
`(fam r, d · σ_r⁻¹)`, where `σ_r` is its route (slot permutation, host chart).  Several registers of
one invocation may share a family; they own distinct streams as soon as their routes differ, in
particular when their footprints on the family are disjoint.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
-/
import LemmaA.Tensor

namespace LemmaA

open TensorProduct LemmaG LemmaG.Stream

section Owner

variable {ι Fam G : Type*} [Group G]

/-- The stream that register `r` owns in the invocation at cover class `d`. -/
def streamOwner (fam : ι → Fam) (σ : ι → G) (d : G) (r : ι) : Fam × G := (fam r, d * (σ r)⁻¹)

/-- Distinct (family, route) pairs give distinct streams, at every cover class. -/
theorem streamOwner_injective (fam : ι → Fam) (σ : ι → G) (d : G)
    (h : Function.Injective fun r => (fam r, σ r)) : Function.Injective (streamOwner fam σ d) := by
  intro r r' hrr
  simp only [streamOwner, Prod.mk.injEq, mul_right_inj, inv_inj] at hrr
  exact h (Prod.ext hrr.1 hrr.2)

/-- **Disjoint footprints give one owner per stream.**  If registers on the same family have
pairwise disjoint, nonempty footprints (`fp σ` is the set of family coordinates that route `σ`
places the register on), the stream owner map is injective at every cover class. -/
theorem streamOwner_injective_of_disjoint {C : Type*} (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set C) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r'))) :
    Function.Injective (streamOwner fam σ d) := by
  refine streamOwner_injective fam σ d (fun r r' h => ?_)
  by_contra hne'
  simp only [Prod.mk.injEq] at h
  obtain ⟨x, hx⟩ := hne r
  have := hdis r r' hne' h.1
  rw [h.2] at this hx
  exact Set.disjoint_left.1 this hx hx

/-- **The cover sweep visits each stream once per route.**  For a fixed route `σ`, exactly one cover
class `d` realizes a register with route `σ` on the stream `(f, g)`, namely `d = g σ`. -/
theorem sweep_unique (σ g : G) : ∃! d : G, d * σ⁻¹ = g :=
  ⟨g * σ, by simp, fun d h => by rw [← h]; simp⟩

end Owner

section Lemma

variable {K : Type*} [CommSemiring K]
variable {A B : Type*} [AddCommMonoid A] [Module K A] [AddCommMonoid B] [Module K B]
variable {ι Λ Fam G C W : Type*} [DecidableEq ι] [Fintype ι] [DecidableEq Fam] [Group G] [DecidableEq G]
variable [AddCommMonoid W] [Module K W]

/-- **Lemma A on streams.**  Registers of one invocation may share a family if their footprints on
it are pairwise disjoint (#433 pure-bank slots, #442 hosted slots, #471/#500 footprints).  Realized
on the streams `(fam r, d · σ_r⁻¹)`, the complete invocation leaves the helper's stream holding
`chart⁻¹ (C ⊗ id) chart` of its own initial value: the spectators are untouched. -/
theorem lemmaA_streams (T : Λ → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set C) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[K] (A ⊗[K] B)) (rec : Λ → Λ → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι Λ K)) (l : ι → Λ) (y : Fam × G → W) (hrec : RecipesExact T rec es)
    (hw : WellLabelled es l) (j : ι) (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (Cj : A →ₗ[K] A) (hfac : ∀ v, T (labRun es l j) ((T (l j)).symm v) = Cj.rTensor B v) :
    realizeRun ⟨streamOwner fam σ d, chart⟩ rec es y (streamOwner fam σ d j) =
      (chart j).symm (Cj.rTensor B (chart j (y (streamOwner fam σ d j)))) :=
  lemmaA_family T ⟨streamOwner fam σ d, chart⟩
    (streamOwner_injective_of_disjoint fam σ d fp hne hdis) rec es l y hrec hw j hS Cj hfac

end Lemma

end LemmaA

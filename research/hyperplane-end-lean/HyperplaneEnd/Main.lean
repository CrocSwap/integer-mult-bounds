/-
Hyperplane-ended helpers, main theorems: Lemma A with an arbitrary terminal frame.

Lemma A (`../e8-lemma-a-lean`) is stated for any label family; its hypothesis (F) is
`T_{λ¹_j} T_{λ⁰_j}⁻¹ = C ⊗ id` on Lemma G's extended labels.  Instantiating the labels with
`Text` (terminal frame `U_j` arbitrary, wrappers keyed by `(E_j, U_j)`) and discharging (F) by
the exact factorization (N) `T_U T_E⁻¹ = L (C ⊗ id) R` gives:

* `hpe_block`     the helper's register ends as `(C ⊗ id) h_j` (local run);
* `hpe_family`    realized on families: the helper's family ends as `χ⁻¹ (C ⊗ id) χ` of itself;
* `hpe_streams`   the same on physical streams with disjoint footprints (Lemma A's main form);
* `hpe_word`      the same for the concrete HPE word `a ++ tail ++ b ++ [post]` (Tail.lean);
* `hyperplane_width`  on frames of `F₂⁹`: `E ≤ U`, `dim E = 1`, `dim U = 8` give width
                  `dim U - dim E = 7`, `9 - 7 = 2` spectators, and `U ≠ FULL`.
The FULL-ended helpers of #484 are the instance `term j = ⊤`.
Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
-/
import HyperplaneEnd.Tail
import LemmaA
import LemmaG.Frames

namespace HyperplaneEnd

open TensorProduct LemmaG LemmaG.Stream LemmaA

variable {K : Type*} [CommSemiring K]
variable {A B : Type*} [AddCommMonoid A] [Module K A] [AddCommMonoid B] [Module K B]
variable {ι Fr : Type*} [DecidableEq ι] [Fintype ι]

/-- **The HPE helper block.**  A well-labelled invocation with exact recipes in the extended
labels `Text`, a helper `j` with a unit row that starts at `(prew, j)` and ends at `(done, j)`, and
the exact factorization (N) for its pair `(E_j, U_j)`: register `j` ends as `(C ⊗ id) h_j`. -/
theorem hpe_block (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B))
    (rec : XLab ι Fr → XLab ι Fr → A ⊗[K] B → A ⊗[K] B) (es : List (Event ι (XLab ι Fr) K))
    (l : ι → XLab ι Fr) (h : ι → A ⊗[K] B) (hrec : RecipesExact (Text T ent term Lw Rw) rec es)
    (hw : WellLabelled es l) (j : ι) (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (hstart : l j = .prew j) (hend : labRun es l j = .done j) (C : A →ₗ[K] A)
    (hN : ∀ v, T (term j) ((T (ent j)).symm v) =
      Lw (ent j) (term j) (C.rTensor B (Rw (ent j) (term j) v))) :
    physRun rec es h j = C.rTensor B (h j) :=
  helper_block (Text T ent term Lw Rw) rec es l h hrec hw j hS C
    (fun v => by rw [hstart, hend]; exact factor_of_exact T ent term Lw Rw j C hN v)

/-- **Lemma A for a hyperplane-ended helper, on families.** -/
theorem hpe_family {Φ W : Type*} [DecidableEq Φ] [AddCommMonoid W] [Module K W]
    (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (σ : Hosting ι Φ K W (A ⊗[K] B))
    (hinj : Function.Injective σ.own) (rec : XLab ι Fr → XLab ι Fr → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι (XLab ι Fr) K)) (l : ι → XLab ι Fr) (y : Φ → W)
    (hrec : RecipesExact (Text T ent term Lw Rw) rec es) (hw : WellLabelled es l) (j : ι)
    (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (hstart : l j = .prew j) (hend : labRun es l j = .done j) (C : A →ₗ[K] A)
    (hN : ∀ v, T (term j) ((T (ent j)).symm v) =
      Lw (ent j) (term j) (C.rTensor B (Rw (ent j) (term j) v))) :
    realizeRun σ rec es y (σ.own j) = (σ.chart j).symm (C.rTensor B (σ.chart j (y (σ.own j)))) :=
  lemmaA_family (Text T ent term Lw Rw) σ hinj rec es l y hrec hw j hS C
    (fun v => by rw [hstart, hend]; exact factor_of_exact T ent term Lw Rw j C hN v)

/-- **Lemma A for a hyperplane-ended helper, on streams.**  Same hypotheses as
`LemmaA.lemmaA_streams`, with (F) replaced by the start/end tags and (N) for the pair
`(E_j, U_j)`.  The terminal frame `term j` is arbitrary; nothing requires it to be FULL. -/
theorem hpe_streams {Fam G Cc W : Type*} [DecidableEq Fam] [Group G] [DecidableEq G]
    [AddCommMonoid W] [Module K W]
    (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B))
    (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set Cc) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[K] (A ⊗[K] B)) (rec : XLab ι Fr → XLab ι Fr → A ⊗[K] B → A ⊗[K] B)
    (es : List (Event ι (XLab ι Fr) K)) (l : ι → XLab ι Fr) (y : Fam × G → W)
    (hrec : RecipesExact (Text T ent term Lw Rw) rec es) (hw : WellLabelled es l) (j : ι)
    (hS : ∀ s, S es j s = if s = j then 1 else 0)
    (hstart : l j = .prew j) (hend : labRun es l j = .done j) (C : A →ₗ[K] A)
    (hN : ∀ v, T (term j) ((T (ent j)).symm v) =
      Lw (ent j) (term j) (C.rTensor B (Rw (ent j) (term j) v))) :
    realizeRun ⟨streamOwner fam σ d, chart⟩ rec es y (streamOwner fam σ d j) =
      (chart j).symm (C.rTensor B (chart j (y (streamOwner fam σ d j)))) :=
  lemmaA_streams (Text T ent term Lw Rw) fam σ d fp hne hdis chart rec es l y hrec hw j hS C
    (fun v => by rw [hstart, hend]; exact factor_of_exact T ent term Lw Rw j C hN v)

/-- **The HPE word.**  For the word `a ++ tail ++ b ++ [post]` of `hpe_labels` (the helper `h`
starts at `(prew, h)`, its single cleanup gate runs at `U = term h` in `cleanup_tail`, the
remaining cleanup `b` never relabels it, the post wrapper names `U`), with exact recipes, a unit
row and (N) for `(ent h, term h)`, the helper's stream ends as `χ⁻¹ (C ⊗ id) χ` of itself. -/
theorem hpe_word {Fam G Cc W : Type*} [DecidableEq Fam] [Group G] [DecidableEq G]
    [AddCommMonoid W] [Module K W]
    (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B))
    (fam : ι → Fam) (σ : ι → G) (d : G)
    (fp : G → Set Cc) (hne : ∀ r, (fp (σ r)).Nonempty)
    (hdis : ∀ r r', r ≠ r' → fam r = fam r' → Disjoint (fp (σ r)) (fp (σ r')))
    (chart : ι → W ≃ₗ[K] (A ⊗[K] B)) (rec : XLab ι Fr → XLab ι Fr → A ⊗[K] B → A ⊗[K] B)
    (h p : ι) (hp : h ≠ p) (Ah Ap : Fr) (q : K) (l : ι → XLab ι Fr)
    (a b : List (Event ι (XLab ι Fr) K)) (y : Fam × G → W)
    (ha : WellLabelled a l) (lh : labRun a l h = .frame Ah) (lp : labRun a l p = .frame Ap)
    (hb : WellLabelled b (labRun (a ++ tail h p Ah Ap (term h) q) l))
    (hmv : ∀ e ∈ b, ¬ e.moves h)
    (hrec : RecipesExact (Text T ent term Lw Rw) rec
      (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)]))
    (hS : ∀ s, S (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)])
      h s = if s = h then 1 else 0)
    (hstart : l h = .prew h) (C : A →ₗ[K] A)
    (hN : ∀ v, T (term h) ((T (ent h)).symm v) =
      Lw (ent h) (term h) (C.rTensor B (Rw (ent h) (term h) v))) :
    realizeRun ⟨streamOwner fam σ d, chart⟩ rec
        (a ++ tail h p Ah Ap (term h) q ++ b ++ [.relabel h (.frame (term h)) (.done h)]) y
        (streamOwner fam σ d h) =
      (chart h).symm (C.rTensor B (chart h (y (streamOwner fam σ d h)))) :=
  let hl := hpe_labels h p hp Ah Ap (term h) q l a b ha lh lp hb hmv
  hpe_streams T ent term Lw Rw fam σ d fp hne hdis chart rec _ l y hrec hl.1 h hS hstart hl.2 C hN

/-- **Width and spectators of a hyperplane end** (frames of `F₂⁹`).  For an entrance `E` of
dimension 1 inside a hyperplane `U` (dimension 8), the residual width is `dim U - dim E = 7`,
the hosted chart has `9 - 7 = 2` spectators, and `U` is not the full frame. -/
theorem hyperplane_width (E U : Frame) (hEU : E ≤ U) (hE : frameRank E = 1) (hU : frameRank U = 8) :
    frameRank U - frameRank E = 7 ∧ 9 - (frameRank U - frameRank E) = 2 ∧ U ≠ ⊤ ∧
      frameRank E ≤ frameRank U := by
  refine ⟨by omega, by omega, ?_, frameRank_strictMono.monotone hEU⟩
  rintro rfl
  have : frameRank (⊤ : Frame) = 9 := by
    simp [frameRank, finrank_top, Module.finrank_fin_fun]
  omega

end HyperplaneEnd

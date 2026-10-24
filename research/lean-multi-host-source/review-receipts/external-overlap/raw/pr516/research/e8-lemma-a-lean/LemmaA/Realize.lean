/-
Lemma A, realization: a local invocation executed on physical families through charts.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Each register `i` of an invocation is hosted on the physical family `own i` through a linear
chart `chart i : W ≃ₗ[K] M` (route and batch).  Executing an event physically reads the
operands through their charts and writes the destination's family back.

* `realize_run`        one owner (injective `own`) ⇒ the physical run, read through the charts,
                       is the local run; families that host no register are untouched.
* `one_owner_needed`   two registers on one family: already a one-event stream breaks it.
* `family_endpoint`    with Lemma G's unit row, the helper's family ends as
                       `chart⁻¹ ∘ T_{λ¹} T_{λ⁰}⁻¹ ∘ chart` of its own initial value.
* `endpoint_indep`     with a zero column, no other family reads the helper's family.
-/
import LemmaG.Stream

namespace LemmaA

open LemmaG LemmaG.Stream

variable {ι Φ Λ K : Type*} [DecidableEq ι] [DecidableEq Φ] [Semiring K]
variable {W M : Type*} [AddCommMonoid W] [Module K W] [AddCommMonoid M] [Module K M]

/-- The register an event writes. -/
def dst : Event ι Λ K → ι
  | .relabel r _ _ => r
  | .add t _ _ => t
  | .scale t _ => t
  | .copy c _ _ => c
  | .clear c _ => c

omit [DecidableEq Φ] in
theorem phys_ne (rec : Λ → Λ → M → M) (e : Event ι Λ K) (h : ι → M) (i : ι) (hi : i ≠ dst e) :
    e.phys rec h i = h i := by
  cases e <;> simp [Event.phys, dst, Function.update_of_ne hi] at hi ⊢ <;>
    exact Function.update_of_ne hi _ _

/-- A hosting: owner family and chart of every register of one invocation. -/
structure Hosting (ι Φ K W M : Type*) [Semiring K] [AddCommMonoid W] [Module K W]
    [AddCommMonoid M] [Module K M] where
  own : ι → Φ
  chart : ι → W ≃ₗ[K] M

/-- The registers as seen through their charts. -/
def view (σ : Hosting ι Φ K W M) (y : Φ → W) : ι → M := fun i => σ.chart i (y (σ.own i))

/-- One event executed on the physical families. -/
def realize (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) (e : Event ι Λ K) (y : Φ → W) : Φ → W :=
  Function.update y (σ.own (dst e)) ((σ.chart (dst e)).symm (e.phys rec (view σ y) (dst e)))

/-- A stream executed on the physical families. -/
def realizeRun (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) :
    List (Event ι Λ K) → (Φ → W) → (Φ → W)
  | [], y => y
  | e :: es, y => realizeRun σ rec es (realize σ rec e y)

theorem view_realize (σ : Hosting ι Φ K W M) (hinj : Function.Injective σ.own)
    (rec : Λ → Λ → M → M) (e : Event ι Λ K) (y : Φ → W) :
    view σ (realize σ rec e y) = e.phys rec (view σ y) := by
  funext i
  by_cases hi : i = dst e
  · subst hi; simp [view, realize]
  · have hf : σ.own i ≠ σ.own (dst e) := hinj.ne hi
    simp only [view, realize, Function.update_of_ne hf]
    rw [phys_ne rec e _ i hi]; rfl

/-- **Realization under the one-owner rule.**  The physical run, read through the charts, is the
local run of the same stream. -/
theorem realize_run (σ : Hosting ι Φ K W M) (hinj : Function.Injective σ.own)
    (rec : Λ → Λ → M → M) :
    ∀ (es : List (Event ι Λ K)) (y : Φ → W),
      view σ (realizeRun σ rec es y) = physRun rec es (view σ y)
  | [], _ => rfl
  | e :: es, y => by
    simp only [realizeRun, physRun]
    rw [realize_run σ hinj rec es, view_realize σ hinj]

omit [DecidableEq ι] [DecidableEq Φ] in
/-- The value of a family that hosts register `i` is the chart preimage of the view. -/
theorem family_eq (σ : Hosting ι Φ K W M) (y : Φ → W) (i : ι) :
    y (σ.own i) = (σ.chart i).symm (view σ y i) := by simp [view]

/-- Families that host no register of the invocation are untouched. -/
theorem realize_untouched (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) :
    ∀ (es : List (Event ι Λ K)) (y : Φ → W) (f : Φ), (∀ i, σ.own i ≠ f) →
      realizeRun σ rec es y f = y f
  | [], _, _, _ => rfl
  | e :: es, y, f, hf => by
    simp only [realizeRun]
    rw [realize_untouched σ rec es _ f hf, realize, Function.update_of_ne (Ne.symm (hf _))]

/-- **The one-owner rule is needed.**  If two registers share a family, the one-event stream
`scale i 0` already changes what register `j` sees, although the local run leaves `j` alone. -/
theorem one_owner_needed (σ : Hosting ι Φ K W M) (rec : Λ → Λ → M → M) (i j : ι) (hij : i ≠ j)
    (hown : σ.own i = σ.own j) (y : Φ → W) (hy : view σ y j ≠ 0) :
    view σ (realizeRun σ rec [Event.scale i (0 : K)] y) j ≠
      physRun rec [Event.scale i (0 : K)] (view σ y) j := by
  have h1 : view σ (realizeRun σ rec [Event.scale i (0 : K)] y) j = 0 := by
    simp only [realizeRun, realize, view, dst]
    rw [hown, Function.update_self]
    simp [Event.phys]
  have h2 : physRun rec [Event.scale i (0 : K)] (view σ y) j = view σ y j := by
    simp [physRun, Event.phys, Function.update_of_ne (Ne.symm hij)]
  rw [h1, h2]
  exact fun h => hy h.symm

section Endpoint

variable [Fintype ι]

/-- **The helper's family at the end of a complete invocation.**  One owner, exact recipes,
well labelled, and a unit row of the scalar shadow (Lemma G, H3): the family ends as the chart
conjugate of `T_{λ¹ j} T_{λ⁰ j}⁻¹` applied to its own initial value. -/
theorem family_endpoint (T : Λ → M ≃ₗ[K] M) (σ : Hosting ι Φ K W M)
    (hinj : Function.Injective σ.own) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (y : Φ → W) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (j : ι)
    (hS : ∀ s, S es j s = if s = j then 1 else 0) :
    realizeRun σ rec es y (σ.own j) =
      (σ.chart j).symm (T (labRun es l j) ((T (l j)).symm (σ.chart j (y (σ.own j))))) := by
  rw [family_eq σ (realizeRun σ rec es y) j, realize_run σ hinj rec es y,
    row_unit T rec es l (view σ y) hrec hw j hS]
  rfl

/-- A zero column: changing input `j` does not change output `r ≠ j`. -/
theorem physRun_indep (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (j r : ι)
    (hcol : S es r j = 0) (v : M) :
    physRun rec es (Function.update h j v) r = physRun rec es h r := by
  rw [conj_matrix T rec es l _ hrec hw r, conj_matrix T rec es l h hrec hw r]
  congr 1
  refine Finset.sum_congr rfl (fun s _ => ?_)
  by_cases hs : s = j
  · subst hs; simp [hcol]
  · rw [Function.update_of_ne hs]

/-- **No other family reads the helper's family.**  If column `j` of the scalar shadow vanishes
off the diagonal (Lemma G, H3), every other family's end value is independent of the helper
family's initial value. -/
theorem endpoint_indep (T : Λ → M ≃ₗ[K] M) (σ : Hosting ι Φ K W M)
    (hinj : Function.Injective σ.own) (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (y : Φ → W) (hrec : RecipesExact T rec es) (hw : WellLabelled es l) (j : ι)
    (hcol : ∀ r, r ≠ j → S es r j = 0) (w : W) (f : Φ) (hf : f ≠ σ.own j) :
    realizeRun σ rec es (Function.update y (σ.own j) w) f = realizeRun σ rec es y f := by
  by_cases hfo : ∃ r, σ.own r = f
  · obtain ⟨r, rfl⟩ := hfo
    have hrj : r ≠ j := fun h => hf (h ▸ rfl)
    rw [family_eq σ (realizeRun σ rec es (Function.update y (σ.own j) w)) r,
      family_eq σ (realizeRun σ rec es y) r, realize_run σ hinj, realize_run σ hinj]
    have hv : view σ (Function.update y (σ.own j) w) =
        Function.update (view σ y) j (σ.chart j w) := by
      funext i
      by_cases hi : i = j
      · subst hi; simp [view]
      · simp [view, Function.update_of_ne hi, Function.update_of_ne (hinj.ne hi)]
    rw [hv, physRun_indep T rec es l _ hrec hw j r (hcol r hrj)]
  · push_neg at hfo
    rw [realize_untouched σ rec es _ f hfo, realize_untouched σ rec es _ f hfo,
      Function.update_of_ne hf]

end Endpoint

end LemmaA

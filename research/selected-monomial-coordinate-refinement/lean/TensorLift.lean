import LemmaG.Stream
import Mathlib.LinearAlgebra.PiTensorProduct.Basis
import Mathlib.LinearAlgebra.StdBasis

/-!
A formal tensor-lift audit of the common-label step in PR2287.
The unchanged LemmaG semantics and scalar shadow are imported, not recreated.
Gareth Davidson / bitplane, substantial OpenAI Codex assistance. Apache-2.0.
-/

open scoped TensorProduct
open LemmaG

namespace CommonLabelTensor

variable {K ι Λ J : Type*} [CommSemiring K] [DecidableEq ι] [Fintype ι]
variable {M : J → Type*} [∀ j, AddCommMonoid (M j)] [∀ j, Module K (M j)]

noncomputable def labels (T : ∀ j, Λ → M j ≃ₗ[K] M j) (A : Λ) :
    (⨂[K] j, M j) ≃ₗ[K] (⨂[K] j, M j) :=
  PiTensorProduct.congr (fun j => T j A)

def recipes (rec : ∀ j, Λ → Λ → M j →ₗ[K] M j) (A B : Λ) :
    (⨂[K] j, M j) →ₗ[K] (⨂[K] j, M j) :=
  PiTensorProduct.map (fun j => rec j A B)

omit [DecidableEq ι] [Fintype ι] in
/-- Separate exact unary certificates lift to the tensor recipe, on all states. -/
theorem recipes_exact (T : ∀ j, Λ → M j ≃ₗ[K] M j)
    (rec : ∀ j, Λ → Λ → M j →ₗ[K] M j) (es : List (Event ι Λ K))
    (hexact : ∀ j, Stream.RecipesExact (T j) (fun A B => rec j A B) es) :
    Stream.RecipesExact (labels T) (fun A B => recipes rec A B) es := by
  intro r A B he x
  have hm : recipes rec A B =
      ((labels T B).toLinearMap.comp (labels T A).symm.toLinearMap) := by
    apply PiTensorProduct.ext
    apply DFunLike.ext
    intro v
    change recipes rec A B (PiTensorProduct.tprod K v) =
      labels T B ((labels T A).symm (PiTensorProduct.tprod K v))
    simp only [recipes, PiTensorProduct.map_tprod, labels,
      PiTensorProduct.congr_symm_tprod, PiTensorProduct.congr_tprod]
    congr 1
    funext j
    exact hexact j r A B he (v j)
  exact DFunLike.congr_fun hm x

/-- Same events and scalar coefficients, arbitrary (not necessarily pure) input. -/
theorem conjugation (T : ∀ j, Λ → M j ≃ₗ[K] M j)
    (rec : ∀ j, Λ → Λ → M j →ₗ[K] M j) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → ⨂[K] j, M j)
    (hexact : ∀ j, Stream.RecipesExact (T j) (fun A B => rec j A B) es)
    (hlabels : Stream.WellLabelled es l) (r : ι) :
    Stream.physRun (fun A B => recipes rec A B) es h r =
      labels T (Stream.labRun es l r)
        (∑ s, Stream.S es r s • (labels T (l s)).symm (h s)) := by
  exact Stream.conj_matrix (labels T) (fun A B => recipes rec A B) es l h
    (recipes_exact T rec es hexact) hlabels r

end CommonLabelTensor

namespace CommonLabelTensor.Coefficients

variable {K R ι Λ : Type*} [CommSemiring K] [CommSemiring R] [DecidableEq ι]

/-- Change the coefficient field, keeping the event/label graph exactly. -/
def mapEvent (φ : K →+* R) : Event ι Λ K → Event ι Λ R
  | .relabel r A B => .relabel r A B
  | .add t s q => .add t s (φ q)
  | .scale t q => .scale t (φ q)
  | .copy c r F => .copy c r F
  | .clear c F => .clear c F

theorem label_step (φ : K →+* R) (e : Event ι Λ K) (l : ι → Λ) :
    (mapEvent φ e).lab l = e.lab l := by
  cases e <;> rfl

omit [DecidableEq ι] in
theorem admissible (φ : K →+* R) (e : Event ι Λ K) (l : ι → Λ) :
    (mapEvent φ e).Admissible l ↔ e.Admissible l := by
  cases e <;> rfl

theorem label_run (φ : K →+* R) (es : List (Event ι Λ K)) (l : ι → Λ) :
    Stream.labRun (es.map (mapEvent φ)) l = Stream.labRun es l := by
  induction es generalizing l with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, Stream.labRun, label_step]
    exact ih (e.lab l)

theorem wellLabelled (φ : K →+* R) (es : List (Event ι Λ K)) (l : ι → Λ) :
    Stream.WellLabelled (es.map (mapEvent φ)) l ↔ Stream.WellLabelled es l := by
  induction es generalizing l with
  | nil => rfl
  | cons e es ih =>
    simp only [List.map_cons, Stream.WellLabelled, admissible, label_step, ih]

omit [DecidableEq ι] in
theorem relabel_membership (φ : K →+* R) (es : List (Event ι Λ K))
    (r : ι) (A B : Λ) :
    Event.relabel r A B ∈ es.map (mapEvent φ) ↔ Event.relabel r A B ∈ es := by
  induction es with
  | nil => simp
  | cons e es ih =>
    cases e <;> simp [mapEvent, ih]

theorem scalar_step (φ : K →+* R) (e : Event ι Λ K) (x : ι → K) :
    (mapEvent φ e).scal (fun i => φ (x i)) = fun i => φ (e.scal x i) := by
  funext i
  cases e <;> simp only [mapEvent, Event.scal, Event.phys]
  all_goals
    simp only [Function.update_apply]
    split_ifs <;> simp_all

theorem scalar_run (φ : K →+* R) (es : List (Event ι Λ K)) (x : ι → K) :
    Stream.scalRun (es.map (mapEvent φ)) (fun i => φ (x i)) =
      fun i => φ (Stream.scalRun es x i) := by
  induction es generalizing x with
  | nil => rfl
  | cons e es ih =>
    change Stream.scalRun (es.map (mapEvent φ)) ((mapEvent φ e).scal (fun i => φ (x i))) = _
    rw [scalar_step, ih]
    rfl

/-- A rational role coefficient is embedded once, regardless of column count. -/
theorem shadow (φ : K →+* R) (es : List (Event ι Λ K)) (r s : ι) :
    Stream.S (es.map (mapEvent φ)) r s = φ (Stream.S es r s) := by
  have hb : (Pi.single s (1 : R) : ι → R) = fun i => φ ((Pi.single s (1 : K) : ι → K) i) := by
    funext i
    by_cases hi : s = i <;> simp [hi]
  unfold Stream.S
  rw [hb, scalar_run]

end CommonLabelTensor.Coefficients

namespace CommonLabelTensor

variable {K R ι Λ J : Type*} [CommSemiring K] [CommSemiring R]
variable [DecidableEq ι] [Fintype ι]
variable {M : J → Type*} [∀ j, AddCommMonoid (M j)] [∀ j, Module R (M j)]

/-- The column recipe condition refers to the ORIGINAL coefficient-field stream. -/
def ColumnRecipesExact (T : ∀ j, Λ → M j ≃ₗ[R] M j)
    (rec : ∀ j, Λ → Λ → M j →ₗ[R] M j) (es : List (Event ι Λ K)) : Prop :=
  ∀ j r A B, Event.relabel r A B ∈ es → ∀ v, rec j A B v = T j B ((T j A).symm v)

/-- Main bridge: tensor over the address field R, while retaining source
coefficients from K through the explicit homomorphism φ (e.g. Q -> C). -/
theorem conjugation_extended (φ : K →+* R)
    (T : ∀ j, Λ → M j ≃ₗ[R] M j) (rec : ∀ j, Λ → Λ → M j →ₗ[R] M j)
    (es : List (Event ι Λ K)) (l : ι → Λ) (h : ι → ⨂[R] j, M j)
    (hexact : ColumnRecipesExact T rec es) (hlabels : Stream.WellLabelled es l) (r : ι) :
    Stream.physRun (fun A B => recipes rec A B) (es.map (Coefficients.mapEvent φ)) h r =
      labels T (Stream.labRun es l r)
        (∑ s, φ (Stream.S es r s) • (labels T (l s)).symm (h s)) := by
  have he : ∀ j, Stream.RecipesExact (T j) (fun A B => rec j A B)
      (es.map (Coefficients.mapEvent φ)) := by
    intro j rr A B hm v
    exact hexact j rr A B ((Coefficients.relabel_membership φ es rr A B).mp hm) v
  have answer := conjugation T rec (es.map (Coefficients.mapEvent φ)) l h he
    ((Coefficients.wellLabelled φ es l).mpr hlabels) r
  simpa only [Coefficients.label_run, Coefficients.shadow] using answer

/-- A unit shadow row stays an uncontaminated unary endpoint at every width. -/
theorem unit_row_extended (φ : K →+* R)
    (T : ∀ j, Λ → M j ≃ₗ[R] M j) (rec : ∀ j, Λ → Λ → M j →ₗ[R] M j)
    (es : List (Event ι Λ K)) (l : ι → Λ) (h : ι → ⨂[R] j, M j)
    (hexact : ColumnRecipesExact T rec es) (hlabels : Stream.WellLabelled es l) (r : ι)
    (hS : ∀ s, Stream.S es r s = if s = r then 1 else 0) :
    Stream.physRun (fun A B => recipes rec A B) (es.map (Coefficients.mapEvent φ)) h r =
      labels T (Stream.labRun es l r) ((labels T (l r)).symm (h r)) := by
  rw [conjugation_extended φ T rec es l h hexact hlabels r]
  simp [hS, ite_smul]

end CommonLabelTensor

namespace CommonLabelTensor

variable {R J : Type*} [CommSemiring R] [Fintype J]
variable (A : J → Type*) [∀ j, Fintype (A j)]

/-- The tensor space is the FULL coordinate array, not only decomposable inputs. -/
noncomputable def coordinates : (⨂[R] j, A j → R) ≃ₗ[R] (((j : J) → A j) → R) :=
  (Basis.piTensorProduct (fun j => Pi.basisFun R (A j))).repr.trans
    (Finsupp.linearEquivFunOnFinite R R ((j : J) → A j))

theorem coordinates_surjective : Function.Surjective (coordinates (R := R) A) :=
  (coordinates (R := R) A).surjective

/-- On pure tensors this equivalence is exactly the usual coordinate product. -/
theorem coordinates_tprod (x : ∀ j, A j → R) (a : ∀ j, A j) :
    coordinates (R := R) A (PiTensorProduct.tprod R x) a = ∏ j, x j (a j) := by
  classical
  simp [coordinates, Basis.piTensorProduct_repr_tprod_apply]

end CommonLabelTensor

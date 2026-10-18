/-
Hyperplane-ended helpers, labels: Lemma G's extended labels with an arbitrary terminal frame.

Lemma G (`../e8-lemma-g-lean/PROOF.md` §1.3) reads every wrapper as a relabel by giving an
entering helper `j` two register-specific tags with operators
* `T_(prew,j) = R_E T_E`        (before the pre wrapper `R_E⁻¹`),
* `T_(done,j) = L_E⁻¹ T_FULL`   (after the post wrapper `L_E⁻¹`).
Here the terminal frame `FULL` is replaced by an arbitrary frame `U_j` (`term j`), and the
wrappers are keyed by the pair `(E_j, U_j)`.  Nothing below names `FULL`.

* `pre_recipe`, `post_recipe`   the wrappers execute `R_{E,U}⁻¹` and `L_{E,U}⁻¹`;
* `wrapped_block`               `T_(done,j) T_(prew,j)⁻¹ = L⁻¹ T_U T_E⁻¹ R⁻¹`;
* `factor_of_exact`             (N) `T_U T_E⁻¹ = L (C ⊗ id) R` gives Lemma A's (F);
* `factor_iff_pre`              with an invertible residual, (F) holds iff the pre wrapper is the
                                `(E, U)` recipe (review finding F1: `R_{E,FULL}` is wrong).
Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
-/
import Mathlib.LinearAlgebra.TensorProduct.Basic

namespace HyperplaneEnd

open TensorProduct

/-- Extended labels: a frame of the word's family, or the register-specific tag of an entering
helper before its pre wrapper (`prew`) or after its post wrapper (`done`). -/
inductive XLab (ι Fr : Type*) where
  | frame (F : Fr)
  | prew (j : ι)
  | done (j : ι)

variable {K : Type*} [CommSemiring K]
variable {M : Type*} [AddCommMonoid M] [Module K M]
variable {ι Fr : Type*}

/-- The operators of the extended labels.  `T` is the word's frame family, `ent j` and `term j`
the entrance and terminal frames of helper `j`, `Lw E U` and `Rw E U` the serialized wrapper
monomials of the pair `(E, U)`. -/
def Text (T : Fr → M ≃ₗ[K] M) (ent term : ι → Fr) (Lw Rw : Fr → Fr → M ≃ₗ[K] M) :
    XLab ι Fr → M ≃ₗ[K] M
  | .frame F => T F
  | .prew j => (T (ent j)).trans (Rw (ent j) (term j))
  | .done j => (T (term j)).trans (Lw (ent j) (term j)).symm

variable (T : Fr → M ≃ₗ[K] M) (ent term : ι → Fr) (Lw Rw : Fr → Fr → M ≃ₗ[K] M)

/-- The pre wrapper `relabel j (prew j) (ent j)` executes `T_E T_(prew,j)⁻¹ = R_{E,U}⁻¹`. -/
theorem pre_recipe (j : ι) (v : M) :
    Text T ent term Lw Rw (.frame (ent j)) ((Text T ent term Lw Rw (.prew j)).symm v) =
      (Rw (ent j) (term j)).symm v := by
  simp [Text, LinearEquiv.symm_trans_apply]

/-- The post wrapper `relabel j (term j) (done j)` executes `T_(done,j) T_U⁻¹ = L_{E,U}⁻¹`. -/
theorem post_recipe (j : ι) (v : M) :
    Text T ent term Lw Rw (.done j) ((Text T ent term Lw Rw (.frame (term j))).symm v) =
      (Lw (ent j) (term j)).symm v := by
  simp [Text]

/-- The wrapped block of helper `j`: `T_(done,j) T_(prew,j)⁻¹ = L⁻¹ T_U T_E⁻¹ R⁻¹`. -/
theorem wrapped_block (j : ι) (v : M) :
    Text T ent term Lw Rw (.done j) ((Text T ent term Lw Rw (.prew j)).symm v) =
      (Lw (ent j) (term j)).symm (T (term j) ((T (ent j)).symm ((Rw (ent j) (term j)).symm v))) := by
  simp [Text, LinearEquiv.symm_trans_apply]

variable {A B : Type*} [AddCommMonoid A] [Module K A] [AddCommMonoid B] [Module K B]

/-- **(N) gives (F).**  If the nested-children factorization `T_U T_E⁻¹ = L (C ⊗ id) R` holds
exactly (global phase included) for the pair `(E_j, U_j)`, the wrapped block in the extended
labels is `C ⊗ id`: Lemma A's hypothesis (F), whatever the terminal frame `U_j` is. -/
theorem factor_of_exact (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (ent term : ι → Fr)
    (Lw Rw : Fr → Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (j : ι) (C : A →ₗ[K] A)
    (hN : ∀ v, T (term j) ((T (ent j)).symm v) =
      Lw (ent j) (term j) (C.rTensor B (Rw (ent j) (term j) v))) (v : A ⊗[K] B) :
    Text T ent term Lw Rw (.done j) ((Text T ent term Lw Rw (.prew j)).symm v) = C.rTensor B v := by
  rw [wrapped_block, hN]
  simp

/-- **The pre wrapper must be the `(E, U)` recipe** (review finding F1).  Suppose (N) holds for
`(E_j, U_j)` with `L, R` and an invertible residual `C`, and the pre wrapper that actually ran
executed `R'⁻¹`.  Then `L⁻¹ T_U T_E⁻¹ R'⁻¹ = C ⊗ id` exactly when `R' = R`.  In particular a
pre wrapper decoded against the FULL recipe `R_{E,FULL} ≠ R_{E,U}` breaks (F). -/
theorem factor_iff_pre (T : Fr → (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (E U : Fr)
    (L R R' : (A ⊗[K] B) ≃ₗ[K] (A ⊗[K] B)) (C : A ≃ₗ[K] A)
    (hN : ∀ v, T U ((T E).symm v) = L ((C : A →ₗ[K] A).rTensor B (R v))) :
    (∀ v, L.symm (T U ((T E).symm (R'.symm v))) = (C : A →ₗ[K] A).rTensor B v) ↔ R' = R := by
  constructor
  · intro h
    have hinj : Function.Injective ((C : A →ₗ[K] A).rTensor B) := by
      rw [← LinearEquiv.coe_rTensor]
      exact (LinearEquiv.rTensor B C).injective
    ext w
    have := h (R' w)
    rw [LinearEquiv.symm_apply_apply, hN, LinearEquiv.symm_apply_apply] at this
    exact (hinj this).symm
  · rintro rfl v
    rw [hN]
    simp

end HyperplaneEnd

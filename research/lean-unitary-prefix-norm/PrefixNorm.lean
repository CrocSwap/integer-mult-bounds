/-
Prefix norm corollaries for the existing Lemma G stream semantics.
Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
The conjugation theorem and Event/Stream definitions are credited imports.
-/
import LemmaG.Stream
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

open scoped BigOperators

namespace PrefixNorm

open LemmaG LemmaG.Stream

section Labelled

variable {ι Λ K M : Type*} [Fintype ι] [DecidableEq ι]
variable [NormedField K] [NormedAddCommGroup M] [NormedSpace K M]

omit [Fintype ι] [NormedField K] in
/-- A prefix inherits the actual source's well-labelled condition. -/
theorem wellLabelled_take (es : List (Event ι Λ K)) (l : ι → Λ)
    (hw : WellLabelled es l) (k : ℕ) : WellLabelled (es.take k) l := by
  have h := (wellLabelled_append (es.take k) (es.drop k) l).mp (by simpa using hw)
  exact h.1

omit [Fintype ι] [DecidableEq ι] in
/-- Exact recipes are inherited by prefixes; no new event model is introduced. -/
theorem recipesExact_take (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (hr : RecipesExact T rec es) (k : ℕ) :
    RecipesExact T rec (es.take k) := by
  intro r A B hm v
  exact hr r A B (List.mem_of_mem_take hm) v

/-- Norm preservation of a linear equivalence also controls its inverse. -/
theorem inverse_norm (T : Λ → M ≃ₗ[K] M)
    (hT : ∀ a x, ‖T a x‖ = ‖x‖) (a : Λ) (x : M) : ‖(T a).symm x‖ = ‖x‖ := by
  simpa using (hT a ((T a).symm x)).symm

/-- Weighted row estimate, on the imported physical semantics and scalar matrix. -/
theorem weighted_row (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (l : ι → Λ) (x : ι → M) (budget : ι → ℝ)
    (hT : ∀ a v, ‖T a v‖ = ‖v‖) (hr : RecipesExact T rec es)
    (hw : WellLabelled es l) (hx : ∀ j, ‖x j‖ ≤ budget j) (r : ι) :
    ‖physRun rec es x r‖ ≤ ∑ j, ‖S es r j‖ * budget j := by
  rw [conj_matrix T rec es l x hr hw r, hT]
  calc
    ‖∑ j, S es r j • (T (l j)).symm (x j)‖
        ≤ ∑ j, ‖S es r j • (T (l j)).symm (x j)‖ := norm_sum_le _ _
    _ = ∑ j, ‖S es r j‖ * ‖x j‖ := by
      apply Finset.sum_congr rfl
      intro j _
      rw [norm_smul, inverse_norm T hT]
    _ ≤ ∑ j, ‖S es r j‖ * budget j := by
      exact Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hx j) (norm_nonneg _)

/-- All finite words and all prefix lengths, including k beyond the word length. -/
theorem weighted_prefix (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (l : ι → Λ) (x : ι → M) (budget : ι → ℝ)
    (hT : ∀ a v, ‖T a v‖ = ‖v‖) (hr : RecipesExact T rec es)
    (hw : WellLabelled es l) (hx : ∀ j, ‖x j‖ ≤ budget j) (k : ℕ) (r : ι) :
    ‖physRun rec (es.take k) x r‖ ≤ ∑ j, ‖S (es.take k) r j‖ * budget j := by
  exact weighted_row T rec (es.take k) l x budget hT (recipesExact_take T rec es hr k)
    (wellLabelled_take es l hw k) hx r

/-- Empty private inputs cost zero. The signed row is restricted to actual inputs. -/
theorem supported_prefix (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (l : ι → Λ) (x : ι → M) (active : Finset ι) (B : ℝ)
    (hT : ∀ a v, ‖T a v‖ = ‖v‖) (hr : RecipesExact T rec es) (hw : WellLabelled es l)
    (hx : ∀ j ∈ active, ‖x j‖ ≤ B) (hz : ∀ j ∉ active, x j = 0) (k : ℕ) (r : ι) :
    ‖physRun rec (es.take k) x r‖ ≤ (∑ j ∈ active, ‖S (es.take k) r j‖) * B := by
  have hi : ∀ j, ‖x j‖ ≤ if j ∈ active then B else 0 := by
    intro j
    by_cases h : j ∈ active
    · simpa [h] using hx j h
    · simp [h, hz j h]
  have bound := weighted_prefix T rec es l x (fun j => if j ∈ active then B else 0)
    hT hr hw hi k r
  simpa [mul_ite, Finset.sum_mul] using bound

/-- A persistent-column prefix certificate supplies one uniform physical bound. -/
theorem supported_certificate (T : Λ → M ≃ₗ[K] M) (rec : Λ → Λ → M → M)
    (es : List (Event ι Λ K)) (l : ι → Λ) (x : ι → M) (active : Finset ι) (B L : ℝ)
    (hT : ∀ a v, ‖T a v‖ = ‖v‖) (hr : RecipesExact T rec es) (hw : WellLabelled es l)
    (hB : 0 ≤ B) (hx : ∀ j ∈ active, ‖x j‖ ≤ B) (hz : ∀ j ∉ active, x j = 0)
    (hrows : ∀ k r, (∑ j ∈ active, ‖S (es.take k) r j‖) ≤ L) (k : ℕ) (r : ι) :
    ‖physRun rec (es.take k) x r‖ ≤ L * B := by
  exact (supported_prefix T rec es l x active B hT hr hw hx hz k r).trans
    (mul_le_mul_of_nonneg_right (hrows k r) hB)

end Labelled

section PartialStore

variable {ν 𝕜 : Type*} [Fintype ν] [DecidableEq ν] [RCLike 𝕜]

/-- A subset of coordinates has been written; the complement still holds the old value. -/
def splice (written : Finset ν) (old new : EuclideanSpace 𝕜 ν) : EuclideanSpace 𝕜 ν :=
  WithLp.toLp 2 (fun i => if i ∈ written then new i else old i)

/-- Actual Euclidean norm, not the max norm of an unwrapped Pi type. -/
theorem splice_sq (written : Finset ν) (old new : EuclideanSpace 𝕜 ν) :
    ‖splice written old new‖ ^ 2 ≤ ‖old‖ ^ 2 + ‖new‖ ^ 2 := by
  rw [PiLp.norm_sq_eq_of_L2, PiLp.norm_sq_eq_of_L2, PiLp.norm_sq_eq_of_L2,
      ← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro i _
  change ‖if i ∈ written then new i else old i‖ ^ 2 ≤ ‖old i‖ ^ 2 + ‖new i‖ ^ 2
  by_cases h : i ∈ written
  · simp only [if_pos h]
    exact le_add_of_nonneg_left (sq_nonneg _)
  · simp only [if_neg h]
    exact le_add_of_nonneg_right (sq_nonneg _)

/-- Explicit factor-two squared allowance for partially stored values. -/
theorem splice_uniform (written : Finset ν) (old new : EuclideanSpace 𝕜 ν) (L : ℝ)
    (hL : 0 ≤ L) (ho : ‖old‖ ≤ L) (hn : ‖new‖ ≤ L) :
    ‖splice written old new‖ ^ 2 ≤ 2 * L ^ 2 := by
  have ho2 : ‖old‖ ^ 2 ≤ L ^ 2 := (sq_le_sq₀ (norm_nonneg _) hL).mpr ho
  have hn2 : ‖new‖ ^ 2 ≤ L ^ 2 := (sq_le_sq₀ (norm_nonneg _) hL).mpr hn
  nlinarith [splice_sq written old new]

/-- A rational/integer squared guard yields a strict binary precision envelope. -/
theorem splice_bits (written : Finset ν) (old new : EuclideanSpace 𝕜 ν) (L : ℝ) (b : ℕ)
    (hL : 0 ≤ L) (ho : ‖old‖ ≤ L) (hn : ‖new‖ ≤ L)
    (hbits : 2 * L ^ 2 < (2 : ℝ) ^ (2 * b)) :
    ‖splice written old new‖ < (2 : ℝ) ^ b := by
  have hp : 0 ≤ (2 : ℝ) ^ b := by positivity
  apply (sq_lt_sq₀ (norm_nonneg _) hp).mp
  have he : ((2 : ℝ) ^ b) ^ 2 = (2 : ℝ) ^ (2 * b) := by rw [← pow_mul, Nat.mul_comm]
  rw [he]
  exact (splice_uniform written old new L hL ho hn).trans_lt hbits

end PartialStore

section ComplexComponents

variable {ν : Type*} [Fintype ν] [DecidableEq ν]

/-- Real and imaginary components can have independent completed-write masks. -/
def components (realDone imagDone : Finset ν) (old new : EuclideanSpace ℂ ν) :
    EuclideanSpace ℂ ν := WithLp.toLp 2 (fun i =>
      ⟨if i ∈ realDone then (new i).re else (old i).re,
       if i ∈ imagDone then (new i).im else (old i).im⟩)

/-- Direct complex half-store bound, without assuming a realification isometry. -/
theorem components_sq (realDone imagDone : Finset ν) (old new : EuclideanSpace ℂ ν) :
    ‖components realDone imagDone old new‖ ^ 2 ≤ ‖old‖ ^ 2 + ‖new‖ ^ 2 := by
  rw [PiLp.norm_sq_eq_of_L2, PiLp.norm_sq_eq_of_L2, PiLp.norm_sq_eq_of_L2,
      ← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro i _
  simp only [Complex.sq_norm, Complex.normSq_apply, components, PiLp.toLp_apply]
  split_ifs <;> nlinarith [sq_nonneg (old i).re, sq_nonneg (old i).im,
                          sq_nonneg (new i).re, sq_nonneg (new i).im]

/-- A uniform bound on either complex endpoint controls any component write order. -/
theorem components_uniform (realDone imagDone : Finset ν) (old new : EuclideanSpace ℂ ν)
    (L : ℝ) (hL : 0 ≤ L) (ho : ‖old‖ ≤ L) (hn : ‖new‖ ≤ L) :
    ‖components realDone imagDone old new‖ ^ 2 ≤ 2 * L ^ 2 := by
  have ho2 : ‖old‖ ^ 2 ≤ L ^ 2 := (sq_le_sq₀ (norm_nonneg _) hL).mpr ho
  have hn2 : ‖new‖ ^ 2 ≤ L ^ 2 := (sq_le_sq₀ (norm_nonneg _) hL).mpr hn
  nlinarith [components_sq realDone imagDone old new]

/-- Strict bit envelope for independently written real/imaginary coordinates. -/
theorem components_bits (realDone imagDone : Finset ν) (old new : EuclideanSpace ℂ ν)
    (L : ℝ) (b : ℕ) (hL : 0 ≤ L) (ho : ‖old‖ ≤ L) (hn : ‖new‖ ≤ L)
    (hbits : 2 * L ^ 2 < (2 : ℝ) ^ (2 * b)) :
    ‖components realDone imagDone old new‖ < (2 : ℝ) ^ b := by
  have hp : 0 ≤ (2 : ℝ) ^ b := by positivity
  apply (sq_lt_sq₀ (norm_nonneg _) hp).mp
  have he : ((2 : ℝ) ^ b) ^ 2 = (2 : ℝ) ^ (2 * b) := by rw [← pow_mul, Nat.mul_comm]
  rw [he]
  exact (components_uniform realDone imagDone old new L hL ho hn).trans_lt hbits

end ComplexComponents

end PrefixNorm

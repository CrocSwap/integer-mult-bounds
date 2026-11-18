/-
SPECBREAK R42 Lemma TS = T1 (audited for J = 7 in internal notes), Model-setting version with explicit targets/ancillas, rank facts, and the corollaries.
Reuses SpecTSUR (product formula, lemmaTS).  See SpecTS.md for the exact statements.
-/
import Nov15.SpecTSUR
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Data.List.FinRange

open Matrix Finset SpecTSUR

set_option linter.unusedSectionVars false

namespace SpecTS

variable {K : Type*} [Field K]

/-! ## §1. General job lemmas (no model assumptions) -/
section Jobs
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- two jobs with `y·x' = 0 = y'·x` commute -/
theorem refl_comm (x y x' y' : n → K) (h1 : y ⬝ᵥ x' = 0) (h2 : y' ⬝ᵥ x = 0) :
    SpecTSUR.refl x y * SpecTSUR.refl x' y' = SpecTSUR.refl x' y' * SpecTSUR.refl x y := by
  have hAB : vecMulVec x y * vecMulVec x' y' = 0 := by
    rw [vecMulVec_mul_vecMulVec, h1]; simp
  have hBA : vecMulVec x' y' * vecMulVec x y = 0 := by
    rw [vecMulVec_mul_vecMulVec, h2]; simp
  simp only [SpecTSUR.refl, mul_sub, sub_mul, one_mul, mul_one, hAB, hBA, sub_zero]
  abel

/-- a job with `y·x = 2` is an involution -/
theorem refl_sq (x y : n → K) (h : y ⬝ᵥ x = 2) : SpecTSUR.refl x y * SpecTSUR.refl x y = 1 := by
  have hAA : vecMulVec x y * vecMulVec x y = (2 : K) • vecMulVec x y := by
    rw [vecMulVec_mul_vecMulVec, h]; ext a b; simp [vecMulVec_apply]; ring
  simp only [SpecTSUR.refl, mul_sub, sub_mul, one_mul, mul_one, hAA]
  ext a b; simp [Matrix.sub_apply, Matrix.smul_apply]; ring

/-- a job whose `x, y` vanish on the ancilla coordinates is block diagonal `(job, I)` -/
theorem refl_blocks {τ α : Type*} [Fintype τ] [Fintype α] [DecidableEq τ] [DecidableEq α]
    (x y : τ ⊕ α → K) (hx : ∀ a, x (Sum.inr a) = 0) (hy : ∀ a, y (Sum.inr a) = 0) :
    SpecTSUR.refl x y = fromBlocks (SpecTSUR.refl (x ∘ Sum.inl) (y ∘ Sum.inl)) 0 0 1 := by
  ext (a | a) (b | b) <;>
    simp [SpecTSUR.refl, vecMulVec_apply, hx, hy, Matrix.one_apply, Matrix.fromBlocks]

/-- ordered jobs as a function on `Fin k` -/
def gJ (x y : ℕ → n → K) (k : ℕ) : Fin k → Matrix n n K := fun i => SpecTSUR.refl (x i) (y i)

theorem pp_eq_prod (x y : ℕ → n → K) (k : ℕ) : pp x y k = (List.ofFn (gJ x y k)).prod := by
  induction k with
  | zero => simp [pp]
  | succ k ih =>
    rw [List.ofFn_succ', List.prod_concat, pp, ih]
    rfl

/-- product of any order of pairwise commuting jobs equals the ordered product -/
theorem prod_perm (x y : ℕ → n → K) (k : ℕ) (hc : ∀ i j, Commute (gJ x y k i) (gJ x y k j))
    (σ : Equiv.Perm (Fin k)) : (List.ofFn (gJ x y k ∘ σ)).prod = pp x y k := by
  rw [pp_eq_prod]
  refine ((σ.ofFn_comp_perm (gJ x y k)).prod_eq' ?_)
  rw [List.pairwise_ofFn]
  intro i j _; exact hc _ _

/-- product of two families of mutually commuting elements -/
theorem prod_ofFn_mul {M : Type*} [Monoid M] (k : ℕ) (a b : Fin k → M)
    (h : ∀ i j, Commute (a i) (b j)) :
    (List.ofFn a).prod * (List.ofFn b).prod = (List.ofFn fun i => a i * b i).prod := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [List.ofFn_succ, List.ofFn_succ, List.ofFn_succ, List.prod_cons, List.prod_cons,
      List.prod_cons]
    have hc : Commute (List.ofFn fun i : Fin k => a i.succ).prod (b 0) :=
      Commute.list_prod_left _ _ (by
        intro u hu
        obtain ⟨i, rfl⟩ := List.mem_ofFn.1 hu
        exact h _ _)
    have := ih (fun i => a i.succ) (fun i => b i.succ) (fun i j => h _ _)
    calc a 0 * (List.ofFn fun i : Fin k => a i.succ).prod * (b 0 * (List.ofFn fun i : Fin k => b i.succ).prod)
        = a 0 * ((List.ofFn fun i : Fin k => a i.succ).prod * b 0) *
            (List.ofFn fun i : Fin k => b i.succ).prod := by simp only [mul_assoc]
      _ = a 0 * (b 0 * (List.ofFn fun i : Fin k => a i.succ).prod) *
            (List.ofFn fun i : Fin k => b i.succ).prod := by rw [hc.eq]
      _ = a 0 * b 0 * ((List.ofFn fun i : Fin k => a i.succ).prod *
            (List.ofFn fun i : Fin k => b i.succ).prod) := by simp only [mul_assoc]
      _ = _ := by rw [this]

/-- the sub-product of the jobs indexed by `T` (in index order, other letters replaced by `1`) -/
noncomputable def gT (x y : ℕ → n → K) (k : ℕ) (T : Finset (Fin k)) : Matrix n n K :=
  open Classical in (List.ofFn fun i => if i ∈ T then gJ x y k i else 1).prod

theorem gT_mul_compl (x y : ℕ → n → K) (k : ℕ) (hc : ∀ i j, Commute (gJ x y k i) (gJ x y k j))
    (T : Finset (Fin k)) : gT x y k T * gT x y k Tᶜ = pp x y k := by
  classical
  rw [pp_eq_prod, gT, gT, prod_ofFn_mul]
  · congr 1
    refine congrArg List.ofFn (funext fun i => ?_)
    by_cases hi : i ∈ T <;> simp [hi]
  · intro i j
    have : ∀ (S : Finset (Fin k)) (i : Fin k), ∀ j : Fin k,
        Commute (if i ∈ T then gJ x y k i else 1) (if j ∈ Tᶜ then gJ x y k j else 1) := by
      intro _ i j
      by_cases hi : i ∈ T <;> by_cases hj : j ∈ Tᶜ <;> simp [hi, hj, hc i j]
    exact this ∅ i j

theorem gT_sq (x y : ℕ → n → K) (k : ℕ) (hc : ∀ i j, Commute (gJ x y k i) (gJ x y k j))
    (hs : ∀ i, gJ x y k i * gJ x y k i = 1) (T : Finset (Fin k)) :
    gT x y k T * gT x y k T = 1 := by
  classical
  rw [gT, prod_ofFn_mul]
  · have : (fun i : Fin k => (if i ∈ T then gJ x y k i else 1) * (if i ∈ T then gJ x y k i else 1))
        = fun _ => 1 := by
      funext i; by_cases hi : i ∈ T <;> simp [hi, hs i]
    rw [this]; simp
  · intro i j
    by_cases hi : i ∈ T <;> by_cases hj : j ∈ T <;> simp [hi, hj, hc i j]

end Jobs

/-! ## §2. The model setting and Lemma TS -/
section Model
variable [DecidableEq K]
variable {τ α ι : Type*} [Fintype τ] [Fintype α] [Fintype ι] [DecidableEq τ] [DecidableEq α]

/-- MODEL SETTING (inherited, unaudited): coordinates `τ ⊕ α` (targets, ancillas); a character `μ`
flips target `j` iff `μ·t_j = 1` (in `ZMod 2`); `D_μ = diag((-1)^(μ·t_j))` on targets, `+1` on ancillas. -/
def sD (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) : τ ⊕ α → K :=
  Sum.elim (fun j => if μ ⬝ᵥ t j = 1 then -1 else 1) (fun _ => 1)

def Dmod (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) : Matrix (τ ⊕ α) (τ ⊕ α) K :=
  diagonal (sD (K := K) (α := α) μ t)

theorem sD_pm (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (a : τ ⊕ α) :
    sD (K := K) (α := α) μ t a = 1 ∨ sD (K := K) (α := α) μ t a = (-1 : K) := by
  rcases a with j | a
  · by_cases h : μ ⬝ᵥ t j = 1 <;> simp [sD, h]
  · simp [sD]

theorem card_flip (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) :
    (univ.filter fun a : τ ⊕ α => sD (K := K) (α := α) μ t a = (-1 : K)).card
      = (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card := by
  have hne : (1 : K) ≠ -1 := by intro h; apply h2; linear_combination h
  simp only [Finset.card_filter, Fintype.sum_sum_type]
  have h0 : ∑ a : α, (if sD (K := K) (α := α) μ t (Sum.inr a) = (-1 : K) then 1 else 0) = 0 := by
    simp [sD, hne]
  rw [h0, add_zero]
  refine Finset.sum_congr rfl fun j _ => ?_
  by_cases h : μ ⬝ᵥ t j = 1 <;> simp [sD, h, hne]

/-- columns `y_i` as an `n × m` matrix -/
def Ym {n : Type*} (y : ℕ → n → K) (m : ℕ) : Matrix n (Fin m) K := Matrix.of fun a i => y i a

/-- **Lemma TS (T1 = R42), model setting.**  Hypotheses (all explicit): char ≠ 2; unit-free character
`μ`: the ordered product of the `k` active jobs `1 - x_i y_iᵀ` equals `D_μ`; and tightness: the number
of flipped targets equals `k`.  Nothing else (not `y_i·x_i = 2`, not the job order, not `J`, `N`, `U`). -/
theorem lemmaTS_model (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) :
    -- (G) Gram = 2 I (both orders, whatever the word order)
    (∀ i j : Fin k, y i ⬝ᵥ x j = if i = j then 2 else 0) ∧
    -- (N) G = 2N, N = I (so N invertible, N = G/2 = I + strict-upper(G))
    (Ym y k)ᵀ * Xm x k = (2 : K) • Nm x y k ∧ Nm x y k = 1 ∧ IsUnit (Nm x y k) ∧
    -- (R) X, Y full rank
    (Xm x k).rank = k ∧ (Ym y k).rank = k ∧
    -- (S) supports: vanish on ancillas and on every unflipped target
    (∀ (i : Fin k) (a : α), x i (Sum.inr a) = 0 ∧ y i (Sum.inr a) = 0) ∧
    (∀ (i : Fin k) (j : τ), μ ⬝ᵥ t j ≠ 1 → x i (Sum.inl j) = 0 ∧ y i (Sum.inl j) = 0) ∧
    -- (I) image(I - D) = span(x_i)
    LinearMap.range (1 - Dmod (K := K) (α := α) μ t).mulVecLin
      = Submodule.span K (Set.range fun i : Fin k => x i) := by
  have hcard' : (univ.filter fun a : τ ⊕ α => sD (K := K) (α := α) μ t a = (-1 : K)).card = k := by
    rw [card_flip h2, hcard]
  obtain ⟨hG, hS, hI⟩ := lemmaTS k x y (sD (K := K) (α := α) μ t) h2 (sD_pm μ t) hprod hcard'
  have hGm : (Ym y k)ᵀ * Xm x k = (2 : K) • (1 : Matrix (Fin k) (Fin k) K) := by
    ext i j
    have := gram_apply x y k i j
    simp only [Ym] at this ⊢
    rw [this, hG i j]
    simp [Matrix.one_apply]
  have hN : Nm x y k = 1 := by
    ext i j
    simp only [Nm, Matrix.add_apply, Matrix.of_apply]
    by_cases hij : i < j
    · simp [hij, hG i j, hij.ne]
    · simp [hij]
  have hrk : ((2 : K) • (1 : Matrix (Fin k) (Fin k) K)).rank = k := by
    have : (2 : K) • (1 : Matrix (Fin k) (Fin k) K) = diagonal fun _ => (2 : K) := by
      ext i j; by_cases h : i = j <;> simp [Matrix.one_apply, diagonal_apply, h]
    rw [this, rank_diagonal]; simp [h2]
  refine ⟨hG, ?_, hN, hN ▸ isUnit_one, ?_, ?_, ?_, ?_, ?_⟩
  · rw [hGm, hN]
  · refine le_antisymm ((Matrix.rank_le_card_width _).trans (by simp)) ?_
    have := rank_mul_le_right (Ym y k)ᵀ (Xm x k)
    rw [hGm, hrk] at this; exact this
  · refine le_antisymm ((Matrix.rank_le_card_width _).trans (by simp)) ?_
    have := (rank_mul_le_left (Ym y k)ᵀ (Xm x k)).trans_eq (Matrix.rank_transpose (Ym y k))
    rw [hGm, hrk] at this; exact this
  · intro i a; exact hS i (Sum.inr a) (by simp [sD])
  · intro i j hj; exact hS i (Sum.inl j) (by simp [sD, hj])
  · exact hI

/-- COROLLARY: supports in target coordinates, jobs are `(job_R, I)` on targets ⊕ ancillas. -/
theorem model_job_blocks (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (i : Fin k) :
    SpecTSUR.refl (x i) (y i) = fromBlocks (SpecTSUR.refl (x i ∘ Sum.inl) (y i ∘ Sum.inl)) 0 0 1 := by
  obtain ⟨-, -, -, -, -, -, hanc, -, -⟩ := lemmaTS_model h2 μ t k x y hprod hcard
  exact refl_blocks _ _ (fun a => (hanc i a).1) (fun a => (hanc i a).2)

/-- COROLLARY: jobs fix ancillas: `(job v)_a = v_a` and the job fixes every ancilla-supported vector. -/
theorem model_job_fix_anc (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (i : Fin k) (v : τ ⊕ α → K) (a : α) :
    (SpecTSUR.refl (x i) (y i) *ᵥ v) (Sum.inr a) = v (Sum.inr a) := by
  rw [model_job_blocks h2 μ t k x y hprod hcard i]
  simp [Matrix.mulVec, dotProduct, Fintype.sum_sum_type, Matrix.fromBlocks, Matrix.one_apply]

/-- COROLLARY: jobs in the tight set pairwise commute. -/
theorem model_commute (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (i j : Fin k) :
    Commute (gJ x y k i) (gJ x y k j) := by
  obtain ⟨hG, -⟩ := lemmaTS_model h2 μ t k x y hprod hcard
  by_cases hij : i = j
  · subst hij; exact Commute.refl _
  · exact refl_comm _ _ _ _ (by simp [hG i j, hij]) (by simp [hG j i, Ne.symm hij])

/-- COROLLARY: every job is an involution. -/
theorem model_invol (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (i : Fin k) :
    gJ x y k i * gJ x y k i = 1 := by
  obtain ⟨hG, -⟩ := lemmaTS_model h2 μ t k x y hprod hcard
  exact refl_sq _ _ (by simpa using hG i i)

/-- COROLLARY: the product of the `k` jobs in ANY order is `D_μ`. -/
theorem model_any_order (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (σ : Equiv.Perm (Fin k)) :
    (List.ofFn (gJ x y k ∘ σ)).prod = Dmod (K := K) (α := α) μ t := by
  rw [prod_perm x y k (model_commute h2 μ t k x y hprod hcard) σ, hprod]

/-- COROLLARY (`g_d = (∏_{S∖d} g) D_R`): for every subset `T` of the tight set, the sub-product
over `T` equals the sub-product over the complement times `D_μ` (`D_μ = D_R ⊕ I_ancillas`). -/
theorem model_gd (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (T : Finset (Fin k)) :
    gT x y k T = gT x y k Tᶜ * Dmod (K := K) (α := α) μ t := by
  have hc := model_commute h2 μ t k x y hprod hcard
  have hs := model_invol h2 μ t k x y hprod hcard
  have h1 := gT_mul_compl x y k hc T
  have h3 := gT_sq x y k hc hs Tᶜ
  rw [← hprod, ← h1]
  symm
  have h1c := gT_mul_compl x y k hc Tᶜ
  rw [compl_compl] at h1c
  calc gT x y k Tᶜ * (gT x y k T * gT x y k Tᶜ)
      = gT x y k Tᶜ * (gT x y k Tᶜ * gT x y k T) := by rw [h1, h1c]
    _ = (gT x y k Tᶜ * gT x y k Tᶜ) * gT x y k T := by rw [Matrix.mul_assoc]
    _ = gT x y k T := by rw [h3, Matrix.one_mul]
  
end Model

/-! ## §3. Non-vacuity: hypotheses are satisfiable (k = 1, one target flipped, one ancilla) over ℚ -/
section Example
def ex_x : ℕ → Unit ⊕ Unit → ℚ := fun _ => Sum.elim (fun _ => 1) (fun _ => 0)
def ex_y : ℕ → Unit ⊕ Unit → ℚ := fun _ => Sum.elim (fun _ => 2) (fun _ => 0)

theorem ex_prod : pp ex_x ex_y 1 = Dmod (K := ℚ) (α := Unit) (fun _ : Unit => (1 : ZMod 2))
    (fun _ _ => (1 : ZMod 2)) := by
  ext (a | a) (b | b) <;>
    simp [pp, SpecTSUR.refl, ex_x, ex_y, Dmod, sD, vecMulVec_apply, diagonal_apply, Matrix.one_apply] <;> norm_num

theorem ex_card : (Finset.univ.filter fun j : Unit =>
    (fun _ : Unit => (1 : ZMod 2)) ⬝ᵥ (fun _ : Unit => (1 : ZMod 2)) = 1).card = 1 := by decide

/-- the model theorem applies (so its hypotheses are not contradictory) -/
example := lemmaTS_model (K := ℚ) (α := Unit) (by norm_num) (fun _ : Unit => (1 : ZMod 2))
  (fun _ _ => (1 : ZMod 2)) 1 ex_x ex_y ex_prod ex_card
end Example

end SpecTS

open SpecTS in
#print axioms lemmaTS_model
open SpecTS in
#print axioms model_job_blocks
open SpecTS in
#print axioms model_job_fix_anc
open SpecTS in
#print axioms model_commute
open SpecTS in
#print axioms model_invol
open SpecTS in
#print axioms model_any_order
open SpecTS in
#print axioms model_gd
open SpecTS in
#print axioms ex_prod

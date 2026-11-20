import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Logic.Equiv.Option
/-!
LINORD (lane LEANLINEAR).  The ORDERING LEMMA of LINEAR56 §3 (pure linear algebra, any field).
`OrdProp M` : for every k, a vector supported on rows < k that is orthogonal to columns 0..k is zero
  (i.e. the k x (k+1) block M[0..k-1, 0..k] has full row rank k).
`exists_ordering` : every n x n matrix of rank >= n-1 (in particular every invertible one) has a
  simultaneous row/column ordering e with OrdProp (M.submatrix e e).
`no_alt_upper` : in such an order there is no nonzero symmetric zero-diagonal N with N*M strictly upper
  triangular (entries on and below the diagonal vanish).
-/
open Matrix Finset

namespace LinOrd

variable {K : Type*} [Field K]

/-- the ordering property -/
def OrdProp {n : ℕ} (M : Matrix (Fin n) (Fin n) K) : Prop :=
  ∀ (k : Fin n) (v : Fin n → K), (∀ j, k ≤ j → v j = 0) →
    (∀ i, i ≤ k → (v ᵥ* M) i = 0) → v = 0

section Exist
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- principal submatrix with index r removed -/
def pm (M : Matrix ι ι K) (r : ι) : Matrix {i // i ≠ r} {i // i ≠ r} K :=
  M.submatrix (Subtype.val : {i // i ≠ r} → ι) Subtype.val

lemma card_ne (r : ι) : Fintype.card {i // i ≠ r} + 1 = Fintype.card ι := by
  rw [← Fintype.card_option, Fintype.card_congr (Equiv.optionSubtypeNe r)]

/-- deleting one column drops the row rank by at most one -/
lemma rank_principal_ge (M : Matrix ι ι K) (r : ι)
    (hind : LinearIndependent K (fun i : {i // i ≠ r} => M i)) :
    Fintype.card ι ≤ (pm M r).rank + 2 := by
  classical
  set S : Submodule K (ι → K) := Submodule.span K (Set.range (fun i : {i // i ≠ r} => M i)) with hS
  have hSf : Module.finrank K S = Fintype.card {i // i ≠ r} := finrank_span_eq_card hind
  set π : (ι → K) →ₗ[K] ({i // i ≠ r} → K) := LinearMap.funLeft K K (Subtype.val : {i // i ≠ r} → ι) with hπ
  have hrn := LinearMap.finrank_range_add_finrank_ker (π.domRestrict S)
  have hker : Module.finrank K (LinearMap.ker (π.domRestrict S)) ≤ 1 := by
    let f : (LinearMap.ker (π.domRestrict S)) →ₗ[K] K :=
      (LinearMap.proj r : (ι → K) →ₗ[K] K) ∘ₗ S.subtype ∘ₗ (LinearMap.ker (π.domRestrict S)).subtype
    have hvan : ∀ x : (LinearMap.ker (π.domRestrict S)), ∀ j, j ≠ r → x.1.1 j = 0 := by
      intro x j hj
      have hx2 : π x.1.1 = 0 := x.2
      have := congrFun hx2 ⟨j, hj⟩
      simpa [hπ] using this
    have hinj : Function.Injective f := by
      intro x y hxy
      have hr : x.1.1 r = y.1.1 r := hxy
      apply Subtype.ext; apply Subtype.ext
      funext j
      by_cases hj : j = r
      · subst hj; exact hr
      · rw [hvan x j hj, hvan y j hj]
    have := LinearMap.finrank_le_finrank_of_injective hinj
    simpa using this
  have hrange : LinearMap.range (π.domRestrict S) =
      Submodule.span K (Set.range (fun i : {i // i ≠ r} =>
        (fun j : {i // i ≠ r} => M i j.1))) := by
    rw [LinearMap.range_domRestrict, hS, Submodule.map_span, ← Set.range_comp]
    rfl
  have hrk : (pm M r).rank =
      Module.finrank K (LinearMap.range (π.domRestrict S)) := by
    rw [hrange, Matrix.rank_eq_finrank_span_row]
    rfl
  have hcard := card_ne r
  omega

/-- some row can be removed so that the remaining rows are independent -/
lemma exists_row_indep (M : Matrix ι ι K) (n : ℕ) (hc : Fintype.card ι = n + 1) (hr : n ≤ M.rank) :
    ∃ r : ι, LinearIndependent K (fun i : {i // i ≠ r} => M i) := by
  classical
  have hn0 : Nonempty ι := Fintype.card_pos_iff.1 (by omega)
  by_cases hli : LinearIndependent K (fun i : ι => M i)
  · obtain ⟨r⟩ := hn0
    exact ⟨r, hli.comp _ Subtype.val_injective⟩
  · rw [Fintype.not_linearIndependent_iff] at hli
    obtain ⟨g, hg, r, hgr⟩ := hli
    refine ⟨r, ?_⟩
    have hmem : M r ∈ Submodule.span K (Set.range (fun i : {i // i ≠ r} => M i)) := by
      have h1 : g r • M r = - ∑ i ∈ Finset.univ.erase r, g i • M i := by
        have := Finset.add_sum_erase Finset.univ (fun i => g i • M i) (Finset.mem_univ r)
        rw [hg] at this
        exact eq_neg_of_add_eq_zero_left this
      have h2 : M r = ∑ i ∈ Finset.univ.erase r, (-(g r)⁻¹ * g i) • M i := by
        have : M r = (g r)⁻¹ • (g r • M r) := by rw [smul_smul, inv_mul_cancel₀ hgr, one_smul]
        rw [this, h1, smul_neg, Finset.smul_sum, ← Finset.sum_neg_distrib]
        refine Finset.sum_congr rfl fun i _ => ?_
        rw [smul_smul, neg_mul, neg_smul]
      rw [h2]
      refine Submodule.sum_mem _ fun i hi => ?_
      refine Submodule.smul_mem _ _ (Submodule.subset_span ⟨⟨i, (Finset.mem_erase.1 hi).1⟩, rfl⟩)
    have hspan : Submodule.span K (Set.range (fun i : ι => M i)) =
        Submodule.span K (Set.range (fun i : {i // i ≠ r} => M i)) := by
      apply le_antisymm
      · rw [Submodule.span_le]
        rintro _ ⟨i, rfl⟩
        by_cases h : i = r
        · subst h; exact hmem
        · exact Submodule.subset_span ⟨⟨i, h⟩, rfl⟩
      · exact Submodule.span_mono (by rintro _ ⟨i, rfl⟩; exact ⟨i.1, rfl⟩)
    rw [linearIndependent_iff_card_eq_finrank_span]
    have hrk : Module.finrank K (Submodule.span K (Set.range (fun i : ι => M i))) = M.rank := by
      rw [Matrix.rank_eq_finrank_span_row]; rfl
    have hcard := card_ne r
    have h3 : Set.finrank K (Set.range (fun i : {i // i ≠ r} => M i)) = M.rank := by
      rw [Set.finrank, ← hspan, hrk]
    have h4 := finrank_range_le_card (R := K) (fun i : {i // i ≠ r} => M i)
    have h5 : Set.finrank K (Set.range (fun i : {i // i ≠ r} => M i)) ≤ Fintype.card {i // i ≠ r} := h4
    omega

end Exist

universe u

/-- THE ORDERING LEMMA (LINEAR56 §3, GL): every matrix of rank >= n-1 has a simultaneous ordering of rows
and columns with the `OrdProp` (in particular every invertible matrix). -/
theorem exists_ordering : ∀ (n : ℕ) (ι : Type u) [Fintype ι] [DecidableEq ι], Fintype.card ι = n →
    ∀ (M : Matrix ι ι K), n ≤ M.rank + 1 → ∃ e : Fin n ≃ ι, OrdProp (M.submatrix e e) := by
  intro n
  induction n with
  | zero =>
    intro ι _ _ hc M _
    refine ⟨(Fintype.equivFinOfCardEq hc).symm, ?_⟩
    intro k; exact absurd k.2 (Nat.not_lt_zero _)
  | succ n ih =>
    intro ι _ _ hc M hr
    obtain ⟨r, hind⟩ := exists_row_indep M n hc (by omega)
    have h1 := rank_principal_ge M r hind
    have h2 := card_ne r
    have hc' : Fintype.card {i // i ≠ r} = n := by omega
    obtain ⟨e', he'⟩ := ih {i // i ≠ r} hc' (pm M r) (by omega)
    let e : Fin (n + 1) ≃ ι :=
      finSuccEquivLast.trans ((Equiv.optionCongr e').trans (Equiv.optionSubtypeNe r))
    have hel : e (Fin.last n) = r := by simp [e]
    have hec : ∀ j : Fin n, e (Fin.castSucc j) = (e' j).1 := by intro j; simp [e]
    refine ⟨e, ?_⟩
    intro k v hv0 hv
    have hvl : v (Fin.last n) = 0 := hv0 _ (Fin.le_last _)
    have hsum : ∀ a : Fin (n + 1), (v ᵥ* (M.submatrix e e)) a =
        ∑ j : Fin n, v (Fin.castSucc j) * M (e' j).1 (e a) := by
      intro a
      simp only [Matrix.vecMul, dotProduct, Matrix.submatrix_apply]
      rw [Fin.sum_univ_castSucc, hvl, zero_mul, add_zero]
      simp only [hec]
    induction k using Fin.lastCases with
    | last =>
      have hg : ∀ g : {i // i ≠ r} → K, ∑ i, g i • M i = 0 → ∀ i, g i = 0 :=
        Fintype.linearIndependent_iff.1 hind
      have := hg (fun i => v (Fin.castSucc (e'.symm i))) (by
        funext c
        have h := hv (e.symm c) (Fin.le_last _)
        rw [hsum] at h
        simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
        rw [← Fintype.sum_equiv e' (fun j => v (Fin.castSucc j) * M (e' j).1 c)
          (fun i => v (Fin.castSucc (e'.symm i)) * M i.1 c) (by intro j; simp)]
        simpa using h)
      funext j
      refine Fin.lastCases ?_ (fun j => ?_) j
      · exact hvl
      · simpa using this (e' j)
    | cast k' =>
      have hv0' : ∀ j, k' ≤ j → v (Fin.castSucc j) = 0 := fun j hj =>
        hv0 _ (Fin.castSucc_le_castSucc_iff.2 hj)
      have key := he' k' (fun j => v (Fin.castSucc j)) hv0' (by
        intro i hi
        have h := hv (Fin.castSucc i) (Fin.castSucc_le_castSucc_iff.2 hi)
        rw [hsum] at h
        simpa [Matrix.vecMul, dotProduct, pm, Matrix.submatrix_apply, hec] using h)
      funext j
      refine Fin.lastCases ?_ (fun j => ?_) j
      · exact hvl
      · simpa using congrFun key j

/-- In an `OrdProp` order there is no nonzero symmetric zero-diagonal N with N*M strictly upper
triangular (entries on and below the diagonal vanish).  [LINEAR56 §3, downward induction.] -/
theorem no_alt_upper {n : ℕ} {M : Matrix (Fin n) (Fin n) K} (hM : OrdProp M)
    (N : Matrix (Fin n) (Fin n) K) (hs : ∀ i j, N i j = N j i) (hd : ∀ i, N i i = 0)
    (hu : ∀ j k : Fin n, k ≤ j → (N * M) j k = 0) : N = 0 := by
  have key : ∀ d : ℕ, ∀ k : Fin n, n - k.val ≤ d → ∀ j, N k j = 0 := by
    intro d
    induction d with
    | zero => intro k hk; exact absurd k.2 (by omega)
    | succ d ih =>
      intro k hk
      have hrow : (fun j => N k j) = 0 := by
        apply hM k
        · intro j hj
          rcases hj.lt_or_eq with h | h
          · rw [hs]; exact ih j (by have : (k : ℕ) < j := h; omega) k
          · rw [← h]; exact hd k
        · intro i hi
          have := hu k i hi
          simpa [Matrix.mul_apply, Matrix.vecMul, dotProduct] using this
      intro j; exact congrFun hrow j
  ext i j
  exact key n i (by omega) j

end LinOrd

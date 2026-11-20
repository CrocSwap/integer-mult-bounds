import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.BilinearForm
import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
/-!
PRICELEMMA (lane LEAN-PRICE).  Kernel-only: no sorry / native_decide / new axioms.
Abstract F2^n (here any field K, dot product), finite label sets D, S with labels lD, lS.
Q[D,S] = Gram matrix (lD t . lS s).  M0 = span lD, A0 = span lS, perp = dot-orthogonal.
(1) rank Q[D,S] = dim M0 - dim (M0 ∩ perp A0), and
    EXACT PRICE LEMMA: rank = min {dim M - dim K : M0 ≤ M, K ≤ M, K ≤ perp A0}  (IsLeast).
(2) PAIR FORM: rank = min {dim M + dim N - n : M0 ≤ M, A0 ≤ N, perp N ≤ M}  (IsLeast).
(3) non-vacuity: n=3 identity case (rank 3) and a self-orthogonal label (rank 0 < dim M).
-/
open Matrix Module Submodule

namespace PriceLemma

variable {K : Type*} [Field K] {n : ℕ}

/-- the dot-product bilinear form on K^n -/
noncomputable def dotF (K : Type*) [Field K] (n : ℕ) : LinearMap.BilinForm K (Fin n → K) :=
  Matrix.toBilin' (1 : Matrix (Fin n) (Fin n) K)

lemma dotF_apply (x y : Fin n → K) : dotF K n x y = x ⬝ᵥ y := by
  simp [dotF, Matrix.toBilin'_apply']

lemma dotF_nd : (dotF K n).Nondegenerate :=
  (Matrix.nondegenerate_toBilin'_iff).2 (Matrix.nondegenerate_iff_det_ne_zero.2 (by simp))

lemma dotF_refl : (dotF K n).IsRefl := by
  intro x y h
  rw [dotF_apply] at *
  rwa [dotProduct_comm]

/-- orthogonal complement -/
noncomputable def perp (N : Submodule K (Fin n → K)) : Submodule K (Fin n → K) :=
  (dotF K n).orthogonal N

lemma mem_perp {N : Submodule K (Fin n → K)} {x : Fin n → K} :
    x ∈ perp N ↔ ∀ y ∈ N, y ⬝ᵥ x = 0 := by
  unfold perp
  simp [LinearMap.BilinForm.orthogonal, Submodule.mem_orthogonalBilin_iff,
    LinearMap.BilinForm.IsOrtho, dotF_apply]

lemma finrank_perp (N : Submodule K (Fin n → K)) :
    finrank K (perp N) = n - finrank K N := by
  have := LinearMap.BilinForm.finrank_orthogonal (dotF_nd (K := K) (n := n)) N
  rw [Module.finrank_fin_fun] at this
  exact this

lemma perp_perp (N : Submodule K (Fin n → K)) : perp (perp N) = N :=
  LinearMap.BilinForm.orthogonal_orthogonal dotF_nd dotF_refl N

lemma perp_anti {N N' : Submodule K (Fin n → K)} (h : N ≤ N') : perp N' ≤ perp N := by
  intro x hx
  rw [mem_perp] at hx ⊢
  exact fun y hy => hx y (h hy)

lemma le_perp_iff {A B : Submodule K (Fin n → K)} : A ≤ perp B ↔ B ≤ perp A := by
  constructor <;> intro h x hx <;> rw [mem_perp] <;> intro y hy
  · rw [dotProduct_comm]; exact (mem_perp.1 (h hy)) x hx
  · rw [dotProduct_comm]; exact (mem_perp.1 (h hy)) x hx

lemma perp_span (ι : Type*) (l : ι → Fin n → K) (x : Fin n → K) :
    x ∈ perp (span K (Set.range l)) ↔ ∀ t, l t ⬝ᵥ x = 0 := by
  rw [mem_perp]
  constructor
  · intro h t; exact h _ (subset_span ⟨t, rfl⟩)
  · intro h y hy
    induction hy using Submodule.span_induction with
    | mem z hz => obtain ⟨t, rfl⟩ := hz; exact h t
    | zero => simp
    | add a b _ _ ha hb => simp [add_dotProduct, ha, hb]
    | smul c a _ ha => simp [smul_dotProduct, ha]

section Gram
variable {ιD ιS : Type*} [Fintype ιD] [Fintype ιS]

/-- the label Gram matrix Q[D,S] -/
def gram (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) : Matrix ιD ιS K :=
  Matrix.of fun t s => lD t ⬝ᵥ lS s

/-- map x ↦ (lD t . x)_t -/
def phi (lD : ιD → Fin n → K) : (Fin n → K) →ₗ[K] (ιD → K) where
  toFun x t := lD t ⬝ᵥ x
  map_add' x y := by ext t; simp [dotProduct_add]
  map_smul' c x := by ext t; simp [dotProduct_smul]

lemma gram_mulVecLin (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    (gram lD lS).mulVecLin = (phi lD) ∘ₗ (Fintype.linearCombination K lS) := by
  ext c t
  simp [gram, phi, Fintype.linearCombination_apply, Matrix.mulVec, dotProduct,
    Finset.sum_apply, Finset.mul_sum, mul_comm, mul_left_comm]
  exact Finset.sum_comm

lemma rank_gram_A (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    (gram lD lS).rank =
      finrank K (span K (Set.range lS)) -
        finrank K (span K (Set.range lS) ⊓ perp (span K (Set.range lD)) : Submodule K _) := by
  set A := span K (Set.range lS)
  have hr : LinearMap.range (gram lD lS).mulVecLin = A.map (phi lD) := by
    rw [gram_mulVecLin, LinearMap.range_comp, Fintype.range_linearCombination]
  have hker : LinearMap.ker (phi lD) = perp (span K (Set.range lD)) := by
    ext x
    rw [perp_span ιD lD x, LinearMap.mem_ker]
    constructor
    · intro h t; exact congrFun h t
    · intro h; ext t; exact h t
  have key := LinearMap.finrank_range_add_finrank_ker ((phi lD).domRestrict A)
  rw [LinearMap.range_domRestrict] at key
  have h2 : finrank K (LinearMap.ker ((phi lD).domRestrict A)) =
      finrank K (A ⊓ perp (span K (Set.range lD)) : Submodule K _) := by
    have e : LinearMap.ker ((phi lD).domRestrict A) =
        (LinearMap.ker (phi lD)).comap A.subtype := LinearMap.ker_comp _ _
    rw [e, ← finrank_map_subtype_eq A, Submodule.map_comap_subtype, hker]
  unfold Matrix.rank
  rw [hr]
  omega


lemma rank_gram_D (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    (gram lD lS).rank =
      finrank K (span K (Set.range lD)) -
        finrank K (span K (Set.range lD) ⊓ perp (span K (Set.range lS)) : Submodule K _) := by
  have h : gram lS lD = (gram lD lS)ᵀ := by
    ext s t; simp [gram, dotProduct_comm]
  rw [← Matrix.rank_transpose, ← h]
  exact rank_gram_A lS lD

lemma finrank_le_n (N : Submodule K (Fin n → K)) : finrank K N ≤ n := by
  simpa using Submodule.finrank_le N

/-- feasible (M,K) values of the exact price lemma -/
def PriceSet (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) : Set ℕ :=
  {v | ∃ M L : Submodule K (Fin n → K), span K (Set.range lD) ≤ M ∧ L ≤ M ∧
      L ≤ perp (span K (Set.range lS)) ∧ v = finrank K M - finrank K L}

/-- monotonicity: dim M - dim (M ∩ P) grows with M -/
lemma mono_price (M0 M P : Submodule K (Fin n → K)) (h : M0 ≤ M) :
    finrank K M0 - finrank K (M0 ⊓ P : Submodule K _) ≤
      finrank K M - finrank K (M ⊓ P : Submodule K _) := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq M0 (M ⊓ P)
  have h2 : M0 ⊓ (M ⊓ P) = M0 ⊓ P := by
    rw [← inf_assoc, inf_eq_left.2 h]
  have h3 : finrank K ↥(M0 ⊔ (M ⊓ P)) ≤ finrank K M :=
    Submodule.finrank_mono (sup_le h inf_le_left)
  have h4 : finrank K ↥(M0 ⊓ P) ≤ finrank K M0 := Submodule.finrank_mono inf_le_left
  rw [h2] at h1
  omega

/-- EXACT PRICE LEMMA: rank Q[D,S] is the least value of dim M - dim L over
    M ⊇ span lD, L ≤ M, L ⊥ lS. -/
theorem exact_price (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    IsLeast (PriceSet lD lS) (gram lD lS).rank := by
  constructor
  · exact ⟨_, span K (Set.range lD) ⊓ perp (span K (Set.range lS)), le_rfl, inf_le_left,
      inf_le_right, rank_gram_D lD lS⟩
  · rintro v ⟨M, L, hM, hL, hLP, rfl⟩
    rw [rank_gram_D lD lS]
    have h1 : finrank K L ≤ finrank K (M ⊓ perp (span K (Set.range lS)) : Submodule K _) :=
      Submodule.finrank_mono (le_inf hL hLP)
    have h2 := mono_price (span K (Set.range lD)) M (perp (span K (Set.range lS))) hM
    omega

/-- feasible (M,N) values of the pair form -/
def PairSet (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) : Set ℕ :=
  {v | ∃ M N : Submodule K (Fin n → K), span K (Set.range lD) ≤ M ∧
      span K (Set.range lS) ≤ N ∧ perp N ≤ M ∧ v = finrank K M + finrank K N - n}

/-- PAIR FORM: rank Q[D,S] = min over pairs (M,N), lD ∈ M, lS ∈ N, N^⊥ ≤ M of
    dim M + dim N - n. -/
theorem pair_price (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    IsLeast (PairSet lD lS) (gram lD lS).rank := by
  have hM0 := finrank_le_n (span K (Set.range lD))
  constructor
  · refine ⟨span K (Set.range lD), perp (span K (Set.range lD) ⊓ perp (span K (Set.range lS))),
      le_rfl, le_perp_iff.2 inf_le_right, by rw [perp_perp]; exact inf_le_left, ?_⟩
    rw [rank_gram_D lD lS, finrank_perp]
    have := finrank_le_n (span K (Set.range lD) ⊓ perp (span K (Set.range lS)) : Submodule K _)
    have h : finrank K (span K (Set.range lD) ⊓ perp (span K (Set.range lS)) : Submodule K _) ≤
      finrank K (span K (Set.range lD)) := Submodule.finrank_mono inf_le_left
    omega
  · rintro v ⟨M, N, hM, hN, hNM, rfl⟩
    obtain ⟨_, hlow⟩ := exact_price lD lS
    have hmem : finrank K M - finrank K (perp N) ∈ PriceSet lD lS :=
      ⟨M, perp N, hM, hNM, perp_anti hN |> fun h => by
        rw [← le_perp_iff] at *; exact (le_perp_iff.2 (by simpa [perp_perp] using le_perp_iff.1 h)), rfl⟩
    have := hlow hmem
    rw [finrank_perp] at this
    have := finrank_le_n N
    have h : finrank K (perp N) ≤ finrank K M := Submodule.finrank_mono hNM
    rw [finrank_perp] at h
    omega

end Gram

/-! Non-vacuity, n = 3 over F2. -/
section Examples

/-- unit labels: Q = identity, price 3 -/
example : IsLeast (PriceSet (K := ZMod 2) (n := 3) (fun i : Fin 3 => Pi.single i 1)
    (fun i : Fin 3 => Pi.single i 1)) 3 := by
  have h : gram (K := ZMod 2) (n := 3) (fun i : Fin 3 => Pi.single i 1)
      (fun i : Fin 3 => Pi.single i 1) = 1 := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [gram, dotProduct, Fin.sum_univ_three, Pi.single_apply]
  have := exact_price (K := ZMod 2) (n := 3) (fun i : Fin 3 => Pi.single i 1)
      (fun i : Fin 3 => Pi.single i 1)
  rwa [h, Matrix.rank_one] at this

/-- self-orthogonal label l = (1,1,0): Q = [0] has rank 0 although dim span l = 1 -/
example : IsLeast (PriceSet (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
    (fun _ : Unit => ![1, 1, 0])) 0 ∧
    finrank (ZMod 2) (span (ZMod 2) (Set.range (fun _ : Unit => (![1, 1, 0] : Fin 3 → ZMod 2)))) = 1 := by
  have h : gram (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
      (fun _ : Unit => ![1, 1, 0]) = 0 := by
    ext i j
    simp [gram, dotProduct, Fin.sum_univ_three]
    decide
  refine ⟨?_, ?_⟩
  · have := exact_price (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
      (fun _ : Unit => ![1, 1, 0])
    rwa [h, Matrix.rank_zero] at this
  · rw [Set.range_const]
    apply finrank_span_singleton
    intro h0
    have := congrFun h0 0
    simp at this

/-- pair form on the same example: price 0 via (M,N) with dim M + dim N = 3 -/
example : IsLeast (PairSet (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
    (fun _ : Unit => ![1, 1, 0])) 0 := by
  have h : gram (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
      (fun _ : Unit => ![1, 1, 0]) = 0 := by
    ext i j
    simp [gram, dotProduct, Fin.sum_univ_three]
    decide
  have := pair_price (K := ZMod 2) (n := 3) (fun _ : Unit => ![1, 1, 0])
      (fun _ : Unit => ![1, 1, 0])
  rwa [h, Matrix.rank_zero] at this

end Examples

#print axioms exact_price
#print axioms pair_price
#print axioms rank_gram_D

end PriceLemma

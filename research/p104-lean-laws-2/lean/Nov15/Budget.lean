/-
SPECBREAK R19 formalization (Nov 15/16 lane LEAN-SYL).

(1) Product formula  ρ_{m-1} ⋯ ρ_0 = I − X N⁻¹ Yᵀ,  ρ_k = I − x_k y_kᵀ,
    N = I + strictLower(Yᵀ X)  (N_ij = y_i ⬝ x_j for i > j), N unit lower-triangular.
(2) SYL (Sylvester) rank bound  rk X + rk Y ≤ m + rank(I − P), and the diagonal ±1 form
    rk X + rk Y ≤ m + #{flipped coordinates}  (char ≠ 2).
(3) Parity: det(I − c·x yᵀ) = 1 − c·(y ⬝ x); a product of factors with y ⬝ x = 0 has det 1,
    so −I_n is such a product only if n is even (char ≠ 2).
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.List.OfFn
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv

open Matrix

set_option backward.isDefEq.respectTransparency false

namespace SYL

variable {K : Type*} [Field K] {n : ℕ}

/-! ## (1) Product formula -/

/-- `wordProd x y k = ρ_{k-1} ⋯ ρ_1 ρ_0` with `ρ_j = 1 − x_j y_jᵀ` (later factors on the left). -/
def wordProd (x y : ℕ → Fin n → K) : ℕ → Matrix (Fin n) (Fin n) K
  | 0 => 1
  | k + 1 => (1 - vecMulVec (x k) (y k)) * wordProd x y k

/-- `X = [x_0 … x_{m-1}]` (columns). -/
def Xmat (x : ℕ → Fin n → K) (m : ℕ) : Matrix (Fin n) (Fin m) K := Matrix.of fun i j => x j i

/-- `N = 1 + strictLower(Yᵀ X)`. -/
def Nmat (x y : ℕ → Fin n → K) (m : ℕ) : Matrix (Fin m) (Fin m) K :=
  1 + Matrix.of fun i j => if j < i then ((Xmat y m)ᵀ * Xmat x m) i j else 0

/-- auxiliary rows `z_k = y_kᵀ P_k`. -/
def zrow (x y : ℕ → Fin n → K) (k : ℕ) : Fin n → K := y k ᵥ* wordProd x y k

lemma wordProd_eq_sum (x y : ℕ → Fin n → K) (m : ℕ) :
    wordProd x y m = 1 - ∑ k ∈ Finset.range m, vecMulVec (x k) (zrow x y k) := by
  induction m with
  | zero => simp [wordProd]
  | succ m ih =>
    have h : vecMulVec (x m) (y m ᵥ* wordProd x y m) = vecMulVec (x m) (zrow x y m) := rfl
    rw [wordProd, Matrix.sub_mul, Matrix.one_mul, vecMulVec_mul, h, Finset.sum_range_succ, ih]
    abel

lemma zrow_eq (x y : ℕ → Fin n → K) (k : ℕ) :
    zrow x y k = y k - ∑ l ∈ Finset.range k, (y k ⬝ᵥ x l) • zrow x y l := by
  conv_lhs => rw [zrow, wordProd_eq_sum]
  rw [vecMul_sub, vecMul_one, vecMul_sum]
  simp only [vecMul_vecMulVec]

/-- `Z` with rows `z_k`. -/
def Zmat (x y : ℕ → Fin n → K) (m : ℕ) : Matrix (Fin m) (Fin n) K :=
  Matrix.of fun k j => zrow x y k j

lemma X_mul_Z (x y : ℕ → Fin n → K) (m : ℕ) :
    Xmat x m * Zmat x y m = ∑ k ∈ Finset.range m, vecMulVec (x k) (zrow x y k) := by
  ext i j
  simp only [mul_apply, Matrix.sum_apply, Xmat, Zmat, of_apply, vecMulVec_apply]
  exact Fin.sum_univ_eq_sum_range (fun k => x k i * zrow x y k j) m

lemma N_mul_Z (x y : ℕ → Fin n → K) (m : ℕ) :
    Nmat x y m * Zmat x y m = (Xmat y m)ᵀ := by
  ext k j
  rw [Nmat, Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, mul_apply]
  simp only [Zmat, Xmat, of_apply, transpose_apply, mul_apply]
  rw [zrow_eq, Pi.sub_apply, Finset.sum_apply]
  have hsum : ∑ l : Fin m, (if l < k then ∑ i : Fin n, y k i * x l i else 0) * zrow x y l j
      = ∑ l ∈ Finset.range k, ((y k ⬝ᵥ x l) • zrow x y l) j := by
    have h1 : ∑ l : Fin m, (if l < k then ∑ i : Fin n, y k i * x l i else 0) * zrow x y l j
        = ∑ l ∈ Finset.range m, (if l < (k : ℕ) then (y k ⬝ᵥ x l) * zrow x y l j else 0) := by
      rw [← Fin.sum_univ_eq_sum_range (fun l => if l < (k : ℕ) then
        (y k ⬝ᵥ x l) * zrow x y l j else 0) m]
      refine Finset.sum_congr rfl fun l _ => ?_
      by_cases hl : l < k
      · rw [if_pos hl, if_pos (Fin.lt_def.mp hl)]; rfl
      · rw [if_neg hl, if_neg (fun h => hl (Fin.lt_def.mpr h)), zero_mul]
    rw [h1, ← Finset.sum_filter]
    have hf : (Finset.range m).filter (fun l => l < (k : ℕ)) = Finset.range k := by
      ext l; simp only [Finset.mem_filter, Finset.mem_range]
      constructor
      · exact fun h => h.2
      · exact fun h => ⟨lt_trans h k.isLt, h⟩
    rw [hf]
    refine Finset.sum_congr rfl fun l _ => ?_
    simp [smul_eq_mul]
  rw [hsum]
  ring

lemma Nmat_lowerTriangular (x y : ℕ → Fin n → K) (m : ℕ) :
    (Nmat x y m).BlockTriangular OrderDual.toDual := by
  intro i j hij
  have hij' : i < j := hij
  simp only [Nmat, Matrix.add_apply, of_apply]
  rw [one_apply_ne (ne_of_lt hij'), if_neg (not_lt.mpr hij'.le), add_zero]

theorem det_Nmat (x y : ℕ → Fin n → K) (m : ℕ) : (Nmat x y m).det = 1 := by
  rw [det_of_lowerTriangular _ (Nmat_lowerTriangular x y m)]
  refine Finset.prod_eq_one fun i _ => ?_
  simp [Nmat]

/-- **Product formula** (R19 §1): `ρ_{m-1} ⋯ ρ_0 = I − X N⁻¹ Yᵀ`. -/
theorem product_formula (x y : ℕ → Fin n → K) (m : ℕ) :
    wordProd x y m = 1 - Xmat x m * (Nmat x y m)⁻¹ * (Xmat y m)ᵀ := by
  have hu : IsUnit (Nmat x y m).det := by rw [det_Nmat]; exact isUnit_one
  have hZ : Zmat x y m = (Nmat x y m)⁻¹ * (Xmat y m)ᵀ := by
    rw [← N_mul_Z x y m, nonsing_inv_mul_cancel_left _ _ hu]
  rw [Matrix.mul_assoc, ← hZ, X_mul_Z, wordProd_eq_sum]

/-- The recursive product is the ordered list product `ρ_{m-1} * ⋯ * ρ_0`. -/
lemma wordProd_eq_listProd (x y : ℕ → Fin n → K) (m : ℕ) :
    wordProd x y m =
      (List.ofFn fun k : Fin m => (1 - vecMulVec (x k) (y k) : Matrix (Fin n) (Fin n) K)).reverse.prod := by
  induction m with
  | zero => simp [wordProd]
  | succ m ih =>
    rw [List.ofFn_succ', List.concat_eq_append, List.reverse_append, List.reverse_singleton,
      List.singleton_append, List.prod_cons, wordProd, ih]
    rfl

/-! ## (2) Sylvester rank inequality and Theorem SYL -/

/-- **Sylvester's rank inequality**: `rk A + rk B ≤ k + rk (A B)` for `A : n×k`, `B : k×p`. -/
theorem sylvester {a b c : Type*} [Fintype a] [Fintype b] [Fintype c] [DecidableEq b]
    (A : Matrix a b K) (B : Matrix b c K) :
    A.rank + B.rank ≤ Fintype.card b + (A * B).rank := by
  classical
  set fA := A.mulVecLin
  set p := LinearMap.range B.mulVecLin
  set g := fA.domRestrict p
  have hrange : LinearMap.range g = LinearMap.range (A * B).mulVecLin := by
    rw [LinearMap.range_domRestrict, mulVecLin_mul, LinearMap.range_comp]
  have hrn := LinearMap.finrank_range_add_finrank_ker g
  have hrnA := LinearMap.finrank_range_add_finrank_ker fA
  have hker : Module.finrank K (LinearMap.ker g) ≤ Module.finrank K (LinearMap.ker fA) := by
    rw [LinearMap.ker_domRestrict]
    rw [← Submodule.finrank_map_subtype_eq p, Submodule.map_comap_subtype]
    exact Submodule.finrank_mono inf_le_right
  have hcard : Module.finrank K (b → K) = Fintype.card b := Module.finrank_fintype_fun_eq_card K
  have hAB : (A * B).rank = Module.finrank K (LinearMap.range g) := by
    rw [hrange]; rfl
  have hB : B.rank = Module.finrank K p := rfl
  have hA : A.rank = Module.finrank K (LinearMap.range fA) := rfl
  omega

/-- **Theorem SYL, core inequality** (R19 §2): `rk X + rk Y ≤ m + rank (I − P)`,
i.e. `r ≥ rk X + rk Y − J` for the word `P = ρ_{m-1} ⋯ ρ_0` (any `y_k ⬝ x_k`). -/
theorem syl_rank (x y : ℕ → Fin n → K) (m : ℕ) :
    (Xmat x m).rank + (Xmat y m).rank ≤ m + (1 - wordProd x y m).rank := by
  have hu : IsUnit (Nmat x y m).det := by rw [det_Nmat]; exact isUnit_one
  have h := sylvester (Xmat x m) ((Nmat x y m)⁻¹ * (Xmat y m)ᵀ)
  have hu' : IsUnit ((Nmat x y m)⁻¹).det := by
    rw [det_nonsing_inv]; exact hu.ringInverse
  rw [rank_mul_eq_right_of_isUnit_det _ _ hu', rank_transpose, Fintype.card_fin] at h
  rw [product_formula, sub_sub_cancel, ← Matrix.mul_assoc] at *
  exact h

/-- rank of `P − 1` for a diagonal `±1` matrix is the number of `−1` entries (char ≠ 2). -/
lemma rank_diag_sub_one [DecidableEq K] (h2 : (2 : K) ≠ 0) (d : Fin n → K) (hd : ∀ i, d i = 1 ∨ d i = -1) :
    (1 - diagonal d).rank = (Finset.univ.filter fun i => d i = -1).card := by
  classical
  have : (1 - diagonal d : Matrix (Fin n) (Fin n) K) = diagonal (fun i => 1 - d i) := by
    rw [← diagonal_one, diagonal_sub]
  rw [this, rank_diagonal, Fintype.card_subtype]
  congr 1
  refine Finset.filter_congr fun i _ => ?_
  rcases hd i with h | h
  · rw [h]; simp only [sub_self, ne_eq, not_true_eq_false, false_iff]
    intro h'
    apply h2
    have : (2 : K) = 1 - (-1) := by ring
    rw [this, ← h', sub_self]
  · rw [h]; simp only [ne_eq, iff_true]
    intro h'; apply h2; rw [← h']; ring

/-- **Theorem SYL, diagonal form**: if the word equals `D = diag(±1)` flipping `r` coordinates
then `rk X + rk Y ≤ J + r` (char ≠ 2). -/
theorem syl_diag [DecidableEq K] (h2 : (2 : K) ≠ 0) (x y : ℕ → Fin n → K) (m : ℕ) (d : Fin n → K)
    (hd : ∀ i, d i = 1 ∨ d i = -1) (hP : wordProd x y m = diagonal d) :
    (Xmat x m).rank + (Xmat y m).rank ≤ m + (Finset.univ.filter fun i => d i = -1).card := by
  have := syl_rank x y m
  rwa [hP, rank_diag_sub_one h2 d hd] at this

/-- **P\* corollary** (R19 §3): a word equal to the identity has `rk X + rk Y ≤ J`. -/
theorem syl_identity (x y : ℕ → Fin n → K) (m : ℕ) (hP : wordProd x y m = 1) :
    (Xmat x m).rank + (Xmat y m).rank ≤ m := by
  have := syl_rank x y m
  rw [hP, sub_self, rank_zero] at this
  simpa using this

/-! ## (3) Parity lemma -/

/-- Matrix determinant lemma for a rank-one update: `det (1 − c·x yᵀ) = 1 − c·(y ⬝ x)`. -/
theorem det_one_sub_smul_vecMulVec (c : K) (x y : Fin n → K) :
    (1 - c • vecMulVec x y : Matrix (Fin n) (Fin n) K).det = 1 - c * (y ⬝ᵥ x) := by
  have : (1 - c • vecMulVec x y : Matrix (Fin n) (Fin n) K)
      = 1 + replicateCol (Fin 1) (-(c • x)) * replicateRow (Fin 1) y := by
    rw [← vecMulVec_eq, sub_eq_add_neg]
    congr 1
    ext i j
    simp [vecMulVec_apply, mul_assoc]
  rw [this, det_one_add_replicateCol_mul_replicateRow, dotProduct_neg, dotProduct_smul,
    smul_eq_mul, sub_eq_add_neg]

/-- `det (I − 2 x yᵀ) = 1` when `y ⬝ x = 0` (isotropic unit). -/
theorem det_unit (x y : Fin n → K) (h : y ⬝ᵥ x = 0) :
    (1 - (2 : K) • vecMulVec x y : Matrix (Fin n) (Fin n) K).det = 1 := by
  rw [det_one_sub_smul_vecMulVec, h, mul_zero, sub_zero]

/-- A product of factors `1 − c·x yᵀ` with `y ⬝ x = 0` has determinant 1. -/
theorem det_prod_units (L : List (K × (Fin n → K) × (Fin n → K)))
    (hL : ∀ t ∈ L, t.2.2 ⬝ᵥ t.2.1 = 0) :
    (L.map fun t => (1 - t.1 • vecMulVec t.2.1 t.2.2 : Matrix (Fin n) (Fin n) K)).prod.det = 1 := by
  induction L with
  | nil => simp
  | cons t L ih =>
    rw [List.map_cons, List.prod_cons, det_mul, det_one_sub_smul_vecMulVec,
      hL t List.mem_cons_self, mul_zero, sub_zero, one_mul]
    exact ih fun s hs => hL s (List.mem_cons_of_mem t hs)

/-- **Parity lemma** (GAPSING G1): if `−I_n` is a product of factors `1 − c·x yᵀ` with `y ⬝ x = 0`
(e.g. `c = 2`), then `n` is even (char ≠ 2). -/
theorem parity (h2 : (2 : K) ≠ 0) (L : List (K × (Fin n → K) × (Fin n → K)))
    (hL : ∀ t ∈ L, t.2.2 ⬝ᵥ t.2.1 = 0)
    (hprod : (L.map fun t => (1 - t.1 • vecMulVec t.2.1 t.2.2 : Matrix (Fin n) (Fin n) K)).prod
      = -1) :
    Even n := by
  have hdet := det_prod_units L hL
  rw [hprod, det_neg, det_one, mul_one, Fintype.card_fin] at hdet
  have hne : (-1 : K) ≠ 1 := by
    intro h; apply h2
    have : (2 : K) = 1 - (-1) := by ring
    rw [this, h, sub_self]
  exact (neg_one_pow_eq_one_iff_even hne).mp hdet

end SYL


/-! # BUDGET (Nov 16): caller-tree budget closures of BIG/BRIDGETREE (AUDIT-C: SOUND / SOUND WITH FIX).
The block above is a verbatim copy of `Nov15/SYL.lean` (product formula). -/

namespace BUDGET
open SYL

variable {K : Type*} [Field K] {n : ℕ}

/-! ## B1(a) bookkeeping -/

/-- **Budget identity** (B1(a), arithmetic part): with `N = Σ N_i` units, roles partitioned as
`n = Σ |P_i| + |S|`, `ρ := N − n = Σ β_i − |S|` where `β_i = N_i − |P_i|`. -/
theorem budget_identity {c : ℕ} (Nu Pc : Fin c → ℕ) (Scard nTot NTot : ℕ)
    (hN : NTot = ∑ i, Nu i) (hn : nTot = ∑ i, Pc i + Scard) :
    (NTot : ℤ) - nTot = ∑ i, ((Nu i : ℤ) - Pc i) - Scard := by
  subst hN hn
  push_cast
  rw [Finset.sum_sub_distrib]
  ring

lemma prod_fixes (L : List (Matrix (Fin n) (Fin n) K)) (v : Fin n → K)
    (h : ∀ M ∈ L, M *ᵥ v = v) : L.prod *ᵥ v = v := by
  induction L with
  | nil => simp
  | cons M L ih =>
    rw [List.prod_cons, ← mulVec_mulVec, ih (fun M' hM' => h M' (List.mem_cons_of_mem _ hM')),
      h M List.mem_cons_self]

/-- **B1(a) block step** (CALLERFAM L4, column form; AUDIT-C: "later pieces cannot cancel"):
total product `Q·M_i·Q'` = −I, the earlier pieces `Q'` and later pieces `Q` fix `e_j`
(`j ∈ P_i` lies outside their supports), the later pieces are invertible ⇒ `M_i e_j = −e_j`.
(The row form is the same statement for the transposed, reversed word.) -/
theorem piece_neg_on_private (Lbefore Lafter : List (Matrix (Fin n) (Fin n) K))
    (M : Matrix (Fin n) (Fin n) K) (v : Fin n → K)
    (htot : (Lafter.prod * M * Lbefore.prod) *ᵥ v = -v)
    (hb : ∀ M' ∈ Lbefore, M' *ᵥ v = v) (ha : ∀ M' ∈ Lafter, M' *ᵥ v = v)
    (hinv : IsUnit (Lafter.prod).det) : M *ᵥ v = -v := by
  have hQ' := prod_fixes Lbefore v hb
  have hQ := prod_fixes Lafter v ha
  rw [← mulVec_mulVec, hQ', ← mulVec_mulVec] at htot
  have h0 : Lafter.prod *ᵥ (M *ᵥ v + v) = 0 := by
    rw [mulVec_add, htot, hQ, neg_add_cancel]
  have : M *ᵥ v + v = 0 := by
    have := congrArg (fun w => (Lafter.prod)⁻¹ *ᵥ w) h0
    simpa [mulVec_mulVec, nonsing_inv_mul _ hinv] using this
  exact eq_neg_of_add_eq_zero_left this

/-! ## B1(b) span bound β_i ≥ d_i ≥ 2 -/

/-- the column space of `1 − ρ_{m-1}⋯ρ_0` lies in the span of the `x_k` (product formula). -/
theorem range_one_sub_le_span (x y : ℕ → Fin n → K) (m : ℕ) :
    LinearMap.range (1 - wordProd x y m).mulVecLin ≤
      Submodule.span K (Set.range fun k : Fin m => x k) := by
  rw [product_formula, sub_sub_cancel, Matrix.mul_assoc]
  rintro _ ⟨v, rfl⟩
  simp only [mulVecLin_apply]
  rw [← mulVec_mulVec]
  set u := ((Nmat x y m)⁻¹ * (Xmat y m)ᵀ) *ᵥ v
  have : Xmat x m *ᵥ u = ∑ k : Fin m, u k • x k := by
    ext i; simp [mulVec, dotProduct, Xmat, Finset.sum_apply, mul_comm]
  rw [this]
  exact Submodule.sum_mem _ fun k _ => Submodule.smul_mem _ _ (Submodule.subset_span ⟨k, rfl⟩)

/-- private roles lie in `V_i`: if the piece product `M = ρ_{m-1}⋯ρ_0` has `M e_j = −e_j`,
then `e_j ∈ span{x_k}` (char ≠ 2). -/
theorem single_mem_span (h2 : (2 : K) ≠ 0) (x y : ℕ → Fin n → K) (m : ℕ) (j : Fin n)
    (hj : wordProd x y m *ᵥ Pi.single j 1 = -Pi.single j 1) :
    (Pi.single j 1 : Fin n → K) ∈ Submodule.span K (Set.range fun k : Fin m => x k) := by
  have hmem : (1 - wordProd x y m) *ᵥ Pi.single j 1 ∈ Submodule.span K (Set.range fun k : Fin m => x k) :=
    range_one_sub_le_span x y m ⟨_, rfl⟩
  rw [sub_mulVec, one_mulVec, hj, sub_neg_eq_add, ← two_smul K] at hmem
  have := Submodule.smul_mem _ (2 : K)⁻¹ hmem
  rwa [smul_smul, inv_mul_cancel₀ h2, one_smul] at this

/-- projection killing the coordinates in `P` (on `R^{P ∪ S}` this is the `S`-projection). -/
def projOff (P : Finset (Fin n)) : (Fin n → K) →ₗ[K] (Fin n → K) where
  toFun v := fun j => if j ∈ P then 0 else v j
  map_add' u v := by ext j; by_cases h : j ∈ P <;> simp [h]
  map_smul' a v := by ext j; by_cases h : j ∈ P <;> simp [h]

/-- **Span bound** (B1(b)): if `V` contains `e_j` for `j ∈ P`, then
`|P| + dim (proj_S V) ≤ dim V`. -/
theorem span_bound (V : Submodule K (Fin n → K)) (P : Finset (Fin n))
    (hP : ∀ j ∈ P, (Pi.single j 1 : Fin n → K) ∈ V) :
    P.card + Module.finrank K (V.map (projOff P)) ≤ Module.finrank K V := by
  classical
  set U := Submodule.span K (Set.range fun j : P => (Pi.single (j : Fin n) (1 : K) : Fin n → K))
  set E := V.map (projOff P)
  have hli : LinearIndependent K (fun j : P => (Pi.single (j : Fin n) (1 : K) : Fin n → K)) :=
    (LinearIndependent.comp (Pi.linearIndependent_single_one (Fin n) K) _ Subtype.val_injective)
  have hU : Module.finrank K U = P.card := by
    rw [finrank_span_eq_card hli, Fintype.card_coe]
  have hUV : U ≤ V := Submodule.span_le.mpr (by rintro _ ⟨j, rfl⟩; exact hP j j.2)
  have hEV : E ≤ V := by
    rintro _ ⟨v, hv, rfl⟩
    have : projOff P v = v - ∑ j ∈ P, v j • (Pi.single j (1 : K) : Fin n → K) := by
      ext i
      simp only [projOff, LinearMap.coe_mk, AddHom.coe_mk, Pi.sub_apply, Finset.sum_apply,
        Pi.smul_apply, Pi.single_apply, smul_eq_mul, mul_ite, mul_one, mul_zero,
        Finset.sum_ite_eq', ]
      by_cases h : i ∈ P <;> simp [h]
    rw [this]
    exact V.sub_mem hv (V.sum_mem fun j hj => V.smul_mem _ (hP j hj))
  have hdisj : U ⊓ E = ⊥ := by
    rw [eq_bot_iff]
    intro w ⟨hwU, hwE⟩
    have hU0 : ∀ i, i ∉ P → w i = 0 := by
      have : U ≤ {v : Fin n → K | ∀ i, i ∉ P → v i = 0} := by
        intro u hu
        induction hu using Submodule.span_induction with
        | mem u hu =>
          obtain ⟨j, rfl⟩ := hu
          intro i hi; simp [Pi.single_apply, show i ≠ j from fun h => hi (h ▸ j.2)]
        | zero => intro i _; rfl
        | add a b _ _ ha hb => intro i hi; simp [ha i hi, hb i hi]
        | smul a b _ hb => intro i hi; simp [hb i hi]
      exact this hwU
    obtain ⟨v, _, rfl⟩ := hwE
    rw [Submodule.mem_bot]
    ext i
    by_cases hi : i ∈ P
    · simp [projOff, hi]
    · exact hU0 i hi
  have hsum := Submodule.finrank_sup_add_finrank_inf_eq U E
  rw [hdisj, finrank_bot, add_zero, hU] at hsum
  have := Submodule.finrank_mono (sup_le hUV hEV)
  omega

/-- a 2-column matrix with a left inverse has a 2-dimensional column space inside `E`. -/
theorem two_le_finrank (E : Submodule K (Fin n → K)) (Xh : Matrix (Fin n) (Fin 2) K)
    (L : Matrix (Fin 2) (Fin n) K) (hL : L * Xh = 1) (hX : LinearMap.range Xh.mulVecLin ≤ E) :
    2 ≤ Module.finrank K E := by
  have h1 : (L * Xh).rank ≤ Xh.rank := rank_mul_le_right L Xh
  rw [hL, rank_one, Fintype.card_fin] at h1
  exact h1.trans (Submodule.finrank_mono hX)

/-- **B1(b)**: `β_i := N_i − |P_i| ≥ d_i := dim proj_S V_i ≥ 2`, for a piece of `m` rank-one
updates whose product is `−1` on the private roles `P` and with one stage matrix `x̂_b`
(columns in `proj_S V_i`) having a left inverse (from Lemma S, `ŷ_aᵀ x̂_b = ±I`). -/
theorem beta_ge_d_ge_two (h2 : (2 : K) ≠ 0) (x y : ℕ → Fin n → K) (m : ℕ) (P : Finset (Fin n))
    (hP : ∀ j ∈ P, wordProd x y m *ᵥ Pi.single j 1 = -Pi.single j 1)
    (Xh : Matrix (Fin n) (Fin 2) K) (L : Matrix (Fin 2) (Fin n) K) (hL : L * Xh = 1)
    (hX : LinearMap.range Xh.mulVecLin ≤
      (Submodule.span K (Set.range fun k : Fin m => x k)).map (projOff P)) :
    2 ≤ Module.finrank K ((Submodule.span K (Set.range fun k : Fin m => x k)).map (projOff P)) ∧
    P.card + Module.finrank K ((Submodule.span K (Set.range fun k : Fin m => x k)).map (projOff P))
      ≤ m := by
  refine ⟨two_le_finrank _ Xh L hL hX, ?_⟩
  have hsb := span_bound (Submodule.span K (Set.range fun k : Fin m => x k)) P
    (fun j hj => single_mem_span h2 x y m j (hP j hj))
  have hV : Module.finrank K (Submodule.span K (Set.range fun k : Fin m => x k)) ≤ m := by
    have := finrank_range_le_card (R := K) (fun k : Fin m => x k)
    simpa [Set.finrank] using this
  omega

/-! ## B1(c) corrected: a split piece has β ≥ 3 (linear-algebra replacement of b1.sing run 2) -/

/-- H-block (rows 0,1 = the global hubs) of a 4×2 matrix on rows (h1, h2, A, B). -/
def hb (M : Matrix (Fin 4) (Fin 2) K) : Matrix (Fin 2) (Fin 2) K :=
  Matrix.of fun i k => M (Fin.castLE (by omega) i) k

lemma cross_H (M N : Matrix (Fin 4) (Fin 2) K)
    (h2 : (∀ k, M 2 k = 0) ∨ (∀ k, N 2 k = 0)) (h3 : (∀ k, M 3 k = 0) ∨ (∀ k, N 3 k = 0)) :
    Mᵀ * N = (hb M)ᵀ * hb N := by
  ext i k
  simp only [mul_apply, transpose_apply, hb, of_apply, Fin.sum_univ_four, Fin.sum_univ_two]
  have e2 : M 2 i * N 2 k = 0 := by rcases h2 with h | h <;> simp [h]
  have e3 : M 3 i * N 3 k = 0 := by rcases h3 with h | h <;> simp [h]
  rw [e2, e3]
  simp [Fin.castLE]

lemma eq_of_left_inv (L : Matrix (Fin 2) (Fin 4) K) (X2 X3 : Matrix (Fin 4) (Fin 2) K)
    (h2 : L * X2 = 1) (h3 : L * X3 = 1)
    (hr : LinearMap.range X3.mulVecLin ≤ LinearMap.range X2.mulVecLin) : X3 = X2 := by
  ext i k
  obtain ⟨c, hc⟩ := hr ⟨Pi.single k 1, rfl⟩
  simp only [mulVecLin_apply] at hc
  have hc' : c = Pi.single k 1 := by
    have := congrArg (fun w => L *ᵥ w) hc
    simp only [mulVec_mulVec, h2, h3, one_mulVec] at this
    exact this
  rw [hc'] at hc
  have := congrFun hc i
  simpa [mulVec_single_one] using this.symm

lemma range_le_of_small (E : Submodule K (Fin 4 → K)) (hE : Module.finrank K E ≤ 2)
    (X2 X3 : Matrix (Fin 4) (Fin 2) K) (L : Matrix (Fin 2) (Fin 4) K) (hL : L * X2 = 1)
    (h2E : LinearMap.range X2.mulVecLin ≤ E) (h3E : LinearMap.range X3.mulVecLin ≤ E) :
    LinearMap.range X3.mulVecLin ≤ LinearMap.range X2.mulVecLin := by
  have hr : 2 ≤ Module.finrank K (LinearMap.range X2.mulVecLin) := by
    have h1 : (L * X2).rank ≤ X2.rank := rank_mul_le_right L X2
    rw [hL, rank_one, Fintype.card_fin] at h1
    exact h1
  have heq := Submodule.eq_of_le_of_finrank_le h2E (hE.trans hr)
  rw [heq]; exact h3E

/-- **B1(c), corrected (AUDIT-C)**. Four stage groups G1..G4 on the shared roles (h1, h2, A, B):
G1, G2 avoid B, G3, G4 avoid A (for both `x̂` and `ŷ`); Lemma S at ρ = 2 gives
`ŷ_iᵀ x̂_j = I` (i earlier) and `ŷ_jᵀ x̂_i = −I` for every cross pair except (G2, G3).
If the S-spans of BOTH the x's and the y's of the piece containing G2, G3 are ≤ 2-dimensional,
there is a contradiction (char ≠ 2). -/
theorem b1c (h2 : (2 : K) ≠ 0) (x1 x2 x3 x4 y1 y2 y3 y4 : Matrix (Fin 4) (Fin 2) K)
    (sx1 : ∀ k, x1 3 k = 0) (sx2 : ∀ k, x2 3 k = 0) (sx3 : ∀ k, x3 2 k = 0) (sx4 : ∀ k, x4 2 k = 0)
    (sy1 : ∀ k, y1 3 k = 0) (sy2 : ∀ k, y2 3 k = 0) (sy3 : ∀ k, y3 2 k = 0) (sy4 : ∀ k, y4 2 k = 0)
    (r12 : y1ᵀ * x2 = 1) (r21 : y2ᵀ * x1 = -1) (r13 : y1ᵀ * x3 = 1) (r31 : y3ᵀ * x1 = -1)
    (r14 : y1ᵀ * x4 = 1) (r41 : y4ᵀ * x1 = -1) (r24 : y2ᵀ * x4 = 1) (r42 : y4ᵀ * x2 = -1)
    (E E' : Submodule K (Fin 4 → K)) (hE : Module.finrank K E ≤ 2) (hE' : Module.finrank K E' ≤ 2)
    (h2E : LinearMap.range x2.mulVecLin ≤ E) (h3E : LinearMap.range x3.mulVecLin ≤ E)
    (h2E' : LinearMap.range y2.mulVecLin ≤ E') (h3E' : LinearMap.range y3.mulVecLin ≤ E') :
    False := by
  -- budget 2 ⇒ x̂3 = x̂2 and ŷ3 = ŷ2
  have hx : x3 = x2 := eq_of_left_inv y1ᵀ x2 x3 r12 r13 (range_le_of_small E hE x2 x3 y1ᵀ r12 h2E h3E)
  have r21' : (-x1ᵀ) * y2 = 1 := by
    rw [Matrix.neg_mul, ← transpose_transpose y2, ← transpose_mul, r21, transpose_neg,
      transpose_one, neg_neg]
  have r31' : (-x1ᵀ) * y3 = 1 := by
    rw [Matrix.neg_mul, ← transpose_transpose y3, ← transpose_mul, r31, transpose_neg,
      transpose_one, neg_neg]
  have hy : y3 = y2 := eq_of_left_inv (-x1ᵀ) y2 y3 r21' r31'
    (range_le_of_small E' hE' y2 y3 (-x1ᵀ) r21' h2E' h3E')
  have sx2' : ∀ k, x2 2 k = 0 := fun k => by rw [← hx]; exact sx3 k
  have sy2' : ∀ k, y2 2 k = 0 := fun k => by rw [← hy]; exact sy3 k
  -- reduce to 2×2 H-blocks
  rw [cross_H y1 x2 (Or.inr sx2') (Or.inl sy1)] at r12
  rw [cross_H y2 x1 (Or.inl sy2') (Or.inl sy2)] at r21
  rw [cross_H y1 x4 (Or.inr sx4) (Or.inl sy1)] at r14
  rw [cross_H y4 x1 (Or.inl sy4) (Or.inr sx1)] at r41
  rw [cross_H y2 x4 (Or.inl sy2') (Or.inl sy2)] at r24
  rw [cross_H y4 x2 (Or.inl sy4) (Or.inr sx2)] at r42
  set a1 := hb x1; set a2 := hb x2; set a4 := hb x4
  set b1 := (hb y1)ᵀ; set b2 := (hb y2)ᵀ; set b4 := (hb y4)ᵀ
  -- b4 = -b1
  have h12' : a2 * b1 = 1 := mul_eq_one_comm.mp r12
  have hb4 : b4 = -b1 := by
    calc b4 = b4 * (a2 * b1) := by rw [h12', Matrix.mul_one]
      _ = (b4 * a2) * b1 := by rw [Matrix.mul_assoc]
      _ = -b1 := by rw [r42, Matrix.neg_mul, Matrix.one_mul]
  -- a4 = -a1
  have r21n : b2 * (-a1) = 1 := by rw [Matrix.mul_neg, r21, neg_neg]
  have h21' : (-a1) * b2 = 1 := mul_eq_one_comm.mp r21n
  have ha4 : a4 = -a1 := by
    calc a4 = ((-a1) * b2) * a4 := by rw [h21', Matrix.one_mul]
      _ = (-a1) * (b2 * a4) := by rw [Matrix.mul_assoc]
      _ = -a1 := by rw [r24, Matrix.mul_one]
  rw [ha4, Matrix.mul_neg] at r14
  rw [hb4, Matrix.neg_mul] at r41
  have e1 : b1 * a1 = -1 := by rw [← neg_neg (b1 * a1), r14]
  have e2 : b1 * a1 = 1 := by rw [← neg_neg (b1 * a1), r41, neg_neg]
  have h11 := congrFun (congrFun (e1.symm.trans e2) 0) 0
  simp only [Matrix.neg_apply, Matrix.one_apply_eq] at h11
  apply h2
  have : (2 : K) = 1 - (-1) := by ring
  rw [this, h11, sub_self]

/-- **B1(c) as a budget statement**: `β ≥ dim E` and `β ≥ dim E'` (span bound for x and y) with the
cross relations of `b1c` force `β ≥ 3` (not `d ≥ 3`; AUDIT-C fix). -/
theorem b1c_budget (h2 : (2 : K) ≠ 0) (β : ℕ) (x1 x2 x3 x4 y1 y2 y3 y4 : Matrix (Fin 4) (Fin 2) K)
    (sx1 : ∀ k, x1 3 k = 0) (sx2 : ∀ k, x2 3 k = 0) (sx3 : ∀ k, x3 2 k = 0) (sx4 : ∀ k, x4 2 k = 0)
    (sy1 : ∀ k, y1 3 k = 0) (sy2 : ∀ k, y2 3 k = 0) (sy3 : ∀ k, y3 2 k = 0) (sy4 : ∀ k, y4 2 k = 0)
    (r12 : y1ᵀ * x2 = 1) (r21 : y2ᵀ * x1 = -1) (r13 : y1ᵀ * x3 = 1) (r31 : y3ᵀ * x1 = -1)
    (r14 : y1ᵀ * x4 = 1) (r41 : y4ᵀ * x1 = -1) (r24 : y2ᵀ * x4 = 1) (r42 : y4ᵀ * x2 = -1)
    (E E' : Submodule K (Fin 4 → K)) (hE : Module.finrank K E ≤ β) (hE' : Module.finrank K E' ≤ β)
    (h2E : LinearMap.range x2.mulVecLin ≤ E) (h3E : LinearMap.range x3.mulVecLin ≤ E)
    (h2E' : LinearMap.range y2.mulVecLin ≤ E') (h3E' : LinearMap.range y3.mulVecLin ≤ E') :
    3 ≤ β := by
  by_contra hβ
  exact b1c h2 x1 x2 x3 x4 y1 y2 y3 y4 sx1 sx2 sx3 sx4 sy1 sy2 sy3 sy4 r12 r21 r13 r31 r14 r41
    r24 r42 E E' (by omega) (by omega) h2E h3E h2E' h3E'

/-- **B1(d)** arithmetic: at ρ = 2, `Σ β_i = 2 + |S|`. c = 3 split pair (|S| = 4, β ≥ (2,3,2)) and
c = 4 h12+h34 (|S| = 4, β_i ≥ 2) are impossible. -/
theorem b1d_c3 (β1 β2 β3 : ℕ) (h : β1 + β2 + β3 = 2 + 4) (h1 : 2 ≤ β1) (h2 : 3 ≤ β2)
    (h3 : 2 ≤ β3) : False := by omega

theorem b1d_c4 (β1 β2 β3 β4 : ℕ) (h : β1 + β2 + β3 + β4 = 2 + 4) (h1 : 2 ≤ β1) (h2 : 2 ≤ β2)
    (h3 : 2 ≤ β3) (h4 : 2 ≤ β4) : False := by omega

/-! ## H1s: a budget-2 twisted piece with shared roles needs ≥ 2 piece hubs (replaces h1s.sing) -/

/-- Cayley step: `(I+R) A Bᵀ = R − I` ⇒ `I − BᵀA` is invertible (char ≠ 2). -/
theorem cayley_one_sub {s : ℕ} (h2 : (2 : K) ≠ 0) (A B : Matrix (Fin s) (Fin 2) K)
    (R : Matrix (Fin s) (Fin s) K) (hcay : (1 + R) * A * Bᵀ = R - 1) :
    IsUnit (1 - Bᵀ * A).det := by
  rw [isUnit_iff_ne_zero]
  intro hdet
  obtain ⟨v, hv0, hv⟩ := exists_mulVec_eq_zero_iff.mpr hdet
  have hCv : (Bᵀ * A) *ᵥ v = v := by
    rw [sub_mulVec, one_mulVec, sub_eq_zero] at hv; exact hv.symm
  set w := A *ᵥ v
  have hABw : (A * Bᵀ) *ᵥ w = w := by
    simp only [w, mulVec_mulVec, Matrix.mul_assoc]
    rw [← mulVec_mulVec, hCv]
  have h1 := congrArg (fun M => M *ᵥ w) hcay
  rw [Matrix.mul_assoc, ← mulVec_mulVec, hABw, add_mulVec, sub_mulVec, one_mulVec] at h1
  have hw : (2 : K) • w = 0 := by
    have : w + R *ᵥ w - (R *ᵥ w - w) = 0 := by rw [h1, sub_self]
    rw [← this]; rw [two_smul]; abel
  have hw0 : w = 0 := (smul_eq_zero.mp hw).resolve_left h2
  apply hv0
  rw [← hCv, ← mulVec_mulVec]
  show Bᵀ *ᵥ w = 0
  rw [hw0, mulVec_zero]

/-- Cayley step, "later" sign: with `R` invertible, `I + BᵀA` is invertible. -/
theorem cayley_one_add {s : ℕ} (h2 : (2 : K) ≠ 0) (A B : Matrix (Fin s) (Fin 2) K)
    (R : Matrix (Fin s) (Fin s) K) (hR : IsUnit R.det) (hcay : (1 + R) * A * Bᵀ = R - 1) :
    IsUnit (1 + Bᵀ * A).det := by
  rw [isUnit_iff_ne_zero]
  intro hdet
  obtain ⟨v, hv0, hv⟩ := exists_mulVec_eq_zero_iff.mpr hdet
  have hCv : (Bᵀ * A) *ᵥ v = -v := by
    rw [add_mulVec, one_mulVec, add_comm] at hv; exact eq_neg_of_add_eq_zero_left hv
  set w := A *ᵥ v
  have hABw : (A * Bᵀ) *ᵥ w = -w := by
    simp only [w, mulVec_mulVec, Matrix.mul_assoc]
    rw [← mulVec_mulVec, hCv, mulVec_neg]
  have h1 := congrArg (fun M => M *ᵥ w) hcay
  rw [Matrix.mul_assoc, ← mulVec_mulVec, hABw, mulVec_neg, add_mulVec, sub_mulVec,
    one_mulVec] at h1
  have hRw : (2 : K) • (R *ᵥ w) = 0 := by
    have : -(w + R *ᵥ w) - (R *ᵥ w - w) = 0 := by rw [h1, sub_self]
    rw [two_smul, ← neg_eq_zero, ← this]; abel
  have hRw0 : R *ᵥ w = 0 := (smul_eq_zero.mp hRw).resolve_left h2
  have hw0 : w = 0 := by
    have := congrArg (fun u => R⁻¹ *ᵥ u) hRw0
    simpa [mulVec_mulVec, nonsing_inv_mul _ hR] using this
  apply hv0
  have : -v = 0 := by rw [← hCv, ← mulVec_mulVec]; show Bᵀ *ᵥ w = 0; rw [hw0, mulVec_zero]
  exact neg_eq_zero.mp this

lemma two_le_of_unit_factor {k : ℕ} (M : Matrix (Fin 2) (Fin 2) K) (hM : IsUnit M.det)
    (Yp Xp : Matrix (Fin k) (Fin 2) K) (h : Ypᵀ * Xp = M) : 2 ≤ k := by
  have h1 : M.rank = 2 := by
    rw [rank_of_isUnit M ((isUnit_iff_isUnit_det M).mpr hM), Fintype.card_fin]
  have h2 : (Ypᵀ * Xp).rank ≤ Xp.rank := rank_mul_le_right _ _
  have h3 : Xp.rank ≤ k := by
    have := rank_le_card_height Xp; simpa using this
  rw [h] at h2
  omega

/-- **H1s** (BRIDGETREE round 2; the Singular std = <1> step as linear algebra). Twisted piece at
budget 2 with `s` shared roles: `X_r[S_i] = A Z_rᵀ`, `Y_a[S_i] = B W_aᵀ`, `(I+R) A Bᵀ = R − I`
(twisted Lemma S), `W_a`, `Z_r` invertible. If a left stage `a` (earlier) and a right stage `r` meet
only in `S_i` and `k` piece hubs `Ph`, and Lemma S gives `G[a,r] = W_a Z_rᵀ`, then `k ≥ 2`. -/
theorem h1s {s k : ℕ} (h2 : (2 : K) ≠ 0) (A B : Matrix (Fin s) (Fin 2) K)
    (R : Matrix (Fin s) (Fin s) K) (hcay : (1 + R) * A * Bᵀ = R - 1)
    (Wa Zr : Matrix (Fin 2) (Fin 2) K) (hW : IsUnit Wa.det) (hZ : IsUnit Zr.det)
    (YaS XrS : Matrix (Fin s) (Fin 2) K) (YaP XrP : Matrix (Fin k) (Fin 2) K)
    (hY : YaS = B * Waᵀ) (hX : XrS = A * Zrᵀ)
    (hG : YaSᵀ * XrS + YaPᵀ * XrP = Wa * Zrᵀ) : 2 ≤ k := by
  have hC := cayley_one_sub h2 A B R hcay
  have hP : YaPᵀ * XrP = Wa * (1 - Bᵀ * A) * Zrᵀ := by
    rw [hY, hX] at hG
    rw [Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_one, ← hG, transpose_mul, transpose_transpose]
    simp only [Matrix.mul_assoc]; abel
  refine two_le_of_unit_factor _ ?_ YaP XrP hP
  rw [det_mul, det_mul, det_transpose]
  exact (hW.mul hC).mul hZ

/-- **H1s**, later sign (`a` later than `r`: `G[a,r] = −W_a Z_rᵀ`), needs `R` invertible. -/
theorem h1s_later {s k : ℕ} (h2 : (2 : K) ≠ 0) (A B : Matrix (Fin s) (Fin 2) K)
    (R : Matrix (Fin s) (Fin s) K) (hR : IsUnit R.det) (hcay : (1 + R) * A * Bᵀ = R - 1)
    (Wa Zr : Matrix (Fin 2) (Fin 2) K) (hW : IsUnit Wa.det) (hZ : IsUnit Zr.det)
    (YaS XrS : Matrix (Fin s) (Fin 2) K) (YaP XrP : Matrix (Fin k) (Fin 2) K)
    (hY : YaS = B * Waᵀ) (hX : XrS = A * Zrᵀ)
    (hG : YaSᵀ * XrS + YaPᵀ * XrP = -(Wa * Zrᵀ)) : 2 ≤ k := by
  have hC := cayley_one_add h2 A B R hR hcay
  have hP : YaPᵀ * XrP = -(Wa * (1 + Bᵀ * A) * Zrᵀ) := by
    rw [hY, hX] at hG
    rw [Matrix.mul_add, Matrix.add_mul, Matrix.mul_one, neg_add, ← hG, transpose_mul,
      transpose_transpose]
    simp only [Matrix.mul_assoc]; abel
  refine two_le_of_unit_factor _ ?_ YaP XrP hP
  rw [det_neg, det_mul, det_mul, det_transpose]
  exact ((isUnit_neg_one.pow _).mul ((hW.mul hC).mul hZ))

end BUDGET

#print axioms BUDGET.budget_identity
#print axioms BUDGET.piece_neg_on_private
#print axioms BUDGET.single_mem_span
#print axioms BUDGET.span_bound
#print axioms BUDGET.beta_ge_d_ge_two
#print axioms BUDGET.b1c
#print axioms BUDGET.b1c_budget
#print axioms BUDGET.b1d_c3
#print axioms BUDGET.b1d_c4
#print axioms BUDGET.cayley_one_sub
#print axioms BUDGET.cayley_one_add
#print axioms BUDGET.h1s
#print axioms BUDGET.h1s_later

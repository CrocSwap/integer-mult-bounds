/-
SPECBREAK R42 Lemma TS (tight supports) + Lemma UR (unit rank), lane LEAN-NEXT26, Nov 17.
Source: cards/WILD/SPECBREAK/R42/RESULT42.md §1-5, AUDIT42.md. See SpecTSUR.md.
Matrices over a field K; coordinates `n` (targets and ancillas); jobs are reflections
`refl x y = 1 - x yᵀ`, ordered products via the prefix function `pp`.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.Diagonal
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.Tactic.NoncommRing
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel

open Matrix Finset

set_option linter.unusedSectionVars false

namespace SpecTSUR

variable {K : Type*} [Field K]

/-! ## §0. rank helpers -/
section Rank
variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

theorem rank_add_le' (A B : Matrix m n K) : (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  rw [Matrix.mulVecLin_add]
  refine le_trans (Submodule.finrank_mono (LinearMap.range_add_le _ _)) ?_
  exact Submodule.finrank_add_le_finrank_add_finrank _ _

theorem rank_sub_le' (A B : Matrix m n K) : (A - B).rank ≤ A.rank + B.rank := by
  have : A - B = A + (-1 : K) • B := by simp [sub_eq_add_neg]
  rw [this]
  refine (rank_add_le' _ _).trans ?_
  have h : ((-1 : K) • B).rank ≤ B.rank := by
    have : (-1 : K) • B = (diagonal fun _ : m => (-1 : K)) * B := by
      ext i j; simp [diagonal_mul]
    rw [this]; exact rank_mul_le_right _ _
  omega

/-- rank is subadditive, the form used: `rank A ≤ rank (A - B) + rank B`. -/
theorem rank_le_sub_add (A B : Matrix m n K) : A.rank ≤ (A - B).rank + B.rank := by
  have : A = (A - B) + B := by simp
  conv_lhs => rw [this]
  exact rank_add_le' _ _

/-- A full column rank matrix has a left inverse. -/
theorem exists_left_inv {k : ℕ} (A : Matrix n (Fin k) K) (h : A.rank = k) :
    ∃ L : Matrix (Fin k) n K, L * A = 1 := by
  have hker : LinearMap.ker A.mulVecLin = ⊥ := by
    have := LinearMap.finrank_range_add_finrank_ker A.mulVecLin
    have h1 : Module.finrank K (LinearMap.range A.mulVecLin) = k := h
    rw [h1, Module.finrank_fin_fun] at this
    have h0 : Module.finrank K (LinearMap.ker A.mulVecLin) = 0 := by omega
    exact Submodule.finrank_eq_zero.1 h0
  obtain ⟨g, hg⟩ := LinearMap.exists_leftInverse_of_injective A.mulVecLin hker
  refine ⟨LinearMap.toMatrix' g, ?_⟩
  have := congrArg LinearMap.toMatrix' hg
  rw [LinearMap.toMatrix'_comp, ← Matrix.toLin'_apply', LinearMap.toMatrix'_toLin'] at this
  simpa using this

/-- rank of a block-diagonal matrix is at least the sum of the block ranks. -/
theorem rank_fromBlocks_diag_ge {m₁ m₂ n₁ n₂ : Type*} [Fintype m₁] [Fintype m₂] [Fintype n₁]
    [Fintype n₂] [DecidableEq m₁] [DecidableEq m₂] [DecidableEq n₁] [DecidableEq n₂]
    (A : Matrix m₁ n₁ K) (B : Matrix m₂ n₂ K) :
    A.rank + B.rank ≤ (fromBlocks A 0 0 B).rank := by
  let e := (LinearEquiv.sumArrowLequivProdArrow m₁ m₂ K K).symm
  let φ : (LinearMap.range A.mulVecLin × LinearMap.range B.mulVecLin) →ₗ[K] ((m₁ ⊕ m₂) → K) :=
    e.toLinearMap ∘ₗ LinearMap.prodMap (LinearMap.range A.mulVecLin).subtype
      (LinearMap.range B.mulVecLin).subtype
  have hinj : Function.Injective φ := by
    intro p q h
    have := e.injective h
    have h1 : (p.1 : m₁ → K) = q.1 := congrArg Prod.fst this
    have h2 : (p.2 : m₂ → K) = q.2 := congrArg Prod.snd this
    exact Prod.ext (Subtype.ext h1) (Subtype.ext h2)
  have hS : LinearMap.range φ ≤ LinearMap.range (fromBlocks A 0 0 B).mulVecLin := by
    rintro _ ⟨⟨⟨_, ⟨a, rfl⟩⟩, ⟨_, ⟨b, rfl⟩⟩⟩, rfl⟩
    refine ⟨Sum.elim a b, ?_⟩
    ext (i | i) <;> simp [φ, e, fromBlocks_mulVec]
  have h1 := LinearMap.finrank_range_of_inj hinj
  rw [Module.finrank_prod] at h1
  have := Submodule.finrank_mono hS
  unfold Matrix.rank
  omega

end Rank


/-! ## §1. Jobs and the product formula -/
section Jobs
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- a job (reflection) `I - x yᵀ` -/
def refl (x y : n → K) : Matrix n n K := 1 - vecMulVec x y

/-- ordered product of the first `i` jobs `refl (x 0) (y 0) * ... * refl (x (i-1)) (y (i-1))` -/
def pp (x y : ℕ → n → K) : ℕ → Matrix n n K
  | 0 => 1
  | i + 1 => pp x y i * refl (x i) (y i)

/-- `z i = (product of the jobs before i) x_i` -/
def zv (x y : ℕ → n → K) (i : ℕ) : n → K := pp x y i *ᵥ x i

/-- telescoping: product = I - sum_i z_i y_iᵀ -/
theorem pp_eq (x y : ℕ → n → K) (m : ℕ) :
    pp x y m = 1 - ∑ i ∈ range m, vecMulVec (zv x y i) (y i) := by
  induction m with
  | zero => simp [pp]
  | succ m ih =>
    have h : pp x y (m + 1) = pp x y m - vecMulVec (zv x y m) (y m) := by
      rw [pp, refl, mul_sub, mul_one, mul_vecMulVec]; rfl
    rw [h, ih, sum_range_succ]
    abel

/-- product formula, coordinates: `z_i + sum_{j<i} (y_j·x_i) z_j = x_i` (i.e. `Z N = X`) -/
theorem zv_rec (x y : ℕ → n → K) (i : ℕ) :
    zv x y i = x i - ∑ j ∈ range i, (y j ⬝ᵥ x i) • zv x y j := by
  rw [zv, pp_eq, sub_mulVec, one_mulVec, sum_mulVec]
  congr 1
  refine sum_congr rfl fun j _ => ?_
  rw [vecMulVec_mulVec, op_smul_eq_smul]

end Jobs


/-! ## §2. Lemma TS (tight supports) -/
section TS
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- columns `x_i`, `y_i`, `z_i` as `n × m` matrices -/
def Xm (x : ℕ → n → K) (m : ℕ) : Matrix n (Fin m) K := Matrix.of fun a i => x i a
def Zm (x y : ℕ → n → K) (m : ℕ) : Matrix n (Fin m) K := Matrix.of fun a i => zv x y i a
/-- `N = I + strict-upper(G)`, `G_ij = y_i · x_j` -/
def Nm (x y : ℕ → n → K) (m : ℕ) : Matrix (Fin m) (Fin m) K :=
  1 + (Matrix.of fun (j i : Fin m) => if j < i then y j ⬝ᵥ x i else 0 : Matrix (Fin m) (Fin m) K)

theorem sum_fin_lt {m : ℕ} (F : ℕ → K) (i : Fin m) :
    ∑ j : Fin m, (if j < i then F j else 0) = ∑ j ∈ range i, F j := by
  have := Fin.sum_univ_eq_sum_range (fun j : ℕ => if j < (i : ℕ) then F j else 0) m
  simp only [Fin.lt_def]
  rw [this, ← sum_filter]
  congr 1
  ext j
  simp only [mem_filter, mem_range]
  have := i.2
  omega

/-- the product formula `Z N = X` -/
theorem ZN_eq (x y : ℕ → n → K) (m : ℕ) : Zm x y m * Nm x y m = Xm x m := by
  ext a i
  have h := congrFun (zv_rec x y i) a
  simp only [Finset.sum_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul] at h
  have h2 : ∑ j : Fin m, zv x y j a * (if j < i then y j ⬝ᵥ x i else 0) =
      ∑ j ∈ range i, (y j ⬝ᵥ x i) * zv x y j a := by
    rw [← sum_fin_lt (fun j => (y j ⬝ᵥ x i) * zv x y j a) i]
    refine sum_congr rfl fun j _ => ?_
    split_ifs <;> simp [mul_comm]
  have h1 : ∑ j : Fin m, zv x y j a * (if j = i then 1 else 0) = zv x y i a := by simp
  simp only [Zm, Nm, Xm, Matrix.mul_apply, Matrix.add_apply, Matrix.one_apply, Matrix.of_apply,
    mul_add, sum_add_distrib]
  rw [h1, h2, h]; ring

theorem sum_ZY (x y : ℕ → n → K) (m : ℕ) :
    ∑ i ∈ range m, vecMulVec (zv x y i) (y i) = Zm x y m * (Matrix.of fun a (i : Fin m) => y i a)ᵀ := by
  ext a b
  rw [Matrix.sum_apply]
  simp only [vecMulVec_apply, Matrix.mul_apply, Zm, Matrix.of_apply, Matrix.transpose_apply]
  exact (Fin.sum_univ_eq_sum_range (fun j => zv x y j a * y j b) m).symm

theorem gram_apply (x y : ℕ → n → K) (m : ℕ) (i j : Fin m) :
    ((Matrix.of fun a (i : Fin m) => y i a)ᵀ * Xm x m) i j = y i ⬝ᵥ x j := by
  simp [Matrix.mul_apply, Xm, dotProduct]

theorem range_mul_right_inv {l o : Type*} [Fintype l] [Fintype o] [DecidableEq l] [DecidableEq o]
    {k : Type*} [Fintype k] [DecidableEq k]
    (A : Matrix l o K) (B : Matrix o k K) (C : Matrix k o K) (h : B * C = 1) :
    LinearMap.range (A * B).mulVecLin = LinearMap.range A.mulVecLin := by
  apply le_antisymm
  · rw [Matrix.mulVecLin_mul]; exact LinearMap.range_comp_le_range _ _
  · have : A = (A * B) * C := by rw [Matrix.mul_assoc, h, Matrix.mul_one]
    conv_lhs => rw [this]
    rw [Matrix.mulVecLin_mul]; exact LinearMap.range_comp_le_range _ _

theorem Nm_isUnit (x y : ℕ → n → K) (m : ℕ) : IsUnit (Nm x y m) := by
  rw [Matrix.isUnit_iff_isUnit_det]
  have hb : (Nm x y m).BlockTriangular id := by
    intro i j hij
    have hij' : j < i := hij
    simp [Nm, Matrix.add_apply, Matrix.one_apply, hij'.ne', not_lt.2 hij'.le]
  rw [Matrix.det_of_upperTriangular hb]
  simp [Nm]

variable [DecidableEq K]

/-- rank of `I - diag s` (`s = ±1`, char ≠ 2) = number of flipped coordinates -/
theorem rank_one_sub_diag (h2 : (2 : K) ≠ 0) (s : n → K) (hs : ∀ a, s a = 1 ∨ s a = -1) :
    (1 - diagonal s).rank = (univ.filter fun a => s a = -1).card := by
  have : (1 - diagonal s) = diagonal fun a => 1 - s a := by
    ext a b; by_cases h : a = b <;> simp [diagonal_apply, Matrix.one_apply, h]
  have hne : (1 : K) ≠ -1 := by intro h; apply h2; linear_combination h
  rw [this, rank_diagonal, Fintype.card_subtype]
  congr 1
  apply filter_congr
  intro a _
  rcases hs a with h | h
  · simp [h, hne]
  · simp [h, sub_neg_eq_add, one_add_one_eq_two, h2]

/-- **Lemma TS (tight supports).** char ≠ 2. A unit-free character: the ordered product of the `m`
jobs `1 - x_i y_iᵀ` is `D = diag s` (`s = ±1`), and the number `r` of flipped coordinates equals the
number `m` of active jobs. Then (i) the Gram matrix is `y_i·x_j = 2 δ_ij`; (ii) every job vanishes
(x and y) on every unflipped coordinate (so never touches a dark target); (iii)
`image (I - D) = span (x_i)`. -/
theorem lemmaTS (m : ℕ) (x y : ℕ → n → K) (s : n → K) (h2 : (2 : K) ≠ 0)
    (hs : ∀ a, s a = 1 ∨ s a = -1)
    (hprod : pp x y m = diagonal s) (hcard : (univ.filter fun a => s a = -1).card = m) :
    (∀ i j : Fin m, y i ⬝ᵥ x j = if i = j then 2 else 0) ∧
    (∀ (i : Fin m) a, s a = 1 → x i a = 0 ∧ y i a = 0) ∧
    LinearMap.range (1 - diagonal s).mulVecLin =
      Submodule.span K (Set.range fun i : Fin m => x i) := by
  set X := Xm x m with hX
  set Y : Matrix n (Fin m) K := Matrix.of fun a i => y i a with hY
  set Z := Zm x y m with hZ
  set N := Nm x y m with hN
  have hZN : Z * N = X := ZN_eq x y m
  have hP : 1 - diagonal s = Z * Yᵀ := by
    have := pp_eq x y m
    rw [hprod, sum_ZY] at this
    rw [this]; abel
  have hDD : diagonal s * diagonal s = 1 := by
    rw [diagonal_mul_diagonal, ← diagonal_one]
    congr 1; funext a; rcases hs a with h | h <;> simp [h]
  have hrP : (1 - diagonal s).rank = m := by rw [rank_one_sub_diag h2 s hs, hcard]
  have hrZ : Z.rank = m := by
    refine le_antisymm ?_ ?_
    · exact (Matrix.rank_le_card_width Z).trans (by simp)
    · have := rank_mul_le_left Z Yᵀ; rw [← hP, hrP] at this; exact this
  have hrY : Y.rank = m := by
    refine le_antisymm ?_ ?_
    · exact (Matrix.rank_le_card_width Y).trans (by simp)
    · have := (rank_mul_le_right Z Yᵀ).trans_eq (Matrix.rank_transpose Y); rw [← hP, hrP] at this; exact this
  obtain ⟨L, hL⟩ := exists_left_inv Z hrZ
  obtain ⟨L', hL'⟩ := exists_left_inv Y hrY
  have hR : Yᵀ * L'ᵀ = 1 := by rw [← Matrix.transpose_mul, hL', Matrix.transpose_one]
  have hsq : (Z * Yᵀ) * (Z * Yᵀ) = (2 : K) • (Z * Yᵀ) := by
    rw [← hP]
    have : (1 - diagonal s) * (1 - diagonal s) = 1 - diagonal s - diagonal s + diagonal s * diagonal s := by
      noncomm_ring
    rw [this, hDD]
    ext a b; simp [Matrix.sub_apply, Matrix.add_apply]; ring
  have hYZ : Yᵀ * Z = (2 : K) • 1 := by
    calc Yᵀ * Z = (L * Z) * (Yᵀ * Z) * (Yᵀ * L'ᵀ) := by rw [hL, hR]; simp
      _ = L * ((Z * Yᵀ) * (Z * Yᵀ)) * L'ᵀ := by simp only [Matrix.mul_assoc]
      _ = L * ((2 : K) • (Z * Yᵀ)) * L'ᵀ := by rw [hsq]
      _ = (2 : K) • ((L * Z) * (Yᵀ * L'ᵀ)) := by
        simp only [Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_assoc]
      _ = (2 : K) • 1 := by rw [hL, hR]; simp
  have hG : Yᵀ * X = (2 : K) • N := by
    rw [← hZN, ← Matrix.mul_assoc, hYZ, Matrix.smul_mul, Matrix.one_mul]
  refine ⟨?_, ?_, ?_⟩
  · intro i j
    have h := congrFun (congrFun hG i) j
    rw [gram_apply] at h
    simp only [Matrix.smul_apply, hN, Nm, Matrix.add_apply, Matrix.one_apply, Matrix.of_apply,
      smul_eq_mul] at h
    rcases lt_trichotomy i j with hij | hij | hij
    · simp only [hij, if_true, hij.ne, if_false, zero_add] at h
      have : y i ⬝ᵥ x j = 0 := by linear_combination (-1 : K) * h
      simp [hij.ne, this]
    · subst hij; simp at h; rw [h]; simp
    · simp only [not_lt.2 hij.le, if_false, hij.ne', add_zero] at h
      simp [hij.ne', h]
  · intro i a ha
    have hP0 : ∀ b, (Z * Yᵀ) a b = 0 ∧ (Z * Yᵀ) b a = 0 := by
      intro b; rw [← hP]
      by_cases h : a = b
      · subst h; simp [Matrix.sub_apply, Matrix.one_apply, diagonal_apply, ha]
      · simp [Matrix.sub_apply, Matrix.one_apply, diagonal_apply, h, Ne.symm h]
    constructor
    · -- row `a` of Z vanishes
      have hrow : (fun j => Z a j) ᵥ* Yᵀ = 0 := by
        funext b; simpa [Matrix.mul_apply, Matrix.vecMul, dotProduct] using (hP0 b).1
      have hw : (fun j => Z a j) = 0 := by
        calc (fun j => Z a j) = (fun j => Z a j) ᵥ* (Yᵀ * L'ᵀ) := by rw [hR]; simp
          _ = 0 := by rw [← Matrix.vecMul_vecMul, hrow]; simp
      have : X a i = 0 := by
        rw [← hZN]; simp [Matrix.mul_apply, congrFun hw]
      simpa [hX, Xm] using this
    · have hcol : Z *ᵥ (fun j => Y a j) = 0 := by
        funext c; simpa [Matrix.mul_apply, Matrix.mulVec, dotProduct] using (hP0 c).2
      have hw : (fun j => Y a j) = 0 := by
        calc (fun j => Y a j) = (L * Z) *ᵥ (fun j => Y a j) := by rw [hL]; simp
          _ = 0 := by rw [← Matrix.mulVec_mulVec, hcol]; simp
      exact congrFun hw i
  · obtain ⟨C, hC⟩ : ∃ C, N * C = 1 := ⟨N⁻¹, Matrix.mul_nonsing_inv _
      ((Matrix.isUnit_iff_isUnit_det _).1 (Nm_isUnit x y m))⟩
    rw [hP, range_mul_right_inv Z (Yᵀ) L'ᵀ hR, ← range_mul_right_inv Z N C hC, hZN,
      Matrix.range_mulVecLin]
    rfl

end TS


/-! ## §3. Lemma UR (unit rank) -/
section UR

/-- `neg` does not change rank -/
theorem rank_neg_le {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]
    (A : Matrix m n K) : (-A).rank ≤ A.rank := by
  have : -A = (diagonal fun _ : m => (-1 : K)) * A := by ext i j; simp [diagonal_mul]
  rw [this]; exact rank_mul_le_right _ _

theorem rank_neg_eq {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]
    (A : Matrix m n K) : (-A).rank = A.rank :=
  le_antisymm (rank_neg_le A) (by simpa using rank_neg_le (-A))

/-! ### Upper bound: words, units moved left past the jobs.
Convention (mirror of `R25Kill.ev_eq`): a word is a list of letters in a group `G`, `inl` = a unit
(transvection), `inr` = a job. The jobs are moved RIGHT, so each unit is conjugated by the product of
the jobs to its left. -/
section Word
variable {G : Type*} [Group G]

def ev : List (G ⊕ G) → G
  | [] => 1
  | .inl a :: w => a * ev w
  | .inr b :: w => b * ev w

/-- ordered product of the job letters -/
def jobsP : List (G ⊕ G) → G
  | [] => 1
  | .inl _ :: w => jobsP w
  | .inr b :: w => b * jobsP w

/-- the unit letters, each conjugated by the jobs before it (`pre` = product of jobs so far) -/
def uconj : List (G ⊕ G) → G → List G
  | [], _ => []
  | .inl t :: w, pre => (pre * t * pre⁻¹) :: uconj w pre
  | .inr j :: w, pre => uconj w (pre * j)

def ucount : List (G ⊕ G) → ℕ
  | [] => 0
  | .inl _ :: w => ucount w + 1
  | .inr _ :: w => ucount w

theorem ev_move : ∀ (w : List (G ⊕ G)) (pre : G),
    pre * ev w = (uconj w pre).prod * (pre * jobsP w)
  | [], pre => by simp [ev, uconj, jobsP]
  | .inl t :: w, pre => by
    have ih := ev_move w pre
    simp only [ev, uconj, jobsP, List.prod_cons]
    calc pre * (t * ev w) = (pre * t * pre⁻¹) * (pre * ev w) := by group
      _ = _ := by rw [ih]; group
  | .inr j :: w, pre => by
    have ih := ev_move w (pre * j)
    simp only [ev, uconj, jobsP]
    rw [← mul_assoc, ih]; group

theorem length_uconj : ∀ (w : List (G ⊕ G)) (pre : G), (uconj w pre).length = ucount w
  | [], _ => rfl
  | .inl _ :: w, pre => by simp [uconj, ucount, length_uconj w pre]
  | .inr j :: w, pre => by simp [uconj, ucount, length_uconj w (pre * j)]

end Word

section Upper
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem rank_prod_sub_one_le (l : List (Matrix n n K)ˣ)
    (h : ∀ a ∈ l, ((a : Matrix n n K) - 1).rank ≤ 1) :
    (((l.prod : (Matrix n n K)ˣ) : Matrix n n K) - 1).rank ≤ l.length := by
  induction l with
  | nil => simp
  | cons a l ih =>
    have h1 := h a (by simp)
    have h2 := ih fun b hb => h b (by simp [hb])
    have e : (((a :: l).prod : (Matrix n n K)ˣ) : Matrix n n K) - 1 =
        (a : Matrix n n K) * (((l.prod : (Matrix n n K)ˣ) : Matrix n n K) - 1) +
          ((a : Matrix n n K) - 1) := by
      simp only [List.prod_cons, Units.val_mul]; noncomm_ring
    rw [e]
    refine (rank_add_le' _ _).trans ?_
    have := rank_mul_le_right (a : Matrix n n K) (((l.prod : (Matrix n n K)ˣ) : Matrix n n K) - 1)
    simp only [List.length_cons]
    omega

theorem uconj_rank : ∀ (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ)) (pre : (Matrix n n K)ˣ),
    (∀ t, Sum.inl t ∈ w → ((t : Matrix n n K) - 1).rank ≤ 1) →
    ∀ c ∈ uconj w pre, ((c : Matrix n n K) - 1).rank ≤ 1
  | [], _, _ => by simp [uconj]
  | .inl t :: w, pre, h => by
    intro c hc
    simp only [uconj, List.mem_cons] at hc
    rcases hc with rfl | hc
    · have e : ((pre * t * pre⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) - 1 =
          (pre : Matrix n n K) * ((t : Matrix n n K) - 1) * ((pre⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) := by
        have := pre.mul_inv
        simp only [Units.val_mul, mul_sub, sub_mul, mul_one]
        rw [Matrix.mul_assoc (pre : Matrix n n K) (t : Matrix n n K), this]
      rw [e]
      exact (rank_mul_le_left _ _).trans ((rank_mul_le_right _ _).trans (h t (by simp)))
    · exact uconj_rank w pre (fun t ht => h t (by simp [ht])) c hc
  | .inr j :: w, pre, h => by
    exact uconj_rank w (pre * j) (fun t ht => h t (by simp [ht]))

/-- **Lemma UR, upper bound.** In a word whose unit letters have rank(t - 1) ≤ 1, with the jobs moved
to the right, `rank(ev w - J) ≤ #units`, `J` = ordered product of the job letters. -/
theorem UR_upper (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (h : ∀ t, Sum.inl t ∈ w → ((t : Matrix n n K) - 1).rank ≤ 1) :
    (((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).rank
      ≤ ucount w := by
  have h1 := ev_move w 1
  simp only [one_mul] at h1
  have h2 := rank_prod_sub_one_le (uconj w 1) (uconj_rank w 1 h)
  rw [length_uconj] at h2
  have e : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) =
      ((((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) - 1) *
        ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) := by
    rw [h1]; simp [sub_mul]
  rw [e]
  exact (rank_mul_le_left _ _).trans h2

end Upper

end UR

section Lower
variable {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd] [DecidableEq K]

/-- a Gram-`2I` clique has ordered product `I - X Yᵀ` -/
theorem pp_clique (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0) :
    pp x y k = 1 - Xm x k * (Matrix.of fun a (i : Fin k) => y i a)ᵀ := by
  have hz : ∀ i < k, zv x y i = x i := by
    intro i hi
    rw [zv_rec]
    have : ∑ j ∈ range i, (y j ⬝ᵥ x i) • zv x y j = 0 := by
      refine sum_eq_zero fun j hj => ?_
      have := mem_range.1 hj
      rw [hg j (by omega) i hi, if_neg (by omega)]; simp
    rw [this, sub_zero]
  have hZ : Zm x y k = Xm x k := by
    ext a i; simp [Zm, Xm, hz i i.2]
  rw [pp_eq, sum_ZY, hZ]

/-- `rank (X Yᵀ) = k` for a Gram-`2I` clique (char ≠ 2) -/
theorem rank_clique (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0) :
    (Xm x k * (Matrix.of fun a (i : Fin k) => y i a)ᵀ).rank = k := by
  set X := Xm x k
  set Y : Matrix n₁ (Fin k) K := Matrix.of fun a i => y i a
  have hYX : Yᵀ * X = (2 : K) • 1 := by
    ext i j
    rw [gram_apply]
    simp [hg i i.2 j j.2, Matrix.one_apply, Fin.val_inj]
  have h4 : (4 : K) ≠ 0 := by
    have : (4 : K) = 2 * 2 := by norm_num
    rw [this]; exact mul_ne_zero h2 h2
  have e : Yᵀ * (X * Yᵀ) * X = (diagonal fun _ : Fin k => (4 : K)) := by
    have : Yᵀ * (X * Yᵀ) * X = (Yᵀ * X) * (Yᵀ * X) := by simp only [Matrix.mul_assoc]
    rw [this, hYX]
    ext i j
    by_cases h : i = j <;> simp [Matrix.smul_apply, Matrix.one_apply, diagonal_apply, h]; norm_num
  refine le_antisymm ?_ ?_
  · exact (rank_mul_le_left X Yᵀ).trans ((Matrix.rank_le_card_width X).trans (by simp))
  · have h1 : (Yᵀ * (X * Yᵀ) * X).rank ≤ (X * Yᵀ).rank :=
      (rank_mul_le_left _ _).trans (rank_mul_le_right _ _)
    rw [e, rank_diagonal] at h1
    simpa [h4] using h1

/-- **Lemma UR, lower bound.** char ≠ 2. `V = V₁ ⊕ V_dark` (coordinates `n₁ ⊕ nd`). The jobs are the
`k` jobs of a Gram-`2I` clique on `V₁` that are ALL the active jobs of μ, so `J = (ordered product) ⊕ I`;
`D = diag s₁ ⊕ diag sd` (signs). With `r₁` flipped targets in `V₁` and `d` flipped dark targets,
`rank (D - J) ≥ d + |k - r₁|` (written with truncated subtraction; one of the two terms is 0). -/
theorem UR_lower (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1) :
    (univ.filter fun a => sd a = -1).card +
      ((k - (univ.filter fun a => s₁ a = -1).card) + ((univ.filter fun a => s₁ a = -1).card - k))
    ≤ (fromBlocks (diagonal s₁) 0 0 (diagonal sd) - fromBlocks (pp x y k) 0 0 1).rank := by
  set M := Xm x k * (Matrix.of fun a (i : Fin k) => y i a)ᵀ with hM
  set E : Matrix n₁ n₁ K := 1 - diagonal s₁ with hE
  have hMk : M.rank = k := rank_clique h2 k x y hg
  have hEr : E.rank = (univ.filter fun a => s₁ a = -1).card := rank_one_sub_diag h2 s₁ hs₁
  have hBr : ((diagonal sd : Matrix nd nd K) - 1).rank = (univ.filter fun a => sd a = -1).card := by
    rw [← neg_sub, rank_neg_eq]; exact rank_one_sub_diag h2 sd hsd
  have eD : fromBlocks (diagonal s₁) 0 0 (diagonal sd) - fromBlocks (pp x y k) 0 0 1 =
      fromBlocks (M - E) 0 0 (diagonal sd - 1) := by
    rw [pp_clique k x y hg]
    ext (i | i) (j | j) <;> simp [hM, hE, diagonal_apply, Matrix.sub_apply, Matrix.one_apply] <;> ring
  have h1 := rank_le_sub_add M E
  have h3 : E.rank ≤ (M - E).rank + M.rank := by
    have := rank_le_sub_add E M
    rw [← neg_sub, rank_neg_eq] at this
    exact this
  have h4 := rank_fromBlocks_diag_ge (M - E) ((diagonal sd : Matrix nd nd K) - 1)
  rw [eD]
  omega

end Lower

section Combined
variable {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd] [DecidableEq K]

/-- **Lemma UR (combined).** A word in `GL(V₁ ⊕ V_dark)` of `U` unit letters (rank(t - 1) ≤ 1) and the
job letters whose ordered product `J = (Gram-2I clique product) ⊕ I` is ALL the active jobs. If the word
multiplies to `D = diag s₁ ⊕ diag sd`, then `U ≥ d + |k - r₁|`. -/
theorem UR_combined (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hunits : ∀ t, Sum.inl t ∈ w → ((t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) - 1).rank ≤ 1)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp x y k) 0 0 1) :
    (univ.filter fun a => sd a = -1).card +
      ((k - (univ.filter fun a => s₁ a = -1).card) + ((univ.filter fun a => s₁ a = -1).card - k))
    ≤ ucount w := by
  have hu := UR_upper w hunits
  rw [hD, hJ] at hu
  exact (UR_lower h2 k x y hg s₁ sd hs₁ hsd).trans hu

end Combined

/-! ## §4. R26#10 as a worked instance, and sanity checks -/
section Instance

/-- **R26#10**: d = 1 (target 4 dark), r₁ = 0, k = 3 (clique A, C, E at μ = 13, all active jobs).
Character data as hypotheses; conclusion `U ≥ 4`, in particular `U = 3` is impossible. -/
theorem r26_10 {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd]
    [DecidableEq K] (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K)
    (hg : ∀ i < 3, ∀ j < 3, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (hd : (univ.filter fun a => sd a = -1).card = 1)
    (hr1 : (univ.filter fun a => s₁ a = -1).card = 0)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hunits : ∀ t, Sum.inl t ∈ w → ((t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) - 1).rank ≤ 1)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp x y 3) 0 0 1) :
    4 ≤ ucount w ∧ ucount w ≠ 3 := by
  have := UR_combined h2 3 x y hg s₁ sd hs₁ hsd w hunits hD hJ
  rw [hd, hr1] at this
  omega

/-- the pure arithmetic: `d + |k - r₁|` for the six R42 kills, all `4 > 3`. -/
theorem r26_arith :
    (1 + ((3 - 0) + (0 - 3)) = 4) ∧ (2 + ((3 - 1) + (1 - 3)) = 4) := by decide

/-- sanity (non-vacuity of TS): one job `1 - x yᵀ`, `x = e₀`, `y = 2 e₀` on `Fin 2` over ℚ, product
`diag(-1, 1)`, one flipped coordinate; conclusion Gram = 2 holds and the dark coordinate 1 is untouched. -/
example : ∃ (x y : ℕ → Fin 2 → ℚ) (s : Fin 2 → ℚ),
    pp x y 1 = diagonal s ∧ (∀ a, s a = 1 ∨ s a = -1) ∧
    (univ.filter fun a => s a = -1).card = 1 := by
  refine ⟨fun _ => ![1, 0], fun _ => ![2, 0], ![-1, 1], ?_, ?_, ?_⟩
  · ext i j; fin_cases i <;> fin_cases j <;> simp [pp, refl, vecMulVec_apply, diagonal_apply] <;> norm_num
  · intro a; fin_cases a <;> simp
  · decide

/-- the tightness hypothesis `r = k` cannot be dropped: two identical jobs on `Fin 1` multiply to `I`
(`r = 0 < k = 2`), yet the Gram matrix is not `2I` (`y₀·x₁ = 2`). -/
theorem tight_needed : ∃ (x y : ℕ → Fin 1 → ℚ),
    pp x y 2 = diagonal (fun _ => (1 : ℚ)) ∧ y 0 ⬝ᵥ x 1 ≠ 0 := by
  refine ⟨fun _ => ![1], fun _ => ![2], ?_, ?_⟩
  · ext i j; fin_cases i; fin_cases j
    simp [pp, refl, Matrix.mul_apply, Matrix.sub_apply, vecMulVec_apply, Fin.sum_univ_one]; norm_num
  · simp [dotProduct]

end Instance

end SpecTSUR

#print axioms SpecTSUR.lemmaTS
#print axioms SpecTSUR.UR_upper
#print axioms SpecTSUR.UR_lower
#print axioms SpecTSUR.UR_combined
#print axioms SpecTSUR.r26_10
#print axioms SpecTSUR.tight_needed

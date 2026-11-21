import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.BilinearForm
import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Order.WellFounded
import Mathlib.Order.Preorder.Finite
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.NoncommRing
import Mathlib.Tactic.LinearCombination
import Mathlib.Data.Matrix.ColumnRowPartitioned
import Mathlib.Data.Matrix.Block
/-!
NETDOUBLING (lane LEANNETDBL, Nov 20).  Kernel-only (every headline prints only propext, Classical.choice, Quot.sound).
Formalises NETDOUBLE (cards/WILD/NOVEL/netdouble/ND.md).  Defs copied from NetNG.lean / Doubling.lean / TensorPot
conventions (no cross-imports).
 (A) F2 network potential, general row-port / column-port types:  rank_F2 (Q∘(G N F)) ≤ D.
 (M) master form on the PORT-DOUBLED network: rank [[(yNf')∘Q,(yNf)∘Q],[(y'Nf')∘Q,(y'Nf)∘Q]] ≤ D;
     half-integer networks (M̄∘Q=0): rank (yNF̄∘Q) + rank (ḠNf∘Q) ≤ D.
 (T) torsion form (F2[ε]/ε²): rank (yN̄F̄ + ḠN̄h'N̄F̄ + ḠN̄f)∘Q ≤ D when M̄∘Q = 0.
 (N4) mod-4 carry identity: I + X_walk = L(G',F',H')  ⇒  D ≥ rank_F2(I + X_walk); split ⇒ D ≥ n.
-/
open Matrix Finset Module
namespace NetDoubling

section Rank
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι]

lemma rank_add_le' {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n K) :
    (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  have h : LinearMap.range (A + B).mulVecLin ≤
      LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin := by
    rintro _ ⟨x, rfl⟩
    exact Submodule.mem_sup.2 ⟨A.mulVecLin x, ⟨x, rfl⟩, B.mulVecLin x, ⟨x, rfl⟩, by simp [add_mulVec]⟩
  exact (Submodule.finrank_mono h).trans (Submodule.finrank_add_le_finrank_add_finrank _ _)

lemma rank_sum_le {J : Type*} (s : Finset J) (f : J → Matrix ι ι K) :
    (∑ j ∈ s, f j).rank ≤ ∑ j ∈ s, (f j).rank := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    rw [sum_insert ha, sum_insert ha]
    exact (rank_add_le' _ _).trans (Nat.add_le_add_left ih _)

lemma rank_diag_mul_diag_le [DecidableEq ι] (x y : ι → K) (Q : Matrix ι ι K) :
    (diagonal x * Q * diagonal y).rank ≤ Q.rank :=
  (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)

end Rank

/-! ## Block upper-triangular rank -/
section Block
variable {K : Type*} [Field K] {m₁ m₂ n₁ n₂ : Type*} [Fintype m₁] [Fintype m₂] [Fintype n₁] [Fintype n₂]

/-- extension by zero into the left summand. -/
def inlLin (m₁ m₂ : Type*) (K : Type*) [Field K] : (m₁ → K) →ₗ[K] (m₁ ⊕ m₂ → K) where
  toFun z := Sum.elim z 0
  map_add' a b := by ext i; cases i <;> simp
  map_smul' c a := by ext i; cases i <;> simp

lemma inlLin_inj : Function.Injective (inlLin m₁ m₂ K) := by
  intro x y h
  ext i
  have := congrFun h (Sum.inl i)
  simpa [inlLin] using this

theorem rank_fromBlocks_triangular (A : Matrix m₁ n₁ K) (B : Matrix m₁ n₂ K) (D : Matrix m₂ n₂ K) :
    A.rank + D.rank ≤ (fromBlocks A B 0 D).rank := by
  classical
  set M := fromBlocks A B 0 D with hM
  set R : Submodule K (m₁ ⊕ m₂ → K) := LinearMap.range M.mulVecLin with hR
  let p : (m₁ ⊕ m₂ → K) →ₗ[K] (m₂ → K) := LinearMap.funLeft K K Sum.inr
  let g : R →ₗ[K] (m₂ → K) := p.domRestrict R
  have h1 := LinearMap.finrank_range_add_finrank_ker g
  have ha : D.rank ≤ Module.finrank K (LinearMap.range g) := by
    unfold Matrix.rank
    apply Submodule.finrank_mono
    rintro _ ⟨x, rfl⟩
    refine ⟨⟨M.mulVecLin (Sum.elim 0 x), LinearMap.mem_range_self _ _⟩, ?_⟩
    ext j
    simp [g, p, hM, fromBlocks_mulVec]
  have hb : A.rank ≤ Module.finrank K (LinearMap.ker g) := by
    have e1 : Module.finrank K (LinearMap.ker g) =
        Module.finrank K (Submodule.map R.subtype (LinearMap.ker g)) :=
      (Submodule.finrank_map_subtype_eq R (LinearMap.ker g)).symm
    rw [e1]
    have e2 : Module.finrank K (Submodule.map (inlLin m₁ m₂ K) (LinearMap.range A.mulVecLin)) = A.rank :=
      (Submodule.equivMapOfInjective _ inlLin_inj _).finrank_eq.symm
    rw [← e2]
    apply Submodule.finrank_mono
    rintro _ ⟨_, ⟨x, rfl⟩, rfl⟩
    have hx : M.mulVecLin (inlLin n₁ n₂ K x) = inlLin m₁ m₂ K (A.mulVecLin x) := by
      ext i
      cases i <;> simp [inlLin, hM, fromBlocks_mulVec]
    refine ⟨⟨inlLin m₁ m₂ K (A.mulVecLin x), ?_⟩, ?_, rfl⟩
    · rw [← hx]; exact LinearMap.mem_range_self _ _
    · ext j
      simp [g, p, inlLin]
  have h3 : Module.finrank K R = M.rank := rfl
  omega

end Block

/-! ## F2 geometry -/
abbrev V (h : ℕ) := Fin h → ZMod 2

def perp {h : ℕ} (W : Submodule (ZMod 2) (V h)) : Submodule (ZMod 2) (V h) where
  carrier := {y | ∀ x ∈ W, x ⬝ᵥ y = 0}
  add_mem' := by
    intro a b ha hb x hx
    simp [dotProduct_add, ha x hx, hb x hx]
  zero_mem' := by intro x hx; simp
  smul_mem' := by
    intro c y hy x hx
    simp [dotProduct_smul, hy x hx]

theorem mem_perp {h : ℕ} {W : Submodule (ZMod 2) (V h)} {y : V h} :
    y ∈ perp W ↔ ∀ x ∈ W, x ⬝ᵥ y = 0 := Iff.rfl

theorem perp_anti {h : ℕ} {W W' : Submodule (ZMod 2) (V h)} (hle : W ≤ W') : perp W' ≤ perp W :=
  fun _ hy x hx => hy x (hle hx)

noncomputable def Bd (h : ℕ) : LinearMap.BilinForm (ZMod 2) (V h) :=
  Matrix.toBilin' (1 : Matrix (Fin h) (Fin h) (ZMod 2))

theorem Bd_apply {h : ℕ} (x y : V h) : Bd h x y = x ⬝ᵥ y := by
  simp [Bd, Matrix.toBilin'_apply']

theorem finrank_perp {h : ℕ} (W : Submodule (ZMod 2) (V h)) :
    finrank (ZMod 2) (perp W) + finrank (ZMod 2) W = h := by
  have hk : LinearMap.ker (Bd h) = ⊥ := by
    rw [LinearMap.ker_eq_bot']
    intro x hx
    funext i
    have := congrArg (fun f => f (Pi.single i 1)) hx
    simpa [Bd_apply, dotProduct, Pi.single_apply] using this
  have e : perp W = (Bd h).orthogonal W := by
    ext y
    rw [LinearMap.BilinForm.mem_orthogonal_iff]
    simp only [mem_perp, LinearMap.IsOrtho, Bd_apply]
  have := LinearMap.BilinForm.finrank_add_finrank_orthogonal' (B := Bd h) W
  rw [hk, inf_bot_eq, finrank_bot] at this
  have h9 : finrank (ZMod 2) (V h) = h := by simp
  rw [e]; omega

theorem finrank_le_h {h : ℕ} (W : Submodule (ZMod 2) (V h)) : finrank (ZMod 2) W ≤ h := by
  have := finrank_perp W; omega

/-! ## generators of the drop space: perp b = perp a ⊕ span g -/
theorem exists_gens {h : ℕ} (A B : Submodule (ZMod 2) (V h)) (hAB : A ≤ B) (d : ℕ)
    (hd : finrank (ZMod 2) B = finrank (ZMod 2) A + d) :
    ∃ g : Fin d → V h, (∀ i, g i ∈ B) ∧ B ≤ A ⊔ Submodule.span (ZMod 2) (Set.range g) := by
  classical
  obtain ⟨C, hC⟩ := exists_isCompl A
  set W := B ⊓ C with hW
  have hsup : A ⊔ W = B := by
    apply le_antisymm
    · exact sup_le hAB inf_le_left
    · intro v hv
      have : v ∈ A ⊔ C := by rw [hC.sup_eq_top]; trivial
      obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 this
      refine Submodule.mem_sup.2 ⟨x, hx, y, ⟨?_, hy⟩, rfl⟩
      have : y = (x + y) - x := by abel
      rw [this]; exact B.sub_mem hv (hAB hx)
  have hdisj : A ⊓ W = ⊥ := by
    apply eq_bot_iff.2
    calc A ⊓ W ≤ A ⊓ C := inf_le_inf_left _ inf_le_right
      _ = ⊥ := hC.inf_eq_bot
      _ ≤ ⊥ := le_rfl
  have hrk := Submodule.finrank_sup_add_finrank_inf_eq A W
  rw [hsup, hdisj, finrank_bot] at hrk
  have hdW : finrank (ZMod 2) (Submodule.span (ZMod 2) (W : Set (V h))) = d := by
    rw [Submodule.span_eq]; omega
  obtain ⟨g, hgmem, hgspan, -⟩ := Submodule.exists_fun_fin_finrank_span_eq (ZMod 2) (W : Set (V h))
  have hgspan' : Submodule.span (ZMod 2) (Set.range g) = W := hgspan.trans (Submodule.span_eq W)
  subst hdW
  refine ⟨g, fun i => (hgmem i).1, ?_⟩
  exact hsup.symm.le.trans (by rw [hgspan'])

/-! ## F2 networks with row ports ρ and column ports σ -/
section F2net

/-- the linear map v ↦ χ_v ⊙ x, χ_v(p) = v·qc p ∈ F2. -/
def TvL {σ : Type*} {h : ℕ} (qc : σ → V h) (x : σ → ZMod 2) : V h →ₗ[ZMod 2] (σ → ZMod 2) where
  toFun v := fun p => (v ⬝ᵥ qc p) * x p
  map_add' v w := by funext p; simp [add_dotProduct, add_mul]
  map_smul' c v := by funext p; simp [smul_dotProduct, mul_assoc]

theorem TvL_apply {σ : Type*} {h : ℕ} (qc : σ → V h) (x : σ → ZMod 2) (v : V h) (p : σ) :
    TvL qc x v p = (v ⬝ᵥ qc p) * x p := rfl

structure FNet (ρ σ κ : Type*) [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] (h : ℕ) where
  qr : ρ → V h
  qc : σ → V h
  lt : κ → κ → Prop
  ltrans : ∀ a b c, lt a b → lt b c → lt a c
  lirr : ∀ a, ¬ lt a a
  a : κ → Submodule (ZMod 2) (V h)
  b : κ → Submodule (ZMod 2) (V h)
  F : Matrix κ σ (ZMod 2)
  G : Matrix ρ κ (ZMod 2)
  H : Matrix κ κ (ZMod 2)
  N : Matrix κ κ (ZMod 2)
  hba : ∀ k, b k ≤ a k
  hF : ∀ k p, F k p ≠ 0 → qc p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, y ⬝ᵥ qr s = 0
  hHlt : ∀ k j, H k j ≠ 0 → lt j k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hN1 : N = 1 + H * N

variable {ρ σ κ : Type*} [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] {h : ℕ}

noncomputable def FNet.drop (Nt : FNet ρ σ κ h) (k : κ) : ℕ :=
  finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k)

/-- row k of N F: the content. -/
def FNet.R (Nt : FNet ρ σ κ h) : Matrix κ σ (ZMod 2) := Nt.N * Nt.F

theorem FNet.hR (Nt : FNet ρ σ κ h) (k : κ) (p : σ) :
    Nt.R k p = Nt.F k p + ∑ j, Nt.H k j * Nt.R j p := by
  have e : Nt.N * Nt.F = Nt.F + Nt.H * (Nt.N * Nt.F) := by
    calc Nt.N * Nt.F = (1 + Nt.H * Nt.N) * Nt.F := by rw [← Nt.hN1]
      _ = _ := by rw [Matrix.add_mul, Matrix.one_mul, Matrix.mul_assoc]
  have := congrFun (congrFun e k) p
  simpa [FNet.R, Matrix.add_apply, Matrix.mul_apply] using this

/-- a general content matrix satisfying the recursion X = Y + H X. -/
theorem FNet.solve (Nt : FNet ρ σ κ h) (Y : Matrix κ σ (ZMod 2)) (k : κ) (p : σ) :
    (Nt.N * Y) k p = Y k p + ∑ j, Nt.H k j * (Nt.N * Y) j p := by
  have e : Nt.N * Y = Y + Nt.H * (Nt.N * Y) := by
    calc Nt.N * Y = (1 + Nt.H * Nt.N) * Y := by rw [← Nt.hN1]
      _ = _ := by rw [Matrix.add_mul, Matrix.one_mul, Matrix.mul_assoc]
  have := congrFun (congrFun e k) p
  simpa [Matrix.add_apply, Matrix.mul_apply] using this

theorem FNet.e_drop (Nt : FNet ρ σ κ h) (k : κ) :
    finrank (ZMod 2) (perp (Nt.b k)) = finrank (ZMod 2) (perp (Nt.a k)) + Nt.drop k := by
  have p1 : finrank (ZMod 2) (perp (Nt.a k)) + finrank (ZMod 2) (Nt.a k) = h := finrank_perp _
  have p2 : finrank (ZMod 2) (perp (Nt.b k)) + finrank (ZMod 2) (Nt.b k) = h := finrank_perp _
  have hle := Submodule.finrank_mono (Nt.hba k)
  unfold FNet.drop
  omega

/-- χ_u kills F_k for u ⊥ a_k. -/
theorem FNet.chi_F (Nt : FNet ρ σ κ h) (k : κ) (u : V h) (hu : u ∈ perp (Nt.a k)) (p : σ) :
    (u ⬝ᵥ Nt.qc p) * Nt.F k p = 0 := by
  by_cases hF : Nt.F k p = 0
  · simp [hF]
  · have := hu _ (Nt.hF k p hF)
    rw [dotProduct_comm] at this
    rw [this, zero_mul]

theorem FNet.wf (Nt : FNet ρ σ κ h) : WellFounded Nt.lt := by
  haveI : IsTrans κ Nt.lt := ⟨Nt.ltrans⟩
  haveI : Std.Irrefl Nt.lt := ⟨Nt.lirr⟩
  exact Finite.wellFounded_of_trans_of_irrefl _

/-- the F2-span of chart images at node k. -/
def FNet.Pi (Nt : FNet ρ σ κ h) (k : κ) : Submodule (ZMod 2) (σ → ZMod 2) :=
  (perp (Nt.b k)).map (TvL Nt.qc (Nt.R k))

/-- relay closure (F2): for u ⊥ a_k, T_{r_k}(u) = Σ_j H_kj T_{r_j}(u). -/
theorem FNet.T_row (Nt : FNet ρ σ κ h) (k : κ) (u : V h) (hu : u ∈ perp (Nt.a k)) :
    TvL Nt.qc (Nt.R k) u = ∑ j, Nt.H k j • TvL Nt.qc (Nt.R j) u := by
  funext p
  simp only [TvL_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
  rw [Nt.hR k p, mul_add, Nt.chi_F k u hu p, zero_add, Finset.mul_sum]
  refine Finset.sum_congr rfl fun j _ => ?_
  ring

theorem FNet.node_closure (Nt : FNet ρ σ κ h) (k : κ) (g : Fin (finrank (ZMod 2) (perp (Nt.b k)) -
      finrank (ZMod 2) (perp (Nt.a k))) → V h)
    (hg : perp (Nt.b k) ≤ perp (Nt.a k) ⊔ Submodule.span (ZMod 2) (Set.range g))
    (S : Submodule (ZMod 2) (σ → ZMod 2)) (hS : ∀ j, Nt.H k j ≠ 0 → Nt.Pi j ≤ S)
    (hgS : ∀ i, TvL Nt.qc (Nt.R k) (g i) ∈ S) : Nt.Pi k ≤ S := by
  rintro _ ⟨v, hv, rfl⟩
  obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 (hg hv)
  rw [map_add]
  refine S.add_mem ?_ ?_
  · rw [Nt.T_row k x hx]
    refine S.sum_mem fun j _ => ?_
    by_cases hj : Nt.H k j = 0
    · simp [hj]
    · refine S.smul_mem _ ?_
      exact hS j hj ⟨x, perp_anti (Nt.hH k j hj) hx, rfl⟩
  · have : Submodule.span (ZMod 2) (Set.range g) ≤
        S.comap (TvL Nt.qc (Nt.R k)) :=
      Submodule.span_le.2 (by rintro _ ⟨i, rfl⟩; exact hgS i)
    exact this hy

/-- (A) F2 network potential: rank_F2 (Q ∘ (G N F)) ≤ D. -/
theorem FNet.rank_le (Nt : FNet ρ σ κ h) :
    (Matrix.of fun t p => (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p).rank ≤ ∑ k, Nt.drop k := by
  classical
  choose g hgmem hg using fun k => exists_gens (perp (Nt.a k)) (perp (Nt.b k))
    (perp_anti (Nt.hba k)) _ (show finrank (ZMod 2) (perp (Nt.b k)) = finrank (ZMod 2) (perp (Nt.a k)) +
      (finrank (ZMod 2) (perp (Nt.b k)) - finrank (ZMod 2) (perp (Nt.a k))) by
        have := Nt.e_drop k; omega)
  let Γ : Finset (σ → ZMod 2) := Finset.univ.image
    (fun x : (Σ k, Fin (finrank (ZMod 2) (perp (Nt.b k)) - finrank (ZMod 2) (perp (Nt.a k)))) =>
      TvL Nt.qc (Nt.R x.1) (g x.1 x.2))
  let Z := Submodule.span (ZMod 2) (Γ : Set (σ → ZMod 2))
  have hPi : ∀ k, Nt.Pi k ≤ Z := by
    intro k
    induction k using Nt.wf.induction with
    | _ k ih =>
      refine Nt.node_closure k (g k) (hg k) Z (fun j hj => ih j (Nt.hHlt k j hj)) ?_
      intro i
      exact Submodule.subset_span (Finset.mem_coe.2 (Finset.mem_image.2 ⟨⟨k, i⟩, Finset.mem_univ _, rfl⟩))
  have hrow : ∀ t, (Matrix.of fun t p => (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p).row t ∈ Z := by
    intro t
    have key : (Matrix.of fun t p => (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p).row t =
        ∑ k, Nt.G t k • TvL Nt.qc (Nt.R k) (Nt.qr t) := by
      funext p
      simp only [Matrix.row, Matrix.of_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, TvL_apply]
      rw [Matrix.mul_assoc, Matrix.mul_apply, Finset.mul_sum]
      refine Finset.sum_congr rfl fun k _ => ?_
      simp only [FNet.R]
      ring
    rw [key]
    refine Z.sum_mem fun k _ => ?_
    by_cases hk : Nt.G t k = 0
    · simp [hk]
    · exact Z.smul_mem _ (hPi k ⟨Nt.qr t, Nt.hG t k hk, rfl⟩)
  rw [Matrix.rank_eq_finrank_span_row]
  have h1 : Submodule.span (ZMod 2) (Set.range (Matrix.of fun t p => (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p).row) ≤ Z :=
    Submodule.span_le.2 (by rintro _ ⟨t, rfl⟩; exact hrow t)
  refine (Submodule.finrank_mono h1).trans ?_
  have h2 : finrank (ZMod 2) Z ≤ Γ.card := finrank_span_finset_le_card Γ
  refine h2.trans (Finset.card_image_le.trans ?_)
  rw [Finset.card_univ, Fintype.card_sigma]
  simp only [Fintype.card_fin]
  refine Finset.sum_le_sum fun k _ => ?_
  have := Nt.e_drop k
  omega

end F2net


/-! ## (M) master form: the port-doubled network -/
section Master
variable {ρ σ κ : Type*} [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] {h : ℕ}

/-- Q ∘ A with Q_tp = qr_t · qc_p. -/
def qmask (qr : ρ → V h) (qc : σ → V h) (A : Matrix ρ σ (ZMod 2)) : Matrix ρ σ (ZMod 2) :=
  Matrix.of fun t p => (qr t ⬝ᵥ qc p) * A t p

/-- y is chart-legal on the G side (y_k ⊆ L(b_k^⊥)). -/
def LegalY (Nt : FNet ρ σ κ h) (y : Matrix ρ κ (ZMod 2)) : Prop :=
  ∀ s k, y s k ≠ 0 → ∀ w ∈ Nt.b k, w ⬝ᵥ Nt.qr s = 0

/-- f is chart-legal on the F side (f_k ⊆ L(a_k)). -/
def LegalF (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) : Prop :=
  ∀ k p, f k p ≠ 0 → Nt.qc p ∈ Nt.a k

/-- the port-doubled network: ports p ⊔ p', F ← [f' | f], G ← [y ; y'], same charts and H. -/
def FNet.double (Nt : FNet ρ σ κ h) (y y' : Matrix ρ κ (ZMod 2)) (f f' : Matrix κ σ (ZMod 2))
    (hy : LegalY Nt y) (hy' : LegalY Nt y') (hf : LegalF Nt f) (hf' : LegalF Nt f') :
    FNet (ρ ⊕ ρ) (σ ⊕ σ) κ h where
  qr := Sum.elim Nt.qr Nt.qr
  qc := Sum.elim Nt.qc Nt.qc
  lt := Nt.lt
  ltrans := Nt.ltrans
  lirr := Nt.lirr
  a := Nt.a
  b := Nt.b
  F := Matrix.fromCols f' f
  G := Matrix.fromRows y y'
  H := Nt.H
  N := Nt.N
  hba := Nt.hba
  hF := by
    intro k p hne
    rcases p with p | p
    · exact hf' k p hne
    · exact hf k p hne
  hG := by
    intro s k hne
    rcases s with s | s
    · exact hy s k hne
    · exact hy' s k hne
  hHlt := Nt.hHlt
  hH := Nt.hH
  hN1 := Nt.hN1

theorem FNet.double_drop (Nt : FNet ρ σ κ h) (y y' : Matrix ρ κ (ZMod 2)) (f f' : Matrix κ σ (ZMod 2))
    (hy : LegalY Nt y) (hy' : LegalY Nt y') (hf : LegalF Nt f) (hf' : LegalF Nt f') (k : κ) :
    (Nt.double y y' f f' hy hy' hf hf').drop k = Nt.drop k := rfl

theorem double_prod (N : Matrix κ κ (ZMod 2)) (y y' : Matrix ρ κ (ZMod 2)) (f f' : Matrix κ σ (ZMod 2)) :
    Matrix.fromRows y y' * N * Matrix.fromCols f' f =
      Matrix.fromBlocks (y * N * f') (y * N * f) (y' * N * f') (y' * N * f) := by
  rw [Matrix.fromRows_mul, Matrix.fromRows_mul_fromCols]

/-- (M) MASTER FORM.  For all chart-legal y, y', f, f':
  D ≥ rank_F2 [[(y N f')∘Q, (y N f)∘Q], [(y' N f')∘Q, (y' N f)∘Q]]. -/
theorem master_form (Nt : FNet ρ σ κ h) (y y' : Matrix ρ κ (ZMod 2)) (f f' : Matrix κ σ (ZMod 2))
    (hy : LegalY Nt y) (hy' : LegalY Nt y') (hf : LegalF Nt f) (hf' : LegalF Nt f') :
    (Matrix.fromBlocks (qmask Nt.qr Nt.qc (y * Nt.N * f')) (qmask Nt.qr Nt.qc (y * Nt.N * f))
      (qmask Nt.qr Nt.qc (y' * Nt.N * f')) (qmask Nt.qr Nt.qc (y' * Nt.N * f))).rank
      ≤ ∑ k, Nt.drop k := by
  have h1 := (Nt.double y y' f f' hy hy' hf hf').rank_le
  have e : (Matrix.of fun t p => ((Nt.double y y' f f' hy hy' hf hf').qr t ⬝ᵥ
      (Nt.double y y' f f' hy hy' hf hf').qc p) *
      ((Nt.double y y' f f' hy hy' hf hf').G * (Nt.double y y' f f' hy hy' hf hf').N *
        (Nt.double y y' f f' hy hy' hf hf').F) t p) =
      Matrix.fromBlocks (qmask Nt.qr Nt.qc (y * Nt.N * f')) (qmask Nt.qr Nt.qc (y * Nt.N * f))
      (qmask Nt.qr Nt.qc (y' * Nt.N * f')) (qmask Nt.qr Nt.qc (y' * Nt.N * f)) := by
    have hp := double_prod Nt.N y y' f f'
    have hp' : (Nt.double y y' f f' hy hy' hf hf').G * (Nt.double y y' f f' hy hy' hf hf').N *
        (Nt.double y y' f f' hy hy' hf hf').F = _ := hp
    rw [hp']
    ext i j
    rcases i with i | i <;> rcases j with j | j <;> rfl
  rw [e] at h1
  exact h1.trans (Finset.sum_le_sum fun k _ => (Nt.double_drop y y' f f' hy hy' hf hf' k).le)

/-- half-integer (M̄∘Q = 0) corollary: for all legal y, f,
   rank ((y N F̄)∘Q) + rank ((Ḡ N f)∘Q) ≤ D. -/
theorem half_form (Nt : FNet ρ σ κ h)
    (hM0 : ∀ t p, Nt.qr t ⬝ᵥ Nt.qc p = 1 → (Nt.G * Nt.N * Nt.F) t p = 0)
    (y : Matrix ρ κ (ZMod 2)) (f : Matrix κ σ (ZMod 2)) (hy : LegalY Nt y) (hf : LegalF Nt f) :
    (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank + (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank
      ≤ ∑ k, Nt.drop k := by
  have hy' : LegalY Nt Nt.G := fun s k hne => Nt.hG s k hne
  have hf' : LegalF Nt Nt.F := fun k p hne => Nt.hF k p hne
  have h1 := master_form Nt y Nt.G f Nt.F hy hy' hf hf'
  have h0 : qmask Nt.qr Nt.qc (Nt.G * Nt.N * Nt.F) = 0 := by
    ext t p
    simp only [qmask, Matrix.of_apply, Matrix.zero_apply]
    rcases (show Nt.qr t ⬝ᵥ Nt.qc p = 0 ∨ Nt.qr t ⬝ᵥ Nt.qc p = 1 by
      generalize Nt.qr t ⬝ᵥ Nt.qc p = x; revert x; decide) with h0 | h1
    · rw [h0, zero_mul]
    · rw [hM0 t p h1, mul_zero]
  rw [h0] at h1
  exact (rank_fromBlocks_triangular _ _ _).trans h1

theorem rank_qmask_le_card (qr : ρ → V h) (qc : σ → V h) (A : Matrix ρ σ (ZMod 2)) :
    (qmask qr qc A).rank ≤ Fintype.card ρ := Matrix.rank_le_card_height _

/-- ρ_B^net / ρ_A^net as maxima over legal families. -/
noncomputable def rhoB (Nt : FNet ρ σ κ h) : ℕ :=
  sSup {r | ∃ y, LegalY Nt y ∧ r = (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank}
noncomputable def rhoA (Nt : FNet ρ σ κ h) : ℕ :=
  sSup {r | ∃ f, LegalF Nt f ∧ r = (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank}

theorem rhoB_attained (Nt : FNet ρ σ κ h) :
    ∃ y, LegalY Nt y ∧ rhoB Nt = (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank := by
  have hne : {r | ∃ y, LegalY Nt y ∧ r = (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank}.Nonempty :=
    ⟨_, 0, fun s k hne => absurd rfl hne, rfl⟩
  have hb : BddAbove {r | ∃ y, LegalY Nt y ∧ r = (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank} :=
    ⟨Fintype.card ρ, by rintro _ ⟨y, -, rfl⟩; exact rank_qmask_le_card _ _ _⟩
  obtain ⟨y, hy, he⟩ := Nat.sSup_mem hne hb
  exact ⟨y, hy, he⟩

theorem rhoA_attained (Nt : FNet ρ σ κ h) :
    ∃ f, LegalF Nt f ∧ rhoA Nt = (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank := by
  have hne : {r | ∃ f, LegalF Nt f ∧ r = (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank}.Nonempty :=
    ⟨_, 0, fun k p hne => absurd rfl hne, rfl⟩
  have hb : BddAbove {r | ∃ f, LegalF Nt f ∧ r = (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank} :=
    ⟨Fintype.card ρ, by rintro _ ⟨f, -, rfl⟩; exact rank_qmask_le_card _ _ _⟩
  obtain ⟨f, hf, he⟩ := Nat.sSup_mem hne hb
  exact ⟨f, hf, he⟩

/-- NET-DOUBLE (M): D ≥ ρ_B^net + ρ_A^net for half networks. -/
theorem rhoB_add_rhoA_le (Nt : FNet ρ σ κ h)
    (hM0 : ∀ t p, Nt.qr t ⬝ᵥ Nt.qc p = 1 → (Nt.G * Nt.N * Nt.F) t p = 0) :
    rhoB Nt + rhoA Nt ≤ ∑ k, Nt.drop k := by
  obtain ⟨y, hy, e1⟩ := rhoB_attained Nt
  obtain ⟨f, hf, e2⟩ := rhoA_attained Nt
  rw [e1, e2]
  exact half_form Nt hM0 y f hy hf

end Master


/-! ## (T) torsion form over F2[ε]/ε²  -/
section Torsion

/-- dimension bound for the ε-torsion of a module generated by P and ε·P:
    if (0,U) ⊆ P + shift(P) then dim U ≤ dim P  (shift (x,y) = (0,x)). -/
theorem dim_bound {A : Type*} [AddCommGroup A] [Module (ZMod 2) A] [FiniteDimensional (ZMod 2) A]
    (P : Submodule (ZMod 2) (A × A)) (U : Submodule (ZMod 2) A)
    (hU : U.map (LinearMap.inr (ZMod 2) A A) ≤
      P ⊔ P.map ((LinearMap.inr (ZMod 2) A A) ∘ₗ (LinearMap.fst (ZMod 2) A A))) :
    finrank (ZMod 2) U ≤ finrank (ZMod 2) P := by
  classical
  set inr := LinearMap.inr (ZMod 2) A A with hinr
  set fstL := LinearMap.fst (ZMod 2) A A with hfst
  set sh := inr ∘ₗ fstL with hsh
  set W := P ⊔ P.map sh with hW
  have hinj : Function.Injective inr := LinearMap.inr_injective
  have e1 : finrank (ZMod 2) U = finrank (ZMod 2) (U.map inr) :=
    (Submodule.equivMapOfInjective inr hinj U).finrank_eq
  have hmapfst : W.map fstL = P.map fstL := by
    rw [hW, Submodule.map_sup, ← Submodule.map_comp]
    have : fstL ∘ₗ sh = 0 := by
      ext x <;> simp [hsh, hfst, hinr]
    rw [this]; simp
  have e2 : finrank (ZMod 2) (P.map sh) = finrank (ZMod 2) (P.map fstL) := by
    have : P.map sh = (P.map fstL).map inr := by rw [hsh, Submodule.map_comp]
    rw [this]
    exact ((Submodule.equivMapOfInjective inr hinj _).finrank_eq).symm
  have e3 := LinearMap.finrank_range_add_finrank_ker (fstL.domRestrict W)
  rw [LinearMap.range_domRestrict, hmapfst] at e3
  have e4 : finrank (ZMod 2) (LinearMap.ker (fstL.domRestrict W)) =
      finrank (ZMod 2) (W ⊓ LinearMap.ker fstL : Submodule (ZMod 2) (A × A)) := by
    have hm : Submodule.map W.subtype (LinearMap.ker (fstL.domRestrict W)) = W ⊓ LinearMap.ker fstL := by
      ext x
      simp only [Submodule.mem_map, LinearMap.mem_ker, LinearMap.domRestrict_apply, Submodule.mem_inf,
        Submodule.subtype_apply]
      constructor
      · rintro ⟨⟨w, hw⟩, hk, rfl⟩; exact ⟨hw, hk⟩
      · rintro ⟨hw, hk⟩; exact ⟨⟨x, hw⟩, hk, rfl⟩
    rw [← hm]
    exact (Submodule.finrank_map_subtype_eq W _).symm
  have e5 : finrank (ZMod 2) W ≤ finrank (ZMod 2) P + finrank (ZMod 2) (P.map sh) :=
    Submodule.finrank_add_le_finrank_add_finrank P (P.map sh)
  have e6 : finrank (ZMod 2) (U.map inr) ≤ finrank (ZMod 2) (W ⊓ LinearMap.ker fstL : Submodule (ZMod 2) (A × A)) :=
    Submodule.finrank_mono (le_inf hU (by rintro _ ⟨u, -, rfl⟩; simp [hfst, hinr]))
  omega

variable {ρ σ κ : Type*} [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] {h : ℕ}

/-- the pair (x, y) stands for x + ε y in R^σ, R = F2[ε]/ε². -/
abbrev PV (σ : Type*) := (σ → ZMod 2) × (σ → ZMod 2)

/-- ε-shift  (x, y) ↦ (0, x). -/
def shL (σ : Type*) : PV σ →ₗ[ZMod 2] PV σ :=
  (LinearMap.inr (ZMod 2) (σ → ZMod 2) (σ → ZMod 2)) ∘ₗ (LinearMap.fst (ZMod 2) (σ → ZMod 2) (σ → ZMod 2))

theorem shL_apply (x : PV σ) : shL σ x = (0, x.1) := rfl

/-- ε-content: Z = N (f + h' R), the ε-part of N^R F^R. -/
def FNet.Zc (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2)) : Matrix κ σ (ZMod 2) :=
  Nt.N * (f + h' * Nt.R)

theorem FNet.hZ (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2)) (k : κ) (p : σ) :
    Nt.Zc f h' k p = f k p + ∑ j, h' k j * Nt.R j p + ∑ j, Nt.H k j * Nt.Zc f h' j p := by
  have := Nt.solve (f + h' * Nt.R) k p
  simpa [FNet.Zc, Matrix.add_apply, Matrix.mul_apply] using this

/-- the pair of chart images at node k:  v ↦ (χ_v ⊙ r_k, χ_v ⊙ z_k). -/
def FNet.eL (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2)) (k : κ) :
    V h →ₗ[ZMod 2] PV σ :=
  LinearMap.prod (TvL Nt.qc (Nt.R k)) (TvL Nt.qc (Nt.Zc f h' k))

theorem FNet.eL_apply (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2)) (k : κ)
    (v : V h) : Nt.eL f h' k v = (TvL Nt.qc (Nt.R k) v, TvL Nt.qc (Nt.Zc f h' k) v) := rfl

/-- relay closure over R = F2[ε]/ε²: for u ⊥ a_k,
   e_k(u) = Σ_j H_kj e_j(u) + Σ_j h'_kj ε e_j(u). -/
theorem FNet.eL_row (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2))
    (hf : LegalF Nt f) (k : κ) (u : V h) (hu : u ∈ perp (Nt.a k)) :
    Nt.eL f h' k u = ∑ j, Nt.H k j • Nt.eL f h' j u + ∑ j, h' k j • shL σ (Nt.eL f h' j u) := by
  have chi_f : ∀ p, (u ⬝ᵥ Nt.qc p) * f k p = 0 := by
    intro p
    by_cases hfk : f k p = 0
    · simp [hfk]
    · have := hu _ (hf k p hfk)
      rw [dotProduct_comm] at this
      rw [this, zero_mul]
  refine Prod.ext ?_ ?_
  · rw [FNet.eL_apply, Prod.fst_add, Prod.fst_sum, Prod.fst_sum]
    simp only [Prod.smul_fst, shL_apply, FNet.eL_apply, smul_zero, Finset.sum_const_zero, add_zero]
    exact Nt.T_row k u hu
  · rw [FNet.eL_apply, Prod.snd_add, Prod.snd_sum, Prod.snd_sum]
    funext p
    simp only [Prod.smul_snd, shL_apply, FNet.eL_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul,
      Pi.add_apply, TvL_apply]
    rw [Nt.hZ f h' k p]
    have e1 : (u ⬝ᵥ Nt.qc p) * (f k p + ∑ j, h' k j * Nt.R j p + ∑ j, Nt.H k j * Nt.Zc f h' j p) =
        (u ⬝ᵥ Nt.qc p) * f k p + ∑ j, h' k j * ((u ⬝ᵥ Nt.qc p) * Nt.R j p) +
          ∑ j, Nt.H k j * ((u ⬝ᵥ Nt.qc p) * Nt.Zc f h' j p) := by
      simp only [mul_add, Finset.mul_sum]
      congr 1
      · congr 1
        refine Finset.sum_congr rfl fun j _ => ?_
        ring
      · refine Finset.sum_congr rfl fun j _ => ?_
        ring
    rw [e1, chi_f p, zero_add, add_comm]

/-- (T) TORSION FORM.  M̄∘Q = 0 ⇒ rank_F2 ((y N̄F̄ + Ḡ N̄ h' N̄ F̄ + Ḡ N̄ f)∘Q) ≤ D, for chart-legal y, f and
   h' on legal relay edges. -/
theorem torsion_form (Nt : FNet ρ σ κ h)
    (hM0 : ∀ t p, Nt.qr t ⬝ᵥ Nt.qc p = 1 → (Nt.G * Nt.N * Nt.F) t p = 0)
    (y : Matrix ρ κ (ZMod 2)) (f : Matrix κ σ (ZMod 2)) (h' : Matrix κ κ (ZMod 2))
    (hy : LegalY Nt y) (hf : LegalF Nt f) (hh : ∀ k j, h' k j ≠ 0 → Nt.lt j k ∧ Nt.b j ≤ Nt.a k) :
    (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F + Nt.G * Nt.N * h' * Nt.N * Nt.F + Nt.G * Nt.N * f)).rank
      ≤ ∑ k, Nt.drop k := by
  classical
  choose g hgmem hg using fun k => exists_gens (perp (Nt.a k)) (perp (Nt.b k))
    (perp_anti (Nt.hba k)) _ (show finrank (ZMod 2) (perp (Nt.b k)) = finrank (ZMod 2) (perp (Nt.a k)) +
      (finrank (ZMod 2) (perp (Nt.b k)) - finrank (ZMod 2) (perp (Nt.a k))) by
        have := Nt.e_drop k; omega)
  let eg : (Σ k, Fin (finrank (ZMod 2) (perp (Nt.b k)) - finrank (ZMod 2) (perp (Nt.a k)))) → PV σ :=
    fun x => Nt.eL f h' x.1 (g x.1 x.2)
  let P : Submodule (ZMod 2) (PV σ) := Submodule.span (ZMod 2) (Set.range eg)
  let Wb : Submodule (ZMod 2) (PV σ) := P ⊔ P.map (shL σ)
  have hsh : ∀ x ∈ Wb, shL σ x ∈ Wb := by
    intro x hx
    obtain ⟨p, hp, _, ⟨p', hp', rfl⟩, rfl⟩ := Submodule.mem_sup.1 hx
    have : shL σ (shL σ p') = 0 := rfl
    rw [map_add, this, add_zero]
    exact Submodule.mem_sup_right ⟨p, hp, rfl⟩
  have hPW : ∀ k, (perp (Nt.b k)).map (Nt.eL f h' k) ≤ Wb := by
    intro k
    induction k using Nt.wf.induction with
    | _ k ih =>
      rintro _ ⟨v, hv, rfl⟩
      obtain ⟨x, hx, y0, hy0, rfl⟩ := Submodule.mem_sup.1 (hg k hv)
      rw [map_add]
      refine Wb.add_mem ?_ ?_
      · rw [Nt.eL_row f h' hf k x hx]
        refine Wb.add_mem (Wb.sum_mem fun j _ => ?_) (Wb.sum_mem fun j _ => ?_)
        · by_cases hj : Nt.H k j = 0
          · simp [hj]
          · exact Wb.smul_mem _ (ih j (Nt.hHlt k j hj) ⟨x, perp_anti (Nt.hH k j hj) hx, rfl⟩)
        · by_cases hj : h' k j = 0
          · simp [hj]
          · obtain ⟨hl, hb⟩ := hh k j hj
            exact Wb.smul_mem _ (hsh _ (ih j hl ⟨x, perp_anti hb hx, rfl⟩))
      · have : Submodule.span (ZMod 2) (Set.range (g k)) ≤ Wb.comap (Nt.eL f h' k) := by
          refine Submodule.span_le.2 ?_
          rintro _ ⟨i, rfl⟩
          exact Submodule.mem_sup_left (Submodule.subset_span ⟨⟨k, i⟩, rfl⟩)
        exact this hy0
  -- rows of the masked matrix lie in {0} × Wb
  set Lm := qmask Nt.qr Nt.qc (y * Nt.N * Nt.F + Nt.G * Nt.N * h' * Nt.N * Nt.F + Nt.G * Nt.N * f) with hLm
  have hsplit : y * Nt.N * Nt.F + Nt.G * Nt.N * h' * Nt.N * Nt.F + Nt.G * Nt.N * f =
      y * Nt.R + Nt.G * Nt.Zc f h' := by
    simp only [FNet.R, FNet.Zc, Matrix.mul_add, Matrix.mul_assoc]
    abel
  have hLmrow : ∀ t p, Lm t p = (Nt.qr t ⬝ᵥ Nt.qc p) * (y * Nt.R + Nt.G * Nt.Zc f h') t p := by
    intro t p
    rw [hLm, hsplit]
    rfl
  have hrow : ∀ t, (0, Lm.row t) ∈ Wb := by
    intro t
    have key : ((0 : σ → ZMod 2), Lm.row t) =
        ∑ k, Nt.G t k • Nt.eL f h' k (Nt.qr t) + ∑ k, y t k • shL σ (Nt.eL f h' k (Nt.qr t)) := by
      refine Prod.ext ?_ ?_
      · rw [Prod.fst_add, Prod.fst_sum, Prod.fst_sum]
        funext p
        simp only [Prod.smul_fst, shL_apply, FNet.eL_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul,
          Pi.add_apply, TvL_apply, Pi.zero_apply, smul_zero, Finset.sum_const_zero, add_zero]
        have h0 : (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p = 0 := by
          rcases (show Nt.qr t ⬝ᵥ Nt.qc p = 0 ∨ Nt.qr t ⬝ᵥ Nt.qc p = 1 by
            generalize Nt.qr t ⬝ᵥ Nt.qc p = x; revert x; decide) with h0 | h1
          · rw [h0, zero_mul]
          · rw [hM0 t p h1, mul_zero]
        have hsum : ∑ k, Nt.G t k * ((Nt.qr t ⬝ᵥ Nt.qc p) * Nt.R k p) =
            (Nt.qr t ⬝ᵥ Nt.qc p) * (Nt.G * Nt.N * Nt.F) t p := by
          rw [Matrix.mul_assoc, Matrix.mul_apply, Finset.mul_sum]
          refine Finset.sum_congr rfl fun k _ => ?_
          simp only [FNet.R]
          ring
        exact (hsum.trans h0).symm
      · rw [Prod.snd_add, Prod.snd_sum, Prod.snd_sum]
        funext p
        have e := hLmrow t p
        simp only [Prod.smul_snd, shL_apply, FNet.eL_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul,
          Pi.add_apply, TvL_apply]
        show Lm t p = _
        rw [e]
        simp only [Matrix.add_apply, Matrix.mul_apply, mul_add, Finset.mul_sum]
        rw [add_comm]
        congr 1 <;> exact Finset.sum_congr rfl fun k _ => by ring
    rw [key]
    refine Wb.add_mem (Wb.sum_mem fun k _ => ?_) (Wb.sum_mem fun k _ => ?_)
    · by_cases hk : Nt.G t k = 0
      · simp [hk]
      · exact Wb.smul_mem _ (hPW k ⟨Nt.qr t, Nt.hG t k hk, rfl⟩)
    · by_cases hk : y t k = 0
      · simp [hk]
      · exact Wb.smul_mem _ (hsh _ (hPW k ⟨Nt.qr t, hy t k hk, rfl⟩))
  rw [Matrix.rank_eq_finrank_span_row]
  have hU : (Submodule.span (ZMod 2) (Set.range Lm.row)).map (LinearMap.inr (ZMod 2) (σ → ZMod 2) (σ → ZMod 2))
      ≤ P ⊔ P.map (shL σ) := by
    rw [Submodule.map_span]
    refine Submodule.span_le.2 ?_
    rintro _ ⟨_, ⟨t, rfl⟩, rfl⟩
    exact hrow t
  refine (dim_bound P _ hU).trans ?_
  have h2 : finrank (ZMod 2) P ≤ (Finset.univ.image eg).card := by
    have := finrank_span_finset_le_card (R := ZMod 2) (Finset.univ.image eg)
    have e : ((Finset.univ.image eg : Finset (PV σ)) : Set (PV σ)) = Set.range eg := by simp
    rw [e] at this
    exact this
  refine h2.trans (Finset.card_image_le.trans ?_)
  rw [Finset.card_univ, Fintype.card_sigma]
  simp only [Fintype.card_fin]
  refine Finset.sum_le_sum fun k _ => ?_
  have := Nt.e_drop k
  omega

end Torsion

/-! ## Net4 (copied from NetNG) and its mod-2 reduction -/
section Net4sec

structure Net4 (ι κ : Type*) [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ] (h : ℕ) where
  q : ι → V h
  hodd : ∀ p, q p ⬝ᵥ q p = 1
  lt : κ → κ → Prop
  ltrans : ∀ a b c, lt a b → lt b c → lt a c
  lirr : ∀ a, ¬ lt a a
  a : κ → Submodule (ZMod 2) (V h)
  b : κ → Submodule (ZMod 2) (V h)
  F : Matrix κ ι (ZMod 4)
  G : Matrix ι κ (ZMod 4)
  H : Matrix κ κ (ZMod 4)
  N : Matrix κ κ (ZMod 4)
  c : ι → ZMod 4
  hba : ∀ k, b k ≤ a k
  hF : ∀ k p, F k p ≠ 0 → q p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, y ⬝ᵥ q s = 0
  hHlt : ∀ k j, H k j ≠ 0 → lt j k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hN1 : N = 1 + H * N
  hN2 : N = 1 + N * H
  hc : ∀ s, c s ≠ 0
  hM : ∀ s p, q s ⬝ᵥ q p = 1 → (G * N * F) s p = if s = p then c s else 0

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ] {h : ℕ}

/-- reduction mod 2. -/
def ψ : ZMod 4 →+* ZMod 2 := ZMod.castHom (by decide : 2 ∣ 4) (ZMod 2)

noncomputable def Net4.drop (Nt : Net4 ι κ h) (k : κ) : ℕ :=
  finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k)

/-- the F2 network F̄, Ḡ, H̄, N̄ of a Z/4 network. -/
def Net4.red (Nt : Net4 ι κ h) : FNet ι ι κ h where
  qr := Nt.q
  qc := Nt.q
  lt := Nt.lt
  ltrans := Nt.ltrans
  lirr := Nt.lirr
  a := Nt.a
  b := Nt.b
  F := Nt.F.map ψ
  G := Nt.G.map ψ
  H := Nt.H.map ψ
  N := Nt.N.map ψ
  hba := Nt.hba
  hF := fun k p hne => Nt.hF k p (fun h0 => hne (by simp [Matrix.map_apply, h0]))
  hG := fun s k hne => Nt.hG s k (fun h0 => hne (by simp [Matrix.map_apply, h0]))
  hHlt := fun k j hne => Nt.hHlt k j (fun h0 => hne (by simp [Matrix.map_apply, h0]))
  hH := fun k j hne => Nt.hH k j (fun h0 => hne (by simp [Matrix.map_apply, h0]))
  hN1 := by
    have := congrArg ψ.mapMatrix Nt.hN1
    simpa [map_add, map_mul, map_one] using this

theorem Net4.red_drop (Nt : Net4 ι κ h) (k : κ) : Nt.red.drop k = Nt.drop k := rfl

theorem psi_two : ψ (2 : ZMod 4) = 0 := by decide

/-- half-integer networks (c = 2, i.e. v₂(c) = 1): M̄∘Q = 0. -/
theorem Net4.hM0 (Nt : Net4 ι κ h) (hc2 : ∀ s, Nt.c s = 2) :
    ∀ t p, Nt.red.qr t ⬝ᵥ Nt.red.qc p = 1 → (Nt.red.G * Nt.red.N * Nt.red.F) t p = 0 := by
  intro t p hq
  have e : Nt.red.G * Nt.red.N * Nt.red.F = ψ.mapMatrix (Nt.G * Nt.N * Nt.F) := by
    simp [Net4.red, map_mul]
  rw [e, RingHom.mapMatrix_apply, Matrix.map_apply, Nt.hM t p hq]
  split_ifs
  · rw [hc2]; exact psi_two
  · exact map_zero ψ

/-- (M) for Z/4 half-integer networks: D ≥ ρ_B^net + ρ_A^net. -/
theorem Net4.half_master (Nt : Net4 ι κ h) (hc2 : ∀ s, Nt.c s = 2) :
    rhoB Nt.red + rhoA Nt.red ≤ ∑ k, Nt.drop k :=
  rhoB_add_rhoA_le Nt.red (Nt.hM0 hc2)

end Net4sec

/-! ## (N4) the mod-4 carry identity  I + X_walk = L(G',F',H') -/
section Carry

lemma two_two {m n : Type*} (X : Matrix m n (ZMod 4)) : (2 : ZMod 4) • (2 : ZMod 4) • X = 0 := by
  rw [smul_smul]
  have : (2 : ZMod 4) * 2 = 0 := by decide
  rw [this, zero_smul]

section alg
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

lemma alg_prod (Gh Gp : Matrix ι κ (ZMod 4)) (Nh Hp : Matrix κ κ (ZMod 4)) (Fh Fp : Matrix κ ι (ZMod 4)) :
    (Gh + (2 : ZMod 4) • Gp) * (Nh + (2 : ZMod 4) • (Nh * Hp * Nh)) * (Fh + (2 : ZMod 4) • Fp) =
      Gh * Nh * Fh + (2 : ZMod 4) • (Gp * Nh * Fh + Gh * Nh * Hp * Nh * Fh + Gh * Nh * Fp) := by
  simp only [Matrix.add_mul, Matrix.mul_add, Matrix.smul_mul, Matrix.mul_smul, smul_add]
  simp only [Matrix.mul_assoc, two_two, add_zero]
  abel

lemma alg_inv (Hh Hp Nh : Matrix κ κ (ZMod 4)) (hA : (1 - Hh) * Nh = 1) :
    (1 - (Hh + (2 : ZMod 4) • Hp)) * (Nh + (2 : ZMod 4) • (Nh * Hp * Nh)) = 1 := by
  have e : (1 - (Hh + (2 : ZMod 4) • Hp)) = (1 - Hh) - (2 : ZMod 4) • Hp := by abel
  have hX : (1 - Hh) * (Nh * Hp * Nh) = Hp * Nh := by
    rw [← Matrix.mul_assoc, ← Matrix.mul_assoc, hA, Matrix.one_mul]
  rw [e, sub_mul, mul_add, mul_add, hA, mul_smul_comm, hX, smul_mul_assoc, smul_mul_assoc, mul_smul_comm,
    two_two]
  abel
end alg

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ] {h : ℕ}

/-- binary digits of a Z/4 element. -/
def dg0 (x : ZMod 4) : ZMod 4 := ((x.val % 2 : ℕ) : ZMod 4)
def dg1 (x : ZMod 4) : ZMod 4 := ((x.val / 2 : ℕ) : ZMod 4)
lemma dg_decomp (x : ZMod 4) : x = dg0 x + 2 * dg1 x := by unfold dg0 dg1; revert x; decide
lemma psi_dg0 (x : ZMod 4) : ψ (dg0 x) = ψ x := by unfold dg0; revert x; decide
lemma dg1_ne (x : ZMod 4) (hx : dg1 x ≠ 0) : x ≠ 0 := by
  unfold dg1 at hx; revert x; decide
lemma dg0_ne (x : ZMod 4) (hx : dg0 x ≠ 0) : x ≠ 0 := by
  unfold dg0 at hx; revert x; decide

/-- 2·x only depends on x mod 2. -/
def emb (x : ZMod 2) : ZMod 4 := 2 * ((x.val : ℕ) : ZMod 4)
lemma two_mul_eq_emb (x : ZMod 4) : 2 * x = emb (ψ x) := by unfold emb; revert x; decide

lemma half_aux : ∀ d l : ZMod 2, (((((emb d - emb l).val : ℕ) : ℤ) / 2 : ℤ) : ZMod 2) = d + l := by
  unfold emb; decide

lemma half_cast (c : ℤ) : ((c / 2 : ℤ) : ZMod 2) = (((c % 4) / 2 : ℤ) : ZMod 2) := by
  have e : c / 2 = (c % 4) / 2 + 2 * (c / 4) := by omega
  have h2 : (2 : ZMod 2) = 0 := by decide
  rw [e]; push_cast; rw [h2]; simp

/-- integer carry: c + 2l ≡ 2d (mod 4)  ⇒  ⌊c/2⌋ ≡ d + l (mod 2). -/
lemma half_lemma (c : ℤ) (d l : ZMod 2) (h : (c : ZMod 4) + emb l = emb d) :
    ((c / 2 : ℤ) : ZMod 2) = d + l := by
  have h' : (c : ZMod 4) = emb d - emb l := eq_sub_of_add_eq h
  have hm : c % 4 = (((emb d - emb l).val : ℕ) : ℤ) := by
    have hv : (((c : ZMod 4).val : ℕ) : ℤ) = c % ((4 : ℕ) : ℤ) := ZMod.val_intCast c
    rw [h'] at hv
    simpa using hv.symm
  rw [half_cast, hm]
  exact half_aux d l

def Net4.Ghat (Nt : Net4 ι κ h) : Matrix ι κ ℤ := Nt.G.map (fun x => ((x.val % 2 : ℕ) : ℤ))
def Net4.Fhat (Nt : Net4 ι κ h) : Matrix κ ι ℤ := Nt.F.map (fun x => ((x.val % 2 : ℕ) : ℤ))
def Net4.Hhat (Nt : Net4 ι κ h) : Matrix κ κ ℤ := Nt.H.map (fun x => ((x.val % 2 : ℕ) : ℤ))
/-- the second binary digit (G', F', H') over F2. -/
def Net4.Gp (Nt : Net4 ι κ h) : Matrix ι κ (ZMod 2) := Nt.G.map (fun x => ψ (dg1 x))
def Net4.Fp (Nt : Net4 ι κ h) : Matrix κ ι (ZMod 2) := Nt.F.map (fun x => ψ (dg1 x))
def Net4.Hp (Nt : Net4 ι κ h) : Matrix κ κ (ZMod 2) := Nt.H.map (fun x => ψ (dg1 x))

/-- X_walk := Q ∘ (cover / 2) mod 2, cover = Ĝ Ñ F̂ (Ñ = Σ Ĥ^i the integer walk-count matrix, given here
as the integer inverse of 1 - Ĥ). -/
def Net4.Xw (Nt : Net4 ι κ h) (Nti : Matrix κ κ ℤ) : Matrix ι ι (ZMod 2) :=
  Matrix.of fun t s => (Nt.q t ⬝ᵥ Nt.q s) * ((((Nt.Ghat * Nti * Nt.Fhat) t s) / 2 : ℤ) : ZMod 2)

theorem zmod2_cases (a : ZMod 2) : a = 0 ∨ a = 1 := by revert a; decide

theorem map_add_psi {m n : Type*} (A B : Matrix m n (ZMod 4)) : (A + B).map ψ = A.map ψ + B.map ψ := by
  ext i j; simp

theorem Net4.carry (Nt : Net4 ι κ h) (hc2 : ∀ s, Nt.c s = 2) (Nti : Matrix κ κ ℤ)
    (hN : Nti = 1 + Nt.Hhat * Nti) :
    1 + Nt.Xw Nti = qmask Nt.q Nt.q (Nt.Gp * Nt.red.N * Nt.red.F +
      Nt.red.G * Nt.red.N * Nt.Hp * Nt.red.N * Nt.red.F + Nt.red.G * Nt.red.N * Nt.Fp) := by
  classical
  let ζ : ℤ →+* ZMod 4 := Int.castRingHom (ZMod 4)
  have hGd : Nt.G = Nt.G.map dg0 + (2 : ZMod 4) • Nt.G.map dg1 := by
    ext i j; simp only [Matrix.add_apply, Matrix.smul_apply, Matrix.map_apply, smul_eq_mul]; exact dg_decomp _
  have hFd : Nt.F = Nt.F.map dg0 + (2 : ZMod 4) • Nt.F.map dg1 := by
    ext i j; simp only [Matrix.add_apply, Matrix.smul_apply, Matrix.map_apply, smul_eq_mul]; exact dg_decomp _
  have hHd : Nt.H = Nt.H.map dg0 + (2 : ZMod 4) • Nt.H.map dg1 := by
    ext i j; simp only [Matrix.add_apply, Matrix.smul_apply, Matrix.map_apply, smul_eq_mul]; exact dg_decomp _
  have hGhat : Nt.Ghat.map ζ = Nt.G.map dg0 := by
    ext i j; simp only [Net4.Ghat, Matrix.map_apply, dg0]; exact map_natCast ζ _
  have hFhat : Nt.Fhat.map ζ = Nt.F.map dg0 := by
    ext i j; simp only [Net4.Fhat, Matrix.map_apply, dg0]; exact map_natCast ζ _
  have hHhat : Nt.Hhat.map ζ = Nt.H.map dg0 := by
    ext i j; simp only [Net4.Hhat, Matrix.map_apply, dg0]; exact map_natCast ζ _
  let N4t : Matrix κ κ (ZMod 4) := Nti.map ζ
  have hA' : N4t = 1 + Nt.H.map dg0 * N4t := by
    have := congrArg ζ.mapMatrix hN
    rw [map_add, map_mul, map_one] at this
    simp only [RingHom.mapMatrix_apply, hHhat] at this
    exact this
  have hA : (1 - Nt.H.map dg0) * N4t = 1 := by
    rw [sub_mul, one_mul]; exact sub_eq_of_eq_add hA'
  have hE : Nt.N = N4t + (2 : ZMod 4) • (N4t * Nt.H.map dg1 * N4t) := by
    have h1 := alg_inv (Nt.H.map dg0) (Nt.H.map dg1) N4t hA
    rw [← hHd] at h1
    have h2 : Nt.N * (1 - Nt.H) = 1 := by
      rw [Matrix.mul_sub, Matrix.mul_one]; exact sub_eq_of_eq_add Nt.hN2
    calc Nt.N = Nt.N * ((1 - Nt.H) * (N4t + (2 : ZMod 4) • (N4t * Nt.H.map dg1 * N4t))) := by
          rw [h1, Matrix.mul_one]
      _ = (Nt.N * (1 - Nt.H)) * (N4t + (2 : ZMod 4) • (N4t * Nt.H.map dg1 * N4t)) :=
          (Matrix.mul_assoc _ _ _).symm
      _ = _ := by rw [h2, Matrix.one_mul]
  have hMexp : Nt.G * Nt.N * Nt.F = Nt.G.map dg0 * N4t * Nt.F.map dg0 + (2 : ZMod 4) •
      (Nt.G.map dg1 * N4t * Nt.F.map dg0 + Nt.G.map dg0 * N4t * Nt.H.map dg1 * N4t * Nt.F.map dg0 +
        Nt.G.map dg0 * N4t * Nt.F.map dg1) := by
    have := alg_prod (Nt.G.map dg0) (Nt.G.map dg1) N4t (Nt.H.map dg1) (Nt.F.map dg0) (Nt.F.map dg1)
    rw [← hGd, ← hE, ← hFd] at this
    exact this
  have hcov : (Nt.Ghat * Nti * Nt.Fhat).map ζ = Nt.G.map dg0 * N4t * Nt.F.map dg0 := by
    rw [Matrix.map_mul, Matrix.map_mul, hGhat, hFhat]
  have hNψ : N4t.map ψ = Nt.red.N := by
    ext i j
    have := congrFun (congrFun hE i) j
    simp only [Matrix.add_apply, Matrix.smul_apply, smul_eq_mul] at this
    simp only [Matrix.map_apply, Net4.red]
    rw [this, map_add, map_mul, psi_two, zero_mul, add_zero]
  have hGψ0 : (Nt.G.map dg0).map ψ = Nt.red.G := by
    ext i j; simp [Net4.red, Matrix.map_apply, psi_dg0]
  have hFψ0 : (Nt.F.map dg0).map ψ = Nt.red.F := by
    ext i j; simp [Net4.red, Matrix.map_apply, psi_dg0]
  have hGψ1 : (Nt.G.map dg1).map ψ = Nt.Gp := by
    ext i j; simp [Net4.Gp, Matrix.map_apply]
  have hFψ1 : (Nt.F.map dg1).map ψ = Nt.Fp := by
    ext i j; simp [Net4.Fp, Matrix.map_apply]
  have hHψ1 : (Nt.H.map dg1).map ψ = Nt.Hp := by
    ext i j; simp [Net4.Hp, Matrix.map_apply]
  have hBR : (Nt.G.map dg1 * N4t * Nt.F.map dg0 + Nt.G.map dg0 * N4t * Nt.H.map dg1 * N4t *
      Nt.F.map dg0 + Nt.G.map dg0 * N4t * Nt.F.map dg1).map ψ =
      Nt.Gp * Nt.red.N * Nt.red.F + Nt.red.G * Nt.red.N * Nt.Hp * Nt.red.N * Nt.red.F +
        Nt.red.G * Nt.red.N * Nt.Fp := by
    simp only [map_add_psi, Matrix.map_mul, hNψ, hGψ0, hFψ0, hGψ1, hFψ1, hHψ1]
  generalize hBRg : (Nt.G.map dg1 * N4t * Nt.F.map dg0 + Nt.G.map dg0 * N4t * Nt.H.map dg1 * N4t *
      Nt.F.map dg0 + Nt.G.map dg0 * N4t * Nt.F.map dg1) = BR at hMexp hBR
  ext t s
  rcases zmod2_cases (Nt.q t ⬝ᵥ Nt.q s) with h0 | h1
  · have hts : t ≠ s := by rintro rfl; rw [Nt.hodd] at h0; exact one_ne_zero h0
    simp [Net4.Xw, qmask, h0, Matrix.one_apply_ne hts]
  · have hMts := Nt.hM t s h1
    have hψBR : ψ (BR t s) = (Nt.Gp * Nt.red.N * Nt.red.F + Nt.red.G * Nt.red.N * Nt.Hp * Nt.red.N *
        Nt.red.F + Nt.red.G * Nt.red.N * Nt.Fp) t s := by
      have := congrFun (congrFun hBR t) s
      rwa [Matrix.map_apply] at this
    have hcovz : ζ ((Nt.Ghat * Nti * Nt.Fhat) t s) = (Nt.G.map dg0 * N4t * Nt.F.map dg0) t s := by
      have := congrFun (congrFun hcov t) s
      rwa [Matrix.map_apply] at this
    have hh : (((Nt.Ghat * Nti * Nt.Fhat) t s : ℤ) : ZMod 4) + emb (ψ (BR t s)) =
        emb (if t = s then 1 else 0) := by
      rw [← two_mul_eq_emb]
      have e : ζ ((Nt.Ghat * Nti * Nt.Fhat) t s) + 2 * BR t s = (Nt.G * Nt.N * Nt.F) t s := by
        rw [hMexp, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul, hcovz]
      have e2 : ((((Nt.Ghat * Nti * Nt.Fhat) t s : ℤ)) : ZMod 4) =
          ζ ((Nt.Ghat * Nti * Nt.Fhat) t s) := rfl
      rw [e2, e, hMts]
      by_cases hts : t = s
      · simp only [hts, if_true, hc2]
        decide
      · simp only [hts, if_false]
        decide
    have hx := half_lemma _ _ _ hh
    have hL : (qmask Nt.q Nt.q (Nt.Gp * Nt.red.N * Nt.red.F + Nt.red.G * Nt.red.N * Nt.Hp * Nt.red.N *
        Nt.red.F + Nt.red.G * Nt.red.N * Nt.Fp)) t s = ψ (BR t s) := by
      rw [hψBR]
      simp only [qmask, Matrix.of_apply, h1, one_mul]
    rw [hL, Matrix.add_apply]
    simp only [Net4.Xw, Matrix.of_apply, h1, one_mul]
    rw [hx, Matrix.one_apply]
    generalize (if t = s then (1 : ZMod 2) else 0) = d
    generalize ψ (BR t s) = l
    revert d l; decide

/-! ### headline theorems -/

theorem psi_zero_of_dg1 (x : ZMod 4) (hx : ψ (dg1 x) ≠ 0) : x ≠ 0 := by
  revert x; decide

/-- (T) HEADLINE: D ≥ rank_F2(I + X_walk) for half-integer Z/4 networks (any relays, incl. even scalars). -/
theorem Net4.torsion_headline (Nt : Net4 ι κ h) (hc2 : ∀ s, Nt.c s = 2) (Nti : Matrix κ κ ℤ)
    (hN : Nti = 1 + Nt.Hhat * Nti) :
    (1 + Nt.Xw Nti).rank ≤ ∑ k, Nt.drop k := by
  rw [Nt.carry hc2 Nti hN]
  have hy : LegalY Nt.red Nt.Gp := by
    intro s k hne
    exact Nt.hG s k (psi_zero_of_dg1 _ hne)
  have hf : LegalF Nt.red Nt.Fp := by
    intro k p hne
    exact Nt.hF k p (psi_zero_of_dg1 _ hne)
  have hh : ∀ k j, Nt.Hp k j ≠ 0 → Nt.red.lt j k ∧ Nt.red.b j ≤ Nt.red.a k := by
    intro k j hne
    have hH0 := psi_zero_of_dg1 _ hne
    exact ⟨Nt.hHlt k j hH0, Nt.hH k j hH0⟩
  exact torsion_form Nt.red (Nt.hM0 hc2) Nt.Gp Nt.Fp Nt.Hp hy hf hh

lemma psi_eq_zero_of (x : ZMod 4) (hx : ψ x = 0) : (((x.val % 2 : ℕ)) : ℤ) = 0 := by
  revert x; decide

theorem Net4.Xw_zero (Nt : Net4 ι κ h) (Nti : Matrix κ κ ℤ) (t s : ι)
    (hrc : (∀ k, Nt.red.G t k = 0) ∨ (∀ k, Nt.red.F k s = 0)) : Nt.Xw Nti t s = 0 := by
  have hcov : (Nt.Ghat * Nti * Nt.Fhat) t s = 0 := by
    rcases hrc with hr | hc
    · rw [Matrix.mul_assoc, Matrix.mul_apply]
      refine Finset.sum_eq_zero fun k _ => ?_
      have : Nt.Ghat t k = 0 := psi_eq_zero_of _ (hr k)
      simp [this]
    · rw [Matrix.mul_apply]
      refine Finset.sum_eq_zero fun k _ => ?_
      have : Nt.Fhat k s = 0 := psi_eq_zero_of _ (hc k)
      simp [this]
  simp [Net4.Xw, hcov]

/-- SPLIT networks (no port both odd-read and odd-gathered): D ≥ n. -/
theorem Net4.split_headline (Nt : Net4 ι κ h) (hc2 : ∀ s, Nt.c s = 2) (Nti : Matrix κ κ ℤ)
    (hN : Nti = 1 + Nt.Hhat * Nti)
    (hsplit : ∀ t, (∀ k, Nt.red.G t k = 0) ∨ (∀ k, Nt.red.F k t = 0)) :
    Fintype.card ι ≤ ∑ k, Nt.drop k := by
  have hXX : Nt.Xw Nti * Nt.Xw Nti = 0 := by
    ext t u
    rw [Matrix.mul_apply]
    refine Finset.sum_eq_zero fun s _ => ?_
    rcases hsplit s with h | h
    · rw [Nt.Xw_zero Nti s u (Or.inl h)]; simp
    · rw [Nt.Xw_zero Nti t s (Or.inr h)]; simp
  have hX2 : Nt.Xw Nti + Nt.Xw Nti = 0 := by
    ext t s
    simp only [Matrix.add_apply, Matrix.zero_apply]
    generalize Nt.Xw Nti t s = x
    revert x; decide
  have hinv : (1 + Nt.Xw Nti) * (1 + Nt.Xw Nti) = 1 := by
    have : (1 + Nt.Xw Nti) * (1 + Nt.Xw Nti) = 1 + (Nt.Xw Nti + Nt.Xw Nti) + Nt.Xw Nti * Nt.Xw Nti := by
      noncomm_ring
    rw [this, hX2, hXX]; simp
  have h1 : Fintype.card ι = (1 : Matrix ι ι (ZMod 2)).rank := (Matrix.rank_one).symm
  rw [h1, ← hinv]
  exact (Matrix.rank_mul_le_left _ _).trans (Nt.torsion_headline hc2 Nti hN)

end Carry

/-! ## non-vacuity -/
section Inst

theorem le_rhoB {ρ σ κ : Type*} [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] {h : ℕ}
    (Nt : FNet ρ σ κ h) (y : Matrix ρ κ (ZMod 2)) (hy : LegalY Nt y) :
    (qmask Nt.qr Nt.qc (y * Nt.N * Nt.F)).rank ≤ rhoB Nt :=
  le_csSup ⟨Fintype.card ρ, by rintro _ ⟨y, -, rfl⟩; exact rank_qmask_le_card _ _ _⟩ ⟨y, hy, rfl⟩

theorem le_rhoA {ρ σ κ : Type*} [Fintype ρ] [Fintype σ] [Fintype κ] [DecidableEq κ] {h : ℕ}
    (Nt : FNet ρ σ κ h) (f : Matrix κ σ (ZMod 2)) (hf : LegalF Nt f) :
    (qmask Nt.qr Nt.qc (Nt.G * Nt.N * f)).rank ≤ rhoA Nt :=
  le_csSup ⟨Fintype.card ρ, by rintro _ ⟨f, -, rfl⟩; exact rank_qmask_le_card _ _ _⟩ ⟨f, hf, rfl⟩

/-- tight half-integer relay-free instance: n = 1, h = 1, F = 2. -/
def net1h : Net4 (Fin 1) (Fin 1) 1 where
  q := ![![1]]
  hodd := by decide
  lt := fun _ _ => False
  ltrans := by decide
  lirr := by decide
  a := fun _ => ⊤
  b := fun _ => ⊥
  F := Matrix.of ![![2]]
  G := Matrix.of ![![1]]
  H := 0
  N := 1
  c := ![2]
  hba := fun _ => bot_le
  hF := fun _ _ _ => Submodule.mem_top
  hG := fun s k _ y hy => by
    rw [Submodule.mem_bot] at hy; subst hy; simp
  hHlt := fun k j hne => absurd (Matrix.zero_apply k j) hne
  hH := fun _ _ _ => bot_le
  hN1 := by decide
  hN2 := by decide
  hc := by decide
  hM := by decide

theorem net1h_c : ∀ s, net1h.c s = 2 := by decide

theorem net1h_drop : ∑ k, net1h.drop k = 1 := by
  simp only [Finset.univ_unique, Finset.sum_singleton]
  show finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (V 1)) - finrank (ZMod 2) (⊥ : Submodule (ZMod 2) (V 1)) = 1
  rw [finrank_top, finrank_bot]; simp

theorem net1h_hN : (1 : Matrix (Fin 1) (Fin 1) ℤ) = 1 + net1h.Hhat * 1 := by decide

theorem net1h_IX : 1 + net1h.Xw 1 = 1 := by
  have : net1h.Xw 1 = 0 := by decide
  rw [this]; simp

/-- (T) is TIGHT here: D = 1 = rank_F2(I + X). -/
theorem net1h_T_tight : (1 + net1h.Xw 1).rank = 1 ∧ ∑ k, net1h.drop k = 1 := by
  refine ⟨?_, net1h_drop⟩
  rw [net1h_IX, Matrix.rank_one]; simp

theorem net1h_T : (1 + net1h.Xw 1).rank ≤ ∑ k, net1h.drop k :=
  net1h.torsion_headline net1h_c 1 net1h_hN

/-- (M) is TIGHT here: ρ_B^net + ρ_A^net = 1 = D. -/
theorem net1h_M_tight : rhoB net1h.red + rhoA net1h.red = 1 := by
  have h1 := net1h.half_master net1h_c
  rw [net1h_drop] at h1
  have h2 : 1 ≤ rhoA net1h.red := by
    have hf : LegalF net1h.red (1 : Matrix (Fin 1) (Fin 1) (ZMod 2)) := fun k p _ => Submodule.mem_top
    refine le_trans ?_ (le_rhoA net1h.red 1 hf)
    have : qmask net1h.red.qr net1h.red.qc (net1h.red.G * net1h.red.N * 1) = 1 := by decide
    rw [this, Matrix.rank_one]; simp
  omega

theorem net1h_split : Fintype.card (Fin 1) ≤ ∑ k, net1h.drop k :=
  net1h.split_headline net1h_c 1 net1h_hN (fun t => by fin_cases t; exact Or.inr (by decide))

/-- relay instance: 2 ports (orthogonal labels), 2 nodes, an EVEN-SCALAR relay 0 → 1 (H = 2),
    F = [[1,0],[0,2]], G = [[0,1],[0,1]]; M = [[2,2],[2,2]], M∘Q = 2 I. -/
def net2h : Net4 (Fin 2) (Fin 2) 2 where
  q := ![![1, 0], ![0, 1]]
  hodd := by decide
  lt := fun a b => a < b
  ltrans := fun a b c h1 h2 => lt_trans h1 h2
  lirr := fun a => lt_irrefl a
  a := fun _ => ⊤
  b := fun _ => ⊥
  F := Matrix.of ![![1, 0], ![0, 2]]
  G := Matrix.of ![![0, 1], ![0, 1]]
  H := Matrix.of ![![0, 0], ![2, 0]]
  N := Matrix.of ![![1, 0], ![2, 1]]
  c := ![2, 2]
  hba := fun _ => bot_le
  hF := fun _ _ _ => Submodule.mem_top
  hG := fun s k _ y hy => by
    rw [Submodule.mem_bot] at hy; subst hy; simp
  hHlt := fun k j hne => by
    fin_cases k <;> fin_cases j <;> simp_all [Matrix.of_apply]
  hH := fun _ _ _ => bot_le
  hN1 := by decide
  hN2 := by decide
  hc := by decide
  hM := by decide

theorem net2h_c : ∀ s, net2h.c s = 2 := by decide

theorem net2h_relay : net2h.H 1 0 = 2 ∧ ∃ k j, net2h.Hp k j ≠ 0 := ⟨by decide, 1, 0, by decide⟩

theorem net2h_drop : ∑ k, net2h.drop k = 4 := by
  simp only [Fin.sum_univ_two]
  show (finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (V 2)) - finrank (ZMod 2) (⊥ : Submodule (ZMod 2) (V 2))) +
    (finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (V 2)) - finrank (ZMod 2) (⊥ : Submodule (ZMod 2) (V 2))) = 4
  rw [finrank_top, finrank_bot]; simp

theorem net2h_hN : (1 : Matrix (Fin 2) (Fin 2) ℤ) = 1 + net2h.Hhat * 1 := by decide

theorem net2h_IX : 1 + net2h.Xw 1 = 1 := by
  have : net2h.Xw 1 = 0 := by decide
  rw [this]; simp

/-- the even-scalar relay term is NEEDED: without H' the torsion matrix is not I. -/
theorem net2h_relay_term_needed :
    qmask net2h.q net2h.q (net2h.Gp * net2h.red.N * net2h.red.F + net2h.red.G * net2h.red.N * net2h.Fp)
      ≠ 1 := by decide

theorem net2h_T : (1 + net2h.Xw 1).rank = 2 ∧ (1 + net2h.Xw 1).rank ≤ ∑ k, net2h.drop k := by
  refine ⟨?_, net2h.torsion_headline net2h_c 1 net2h_hN⟩
  rw [net2h_IX, Matrix.rank_one]; simp

theorem net2h_M : rhoB net2h.red + rhoA net2h.red ≤ 4 := by
  have := net2h.half_master net2h_c
  rwa [net2h_drop] at this

end Inst

/-! ### the h = 5 relay instance of ND.md / N2D (2 nodes, 1 odd relay, D = 4), mod-2 reduction -/
section Relay5

/-- bit-vector of a natural number in F2^5. -/
def vec5 (n : ℕ) : V 5 := fun b => if n.testBit b.val then 1 else 0

/-- port labels (the 16 odd vectors of F2^5). -/
def lab5 : Fin 16 → V 5 := fun i => vec5 (![1, 2, 4, 7, 8, 11, 13, 14, 16, 19, 21, 22, 25, 26, 28, 31] i)

theorem dot_zero_of_span {h : ℕ} (S : Set (V h)) (w : V h) (hS : ∀ x ∈ S, x ⬝ᵥ w = 0) :
    ∀ y ∈ Submodule.span (ZMod 2) S, y ⬝ᵥ w = 0 := by
  intro y hy
  refine Submodule.span_induction (p := fun y _ => y ⬝ᵥ w = 0) hS ?_ ?_ ?_ hy
  · simp
  · intro x y _ _ hx hy; simp [add_dotProduct, hx, hy]
  · intro c x _ hx; simp [smul_dotProduct, hx]

/-- b_0 = a_1 = ⟨2, 8, 20⟩, b_1 = ⟨22⟩. -/
def sp3 : Submodule (ZMod 2) (V 5) := Submodule.span (ZMod 2) (Set.range ![vec5 2, vec5 8, vec5 20])
def sp1 : Submodule (ZMod 2) (V 5) := Submodule.span (ZMod 2) (Set.range ![vec5 22])

theorem sp3_dim : finrank (ZMod 2) sp3 = 3 := by
  have hli : LinearIndependent (ZMod 2) ![vec5 2, vec5 8, vec5 20] := by
    rw [Fintype.linearIndependent_iff]
    decide
  unfold sp3
  rw [finrank_span_eq_card hli]
  simp

theorem sp1_dim : finrank (ZMod 2) sp1 = 1 := by
  have hli : LinearIndependent (ZMod 2) ![vec5 22] := by
    rw [Fintype.linearIndependent_iff]
    decide
  unfold sp1
  rw [finrank_span_eq_card hli]
  simp

theorem sp1_le_sp3 : sp1 ≤ sp3 := by
  have : vec5 22 = vec5 2 + vec5 20 := by decide
  refine Submodule.span_le.2 ?_
  rintro _ ⟨i, rfl⟩
  fin_cases i
  simp only [Fin.zero_eta, Matrix.cons_val_zero]
  rw [this]
  exact Submodule.add_mem _ (Submodule.subset_span ⟨0, rfl⟩) (Submodule.subset_span ⟨2, rfl⟩)

/-- F̄ rows (F_j mod 2, F_k mod 2), Ḡ columns, H̄, N̄ of the N2D relay counterexample. -/
def F5 : Matrix (Fin 2) (Fin 16) (ZMod 2) :=
  Matrix.of ![![1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1], ![0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]]
def G5 : Matrix (Fin 16) (Fin 2) (ZMod 2) :=
  Matrix.of ![![1, 0], ![0, 0], ![0, 0], ![0, 1], ![0, 1], ![0, 0], ![0, 0], ![0, 1], ![0, 0], ![0, 1],
    ![0, 1], ![0, 0], ![0, 0], ![0, 0], ![0, 1], ![0, 0]]
def H5 : Matrix (Fin 2) (Fin 2) (ZMod 2) := Matrix.of ![![0, 0], ![1, 0]]
def N5 : Matrix (Fin 2) (Fin 2) (ZMod 2) := Matrix.of ![![1, 0], ![1, 1]]

theorem mem_sp3_of (n : ℕ) (hn : vec5 n = vec5 2 ∨ vec5 n = vec5 8 ∨ vec5 n = vec5 20 ∨
    vec5 n = vec5 2 + vec5 20 ∨ vec5 n = vec5 8 + vec5 20) : vec5 n ∈ sp3 := by
  have h2 : vec5 2 ∈ sp3 := Submodule.subset_span ⟨0, rfl⟩
  have h8 : vec5 8 ∈ sp3 := Submodule.subset_span ⟨1, rfl⟩
  have h20 : vec5 20 ∈ sp3 := Submodule.subset_span ⟨2, rfl⟩
  rcases hn with h | h | h | h | h <;> rw [h]
  · exact h2
  · exact h8
  · exact h20
  · exact Submodule.add_mem _ h2 h20
  · exact Submodule.add_mem _ h8 h20

/-- the relay network over F2. -/
def relay5 : FNet (Fin 16) (Fin 16) (Fin 2) 5 where
  qr := lab5
  qc := lab5
  lt := fun a b => a < b
  ltrans := fun a b c h1 h2 => lt_trans h1 h2
  lirr := fun a => lt_irrefl a
  a := fun k => if k = 0 then ⊤ else sp3
  b := fun k => if k = 0 then sp3 else sp1
  F := F5
  G := G5
  H := H5
  N := N5
  hba := by
    intro k
    fin_cases k
    · simp
    · simpa using sp1_le_sp3
  hF := by
    intro k p hne
    fin_cases k
    · simp
    · simp only [Fin.mk_one, Fin.isValue, one_ne_zero, if_false]
      fin_cases p <;> first
        | (exfalso; apply hne; decide)
        | (exact mem_sp3_of _ (by decide))
  hG := by
    intro s k hne y hy
    fin_cases k
    · simp only [Fin.zero_eta, Fin.isValue, if_true] at hy
      have hs : s = 0 := by
        by_contra hs; apply hne; revert hs; revert s; decide
      subst hs
      exact dot_zero_of_span _ _ (by
        intro x hx
        simp only [Set.mem_range] at hx
        obtain ⟨i, rfl⟩ := hx
        fin_cases i <;> decide) y hy
    · simp only [Fin.mk_one, Fin.isValue, one_ne_zero, if_false] at hy
      have hs : s = 3 ∨ s = 4 ∨ s = 7 ∨ s = 9 ∨ s = 10 ∨ s = 14 := by
        by_contra hs; apply hne; revert hs; revert s; decide
      exact dot_zero_of_span _ _ (by
        intro x hx
        simp only [Set.mem_range] at hx
        obtain ⟨i, rfl⟩ := hx
        fin_cases i
        rcases hs with rfl | rfl | rfl | rfl | rfl | rfl <;> decide) y hy
  hHlt := by
    intro k j hne
    fin_cases k <;> fin_cases j <;> simp_all [H5, Matrix.of_apply]
  hH := by
    intro k j hne
    fin_cases k <;> fin_cases j <;> simp_all [H5, Matrix.of_apply]
  hN1 := by decide

theorem relay5_drop : ∑ k, relay5.drop k = 4 := by
  simp only [Fin.sum_univ_two]
  show (finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (V 5)) - finrank (ZMod 2) sp3) +
    (finrank (ZMod 2) sp3 - finrank (ZMod 2) sp1) = 4
  rw [finrank_top, sp3_dim, sp1_dim]; simp

/-- M̄ ∘ Q ≠ 0 here (so the half-network corollary does NOT apply; only the block form does). -/
theorem relay5_MQ_ne : qmask relay5.qr relay5.qc (relay5.G * relay5.N * relay5.F) ≠ 0 := by decide

/-- the master block form holds on the relay instance, for every legal y, y', f, f'. -/
theorem relay5_master (y y' : Matrix (Fin 16) (Fin 2) (ZMod 2)) (f f' : Matrix (Fin 2) (Fin 16) (ZMod 2))
    (hy : LegalY relay5 y) (hy' : LegalY relay5 y') (hf : LegalF relay5 f) (hf' : LegalF relay5 f') :
    (Matrix.fromBlocks (qmask relay5.qr relay5.qc (y * relay5.N * f')) (qmask relay5.qr relay5.qc (y * relay5.N * f))
      (qmask relay5.qr relay5.qc (y' * relay5.N * f')) (qmask relay5.qr relay5.qc (y' * relay5.N * f))).rank ≤ 4 := by
  rw [← relay5_drop]
  exact master_form relay5 y y' f f' hy hy' hf hf'

end Relay5

#print axioms relay5_drop
#print axioms relay5_MQ_ne
#print axioms relay5_master

#print axioms rank_fromBlocks_triangular
#print axioms exists_gens
#print axioms FNet.rank_le
#print axioms master_form
#print axioms half_form
#print axioms rhoB_add_rhoA_le
#print axioms dim_bound
#print axioms torsion_form
#print axioms Net4.half_master
#print axioms Net4.carry
#print axioms Net4.torsion_headline
#print axioms Net4.split_headline
#print axioms net1h_T_tight
#print axioms net1h_M_tight
#print axioms net1h_split
#print axioms net2h_T
#print axioms net2h_M
#print axioms net2h_relay_term_needed

end NetDoubling

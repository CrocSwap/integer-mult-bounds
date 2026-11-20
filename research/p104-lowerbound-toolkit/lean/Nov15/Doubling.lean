import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.NoncommRing
import Mathlib.Data.Matrix.ColumnRowPartitioned
import Mathlib.Data.Matrix.Block
/-!
DOUBLING (lane LEANDOUBLE). Preamble copied from HalfCancel.lean.  Kernel-only: no sorry / native_decide / axioms.
Half-level cancellation law for half-integer decoders, abstract index type and abstract 0/1 pattern Mz
(Mz t t = 1).  Row k: integer vectors w_k, v_k (v_k = 2 u_k), decoder identity
  sum_k w_k(t) v_k(s) Mz(t,s) = 2 [t = s].
With a = w mod 2, w' = w div 2 (same for v, b, v'):  over F2,   I = X + sum_k B_k,
 X = Mz * (cover count / 2),  B_k = diag(w') Q_k diag(b) + diag(a) Q_k diag(v'),  rank B_k <= 2 rank Q_k.
NEW here (ORBITLP DOUBLING LEMMA): for ANY F2 vectors y_k, z_k,
  rank Yhat + rank Zhat <= C = sum_k rank Q_k,  Yhat = sum diag(y_k) Q_k diag(b_k), Zhat = sum diag(a_k) Q_k diag(z_k),
via block upper-triangular [[Yhat,*],[0,Zhat]] = sum_k L_k Q_k R_k (lower-left block = sum diag(a)Q diag(b) = 0 by cover_even).
Corollaries: C >= rank_F2(I+X) (HalfCancel had half of it); split decoders (no port odd on both sides): C >= n.
-/
open Matrix Finset

namespace Doubling

instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

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

variable {ι κ : Type*} [Fintype ι] [DecidableEq ι]

/-- cover count of cell (t,s): number of rows whose half parts a_k(t) b_k(s) are both odd. -/
def cover (J : Finset κ) (w v : κ → ι → ℤ) (t s : ι) : ℤ := ∑ k ∈ J, (w k t % 2) * (v k s % 2)

/-- X = (cover/2) mod 2, masked by the pattern. -/
def Xm (Mz : ι → ι → ℤ) (J : Finset κ) (w v : κ → ι → ℤ) : Matrix ι ι (ZMod 2) :=
  Matrix.of fun t s => (Mz t s : ZMod 2) * ((cover J w v t s / 2 : ℤ) : ZMod 2)

/-- carry matrix of one row. -/
def Bm (Mz : ι → ι → ℤ) (w v : ι → ℤ) : Matrix ι ι (ZMod 2) :=
  Matrix.of fun t s => (Mz t s : ZMod 2) *
    (((w t / 2 : ℤ) : ZMod 2) * ((v s % 2 : ℤ) : ZMod 2) + ((w t % 2 : ℤ) : ZMod 2) * ((v s / 2 : ℤ) : ZMod 2))

/-- the pattern restricted to supp w x supp v (zero padded), over F2. -/
def Qk (Mz : ι → ι → ℤ) (w v : ι → ℤ) : Matrix ι ι (ZMod 2) :=
  Matrix.of fun t s => if w t ≠ 0 ∧ v s ≠ 0 then (Mz t s : ZMod 2) else 0

lemma prod_expand (x y : ℤ) :
    x * y = (x % 2) * (y % 2) + 2 * ((x / 2) * (y % 2) + (x % 2) * (y / 2)) + 4 * ((x / 2) * (y / 2)) := by
  have hx : x = x % 2 + 2 * (x / 2) := by omega
  have hy : y = y % 2 + 2 * (y / 2) := by omega
  generalize x % 2 = a at *
  generalize x / 2 = p at *
  generalize y % 2 = b at *
  generalize y / 2 = q at *
  subst hx hy
  ring

lemma two_zmod : (2 : ZMod 2) = 0 := by decide
lemma key3 (a b c : ZMod 2) : a - b - 2 * c = a + b := by revert a b c; decide
lemma add_self_zmod (x : ZMod 2) : x + x = 0 := by revert x; decide
lemma neg_zmod (x : ZMod 2) : -x = x := by revert x; decide

variable (Mz : ι → ι → ℤ) (J : Finset κ) (w v : κ → ι → ℤ)

/-- (1a) mod-2 cancellation: on pattern cells the cover count is even. -/
theorem cover_even (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (t s : ι) (h : Mz t s = 1) : 2 ∣ cover J w v t s := by
  have h1 := hdec t s
  rw [h] at h1
  simp only [mul_one] at h1
  have h2 : ∑ k ∈ J, w k t * v k s =
      cover J w v t s + 2 * ∑ k ∈ J, ((w k t / 2) * (v k s % 2) + (w k t % 2) * (v k s / 2))
        + 4 * ∑ k ∈ J, ((w k t / 2) * (v k s / 2)) := by
    simp only [cover, Finset.mul_sum, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun k _ => prod_expand _ _
  rw [h2] at h1
  split_ifs at h1 <;> omega

/-- (1) the mod-4 reduction identity (complete half-level content):  I = X + sum_k B_k over F2. -/
theorem carry_identity (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1) (hd : ∀ t, Mz t t = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    (1 : Matrix ι ι (ZMod 2)) = Xm Mz J w v + ∑ k ∈ J, Bm Mz (w k) (v k) := by
  ext t s
  rw [Matrix.add_apply, Matrix.sum_apply]
  rcases h01 t s with h0 | h1
  · have hts : t ≠ s := by
      rintro rfl; rw [hd t] at h0; exact one_ne_zero h0
    simp [Xm, Bm, h0, Matrix.one_apply_ne hts]
  · have e := hdec t s
    rw [h1] at e
    simp only [mul_one] at e
    have h2 : ∑ k ∈ J, w k t * v k s =
        cover J w v t s + 2 * ∑ k ∈ J, ((w k t / 2) * (v k s % 2) + (w k t % 2) * (v k s / 2))
          + 4 * ∑ k ∈ J, ((w k t / 2) * (v k s / 2)) := by
      simp only [cover, Finset.mul_sum, ← Finset.sum_add_distrib]
      exact Finset.sum_congr rfl fun k _ => prod_expand _ _
    rw [h2] at e
    set S := ∑ k ∈ J, ((w k t / 2) * (v k s % 2) + (w k t % 2) * (v k s / 2)) with hS
    set T := ∑ k ∈ J, ((w k t / 2) * (v k s / 2)) with hT
    have hc : cover J w v t s / 2 = (if t = s then 1 else 0) - S - 2 * T := by
      split_ifs at e ⊢ <;> omega
    have hS' : ((S : ℤ) : ZMod 2) = ∑ k ∈ J, (((w k t / 2 : ℤ) : ZMod 2) * ((v k s % 2 : ℤ) : ZMod 2)
        + ((w k t % 2 : ℤ) : ZMod 2) * ((v k s / 2 : ℤ) : ZMod 2)) := by
      rw [hS]; push_cast; rfl
    have hq : ((cover J w v t s / 2 : ℤ) : ZMod 2) = (if t = s then 1 else 0) + ((S : ℤ) : ZMod 2) := by
      rw [hc]
      by_cases hts : t = s
      · simp only [hts, if_true]; push_cast; exact key3 _ _ _
      · simp only [hts, if_false]; push_cast; exact key3 _ _ _
    simp only [Xm, Bm, Matrix.of_apply, h1, Int.cast_one, one_mul]
    rw [hq, hS']
    by_cases hts : t = s
    · subst hts; simp [add_assoc, add_self_zmod]
    · simp [hts, Matrix.one_apply_ne hts, add_assoc, add_self_zmod]

/-- Bm in terms of the padded pattern: B = diag(w') Q diag(b) + diag(a) Q diag(v'). -/
theorem Bm_eq (w v : ι → ℤ) :
    Bm Mz w v = diagonal (fun t => ((w t / 2 : ℤ) : ZMod 2)) * Qk Mz w v * diagonal (fun s => ((v s % 2 : ℤ) : ZMod 2))
      + diagonal (fun t => ((w t % 2 : ℤ) : ZMod 2)) * Qk Mz w v * diagonal (fun s => ((v s / 2 : ℤ) : ZMod 2)) := by
  ext t s
  simp only [Matrix.add_apply, Matrix.diagonal_mul, Matrix.mul_diagonal, Bm, Qk, Matrix.of_apply]
  by_cases hw : w t = 0
  · simp [hw]
  · by_cases hv : v s = 0
    · simp [hv]
    · simp [hw, hv]; ring


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

/-! ## The doubling lemma -/
section Main
variable {ι κ : Type*} [Fintype ι] [DecidableEq ι]
variable (Mz : ι → ι → ℤ) (J : Finset κ) (w v : κ → ι → ℤ)

/-- parity vector over F2 -/
def par (x : ι → ℤ) : ι → ZMod 2 := fun t => ((x t % 2 : ℤ) : ZMod 2)
/-- half vector (floor division by 2) over F2 -/
def hal (x : ι → ℤ) : ι → ZMod 2 := fun t => ((x t / 2 : ℤ) : ZMod 2)

/-- Tm l r = sum_k diag(l_k) Q_k diag(r_k).  Yhat = Tm y (par v), Zhat = Tm (par w) z. -/
def Tm (l r : κ → ι → ZMod 2) : Matrix ι ι (ZMod 2) :=
  ∑ k ∈ J, diagonal (l k) * Qk Mz (w k) (v k) * diagonal (r k)

/-- one summand P_k = [diag y; diag a] Q_k [diag b, diag z] as a (ι ⊕ ι)-square matrix. -/
def Pk (y z : ι → ZMod 2) (w v : ι → ℤ) : Matrix (ι ⊕ ι) (ι ⊕ ι) (ZMod 2) :=
  fromBlocks (diagonal y * Qk Mz w v * diagonal (par v)) (diagonal y * Qk Mz w v * diagonal z)
    (diagonal (par w) * Qk Mz w v * diagonal (par v)) (diagonal (par w) * Qk Mz w v * diagonal z)

lemma Pk_factor (y z : ι → ZMod 2) (w v : ι → ℤ) :
    Pk Mz y z w v = fromRows (diagonal y) (diagonal (par w)) * Qk Mz w v *
      fromCols (diagonal (par v)) (diagonal z) := by
  rw [Matrix.mul_assoc, Matrix.mul_fromCols, Matrix.fromRows_mul_fromCols]
  simp only [Pk, Matrix.mul_assoc]

lemma rank_Pk_le (y z : ι → ZMod 2) (w v : ι → ℤ) : (Pk Mz y z w v).rank ≤ (Qk Mz w v).rank := by
  rw [Pk_factor]
  exact (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)

/-- per-cell identity: the support mask in Q_k is invisible after multiplying by the parities. -/
lemma par_Qk_par (w v : ι → ℤ) (t s : ι) :
    par w t * Qk Mz w v t s * par v s = (Mz t s : ZMod 2) * (par w t * par v s) := by
  by_cases hw : w t = 0
  · simp [par, hw]
  · by_cases hv : v s = 0
    · simp [par, hv]
    · simp [Qk, hw, hv]; ring

/-- lower-left block vanishes: sum_k diag(a_k) Q_k diag(b_k) = 0 (mod-2 law). -/
theorem lowerleft_zero (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    ∑ k ∈ J, diagonal (par (w k)) * Qk Mz (w k) (v k) * diagonal (par (v k)) = 0 := by
  ext t s
  rw [Matrix.sum_apply]
  simp only [Matrix.diagonal_mul, Matrix.mul_diagonal]
  have e : ∀ k ∈ J, par (w k) t * Qk Mz (w k) (v k) t s * par (v k) s
      = (Mz t s : ZMod 2) * (par (w k) t * par (v k) s) := fun k _ => par_Qk_par Mz (w k) (v k) t s
  rw [Finset.sum_congr rfl e, ← Finset.mul_sum]
  rcases h01 t s with h0 | h1
  · simp [h0]
  · have hc := cover_even Mz J w v hdec t s h1
    have : (∑ k ∈ J, par (w k) t * par (v k) s) = ((cover J w v t s : ℤ) : ZMod 2) := by
      simp [cover, par]
    rw [this, (ZMod.intCast_zmod_eq_zero_iff_dvd _ 2).2 hc]
    simp

/-- THE DOUBLING LEMMA (master form).  For ANY F2 vectors y_k, z_k (WLOG y_k ⊆ D_k, z_k ⊆ S_k: the
mask inside Q_k makes the choice outside the supports irrelevant),
  rank Yhat + rank Zhat <= sum_k rank Q_k. -/
theorem doubling (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (y z : κ → ι → ZMod 2) :
    (Tm Mz J w v y (fun k => par (v k))).rank + (Tm Mz J w v (fun k => par (w k)) z).rank
      ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  have hsum : ∑ k ∈ J, Pk Mz (y k) (z k) (w k) (v k) =
      fromBlocks (Tm Mz J w v y (fun k => par (v k))) (Tm Mz J w v y z) 0
        (Tm Mz J w v (fun k => par (w k)) z) := by
    have hBL := lowerleft_zero Mz J w v h01 hdec
    ext i j
    rcases i with i | i <;> rcases j with j | j
    · simp [Pk, Tm, Matrix.sum_apply]
    · simp [Pk, Tm, Matrix.sum_apply]
    · have := congrFun (congrFun hBL i) j
      simpa [Pk, Matrix.sum_apply] using this
    · simp [Pk, Tm, Matrix.sum_apply]
  have h1 := rank_fromBlocks_triangular (Tm Mz J w v y (fun k => par (v k))) (Tm Mz J w v y z)
    (Tm Mz J w v (fun k => par (w k)) z)
  rw [← hsum] at h1
  refine h1.trans ((rank_sum_le (K := ZMod 2) J _).trans ?_)
  exact Finset.sum_le_sum fun k _ => rank_Pk_le Mz _ _ _ _

/-- Y + Z = I + X for y = w', z = v'. -/
theorem Y_add_Z (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1) (hd : ∀ t, Mz t t = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    Tm Mz J w v (fun k => hal (w k)) (fun k => par (v k)) + Tm Mz J w v (fun k => par (w k)) (fun k => hal (v k))
      = 1 + Xm Mz J w v := by
  have hc := carry_identity Mz J w v h01 hd hdec
  have h : (1 : Matrix ι ι (ZMod 2)) + Xm Mz J w v = ∑ k ∈ J, Bm Mz (w k) (v k) := by
    ext t s
    have := congrArg (fun m => m t s) hc
    simp only [Matrix.add_apply, Matrix.sum_apply] at this ⊢
    generalize (1 : Matrix ι ι (ZMod 2)) t s = a at *
    generalize Xm Mz J w v t s = b at *
    generalize ∑ k ∈ J, Bm Mz (w k) (v k) t s = c at *
    revert a b c; decide
  rw [h, Tm, Tm, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [Bm_eq]
  rfl

/-- COROLLARY: C >= rank_F2 (I + X)  (HalfCancel.cost_ge_half_rank had  rank <= 2C). -/
theorem cost_ge_rank (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1) (hd : ∀ t, Mz t t = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0) :
    (1 + Xm Mz J w v).rank ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  rw [← Y_add_Z Mz J w v h01 hd hdec]
  exact (rank_add_le' _ _).trans (doubling Mz J w v h01 hdec _ _)

/-- X vanishes unless the row port is odd on the w side and the column port on the v side. -/
lemma Xm_eq_zero_of (t s : ι) (h : (∀ k ∈ J, w k t % 2 = 0) ∨ (∀ k ∈ J, v k s % 2 = 0)) :
    Xm Mz J w v t s = 0 := by
  have : cover J w v t s = 0 := by
    unfold cover
    rcases h with h | h
    · exact Finset.sum_eq_zero fun k hk => by simp [h k hk]
    · exact Finset.sum_eq_zero fun k hk => by simp [h k hk]
  simp [Xm, this]

/-- SPLIT decoders (no port is odd on both sides): C >= n. -/
theorem split_cost_ge_card (h01 : ∀ t s, Mz t s = 0 ∨ Mz t s = 1) (hd : ∀ t, Mz t t = 1)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Mz t s = if t = s then 2 else 0)
    (hsplit : ∀ t, (∀ k ∈ J, w k t % 2 = 0) ∨ (∀ k ∈ J, v k t % 2 = 0)) :
    Fintype.card ι ≤ ∑ k ∈ J, (Qk Mz (w k) (v k)).rank := by
  have hXX : Xm Mz J w v * Xm Mz J w v = 0 := by
    ext t u
    rw [Matrix.mul_apply]
    refine Finset.sum_eq_zero fun s _ => ?_
    rcases hsplit s with h | h
    · rw [Xm_eq_zero_of Mz J w v s u (Or.inl h)]; simp
    · rw [Xm_eq_zero_of Mz J w v t s (Or.inr h)]; simp
  have hX2 : Xm Mz J w v + Xm Mz J w v = 0 := by
    ext t s; simp [Matrix.add_apply, add_self_zmod]
  have hinv : (1 + Xm Mz J w v) * (1 + Xm Mz J w v) = 1 := by
    have : (1 + Xm Mz J w v) * (1 + Xm Mz J w v) = 1 + (Xm Mz J w v + Xm Mz J w v) + Xm Mz J w v * Xm Mz J w v := by
      noncomm_ring
    rw [this, hX2, hXX]; simp
  have h1 : Fintype.card ι = (1 : Matrix ι ι (ZMod 2)).rank := (Matrix.rank_one).symm
  rw [h1, ← hinv]
  exact (Matrix.rank_mul_le_left _ _).trans (cost_ge_rank Mz J w v h01 hd hdec)

end Main

/-! ## Non-vacuity -/
section Inst
/-- 2-clique Hadamard decoder (from HalfCancel): rows (1,1)x(1,1) and (1,-1)x(1,-1), Mz = J. -/
def W : Fin 2 → Fin 2 → ℤ := fun k t => if k = 0 then 1 else if t = 0 then 1 else -1
def M2 : Fin 2 → Fin 2 → ℤ := fun _ _ => 1

lemma inst_dec : ∀ t s : Fin 2, ∑ k ∈ (Finset.univ : Finset (Fin 2)), W k t * W k s * M2 t s
    = if t = s then 2 else 0 := by decide

lemma inst_Qk (k : Fin 2) : Qk M2 (W k) (W k) = vecMulVec (fun _ => (1 : ZMod 2)) (fun _ => 1) := by
  ext t s; fin_cases k <;> fin_cases t <;> fin_cases s <;> decide

lemma inst_C_le : ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Qk M2 (W k) (W k)).rank ≤ 2 := by
  have h : ∀ k : Fin 2, (Qk M2 (W k) (W k)).rank ≤ 1 := fun k => by
    rw [inst_Qk]; exact Matrix.rank_vecMulVec_le _ _
  calc _ ≤ ∑ k : Fin 2, 1 := Finset.sum_le_sum fun k _ => h k
    _ = 2 := by simp

lemma inst_IX : (1 : Matrix (Fin 2) (Fin 2) (ZMod 2)) + Xm M2 Finset.univ W W = !![0, 1; 1, 0] := by
  ext t s; fin_cases t <;> fin_cases s <;> decide

lemma inst_IX_rank : (1 + Xm M2 Finset.univ W W).rank = 2 := by
  have hinv : (1 + Xm M2 Finset.univ W W) * (1 + Xm M2 Finset.univ W W) = 1 := by
    rw [inst_IX]; ext t s; fin_cases t <;> fin_cases s <;> decide
  have h1 : (1 : Matrix (Fin 2) (Fin 2) (ZMod 2)).rank ≤ (1 + Xm M2 Finset.univ W W).rank := by
    conv_lhs => rw [← hinv]
    exact Matrix.rank_mul_le_left _ _
  rw [Matrix.rank_one] at h1
  have h2 := (Matrix.rank_le_card_height (1 + Xm M2 Finset.univ W W))
  simp at h1 h2
  omega

/-- TIGHT: C = 2 = rank_F2 (I+X); HalfCancel only gave 2 <= 2C = 4, i.e. C >= 1. -/
theorem inst_tight : ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Qk M2 (W k) (W k)).rank = 2 ∧
    (1 + Xm M2 Finset.univ W W).rank = 2 := by
  have h := cost_ge_rank M2 Finset.univ W W (fun _ _ => Or.inr rfl) (fun _ => rfl) inst_dec
  rw [inst_IX_rank] at h
  exact ⟨le_antisymm inst_C_le h, inst_IX_rank⟩

/-- the master inequality on the instance with y = w', z = v' (both ranks 1). -/
theorem inst_master :
    (Tm M2 Finset.univ W W (fun k => hal (W k)) (fun k => par (W k))).rank +
    (Tm M2 Finset.univ W W (fun k => par (W k)) (fun k => hal (W k))).rank ≤ 2 :=
  (doubling M2 Finset.univ W W (fun _ _ => Or.inr rfl) inst_dec _ _).trans inst_C_le

/-- split decoder with both sides nonempty: ports 0 (v odd only) and 1 (w odd only), Mz = identity pattern. -/
def Ws : Fin 2 → Fin 2 → ℤ := fun k t => if k = 0 then (if t = 0 then 2 else 0) else (if t = 1 then 1 else 0)
def Vs : Fin 2 → Fin 2 → ℤ := fun k t => if k = 0 then (if t = 0 then 1 else 0) else (if t = 1 then 2 else 0)
def Mid : Fin 2 → Fin 2 → ℤ := fun t s => if t = s then 1 else 0

lemma split_dec : ∀ t s : Fin 2, ∑ k ∈ (Finset.univ : Finset (Fin 2)), Ws k t * Vs k s * Mid t s
    = if t = s then 2 else 0 := by decide

lemma split_split : ∀ t : Fin 2, (∀ k ∈ (Finset.univ : Finset (Fin 2)), Ws k t % 2 = 0) ∨
    (∀ k ∈ (Finset.univ : Finset (Fin 2)), Vs k t % 2 = 0) := by decide

lemma split_C_le : ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Qk Mid (Ws k) (Vs k)).rank ≤ 2 := by
  have h : ∀ k : Fin 2, (Qk Mid (Ws k) (Vs k)).rank ≤ 1 := fun k => by
    have : Qk Mid (Ws k) (Vs k) = vecMulVec (fun t => if t = k then (1 : ZMod 2) else 0) (fun t => if t = k then 1 else 0) := by
      ext t s; fin_cases k <;> fin_cases t <;> fin_cases s <;> decide
    rw [this]; exact Matrix.rank_vecMulVec_le _ _
  calc _ ≤ ∑ k : Fin 2, 1 := Finset.sum_le_sum fun k _ => h k
    _ = 2 := by simp

/-- split corollary is tight here: C = 2 = n. -/
theorem split_tight : ∑ k ∈ (Finset.univ : Finset (Fin 2)), (Qk Mid (Ws k) (Vs k)).rank = 2 := by
  have h := split_cost_ge_card Mid Finset.univ Ws Vs
    (fun t s => by unfold Mid; split_ifs <;> simp) (fun t => by simp [Mid]) split_dec split_split
  simp at h
  exact le_antisymm split_C_le h

end Inst

#print axioms rank_fromBlocks_triangular
#print axioms lowerleft_zero
#print axioms doubling
#print axioms Y_add_Z
#print axioms cost_ge_rank
#print axioms split_cost_ge_card
#print axioms inst_tight
#print axioms inst_master
#print axioms split_tight

end Doubling

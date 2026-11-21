/-
CallerLeafChannel (lane TRIBUILD, Nov 20).  LEAF-CHANNEL law for host-only stage products (cards/WILD/NOVEL/tribuild/TB.md).
Setting = CallerSGram: rows Fin n, columns ι with stage map β (β i < k), P = sgProd A B β k, K = sgK β (B^T A).
Leaves Lf: rows whose A- and B-rows vanish off one stage.
(1) `count_le`     abstract triangular stage count: if every c in S with c = 0 below stage t has blk_t c in Z t,
                    then finrank S <= sum_t finrank (Z t).
(2) `reduce_le`    finrank (ker(P+1) ⊓ leaf space) <= finrank S1,  S1 = ker K ⊓ ker (non-leaf rows of A)   [x ↦ H B^T x].
(3) `lower`/`upper` S1 is block lower triangular w.r.t. N_t = K_tt - X_tt and block upper triangular w.r.t. M_t = K_tt + X_tt
                    (X = non-leaf part of B^T A; off-diagonal blocks of B^T A only see non-leaf rows).
(4) `S1_le`        if each K_tt is injective on its block (lambda_t != -1) and each stage has <= 2 columns: finrank S1 <= k.
(5) `leaf_channel` #Lf <= k + rank (P + 1).   With thin deletion (rank(P_h + 1) <= T, paper) this is  d1 <= k + T.
(6) `inst_*`       non-vacuity: k = 2, 2 hubs + 2 leaves, both leaves in ker(P+1): the bound finrank (ker ⊓ leaves) <= k is attained.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Projection
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Module
import Mathlib.Tactic.IntervalCases
import Nov15.CallerSGram

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerLeaf
open Matrix Finset CallerSign Module

section core
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- restriction to the columns of stage t. -/
def blk (β : ι → ℕ) (t : ℕ) : (ι → K) →ₗ[K] (ι → K) where
  toFun c := fun i => if β i = t then c i else 0
  map_add' x y := by funext i; simp only [Pi.add_apply]; split_ifs <;> simp
  map_smul' a x := by funext i; simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]; split_ifs <;> simp

@[simp] theorem blk_apply (β : ι → ℕ) (t : ℕ) (c : ι → K) (i : ι) :
    blk β t c i = if β i = t then c i else 0 := rfl

/-- vectors supported on stage t. -/
def W (β : ι → ℕ) (t : ℕ) : Submodule K (ι → K) where
  carrier := {v | ∀ i, β i ≠ t → v i = 0}
  add_mem' {x y} hx hy i h := by simp [hx i h, hy i h]
  zero_mem' i h := rfl
  smul_mem' a x hx i h := by simp [hx i h]

theorem blk_mem_W (β : ι → ℕ) (t : ℕ) (c : ι → K) : blk β t c ∈ W β t := by
  intro i h; simp [h]

theorem finrank_W_le (β : ι → ℕ) (t : ℕ) :
    finrank K (W (K := K) β t) ≤ Fintype.card {i // β i = t} := by
  let f : W (K := K) β t →ₗ[K] ({i // β i = t} → K) :=
    { toFun := fun v j => (v : ι → K) j.1, map_add' := fun _ _ => rfl, map_smul' := fun _ _ => rfl }
  have hf : Function.Injective f := by
    intro v w h
    apply Subtype.ext; funext i
    by_cases hi : β i = t
    · exact congrFun h ⟨i, hi⟩
    · rw [v.2 i hi, w.2 i hi]
  calc finrank K (W (K := K) β t) ≤ finrank K ({i // β i = t} → K) :=
        LinearMap.finrank_le_finrank_of_injective hf
    _ = Fintype.card {i // β i = t} := Module.finrank_fintype_fun_eq_card K

/-- (1) abstract triangular stage count. -/
theorem count_le (β : ι → ℕ) (k : ℕ) (hβ : ∀ i, β i < k) (S : Submodule K (ι → K))
    (Z : ℕ → Submodule K (ι → K))
    (hZ : ∀ c ∈ S, ∀ t < k, (∀ i, β i < t → c i = 0) → blk β t c ∈ Z t) :
    finrank K S ≤ ∑ t ∈ range k, finrank K (Z t) := by
  choose Q hQ using fun t => Submodule.exists_isCompl (Z t)
  let F : S →ₗ[K] ((t : Fin k) → Z t) :=
    LinearMap.pi fun t => (Submodule.projectionOnto (Z t) (Q t) (hQ t)) ∘ₗ (blk β t) ∘ₗ S.subtype
  have hinj : Function.Injective F := by
    rw [← LinearMap.ker_eq_bot, Submodule.eq_bot_iff]
    intro c hc
    rw [LinearMap.mem_ker] at hc
    have key : ∀ t ≤ k, ∀ i, β i < t → (c : ι → K) i = 0 := by
      intro t
      induction t with
      | zero => intro _ i h; omega
      | succ t ih =>
        intro ht i hi
        have ih' := ih (by omega)
        have hm := hZ c c.2 t (by omega) ih'
        have h0 : F c ⟨t, by omega⟩ = 0 := by rw [hc]; rfl
        have h1 : Submodule.projectionOnto (Z t) (Q t) (hQ t) (blk β t (c : ι → K)) = ⟨_, hm⟩ :=
          Submodule.projectionOnto_apply_of_mem_left (hQ t) hm
        have h2 : blk β t (c : ι → K) = 0 := by
          have : (⟨_, hm⟩ : Z t) = 0 := by rw [← h1]; exact h0
          exact congrArg Subtype.val this
        rcases Nat.lt_succ_iff_lt_or_eq.1 hi with h | h
        · exact ih' i h
        · have := congrFun h2 i
          simpa [blk_apply, h] using this
    ext i
    simpa using key k le_rfl i (hβ i)
  calc finrank K S ≤ finrank K ((t : Fin k) → Z t) := LinearMap.finrank_le_finrank_of_injective hinj
    _ = ∑ t : Fin k, finrank K (Z t) := Module.finrank_pi_fintype K
    _ = ∑ t ∈ range k, finrank K (Z t) := Fin.sum_univ_eq_sum_range (fun t => finrank K (Z t)) k

variable {n : ℕ}

/-- non-leaf part of a role matrix. -/
def hub (Lf : Finset (Fin n)) (A : Matrix (Fin n) ι K) : Matrix (Fin n) ι K :=
  Matrix.of fun r i => if r ∈ Lf then 0 else A r i

/-- X = (non-leaf B)^T (non-leaf A). -/
def GH (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) : Matrix ι ι K := (hub Lf B)ᵀ * hub Lf A

/-- leaves: rows vanishing off one stage. -/
def LeafSet (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) (β : ι → ℕ) : Prop :=
  ∀ r ∈ Lf, ∃ s, ∀ i, β i ≠ s → A r i = 0 ∧ B r i = 0

theorem G_off {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} {β : ι → ℕ} (hL : LeafSet Lf A B β)
    {i j : ι} (hij : β i ≠ β j) : sgG A B i j = GH Lf A B i j := by
  simp only [sgG, GH, hub, Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply]
  apply Finset.sum_congr rfl
  intro r _
  by_cases hr : r ∈ Lf
  · obtain ⟨s, hs⟩ := hL r hr
    simp only [hr, if_true, mul_zero]
    by_cases h : β i = s
    · have : β j ≠ s := fun h' => hij (h.trans h'.symm)
      rw [(hs j this).1, mul_zero]
    · rw [(hs i h).2, zero_mul]
  · simp [hr]

theorem K_up (β : ι → ℕ) (G : Matrix ι ι K) {i j : ι} (h : β i < β j) : sgK β G i j = G i j := by
  have hij : i ≠ j := fun e => by subst e; exact lt_irrefl _ h
  simp [sgK, sgDiag, sgUp, sgLow, Matrix.one_apply, hij, h, h.ne, not_lt.mpr h.le]

theorem K_low (β : ι → ℕ) (G : Matrix ι ι K) {i j : ι} (h : β j < β i) : sgK β G i j = -G i j := by
  have hij : i ≠ j := fun e => by subst e; exact lt_irrefl _ h
  simp [sgK, sgDiag, sgUp, sgLow, Matrix.one_apply, hij, h, h.ne', not_lt.mpr h.le]

/-- S1 = ker K ⊓ ker (non-leaf rows of A). -/
def S1 (β : ι → ℕ) (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) : Submodule K (ι → K) :=
  LinearMap.ker (sgK β (sgG A B)).mulVecLin ⊓ LinearMap.ker (hub Lf A).mulVecLin

theorem GH_mulVec (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) (v : ι → K) :
    GH Lf A B *ᵥ v = (hub Lf B)ᵀ *ᵥ (hub Lf A *ᵥ v) := by
  rw [GH, mulVec_mulVec]

/-- (3a) lower triangularity with diagonal N_t = K_tt - X_tt. -/
theorem lower {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} (hL : LeafSet Lf A B β)
    {c : ι → K} (hc : c ∈ S1 β Lf A B) (t : ℕ) (hlo : ∀ i, β i < t → c i = 0) (i : ι) (hi : β i = t) :
    (sgK β (sgG A B) *ᵥ blk β t c) i - (GH Lf A B *ᵥ blk β t c) i = 0 := by
  have hK : sgK β (sgG A B) *ᵥ c = 0 := hc.1
  have hA : hub Lf A *ᵥ c = 0 := hc.2
  set d := c - blk β t c with hd
  have hdz : ∀ j, ¬ t < β j → d j = 0 := by
    intro j hj
    simp only [hd, Pi.sub_apply, blk_apply]
    rcases Nat.lt_or_ge (β j) t with h | h
    · simp [hlo j h, h.ne]
    · have : β j = t := by omega
      simp [this]
  have e1 : (sgK β (sgG A B) *ᵥ d) i = (GH Lf A B *ᵥ d) i := by
    simp only [Matrix.mulVec, dotProduct]
    apply Finset.sum_congr rfl
    intro j _
    by_cases hj : t < β j
    · rw [K_up β _ (by omega), G_off hL (by omega)]
    · rw [hdz j hj, mul_zero, mul_zero]
  have e2 : GH Lf A B *ᵥ d = -(GH Lf A B *ᵥ blk β t c) := by
    rw [GH_mulVec, GH_mulVec, hd, mulVec_sub, hA, zero_sub, mulVec_neg]
  have e3 : sgK β (sgG A B) *ᵥ blk β t c + sgK β (sgG A B) *ᵥ d = 0 := by
    rw [← mulVec_add, hd, add_sub_cancel, hK]
  have := congrFun e3 i
  rw [Pi.add_apply, e1, e2, Pi.neg_apply, Pi.zero_apply] at this
  rw [sub_eq_add_neg]; exact this

/-- (3b) upper triangularity with diagonal M_t = K_tt + X_tt. -/
theorem upper {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} (hL : LeafSet Lf A B β)
    {c : ι → K} (hc : c ∈ S1 β Lf A B) (t : ℕ) (hhi : ∀ i, t < β i → c i = 0) (i : ι) (hi : β i = t) :
    (sgK β (sgG A B) *ᵥ blk β t c) i + (GH Lf A B *ᵥ blk β t c) i = 0 := by
  have hK : sgK β (sgG A B) *ᵥ c = 0 := hc.1
  have hA : hub Lf A *ᵥ c = 0 := hc.2
  set d := c - blk β t c with hd
  have hdz : ∀ j, ¬ β j < t → d j = 0 := by
    intro j hj
    simp only [hd, Pi.sub_apply, blk_apply]
    rcases Nat.lt_or_ge t (β j) with h | h
    · simp [hhi j h, h.ne']
    · have : β j = t := by omega
      simp [this]
  have e1 : (sgK β (sgG A B) *ᵥ d) i = -(GH Lf A B *ᵥ d) i := by
    simp only [Matrix.mulVec, dotProduct]
    rw [← Finset.sum_neg_distrib]
    apply Finset.sum_congr rfl
    intro j _
    by_cases hj : β j < t
    · rw [K_low β _ (by omega), G_off hL (by omega), neg_mul]
    · rw [hdz j hj, mul_zero, mul_zero, neg_zero]
  have e2 : GH Lf A B *ᵥ d = -(GH Lf A B *ᵥ blk β t c) := by
    rw [GH_mulVec, GH_mulVec, hd, mulVec_sub, hA, zero_sub, mulVec_neg]
  have e3 : sgK β (sgG A B) *ᵥ blk β t c + sgK β (sgG A B) *ᵥ d = 0 := by
    rw [← mulVec_add, hd, add_sub_cancel, hK]
  have := congrFun e3 i
  rw [Pi.add_apply, e1, e2, Pi.neg_apply, neg_neg, Pi.zero_apply] at this
  exact this

/-- stage spaces of the two triangular forms. -/
def Zlo (β : ι → ℕ) (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) (t : ℕ) : Submodule K (ι → K) :=
  W β t ⊓ LinearMap.ker (blk β t ∘ₗ (sgK β (sgG A B) - GH Lf A B).mulVecLin)
def Zhi (β : ι → ℕ) (Lf : Finset (Fin n)) (A B : Matrix (Fin n) ι K) (t : ℕ) : Submodule K (ι → K) :=
  W β t ⊓ LinearMap.ker (blk β t ∘ₗ (sgK β (sgG A B) + GH Lf A B).mulVecLin)

/-- lambda_t != -1 in block form: K_tt injective on the stage-t block. -/
def KInj (β : ι → ℕ) (G : Matrix ι ι K) (t : ℕ) : Prop :=
  ∀ v ∈ W β t, (∀ i, β i = t → (sgK β G *ᵥ v) i = 0) → v = 0

theorem Z_disj {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} (h2 : (2 : K) ≠ 0) {t : ℕ}
    (hK : KInj β (sgG A B) t) : Zlo β Lf A B t ⊓ Zhi β Lf A B t = ⊥ := by
  rw [Submodule.eq_bot_iff]
  rintro v ⟨⟨hw, hlo0⟩, ⟨_, hhi0⟩⟩
  have hlo : blk β t ((sgK β (sgG A B) - GH Lf A B) *ᵥ v) = 0 := hlo0
  have hhi : blk β t ((sgK β (sgG A B) + GH Lf A B) *ᵥ v) = 0 := hhi0
  apply hK v hw
  intro i hi
  have a := congrFun hlo i
  have b := congrFun hhi i
  simp only [blk_apply, hi, if_true, sub_mulVec, add_mulVec, Pi.sub_apply, Pi.add_apply,
    Pi.zero_apply] at a b
  have : (2 : K) * (sgK β (sgG A B) *ᵥ v) i = 0 := by linear_combination a + b
  rcases mul_eq_zero.1 this with h | h
  · exact absurd h h2
  · exact h

theorem Z_sum_le {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} (h2 : (2 : K) ≠ 0) {t : ℕ}
    (hK : KInj β (sgG A B) t) :
    finrank K (Zlo β Lf A B t) + finrank K (Zhi β Lf A B t) ≤ finrank K (W (K := K) β t) := by
  have e := Submodule.finrank_sup_add_finrank_inf_eq (Zlo β Lf A B t) (Zhi β Lf A B t)
  rw [Z_disj h2 hK, finrank_bot, add_zero] at e
  rw [← e]
  exact Submodule.finrank_mono (sup_le inf_le_left inf_le_left)

/-- (4) finrank S1 <= k. -/
theorem S1_le {β : ι → ℕ} {k : ℕ} (hβ : ∀ i, β i < k) {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K}
    (h2 : (2 : K) ≠ 0) (hL : LeafSet Lf A B β) (hK : ∀ t < k, KInj β (sgG A B) t)
    (hw : ∀ t < k, Fintype.card {i // β i = t} ≤ 2) : finrank K (S1 β Lf A B) ≤ k := by
  have hlo : finrank K (S1 β Lf A B) ≤ ∑ t ∈ range k, finrank K (Zlo β Lf A B t) := by
    apply count_le β k hβ
    intro c hc t ht hz
    refine ⟨blk_mem_W β t c, ?_⟩
    change blk β t ((sgK β (sgG A B) - GH Lf A B) *ᵥ blk β t c) = 0
    funext i
    simp only [blk_apply, sub_mulVec, Pi.sub_apply, Pi.zero_apply]
    split_ifs with hi
    · exact lower hL hc t hz i hi
    · rfl
  -- reversed order for the upper form
  let β' : ι → ℕ := fun i => k - 1 - β i
  have hβ' : ∀ i, β' i < k := fun i => by have := hβ i; simp only [β']; omega
  have hhi : finrank K (S1 β Lf A B) ≤ ∑ t ∈ range k, finrank K (Zhi β Lf A B (k - 1 - t)) := by
    apply count_le β' k hβ'
    intro c hc t ht hz
    have hb : blk β' t c = blk β (k - 1 - t) c := by
      funext i; simp only [blk_apply, β']
      have := hβ i
      by_cases h : β i = k - 1 - t
      · rw [if_pos (by omega), if_pos h]
      · rw [if_neg (by omega), if_neg h]
    rw [hb]
    refine ⟨blk_mem_W β _ c, ?_⟩
    change blk β (k - 1 - t) ((sgK β (sgG A B) + GH Lf A B) *ᵥ blk β (k - 1 - t) c) = 0
    funext i
    simp only [blk_apply, add_mulVec, Pi.add_apply, Pi.zero_apply]
    split_ifs with hi
    · refine upper hL hc (k - 1 - t) (fun j hj => hz j ?_) i hi
      have := hβ j; simp only [β']; omega
    · rfl
  rw [Finset.sum_range_reflect (fun t => finrank K (Zhi β Lf A B t)) k] at hhi
  have hsum : ∑ t ∈ range k, (finrank K (Zlo β Lf A B t) + finrank K (Zhi β Lf A B t)) ≤ ∑ t ∈ range k, 2 := by
    apply Finset.sum_le_sum
    intro t ht
    have ht' := Finset.mem_range.1 ht
    exact (Z_sum_le h2 (hK t ht')).trans ((finrank_W_le β t).trans (hw t ht'))
  rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_range, smul_eq_mul] at hsum
  omega

/-- leaf space: vectors vanishing on non-leaf rows. -/
def Lsp (Lf : Finset (Fin n)) : Submodule K (Fin n → K) where
  carrier := {x | ∀ r, r ∉ Lf → x r = 0}
  add_mem' {x y} hx hy r h := by simp [hx r h, hy r h]
  zero_mem' r h := rfl
  smul_mem' a x hx r h := by simp [hx r h]

theorem card_le_finrank_Lsp (Lf : Finset (Fin n)) : Lf.card ≤ finrank K (Lsp (K := K) Lf) := by
  let f : (Lf → K) →ₗ[K] Lsp (K := K) Lf :=
    { toFun := fun g => ⟨fun r => if h : r ∈ Lf then g ⟨r, h⟩ else 0, fun r hr => by simp [hr]⟩
      map_add' := fun g g' => by
        apply Subtype.ext; funext r; simp only [Submodule.coe_add, Pi.add_apply]
        split_ifs <;> simp
      map_smul' := fun a g => by
        apply Subtype.ext; funext r
        simp only [Submodule.coe_smul, Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
        split_ifs <;> simp }
  have hf : Function.Injective f := by
    intro g g' h
    funext ⟨r, hr⟩
    have := congrFun (congrArg Subtype.val h) r
    simpa [f, hr] using this
  calc Lf.card = finrank K (Lf → K) := by rw [Module.finrank_fintype_fun_eq_card]; simp
    _ ≤ _ := LinearMap.finrank_le_finrank_of_injective hf

/-- (2) reduction: x ↦ H B^T x maps ker(P+1) ⊓ leaves injectively into S1. -/
theorem reduce_le {β : ι → ℕ} {k : ℕ} (hβ : ∀ i, β i < k) {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K}
    (h2 : (2 : K) ≠ 0) :
    finrank K (LinearMap.ker (sgProd A B β k + 1).mulVecLin ⊓ Lsp (K := K) Lf : Submodule K (Fin n → K))
      ≤ finrank K (S1 β Lf A B) := by
  set S0 := (LinearMap.ker (sgProd A B β k + 1).mulVecLin ⊓ Lsp (K := K) Lf : Submodule K (Fin n → K))
  have hP := sgProd_eq A B β k hβ
  have hHM := (sg_HM β (sgG A B)).2
  -- key identity: x in S0 => A c = -2 x with c = H B^T x
  have hAc : ∀ x ∈ S0, A *ᵥ ((1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x)) = -(2 : K) • x := by
    intro x hx
    have h0 : (sgProd A B β k + 1) *ᵥ x = 0 := hx.1
    rw [hP, add_mulVec, add_mulVec, one_mulVec, ← mulVec_mulVec, ← mulVec_mulVec] at h0
    have e : A *ᵥ ((1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x)) = (x + A *ᵥ ((1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x)) + x) - (2 : K) • x := by module
    rw [e, h0]; module
  have hmem : ∀ x ∈ S0, (1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x) ∈ S1 β Lf A B := by
    intro x hx
    have hA := hAc x hx
    constructor
    · show sgK β (sgG A B) *ᵥ _ = 0
      rw [sgK_eq, add_mulVec, smul_mulVec, mulVec_mulVec (Bᵀ *ᵥ x) (1 - sgLow β (sgG A B)) (1 - sgLow β (sgG A B))⁻¹, hHM,
        one_mulVec]
      have hG : sgG A B *ᵥ ((1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x))
          = Bᵀ *ᵥ (A *ᵥ ((1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ x))) := by
        simp only [sgG, mulVec_mulVec, Matrix.mul_assoc]
      rw [hG, hA, mulVec_smul]
      module
    · show hub Lf A *ᵥ _ = 0
      funext r
      have hx2 := hx.2
      have := congrFun hA r
      simp only [Matrix.mulVec, dotProduct, hub, Matrix.of_apply, Pi.zero_apply] at this ⊢
      by_cases hr : r ∈ Lf
      · simp [hr]
      · simp only [hr, if_false]
        rw [this, Pi.smul_apply, hx2 r hr, smul_zero]
  let f : S0 →ₗ[K] S1 β Lf A B :=
    LinearMap.codRestrict (S1 β Lf A B) (((1 - sgLow β (sgG A B))⁻¹ * Bᵀ).mulVecLin ∘ₗ S0.subtype)
      (fun x => by simp only [LinearMap.comp_apply, Submodule.subtype_apply, Matrix.mulVecLin_apply,
        ← mulVec_mulVec]; exact hmem x x.2)
  have hf : Function.Injective f := by
    rw [← LinearMap.ker_eq_bot, Submodule.eq_bot_iff]
    intro x hx
    rw [LinearMap.mem_ker] at hx
    have hc : (1 - sgLow β (sgG A B))⁻¹ *ᵥ (Bᵀ *ᵥ (x : Fin n → K)) = 0 := by
      have h' : ((1 - sgLow β (sgG A B))⁻¹ * Bᵀ) *ᵥ (x : Fin n → K) = 0 := congrArg Subtype.val hx
      rwa [← mulVec_mulVec] at h'
    have := hAc x x.2
    rw [hc, mulVec_zero] at this
    ext r
    have hr := congrFun this r
    simp only [Pi.zero_apply, Pi.smul_apply, smul_eq_mul, neg_mul] at hr
    have : (2 : K) * (x : Fin n → K) r = 0 := by linear_combination hr
    rcases mul_eq_zero.1 this with h | h
    · exact absurd h h2
    · simpa using h
  exact LinearMap.finrank_le_finrank_of_injective hf

/-- (5) LEAF-CHANNEL: #leaves <= k + rank(P + 1). -/
theorem leaf_channel {β : ι → ℕ} {k : ℕ} (hβ : ∀ i, β i < k) {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K}
    (h2 : (2 : K) ≠ 0) (hL : LeafSet Lf A B β) (hK : ∀ t < k, KInj β (sgG A B) t)
    (hw : ∀ t < k, Fintype.card {i // β i = t} ≤ 2) :
    Lf.card ≤ k + (sgProd A B β k + 1).rank := by
  have hS := (reduce_le (Lf := Lf) hβ h2).trans (S1_le hβ h2 hL hK hw)
  have e1 := Submodule.finrank_sup_add_finrank_inf_eq
    (LinearMap.ker (sgProd A B β k + 1).mulVecLin) (Lsp (K := K) Lf)
  have e2 := LinearMap.finrank_range_add_finrank_ker (sgProd A B β k + 1).mulVecLin
  have e3 := Submodule.finrank_le (LinearMap.ker (sgProd A B β k + 1).mulVecLin ⊔ Lsp (K := K) Lf)
  have e4 := card_le_finrank_Lsp (K := K) Lf
  have hr : (sgProd A B β k + 1).rank = finrank K (LinearMap.range (sgProd A B β k + 1).mulVecLin) := rfl
  simp only [Module.finrank_fintype_fun_eq_card, Fintype.card_fin] at e2 e3
  omega

end core

/-! ## (6) non-vacuity: k = 2, hubs 0,1, leaves 2,3 of stage 0; columns 0,1 stage 0 and 2,3 stage 1.
Stage 0: A_H = A_L = I, B_H = I, B_L = -2I (K_00 = I, N_0 = 0). Stage 1: A_H = I, B_H = -I (K_11 = I).
Both leaves lie in ker(P+1), so finrank (ker(P+1) ⊓ leaves) = 2 = k: the S1 bound is attained. -/
def beta2 : Fin 4 → ℕ := ![0, 0, 1, 1]
def A2 : Matrix (Fin 4) (Fin 4) ℚ := !![1, 0, 1, 0; 0, 1, 0, 1; 1, 0, 0, 0; 0, 1, 0, 0]
def B2 : Matrix (Fin 4) (Fin 4) ℚ := !![1, 0, -1, 0; 0, 1, 0, -1; -2, 0, 0, 0; 0, -2, 0, 0]
def L2 : Finset (Fin 4) := {2, 3}

theorem inst_prod : sgProd A2 B2 beta2 2 + 1 = !![1, 0, 0, 0; 0, 1, 0, 0; 1, 0, 0, 0; 0, 1, 0, 0] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [sgProd, sgStage, blkPi, A2, B2, beta2, Matrix.mul_apply, Fin.sum_univ_four, Matrix.diagonal_apply,
      Matrix.one_apply, Matrix.vecMul, dotProduct] <;> norm_num

theorem inst_leaf : LeafSet L2 A2 B2 beta2 := by
  intro r hr
  simp only [L2, Finset.mem_insert, Finset.mem_singleton] at hr
  refine ⟨0, fun i hi => ?_⟩
  rcases hr with rfl | rfl <;> fin_cases i <;> simp_all [beta2, A2, B2]

theorem inst_kinj : ∀ t < 2, KInj beta2 (sgG A2 B2) t := by
  intro t ht v hv hz
  funext j
  have hv' : ∀ i, beta2 i ≠ t → v i = 0 := hv
  interval_cases t
  · have h0 := hz 0 rfl; have h1 := hz 1 rfl
    have v2 := hv' 2 (by simp [beta2]); have v3 := hv' 3 (by simp [beta2])
    simp [Matrix.mulVec, dotProduct, Fin.sum_univ_four, sgK, sgDiag, sgUp, sgLow, sgG, A2, B2, beta2,
      Matrix.mul_apply, Matrix.one_apply, v2, v3] at h0 h1
    fin_cases j <;> simp_all
  · have h2 := hz 2 rfl; have h3 := hz 3 rfl
    have v0 := hv' 0 (by simp [beta2]); have v1 := hv' 1 (by simp [beta2])
    simp [Matrix.mulVec, dotProduct, Fin.sum_univ_four, sgK, sgDiag, sgUp, sgLow, sgG, A2, B2, beta2,
      Matrix.mul_apply, Matrix.one_apply, v0, v1] at h2 h3
    fin_cases j <;> norm_num at h2 h3 <;> simp_all

theorem inst_w : ∀ t < 2, Fintype.card {i // beta2 i = t} ≤ 2 := by
  intro t ht; interval_cases t <;> decide

/-- the hypotheses of `leaf_channel` hold on the instance (so the theorem is not vacuous). -/
theorem inst_channel : L2.card ≤ 2 + (sgProd A2 B2 beta2 2 + 1).rank :=
  leaf_channel (fun i => by fin_cases i <;> simp [beta2]) (by norm_num) inst_leaf inst_kinj inst_w

/-- tightness: both leaves are in ker(P+1) (P acts as -1 on the leaf space), so dim S = 2 = k. -/
theorem inst_tight : ∀ x ∈ Lsp (K := ℚ) L2, (sgProd A2 B2 beta2 2 + 1) *ᵥ x = 0 := by
  intro x hx
  have x0 := hx 0 (by simp [L2]); have x1 := hx 1 (by simp [L2])
  rw [inst_prod]
  funext i
  fin_cases i <;> simp [Matrix.mulVec, dotProduct, Fin.sum_univ_four, x0, x1]

end CallerLeaf

#print axioms CallerLeaf.count_le
#print axioms CallerLeaf.reduce_le
#print axioms CallerLeaf.S1_le
#print axioms CallerLeaf.leaf_channel
#print axioms CallerLeaf.inst_channel
#print axioms CallerLeaf.inst_tight

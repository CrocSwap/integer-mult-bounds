/-
CallerRC2 (lane LEANRC2).  CALLERCUT's RELAY-CUT law RC2_l (cards/WILD/NOVEL/callercut/CC.md, section 1), pair form.
Frame-level model (RB section 0), coordinatised.  Roles r have masks M r (stage sets), blocks bh r s, ah r s in K^m
(bh_r[s], ah_r[t] of CC), Ghat_st = sum_r bh_r[s] ah_r[t]^T (`gBlk`).  Each role has a piece `pc r s` at each stage of its
mask (s in pc r s subset M r); a piece q with 2 <= |q| carries x_q (supported on E(q) = roles with mask >= q, with
sum_r x_q(r) bh_r[s'] = 0 at every stage s' of q) and a biorthogonal y_q (pieces sharing a stage).
(1) rc2_lin  : linear-algebra core: if the rows b_r (r in W) span K^m and carry |iota| independent kernel vectors supported on W,
               then m + |iota| <= |W|.
(2) rc2_pair : s /= t, l >= 2, Ghat_st invertible, W = {deep (D >= l) roles at s} u {roles covering s and t}:
               m <= #{r at s deep, |P_r(s)| < l, t notin P_r(s)} + #{r covering s,t, D_r < l, t notin P_r(s)}   (m = 2: >= 2).
(3) rc2_avg  : arithmetic corollary (per-stage form): summing over (s,t) gives the averaged type row
               m k (k-1) <= sum_r ( [D_r >= l] sum_{s in M_r, |P|<l} (k-|P|) + [D_r < l] sum_{s in M_r} (D_r - |P|) ).
(4) bridge   : rc2_pair_sg: the hypotheses on Ghat_st hold in every CallerSGram P_k = -1 frame (K_tt invertible, char /= 2).
(5) non-vacuity: k = 3 CallerSGram instance (all-singleton pieces); and a toy with a genuine multi piece (kernel vector used).
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring
import Nov15.CallerSGram

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerSign
open Matrix Finset

section lin
variable {K : Type*} [Field K] {R : Type*} [Fintype R] [DecidableEq R] {m : ℕ}

theorem rc2_lin (W : Finset R) (b : R → Fin m → K)
    (hsurj : ∀ v : Fin m → K, ∃ c : R → K, (∀ r, r ∉ W → c r = 0) ∧ ∀ a, ∑ r, c r * b r a = v a)
    {ι : Type*} [Fintype ι] (xs : ι → R → K) (hind : LinearIndependent K xs)
    (hsupp : ∀ i r, xs i r ≠ 0 → r ∈ W) (hker : ∀ i a, ∑ r, xs i r * b r a = 0) :
    m + Fintype.card ι ≤ W.card := by
  classical
  let Bm : Matrix (Fin m) W K := Matrix.of fun a r => b r.1 a
  let g : (W → K) →ₗ[K] (Fin m → K) := Bm.mulVecLin
  have hsum : ∀ c : R → K, (∀ r, r ∉ W → c r = 0) → ∀ a,
      g (fun r : W => c r.1) a = ∑ r, c r * b r a := by
    intro c hc a
    simp only [g, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Bm, Matrix.of_apply]
    calc ∑ r : W, b r.1 a * c r.1 = ∑ r : W, c r.1 * b r.1 a := by
          refine Finset.sum_congr rfl fun r _ => mul_comm _ _
      _ = ∑ r ∈ W, c r * b r a := Finset.sum_coe_sort W (fun r => c r * b r a)
      _ = ∑ r, c r * b r a :=
          Finset.sum_subset (Finset.subset_univ _) (fun r _ hr => by simp [hc r hr])
  have hsg : Function.Surjective g := by
    intro v
    obtain ⟨c, hc, hv⟩ := hsurj v
    refine ⟨fun r => c r.1, ?_⟩
    funext a
    rw [hsum c hc a, hv a]
  have hrange : LinearMap.range g = ⊤ := LinearMap.range_eq_top.mpr hsg
  have hrn := LinearMap.finrank_range_add_finrank_ker g
  rw [hrange, finrank_top, Module.finrank_fin_fun, Module.finrank_fintype_fun_eq_card,
    Fintype.card_coe] at hrn
  let xk : ι → LinearMap.ker g := fun i => ⟨fun r : W => xs i r.1, by
    rw [LinearMap.mem_ker]
    funext a
    rw [hsum (xs i) (fun r hr => by by_contra h; exact hr (hsupp i r h)) a]
    exact hker i a⟩
  have hxk : LinearIndependent K xk := by
    apply LinearIndependent.of_comp (LinearMap.ker g).subtype
    rw [Fintype.linearIndependent_iff]
    intro c hc i
    have h0 : ∑ i, c i • xs i = 0 := by
      funext r
      by_cases hr : r ∈ W
      · have := congrFun hc ⟨r, hr⟩
        simpa [xk, Finset.sum_apply] using this
      · have : ∀ i, xs i r = 0 := fun i => by by_contra h; exact hr (hsupp i r h)
        simp [Finset.sum_apply, this]
    exact (Fintype.linearIndependent_iff.mp hind) c h0 i
  have := hxk.fintype_card_le_finrank
  omega

end lin

section rc2
variable {K : Type*} [Field K] {R : Type*} [Fintype R] [DecidableEq R] {k m : ℕ}

/-- `Ghat_st = sum_r bh_r[s] ah_r[t]^T` -/
def gBlk (bh ah : R → Fin k → Fin m → K) (s t : Fin k) : Matrix (Fin m) (Fin m) K :=
  Matrix.of fun a b => ∑ r, bh r s a * ah r t b

/-- piece data.  A piece is a piece INSTANCE (role `r`, its block `pc r s` of stages): two roles with the same stage set
    carry two pieces, each with its own kernel vector `x r s` (supported on E(q), roles with mask >= q) and biorthogonal `y r s`. -/
structure Pieces (M : R → Finset (Fin k)) (bh : R → Fin k → Fin m → K) where
  pc : R → Fin k → Finset (Fin k)
  x : R → Fin k → R → K
  y : R → Fin k → R → K
  pc_mem : ∀ r s, s ∈ M r → s ∈ pc r s
  pc_sub : ∀ r s, s ∈ M r → pc r s ⊆ M r
  x_supp : ∀ r s, s ∈ M r → 2 ≤ (pc r s).card → ∀ r', x r s r' ≠ 0 → pc r s ⊆ M r'
  x_ker : ∀ r s, s ∈ M r → 2 ≤ (pc r s).card → ∀ s' ∈ pc r s, ∀ a,
    ∑ r', x r s r' * bh r' s' a = 0
  biorth : ∀ r s r' s', s ∈ M r → s' ∈ M r' → 2 ≤ (pc r s).card → 2 ≤ (pc r' s').card →
    (∃ u, u ∈ pc r s ∧ u ∈ pc r' s') →
    ∑ r'', y r s r'' * x r' s' r'' = if r = r' ∧ pc r s = pc r' s' then 1 else 0

/-- left side of RC2 at `(s,t,l)`: deep roles at s with a small piece missing t -/
def rcDeep (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (s t : Fin k) (l : ℕ) : ℕ :=
  (univ.filter fun r => s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l ∧ t ∉ pc r s).card

/-- shallow roles covering s and t whose piece at s misses t -/
def rcShal (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (s t : Fin k) (l : ℕ) : ℕ :=
  (univ.filter fun r => s ∈ M r ∧ t ∈ M r ∧ (M r).card < l ∧ t ∉ pc r s).card

theorem rc2_pair (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin m → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (s t : Fin k) (hst : s ≠ t) (l : ℕ) (hl : 2 ≤ l)
    (hG : IsUnit (gBlk bh ah s t).det) :
    m ≤ rcDeep M P.pc s t l + rcShal M P.pc s t l := by
  classical
  set W : Finset R := univ.filter fun r => s ∈ M r ∧ (l ≤ (M r).card ∨ t ∈ M r) with hW
  set good : R → Prop := fun r => l ≤ (P.pc r s).card ∨ t ∈ P.pc r s with hgood
  set Wg : Finset R := W.filter good with hWg
  have hcard2 : ∀ r, s ∈ M r → good r → 2 ≤ (P.pc r s).card := by
    intro r hr hg
    rcases hg with h | h
    · omega
    · have hsub : ({s, t} : Finset (Fin k)) ⊆ P.pc r s := by
        intro u hu
        rcases Finset.mem_insert.mp hu with rfl | hu
        · exact P.pc_mem r _ hr
        · rw [Finset.mem_singleton.mp hu]; exact h
      have := Finset.card_le_card hsub
      rwa [Finset.card_pair hst] at this
  have hWgmem : ∀ r ∈ Wg, s ∈ M r ∧ good r := by
    intro r hr
    have hr' := Finset.mem_filter.mp hr
    exact ⟨(Finset.mem_filter.mp hr'.1).2.1, hr'.2⟩
  -- surjectivity
  have hsurj : ∀ v : Fin m → K, ∃ c : R → K, (∀ r, r ∉ W → c r = 0) ∧
      ∀ a, ∑ r, c r * bh r s a = v a := by
    intro v
    have hinv := Matrix.mul_nonsing_inv _ hG
    set w : Fin m → K := (gBlk bh ah s t)⁻¹ *ᵥ v with hw
    have hGw : (gBlk bh ah s t) *ᵥ w = v := by
      rw [hw, Matrix.mulVec_mulVec, hinv, Matrix.one_mulVec]
    refine ⟨fun r => if r ∈ W then ∑ b, ah r t b * w b else 0, ?_, ?_⟩
    · intro r hr; simp [hr]
    · intro a
      rw [← hGw]
      simp only [Matrix.mulVec, dotProduct, gBlk, Matrix.of_apply]
      simp_rw [Finset.sum_mul]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun r _ => ?_
      by_cases hr : r ∈ W
      · simp only [hr, if_true]
        rw [Finset.sum_mul]
        exact Finset.sum_congr rfl fun b _ => by ring
      · simp only [hr, if_false, zero_mul]
        have : s ∉ M r ∨ t ∉ M r := by
          by_contra h
          push Not at h
          exact hr (Finset.mem_filter.mpr ⟨Finset.mem_univ _, h.1, Or.inr h.2⟩)
        rcases this with h | h
        · simp [hbh r s h, Finset.sum_mul]
        · simp [hah r t h]
  -- the kernel family: one piece instance per good role at s
  let ι := {r // r ∈ Wg}
  let xs : ι → R → K := fun i => P.x i.1 s
  have hind : LinearIndependent K xs := by
    rw [Fintype.linearIndependent_iff]
    intro c hc j
    have h1 : ∑ r'', P.y j.1 s r'' * (∑ i, c i * xs i r'') = 0 := by
      have : ∀ r'', ∑ i, c i * xs i r'' = 0 := fun r'' => by
        have := congrFun hc r''
        simpa [Finset.sum_apply] using this
      simp [this]
    have h2 : ∑ r'', P.y j.1 s r'' * (∑ i, c i * xs i r'') = c j := by
      simp_rw [Finset.mul_sum]
      rw [Finset.sum_comm]
      have : ∀ i : ι, ∑ r'', P.y j.1 s r'' * (c i * xs i r'') = c i * (if j = i then 1 else 0) := by
        intro i
        obtain ⟨hsi, hgi⟩ := hWgmem i.1 i.2
        obtain ⟨hsj, hgj⟩ := hWgmem j.1 j.2
        have hb := P.biorth j.1 s i.1 s hsj hsi (hcard2 j.1 hsj hgj) (hcard2 i.1 hsi hgi)
          ⟨s, P.pc_mem j.1 s hsj, P.pc_mem i.1 s hsi⟩
        have hiff : (j = i) ↔ (j.1 = i.1 ∧ P.pc j.1 s = P.pc i.1 s) := by
          constructor
          · intro h; rw [h]; exact ⟨rfl, rfl⟩
          · intro h; exact Subtype.ext h.1
        have e : ∑ r'', P.y j.1 s r'' * (c i * xs i r'') = c i * ∑ r'', P.y j.1 s r'' * P.x i.1 s r'' := by
          rw [Finset.mul_sum]
          refine Finset.sum_congr rfl fun r'' _ => ?_
          simp only [xs]; ring
        rw [e, hb]
        congr 1
        exact if_congr hiff.symm rfl rfl
      simp only [this, mul_ite, mul_one, mul_zero]
      rw [Finset.sum_ite_eq]; simp
    rw [← h2, h1]
  have hsupp : ∀ i r, xs i r ≠ 0 → r ∈ W := by
    intro i r' hr'
    obtain ⟨hsr, hg⟩ := hWgmem i.1 i.2
    have hsub := P.x_supp i.1 s hsr (hcard2 i.1 hsr hg) r' hr'
    have hs' : s ∈ M r' := hsub (P.pc_mem i.1 s hsr)
    refine Finset.mem_filter.mpr ⟨Finset.mem_univ _, hs', ?_⟩
    rcases hg with h | h
    · left; exact h.trans (Finset.card_le_card hsub)
    · right; exact hsub h
  have hker : ∀ i a, ∑ r, xs i r * bh r s a = 0 := by
    intro i a
    obtain ⟨hsr, hg⟩ := hWgmem i.1 i.2
    exact P.x_ker i.1 s hsr (hcard2 i.1 hsr hg) s (P.pc_mem i.1 s hsr) a
  have hmain := rc2_lin W (fun r => bh r s) hsurj xs hind hsupp hker
  have hιcard : Fintype.card ι = Wg.card := Fintype.card_coe Wg
  have hsplit : Wg.card + (W.filter fun r => ¬ good r).card = W.card :=
    Finset.card_filter_add_card_filter_not good
  have hng : (W.filter fun r => ¬ good r).card ≤ rcDeep M P.pc s t l + rcShal M P.pc s t l := by
    refine le_trans (Finset.card_le_card ?_) (Finset.card_union_le _ _)
    intro r hr
    obtain ⟨hrW, hng⟩ := Finset.mem_filter.mp hr
    obtain ⟨_, hsr, hd⟩ := Finset.mem_filter.mp hrW
    have hng' : ¬ (l ≤ (P.pc r s).card ∨ t ∈ P.pc r s) := hng
    push Not at hng'
    rw [Finset.mem_union]
    by_cases hdeep : l ≤ (M r).card
    · left
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsr, hdeep, hng'.1, hng'.2⟩
    · right
      have htr : t ∈ M r := hd.resolve_left hdeep
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsr, htr, by omega, hng'.2⟩
  omega


theorem swap3 {α β γ : Type*} [Fintype α] [Fintype β] [Fintype γ] (f : α → β → γ → ℕ) :
    ∑ a, ∑ b, ∑ c, f a b c = ∑ c, ∑ a, ∑ b, f a b c := by
  calc ∑ a, ∑ b, ∑ c, f a b c = ∑ a, ∑ c, ∑ b, f a b c :=
        Finset.sum_congr rfl fun a _ => Finset.sum_comm
    _ = _ := Finset.sum_comm

theorem sum_not_mem {k : ℕ} (A : Finset (Fin k)) :
    ∑ t : Fin k, (if t ∉ A then 1 else 0 : ℕ) = k - A.card := by
  rw [Finset.sum_boole]
  have : (univ.filter fun t : Fin k => t ∉ A) = Aᶜ := by ext; simp
  rw [this, Finset.card_compl]; simp

theorem sum_mem_sdiff {k : ℕ} (M A : Finset (Fin k)) (h : A ⊆ M) :
    ∑ t : Fin k, (if t ∈ M ∧ t ∉ A then 1 else 0 : ℕ) = M.card - A.card := by
  rw [Finset.sum_boole]
  have : (univ.filter fun t : Fin k => t ∈ M ∧ t ∉ A) = M \ A := by ext; simp
  rw [this, Finset.card_sdiff_of_subset h]; simp

theorem rcDeep_eq (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (l : ℕ) :
    ∑ s, ∑ t, rcDeep M pc s t l =
      ∑ r, ∑ s, (if s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l then k - (pc r s).card else 0) := by
  classical
  unfold rcDeep
  simp_rw [Finset.card_filter]
  rw [swap3]
  refine Finset.sum_congr rfl fun r _ => ?_
  refine Finset.sum_congr rfl fun s _ => ?_
  by_cases hc : s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l
  · rw [if_pos hc, ← sum_not_mem (pc r s)]
    refine Finset.sum_congr rfl fun t _ => ?_
    by_cases ht : t ∈ pc r s <;> simp [ht, hc]
  · rw [if_neg hc]
    simp only [Finset.sum_eq_zero_iff]
    intro t _
    have : ¬ (s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l ∧ t ∉ pc r s) := fun h => hc ⟨h.1, h.2.1, h.2.2.1⟩
    simp [this]

theorem rcShal_eq (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (l : ℕ)
    (hsub : ∀ r s, s ∈ M r → pc r s ⊆ M r) :
    ∑ s, ∑ t, rcShal M pc s t l =
      ∑ r, ∑ s, (if s ∈ M r ∧ (M r).card < l then (M r).card - (pc r s).card else 0) := by
  classical
  unfold rcShal
  simp_rw [Finset.card_filter]
  rw [swap3]
  refine Finset.sum_congr rfl fun r _ => ?_
  refine Finset.sum_congr rfl fun s _ => ?_
  by_cases hc : s ∈ M r ∧ (M r).card < l
  · rw [if_pos hc, ← sum_mem_sdiff (M r) (pc r s) (hsub r s hc.1)]
    refine Finset.sum_congr rfl fun t _ => ?_
    by_cases ht : t ∈ M r <;> by_cases ht2 : t ∈ pc r s <;> simp [ht, ht2, hc]
  · rw [if_neg hc]
    simp only [Finset.sum_eq_zero_iff]
    intro t _
    have : ¬ (s ∈ M r ∧ t ∈ M r ∧ (M r).card < l ∧ t ∉ pc r s) := fun h => hc ⟨h.1, h.2.2.1⟩
    simp [this]

/-- averaged RC2 (per-stage form): summing the pair form over all ordered pairs `s /= t`. -/
theorem rc2_avg (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin m → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (l : ℕ) (hl : 2 ≤ l)
    (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det) :
    m * (k * (k - 1)) ≤ ∑ r, (
      (∑ s, (if s ∈ M r ∧ l ≤ (M r).card ∧ (P.pc r s).card < l then k - (P.pc r s).card else 0)) +
      (∑ s, (if s ∈ M r ∧ (M r).card < l then (M r).card - (P.pc r s).card else 0))) := by
  classical
  rw [Finset.sum_add_distrib, ← rcDeep_eq M P.pc l, ← rcShal_eq M P.pc l P.pc_sub,
    ← Finset.sum_add_distrib]
  have hrow : ∀ s : Fin k, (k - 1) * m ≤ ∑ t, (rcDeep M P.pc s t l + rcShal M P.pc s t l) := by
    intro s
    calc (k - 1) * m = ∑ t ∈ univ.erase s, m := by
          rw [Finset.sum_const, Finset.card_erase_of_mem (Finset.mem_univ _)]; simp
      _ ≤ ∑ t ∈ univ.erase s, (rcDeep M P.pc s t l + rcShal M P.pc s t l) :=
          Finset.sum_le_sum fun t ht =>
            rc2_pair M bh ah hbh hah P s t (Finset.ne_of_mem_erase ht).symm l hl (hG s t (Finset.ne_of_mem_erase ht).symm)
      _ ≤ ∑ t, (rcDeep M P.pc s t l + rcShal M P.pc s t l) :=
          Finset.sum_le_sum_of_subset (Finset.erase_subset _ _)
  calc m * (k * (k - 1)) = ∑ s : Fin k, (k - 1) * m := by
        rw [Finset.sum_const]; simp [mul_comm, mul_left_comm]
    _ ≤ ∑ s, ∑ t, (rcDeep M P.pc s t l + rcShal M P.pc s t l) := Finset.sum_le_sum fun s _ => hrow s
    _ = _ := by simp_rw [Finset.sum_add_distrib]

end rc2

/-! ## bridge: every CallerSGram `P_k = -1` frame supplies the hypotheses of RC2 -/
section bridge
variable {K : Type*} [Field K] {n k m : ℕ}

open Classical in
/-- mask of role `r`: stages where its `A`- or `B`-row is nonzero -/
noncomputable def maskOf (A B : Matrix (Fin n) (Fin k × Fin m) K) (r : Fin n) : Finset (Fin k) :=
  Finset.univ.filter fun s => meets A B r s

theorem mem_maskOf (A B : Matrix (Fin n) (Fin k × Fin m) K) (r : Fin n) (s : Fin k) :
    s ∈ maskOf A B r ↔ meets A B r s := by
  classical
  simp [maskOf]

/-- off-diagonal Gram blocks of a `P_k = -1` frame are invertible (the step inside `sgPairCoverage`). -/
theorem sgG_blk_unit (A B : Matrix (Fin n) (Fin k × Fin m) K) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B (fun i => (i.1 : ℕ)) k = -1) (hn : n + m = k * m)
    (hdiag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det)
    (s t : Fin k) (hst : s ≠ t) : IsUnit (blkOf (sgG A B) s t).det := by
  have hF := (sgForward A B (fun i => (i.1 : ℕ)) k h2 (fun i => i.1.isLt) hP).1
  simp only [Fintype.card_prod, Fintype.card_fin] at hF
  have hr : (sgK (fun i => (i.1 : ℕ)) (sgG A B)).rank ≤ m := by omega
  exact blk_G_unit _ s t hst (blk_unit _ hr s t (hdiag s) (hdiag t))

theorem gBlk_eq_blkOf (A B : Matrix (Fin n) (Fin k × Fin m) K) (s t : Fin k) :
    gBlk (fun r s a => B r (s, a)) (fun r s a => A r (s, a)) s t = blkOf (sgG A B) s t := by
  ext a b
  simp [gBlk, blkOf, sgG, Matrix.mul_apply, Matrix.transpose_apply]

/-- RC2 pair form in a CallerSGram frame, for ANY piece data on the frame's masks. -/
theorem rc2_pair_sg (A B : Matrix (Fin n) (Fin k × Fin m) K) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B (fun i => (i.1 : ℕ)) k = -1) (hn : n + m = k * m)
    (hdiag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det)
    (P : Pieces (maskOf A B) (fun r s a => B r (s, a)))
    (s t : Fin k) (hst : s ≠ t) (l : ℕ) (hl : 2 ≤ l) :
    m ≤ rcDeep (maskOf A B) P.pc s t l + rcShal (maskOf A B) P.pc s t l := by
  refine rc2_pair (maskOf A B) (fun r s a => B r (s, a)) (fun r s a => A r (s, a)) ?_ ?_ P s t hst l hl ?_
  · intro r s hs a
    by_contra h
    exact hs ((mem_maskOf A B r s).mpr ⟨a, Or.inr h⟩)
  · intro r s hs a
    by_contra h
    exact hs ((mem_maskOf A B r s).mpr ⟨a, Or.inl h⟩)
  · rw [gBlk_eq_blkOf]; exact sgG_blk_unit A B h2 hP hn hdiag s t hst

end bridge

/-! ## non-vacuity 1: k = 3, m = 2, n = 4 (CallerSGram's design), all-singleton pieces -/
section inst1
variable {R : Type*} [Fintype R] [DecidableEq R] {k m : ℕ} {K : Type*} [Field K]

/-- all-singleton pieces (every stage of every role is a main): the kernel family is empty. -/
def singP (M : R → Finset (Fin k)) (bh : R → Fin k → Fin m → K) : Pieces M bh where
  pc := fun _ s => {s}
  x := fun _ _ _ => 0
  y := fun _ _ _ => 0
  pc_mem := by intro r s _; simp
  pc_sub := by intro r s h; simpa using h
  x_supp := by intro r s _ h; simp at h
  x_ker := by intro r s _ h; simp at h
  biorth := by intro r s r' s' _ _ h; simp at h

theorem inst_rc2 : ∀ s t : Fin 3, s ≠ t → ∀ l, 2 ≤ l →
    2 ≤ rcDeep (maskOf A3 B3) (singP (maskOf A3 B3) (fun r s a => B3 r (s, a))).pc s t l
      + rcShal (maskOf A3 B3) (singP (maskOf A3 B3) (fun r s a => B3 r (s, a))).pc s t l :=
  fun s t hst l hl => rc2_pair_sg A3 B3 (by norm_num) prod_A3B3 (by norm_num) diag_unit_A3B3
    (singP _ _) s t hst l hl

end inst1

/-! ## non-vacuity 2: toy with a genuine multi piece (a kernel vector is used) -/
section toy

def toyM : Fin 3 → Finset (Fin 2) := fun _ => Finset.univ
def toyB : Fin 3 → Fin 2 → Fin 2 → ℚ := fun r _ => ![![1, 0], ![0, 1], ![1, 0]] r
def toyA : Fin 3 → Fin 2 → Fin 2 → ℚ := fun r _ => ![![1, 0], ![0, 1], ![0, 0]] r

/-- role 2 has the 2-stage piece `{0,1}` (kernel vector `(1,0,-1)`, since `bh_0 = bh_2`); roles 0,1 are mains -/
def toyP : Pieces toyM toyB where
  pc := fun r s => if r = 2 then Finset.univ else {s}
  x := fun r _ r' => if r = 2 then ![(1 : ℚ), 0, -1] r' else 0
  y := fun r _ r' => if r = 2 then ![(0 : ℚ), 0, -1] r' else 0
  pc_mem := by intro r s _; by_cases h : r = 2 <;> simp [h]
  pc_sub := by intro r s _; simp [toyM]
  x_supp := by intro r s _ _ r' _; simp [toyM]
  x_ker := by
    intro r s _ h2 s' _ a
    by_cases h : r = 2
    · fin_cases a <;> simp [h, toyB, Fin.sum_univ_three]
    · simp [h] at h2
  biorth := by
    intro r s r' s' _ _ h h' _
    by_cases hr : r = 2
    · by_cases hr' : r' = 2
      · subst hr; subst hr'; simp [Fin.sum_univ_three]
      · simp [hr'] at h'
    · simp [hr] at h

theorem toy_gunit : IsUnit (gBlk toyB toyA 0 1).det := by
  rw [isUnit_iff_ne_zero]
  simp [gBlk, Matrix.det_fin_two, toyB, toyA, Fin.sum_univ_three]

/-- the multi piece exists and its kernel vector is nonzero -/
theorem toy_piece : 2 ≤ (toyP.pc 2 0).card ∧ toyP.x 2 0 0 ≠ 0 := by
  refine ⟨?_, ?_⟩ <;> simp [toyP]

theorem toy_rc2 : 2 ≤ rcDeep toyM toyP.pc 0 1 2 + rcShal toyM toyP.pc 0 1 2 :=
  rc2_pair toyM toyB toyA (by intro r s h; exact absurd (by simp [toyM]) h)
    (by intro r s h; exact absurd (by simp [toyM]) h) toyP 0 1 (by decide) 2 le_rfl toy_gunit

/-- exact values: both deep roles 0,1 are counted, the piece-carrying role 2 is not (tight). -/
theorem toy_rc2_val : rcDeep toyM toyP.pc 0 1 2 = 2 ∧ rcShal toyM toyP.pc 0 1 2 = 0 := by
  constructor <;> simp [rcDeep, rcShal, toyM, toyP] <;> decide

end toy

#print axioms rc2_lin
#print axioms rc2_pair
#print axioms rc2_avg
#print axioms rc2_pair_sg
#print axioms inst_rc2
#print axioms toy_rc2
#print axioms toy_rc2_val
end CallerSign

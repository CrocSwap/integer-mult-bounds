/-
CallerExtraThin (lane EXTRATHIN).  Excess-thin (e = T - Q >= 1) caller laws, on HOST columns only.
(1) rc2_lin_rank : rc2_lin with "span contains rho independent vectors" instead of "span = K^m".
(2) rc2_set      : SET-RC2.  For a stage s and ANY partner set T (s notin T), if rho independent vectors lie in the
                   column space of the Gram strip G_{s,T} = [G_st]_{t in T}, then
                   rho <= #{deep (|M|>=l) roles at s, |P_r(s)| < l, P_r(s) disjoint T}
                        + #{shallow roles at s meeting T, P_r(s) disjoint T}.
                   T = {t} with rho = 2 is CallerRC2.rc2_pair; rho = rank G_{s,T} is the e-robust form (any e).
(3) deficit      : DEFICIT.  Kh = host part of K (block (s,a),(t,b)), 2x2 diagonal blocks invertible.  If stage s carries
                   d s independent left-null vectors of its off-diagonal strip, and d t0 = 0, then
                   sum_s d s + 2 <= rank Kh   ( <= rank K <= 2 + e  by sgForward ).
(4) non-vacuity  : a one-role two-stage rc2_set instance; deficit tight on Kh = 1 (k = 2, d = (0,2), rank 4).
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.Nondegenerate
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Nov15.CallerRC2

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerExtraThin
open Matrix Finset CallerSign

section lin
variable {K : Type*} [Field K] {R : Type*} [Fintype R] [DecidableEq R] {m : ℕ}

theorem rc2_lin_rank (W : Finset R) (b : R → Fin m → K) {ρ : ℕ} (u : Fin ρ → Fin m → K)
    (hu : LinearIndependent K u)
    (hin : ∀ i, ∃ c : R → K, (∀ r, r ∉ W → c r = 0) ∧ ∀ a, ∑ r, c r * b r a = u i a)
    {ι : Type*} [Fintype ι] (xs : ι → R → K) (hind : LinearIndependent K xs)
    (hsupp : ∀ i r, xs i r ≠ 0 → r ∈ W) (hker : ∀ i a, ∑ r, xs i r * b r a = 0) :
    ρ + Fintype.card ι ≤ W.card := by
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
  have hmem : ∀ i, u i ∈ LinearMap.range g := by
    intro i
    obtain ⟨c, hc, hv⟩ := hin i
    refine ⟨fun r => c r.1, ?_⟩
    funext a
    rw [hsum c hc a, hv a]
  have hrk : ρ ≤ Module.finrank K (LinearMap.range g) := by
    let ur : Fin ρ → LinearMap.range g := fun i => ⟨u i, hmem i⟩
    have hur : LinearIndependent K ur := by
      apply LinearIndependent.of_comp (LinearMap.range g).subtype
      exact hu
    simpa using hur.fintype_card_le_finrank
  have hrn := LinearMap.finrank_range_add_finrank_ker g
  rw [Module.finrank_fintype_fun_eq_card, Fintype.card_coe] at hrn
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

section set
variable {K : Type*} [Field K] {R : Type*} [Fintype R] [DecidableEq R] {k m : ℕ}

/-- deep (|M| >= l) roles at `s` whose piece at `s` is small and misses `T` -/
def rcDeepT (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (s : Fin k) (T : Finset (Fin k)) (l : ℕ) : ℕ :=
  (univ.filter fun r => s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l ∧ Disjoint (pc r s) T).card

/-- shallow roles at `s` meeting `T` whose piece at `s` misses `T` -/
def rcShalT (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k)) (s : Fin k) (T : Finset (Fin k)) (l : ℕ) : ℕ :=
  (univ.filter fun r => s ∈ M r ∧ (M r ∩ T).Nonempty ∧ (M r).card < l ∧ Disjoint (pc r s) T).card

theorem rc2_set (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin m → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (s : Fin k) (T : Finset (Fin k)) (hsT : s ∉ T) (l : ℕ) (hl : 2 ≤ l)
    {ρ : ℕ} (u : Fin ρ → Fin m → K) (hu : LinearIndependent K u)
    (hcol : ∀ i, ∃ w : Fin k → Fin m → K, (∀ t, t ∉ T → w t = 0) ∧
        u i = ∑ t, (gBlk bh ah s t) *ᵥ w t) :
    ρ ≤ rcDeepT M P.pc s T l + rcShalT M P.pc s T l := by
  classical
  set W : Finset R := univ.filter fun r => s ∈ M r ∧ (l ≤ (M r).card ∨ (M r ∩ T).Nonempty) with hW
  set good : R → Prop := fun r => l ≤ (P.pc r s).card ∨ (P.pc r s ∩ T).Nonempty with hgood
  set Wg : Finset R := W.filter good with hWg
  have hcard2 : ∀ r, s ∈ M r → good r → 2 ≤ (P.pc r s).card := by
    intro r hr hg
    rcases hg with h | ⟨t, ht⟩
    · omega
    · have hts : t ≠ s := fun e => hsT (e ▸ (Finset.mem_inter.mp ht).2)
      have hsub : ({s, t} : Finset (Fin k)) ⊆ P.pc r s := by
        intro u hu
        rcases Finset.mem_insert.mp hu with rfl | hu
        · exact P.pc_mem r _ hr
        · rw [Finset.mem_singleton.mp hu]; exact (Finset.mem_inter.mp ht).1
      have := Finset.card_le_card hsub
      rwa [Finset.card_pair (Ne.symm hts)] at this
  have hWgmem : ∀ r ∈ Wg, s ∈ M r ∧ good r := by
    intro r hr
    have hr' := Finset.mem_filter.mp hr
    exact ⟨(Finset.mem_filter.mp hr'.1).2.1, hr'.2⟩
  -- the columns of G_{s,T} lie in the span of the W-rows at s
  have hin : ∀ i, ∃ c : R → K, (∀ r, r ∉ W → c r = 0) ∧ ∀ a, ∑ r, c r * bh r s a = u i a := by
    intro i
    obtain ⟨w, hw0, hwu⟩ := hcol i
    refine ⟨fun r => if r ∈ W then ∑ t, ∑ b, ah r t b * w t b else 0, ?_, ?_⟩
    · intro r hr; simp [hr]
    · intro a
      have key : u i a = ∑ t, ∑ b, ∑ r, bh r s a * ah r t b * w t b := by
        rw [hwu, Finset.sum_apply]
        refine Finset.sum_congr rfl fun t _ => ?_
        simp only [Matrix.mulVec, dotProduct, gBlk, Matrix.of_apply, Finset.sum_mul]
      have swap : ∑ t, ∑ b, ∑ r, bh r s a * ah r t b * w t b = ∑ r, ∑ t, ∑ b, bh r s a * ah r t b * w t b := by
        calc ∑ t, ∑ b, ∑ r, bh r s a * ah r t b * w t b = ∑ t, ∑ r, ∑ b, bh r s a * ah r t b * w t b :=
              Finset.sum_congr rfl (fun t _ => Finset.sum_comm)
          _ = ∑ r, ∑ t, ∑ b, bh r s a * ah r t b * w t b := Finset.sum_comm
      rw [key, swap]
      refine Finset.sum_congr rfl fun r _ => ?_
      by_cases hr : r ∈ W
      · simp only [hr, if_true, Finset.sum_mul]
        exact Finset.sum_congr rfl fun t _ => Finset.sum_congr rfl fun b _ => by ring
      · simp only [hr, if_false, zero_mul]
        symm
        refine Finset.sum_eq_zero fun t _ => Finset.sum_eq_zero fun b _ => ?_
        by_cases hsM : s ∈ M r
        · by_cases htT : t ∈ T
          · have htM : t ∉ M r := by
              intro htM
              exact hr (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsM,
                Or.inr ⟨t, Finset.mem_inter.mpr ⟨htM, htT⟩⟩⟩)
            simp [hah r t htM b]
          · simp [hw0 t htT]
        · simp [hbh r s hsM a]
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
    rcases hg with h | ⟨t, ht⟩
    · left; exact h.trans (Finset.card_le_card hsub)
    · right
      exact ⟨t, Finset.mem_inter.mpr ⟨hsub (Finset.mem_inter.mp ht).1, (Finset.mem_inter.mp ht).2⟩⟩
  have hker : ∀ i a, ∑ r, xs i r * bh r s a = 0 := by
    intro i a
    obtain ⟨hsr, hg⟩ := hWgmem i.1 i.2
    exact P.x_ker i.1 s hsr (hcard2 i.1 hsr hg) s (P.pc_mem i.1 s hsr) a
  have hmain := rc2_lin_rank W (fun r => bh r s) u hu hin xs hind hsupp hker
  have hιcard : Fintype.card ι = Wg.card := Fintype.card_coe Wg
  have hsplit : Wg.card + (W.filter fun r => ¬ good r).card = W.card :=
    Finset.card_filter_add_card_filter_not good
  have hng : (W.filter fun r => ¬ good r).card ≤ rcDeepT M P.pc s T l + rcShalT M P.pc s T l := by
    refine le_trans (Finset.card_le_card ?_) (Finset.card_union_le _ _)
    intro r hr
    obtain ⟨hrW, hng⟩ := Finset.mem_filter.mp hr
    obtain ⟨_, hsr, hd⟩ := Finset.mem_filter.mp hrW
    have hng' : ¬ (l ≤ (P.pc r s).card ∨ (P.pc r s ∩ T).Nonempty) := hng
    push Not at hng'
    have hdisj : Disjoint (P.pc r s) T := Finset.disjoint_iff_inter_eq_empty.mpr hng'.2
    rw [Finset.mem_union]
    by_cases hdeep : l ≤ (M r).card
    · left
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsr, hdeep, hng'.1, hdisj⟩
    · right
      exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, hsr, hd.resolve_left hdeep, by omega, hdisj⟩
  omega

end set

section deficit
variable {K : Type*} [Field K] {k : ℕ}

/-- DEFICIT.  `Kh` indexed by (stage, slot); diagonal 2x2 blocks invertible; `v s` = `d s` independent left-null vectors
    of stage s's off-diagonal strip; `d t0 = 0`.  Then `sum d + 2 <= rank Kh`. -/
theorem deficit (Kh : Matrix (Fin k × Fin 2) (Fin k × Fin 2) K)
    (hdiag : ∀ s, (Kh.submatrix (fun a => (s, a)) (fun a => (s, a))).det ≠ 0)
    (d : Fin k → ℕ) (v : ∀ s, Fin (d s) → Fin 2 → K) (hv : ∀ s, LinearIndependent K (v s))
    (hnull : ∀ s j t b, t ≠ s → ∑ a, v s j a * Kh (s, a) (t, b) = 0)
    (t0 : Fin k) (hd0 : d t0 = 0) :
    (∑ s, d s) + 2 ≤ Kh.rank := by
  classical
  let F : (Σ s, Fin (d s)) ⊕ Fin 2 → (Fin k × Fin 2 → K) := fun i =>
    match i with
    | Sum.inl ⟨s, j⟩ => ∑ a, v s j a • Kh (s, a)
    | Sum.inr a => Kh (t0, a)
  have hFval : ∀ s j c, F (Sum.inl ⟨s, j⟩) c = ∑ a, v s j a * Kh (s, a) c := by
    intro s j c; simp [F, Finset.sum_apply]
  have hFr : ∀ a c, F (Sum.inr a) c = Kh (t0, a) c := fun a c => rfl
  have hspan : ∀ i, F i ∈ Submodule.span K (Set.range Kh.row) := by
    intro i
    rcases i with ⟨s, j⟩ | a
    · exact Submodule.sum_mem _ fun a _ => Submodule.smul_mem _ _ (Submodule.subset_span ⟨(s, a), rfl⟩)
    · exact Submodule.subset_span ⟨(t0, a), rfl⟩
  have hind : LinearIndependent K F := by
    rw [Fintype.linearIndependent_iff]
    intro g hg
    have hev : ∀ c, (∑ s, ∑ j, g (Sum.inl ⟨s, j⟩) * ∑ a, v s j a * Kh (s, a) c)
        + ∑ a, g (Sum.inr a) * Kh (t0, a) c = 0 := by
      intro c
      have := congrFun hg c
      rw [Fintype.sum_sum_type, Fintype.sum_sigma] at this
      simp only [Pi.add_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply, hFval, hFr] at this
      exact this
    -- block t0
    have hoff : ∀ s j b, s ≠ t0 → ∑ a, v s j a * Kh (s, a) (t0, b) = 0 := fun s j b h => hnull s j t0 b (Ne.symm h)
    have hz0 : ∀ s, ∑ j, g (Sum.inl ⟨s, j⟩) * ∑ a, v s j a * Kh (s, a) (t0, 0) = 0 ∧
        ∑ j, g (Sum.inl ⟨s, j⟩) * ∑ a, v s j a * Kh (s, a) (t0, 1) = 0 := by
      intro s
      by_cases h : s = t0
      · subst h
        have : IsEmpty (Fin (d s)) := by rw [hd0]; exact Fin.isEmpty'
        exact ⟨Finset.sum_of_isEmpty _, Finset.sum_of_isEmpty _⟩
      · exact ⟨Finset.sum_eq_zero fun j _ => by rw [hoff s j 0 h, mul_zero],
          Finset.sum_eq_zero fun j _ => by rw [hoff s j 1 h, mul_zero]⟩
    have hgr : (fun a => g (Sum.inr a)) = 0 := by
      apply Matrix.eq_zero_of_vecMul_eq_zero (hdiag t0)
      funext b
      have e := hev (t0, b)
      have hs : ∑ s, ∑ j, g (Sum.inl ⟨s, j⟩) * ∑ a, v s j a * Kh (s, a) (t0, b) = 0 := by
        refine Finset.sum_eq_zero fun s _ => ?_
        fin_cases b
        · exact (hz0 s).1
        · exact (hz0 s).2
      rw [hs, zero_add] at e
      simpa [Matrix.vecMul, dotProduct, Matrix.submatrix_apply] using e
    have hgr' : ∀ a, g (Sum.inr a) = 0 := fun a => congrFun hgr a
    -- each stage block
    have hgl : ∀ s j, g (Sum.inl ⟨s, j⟩) = 0 := by
      intro s
      have hw : (fun a => ∑ j, g (Sum.inl ⟨s, j⟩) * v s j a) = 0 := by
        apply Matrix.eq_zero_of_vecMul_eq_zero (hdiag s)
        funext b
        have e := hev (s, b)
        simp only [hgr', zero_mul, Finset.sum_const_zero, add_zero] at e
        have hothers : ∀ s', s' ≠ s → ∑ j, g (Sum.inl ⟨s', j⟩) * ∑ a, v s' j a * Kh (s', a) (s, b) = 0 :=
          fun s' h => Finset.sum_eq_zero fun j _ => by rw [hnull s' j s b (Ne.symm h), mul_zero]
        rw [Finset.sum_eq_single s (fun s' _ h => hothers s' h) (by simp)] at e
        simp only [Matrix.vecMul, dotProduct, Matrix.submatrix_apply, Pi.zero_apply]
        rw [← e]
        simp_rw [Finset.sum_mul, Finset.mul_sum]
        rw [Finset.sum_comm]
        exact Finset.sum_congr rfl fun a _ => Finset.sum_congr rfl fun j _ => by ring
      have := (Fintype.linearIndependent_iff.mp (hv s)) (fun j => g (Sum.inl ⟨s, j⟩))
        (by funext a; have := congrFun hw a; simpa [Finset.sum_apply] using this)
      exact this
    intro i
    rcases i with ⟨s, j⟩ | a
    · exact hgl s j
    · exact hgr' a
  let Fs : (Σ s, Fin (d s)) ⊕ Fin 2 → Submodule.span K (Set.range Kh.row) := fun i => ⟨F i, hspan i⟩
  have hFs : LinearIndependent K Fs := by
    apply LinearIndependent.of_comp (Submodule.span K (Set.range Kh.row)).subtype
    exact hind
  have hc := hFs.fintype_card_le_finrank
  rw [Matrix.rank_eq_finrank_span_row]
  simpa [Fintype.card_sum, Fintype.card_sigma] using hc

end deficit

/-! ## non-vacuity -/
section inst
/-- one role, two stages, m = 1: b = a = 1 at both stages, singleton pieces. -/
def M1 : Fin 1 → Finset (Fin 2) := fun _ => Finset.univ
def b1 : Fin 1 → Fin 2 → Fin 1 → ℚ := fun _ _ _ => 1
def P1 : Pieces M1 b1 := singP M1 b1

theorem inst_set : 1 ≤ rcDeepT M1 P1.pc 0 {1} 2 + rcShalT M1 P1.pc 0 {1} 2 := by
  refine rc2_set M1 b1 b1 (fun r s h => by simp [M1] at h) (fun r s h => by simp [M1] at h) P1 0 {1}
    (by decide) 2 le_rfl (u := fun _ => fun _ => 1) ?_ ?_
  · rw [Fintype.linearIndependent_iff]
    intro g hg i
    have := congrFun hg 0
    fin_cases i
    simpa using this
  · intro i
    refine ⟨fun t => if t = 1 then fun _ => 1 else 0, ?_, ?_⟩
    · intro t ht; simp at ht; simp [ht]
    · funext a
      simp [Fin.sum_univ_two, gBlk, b1, Matrix.mulVec, dotProduct]

/-- the role really is counted: rcDeepT = 1 (deep singleton at stage 0 missing T = {1}). -/
theorem inst_set_val : rcDeepT M1 P1.pc 0 {1} 2 = 1 := by decide

theorem inst_deficit : (∑ s : Fin 2, (![0, 2] : Fin 2 → ℕ) s) + 2 ≤ (1 : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℚ).rank := by
  refine deficit (1 : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℚ) ?_ ![0, 2]
    (fun s => fun j => fun a => if (j : ℕ) = (a : ℕ) then 1 else 0) ?_ ?_ 0 rfl
  · intro s; simp [Matrix.det_fin_two, Matrix.one_apply]
  · intro s
    rw [Fintype.linearIndependent_iff]
    intro g hg j
    have := congrFun hg ⟨j.1, by have := j.2; fin_cases s <;> simp_all⟩
    simpa [Finset.sum_apply, Fin.val_inj, Finset.sum_ite_eq'] using this
  · intro s j t b h
    simp [Matrix.one_apply, Prod.ext_iff, Ne.symm h]

theorem inst_deficit_tight : (1 : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℚ).rank = 4 := by
  rw [Matrix.rank_one]; simp

end inst
end CallerExtraThin

#print axioms CallerExtraThin.rc2_lin_rank
#print axioms CallerExtraThin.rc2_set
#print axioms CallerExtraThin.deficit
#print axioms CallerExtraThin.inst_set
#print axioms CallerExtraThin.inst_set_val
#print axioms CallerExtraThin.inst_deficit
#print axioms CallerExtraThin.inst_deficit_tight

/-
SPECBREAK R35 Lemma COV (corrected covering lemma), lane LEAN-NEXT28, Nov 17.
Source: cards/WILD/SPECBREAK/R35/RESULT35.md item 2 (after R34/AUDIT-ALEMMA.md). See SpecCOV.md.
Builds on Nov15/SpecTSUR.lean (pp, Xm, Zm, Nm, product formula, sum_ZY, Nm_isUnit) and the
Sylvester inequality of Nov15/Budget.lean.
-/
import Nov15.SpecTSUR
import Nov15.Budget

open Matrix Finset SpecTSUR

set_option linter.unusedSectionVars false

namespace SpecCOV

variable {K : Type*} [Field K]

/-! ## §1. Per-character Sylvester bound `s + t ≤ m + rank(I - P)` -/
section Char
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem rank_Xm (x : ℕ → n → K) (m : ℕ) :
    (Xm x m).rank = Module.finrank K (Submodule.span K (x '' Set.Iio m)) := by
  have hs : Set.range (Xm x m).col = x '' Set.Iio m := by
    ext v
    simp only [Set.mem_range, Set.mem_image, Set.mem_Iio]
    constructor
    · rintro ⟨i, rfl⟩; exact ⟨i, i.2, rfl⟩
    · rintro ⟨k, hk, rfl⟩; exact ⟨⟨k, hk⟩, rfl⟩
  rw [Matrix.rank_eq_finrank_span_cols, hs]

theorem rank_Zm (x y : ℕ → n → K) (m : ℕ) : (Zm x y m).rank = (Xm x m).rank := by
  have hu : IsUnit (Nm x y m).det := (Matrix.isUnit_iff_isUnit_det _).1 (Nm_isUnit x y m)
  rw [← ZN_eq x y m, Matrix.rank_mul_eq_left_of_isUnit_det _ _ hu]

/-- **Sylvester per character**: the product of the first `m` jobs `P` satisfies
`rk X + rk Y ≤ m + rank (I - P)`, with `rk X = dim span {x_k : k < m}`. No hypothesis on `y_k·x_k`. -/
theorem char_syl (x y : ℕ → n → K) (m : ℕ) :
    Module.finrank K (Submodule.span K (x '' Set.Iio m)) +
      Module.finrank K (Submodule.span K (y '' Set.Iio m)) ≤ m + (1 - pp x y m).rank := by
  have h := SYL.sylvester (Zm x y m) (Matrix.of fun a (i : Fin m) => y i a)ᵀ
  rw [rank_Zm, Matrix.rank_transpose, Fintype.card_fin] at h
  have e : (1 : Matrix n n K) - pp x y m = Zm x y m * (Matrix.of fun a (i : Fin m) => y i a)ᵀ := by
    rw [pp_eq, sub_sub_cancel, sum_ZY]
  rw [← e] at h
  have h1 : (Matrix.of fun a (i : Fin m) => y i a).rank = (Xm y m).rank := rfl
  rw [h1, rank_Xm, rank_Xm] at h
  exact h

end Char

/-! ## §2. Covering dimension count -/
section Cover
open Classical

variable {F : Type*} [DecidableEq F] {V : Type*} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- union of the first `j` active sets -/
noncomputable def Tu (S : ℕ → Finset F) (j : ℕ) : Finset F := (range j).biUnion S

theorem Tu_succ (S : ℕ → Finset F) (j : ℕ) : Tu S (j + 1) = Tu S j ∪ S j := by
  simp [Tu, Finset.range_add_one, Finset.biUnion_insert, Finset.union_comm]

/-- **subadditivity with overlap correction**: each character `i` flagged as an overlap has a shared
element `f ∈ S i ∩ Tu S i` with `v f ≠ 0`; then
`dim span(v '' union) + #overlaps ≤ Σ dim span(v '' S i)`. -/
theorem cover_dim (v : F → V) (S : ℕ → Finset F) (flag : ℕ → Prop) [DecidablePred flag]
    (hflag : ∀ i, flag i → ∃ f ∈ S i, f ∈ Tu S i ∧ v f ≠ 0) (j : ℕ) :
    Module.finrank K (Submodule.span K (v '' (Tu S j : Set F))) + ((range j).filter flag).card ≤
      ∑ i ∈ range j, Module.finrank K (Submodule.span K (v '' (S i : Set F))) := by
  induction j with
  | zero =>
    have h0 : Tu S 0 = ∅ := by simp [Tu]
    rw [h0]
    simp
  | succ j ih =>
    rw [Tu_succ, Finset.sum_range_succ, Finset.range_add_one, Finset.filter_insert]
    have hj : j ∉ (range j).filter flag := by simp
    have hsup := Submodule.finrank_sup_add_finrank_inf_eq
      (Submodule.span K (v '' (Tu S j : Set F))) (Submodule.span K (v '' (S j : Set F)))
    have hspan : Submodule.span K (v '' ((Tu S j ∪ S j : Finset F) : Set F)) =
        Submodule.span K (v '' (Tu S j : Set F)) ⊔ Submodule.span K (v '' (S j : Set F)) := by
      rw [Finset.coe_union, Set.image_union, Submodule.span_union]
    rw [hspan]
    by_cases hf : flag j
    · obtain ⟨f, hfS, hfT, hv⟩ := hflag j hf
      have hne : Submodule.span K (v '' (Tu S j : Set F)) ⊓ Submodule.span K (v '' (S j : Set F)) ≠ ⊥ := by
        intro hb
        have hm : v f ∈ Submodule.span K (v '' (Tu S j : Set F)) ⊓ Submodule.span K (v '' (S j : Set F)) :=
          ⟨Submodule.subset_span ⟨f, by exact_mod_cast hfT, rfl⟩,
           Submodule.subset_span ⟨f, by exact_mod_cast hfS, rfl⟩⟩
        rw [hb] at hm
        exact hv (by simpa using hm)
      have h1 := Submodule.one_le_finrank_iff.2 hne
      rw [if_pos hf, Finset.card_insert_of_notMem hj]
      omega
    · rw [if_neg hf]
      omega

variable [Fintype F]

/-- uncovered factors cost at most one dimension each -/
theorem finrank_le_cover (v : F → V) (hspan : Submodule.span K (Set.range v) = ⊤) (T : Finset F) :
    Module.finrank K V ≤ Module.finrank K (Submodule.span K (v '' (T : Set F))) + (univ \ T).card := by
  have hle : (⊤ : Submodule K V) ≤ Submodule.span K (v '' (T : Set F)) ⊔
      Submodule.span K (v '' ((univ \ T : Finset F) : Set F)) := by
    rw [← hspan, ← Submodule.span_union, Submodule.span_le]
    rintro _ ⟨f, rfl⟩
    by_cases hf : f ∈ T
    · exact Submodule.subset_span (Or.inl ⟨f, hf, rfl⟩)
    · exact Submodule.subset_span (Or.inr ⟨f, by simpa using hf, rfl⟩)
  have h1 : Module.finrank K V ≤ Module.finrank K
      ↥(Submodule.span K (v '' (T : Set F)) ⊔ Submodule.span K (v '' ((univ \ T : Finset F) : Set F))) := by
    have := Submodule.finrank_mono hle
    simpa using this
  have h2 := Submodule.finrank_add_le_finrank_add_finrank (Submodule.span K (v '' (T : Set F)))
    (Submodule.span K (v '' ((univ \ T : Finset F) : Set F)))
  have h3 : Module.finrank K (Submodule.span K (v '' ((univ \ T : Finset F) : Set F))) ≤ (univ \ T).card := by
    have := finrank_span_finset_le_card (R := K) ((univ \ T).image v)
    rw [Finset.coe_image] at this
    exact this.trans Finset.card_image_le
  omega

end Cover

/-! ## §3. Lemma COV (general form) -/
section Main
open Classical
variable {n : Type*} [Fintype n] [DecidableEq n] {F : Type*} [Fintype F] [DecidableEq F]

/-- active factor set of character `i`: the factors `idx i 0, …, idx i (mm i - 1)` -/
noncomputable def Sset (mm : ℕ → ℕ) (idx : ℕ → ℕ → F) (i : ℕ) : Finset F :=
  (range (mm i)).image (idx i)

theorem image_Sset (v : F → n → K) (mm : ℕ → ℕ) (idx : ℕ → ℕ → F) (i : ℕ) :
    v '' (Sset mm idx i : Set F) = (fun k => v (idx i k)) '' Set.Iio (mm i) := by
  rw [Sset, Finset.coe_image, Set.image_image]
  congr 1
  ext k; simp

/-- **Lemma COV, general form.** Factors `f : F` (jobs and units) are reflections `I - x_f y_fᵀ`.
`m` characters `i`; character `i` has the ordered active factors `idx i 0 … idx i (mm i - 1)` whose
product is `D i` with `rank (I - D i) ≤ r i` (R35: `r_i = #targets flipped`, `mm i = k_i + u_i`).
Assume the `x_f` span `V` and the `y_f` span `V` (R30 A1: the x's of ALL `M = 6 + U` factors).
`flag i` marks the overlap characters: each flagged `i` shares a factor `f` with the earlier union
(`f ∈ Tu i`) with `x_f ≠ 0 ≠ y_f`.  Then
`2 n + 2·#flagged ≤ Σ_i (r_i + mm_i) + 2·#(uncovered factors)`.
No hypothesis on `y_f·x_f` and no characteristic assumption. -/
theorem COV_flag (x y : F → n → K)
    (hx : Submodule.span K (Set.range x) = ⊤) (hy : Submodule.span K (Set.range y) = ⊤)
    (m : ℕ) (mm : ℕ → ℕ) (idx : ℕ → ℕ → F) (D : ℕ → Matrix n n K) (r : ℕ → ℕ)
    (hP : ∀ i < m, pp (fun k => x (idx i k)) (fun k => y (idx i k)) (mm i) = D i)
    (hr : ∀ i < m, (1 - D i).rank ≤ r i)
    (flag : ℕ → Prop) [DecidablePred flag]
    (hflag : ∀ i, flag i → ∃ f ∈ Sset mm idx i, f ∈ Tu (Sset mm idx) i ∧ x f ≠ 0 ∧ y f ≠ 0) :
    2 * Fintype.card n + 2 * ((range m).filter flag).card
      ≤ ∑ i ∈ range m, (r i + mm i) + 2 * (univ \ Tu (Sset mm idx) m).card := by
  have hcx := cover_dim (K := K) x (Sset mm idx) flag
    (fun i hi => let ⟨f, h1, h2, h3, _⟩ := hflag i hi; ⟨f, h1, h2, h3⟩) m
  have hcy := cover_dim (K := K) y (Sset mm idx) flag
    (fun i hi => let ⟨f, h1, h2, _, h4⟩ := hflag i hi; ⟨f, h1, h2, h4⟩) m
  have hux := finrank_le_cover (K := K) x hx (Tu (Sset mm idx) m)
  have huy := finrank_le_cover (K := K) y hy (Tu (Sset mm idx) m)
  rw [Module.finrank_fintype_fun_eq_card] at hux huy
  have hsum : ∑ i ∈ range m, (Module.finrank K (Submodule.span K (x '' (Sset mm idx i : Set F))) +
      Module.finrank K (Submodule.span K (y '' (Sset mm idx i : Set F)))) ≤ ∑ i ∈ range m, (r i + mm i) := by
    refine Finset.sum_le_sum fun i hi => ?_
    have hi' : i < m := Finset.mem_range.1 hi
    have h := char_syl (fun k => x (idx i k)) (fun k => y (idx i k)) (mm i)
    rw [hP i hi'] at h
    have := hr i hi'
    rw [image_Sset, image_Sset]
    omega
  rw [Finset.sum_add_distrib] at hsum
  omega

end Main

/-! ## §4. Lemma COV in the R35 shape: factors = jobs `J` ⊕ `U` units -/
section R35
open Classical
variable {n : Type*} [Fintype n] [DecidableEq n] {J : Type*} [Fintype J]

/-- **Lemma COV (R35 item 2, corrected after the R34 audit).**
Factors: jobs `j : J` and `U` units (`Fin U`), `x_f, y_f` their reflection vectors, all `x_f` span `V`
and all `y_f` span `V` (R30 A1, `M = |J| + U` factors).  Character `i < m`: active jobs `Sj i`
(`k_i = |Sj i|`), units active iff `q i` (`u_i = U` then, else `0`), the active factors listed once each
in the word order by `idx i`, with product `D i` and `rank (I - D i) ≤ r i` (`r_i = #flipped targets`).
Overlap characters: share a job with an earlier character (`x_j ≠ 0 ≠ y_j`), or the unit block with an
earlier character (units nonzero).  Then
`2n + 2·#overlaps ≤ Σ_i (r_i + k_i + u_i) + 2·#uncovered jobs + 2U·[no character has units active]`. -/
theorem COV_R35 (U : ℕ) (x y : J ⊕ Fin U → n → K)
    (hx : Submodule.span K (Set.range x) = ⊤) (hy : Submodule.span K (Set.range y) = ⊤)
    (m : ℕ) (Sj : ℕ → Finset J) (q : ℕ → Prop) (mm : ℕ → ℕ) (idx : ℕ → ℕ → J ⊕ Fin U)
    (D : ℕ → Matrix n n K) (r : ℕ → ℕ)
    (hact : ∀ i < m, Sset mm idx i = (Sj i).disjSum (if q i then (univ : Finset (Fin U)) else ∅))
    (hinj : ∀ i < m, Set.InjOn (idx i) (Set.Iio (mm i)))
    (hP : ∀ i < m, pp (fun k => x (idx i k)) (fun k => y (idx i k)) (mm i) = D i)
    (hr : ∀ i < m, (1 - D i).rank ≤ r i) :
    2 * Fintype.card n +
      2 * ((range m).filter fun i =>
        (∃ j ∈ Sj i, (∃ l < i, j ∈ Sj l) ∧ x (Sum.inl j) ≠ 0 ∧ y (Sum.inl j) ≠ 0) ∨
        (q i ∧ (∃ l < i, q l) ∧ ∃ u : Fin U, x (Sum.inr u) ≠ 0 ∧ y (Sum.inr u) ≠ 0)).card
      ≤ ∑ i ∈ range m, (r i + (Sj i).card + (if q i then U else 0))
        + 2 * (univ \ (range m).biUnion Sj).card + 2 * (if ∃ i < m, q i then 0 else U) := by
  -- (1) sizes
  have hsz : ∀ i ∈ range m, mm i = (Sj i).card + (if q i then U else 0) := by
    intro i hi
    have hi' := Finset.mem_range.1 hi
    have hc : (Sset mm idx i).card = mm i := by
      have h1 := Finset.card_image_of_injOn (s := range (mm i)) (f := idx i) (by simpa using hinj i hi')
      rw [Finset.card_range] at h1
      rw [Sset]; convert h1
    rw [← hc, hact i hi', Finset.card_disjSum]
    split_ifs <;> simp
  have hsum : ∑ i ∈ range m, (r i + mm i) = ∑ i ∈ range m, (r i + (Sj i).card + (if q i then U else 0)) := by
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [hsz i hi]; ring
  -- (2) overlaps
  have hmemT : ∀ i f, f ∈ Tu (Sset mm idx) i ↔ ∃ l < i, f ∈ Sset mm idx l := by
    intro i f; simp [Tu]
  have hgen := COV_flag x y hx hy m mm idx D r hP hr
    (fun i => i < m ∧
      ((∃ j ∈ Sj i, (∃ l < i, j ∈ Sj l) ∧ x (Sum.inl j) ≠ 0 ∧ y (Sum.inl j) ≠ 0) ∨
        (q i ∧ (∃ l < i, q l) ∧ ∃ u : Fin U, x (Sum.inr u) ≠ 0 ∧ y (Sum.inr u) ≠ 0))) (by
    intro i hi
    obtain ⟨hi', hi⟩ := hi
    · rcases hi with ⟨j, hj, ⟨l, hl, hjl⟩, h1, h2⟩ | ⟨hq, ⟨l, hl, hql⟩, u, h1, h2⟩
      · refine ⟨Sum.inl j, ?_, (hmemT i _).2 ⟨l, hl, ?_⟩, h1, h2⟩
        · rw [hact i hi']; simpa using hj
        · rw [hact l (by omega)]; simpa using hjl
      · refine ⟨Sum.inr u, ?_, (hmemT i _).2 ⟨l, hl, ?_⟩, h1, h2⟩
        · rw [hact i hi']; simp [hq]
        · rw [hact l (by omega)]; simp [hql]
    )
  have hcard : ((range m).filter fun i => i < m ∧
      ((∃ j ∈ Sj i, (∃ l < i, j ∈ Sj l) ∧ x (Sum.inl j) ≠ 0 ∧ y (Sum.inl j) ≠ 0) ∨
        (q i ∧ (∃ l < i, q l) ∧ ∃ u : Fin U, x (Sum.inr u) ≠ 0 ∧ y (Sum.inr u) ≠ 0))).card =
      ((range m).filter fun i =>
        (∃ j ∈ Sj i, (∃ l < i, j ∈ Sj l) ∧ x (Sum.inl j) ≠ 0 ∧ y (Sum.inl j) ≠ 0) ∨
        (q i ∧ (∃ l < i, q l) ∧ ∃ u : Fin U, x (Sum.inr u) ≠ 0 ∧ y (Sum.inr u) ≠ 0)).card := by
    apply congrArg Finset.card
    ext i
    simp only [Finset.mem_filter, Finset.mem_range]
    exact ⟨fun h => ⟨h.1, h.2.2⟩, fun h => ⟨h.1, h.1, h.2⟩⟩
  -- (3) uncovered
  have hunc : (univ \ Tu (Sset mm idx) m).card ≤
      (univ \ (range m).biUnion Sj).card + (if ∃ i < m, q i then 0 else U) := by
    have hsub : (univ \ Tu (Sset mm idx) m) ⊆
        (univ \ (range m).biUnion Sj).disjSum
          (if ∃ i < m, q i then (∅ : Finset (Fin U)) else univ) := by
      intro f hf
      rw [Finset.mem_sdiff, hmemT] at hf
      rcases f with j | u
      · refine Finset.inl_mem_disjSum.2 ?_
        simp only [Finset.mem_sdiff, Finset.mem_univ, true_and, Finset.mem_biUnion, Finset.mem_range,
          not_exists, not_and]
        intro l hl hj
        apply hf.2
        refine ⟨l, hl, ?_⟩
        rw [hact l hl]; simpa using hj
      · refine Finset.inr_mem_disjSum.2 ?_
        by_cases hq : ∃ i < m, q i
        · exfalso
          obtain ⟨l, hl, hql⟩ := hq
          apply hf.2
          refine ⟨l, hl, ?_⟩
          rw [hact l hl]; simp [hql]
        · simp [hq]
    have := Finset.card_le_card hsub
    rw [Finset.card_disjSum] at this
    refine this.trans ?_
    split_ifs <;> simp
  rw [hsum, hcard] at hgen
  omega

end R35

/-! ## §5. Necessity of the hypotheses -/
section Sanity

/-- the spanning hypothesis (A1) of `COV_flag` cannot be dropped: `n = 1`, one factor with
`x = y = 0` (so `P = I`, `r = 0`, `m = 1`), no overlaps, nothing uncovered: the conclusion
`2·1 ≤ (0 + 1) + 0` is false, while every other hypothesis holds. -/
theorem cov_needs_span : ∃ (x y : Unit → Fin 1 → ℚ),
    Submodule.span ℚ (Set.range x) ≠ ⊤ ∧
    pp (fun k => x ((fun _ _ => ()) 0 k)) (fun k => y ((fun _ _ => ()) 0 k)) 1 = 1 ∧
    ¬ (2 * Fintype.card (Fin 1) + 2 * ((range 1).filter fun _ => False).card ≤
      ∑ i ∈ range 1, (0 + (fun _ => 1) i) +
        2 * (univ \ Tu (Sset (fun _ => 1) (fun (_ : ℕ) (_ : ℕ) => ())) 1).card) := by
  classical
  refine ⟨fun _ => 0, fun _ => 0, ?_, ?_, ?_⟩
  · intro h
    have h1 : Set.range (fun _ : Unit => (0 : Fin 1 → ℚ)) = {0} := by ext v; simp [eq_comm]
    rw [h1, Submodule.span_singleton_eq_bot.2 rfl] at h
    have := congrArg (fun S : Submodule ℚ (Fin 1 → ℚ) => Module.finrank ℚ S) h
    simp at this
  · simp [pp, SpecTSUR.refl]
  · have h2 : Tu (Sset (fun _ => 1) (fun (_ : ℕ) (_ : ℕ) => ())) 1 = (univ : Finset Unit) := by
      ext f; simp [Tu, Sset]
    rw [h2]; simp

end Sanity

end SpecCOV

#print axioms SpecCOV.char_syl
#print axioms SpecCOV.cover_dim
#print axioms SpecCOV.finrank_le_cover
#print axioms SpecCOV.COV_flag
#print axioms SpecCOV.COV_R35
#print axioms SpecCOV.cov_needs_span

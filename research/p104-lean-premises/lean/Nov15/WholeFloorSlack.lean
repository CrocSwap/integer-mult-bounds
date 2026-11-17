/-
WholeFloorSlack : the SLACK-RANK lemma of WHOLEFLOOR R3 §2.
For a run reaching s and a chart c:
  stay c   = public registers ending at c           (F_stay: their final rows)
  BL c     = public registers born at c that leave   (E_BL: their unit rows)
  passers  = public entrants into c that end elsewhere (= enter, then leave: public never CLEARed)
  o_c      = owned MOVEs into c
Hypothesis `Indep c` (R3: "independent ... checked"): the final rows of stay c together with the unit
rows of BL c are linearly independent. Then
  dim I_c ≤ |B| + |A| + o ,  |stay| + |BL| = |B| + |A| − s_c ,
  I_c = F_stay ⊕ E_BL ⊕ K_c  with  dim K_c ≤ s_c + o_c.
-/
import Nov15.WholeFloorModel

set_option linter.unusedSectionVars false

namespace WholeFloor

open Module Finset

variable {K Reg C : Type*} [Field K] [Fintype Reg] [DecidableEq Reg] [DecidableEq C] [PartialOrder C]
  (pub : Reg → Prop)

open Classical in
/-- public registers ending at c. -/
noncomputable def stayS (s : St K Reg C) (c : C) : Finset Reg :=
  univ.filter fun r => pub r ∧ s.loc r = .sit c

open Classical in
/-- public registers born at c that end elsewhere ("C-born leavers"). -/
noncomputable def blS (s : St K Reg C) (c : C) : Finset Reg :=
  (s.B c).filter fun r => s.loc r ≠ .sit c

open Classical in
/-- passers: public entrants into c that do not end at c. -/
noncomputable def passS (s : St K Reg C) (c : C) : Finset Reg :=
  (s.A c).filter fun r => s.loc r ≠ .sit c

/-- slack σ_c = s_c + o_c. -/
noncomputable def sigma (s : St K Reg C) (c : C) : ℕ := (passS s c).card + (s.O c).length

open Classical in
/-- F_stay(c): span of the final rows of the registers ending at c. -/
noncomputable def Fstay (s : St K Reg C) (c : C) : Submodule K (Reg → K) :=
  Submodule.span K ((fun r => s.row r) '' ↑(stayS pub s c))

/-- E_BL(c): span of the unit rows of c-born leavers. -/
noncomputable def EBL (s : St K Reg C) (c : C) : Submodule K (Reg → K) :=
  Submodule.span K ((fun r => (Pi.single r (1 : K) : Reg → K)) '' ↑(blS s c))

open Classical in
/-- the "target" family: final row of a stayer, unit row of a born leaver. -/
noncomputable def tv (s : St K Reg C) (c : C) (r : Reg) : Reg → K :=
  if s.loc r = .sit c then s.row r else Pi.single r 1

/-- the data hypothesis of R3 §2 (checked on words). -/
def Indep (s : St K Reg C) (c : C) : Prop :=
  LinearIndependent K (fun r : ↥(stayS pub s c ∪ blS s c) => tv s c r)

theorem gens_finrank_le (s : St K Reg C) (c : C) :
    finrank K (I s c) ≤ (s.B c).card + (s.A c).card + (s.O c).length := by
  classical
  have : gens s c = ↑(((s.B c).image fun r => (Pi.single r (1 : K) : Reg → K)) ∪
      ((s.A c).image fun r => s.eRow r c) ∪ (s.O c).toFinset) := by
    ext x; simp [gens, or_assoc]
  unfold I; rw [this]
  refine (finrank_span_finset_le_card _).trans ?_
  refine (Finset.card_union_le _ _).trans ?_
  exact add_le_add ((Finset.card_union_le _ _).trans (add_le_add Finset.card_image_le Finset.card_image_le))
    (List.toFinset_card_le _)

/-- **counting identity**: |stay| + |BL| + |passers| = |B| + |A|  (needs disjointness of B, A and
that a public register at c was born at c or entered c: the model invariants). -/
theorem count_id {s : St K Reg C} (hs : Inv pub s) (c : C) :
    (stayS pub s c).card + (blS s c).card + (passS s c).card = (s.B c).card + (s.A c).card := by
  classical
  have e1 : stayS pub s c = (s.B c).filter (fun r => s.loc r = .sit c) ∪
      (s.A c).filter (fun r => s.loc r = .sit c) := by
    ext r
    simp only [stayS, mem_filter, mem_univ, true_and, mem_union]
    constructor
    · rintro ⟨hp, hl⟩
      rcases hs.stay r c hp hl with h | h
      · exact Or.inl ⟨h, hl⟩
      · exact Or.inr ⟨h, hl⟩
    · rintro (⟨h, hl⟩ | ⟨h, hl⟩)
      · exact ⟨hs.pubBA r c (Or.inl h), hl⟩
      · exact ⟨hs.pubBA r c (Or.inr h), hl⟩
  have hd : Disjoint ((s.B c).filter (fun r => s.loc r = .sit c))
      ((s.A c).filter (fun r => s.loc r = .sit c)) :=
    Finset.disjoint_filter_filter (hs.disj c)
  have h1 : ((s.B c).filter (fun r => s.loc r = .sit c)).card + (blS s c).card = (s.B c).card := by
    convert Finset.card_filter_add_card_filter_not (s := s.B c) (fun r => s.loc r = .sit c)
    unfold blS; congr
  have h2 : ((s.A c).filter (fun r => s.loc r = .sit c)).card + (passS s c).card = (s.A c).card := by
    convert Finset.card_filter_add_card_filter_not (s := s.A c) (fun r => s.loc r = .sit c)
    unfold passS; congr
  rw [e1, Finset.card_union_of_disjoint hd]
  omega

theorem fstay_le_I {s : St K Reg C} (hs : Inv pub s) (c : C) : Fstay pub s c ≤ I s c := by
  classical
  refine Submodule.span_le.2 ?_
  rintro _ ⟨r, hr, rfl⟩
  simp only [stayS, Finset.coe_filter, mem_univ, true_and, Set.mem_ofPred_eq] at hr
  exact hs.cs r c hr.2

theorem ebl_le_I (s : St K Reg C) (c : C) : EBL s c ≤ I s c := by
  classical
  refine Submodule.span_le.2 ?_
  rintro _ ⟨r, hr, rfl⟩
  simp only [blS, Finset.coe_filter, Set.mem_ofPred_eq] at hr
  exact Submodule.subset_span (Or.inl (Or.inl ⟨r, hr.1, rfl⟩))

theorem finrank_Fstay_le (s : St K Reg C) (c : C) : finrank K (Fstay pub s c) ≤ (stayS pub s c).card := by
  classical
  have : Fstay pub s c = Submodule.span K (↑((stayS pub s c).image fun r => s.row r) : Set (Reg → K)) := by
    simp [Fstay, Finset.coe_image]
  rw [this]
  exact (finrank_span_finset_le_card _).trans Finset.card_image_le

theorem finrank_EBL_le (s : St K Reg C) (c : C) : finrank K (EBL s c) ≤ (blS s c).card := by
  classical
  have : EBL s c = Submodule.span K (↑((blS s c).image fun r => (Pi.single r (1 : K) : Reg → K)) : Set (Reg → K)) := by
    simp [EBL, Finset.coe_image]
  rw [this]
  exact (finrank_span_finset_le_card _).trans Finset.card_image_le

theorem stay_bl_disjoint (s : St K Reg C) (c : C) : Disjoint (stayS pub s c) (blS s c) := by
  classical
  rw [Finset.disjoint_left]
  intro r h1 h2
  simp only [stayS, mem_filter, mem_univ, true_and] at h1
  simp only [blS, mem_filter] at h2
  exact h2.2 h1.2

theorem span_range_tv (s : St K Reg C) (c : C) :
    Submodule.span K (Set.range fun r : ↥(stayS pub s c ∪ blS s c) => tv s c r) =
      Fstay pub s c ⊔ EBL s c := by
  classical
  unfold Fstay EBL
  rw [← Submodule.span_union]
  congr 1
  ext x
  simp only [Set.mem_range, Set.mem_union, Set.mem_image, Finset.mem_coe, Subtype.exists,
    Finset.mem_union]
  constructor
  · rintro ⟨r, hr, rfl⟩
    rcases hr with hr | hr
    · left; refine ⟨r, hr, ?_⟩
      have : s.loc r = .sit c := by simpa [stayS] using (by simpa [stayS] using hr : pub r ∧ s.loc r = .sit c).2
      simp [tv, this]
    · right; refine ⟨r, hr, ?_⟩
      have : s.loc r ≠ .sit c := by simpa [blS] using (Finset.mem_filter.1 hr).2
      simp [tv, this]
  · rintro (⟨r, hr, rfl⟩ | ⟨r, hr, rfl⟩)
    · refine ⟨r, Or.inl hr, ?_⟩
      have : s.loc r = .sit c := by simpa [stayS] using (by simpa [stayS] using hr : pub r ∧ s.loc r = .sit c).2
      simp [tv, this]
    · refine ⟨r, Or.inr hr, ?_⟩
      have : s.loc r ≠ .sit c := (Finset.mem_filter.1 hr).2
      simp [tv, this]

/-- **SLACK-RANK lemma** (R3 §2). On every reachable state, for every chart c where the data
hypothesis `Indep` holds: I_c = F_stay ⊕ E_BL ⊕ K_c with dim K_c ≤ σ_c = s_c + o_c, and
dim(F_stay ⊕ E_BL) = |B_c| + |A_c| − s_c. -/
theorem slack_rank {s : St K Reg C} (hr : Reach pub s) (c : C) (hind : Indep pub s c) :
    ∃ Kc : Submodule K (Reg → K),
      Fstay pub s c ≤ I s c ∧ EBL s c ≤ I s c ∧ Disjoint (Fstay pub s c) (EBL s c) ∧
      Disjoint (Fstay pub s c ⊔ EBL s c) Kc ∧ Fstay pub s c ⊔ EBL s c ⊔ Kc = I s c ∧
      finrank K Kc ≤ sigma s c ∧
      finrank K ↥(Fstay pub s c ⊔ EBL s c) + (passS s c).card = (s.B c).card + (s.A c).card := by
  classical
  have hs := reach_inv pub hr
  have hF := fstay_le_I pub hs c
  have hE := ebl_le_I s c
  set M := Fstay pub s c ⊔ EBL s c with hM
  have hMI : M ≤ I s c := sup_le hF hE
  have hfM : finrank K ↥M = (stayS pub s c).card + (blS s c).card := by
    have := finrank_span_eq_card hind
    rw [span_range_tv pub s c] at this
    rw [this, Fintype.card_coe, Finset.card_union_of_disjoint (stay_bl_disjoint pub s c)]
  have hcnt := count_id pub hs c
  have hdisj : Disjoint (Fstay pub s c) (EBL s c) := by
    have h := Submodule.finrank_sup_add_finrank_inf_eq (Fstay pub s c) (EBL s c)
    rw [← hM] at h
    have h1 := finrank_Fstay_le pub s c
    have h2 := finrank_EBL_le s c
    have h0 : finrank K ↥(Fstay pub s c ⊓ EBL s c) = 0 := by omega
    rw [Submodule.disjoint_def]
    intro x hx1 hx2
    have : Fstay pub s c ⊓ EBL s c = ⊥ := Submodule.finrank_eq_zero.1 h0
    have hx : x ∈ Fstay pub s c ⊓ EBL s c := ⟨hx1, hx2⟩
    rw [this] at hx; simpa using hx
  -- complement of M inside I
  obtain ⟨N, hN⟩ := Submodule.exists_isCompl (M.comap (I s c).subtype)
  refine ⟨N.map (I s c).subtype, hF, hE, hdisj, ?_, ?_, ?_, by omega⟩
  · rw [Submodule.disjoint_def]
    rintro x hxM ⟨n, hn, rfl⟩
    have hmem : n ∈ M.comap (I s c).subtype := hxM
    have : n = 0 := by
      have := hN.disjoint
      rw [Submodule.disjoint_def] at this
      exact this n hmem hn
    simp [this]
  · apply le_antisymm
    · exact sup_le hMI (by rintro _ ⟨n, _, rfl⟩; exact n.2)
    · intro x hx
      have hx' : (⟨x, hx⟩ : ↥(I s c)) ∈ (M.comap (I s c).subtype) ⊔ N := by
        rw [hN.sup_eq_top]; trivial
      obtain ⟨y, hy, z, hz, hyz⟩ := Submodule.mem_sup.1 hx'
      have : x = y.1 + z.1 := by simpa using congrArg Subtype.val hyz.symm
      rw [this]
      exact Submodule.mem_sup.2 ⟨y.1, hy, z.1, ⟨z, hz, rfl⟩, rfl⟩
  · -- dimension count
    have h1 := Submodule.finrank_add_eq_of_isCompl hN
    have h2 : finrank K ↥(N.map (I s c).subtype) = finrank K ↥N := Submodule.finrank_map_subtype_eq _ _
    have h3 : finrank K ↥(M.comap (I s c).subtype) = finrank K ↥M := by
      rw [← Submodule.finrank_map_subtype_eq (I s c) (M.comap (I s c).subtype),
        Submodule.map_comap_subtype, inf_eq_right.2 hMI]
    have h4 := gens_finrank_le s c
    simp only [sigma]
    omega

end WholeFloor

#print axioms WholeFloor.count_id
#print axioms WholeFloor.slack_rank

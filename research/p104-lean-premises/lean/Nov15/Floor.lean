/-
Class-K junk floor (780 stops = 1,081.31 D0/call), Sources: internal notes (F1, F2, F3 certificate, F4),
         internal notes (R0(a,b,c), R1, R2, R3, R4 certificate).

Everything is stated per chart / per build over an arbitrary field, with the op-model facts
(the forward span law and the entry count, ExportLaw.forward_span / forward_count / stay_count)
taken as explicit hypotheses. See Floor.md for the statement ↔ prose mapping.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.Order.WellFounded
import Mathlib.Logic.Relation
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.Ring.Defs

open Module Submodule

set_option linter.unusedSectionVars false

namespace Floor

/-! ## 1. Linear-algebra core -/
section Core
variable {K V W U : Type*} [Field K] [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
  [AddCommGroup U] [Module K U]

/-- `b` is linearly independent modulo `M`. -/
def IndepMod {ι : Type*} [Fintype ι] (M : Submodule K W) (b : ι → W) : Prop :=
  ∀ β : ι → K, (∑ i, β i • b i) ∈ M → ∀ i, β i = 0

/-- Independence mod `M` adds exactly `|ι|` to the dimension. -/
theorem finrank_sup_of_indepMod [FiniteDimensional K W] {ι : Type*} [Fintype ι]
    (M : Submodule K W) (b : ι → W) (hb : IndepMod M b) :
    finrank K (M ⊔ span K (Set.range b) : Submodule K W) = finrank K M + Fintype.card ι := by
  have hli : LinearIndependent K b := by
    rw [Fintype.linearIndependent_iff]
    intro g hg; exact hb g (by rw [hg]; exact M.zero_mem)
  have hinf : M ⊓ span K (Set.range b) = ⊥ := by
    rw [eq_bot_iff]
    rintro x ⟨hxM, hxS⟩
    obtain ⟨β, rfl⟩ := (Submodule.mem_span_range_iff_exists_fun K).1 hxS
    have h0 := hb β hxM
    simp [h0]
  have := Submodule.finrank_sup_add_finrank_inf_eq M (span K (Set.range b))
  rw [hinf, finrank_bot, finrank_span_eq_card hli] at this
  omega

/-- Core stay-count step (FANOUT F2 / RANKSTEINER R0(c) proof):
for `A, T ≤ S` with `T ⊆ ker ρ`, `dim ρ(A) + dim T ≤ dim S`. -/
theorem finrank_map_add_le [FiniteDimensional K V] (ρ : V →ₗ[K] W) (S A T : Submodule K V)
    (hA : A ≤ S) (hT : T ≤ S) (hTk : T ≤ LinearMap.ker ρ) :
    finrank K (A.map ρ) + finrank K T ≤ finrank K S := by
  have h1 := LinearMap.finrank_range_add_finrank_ker (ρ.domRestrict S)
  rw [LinearMap.range_domRestrict] at h1
  have h2 : finrank K (A.map ρ) ≤ finrank K (S.map ρ) :=
    Submodule.finrank_mono (Submodule.map_mono hA)
  have h3 : finrank K T ≤ finrank K (LinearMap.ker (ρ.domRestrict S)) := by
    rw [← (Submodule.comapSubtypeEquivOfLe hT).finrank_eq]
    apply Submodule.finrank_mono
    intro x hx
    simp only [Submodule.mem_comap, Submodule.subtype_apply] at hx
    simpa [LinearMap.mem_ker] using hTk hx
  omega

/-- Tokens of distinct registers are independent: `dim span{e_i : i ∈ T} = |T|`. -/
theorem finrank_tokens {ι : Type*} [Fintype ι] [DecidableEq ι] (T : Finset ι) :
    finrank K (span K (Set.range fun i : T => (Pi.single (i : ι) (1 : K) : ι → K))) = T.card := by
  have hli : LinearIndependent K (fun i : T => (Pi.single (i : ι) (1 : K) : ι → K)) := by
    have := (Pi.basisFun K ι).linearIndependent.comp (Subtype.val : T → ι) Subtype.val_injective
    simpa [Function.comp_def] using this
  rw [finrank_span_eq_card hli, Fintype.card_coe]

end Core

/-! ## 2. The stay floor at one chart (F2, R0(c), R1, R3-count)

Registers `ι`, rows in `ι → K`, `ρ : (ι → K) → W` (deletes helper coordinates).
At a chart c: `S` = span of every row ever at c; `Tok` = registers whose own token is held at c
and killed by ρ (the he helper enders, class N, and the hb helper births).
`hent`: dim S ≤ #entries = hd + he + ka + oa + hb + kb  (forward span law + one entry per register,
ExportLaw.forward_count / stay_count / hOnce). -/
section Stay
variable {K W U : Type*} [Field K] [AddCommGroup W] [Module K W] [AddCommGroup U] [Module K U]
  {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Generic stay floor: any set `X` of rows held at c has `rank ρ(X) ≤ hd + ka + oa + kb`. -/
theorem stay_floor (ρ : (ι → K) →ₗ[K] W) (S : Submodule K (ι → K)) (X : Set (ι → K))
    (Tok : Finset ι) (hd he hb ka oa kb : ℕ)
    (hX : X ⊆ S) (hTokS : ∀ i ∈ Tok, (Pi.single i 1 : ι → K) ∈ S)
    (hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0) (hTokc : Tok.card = he + hb)
    (hent : finrank K S ≤ hd + he + ka + oa + hb + kb) :
    finrank K (span K (ρ '' X)) ≤ hd + ka + oa + kb := by
  set T := span K (Set.range fun i : Tok => (Pi.single (i : ι) (1 : K) : ι → K))
  have hT : T ≤ S := by
    rw [span_le]; rintro _ ⟨i, rfl⟩; exact hTokS i i.2
  have hTk : T ≤ LinearMap.ker ρ := by
    rw [span_le]; rintro _ ⟨i, rfl⟩; exact hTokρ i i.2
  have hA : span K X ≤ S := by rw [span_le]; exact hX
  have := finrank_map_add_le ρ S (span K X) T hA hT hTk
  rw [Submodule.map_span, finrank_tokens] at this
  omega

/-- **R1 (local rank law)**: hd(c) ≥ rank(ρK_c + ρR(c)) − ka − oa − kb. -/
theorem R1_local_rank (ρ : (ι → K) →ₗ[K] W) (S : Submodule K (ι → K)) (Kc R : Set (ι → K))
    (Tok : Finset ι) (hd he hb ka oa kb : ℕ)
    (hK : Kc ⊆ S) (hR : R ⊆ S) (hTokS : ∀ i ∈ Tok, (Pi.single i 1 : ι → K) ∈ S)
    (hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0) (hTokc : Tok.card = he + hb)
    (hent : finrank K S ≤ hd + he + ka + oa + hb + kb) :
    (finrank K (span K (ρ '' Kc) ⊔ span K (ρ '' R) : Submodule K W) : ℤ) - ka - oa - kb ≤ hd := by
  have := stay_floor ρ S (Kc ∪ R) Tok hd he hb ka oa kb (Set.union_subset hK hR) hTokS hTokρ
    hTokc hent
  rw [Set.image_union, span_union] at this
  omega

/-- **F2 / R0(c) (ρ-refined count)**: hd(c) ≥ a_H(c) − slr(c), with
a_H = dim(ρK + ρHelpArr) − dim ρK and slr = ka + oa + kb − rank ρK. -/
theorem F2_count (ρ : (ι → K) →ₗ[K] W) (S : Submodule K (ι → K)) (Kc H : Set (ι → K))
    (Tok : Finset ι) (hd he hb ka oa kb : ℕ)
    (hK : Kc ⊆ S) (hH : H ⊆ S) (hTokS : ∀ i ∈ Tok, (Pi.single i 1 : ι → K) ∈ S)
    (hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0) (hTokc : Tok.card = he + hb)
    (hent : finrank K S ≤ hd + he + ka + oa + hb + kb) :
    ((finrank K (span K (ρ '' Kc) ⊔ span K (ρ '' H) : Submodule K W) : ℤ)
        - finrank K (span K (ρ '' Kc)))
      - ((ka + oa + kb : ℕ) - (finrank K (span K (ρ '' Kc)) : ℤ)) ≤ hd := by
  have := R1_local_rank ρ S Kc H Tok hd he hb ka oa kb hK hH hTokS hTokρ hTokc hent
  push_cast; omega

/-- **Hop count / R3 count**: helper arrivals `b` held at c whose ρ-rows are independent
modulo ρK_c + ρR(c) give hd(c) ≥ rank(ρK_c + ρR(c)) − ka − oa − kb + m.
With `R = ∅` this is F3's `#hops(c) ≤ hd(c) + slr(c)`; with type-A hops it is R3's
`hd(c) ≥ needR(c) + #A-hops(c)`. -/
theorem hop_count [FiniteDimensional K W] {m : Type*} [Fintype m]
    (ρ : (ι → K) →ₗ[K] W) (S : Submodule K (ι → K)) (Kc R : Set (ι → K)) (b : m → (ι → K))
    (Tok : Finset ι) (hd he hb ka oa kb : ℕ)
    (hK : Kc ⊆ S) (hR : R ⊆ S) (hbS : ∀ j, b j ∈ S)
    (hind : IndepMod (span K (ρ '' Kc) ⊔ span K (ρ '' R)) (fun j => ρ (b j)))
    (hTokS : ∀ i ∈ Tok, (Pi.single i 1 : ι → K) ∈ S)
    (hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0) (hTokc : Tok.card = he + hb)
    (hent : finrank K S ≤ hd + he + ka + oa + hb + kb) :
    (finrank K (span K (ρ '' Kc) ⊔ span K (ρ '' R) : Submodule K W) : ℤ) - ka - oa - kb
      + Fintype.card m ≤ hd := by
  have hX : Kc ∪ R ∪ Set.range b ⊆ S := by
    refine Set.union_subset (Set.union_subset hK hR) ?_
    rintro _ ⟨j, rfl⟩; exact hbS j
  have h := stay_floor ρ S _ Tok hd he hb ka oa kb hX hTokS hTokρ hTokc hent
  rw [Set.image_union, Set.image_union, span_union, span_union, ← Set.range_comp] at h
  have := finrank_sup_of_indepMod _ _ hind
  simp only [Function.comp_def] at h
  omega

/-- F3 in FANOUT's π-form: HB_c is a basis of (KA_c + π HelpArr_c)/KA_c with π = π' ∘ ρ.
If π'(ρK_c) ⊆ KA_c, π-independence mod KA_c implies ρ-independence mod ρK_c (the F2 proof's
"apply π" step), so `hop_count` applies. -/
theorem indepMod_of_proj {m : Type*} [Fintype m] (π' : W →ₗ[K] U) (M : Submodule K W)
    (KA : Submodule K U) (hMK : M.map π' ≤ KA) (b : m → W)
    (hb : IndepMod KA (fun j => π' (b j))) : IndepMod M b := by
  intro β hβ
  apply hb β
  have : π' (∑ i, β i • b i) ∈ KA := hMK ⟨_, hβ, rfl⟩
  simpa [map_sum, map_smul] using this

end Stay

/-! ## 3. F1 descent lemma, R0(b), F4 / R2 single-source commodities

Charts `C` with a well-founded strict order (chart containment; helper moves strictly ascend).
`P c` = π(S_c) (or ρ(S_c) for R2). `KA c` = the fixed kept part. `HB c` = a fixed set of helper
arrivals at c (a basis of the helper part); `tail b` = the chart b departed from and `vec b` its
(projected) row, which was held at `tail b`. -/
section Descent
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
  {C : Type*} [PartialOrder C] [WellFoundedLT C] {Hop : Type*}
  (KA P : C → Submodule K V) (HB : C → Set Hop) (tail : Hop → C) (vec : Hop → V)

/-- One descent step c → c' : an element of HB_{c'} with tail c that φ sees. -/
def Step (φ : V →ₗ[K] K) (c c' : C) : Prop := ∃ b ∈ HB c', tail b = c ∧ φ (vec b) ≠ 0

/-- s is a φ-source: φ(KA_s) ≠ 0. -/
def Source (φ : V →ₗ[K] K) (s : C) : Prop := ∃ w ∈ KA s, φ w ≠ 0

variable {KA P HB tail vec}

lemma exists_hop_of_sup {φ : V →ₗ[K] K} {A : Submodule K V} {X : Set V} {v : V}
    (hA : ∀ w ∈ A, φ w = 0) (hv : v ∈ A ⊔ span K X) (hφ : φ v ≠ 0) : ∃ x ∈ X, φ x ≠ 0 := by
  by_contra hcon
  push Not at hcon
  have : A ⊔ span K X ≤ LinearMap.ker φ :=
    sup_le (fun w hw => hA w hw) (span_le.2 fun x hx => hcon x hx)
  exact hφ (this hv)

lemma step_lt (hvec : ∀ c, ∀ b ∈ HB c, vec b ∈ P (tail b) ∧ tail b < c)
    {φ : V →ₗ[K] K} {c c' : C} (h : Step HB tail vec φ c c') : c < c' := by
  obtain ⟨b, hb, rfl, -⟩ := h; exact (hvec _ b hb).2

lemma rtg_le (hvec : ∀ c, ∀ b ∈ HB c, vec b ∈ P (tail b) ∧ tail b < c)
    {φ : V →ₗ[K] K} {c c' : C} (h : Relation.ReflTransGen (Step HB tail vec φ) c c') : c ≤ c' := by
  induction h with
  | refl => exact le_rfl
  | tail _ hs ih => exact ih.trans (step_lt hvec hs).le

/-- **F1 DESCENT LEMMA.** Hypotheses: `hP` P(c) ⊆ KA_c + span vec(HB_c) (forward span law plus the
choice of HB_c); `hvec` every b ∈ HB_c was held at its tail, which is strictly below c.
If φ kills KA_t and sees some v ∈ P(t), there is a φ-source s and a first hop b ∈ HB_{c₁} with
tail s, φ(vec b) ≠ 0, followed by a chain of φ-visible hops c₁ → … → t; hence s < c₁ ≤ t. -/
theorem F1_descent (hP : ∀ c, P c ≤ KA c ⊔ span K (vec '' HB c))
    (hvec : ∀ c, ∀ b ∈ HB c, vec b ∈ P (tail b) ∧ tail b < c)
    (φ : V →ₗ[K] K) (t : C) (hKt : ∀ w ∈ KA t, φ w = 0) (v : V) (hv : v ∈ P t) (hφv : φ v ≠ 0) :
    ∃ s c₁, ∃ b ∈ HB c₁, Source KA φ s ∧ tail b = s ∧ φ (vec b) ≠ 0 ∧ s < c₁ ∧ c₁ ≤ t ∧
      Relation.ReflTransGen (Step HB tail vec φ) c₁ t := by
  -- Good c: a source and a first hop ending in a chain to c.
  have key : ∀ c, ∀ v ∈ P c, φ v ≠ 0 → Source KA φ c ∨
      ∃ s c₁, ∃ b ∈ HB c₁, Source KA φ s ∧ tail b = s ∧ φ (vec b) ≠ 0 ∧
        Relation.ReflTransGen (Step HB tail vec φ) c₁ c := by
    intro c
    induction c using WellFoundedLT.induction with
    | _ c ih =>
      intro v hv hφv
      by_cases hsrc : Source KA φ c
      · exact Or.inl hsrc
      · right
        have hA : ∀ w ∈ KA c, φ w = 0 := by
          intro w hw; by_contra h; exact hsrc ⟨w, hw, h⟩
        obtain ⟨x, ⟨b, hb, rfl⟩, hx⟩ := exists_hop_of_sup hA (hP c hv) hφv
        obtain ⟨hbP, hlt⟩ := hvec c b hb
        rcases ih (tail b) hlt (vec b) hbP hx with hs | ⟨s, c₁, b₁, hb₁, hs, ht, hφ, hr⟩
        · exact ⟨tail b, c, b, hb, hs, rfl, hx, Relation.ReflTransGen.refl⟩
        · exact ⟨s, c₁, b₁, hb₁, hs, ht, hφ, hr.tail ⟨b, hb, rfl, hx⟩⟩
  rcases key t v hv hφv with hs | ⟨s, c₁, b, hb, hs, ht, hφ, hr⟩
  · obtain ⟨w, hw, hne⟩ := hs; exact absurd (hKt w hw) hne
  · refine ⟨s, c₁, b, hb, hs, ht, hφ, ?_, rtg_le hvec hr, hr⟩
    rw [← ht]; exact (hvec c₁ b hb).2

/-- **R0(b)**: P(c) ⊆ Σ_{c' ≤ c} KA_{c'} (induction on the chart order). -/
theorem R0b (hP : ∀ c, P c ≤ KA c ⊔ span K (vec '' HB c))
    (hvec : ∀ c, ∀ b ∈ HB c, vec b ∈ P (tail b) ∧ tail b < c) (c : C) :
    P c ≤ ⨆ (c' : C) (_ : c' ≤ c), KA c' := by
  induction c using WellFoundedLT.induction with
  | _ c ih =>
    refine (hP c).trans (sup_le ?_ ?_)
    · exact le_iSup₂_of_le c le_rfl le_rfl
    · rw [span_le]
      rintro _ ⟨b, hb, rfl⟩
      obtain ⟨hbP, hlt⟩ := hvec c b hb
      have h1 := ih (tail b) hlt hbP
      refine (iSup₂_le fun c' hc' => le_iSup₂_of_le (f := fun c' (_ : c' ≤ c) => KA c') c'
        (hc'.trans hlt.le) le_rfl) h1

/-- Separating functional (FANOUT F4 / RANKSTEINER R2 existence step): if n ∉ W there is φ with
φ(W) = 0 and φ(n) ≠ 0. -/
theorem exists_sep [FiniteDimensional K V] (W : Submodule K V) (n : V) (hn : n ∉ W) :
    ∃ φ : V →ₗ[K] K, φ n ≠ 0 ∧ ∀ w ∈ W, φ w = 0 := by
  obtain ⟨f, hf, hW⟩ := Submodule.exists_dual_map_eq_bot_of_notMem hn inferInstance
  refine ⟨f, hf, fun w hw => ?_⟩
  have : f w ∈ W.map f := ⟨w, hw, rfl⟩
  rw [hW] at this; simpa using this

/-- **F4 / R2 single-source commodity.** If φ kills KA_t and every KA_{s'} with s' < t, s' ≠ s,
and sees some v ∈ P(t), then the commodity leaves s by its own first hop: some b ∈ HB_{c₁} with
tail s, φ(vec b) ≠ 0, s < c₁ ≤ t. -/
theorem F4_single_source (hP : ∀ c, P c ≤ KA c ⊔ span K (vec '' HB c))
    (hvec : ∀ c, ∀ b ∈ HB c, vec b ∈ P (tail b) ∧ tail b < c)
    (φ : V →ₗ[K] K) (s t : C) (hKt : ∀ w ∈ KA t, φ w = 0)
    (hW : ∀ s', s' < t → s' ≠ s → ∀ w ∈ KA s', φ w = 0)
    (v : V) (hv : v ∈ P t) (hφv : φ v ≠ 0) :
    ∃ c₁, ∃ b ∈ HB c₁, tail b = s ∧ φ (vec b) ≠ 0 ∧ s < c₁ ∧ c₁ ≤ t := by
  obtain ⟨s₀, c₁, b, hb, ⟨w, hw, hne⟩, ht, hφ, hlt, hle, -⟩ :=
    F1_descent hP hvec φ t hKt v hv hφv
  have : s₀ = s := by
    by_contra h; exact hne (hW s₀ (lt_of_lt_of_le hlt hle) h w hw)
  subst this
  exact ⟨c₁, b, hb, ht, hφ, hlt, hle⟩

end Descent

/-! ## 4. R3 triangular independence -/
section R3
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
  {C : Type*} [PartialOrder C] {m : Type*} [Fintype m] [DecidableEq m]

/-- Abstract triangular independence: ψ_i(b_j) ≠ 0 for i ≠ j only if s_i < s_j, ψ_j(b_j) ≠ 0,
every ψ_i kills M. Then the b_j are independent modulo M. -/
theorem tri_indepMod (s : m → C) (b : m → V) (ψ : m → V →ₗ[K] K) (M : Submodule K V)
    (hM : ∀ i, ∀ w ∈ M, ψ i w = 0) (hdiag : ∀ j, ψ j (b j) ≠ 0)
    (htri : ∀ i j, i ≠ j → ψ i (b j) ≠ 0 → s i < s j) : IndepMod M b := by
  classical
  intro β hβ
  by_contra hne
  push Not at hne
  set J := Finset.univ.filter fun j => β j ≠ 0
  have hJ : (J.image s).Nonempty := by
    obtain ⟨j, hj⟩ := hne; exact ⟨s j, Finset.mem_image.2 ⟨j, by simp [J, hj], rfl⟩⟩
  obtain ⟨x, hx⟩ := Finset.exists_maximal hJ
  obtain ⟨j0, hj0J, rfl⟩ := Finset.mem_image.1 hx.1
  have hj0 : β j0 ≠ 0 := by simpa [J] using hj0J
  have h0 := hM j0 _ hβ
  rw [map_sum, Finset.sum_eq_single j0] at h0
  · simp only [map_smul, smul_eq_mul] at h0
    exact mul_ne_zero hj0 (hdiag j0) h0
  · intro j _ hjj
    simp only [map_smul, smul_eq_mul]
    by_cases hbj : β j = 0
    · simp [hbj]
    · by_contra hprod
      have hψ : ψ j0 (b j) ≠ 0 := right_ne_zero_of_mul hprod
      have hlt := htri j0 j (Ne.symm hjj) hψ
      have hjmem : s j ∈ J.image s := Finset.mem_image.2 ⟨j, by simp [J, hbj], rfl⟩
      exact hlt.not_ge (hx.2 hjmem hlt.le)
  · intro h; exact absurd (Finset.mem_univ _) h

/-- **R3**: first hops b_j into c from pairwise distinct sources s_j, each with an R2 commodity
(t_j, s_j, ψ_j): ψ_j kills Kρ_{c'} for every c' ≤ t_j, c' ≠ s_j; s_j < c ≤ t_j; ψ_j(b_j) ≠ 0;
b_j ∈ Σ_{c' ≤ s_j} Kρ_{c'} (R0(b)). Then the b_j are independent mod Kρ_c, and mod Kρ_c + ρR(c)
if every ψ_j kills ρR(c) ("type A at c"). -/
theorem R3_indep (Kρ : C → Submodule K V) (R : Submodule K V) (c : C) (s t : m → C)
    (hs : Function.Injective s) (b : m → V) (ψ : m → V →ₗ[K] K)
    (hψK : ∀ i c', c' ≤ t i → c' ≠ s i → ∀ w ∈ Kρ c', ψ i w = 0)
    (hψR : ∀ i, ∀ w ∈ R, ψ i w = 0)
    (hsc : ∀ j, s j < c) (hct : ∀ j, c ≤ t j) (hdiag : ∀ j, ψ j (b j) ≠ 0)
    (hb : ∀ j, b j ∈ ⨆ (c' : C) (_ : c' ≤ s j), Kρ c') :
    IndepMod (Kρ c ⊔ R) b := by
  apply tri_indepMod s b ψ
  · intro i w hw
    obtain ⟨y, hy, z, hz, rfl⟩ := Submodule.mem_sup.1 hw
    rw [map_add, hψK i c (hct i) (hsc i).ne' y hy, hψR i z hz, add_zero]
  · exact hdiag
  · intro i j hij hψ
    by_contra hlt
    apply hψ
    have hle : (⨆ (c' : C) (_ : c' ≤ s j), Kρ c') ≤ LinearMap.ker (ψ i) := by
      refine iSup₂_le fun c' hc' w hw => ?_
      have hne : c' ≠ s i := by
        rintro rfl
        rcases hc'.lt_or_eq with h | h
        · exact hlt h
        · exact hij (hs h)
      exact hψK i c' ((hc'.trans (hsc j).le).trans (hct i)) hne w hw
    exact hle (hb j)

end R3

/-! ## 5. LP weak duality (FANOUT F3 / RANKSTEINER R4 certificate)

Primal: min cᵀx s.t. A x ≥ b, x ≥ 0. A dual vector y ≥ 0 with yᵀA ≤ c bounds every feasible
objective from below. The LP data and the dual vector are checked in exact Fractions by
lp2.py / rslp.py; here only the generic certificate lemma. -/
section LP
variable {𝕜 : Type*} [Field 𝕜] [LinearOrder 𝕜] [IsStrictOrderedRing 𝕜]
  {r n : Type*} [Fintype r] [Fintype n]

theorem weak_duality (A : r → n → 𝕜) (b : r → 𝕜) (c : n → 𝕜) (x : n → 𝕜) (y : r → 𝕜)
    (hx : ∀ j, 0 ≤ x j) (hAx : ∀ i, b i ≤ ∑ j, A i j * x j)
    (hy : ∀ i, 0 ≤ y i) (hyA : ∀ j, ∑ i, y i * A i j ≤ c j) :
    ∑ i, y i * b i ≤ ∑ j, c j * x j := by
  calc ∑ i, y i * b i ≤ ∑ i, y i * ∑ j, A i j * x j :=
        Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hAx i) (hy i)
    _ = ∑ j, (∑ i, y i * A i j) * x j := by
        simp only [Finset.mul_sum, Finset.sum_mul]
        rw [Finset.sum_comm]; congr 1; ext j; congr 1; ext i; ring
    _ ≤ ∑ j, c j * x j := Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_right (hyA j) (hx j)

/-- The floor as used: helper cost ≥ κ·Σ_c hd(c), the native gives a feasible x of objective
≤ Σ_c hd(c), and y is a dual certificate. Then cost ≥ κ · bᵀy. -/
theorem floor_of_certificate (A : r → n → 𝕜) (b : r → 𝕜) (c : n → 𝕜) (x : n → 𝕜) (y : r → 𝕜)
    (hx : ∀ j, 0 ≤ x j) (hAx : ∀ i, b i ≤ ∑ j, A i j * x j)
    (hy : ∀ i, 0 ≤ y i) (hyA : ∀ j, ∑ i, y i * A i j ≤ c j)
    (κ HD cost : 𝕜) (hκ : 0 ≤ κ) (hobj : ∑ j, c j * x j ≤ HD) (hcost : κ * HD ≤ cost) :
    κ * ∑ i, y i * b i ≤ cost :=
  (mul_le_mul_of_nonneg_left ((weak_duality A b c x y hx hAx hy hyA).trans hobj) hκ).trans hcost

end LP

end Floor

#print axioms Floor.F1_descent
#print axioms Floor.R0b
#print axioms Floor.F4_single_source
#print axioms Floor.F2_count
#print axioms Floor.R1_local_rank
#print axioms Floor.hop_count
#print axioms Floor.indepMod_of_proj
#print axioms Floor.R3_indep
#print axioms Floor.weak_duality
#print axioms Floor.floor_of_certificate
#print axioms Floor.exists_sep

/-
WordModelY (lane WM-Y, Nov 18): Theorem Y (port lemma / slack-rank count, R3 §2) on the shared word model.
  `theoremY : Word cl s → CSFinal s → CSEntry s → BornUnique s → SlackRank (pub cl) s → 104 ≤ nStops s + nOwnNonV s`.
Premises used (all in Defs): public strict ascent (movePub, VERIFIER l.51, enters via CSEntry/SlackRank only
through the model), caller data (odd labels, injective, 104 ports), Word endpoint fields, and the target
Jacobian forms `tgt` (a finite check on the #7113 contract).  Kernel only: no sorry, no native_decide.
-/
import Nov15.WordModelDefs
import Nov15.WordModelYCard
import Mathlib.Tactic.IntervalCases
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.StdBasis

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique Module

/-! ## Finite facts about labels and charts -/

theorem wt_zero : wt 0 = 0 := by decide

theorem dot_self_odd {q : ℕ} (h : wt q % 2 = 1) : dot q q = 1 := by
  simp [dot, h]

set_option maxRecDepth 10000 in
theorem Hq_card : ∀ q < 512, q ≠ 0 → (Hq q).card = 256 := by
  intro q hq hne
  obtain ⟨k, i, hk, hi, rfl⟩ : ∃ k i, k < 16 ∧ i < 32 ∧ q = 32 * k + i :=
    ⟨q / 32, q % 32, by omega, Nat.mod_lt _ (by norm_num), by omega⟩
  interval_cases k <;> first | exact Hq_card_c0 i hi hne | exact Hq_card_c1 i hi hne | exact Hq_card_c2 i hi hne | exact Hq_card_c3 i hi hne | exact Hq_card_c4 i hi hne | exact Hq_card_c5 i hi hne | exact Hq_card_c6 i hi hne | exact Hq_card_c7 i hi hne | exact Hq_card_c8 i hi hne | exact Hq_card_c9 i hi hne | exact Hq_card_c10 i hi hne | exact Hq_card_c11 i hi hne | exact Hq_card_c12 i hi hne | exact Hq_card_c13 i hi hne | exact Hq_card_c14 i hi hne | exact Hq_card_c15 i hi hne


theorem recon : ∀ q < 512, q = dot 1 q + 2 * dot 2 q + 4 * dot 4 q + 8 * dot 8 q + 16 * dot 16 q
    + 32 * dot 32 q + 64 * dot 64 q + 128 * dot 128 q + 256 * dot 256 q := by
  decide +kernel

theorem Hq_inj {q q' : ℕ} (hq : q < 512) (hq' : q' < 512) (h : Hq q = Hq q') : q = q' := by
  have key : ∀ v < 512, dot v q = dot v q' := by
    intro v hv
    have := Finset.ext_iff.mp h v
    simp only [Hq, mem_filter, mem_range, hv, true_and] at this
    have h1 : dot v q < 2 := Nat.mod_lt _ (by norm_num)
    have h2 : dot v q' < 2 := Nat.mod_lt _ (by norm_num)
    omega
  rw [recon q hq, recon q' hq', key 1 (by norm_num), key 2 (by norm_num), key 4 (by norm_num),
    key 8 (by norm_num), key 16 (by norm_num), key 32 (by norm_num), key 64 (by norm_num),
    key 128 (by norm_num), key 256 (by norm_num)]

theorem Hq_sub_Vc (q : ℕ) : Hq q ⊆ Vc := by
  intro v hv; simp only [Hq, mem_filter] at hv; exact hv.1

theorem line_card_le (q : ℕ) : (line q).card ≤ 2 := by
  unfold line; exact Finset.card_le_two

/-! ## Caller / target facts -/

section Caller
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

theorem lab_ne_zero (cl : Caller Pt) (p : Pt) : cl.lab p ≠ 0 := by
  intro h; have := cl.lab_odd p; rw [h, wt_zero] at this; simp at this

theorem Hq_card_lab (cl : Caller Pt) (p : Pt) : (Hq (cl.lab p)).card = 256 :=
  Hq_card _ (cl.lab_lt p) (lab_ne_zero cl p)

theorem lab_not_mem (cl : Caller Pt) (p : Pt) : cl.lab p ∉ Hq (cl.lab p) := by
  intro h
  simp only [Hq, mem_filter] at h
  have := dot_self_odd (cl.lab_odd p)
  omega

theorem Hq_lab_inj (cl : Caller Pt) {p p' : Pt} (h : Hq (cl.lab p) = Hq (cl.lab p')) : p = p' :=
  cl.lab_inj (Hq_inj (cl.lab_lt p) (cl.lab_lt p') h)

theorem Hq_ne_Vc (cl : Caller Pt) (p : Pt) : Hq (cl.lab p) ≠ Vc := by
  intro h
  have : cl.lab p ∈ Vc := by simp [Vc, cl.lab_lt p]
  rw [← h] at this
  exact lab_not_mem cl p this

theorem tgt_x_coord (cl : Caller Pt) (r : Reg Pt Hl Ow) (p' : Pt)
    (h : tgt cl r (.x p') ≠ 0) : r = .x p' ∨ r = .y p' := by
  by_contra hc
  rw [not_or] at hc
  apply h
  cases r with
  | x p =>
    have h1 : p ≠ p' := fun e => hc.1 (by rw [e])
    by_cases hD : cl.isD p = true <;> simp [tgt, e, hD, Pi.single_apply, h1, h1.symm]
  | y p =>
    have h1 : p ≠ p' := fun e => hc.2 (by rw [e])
    by_cases hD : cl.isD p = true <;> simp [tgt, e, hD, Pi.single_apply, h1, h1.symm]
  | x2 p => simp [tgt, e, Pi.single_apply]
  | y2 p => simp [tgt, e, Pi.single_apply]
  | h i => simp [tgt, e, Pi.single_apply]
  | o i => simp [tgt]

theorem tgt_y_x (cl : Caller Pt) (p : Pt) : tgt cl (Reg.y p : Reg Pt Hl Ow) (.x p) ≠ 0 := by
  by_cases hD : cl.isD p = true <;> simp [tgt, e, Pi.single_apply, hD]

end Caller

/-! ## Generator vanishing: S_C ≤ ker Φ_Z -/

section Main
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]
  {cl : Caller Pt} {s : St (Reg Pt Hl Ow)}

/-- coordinates (x_p)_{p ∈ Z}. -/
noncomputable def PhiZ (Z : Finset Pt) : (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] (Z → ℚ) :=
  LinearMap.funLeft ℚ ℚ (fun p' : Z => Reg.x p'.1)

theorem PhiZ_apply (Z : Finset Pt) (v : Reg Pt Hl Ow → ℚ) (p' : Z) : PhiZ Z v p' = v (.x p'.1) := rfl

theorem S_le_ker (W : Word cl s) (hBU : BornUnique s) (C : Ch) (hC : C ≠ Vc) (Z : Finset Pt)
    (hb : ∀ p' ∈ Z, Hq (cl.lab p') ≠ C) (hc : ∀ p' ∈ Z, line (cl.lab p') ≠ C) :
    Submodule.span ℚ (Fstay (pub cl) s C ∪ EBL s C) ≤ LinearMap.ker (PhiZ (Hl := Hl) (Ow := Ow) Z) := by
  rw [Submodule.span_le]
  intro v hv
  rw [SetLike.mem_coe, LinearMap.mem_ker]
  rcases hv with ⟨r, hpub, hloc, rfl⟩ | ⟨r, ⟨hrB, hrloc⟩, rfl⟩
  · funext p'
    rw [PhiZ_apply, W.final_row r hpub]
    by_contra hne
    rcases tgt_x_coord cl r p'.1 hne with rfl | rfl
    · rw [W.x_final] at hloc
      exact hC (Loc.sit.inj hloc).symm
    · rw [W.y_final] at hloc
      exact hb p'.1 p'.2 (Loc.sit.inj hloc)
  · funext p'
    show (Pi.single r (1:ℚ) : Reg Pt Hl Ow → ℚ) (Reg.x p'.1) = (0 : Z → ℚ) p'
    rw [Pi.single_apply]
    by_cases h : Reg.x p'.1 = r
    · exfalso
      subst h
      have h1 := W.x_birth p'.1
      have := hBU _ _ _ hrB h1
      exact hc p'.1 p'.2 this.symm
    · simp [h]

/-! ## Port lemma: a slack-free H_p is fed from a smaller chart -/

theorem port_fed (W : Word cl s) (hCSF : CSFinal s) (hCSE : CSEntry s) (hBU : BornUnique s)
    (K : Ch → Submodule ℚ (Reg Pt Hl Ow → ℚ))
    (hK : ∀ c, c ≠ Vc → finrank ℚ (K c) ≤ sigma s c ∧
      I s c ≤ Submodule.span ℚ (Fstay (pub cl) s c ∪ EBL s c) ⊔ K c)
    (p : Pt) (hσ : sigma s (Hq (cl.lab p)) = 0) :
    ∃ C ρ, C < Hq (cl.lab p) ∧ ρ ∈ I s C ∧ ρ (.x p) ≠ 0 ∧ ∀ p' ≠ p, ρ (.x p') = 0 := by
  classical
  set H := Hq (cl.lab p) with hH
  have hHV : H ≠ Vc := Hq_ne_Vc cl p
  obtain ⟨hKr, hKI⟩ := hK H hHV
  have hK0 : K H = ⊥ := by
    have : finrank ℚ (K H) = 0 := by omega
    exact Submodule.finrank_eq_zero.mp this
  have hσ' : ∀ m ∈ s.olog, m.2.1 ≠ H := by
    intro m hm hmH
    have h0 : s.olog.countP (fun m => decide (m.2.1 = H)) = 0 := by
      unfold sigma at hσ; omega
    rw [List.countP_eq_zero] at h0
    exact h0 m hm (by simpa using hmH)
  -- an entry row with nonzero x_p coordinate
  have hex : ∃ r ∈ s.A H, s.eRow r H (.x p) ≠ 0 := by
    by_contra hcon
    push Not at hcon
    have hle : I s H ≤ LinearMap.ker (LinearMap.proj (R := ℚ) (φ := fun _ : Reg Pt Hl Ow => ℚ) (.x p)) := by
      unfold I
      rw [Submodule.span_le]
      intro v hv
      rw [SetLike.mem_coe, LinearMap.mem_ker, LinearMap.proj_apply]
      rcases hv with (⟨r, hrB, rfl⟩ | ⟨r, hrA, rfl⟩) | ⟨a, ha⟩
      · show (Pi.single r (1:ℚ) : Reg Pt Hl Ow → ℚ) (Reg.x p) = 0
        rw [Pi.single_apply]
        by_cases h : Reg.x p = r
        · exfalso
          subst h
          have := hBU _ _ _ (Finset.mem_coe.mp hrB) (W.x_birth p)
          have hc1 : H.card ≤ 2 := by rw [this]; exact line_card_le _
          have h2 : H.card = 256 := Hq_card_lab cl p
          omega
        · simp [h]
      · exact hcon r (Finset.mem_coe.mp hrA)
      · exact absurd rfl (hσ' _ ha)
    have hyI := hCSF (.y p) H (W.y_final p)
    have := hle hyI
    rw [LinearMap.mem_ker, LinearMap.proj_apply, W.final_row _ rfl] at this
    exact tgt_y_x cl p this
  obtain ⟨r, hrA, hρ⟩ := hex
  have hρI : s.eRow r H ∈ I s H := Submodule.subset_span (Or.inl (Or.inr ⟨r, hrA, rfl⟩))
  have hρS : s.eRow r H ∈ Submodule.span ℚ (Fstay (pub cl) s H ∪ EBL s H) := by
    have := hKI hρI
    rw [hK0, sup_bot_eq] at this
    exact this
  have hker := S_le_ker W hBU H hHV (Finset.univ.erase p)
    (by
      intro p' hp' h
      exact (Finset.ne_of_mem_erase hp') (Hq_lab_inj cl h))
    (by
      intro p' _ h
      have h1 := line_card_le (cl.lab p')
      have h2 : H.card = 256 := Hq_card_lab cl p
      rw [h] at h1
      omega) hρS
  rw [LinearMap.mem_ker] at hker
  obtain ⟨C, hC, hρC⟩ := hCSE r H hrA
  refine ⟨C, s.eRow r H, hC, hρC, hρ, ?_⟩
  intro p' hp'
  have := congrFun hker ⟨p', Finset.mem_erase.mpr ⟨hp', Finset.mem_univ _⟩⟩
  simpa [PhiZ_apply] using this

/-! ## Rank bound for fed ports -/

theorem fed_card_le (W : Word cl s) (hBU : BornUnique s) (C : Ch) (Kc : Submodule ℚ (Reg Pt Hl Ow → ℚ))
    (hKr : finrank ℚ Kc ≤ sigma s C)
    (hKI : I s C ≤ Submodule.span ℚ (Fstay (pub cl) s C ∪ EBL s C) ⊔ Kc)
    (hCV : C ≠ Vc) (F : Finset Pt)
    (hF : ∀ p ∈ F, ∃ ρ, C < Hq (cl.lab p) ∧ ρ ∈ I s C ∧ ρ (.x p) ≠ 0 ∧ ∀ p' ≠ p, ρ (.x p') = 0) :
    F.card ≤ sigma s C := by
  have hker := S_le_ker W hBU C hCV F
    (by
      intro p' hp' h
      obtain ⟨ρ, hlt, -⟩ := hF p' hp'
      rw [h] at hlt; exact lt_irrefl _ hlt)
    (by
      intro p' hp' h
      obtain ⟨ρ, hlt, -⟩ := hF p' hp'
      have hm : cl.lab p' ∈ line (cl.lab p') := by simp [line]
      rw [h] at hm
      exact lab_not_mem cl p' (hlt.1 hm))
  have htop : (⊤ : Submodule ℚ (F → ℚ)) ≤ Submodule.map (PhiZ (Hl := Hl) (Ow := Ow) F) Kc := by
    rw [← (Pi.basisFun ℚ F).span_eq, Submodule.span_le]
    rintro _ ⟨p, rfl⟩
    rw [Pi.basisFun_apply]
    obtain ⟨ρ, -, hρI, hρx, hρ0⟩ := hF p.1 p.2
    obtain ⟨sv, hsv, k, hk, hsum⟩ := Submodule.mem_sup.mp (hKI hρI)
    have hPs : PhiZ (Hl := Hl) (Ow := Ow) F sv = 0 := hker hsv
    have hPρ : PhiZ (Hl := Hl) (Ow := Ow) F ρ = ρ (.x p.1) • (Pi.single p (1 : ℚ)) := by
      funext p''
      rw [PhiZ_apply, Pi.smul_apply, Pi.single_apply]
      by_cases h : p'' = p
      · subst h; simp
      · have : p''.1 ≠ p.1 := fun e => h (Subtype.ext e)
        simp [h, hρ0 _ this]
    have hPk : PhiZ (Hl := Hl) (Ow := Ow) F k = ρ (.x p.1) • (Pi.single p (1 : ℚ)) := by
      rw [← hPρ, ← hsum, map_add, hPs, zero_add]
    have : Pi.single p (1 : ℚ) = (ρ (.x p.1))⁻¹ • PhiZ (Hl := Hl) (Ow := Ow) F k := by
      rw [hPk, smul_smul, inv_mul_cancel₀ hρx, one_smul]
    rw [SetLike.mem_coe, this]
    exact Submodule.smul_mem _ _ (Submodule.mem_map_of_mem hk)
  have h1 : finrank ℚ (⊤ : Submodule ℚ (F → ℚ)) ≤ finrank ℚ
      (Submodule.map (PhiZ (Hl := Hl) (Ow := Ow) F) Kc) := Submodule.finrank_mono htop
  have h2 := Submodule.finrank_map_le (PhiZ (Hl := Hl) (Ow := Ow) F) Kc
  rw [finrank_top, Module.finrank_fintype_fun_eq_card, Fintype.card_coe] at h1
  omega

/-! ## Counting -/

theorem sum_countP_le {α β : Type} [DecidableEq β] (l : List α) (g : α → β) (T : Finset β)
    (P : β → Prop) [DecidablePred P] (hT : ∀ C ∈ T, P C) :
    ∑ C ∈ T, l.countP (fun a => decide (g a = C)) ≤ l.countP (fun a => decide (P (g a))) := by
  induction l with
  | nil => simp
  | cons a l ih =>
    simp only [List.countP_cons, Finset.sum_add_distrib]
    have h : ∑ C ∈ T, (if decide (g a = C) = true then 1 else 0) ≤ (if decide (P (g a)) = true then 1 else 0) := by
      simp only [decide_eq_true_eq]
      rw [Finset.sum_ite_eq]
      by_cases hm : g a ∈ T
      · simp [hm, hT _ hm]
      · simp [hm]
    omega

/-! ## Theorem Y -/

theorem theoremY (W : Word cl s) (hCSF : CSFinal s) (hCSE : CSEntry s) (hBU : BornUnique s)
    (hSR : SlackRank (pub cl) s) : 104 ≤ nStops s + nOwnNonV s := by
  classical
  have hK' : ∀ c, ∃ K : Submodule ℚ (Reg Pt Hl Ow → ℚ), c ≠ Vc → (finrank ℚ K ≤ sigma s c ∧
      I s c ≤ Submodule.span ℚ (Fstay (pub cl) s c ∪ EBL s c) ⊔ K) := by
    intro c
    by_cases h : c = Vc
    · exact ⟨⊥, fun h' => absurd h h'⟩
    · obtain ⟨K, hK⟩ := hSR c h
      exact ⟨K, fun _ => hK⟩
  choose K hK using hK'
  have hP : ∀ p, ∃ C ρ, sigma s (Hq (cl.lab p)) = 0 → (C < Hq (cl.lab p) ∧ ρ ∈ I s C ∧
      ρ (.x p) ≠ 0 ∧ ∀ p' ≠ p, ρ (.x p') = 0) := by
    intro p
    by_cases h : sigma s (Hq (cl.lab p)) = 0
    · obtain ⟨C, ρ, hh⟩ := port_fed W hCSF hCSE hBU K hK p h
      exact ⟨C, ρ, fun _ => hh⟩
    · exact ⟨∅, 0, fun h' => absurd h' h⟩
  choose Cp ρp hρ using hP
  let w : Pt → Ch := fun p => if sigma s (Hq (cl.lab p)) = 0 then Cp p else Hq (cl.lab p)
  have hwV : ∀ p, w p ≠ Vc := by
    intro p
    simp only [w]
    split_ifs with h
    · intro hV
      have hlt := (hρ p h).1
      rw [hV] at hlt
      exact hlt.2 (Hq_sub_Vc _)
    · exact Hq_ne_Vc cl p
  have hfib : ∀ C, (Finset.univ.filter (fun p => w p = C)).card ≤ sigma s C := by
    intro C
    by_cases hg : ∃ p0, sigma s (Hq (cl.lab p0)) ≠ 0 ∧ Hq (cl.lab p0) = C
    · obtain ⟨p0, hp0, hC⟩ := hg
      have hσ : 1 ≤ sigma s C := by rw [← hC]; omega
      have hsub : Finset.univ.filter (fun p => w p = C) ⊆ {p0} := by
        intro p hp
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hp
        rw [Finset.mem_singleton]
        simp only [w] at hp
        split_ifs at hp with h
        · exfalso
          have hlt := (hρ p h).1
          rw [hp] at hlt
          have h1 := Finset.card_lt_card hlt
          rw [← hC, Hq_card_lab cl p0, Hq_card_lab cl p] at h1
          omega
        · exact Hq_lab_inj cl (hp.trans hC.symm)
      have := Finset.card_le_card hsub
      simp at this
      omega
    · push Not at hg
      rcases (Finset.univ.filter (fun p => w p = C)).eq_empty_or_nonempty with he | hne
      · rw [he]; simp
      · obtain ⟨p1, hp1⟩ := hne
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hp1
        have hCV : C ≠ Vc := hp1 ▸ hwV p1
        have hsub : Finset.univ.filter (fun p => w p = C) ⊆
            Finset.univ.filter (fun p => sigma s (Hq (cl.lab p)) = 0 ∧ Cp p = C) := by
          intro p hp
          simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hp ⊢
          simp only [w] at hp
          split_ifs at hp with h
          · exact ⟨h, hp⟩
          · exact absurd hp (hg p h)
        obtain ⟨hKr, hKI⟩ := hK C hCV
        have := fed_card_le W hBU C (K C) hKr hKI hCV
          (Finset.univ.filter (fun p => sigma s (Hq (cl.lab p)) = 0 ∧ Cp p = C))
          (by
            intro p hp
            simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hp
            obtain ⟨hσ0, hC⟩ := hp
            obtain ⟨a, b, c, d⟩ := hρ p hσ0
            exact ⟨ρp p, hC ▸ a, hC ▸ b, c, d⟩)
        exact (Finset.card_le_card hsub).trans this
  have h104 : 104 ≤ ∑ C ∈ Finset.univ.image w, sigma s C := by
    have h1 := Finset.card_eq_sum_card_image w (Finset.univ : Finset Pt)
    rw [Finset.card_univ, cl.card104] at h1
    rw [h1]
    exact Finset.sum_le_sum (fun C _ => hfib C)
  have hT : ∀ C ∈ Finset.univ.image w, C ≠ Vc := by
    intro C hC
    obtain ⟨p, -, rfl⟩ := Finset.mem_image.mp hC
    exact hwV p
  have hs1 := sum_countP_le s.slog Prod.snd (Finset.univ.image w) (fun _ => True) (fun C _ => trivial)
  have hs2 := sum_countP_le s.olog (fun m => m.2.1) (Finset.univ.image w) (fun C => C ≠ Vc) hT
  have hsig : ∑ C ∈ Finset.univ.image w, sigma s C =
      ∑ C ∈ Finset.univ.image w, s.slog.countP (fun t => decide (t.2 = C)) +
      ∑ C ∈ Finset.univ.image w, s.olog.countP (fun m => decide (m.2.1 = C)) := by
    unfold sigma; rw [Finset.sum_add_distrib]
  have hl : s.slog.countP (fun a => decide (True)) = nStops s := by
    simp [nStops]
  have hl2 : s.olog.countP (fun a => decide (a.2.1 ≠ Vc)) = nOwnNonV s := by
    unfold nOwnNonV; congr
  omega

end Main

end WordModel

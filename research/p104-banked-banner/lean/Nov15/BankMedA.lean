/-
BankMedA .  `Mediated` / `MediatedS` of BankTieA/C become THEOREMS (BD §1 last-descent split).
  descent k  :=  ¬ src k ≤ dst k        (every other bank is a nested hop / ascent: src ≤ dst, charts only grow)
  gens N C   :=  inputs born in charts ≤ C  ∪  descent forms d k delivered to charts ≤ C.
  d_mem      : every bank form d j ∈ span (gens N (src j))      (strong induction on the schedule; Net.read)
  O_mem      : every output   O f ∈ span (gens N (B f))         (Net.out)
  last_descent_split : under chart locality (P-LOC)  hin : lq p ∈ A (xin p),  hout : B (yout s) ⊥ lq s,
      ∃ γ, (γ f k ≠ 0 → k a descent ∧ dst k ≤ B f) ∧ on odd pairs O (yout s) (xin p) = Σ_k d k (xin p) · γ (yout s) k.
      (parity: the non-descent residual of O (yout s) only holds inputs with A (xin p) ≤ B (yout s), killed by oddness.)
  mediatedS_of_loc / mediated_of_loc : + every descent is a chain step (hcov) ⟹ the regathered tie (same layout charts,
      fresh, β, carried, e, xin, yout; gathers := γ) satisfies MediatedS / Mediated.  No nest / minors / Contract needed.
  bank_kappa_lt_banner_tiedS_loc : banner with hM replaced by hin, hout, hcov.  Kernel only.
-/
import Nov15.BankTieC

namespace BankMed
open Finset Module Submodule BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall BankWireC BankTie

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- generators of the last-descent space at chart C. -/
def gens (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (C : Submodule (ZMod 2) V) : Set (Fld → ℚ) :=
  {v | ∃ g, N.A g ≤ C ∧ v = Pi.single g 1} ∪ {v | ∃ k, ¬ N.src k ≤ N.dst k ∧ N.dst k ≤ C ∧ v = N.d k}

theorem gens_mono (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) {C C' : Submodule (ZMod 2) V} (h : C ≤ C') :
    gens N C ⊆ gens N C' := by
  rintro v (⟨g, hg, rfl⟩ | ⟨k, hk, hd, rfl⟩)
  · exact Or.inl ⟨g, hg.trans h, rfl⟩
  · exact Or.inr ⟨k, hk, hd.trans h, rfl⟩

/-- every bank form lies in the last-descent span of its source chart. -/
theorem d_mem (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (j : Bank) : N.d j ∈ span ℚ (gens N (N.src j)) := by
  induction j using WellFoundedLT.induction with
  | _ j ih =>
    refine (span_le.mpr ?_) (N.read j)
    rintro v (⟨g, hg, rfl⟩ | ⟨i, hi, hd, rfl⟩)
    · exact subset_span (Or.inl ⟨g, hg.le, rfl⟩)
    · by_cases hdesc : N.src i ≤ N.dst i
      · exact span_mono (gens_mono N (hdesc.trans hd.le)) (ih i hi)
      · exact subset_span (Or.inr ⟨i, hdesc, hd.le, rfl⟩)

/-- every output lies in the last-descent span of its output chart. -/
theorem O_mem (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (f : Fld) : N.O f ∈ span ℚ (gens N (N.B f)) := by
  refine (span_le.mpr ?_) (N.out f)
  rintro v (⟨g, hg, rfl⟩ | ⟨i, hd, rfl⟩)
  · exact subset_span (Or.inl ⟨g, hg.le, rfl⟩)
  · by_cases hdesc : N.src i ≤ N.dst i
    · exact span_mono (gens_mono N (hdesc.trans hd.le)) (d_mem N i)
    · exact subset_span (Or.inr ⟨i, hdesc, hd.le, rfl⟩)

open Classical in
/-- indexed generators (zero where the generator condition fails). -/
noncomputable def gfun (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (C : Submodule (ZMod 2) V) :
    Fld ⊕ Bank → (Fld → ℚ)
  | Sum.inl g => if N.A g ≤ C then Pi.single g 1 else 0
  | Sum.inr k => if ¬ N.src k ≤ N.dst k ∧ N.dst k ≤ C then N.d k else 0

theorem coeffs (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (f : Fld) :
    ∃ c : Fld ⊕ Bank → ℚ, ∑ i, c i • gfun N (N.B f) i = N.O f := by
  classical
  have hle : span ℚ (gens N (N.B f)) ≤ span ℚ (Set.range (gfun N (N.B f))) := by
    refine span_mono ?_
    rintro v (⟨g, hg, rfl⟩ | ⟨k, hk, hd, rfl⟩)
    · exact ⟨Sum.inl g, by simp [gfun, hg]⟩
    · exact ⟨Sum.inr k, by simp [gfun, hk, hd]⟩
  exact (mem_span_range_iff_exists_fun ℚ).1 (hle (O_mem N f))

/-- **last-descent split** (BD §1), from Net path semantics + chart locality alone. -/
theorem last_descent_split (N : Net ℚ (Submodule (ZMod 2) V) Fld Bank) (xin yout : Fin 104 → Fld)
    (hin : ∀ p, DF.lq p ∈ N.A (xin p)) (hout : ∀ s, ∀ y ∈ N.B (yout s), dot (DF.lq s) y = 0) :
    ∃ γ : Fld → Bank → ℚ, (∀ f k, γ f k ≠ 0 → ¬ N.src k ≤ N.dst k ∧ N.dst k ≤ N.B f) ∧
      ∀ p s, dot (DF.lq p) (DF.lq s) = 1 → N.O (yout s) (xin p) = ∑ k, N.d k (xin p) * γ (yout s) k := by
  classical
  choose c hc using coeffs N
  refine ⟨fun f k => if ¬ N.src k ≤ N.dst k ∧ N.dst k ≤ N.B f then c f (Sum.inr k) else 0, ?_, ?_⟩
  · intro f k h
    by_contra h'
    exact h (if_neg h')
  · intro p s hps
    have hnot : ¬ N.A (xin p) ≤ N.B (yout s) := by
      intro hle
      have h0 := hout s (DF.lq p) (hle (hin p))
      have hc' : dot (DF.lq p) (DF.lq s) = dot (DF.lq s) (DF.lq p) := dotProduct_comm _ _
      rw [hc', h0] at hps
      exact zero_ne_one hps
    rw [← hc (yout s)]
    rw [Finset.sum_apply, Fintype.sum_sum_type]
    have h1 : ∑ g : Fld, (c (yout s) (Sum.inl g) • gfun N (N.B (yout s)) (Sum.inl g)) (xin p) = 0 := by
      refine Finset.sum_eq_zero fun g _ => ?_
      by_cases hg : g = xin p
      · subst hg; simp [gfun, hnot]
      · by_cases hA : N.A g ≤ N.B (yout s)
        · simp [gfun, hA, Ne.symm hg]
        · simp [gfun, hA]
    rw [h1, zero_add]
    refine Finset.sum_congr rfl fun k _ => ?_
    by_cases hk : ¬ N.src k ≤ N.dst k ∧ N.dst k ≤ N.B (yout s)
    · simp only [gfun, Pi.smul_apply, smul_eq_mul, if_pos hk]; ring
    · simp only [gfun, Pi.smul_apply, smul_eq_mul, if_neg hk]; simp

variable {G : BankedGraph ℚ Fld Bank} {T : Type} [Fintype T]

theorem carried_congr {m : ℕ} (C C' : ChainRow.RelayChain ℚ DF.lq m) (hf : C.fresh = C'.fresh)
    (hb : C.beta = C'.beta) : ∀ k, C.carried k = C'.carried k
  | 0 => by simp [ChainRow.RelayChain.carried, hf]
  | k + 1 => by
    funext p
    simp only [ChainRow.RelayChain.carried, carried_congr C C' hf hb k, hf, hb]

/-- the tie with its gathers replaced by g (any legal gather family read off G). -/
def regather (τ : ChainTie G T) (g : Fin 104 → Bank → ℚ)
    (hg : ∀ s k, g s k ≠ 0 → ∀ y ∈ G.N.dst k, dot (DF.lq s) y = 0) : ChainTie G T where
  L := { len := τ.L.len
         chain := fun c =>
          { ch := (τ.L.chain c).ch
            desc := (τ.L.chain c).desc
            fresh := (τ.L.chain c).fresh
            fresh_supp := (τ.L.chain c).fresh_supp
            gath := fun k s => if h : k < τ.L.len c then g s (τ.e ⟨c, ⟨k, h⟩⟩) else 0
            gath_supp := by
              intro k s hne y hy
              by_cases h : k < τ.L.len c
              · rw [dif_pos h] at hne
                have := τ.hdst ⟨c, ⟨k, h⟩⟩
                exact hg s _ hne y (by rw [← this]; exact hy)
              · rw [dif_neg h] at hne; exact absurd rfl hne
            beta := (τ.L.chain c).beta
            beta_ne := (τ.L.chain c).beta_ne } }
  e := τ.e
  inj := τ.inj
  hsrc := fun x => τ.hsrc x
  hdst := fun x => τ.hdst x
  xin := τ.xin
  yout := τ.yout
  hcar := fun x p => by
    rw [← τ.hcar x p]
    refine congrFun (carried_congr _ (τ.L.chain x.1) ?_ ?_ _) p <;> rfl

/-- **MediatedS as a theorem**: chart locality + every descent is a chain step. -/
theorem mediatedS_of_loc (τ : ChainTie G T) (c : Fin 104 → ℚ) (hc : ∀ s, c s ≠ 0)
    (hin : ∀ p, DF.lq p ∈ G.N.A (τ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (τ.yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ k, ¬ G.N.src k ≤ G.N.dst k → ∃ x, τ.e x = k) :
    ∃ τ' : ChainTie G T, τ'.xin = τ.xin ∧ τ'.yout = τ.yout ∧ MediatedS τ' c := by
  classical
  obtain ⟨γ, hγ, hsplit⟩ := last_descent_split G.N τ.xin τ.yout hin hout
  have hg : ∀ s k, (c s)⁻¹ * γ (τ.yout s) k ≠ 0 → ∀ y ∈ G.N.dst k, dot (DF.lq s) y = 0 := by
    intro s k h y hy
    exact hout s y ((hγ _ k (right_ne_zero_of_mul h)).2 hy)
  refine ⟨regather τ (fun s k => (c s)⁻¹ * γ (τ.yout s) k) hg, rfl, rfl, ?_⟩
  intro p s hps
  show G.N.O (τ.yout s) (τ.xin p) = c s * ∑ x : (Σ c : T, Fin (τ.L.len c)),
      G.N.d (τ.e x) (τ.xin p) * (if h : (x.2 : ℕ) < τ.L.len x.1 then (c s)⁻¹ * γ (τ.yout s) (τ.e ⟨x.1, ⟨x.2, h⟩⟩) else 0)
  simp only [dif_pos (Fin.is_lt _), Fin.eta]
  rw [hsplit p s hps]
  have hsub : ∑ k ∈ univ.image τ.e, G.N.d k (τ.xin p) * γ (τ.yout s) k = ∑ k, G.N.d k (τ.xin p) * γ (τ.yout s) k := by
    refine Finset.sum_subset (Finset.subset_univ _) fun k _ hk => ?_
    by_contra hne
    obtain ⟨x, hx⟩ := hcov k (hγ _ k (right_ne_zero_of_mul hne)).1
    exact hk (Finset.mem_image.2 ⟨x, Finset.mem_univ _, hx⟩)
  rw [← hsub, Finset.sum_image fun x _ y _ h => τ.inj h, Finset.mul_sum]
  refine Finset.sum_congr rfl fun x _ => ?_
  rw [mul_left_comm (c s), mul_inv_cancel_left₀ (hc s)]

theorem mediated_of_loc (τ : ChainTie G T)
    (hin : ∀ p, DF.lq p ∈ G.N.A (τ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (τ.yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ k, ¬ G.N.src k ≤ G.N.dst k → ∃ x, τ.e x = k) :
    ∃ τ' : ChainTie G T, τ'.xin = τ.xin ∧ τ'.yout = τ.yout ∧ Mediated τ' := by
  obtain ⟨τ', h1, h2, h3⟩ := mediatedS_of_loc τ (fun _ => 1) (fun _ => one_ne_zero) hin hout hcov
  exact ⟨τ', h1, h2, fun p s hps => by rw [h3 p s hps, one_mul]⟩

/-- **banner, Mediated discharged**: hM replaced by chart locality + descents ⊆ chain steps. -/
theorem bank_kappa_lt_banner_tiedS_loc (G : Fin 2048 → BankedGraph ℚ Fld Bank) (hc : ∀ i, HSContract (G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (G i) T) (h8 : Fintype.card T ≤ 8) (c : Fin 2048 → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (G i) (τ i).xin (τ i).yout (c i))
    (hin : ∀ i p, DF.lq p ∈ (G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (G i).N.src k ≤ (G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin 2048 → O → Chart)
    (hF : ∀ i, (gModel (G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankBannerCert.TB - cdat (1 - κ) BankBannerCert.PB) :
    κ < 2381707 / 250000000 := by
  have hex := fun i => mediatedS_of_loc (τ i) (c i) (fun s => ((hC i).1 s).1) (hin i) (hout i) (hcov i)
  choose τ' hx hy hM using hex
  refine bank_kappa_lt_banner_tiedS G hc τ' h8 c (fun i => ?_) hM oi oc hF hW κ hκ0 hκ1 paid hpaid hcaller
  rw [hx i, hy i]; exact hC i

end BankMed
#print axioms BankMed.last_descent_split
#print axioms BankMed.mediated_of_loc
#print axioms BankMed.bank_kappa_lt_banner_tiedS_loc

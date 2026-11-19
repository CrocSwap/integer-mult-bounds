/-
ThmGB.  Theorem G (general descent DAGs) TIED TO A BANKED GRAPH G (kernel only).
  GLayout G R Tr Tu : groups R (pure relay chains of G's banks; a zero-relay chain enters as its pieces), whose
    HEAD deposit may carry folded trunk content; trunks Tr (G's banks, any DAG listed outward per group, OrdW);
    tails Tu (G's banks, fresh-free: d = Σ_r μ_{u r}·(group-r end content), listed outward per group, OrdU).
    No-bypass: every descent of G is a group bank, a tail bank, input-dead, or not gatherable (so trunks are never
    gathered and trunk content reaches a gather only through a group).  Gathers are read off G
    (BankMed.last_descent_split).  Every field is a statement about G's banks, charts, d; no free bridge objects.
  rows                : folding gives an IsDecoder with one row per group; |R| = 8; per group
                        dim(head ⊔ ancestor trunk charts) ≥ 8 and dim(end ⊓ tail end charts) ≤ 1.
  foldW_bound / foldU_bound : δ_r ≤ Σ_{anc r} d_T and δ'_r ≤ Σ_{tails r} d_U (FOLD, both sides).
  decoupled           : descMass G ≥ 56 + E_W + E_U   (Theorem G).
  mass_ge_56_comp     : per-component OTI on both sides ⟹ descMass G ≥ 56.
  mass_ge_56_disjoint : every trunk feeds ≤ 1 group and every tail is fed by ≤ 1 group ⟹ ≥ 56 (no OTI hypothesis).
  big_mass_floor_G    : × BankCallerGen ⟹ κ < .00952721 for every K-call caller and every Theorem-G graph.
  ofChainTieG / kappa7761_lt_G : non-vacuity (#7761, Tr = Tu = Empty).
-/
import Nov15.ThmGA
import Nov15.BankBigB

open Module Submodule Finset

namespace ThmG
open DecoderWall ChainRow BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie
  BankPrem BankCallerGen BankBig

/-- a GROUP: pure relay chain whose head deposit (step 0) is unrestricted (it may carry folded trunk content). -/
structure HPre where
  ch : ℕ → Ch
  desc : ∀ j, ch (j + 1) ≤ ch j
  fresh : ℕ → Fin 104 → ℚ
  fresh_supp : ∀ j p, 0 < j → fresh j p ≠ 0 → DF.lq p ∈ ch j
  beta : ℕ → ℚ
  beta_ne : ∀ k, beta k ≠ 0

namespace HPre
variable (C : HPre)

def carried : ℕ → Fin 104 → ℚ
  | 0 => C.fresh 0
  | k + 1 => fun p => C.beta (k + 1) * carried k p + C.fresh (k + 1) p

def P (k : ℕ) : ℚ := ∏ i ∈ range (k + 1), C.beta i

theorem P_ne (k : ℕ) : C.P k ≠ 0 := prod_ne_zero_iff.2 fun i _ => C.beta_ne i

def phi (m : ℕ) (p : Fin 104) : ℚ := ∑ j ∈ range m, (C.P j)⁻¹ * C.fresh j p

theorem carried_eq (k : ℕ) (p : Fin 104) :
    C.carried k p = ∑ j ∈ range (k + 1), C.P k * (C.P j)⁻¹ * C.fresh j p := by
  induction k with
  | zero => simp [carried, C.P_ne 0]
  | succ k ih =>
    simp only [carried]
    rw [ih, sum_range_succ _ (k + 1), mul_sum]
    have hP : C.P (k + 1) = C.P k * C.beta (k + 1) := by
      simp only [P]; rw [prod_range_succ _ (k + 1)]
    rw [mul_inv_cancel₀ (C.P_ne (k + 1)), one_mul]
    congr 1
    refine sum_congr rfl fun j _ => ?_
    rw [hP]; ring

theorem carried_phi (k : ℕ) (p : Fin 104) : C.carried k p = C.P k * C.phi (k + 1) p := by
  rw [carried_eq, phi, mul_sum]
  exact sum_congr rfl fun j _ => by ring

theorem antitone_ch : Antitone C.ch := antitone_nat_of_succ_le C.desc

/-- chain-row identity with a head deposit: on an odd pair the chain block is φ(p)·Σ P_k g_k. -/
theorem chain_row {p s : Fin 104} (hps : dot (DF.lq p) (DF.lq s) = 1) (m : ℕ) (g : ℕ → ℚ)
    (hg : ∀ k, k < m → g k ≠ 0 → ∀ y ∈ C.ch (k + 1), dot (DF.lq s) y = 0) :
    ∑ k ∈ range m, C.carried k p * g k = C.phi m p * ∑ k ∈ range m, C.P k * g k := by
  unfold phi
  rw [sum_mul_sum, sum_comm]
  refine sum_congr rfl fun k hk => ?_
  rw [carried_eq, sum_mul]
  have hk' : k < m := mem_range.1 hk
  have hsub : range (k + 1) ⊆ range m := by
    intro j hj; simp only [mem_range] at *; omega
  rw [sum_subset hsub]
  · exact sum_congr rfl fun j _ => by ring
  · intro j _ hj
    simp only [mem_range, not_lt] at hj
    by_cases hf : C.fresh j p = 0
    · rw [hf]; ring
    by_cases hgk : g k = 0
    · rw [hgk]; ring
    exfalso
    have hm : DF.lq p ∈ C.ch (k + 1) := C.antitone_ch (show k + 1 ≤ j by omega)
      (C.fresh_supp j p (by omega) hf)
    have h0 := hg k hk' hgk (DF.lq p) hm
    rw [show dot (DF.lq s) (DF.lq p) = dot (DF.lq p) (DF.lq s) from dotProduct_comm _ _, hps] at h0
    exact one_ne_zero h0

theorem phi_ne (m : ℕ) (p : Fin 104) (h : C.phi m p ≠ 0) : ∃ j < m, C.fresh j p ≠ 0 := by
  obtain ⟨j, hj, hj'⟩ := exists_ne_zero_of_sum_ne_zero h
  exact ⟨j, mem_range.1 hj, right_ne_zero_of_mul hj'⟩

noncomputable def mass (m : ℕ) : ℕ := ∑ j ∈ range m, (dm (C.ch j) - dm (C.ch (j + 1)))

theorem drop_le_mass : ∀ m, dm (C.ch 0) - dm (C.ch m) ≤ C.mass m
  | 0 => by simp [mass]
  | m + 1 => by
    have ih := drop_le_mass m
    simp only [mass] at *
    rw [sum_range_succ]
    have h1 := Submodule.finrank_mono (C.desc m)
    have h2 := Submodule.finrank_mono (C.antitone_ch (Nat.zero_le m))
    omega

end HPre

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- **Theorem-G layout tied to G.** -/
structure GLayout (G : BankedGraph ℚ Fld Bank) (R Tr Tu : Type) [Fintype R] [Fintype Tr] [Fintype Tu] where
  xin : Fin 104 → Fld
  yout : Fin 104 → Fld
  len : R → ℕ
  grp : R → HPre
  eg : (Σ r : R, Fin (len r)) → Bank
  eT : Tr → Bank
  eU : Tu → Bank
  inj : Function.Injective (Sum.elim eg (Sum.elim eT eU))
  gsrc : ∀ x : (Σ r : R, Fin (len r)), (grp x.1).ch x.2 = G.N.src (eg x)
  gdst : ∀ x : (Σ r : R, Fin (len r)), (grp x.1).ch ((x.2 : ℕ) + 1) = G.N.dst (eg x)
  gcar : ∀ (x : Σ r : R, Fin (len r)) p, (grp x.1).carried x.2 p = G.N.d (eg x) (xin p)
  -- trunks (W side)
  ancL : R → List Tr
  anc_nodup : ∀ r, (ancL r).Nodup
  anc_ord : ∀ r, OrdW (fun t => G.N.src (eT t)) (fun t => G.N.dst (eT t)) ((grp r).ch 0) (ancL r)
  head_supp : ∀ r p, (grp r).fresh 0 p ≠ 0 →
    DF.lq p ∈ hullW (fun t => G.N.src (eT t)) ((grp r).ch 0) (ancL r)
  tdesc : ∀ t, G.N.dst (eT t) ≤ G.N.src (eT t)
  -- tails (U side)
  mu : Tu → R → ℚ
  mu_len : ∀ u r, mu u r ≠ 0 → 0 < len r
  ucar : ∀ u p, G.N.d (eU u) (xin p) = ∑ r, mu u r * (grp r).carried (len r - 1) p
  tailL : R → List Tu
  tail_nodup : ∀ r, (tailL r).Nodup
  tail_mem : ∀ u r, mu u r ≠ 0 → u ∈ tailL r
  tail_ord : ∀ r, OrdU (fun u => G.N.src (eU u)) (fun u => G.N.dst (eU u)) ((grp r).ch (len r)) (tailL r)
  udesc : ∀ u, G.N.dst (eU u) ≤ G.N.src (eU u)
  -- no bypass
  silent : ∀ k, ¬ G.N.src k ≤ G.N.dst k →
    (∃ x, eg x = k) ∨ (∃ u, eU u = k) ∨ (∀ p, G.N.d k (xin p) = 0) ∨ ¬ Gatherable G yout k

variable {G : BankedGraph ℚ Fld Bank} {R Tr Tu : Type} [Fintype R] [Fintype Tr] [Fintype Tu]
  [DecidableEq Tr] [DecidableEq Tu]

namespace GLayout
variable (Λ : GLayout G R Tr Tu)

def sT (t : Tr) : Ch := G.N.src (Λ.eT t)
def tT (t : Tr) : Ch := G.N.dst (Λ.eT t)
def sU (u : Tu) : Ch := G.N.src (Λ.eU u)
def tU (u : Tu) : Ch := G.N.dst (Λ.eU u)
/-- head chart a_r, end chart b_r, W hull, U hull. -/
def hd (r : R) : Ch := (Λ.grp r).ch 0
def en (r : R) : Ch := (Λ.grp r).ch (Λ.len r)
def hW (r : R) : Ch := hullW Λ.sT (Λ.hd r) (Λ.ancL r)
def hU (r : R) : Ch := hullU Λ.tU (Λ.en r) (Λ.tailL r)
/-- trunk / tail drops and group descent mass. -/
noncomputable def dTr (t : Tr) : ℕ := dm (Λ.sT t) - dm (Λ.tT t)
noncomputable def dTu (u : Tu) : ℕ := dm (Λ.sU u) - dm (Λ.tU u)
noncomputable def mG (r : R) : ℕ := (Λ.grp r).mass (Λ.len r)

open Classical in
/-- **ROWS.** Folding trunks into heads and tails into gathers gives an IsDecoder with one row per group. -/
theorem rows (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8) :
    Fintype.card R = 8 ∧ ∀ r, 8 ≤ dm (Λ.hW r) ∧ dm (Λ.hU r) ≤ 1 := by
  obtain ⟨γ, hγ, hsplit⟩ := BankMed.last_descent_split G.N Λ.xin Λ.yout hin hout
  have hγL : ∀ s k, γ (Λ.yout s) k ≠ 0 → ∀ y ∈ G.N.dst k, dot (DF.lq s) y = 0 := fun s k h y hy =>
    hout s y ((hγ _ k h).2 hy)
  -- per-group gathers as functions of ℕ
  let gk : Fin 104 → R → ℕ → ℚ := fun s r k =>
    if h : k < Λ.len r then γ (Λ.yout s) (Λ.eg ⟨r, ⟨k, h⟩⟩) else 0
  let Φ : Fin 104 → R → ℚ := fun p r => (Λ.grp r).phi (Λ.len r) p
  let Γ : Fin 104 → R → ℚ := fun s r =>
    ∑ k ∈ range (Λ.len r), (Λ.grp r).P k * gk s r k +
      ∑ u, Λ.mu u r * (Λ.grp r).P (Λ.len r - 1) * γ (Λ.yout s) (Λ.eU u)
  -- the two-way bank map (groups ⊕ tails)
  let E2 : (Σ r : R, Fin (Λ.len r)) ⊕ Tu → Bank := Sum.elim Λ.eg Λ.eU
  have hE2 : Function.Injective E2 := by
    rintro (x | x) (y | y) h
    · exact congrArg Sum.inl (Sum.inl.inj (Λ.inj (a₁ := Sum.inl x) (a₂ := Sum.inl y) h))
    · exact absurd (Λ.inj (a₁ := Sum.inl x) (a₂ := Sum.inr (Sum.inr y)) h) (by simp)
    · exact absurd (Λ.inj (a₁ := Sum.inr (Sum.inr x)) (a₂ := Sum.inl y) h) (by simp)
    · have := Λ.inj (a₁ := Sum.inr (Sum.inr x)) (a₂ := Sum.inr (Sum.inr y)) h
      simp only [Sum.inr.injEq] at this
      rw [this]
  -- odd identity
  have hodd : ∀ p s, dot (DF.lq p) (DF.lq s) = 1 →
      G.N.O (Λ.yout s) (Λ.xin p) = ∑ r, Φ p r * Γ s r := by
    intro p s hps
    rw [hsplit p s hps]
    have hsub : ∑ k ∈ univ.image E2, G.N.d k (Λ.xin p) * γ (Λ.yout s) k =
        ∑ k, G.N.d k (Λ.xin p) * γ (Λ.yout s) k := by
      refine sum_subset (subset_univ _) fun k _ hk => ?_
      by_cases hγk : γ (Λ.yout s) k = 0
      · rw [hγk, mul_zero]
      · have hd := hγ _ k hγk
        rcases Λ.silent k hd.1 with ⟨x, hx⟩ | ⟨u, hu⟩ | h0 | hng
        · exact absurd (mem_image.2 ⟨Sum.inl x, mem_univ _, hx⟩) hk
        · exact absurd (mem_image.2 ⟨Sum.inr u, mem_univ _, hu⟩) hk
        · rw [h0 p, zero_mul]
        · exact absurd ⟨s, hd.2⟩ hng
    rw [← hsub, sum_image fun x _ y _ h => hE2 h, Fintype.sum_sum_type]
    simp only [E2, Sum.elim_inl, Sum.elim_inr]
    -- group part
    have hgrp : ∑ x : (Σ r : R, Fin (Λ.len r)), G.N.d (Λ.eg x) (Λ.xin p) * γ (Λ.yout s) (Λ.eg x) =
        ∑ r, Φ p r * ∑ k ∈ range (Λ.len r), (Λ.grp r).P k * gk s r k := by
      rw [Fintype.sum_sigma]
      refine sum_congr rfl fun r _ => ?_
      have h1 : ∑ k : Fin (Λ.len r), G.N.d (Λ.eg ⟨r, k⟩) (Λ.xin p) * γ (Λ.yout s) (Λ.eg ⟨r, k⟩) =
          ∑ k ∈ range (Λ.len r), (Λ.grp r).carried k p * gk s r k := by
        rw [← Fin.sum_univ_eq_sum_range (fun k => (Λ.grp r).carried k p * gk s r k)]
        refine sum_congr rfl fun k _ => ?_
        rw [← Λ.gcar ⟨r, k⟩ p]
        simp only [gk, dif_pos k.2, Fin.eta]
      rw [h1]
      refine (Λ.grp r).chain_row hps _ _ fun k hk hne y hy => ?_
      simp only [gk, dif_pos hk] at hne
      exact hγL s _ hne y (by rw [← Λ.gdst ⟨r, ⟨k, hk⟩⟩]; exact hy)
    -- tail part
    have htail : ∑ u, G.N.d (Λ.eU u) (Λ.xin p) * γ (Λ.yout s) (Λ.eU u) =
        ∑ r, Φ p r * ∑ u, Λ.mu u r * (Λ.grp r).P (Λ.len r - 1) * γ (Λ.yout s) (Λ.eU u) := by
      simp only [Λ.ucar, sum_mul, mul_sum]
      rw [sum_comm]
      refine sum_congr rfl fun r _ => sum_congr rfl fun u _ => ?_
      by_cases hm : Λ.mu u r = 0
      · rw [hm]; ring
      · have hl := Λ.mu_len u r hm
        rw [(Λ.grp r).carried_phi, Nat.sub_add_cancel hl]
        ring
    rw [hgrp, htail, ← sum_add_distrib]
    exact sum_congr rfl fun r _ => by simp only [Γ]; ring
  -- the folded decoder
  let Cg : Fin 104 → R → ℚ := fun s r => (cs s)⁻¹ * Γ s r
  have hd : IsDecoder DF.lq Φ Cg :=
    { diag := fun t => by
        have h := hodd t t (lq_odd t)
        rw [(hC.1 t).2] at h
        simp only [Cg, mul_left_comm (Φ t _), ← mul_sum, ← h]
        exact inv_mul_cancel₀ (hC.1 t).1
      odd := fun t s hts h => by
        have h2 := hodd t s h
        rw [hC.2 t s hts h] at h2
        simp only [Cg, mul_left_comm (Φ t _), ← mul_sum, ← h2, mul_zero] }
  have hcard : Fintype.card R = 8 := le_antisymm h8 (DF.decoder_rows_ge_eight Φ Cg hd)
  refine ⟨hcard, fun r => ⟨?_, ?_⟩⟩
  · refine dep_hull_ge_8 Φ Cg hd hcard r _ fun p hp => ?_
    obtain ⟨j, hj, hf⟩ := (Λ.grp r).phi_ne _ p hp
    rcases Nat.eq_zero_or_pos j with rfl | hj0
    · exact Λ.head_supp r p hf
    · exact le_hullW _ _ _ ((Λ.grp r).antitone_ch (Nat.zero_le j) ((Λ.grp r).fresh_supp j p hj0 hf))
  · refine gat_hull_le_1 Φ Cg hd hcard r _ fun s hs y hy => ?_
    have hΓ : Γ s r ≠ 0 := right_ne_zero_of_mul hs
    have hyen : y ∈ Λ.en r := hullU_le _ _ _ hy
    rcases (show (∑ k ∈ range (Λ.len r), (Λ.grp r).P k * gk s r k) ≠ 0 ∨
        (∑ u, Λ.mu u r * (Λ.grp r).P (Λ.len r - 1) * γ (Λ.yout s) (Λ.eU u)) ≠ 0 by
      by_contra hc; push_neg at hc; exact hΓ (by simp only [Γ, hc.1, hc.2, add_zero])) with h1 | h1
    · obtain ⟨k, hk, hk'⟩ := exists_ne_zero_of_sum_ne_zero h1
      have hkl : k < Λ.len r := mem_range.1 hk
      have hne := right_ne_zero_of_mul hk'
      simp only [gk, dif_pos hkl] at hne
      refine hγL s _ hne y ?_
      rw [← Λ.gdst ⟨r, ⟨k, hkl⟩⟩]
      exact (Λ.grp r).antitone_ch (show k + 1 ≤ Λ.len r by omega) hyen
    · obtain ⟨u, -, hu⟩ := exists_ne_zero_of_sum_ne_zero h1
      have hγu := right_ne_zero_of_mul hu
      have hmu : Λ.mu u r ≠ 0 := left_ne_zero_of_mul (left_ne_zero_of_mul hu)
      exact hγL s _ hγu y (hullU_le_mem _ _ _ _ (Λ.tail_mem u r hmu) hy)

/-- FOLD bounds (both sides) from the folded decoder. -/
theorem fold_bounds (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8) (r : R) :
    dW (Λ.hd r) ≤ ∑ t ∈ (Λ.ancL r).toFinset, (Λ.dTr t : ℤ) ∧
      dU (Λ.en r) ≤ ∑ u ∈ (Λ.tailL r).toFinset, (Λ.dTu u : ℤ) := by
  obtain ⟨-, hr⟩ := Λ.rows cs hC hin hout h8
  obtain ⟨hw, hu⟩ := hr r
  have fw := fold_W Λ.sT Λ.tT Λ.tdesc (Λ.ancL r) (Λ.hd r) (Λ.anc_ord r)
  have fu := fold_U Λ.sU Λ.tU Λ.udesc (Λ.tailL r) (Λ.en r) (Λ.tail_ord r)
  have ew : (dropL Λ.sT Λ.tT (Λ.ancL r) : ℤ) = ∑ t ∈ (Λ.ancL r).toFinset, (Λ.dTr t : ℤ) := by
    rw [List.sum_toFinset _ (Λ.anc_nodup r), dropL]; push_cast; rw [List.map_map]; rfl
  have eu : (dropL Λ.sU Λ.tU (Λ.tailL r) : ℤ) = ∑ u ∈ (Λ.tailL r).toFinset, (Λ.dTu u : ℤ) := by
    rw [List.sum_toFinset _ (Λ.tail_nodup r), dropL]; push_cast; rw [List.map_map]; rfl
  have hw' : 8 ≤ dm (hullW Λ.sT (Λ.hd r) (Λ.ancL r)) := hw
  have hu' : dm (hullU Λ.tU (Λ.en r) (Λ.tailL r)) ≤ 1 := hu
  constructor
  · rw [← ew]; simp only [dW]; omega
  · rw [← eu]; simp only [dU]; omega

/-- mass accounting: descMass G ≥ Σ group masses + Σ trunk drops + Σ tail drops. -/
theorem mass_acct : ∑ r, (Λ.mG r : ℤ) + ∑ t, (Λ.dTr t : ℤ) + ∑ u, (Λ.dTu u : ℤ) ≤ descMass G := by
  classical
  set f : Bank → ℤ := fun k => max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 with hf
  have hg : ∑ r, (Λ.mG r : ℤ) = ∑ x : (Σ r : R, Fin (Λ.len r)), f (Λ.eg x) := by
    rw [Fintype.sum_sigma]
    refine sum_congr rfl fun r _ => ?_
    simp only [mG, HPre.mass]; push_cast
    rw [← Fin.sum_univ_eq_sum_range]
    refine sum_congr rfl fun j _ => ?_
    rw [term_eq]
    show max ((dm ((Λ.grp r).ch j) : ℤ) - dm ((Λ.grp r).ch (j + 1))) 0 = _
    rw [Λ.gsrc ⟨r, j⟩, Λ.gdst ⟨r, j⟩]
  have ht' : ∀ t, (Λ.dTr t : ℤ) = f (Λ.eT t) := fun t => by
    simp only [dTr, sT, tT]; rw [term_eq]
  have hu' : ∀ u, (Λ.dTu u : ℤ) = f (Λ.eU u) := fun u => by
    simp only [dTu, sU, tU]; rw [term_eq]
  simp only [ht', hu', hg]
  have e3 : ∑ x : (Σ r : R, Fin (Λ.len r)), f (Λ.eg x) + ∑ t, f (Λ.eT t) + ∑ u, f (Λ.eU u) =
      ∑ x, f (Sum.elim Λ.eg (Sum.elim Λ.eT Λ.eU) x) := by
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]; simp only [Sum.elim_inl, Sum.elim_inr]; ring
  rw [e3, ← sum_image (f := f) fun x _ y _ h => Λ.inj h]
  exact sum_le_sum_of_subset_of_nonneg (subset_univ _) fun k _ _ => le_max_right _ _

/-- **THEOREM G (decoupling, tied).**  descMass G ≥ 56 + E_W + E_U. -/
theorem decoupled (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8) :
    56 + ((∑ t, (Λ.dTr t : ℤ)) - ∑ r, dW (Λ.hd r)) + ((∑ u, (Λ.dTu u : ℤ)) - ∑ r, dU (Λ.en r)) ≤
      descMass G := by
  have hc := (Λ.rows cs hC hin hout h8).1
  have h := decouple hc Λ.hd Λ.en Λ.mG (fun r => (Λ.grp r).drop_le_mass (Λ.len r)) Λ.dTr Λ.dTu
  have := Λ.mass_acct
  linarith

/-- **D ≥ 56 under OTI on both sides** (OTI_W : Σ δ_r ≤ Σ d_T, OTI_U : Σ δ'_r ≤ Σ d_U). -/
theorem mass_ge_56_oti (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8)
    (hW : ∑ r, dW (Λ.hd r) ≤ ∑ t, (Λ.dTr t : ℤ)) (hU : ∑ r, dU (Λ.en r) ≤ ∑ u, (Λ.dTu u : ℤ)) :
    56 ≤ descMass G := by
  have := Λ.decoupled cs hC hin hout h8
  linarith

/-- the per-component OTI hypothesis package (components on each side; any shape). -/
structure CompOTI (Λ : GLayout G R Tr Tu) {C D : Type} [Fintype C] [DecidableEq C] [Fintype D]
    [DecidableEq D] where
  cr : R → C
  ct : Tr → C
  dr : R → D
  du : Tu → D
  otiW : ∀ c, OTIComp (fun r => dW (Λ.hd r)) Λ.dTr cr ct c
  otiU : ∀ d, OTIComp (fun r => dU (Λ.en r)) Λ.dTu dr du d

/-- **D ≥ 56, component form.**  Each component's OTI is discharged by `otiComp_disjoint` (FOLD, using
`fold_bounds`), `otiComp_hall`, or stays a named hypothesis. -/
theorem mass_ge_56_comp (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8) {C D : Type} [Fintype C] [DecidableEq C] [Fintype D] [DecidableEq D]
    (K : CompOTI Λ (C := C) (D := D)) : 56 ≤ descMass G :=
  Λ.mass_ge_56_oti cs hC hin hout h8 (oti_of_comp _ _ K.cr K.ct K.otiW) (oti_of_comp _ _ K.dr K.du K.otiU)

/-- **D ≥ 56 with NO OTI hypothesis** when every trunk feeds ≤ 1 group and every tail is fed by ≤ 1 group
(nested trunks in any in-tree, trunk + tail on one group, Theorem-S single-group trunks; FOLD on both sides). -/
theorem mass_ge_56_disjoint (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Fintype.card R ≤ 8)
    (hdW : ∀ r r', r ≠ r' → Disjoint (Λ.ancL r).toFinset (Λ.ancL r').toFinset)
    (hdU : ∀ r r', r ≠ r' → Disjoint (Λ.tailL r).toFinset (Λ.tailL r').toFinset) : 56 ≤ descMass G := by
  classical
  have hW := oti_of_comp (fun r => dW (Λ.hd r)) Λ.dTr (fun _ => ()) (fun _ => ()) fun c =>
    otiComp_disjoint _ _ _ _ c (fun r => (Λ.ancL r).toFinset)
      (fun r _ => (Λ.fold_bounds cs hC hin hout h8 r).1) (fun _ _ _ _ => rfl)
      (fun r r' _ _ h => hdW r r' h)
  have hU := oti_of_comp (fun r => dU (Λ.en r)) Λ.dTu (fun _ => ()) (fun _ => ()) fun c =>
    otiComp_disjoint _ _ _ _ c (fun r => (Λ.tailL r).toFinset)
      (fun r _ => (Λ.fold_bounds cs hC hin hout h8 r).2) (fun _ _ _ _ => rfl)
      (fun r r' _ _ h => hdU r r' h)
  exact Λ.mass_ge_56_oti cs hC hin hout h8 hW hU

end GLayout

/-! ## the κ bound for every caller in the family and every Theorem-G graph -/

/-- κ from any per-call mass floor (the banner pipeline with hD supplied). -/
theorem kappa_of_mass (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N) (hD : ∀ i, 56 ≤ descMass (c.G i))
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 := by
  have hXD : ∀ i, 2 * descMass (c.G i) ≤ excess (c.G i) := fun i => xbal_tied (c.G i) (oi i) (oc i) (hF i) (hW i)
  exact bank_kappa_lt_banner_of_cert K c.T c.P _ (by norm_num) (cert_gen K hK c.T c.P hTP) c.G hc hD hXD
    κ hκ0 hκ1 _ (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k) (hcaller_of_valid c _ _ hV)

/-- **`big_mass_floor_G`**: every K-call caller of the family whose graphs each carry a Theorem-G layout
(≤ 8 groups, any trunk/tail DAGs without bypass) with per-component OTI on both sides: κ < .00952721. -/
theorem big_mass_floor_G (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, GLayout (c.G i) (R i) (Tr i) (Tu i)) (h8 : ∀ i, Fintype.card (R i) ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {C D : Fin K → Type} [∀ i, Fintype (C i)] [∀ i, DecidableEq (C i)] [∀ i, Fintype (D i)]
    [∀ i, DecidableEq (D i)] (Kc : ∀ i, (Λ i).CompOTI (C := C i) (D := D i))
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  kappa_of_mass K hK c hTP hc
    (fun i => (Λ i).mass_ge_56_comp (cs i) (hC i) (hin i) (hout i) (h8 i) (Kc i)) oi oc hF hW κ hκ0 hκ1 hV

/-- same with no OTI hypothesis: every trunk feeds ≤ 1 group and every tail is fed by ≤ 1 group. -/
theorem big_mass_floor_G_disjoint (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, GLayout (c.G i) (R i) (Tr i) (Tu i)) (h8 : ∀ i, Fintype.card (R i) ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    (hdW : ∀ i r r', r ≠ r' → Disjoint ((Λ i).ancL r).toFinset ((Λ i).ancL r').toFinset)
    (hdU : ∀ i r r', r ≠ r' → Disjoint ((Λ i).tailL r).toFinset ((Λ i).tailL r').toFinset)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  kappa_of_mass K hK c hTP hc
    (fun i => (Λ i).mass_ge_56_disjoint (cs i) (hC i) (hin i) (hout i) (h8 i) (hdW i) (hdU i))
    oi oc hF hW κ hκ0 hκ1 hV

/-! ## non-vacuity: a pure-chain tie is a Theorem-G layout with no trunks and no tails -/

def hOfRelay {m : ℕ} (Cc : ChainRow.RelayChain ℚ DF.lq m) : HPre :=
  ⟨Cc.ch, Cc.desc, Cc.fresh, fun j p _ h => Cc.fresh_supp j p h, Cc.beta, Cc.beta_ne⟩

theorem hOfRelay_carried {m : ℕ} (Cc : ChainRow.RelayChain ℚ DF.lq m) :
    ∀ k, (hOfRelay Cc).carried k = Cc.carried k
  | 0 => rfl
  | k + 1 => by
    funext p
    show Cc.beta (k + 1) * (hOfRelay Cc).carried k p + Cc.fresh (k + 1) p = _
    rw [hOfRelay_carried Cc k]; rfl

noncomputable def ofChainTieG {T : Type} [Fintype T] (τ : ChainTie G T)
    (hcov : ∀ k, ¬ G.N.src k ≤ G.N.dst k → ∃ x, τ.e x = k) : GLayout G T Empty Empty where
  xin := τ.xin
  yout := τ.yout
  len := τ.L.len
  grp := fun c => hOfRelay (τ.L.chain c)
  eg := τ.e
  eT := fun t => t.elim
  eU := fun u => u.elim
  inj := by
    rintro (x | x | x) (y | y | y) h
    · exact congrArg Sum.inl (τ.inj h)
    all_goals first | exact x.elim | exact y.elim
  gsrc := fun x => τ.hsrc x
  gdst := fun x => τ.hdst x
  gcar := fun x p => by rw [hOfRelay_carried]; exact τ.hcar x p
  ancL := fun _ => []
  anc_nodup := fun _ => List.nodup_nil
  anc_ord := fun _ => trivial
  head_supp := fun c p h => (τ.L.chain c).fresh_supp 0 p h
  tdesc := fun t => t.elim
  mu := fun u => u.elim
  mu_len := fun u => u.elim
  ucar := fun u => u.elim
  tailL := fun _ => []
  tail_nodup := fun _ => List.nodup_nil
  tail_mem := fun u => u.elim
  tail_ord := fun _ => trivial
  udesc := fun u => u.elim
  silent := fun k hk => Or.inl (hcov k hk)

end ThmG

namespace Bridge7761
open ThmG BankBig BankTie BankPrem BankCallerGen

/-- **NON-VACUITY**: #7761 instantiates `big_mass_floor_G_disjoint` (no trunks, no tails; only Valid remains). -/
theorem kappa7761_lt_G (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  big_mass_floor_G_disjoint 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761) (fun _ => HS7761 hO7761)
    (R := fun _ => Fin 8) (Tr := fun _ => Empty) (Tu := fun _ => Empty) (fun _ => ofChainTieG τ7761 hcov7761G)
    (fun _ => by simp) (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy)
    (fun _ r r' _ => by simp [ofChainTieG]) (fun _ r r' _ => by simp [ofChainTieG])
    (fun _ => fun e : Empty => e.elim) (fun _ => fun e : Empty => e.elim)
    (fun _ => gflow7761) (fun _ => le_of_eq gW7761.symm) κ hκ0 hκ1 hV

end Bridge7761

#print axioms ThmG.GLayout.rows
#print axioms ThmG.GLayout.fold_bounds
#print axioms ThmG.GLayout.decoupled
#print axioms ThmG.GLayout.mass_ge_56_comp
#print axioms ThmG.GLayout.mass_ge_56_disjoint
#print axioms ThmG.big_mass_floor_G
#print axioms ThmG.big_mass_floor_G_disjoint
#print axioms Bridge7761.kappa7761_lt_G

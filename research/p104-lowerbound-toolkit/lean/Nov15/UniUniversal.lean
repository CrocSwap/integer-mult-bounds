/-
UniUniversal (lane UNI-L6, Nov 19).  ONE theorem for both construction classes:

  `kappa_lt_universal : Crossing k κ → κ < k.kbar`        (k = .w7113 : .0093453742,  k = .family : .00952721)
  `kappa_lt_universal_max : Crossing k κ → κ < .00952721`  (one constant, the max of the two)

`Crossing k κ` (inductive, every field pinned to the construction; no free bridge objects):
* `word`       : 17 legal traces under ANY WordModel caller with the #7113 ports (Ports7113) and 96 D ports (DCount),
                 end states Words + the verifier clauses (FramesSubsp, ChartsSubsp, OwnedNested); the graph used is
                 THE fold `foldBanked7113 … (h i) …` (UNI-L2B); Valid is the WORD's Theorem-K crossing against the #7113
                 block: cdat P + Σ wordPaid ≤ cdat T + Σ_helpers gc(climb)  (no banked object in it).
* `banked7113` : 17 banked graphs under the #7113 block (T = Tcal, P = Pcal), Valid as BankPrem.Valid.
* `family`     : K banked graphs under any CallerGen-family block (sign form hTP) — #7761, #7786, … — BankPrem.Valid.
Each call further carries HSContract and the two decoder halves of X = D + R (UniOwnedBank.excess_split_bank):
* `DHalf G` (D ≥ 56), evidence: a unified layout + per-component OTI discharges (BankUnify.mass_ge_56_disch), a unified
  layout with disjoint ancestor/tail lists (mass_ge_56_disjoint), or the fold tables (`FoldsP`, the named L1 fold
  equality, + a decided table sum).
* `RHalf G` (R ≥ 56), evidence: `trans` (UniTrans.TransWitness: owned-rise witness with a unified layout, NAMED),
  `balance` (climb + D ≤ A, the NoFlow W ≥ 0 route; with D ≥ 56 gives R ≥ D ≥ 56), or the fold tables.
Core: `kappa_of_cert_dep` = BankBanner.bank_kappa_lt_banner_of_cert with per-call field/bank TYPES (17 words fold to
graphs with different bank counts) and X ≥ 112 directly.
Instances: #7761 (family, layout + balance: only Valid remains), t7669 and w_s4 (word, caller7113 with Hl = Fin 1101,
Ow = Fin 68; D and R from the fold tables; remaining: per-call Folds (L1), HSContract, word Valid).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.NoFlowA
import Nov15.UniOwnedBank
import Nov15.UniFold7113Inst
import Nov15.UniUniversalWs4Data
import Nov15.UniTrans

set_option linter.unusedSectionVars false

namespace UniUniversal
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankMassF BankFitHS
  BankCallerGen UniOwnedBank NoFlow UniWC

/-! ## 1. core: per-call types, X ≥ 112 -/

theorem kappa_of_cert_dep (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : 46726871 / 5000000000 ≤ kbar)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i)) (hc : ∀ i, HSContract (G i).N)
    (hX : ∀ i, 112 ≤ excess (G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) P + ∑ i, ∑ k, BankPrem.specInvoice (G i) (1 - κ) k ≤
      cdat (1 - κ) T + ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc' := hcert κ hge hκ1.le
  simp only at hc'
  have hb := UniBud.cert κ (by linarith) hκ1.le
  unfold UniBud.FceilBank at hb
  have hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ (1 - κ)) := by
    have hz : (0:ℝ) ^ (1 - κ) = 0 := Real.zero_rpow (by linarith)
    simp only [c1', cc]
    norm_num [hz]
    linarith
  have each : ∀ i, 400 * (8:ℝ) ^ (1 - κ) + 112 * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      + 104 * (1 + (7:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      ≤ ∑ k, BankPrem.specInvoice (G i) (1 - κ) k - helperCredit (G i).N (1 - κ) (G i).Mn := fun i => by
    have hXi : (112 : ℝ) ≤ (excess (G i) : ℝ) := by exact_mod_cast hX i
    have := price_hsX (G i) (hc i) (s := 1 - κ) (by linarith) (by linarith) hbud 112 hXi _
      (fun k => BankPrem.bankPrice_le_specInvoice (G i) (by linarith) k)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  linarith

/-! ## 2. fold tables, parametric in the data (one structure for every word) -/

section tables
variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- NAMED L1 fold equality, data-parametric: G's banks / fields are the word's MOVEs / public registers and its chart
heights are the packed tables (hs, hd: bank src/dst; fi, ff: field birth/final).  UniWC.Folds = FoldsP at t7669's data. -/
structure FoldsP (G : BankedGraph ℚ Fld Bank) (nb nf hs hd fi ff : ℕ) where
  eB : Bank ≃ Fin nb
  eF : Fld ≃ Fin nf
  hsrc : ∀ k, ht (G.N.src k) = nib hs (eB k)
  hdst : ∀ k, ht (G.N.dst k) = nib hd (eB k)
  hini : ∀ f, ht (G.N.A f) = nib fi (eF f)
  hfin : ∀ f, ht (G.N.B f) = nib ff (eF f)

def ofFolds {G : BankedGraph ℚ Fld Bank} (F : Folds G) :
    FoldsP G T7669Data.NB T7669Data.NF T7669Data.HS T7669Data.HD T7669Data.FI T7669Data.FF :=
  ⟨F.eB, F.eF, F.hsrc, F.hdst, F.hini, F.hfin⟩

variable {G : BankedGraph ℚ Fld Bank} {nb nf hs hd fi ff : ℕ}

theorem sum_bankP (F : FoldsP G nb nf hs hd fi ff) (g : ℕ → ℕ → ℕ) (hg : g 0 0 = 0) (d : ℕ)
    (h1 : hs < 16 ^ nb) (h2 : hd < 16 ^ nb) (hn : nb ≤ 2 ^ d) :
    ∑ k, g (nib hs (F.eB k)) (nib hd (F.eB k)) = tsum g hs hd d 0 := by
  rw [Fintype.sum_equiv F.eB _ (fun j : Fin nb => g (nib hs j) (nib hd j)) (fun k => rfl),
    Fin.sum_univ_eq_sum_range (fun i => g (nib hs i) (nib hd i)) nb]
  exact sum_range_tsum g hg hs hd nb d h1 h2 hn

theorem descMassP (F : FoldsP G nb nf hs hd fi ff) (d : ℕ) (h1 : hs < 16 ^ nb) (h2 : hd < 16 ^ nb)
    (hn : nb ≤ 2 ^ d) : descMass G = (tsum gD hs hd d 0 : ℤ) := by
  unfold descMass
  have e : ∀ k, max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 = ((gD (nib hs (F.eB k)) (nib hd (F.eB k)) : ℕ) : ℤ) := by
    intro k; rw [F.hsrc, F.hdst]; unfold gD; omega
  rw [Finset.sum_congr rfl fun k _ => e k, ← Nat.cast_sum, sum_bankP F gD rfl d h1 h2 hn]

theorem hostedRiseP (F : FoldsP G nb nf hs hd fi ff) (d d' : ℕ) (h1 : hs < 16 ^ nb) (h2 : hd < 16 ^ nb)
    (hn : nb ≤ 2 ^ d) (h3 : fi < 16 ^ nf) (h4 : ff < 16 ^ nf) (hn' : nf ≤ 2 ^ d') :
    hostedRise G = (tsum gA hs hd d 0 : ℤ) - tsum gA fi ff d' 0 := by
  unfold hostedRise
  have e1 : ∀ k, max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0 = ((gA (nib hs (F.eB k)) (nib hd (F.eB k)) : ℕ) : ℤ) := by
    intro k; rw [F.hsrc, F.hdst]; unfold gA; omega
  have e2 : ∀ f, (G.cl f : ℤ) = ((gA (nib fi (F.eF f)) (nib ff (F.eF f)) : ℕ) : ℤ) := by
    intro f
    have := (G.climb f).2
    have a := F.hini f; have b := F.hfin f
    simp only [ht] at a b
    unfold gA; omega
  rw [Finset.sum_congr rfl fun k _ => e1 k, Finset.sum_congr rfl fun f _ => e2 f, ← Nat.cast_sum, ← Nat.cast_sum,
    sum_bankP F gA rfl d h1 h2 hn,
    Fintype.sum_equiv F.eF _ (fun j : Fin nf => gA (nib fi j) (nib ff j)) (fun f => rfl),
    Fin.sum_univ_eq_sum_range (fun i => gA (nib fi i) (nib ff i)) nf,
    sum_range_tsum gA rfl fi ff nf d' h3 h4 hn']

end tables

/-! ## 3. the two decoder halves as evidence types -/

section halves
open BankUnify DecoderWall ChainRow BankTie BankBig ThmG
variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- evidence for the live half D ≥ 56. -/
inductive DHalf (G : BankedGraph ℚ Fld Bank) : Prop
  /-- unified layout (≤ 8 pieces) + per-component OTI discharges (Theorem G / layout mass). -/
  | layout {R Tr Tu Tz : Type} [Fintype R] [Fintype Tr] [Fintype Tu] [Fintype Tz] [DecidableEq Tr] [DecidableEq Tu]
      (Λ : ULayout G R Tr Tu Tz) (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
      (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p))
      (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), DecoderWall.dot (DF.lq s) y = 0)
      (h8 : Λ.pieces ≤ 8) {C D : Type} [Fintype C] [DecidableEq C] [Fintype D] [DecidableEq D]
      (cr : R → C) (ct : Tr → C) (dr : R → D) (du : Tu → D)
      (hWc : ∀ c, Λ.DischW cr ct c) (hUc : ∀ d, Λ.DischU dr du d)
  /-- unified layout with pairwise-disjoint ancestor / tail lists (no OTI hypothesis). -/
  | layoutDisjoint {R Tr Tu Tz : Type} [Fintype R] [Fintype Tr] [Fintype Tu] [Fintype Tz] [DecidableEq Tr]
      [DecidableEq Tu] (Λ : ULayout G R Tr Tu Tz) (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
      (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p))
      (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), DecoderWall.dot (DF.lq s) y = 0)
      (h8 : Λ.pieces ≤ 8)
      (hdW : ∀ r r', r ≠ r' → Disjoint (Λ.ancL r).toFinset (Λ.ancL r').toFinset)
      (hdU : ∀ r r', r ≠ r' → Disjoint (Λ.tailL r).toFinset (Λ.tailL r').toFinset)
  /-- fold tables (named L1 fold equality FoldsP) + decided table sum. -/
  | tables {nb nf hs hd fi ff : ℕ} (F : FoldsP G nb nf hs hd fi ff) (d : ℕ) (h1 : hs < 16 ^ nb) (h2 : hd < 16 ^ nb)
      (hn : nb ≤ 2 ^ d) (h56 : 56 ≤ tsum gD hs hd d 0)

/-- evidence for the hosted half R ≥ 56 (R = A - Σc, X = D + R). -/
inductive RHalf (G : BankedGraph ℚ Fld Bank) : Prop
  /-- NAMED hosted Wall56: a transpose witness Gt injected into G's owned banks carrying a unified layout
  (UniTrans.TransWitness; R(G) = D(Gᵀ) is false, so the witness is the corrected route). -/
  | trans (T : UniTrans.TransWitness G)
  /-- NoFlow balance climb + D ≤ A (W ≥ 0): R ≥ D. -/
  | balance (hAD : climbG G + descMass G ≤ ascMass G)
  /-- fold tables + decided table sums. -/
  | tables {nb nf hs hd fi ff : ℕ} (F : FoldsP G nb nf hs hd fi ff) (d d' : ℕ) (h1 : hs < 16 ^ nb)
      (h2 : hd < 16 ^ nb) (hn : nb ≤ 2 ^ d) (h3 : fi < 16 ^ nf) (h4 : ff < 16 ^ nf) (hn' : nf ≤ 2 ^ d')
      (h56 : 56 + tsum gA fi ff d' 0 ≤ tsum gA hs hd d 0)

theorem DHalf.mass {G : BankedGraph ℚ Fld Bank} (H : DHalf G) : 56 ≤ descMass G := by
  cases H with
  | layout Λ cs hC hin hout h8 cr ct dr du hWc hUc => exact Λ.mass_ge_56_disch cs hC hin hout h8 cr ct dr du hWc hUc
  | layoutDisjoint Λ cs hC hin hout h8 hdW hdU => exact Λ.mass_ge_56_disjoint cs hC hin hout h8 hdW hdU
  | tables F d h1 h2 hn h56 => rw [descMassP F d h1 h2 hn]; exact_mod_cast h56

theorem hostedRise_eq_asc (G : BankedGraph ℚ Fld Bank) : hostedRise G = ascMass G - climbG G := rfl

theorem RHalf.rise {G : BankedGraph ℚ Fld Bank} (hD : 56 ≤ descMass G) (H : RHalf G) : 56 ≤ hostedRise G := by
  cases H with
  | trans T => exact T.hR
  | balance hAD => rw [hostedRise_eq_asc]; linarith
  | tables F d d' h1 h2 hn h3 h4 hn' h56 =>
    rw [hostedRiseP F d d' h1 h2 hn h3 h4 hn']; omega

/-- X = D + R ≥ 112 from the two halves. -/
theorem excess_of_halves {G : BankedGraph ℚ Fld Bank} (hD : DHalf G) (hR : RHalf G) : 112 ≤ excess G := by
  have a := hD.mass
  have b := hR.rise a
  rw [excess_split_bank]; omega

end halves

/-! ## 4. the class and the head theorem -/

/-- which certified caller rung applies. -/
inductive Kind | w7113 | family

noncomputable def Kind.kbar : Kind → ℝ
  | .w7113 => 93453742 / 10000000000
  | .family => 952721 / 100000000

open WordModel Uni in
/-- **the universal class**: κ is a crossing of one of the constructions below. -/
inductive Crossing : Kind → ℝ → Prop
  /-- 17 legal WORDS under a #7113 caller, through their folds. -/
  | word {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow] [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]
      (cl : WordModel.Caller Pt) (hP : UniFold7113.Ports7113 cl) (hDc : DCount cl)
      (tr : Fin 17 → Uni.Trace (Reg Pt Hl Ow)) (h : ∀ i, Uni.Legal (pub cl) (tr i))
      (hw : ∀ i, Word cl (exec (tr i))) (hfr : ∀ i, FramesSubsp (exec (tr i)))
      (hcs : ∀ i, ChartsSubsp (exec (tr i))) (hn : ∀ i, OwnedNested (exec (tr i)))
      (hc : ∀ i, HSContract (foldS (h i)))
      (hD : ∀ i, DHalf (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
      (hR : ∀ i, RHalf (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
      (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
      (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid cl (exec (tr i)) specPrice (1 - κ) ≤
        cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r)) :
      Crossing .w7113 κ
  /-- 17 banked graphs under the #7113 block. -/
  | banked7113 {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]
      (c : BankPrem.Caller ℚ Fld Bank 17) (hT : c.T = Tcal) (hP : c.P = Pcal)
      (hc : ∀ i, HSContract (c.G i).N) (hD : ∀ i, DHalf (c.G i)) (hR : ∀ i, RHalf (c.G i))
      (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
      (hV : BankPrem.Valid c (1 - κ) (fun i k => BankPrem.specInvoice (c.G i) (1 - κ) k)) :
      Crossing .w7113 κ
  /-- K banked graphs under a CallerGen-family block (#7761, #7786, …). -/
  | family {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]
      (K : ℕ) (hK : 0 < K) (c : BankPrem.Caller ℚ Fld Bank K)
      (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
      (hc : ∀ i, HSContract (c.G i).N) (hD : ∀ i, DHalf (c.G i)) (hR : ∀ i, RHalf (c.G i))
      (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
      (hV : BankPrem.Valid c (1 - κ) (fun i k => BankPrem.specInvoice (c.G i) (1 - κ) k)) :
      Crossing .family κ

theorem cert7113 : Cert (fun s => cdat s Tcal - cdat s Pcal -
    ((17 : ℕ) : ℝ) * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (93453742 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113.cert7113_X112HS t h1 h2
  push_cast
  linarith

theorem valid_dep {L : ℕ} {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]
    (c : BankPrem.Caller ℚ Fld Bank L) (s : ℝ)
    (hV : BankPrem.Valid c s (fun i k => BankPrem.specInvoice (c.G i) s k)) :
    cdat s c.P + ∑ i, ∑ k, BankPrem.specInvoice (c.G i) s k ≤ cdat s c.T + ∑ i, helperCredit (c.G i).N s (c.G i).Mn :=
  hV

/-- **`kappa_lt_universal`**: every crossing of the class lies below its caller's certified rung. -/
theorem kappa_lt_universal (k : Kind) (κ : ℝ) (H : Crossing k κ) : κ < k.kbar := by
  cases H with
  | word cl hP hDc tr h hw hfr hcs hn hc hD hR κ hκ0 hκ1 hV =>
    show κ < 93453742 / 10000000000
    have hσ : (1 - κ) ≠ 0 := by intro h0; linarith
    refine kappa_of_cert_dep 17 Tcal Pcal _ (by norm_num) cert7113
      (fun i => UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)) hc
      (fun i => excess_of_halves (hD i) (hR i)) κ hκ0 hκ1 ?_
    have e1 : ∀ i, ∑ k, BankPrem.specInvoice (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))
        (1 - κ) k = Uni.wordPaid cl (Uni.exec (tr i)) WordModel.specPrice (1 - κ) := fun i =>
      UniFold7113.foldBanked7113_paid cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i) (1 - κ)
    have e2 : ∀ i, helperCredit (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).N (1 - κ)
        (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).Mn =
        ∑ r ∈ (WordModel.helpers : Finset (WordModel.Reg _ _ _)), gc (1 - κ) (WordModel.hcred (Uni.exec (tr i)) r) :=
      fun i => Uni.fold_credit cl (h i) (hw i) (hfr i) hσ
    simp only [e1, e2]
    exact hV
  | banked7113 c hT hP hc hD hR κ hκ0 hκ1 hV =>
    show κ < 93453742 / 10000000000
    have hv := valid_dep c _ hV
    rw [hT, hP] at hv
    exact kappa_of_cert_dep 17 Tcal Pcal _ (by norm_num) cert7113 c.G hc
      (fun i => excess_of_halves (hD i) (hR i)) κ hκ0 hκ1 hv
  | family K hK c hTP hc hD hR κ hκ0 hκ1 hV =>
    show κ < 952721 / 100000000
    exact kappa_of_cert_dep K c.T c.P _ (by norm_num) (cert_gen K hK c.T c.P hTP) c.G hc
      (fun i => excess_of_halves (hD i) (hR i)) κ hκ0 hκ1 (valid_dep c _ hV)

/-- one constant for the whole class: κ < .00952721 (= max of the two rungs). -/
theorem kappa_lt_universal_max (k : Kind) (κ : ℝ) (H : Crossing k κ) : κ < 952721 / 100000000 := by
  have := kappa_lt_universal k κ H
  cases k <;> simp only [Kind.kbar] at this <;> linarith

/-! ## 5. instances (non-vacuity) -/

section inst
open Bridge7761 BankUnify ThmG BankBig BankTie

/-- **#7761** (family): 8 chains as unified groups (layoutDisjoint) + NoFlow balance (A 9721 ≥ Σc 9665 + D 56);
only Valid remains. -/
theorem kappa7761_universal (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : BankPrem.Valid (caller7761 hO7761) (1 - κ)
      (fun i k => BankPrem.specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  kappa_lt_universal .family κ <| Crossing.family 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761)
    (fun _ => HS7761 hO7761)
    (fun i => DHalf.layoutDisjoint (ofGLayout (ofChainTieG τ7761 hcov7761G) len7761_pos) Bridge7761.cc (hC7761 i)
      (fun p => hin7761 p) (fun s y hy => hout7761 s y hy) ((ofGLayout_pieces _ _).trans_le (by simp))
      (fun r r' _ => by simp [ofGLayout, ofChainTieG]) (fun r r' _ => by simp [ofGLayout, ofChainTieG]))
    (fun _ => RHalf.balance ad7761) κ hκ0 hκ1 hV

end inst

section words
open WordModel Uni UniFold7113

/-- **t7669** (word): 17 legal traces under caller7113 (Hl = Fin 1101, Ow = Fin 68) whose folds are t7669's tables
(Folds, the named L1 fold equality); D = 56 and R = 10943 - 10887 = 56 from the tables.  Remaining: Folds, HSContract,
the word's Valid. -/
theorem kappa_t7669_universal (tr : Fin 17 → Uni.Trace (Reg (Fin 104) (Fin 1101) (Fin 68)))
    (h : ∀ i, Uni.Legal (pub caller7113) (tr i)) (hw : ∀ i, Word caller7113 (exec (tr i)))
    (hfr : ∀ i, FramesSubsp (exec (tr i))) (hcs : ∀ i, ChartsSubsp (exec (tr i)))
    (hn : ∀ i, OwnedNested (exec (tr i)))
    (F : ∀ i, Folds (foldBanked7113 caller7113 ports_caller7113 dcount_caller7113 (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (hc : ∀ i, HSContract (foldS (h i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid caller7113 (exec (tr i)) specPrice (1 - κ) ≤
      cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg (Fin 104) (Fin 1101) (Fin 68))),
        gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 :=
  kappa_lt_universal .w7113 κ <| Crossing.word caller7113 ports_caller7113 dcount_caller7113 tr h hw hfr hcs hn hc
    (fun i => DHalf.tables (ofFolds (F i)) 13 HS_lt HD_lt (by decide) (le_of_eq D_data.symm))
    (fun i => RHalf.tables (ofFolds (F i)) 13 11 HS_lt HD_lt (by decide) FI_lt FF_lt (by decide)
      (by rw [A_data, C_data] <;> norm_num))
    κ hκ0 hκ1 hV

/-- **w_s4** (word): same caller and register types; folds are w_s4's tables (UniUniversalWs4Data: D 56,
R = 10942 - 10886 = 56).  Remaining: FoldsP at the w_s4 tables, HSContract, the word's Valid. -/
theorem kappa_ws4_universal (tr : Fin 17 → Uni.Trace (Reg (Fin 104) (Fin 1101) (Fin 68)))
    (h : ∀ i, Uni.Legal (pub caller7113) (tr i)) (hw : ∀ i, Word caller7113 (exec (tr i)))
    (hfr : ∀ i, FramesSubsp (exec (tr i))) (hcs : ∀ i, ChartsSubsp (exec (tr i)))
    (hn : ∀ i, OwnedNested (exec (tr i)))
    (F : ∀ i, FoldsP (foldBanked7113 caller7113 ports_caller7113 dcount_caller7113 (h i) (hw i) (hfr i) (hcs i) (hn i))
      Ws4Data.NB Ws4Data.NF Ws4Data.HS Ws4Data.HD Ws4Data.FI Ws4Data.FF)
    (hc : ∀ i, HSContract (foldS (h i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid caller7113 (exec (tr i)) specPrice (1 - κ) ≤
      cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg (Fin 104) (Fin 1101) (Fin 68))),
        gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 :=
  kappa_lt_universal .w7113 κ <| Crossing.word caller7113 ports_caller7113 dcount_caller7113 tr h hw hfr hcs hn hc
    (fun i => DHalf.tables (F i) 13 Ws4Data.HS_lt Ws4Data.HD_lt Ws4Data.NB_le (le_of_eq Ws4Data.D_data.symm))
    (fun i => RHalf.tables (F i) 13 11 Ws4Data.HS_lt Ws4Data.HD_lt Ws4Data.NB_le Ws4Data.FI_lt Ws4Data.FF_lt
      Ws4Data.NF_le (by rw [Ws4Data.A_data, Ws4Data.C_data] <;> norm_num))
    κ hκ0 hκ1 hV

end words

end UniUniversal

#print axioms UniUniversal.kappa_of_cert_dep
#print axioms UniUniversal.kappa_lt_universal
#print axioms UniUniversal.kappa_lt_universal_max
#print axioms UniUniversal.kappa7761_universal
#print axioms UniUniversal.kappa_t7669_universal
#print axioms UniUniversal.kappa_ws4_universal

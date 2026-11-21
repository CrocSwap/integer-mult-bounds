/-
UniWordChain (lane UNI-L4, Nov 19).  Stage L4 WORDCHAIN: `kappa_t7669_lt_banner : κ < .0093453742` for any caller that is 17 folded copies of t7669
against the 7113 caller block.  Pieces:
  UniWordChainA : kernel data checks on the folded word (D = 56, A = 10943, climb = 10887, 23 descents = 8 pure chains, ties, shapes, cover).
  here          : `Folds G` = the NAMED L1 HYPOTHESIS (heights of the banked graph's charts are the folded word's: the fold-equality theorem of UNI-L0L1,
                  not yet built), `descMass_eq`, `excess_eq` (⟹ D ≥ 56 and X ≥ 2D from the data alone), the budget-extended rung
                  `uni_kappa_of_cert` (BankBanner.bank_kappa_lt_banner_of_cert with the m1 budget re-certified down to .00934537: UniBud),
                  and the assembly with UniCaller7113.cert7113_X112HS.
Remaining hypotheses of the head theorem: `Folds` (L1), `HSContract` (L1 + callerFacts7113), Valid (SPEC crossing).  Kernel only.
-/
import Nov15.UniWordChainA
import Nov15.UniBud
import Nov15.UniCaller7113
import Nov15.BankBanner
import Nov15.BankPrem

namespace UniWC
open Finset Module BankNC0 BankWireC BankWireD BankHelp BankFit SafeRungsPrice BankMassF BankFitHS BankBanner BankPrem T7669Data

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- NAMED L1 HYPOTHESIS: the banked graph G is the fold of t7669: its banks are the 6157 MOVEs, its fields the 1501 public registers, and chart
heights are the folded dimensions (src / dst per bank, initial / final per field). -/
structure Folds (G : BankedGraph ℚ Fld Bank) where
  eB : Bank ≃ Fin NB
  eF : Fld ≃ Fin NF
  hsrc : ∀ k, ht (G.N.src k) = nib HS (eB k)
  hdst : ∀ k, ht (G.N.dst k) = nib HD (eB k)
  hini : ∀ f, ht (G.N.A f) = nib FI (eF f)
  hfin : ∀ f, ht (G.N.B f) = nib FF (eF f)

variable {G : BankedGraph ℚ Fld Bank}

theorem sum_bank (F : Folds G) (g : ℕ → ℕ → ℕ) (hg : g 0 0 = 0) (d : ℕ) (hd : NB ≤ 2 ^ d) :
    ∑ k, g (nib HS (F.eB k)) (nib HD (F.eB k)) = tsum g HS HD d 0 := by
  rw [Fintype.sum_equiv F.eB _ (fun j : Fin NB => g (nib HS j) (nib HD j)) (fun k => rfl),
    Fin.sum_univ_eq_sum_range (fun i => g (nib HS i) (nib HD i)) NB]
  exact sum_range_tsum g hg HS HD NB d HS_lt HD_lt hd

theorem descMass_eq (F : Folds G) : descMass G = 56 := by
  unfold descMass
  have h1 : ∀ k, max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 = ((gD (nib HS (F.eB k)) (nib HD (F.eB k)) : ℕ) : ℤ) := by
    intro k; rw [F.hsrc, F.hdst]; unfold gD; omega
  rw [Finset.sum_congr rfl fun k _ => h1 k, ← Nat.cast_sum, sum_bank F gD rfl 13 (by decide), D_data]
  rfl

theorem excess_eq (F : Folds G) : excess G = 112 := by
  unfold excess
  have h1 : ∀ k, (dh (ht (G.N.src k)) (ht (G.N.dst k)) : ℤ) =
      ((gD (nib HS (F.eB k)) (nib HD (F.eB k)) + gA (nib HS (F.eB k)) (nib HD (F.eB k)) : ℕ) : ℤ) := by
    intro k; rw [F.hsrc, F.hdst]; unfold dh gD gA; omega
  have h2 : ∀ f, (G.cl f : ℤ) = ((gA (nib FI (F.eF f)) (nib FF (F.eF f)) : ℕ) : ℤ) := by
    intro f
    have := (G.climb f).2
    have a := F.hini f; have b := F.hfin f
    simp only [ht] at a b
    unfold gA; omega
  rw [Finset.sum_congr rfl fun k _ => h1 k, Finset.sum_congr rfl fun f _ => h2 f, ← Nat.cast_sum, ← Nat.cast_sum]
  rw [Finset.sum_add_distrib, sum_bank F gD rfl 13 (by decide), sum_bank F gA rfl 13 (by decide), D_data, A_data]
  rw [Fintype.sum_equiv F.eF _ (fun j : Fin NF => gA (nib FI j) (nib FF j)) (fun f => rfl),
    Fin.sum_univ_eq_sum_range (fun i => gA (nib FI i) (nib FF i)) NF,
    sum_range_tsum gA rfl FI FF NF 11 FI_lt FF_lt (by decide), C_data]
  norm_num

/-- the mass floor for the folded word: D = 56 (D ≥ 56) and X = 2 D, from the data alone. -/
theorem word_mass (F : Folds G) : 56 ≤ descMass G ∧ 2 * descMass G ≤ excess G := by
  rw [descMass_eq F, excess_eq F]; norm_num

/-- BankBanner.bank_kappa_lt_banner_of_cert with the m1 budget certified from kbar = .0093453742 (UniBud) instead of .009526. -/
theorem uni_kappa_of_cert (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : kbar = 93453742 / 10000000000)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    (G : Fin L → BankedGraph ℚ Fld Bank) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i)) (hXD : ∀ i, 2 * descMass (G i) ≤ excess (G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin L → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) T - cdat (1 - κ) P) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc' := hcert κ hge hκ1.le
  simp only at hc'
  have hb := UniBud.cert κ (by rw [hk] at hge; norm_num at hge ⊢; linarith) hκ1.le
  unfold UniBud.FceilBank at hb
  have hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ (1 - κ)) := by
    have hz : (0:ℝ) ^ (1 - κ) = 0 := Real.zero_rpow (by linarith)
    simp only [c1', cc]
    norm_num [hz]
    linarith
  have each : ∀ i, 400 * (8:ℝ) ^ (1 - κ) + 112 * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      + 104 * (1 + (7:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      ≤ ∑ k, paid i k - helperCredit (G i).N (1 - κ) (G i).Mn := fun i => by
    have := price_hsX (G i) (hc i) (s := 1 - κ) (by linarith) (by linarith) hbud 112
      (excess_ge_112 (G i) (hD i) (hXD i)) _ (hpaid i)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  linarith

/-- **`kappa_t7669_lt_banner`**: 17 copies of the folded t7669 under the #7113 caller block (Tcal / Pcal) cannot cross at κ ≥ .0093453742.
Hypotheses: `Folds` (L1 fold equality, named), HSContract (L1 + callerFacts7113), Valid (the SPEC invoice crossing). -/
theorem kappa_t7669_lt_banner (c : Caller ℚ Fld Bank 17) (hT : c.T = Tcal) (hP : c.P = Pcal)
    (hF : ∀ i, Folds (c.G i)) (hc : ∀ i, HSContract (c.G i).N)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 93453742 / 10000000000 := by
  have hcert : Cert (fun s => cdat s Tcal - cdat s Pcal -
      ((17 : ℕ) : ℝ) * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (93453742 / 10000000000) := by
    intro t h1 h2
    have := UniCaller7113.cert7113_X112HS t h1 h2
    push_cast
    linarith
  have hcal := hcaller_of_valid c (1 - κ) _ hV
  rw [hT, hP] at hcal
  exact uni_kappa_of_cert 17 Tcal Pcal _ rfl hcert c.G hc (fun i => (word_mass (hF i)).1)
    (fun i => (word_mass (hF i)).2) κ hκ0 hκ1 _ (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k) hcal

end UniWC
#print axioms UniWC.descMass_eq
#print axioms UniWC.excess_eq
#print axioms UniWC.uni_kappa_of_cert
#print axioms UniWC.kappa_t7669_lt_banner

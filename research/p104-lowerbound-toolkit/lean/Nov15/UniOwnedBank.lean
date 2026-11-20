/-
UniOwnedBank (lane UNI-L5 OWNEDBAL, Nov 19).  Route (b) on the banked side, plugged into the L4 word chain.
  hostedRise G = Σ_banks max(ht dst - ht src, 0) - Σ_fields cl   (A - Σc: the hosted half; through the fold of a word
                 = owned ascent mass R, UniOwnedBal.excess_split_word)
  excess_split_bank : excess G = descMass G + hostedRise G   (exact, every banked graph; W = hostedRise - descMass)
  excess_ge_112_halves : D ≥ 56 → R ≥ 56 → X ≥ 112            (replaces X ≥ 2D, i.e. W ≥ 0, which is false for words)
  uni_kappa_of_halves : UniWC.uni_kappa_of_cert with hXD replaced by the hosted half hR.
  kappa_word_lt_banner : ANY 17 banked graphs under the #7113 block with D ≥ 56 (Theorem G) and R ≥ 56 (transposed
                         Theorem G) ⟹ κ < .0093453742.  No sign of W, no fold data.
  hostedRise_eq / kappa_t7669_lt_banner_halves : t7669 instance (R = 10943 - 10887 = 56 from the fold tables).
Kernel only.
-/
import Nov15.UniWordChain

namespace UniOwnedBank
open Finset Module BankNC0 BankWireC BankWireD BankHelp BankFit SafeRungsPrice BankMassF BankFitHS BankBanner BankPrem
  T7669Data UniWC

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- hosted rise R = ascent mass - field climb (A - Σc). -/
noncomputable def hostedRise (G : BankedGraph ℚ Fld Bank) : ℤ :=
  ∑ k, max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0 - ∑ f, (G.cl f : ℤ)

/-- **excess split**: X = D + R on every banked graph. -/
theorem excess_split_bank (G : BankedGraph ℚ Fld Bank) : excess G = descMass G + hostedRise G := by
  unfold excess descMass hostedRise
  have : ∀ k, (dh (ht (G.N.src k)) (ht (G.N.dst k)) : ℤ) =
      max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 + max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0 := by
    intro k; unfold dh; omega
  rw [Finset.sum_congr rfl fun k _ => this k, Finset.sum_add_distrib]; ring

/-- the folded W is R - D. -/
theorem W_bank (G : BankedGraph ℚ Fld Bank) : excess G - 2 * descMass G = hostedRise G - descMass G := by
  rw [excess_split_bank]; ring

/-- **`excess_ge_112_halves`**: the two decoder halves give X ≥ 112; no sign of W. -/
theorem excess_ge_112_halves (G : BankedGraph ℚ Fld Bank) (hD : 56 ≤ descMass G) (hR : 56 ≤ hostedRise G) :
    (112 : ℝ) ≤ (excess G : ℝ) := by
  have : (112 : ℤ) ≤ excess G := by rw [excess_split_bank]; omega
  exact_mod_cast this

/-- UniWC.uni_kappa_of_cert with the X ≥ 2D (W ≥ 0) hypothesis replaced by the hosted half R ≥ 56. -/
theorem uni_kappa_of_halves (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : kbar = 93453742 / 10000000000)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    (G : Fin L → BankedGraph ℚ Fld Bank) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i)) (hR : ∀ i, 56 ≤ hostedRise (G i))
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
      (excess_ge_112_halves (G i) (hD i) (hR i)) _ (hpaid i)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  linarith

/-- **`kappa_word_lt_banner`**: any 17 banked graphs (folded words) under the #7113 caller block with the live half
D ≥ 56 (Theorem G) and the hosted half R ≥ 56 (transposed Theorem G) cannot cross at κ ≥ .0093453742.
Hypotheses: hD, hR (named halves), HSContract, Valid.  No W sign, no fold data. -/
theorem kappa_word_lt_banner (c : Caller ℚ Fld Bank 17) (hT : c.T = Tcal) (hP : c.P = Pcal)
    (hc : ∀ i, HSContract (c.G i).N)
    (hD : ∀ i, 56 ≤ descMass (c.G i)) (hR : ∀ i, 56 ≤ hostedRise (c.G i))
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
  exact uni_kappa_of_halves 17 Tcal Pcal _ rfl hcert c.G hc hD hR κ hκ0 hκ1 _
    (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k) hcal

variable {G : BankedGraph ℚ Fld Bank}

/-- t7669: R = A - Σc = 10943 - 10887 = 56 from the fold tables. -/
theorem hostedRise_eq (F : Folds G) : hostedRise G = 56 := by
  unfold hostedRise
  have h1 : ∀ k, max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0 = ((gA (nib HS (F.eB k)) (nib HD (F.eB k)) : ℕ) : ℤ) := by
    intro k; rw [F.hsrc, F.hdst]; unfold gA; omega
  have h2 : ∀ f, (G.cl f : ℤ) = ((gA (nib FI (F.eF f)) (nib FF (F.eF f)) : ℕ) : ℤ) := by
    intro f
    have := (G.climb f).2
    have a := F.hini f; have b := F.hfin f
    simp only [ht] at a b
    unfold gA; omega
  rw [Finset.sum_congr rfl fun k _ => h1 k, Finset.sum_congr rfl fun f _ => h2 f, ← Nat.cast_sum, ← Nat.cast_sum]
  rw [sum_bank F gA rfl 13 (by decide), A_data]
  rw [Fintype.sum_equiv F.eF _ (fun j : Fin NF => gA (nib FI j) (nib FF j)) (fun f => rfl),
    Fin.sum_univ_eq_sum_range (fun i => gA (nib FI i) (nib FF i)) NF,
    sum_range_tsum gA rfl FI FF NF 11 FI_lt FF_lt (by decide), C_data]
  norm_num

/-- t7669 through the halves route: same κ bound as UniWC.kappa_t7669_lt_banner, with D and R read off the fold. -/
theorem kappa_t7669_lt_banner_halves (c : Caller ℚ Fld Bank 17) (hT : c.T = Tcal) (hP : c.P = Pcal)
    (hF : ∀ i, Folds (c.G i)) (hc : ∀ i, HSContract (c.G i).N)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 93453742 / 10000000000 :=
  kappa_word_lt_banner c hT hP hc (fun i => by rw [descMass_eq (hF i)]) (fun i => by rw [hostedRise_eq (hF i)])
    κ hκ0 hκ1 hV

end UniOwnedBank
#print axioms UniOwnedBank.excess_split_bank
#print axioms UniOwnedBank.kappa_word_lt_banner
#print axioms UniOwnedBank.kappa_t7669_lt_banner_halves

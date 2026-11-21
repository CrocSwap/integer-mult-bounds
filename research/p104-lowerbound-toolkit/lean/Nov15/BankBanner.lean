/-
BankBanner (lane LEAN-BANNER, Nov 18).  D56-dir banked rung (UCEIL/bankd56 BD.md §5, bd2.log row X=112 Z=104) as ONE kernel theorem.
  descMass G  = Σ_banks max(ht src - ht dst, 0)                 (descent mass D, XBal.Model.D naming)
  excess G    = Σ_banks |ht dst - ht src| - Σ_fields cl          (excess mass X = paid mass net of field climb, XBal.Model.X)
  price_hsX   : per call, 400 g8 + X·D9 + 104 (g1 + g7 - g8) + helperCredit ≤ Σ paid   for ANY real X ≤ excess G
                (BankFitHS3.price_hs with the flag mass 28 replaced by the mass premise; HS molecules unchanged).
  bank_kappa_lt_banner_of_cert : any L-call caller + exact Cert of its X=112 HS ceiling (kbar ≥ 9526/10^6), D ≥ 56, X ≥ 2D ⟹ κ < kbar.
  bank_kappa_lt_banner : #7761's caller block (2048 calls, BankBannerCert) ⟹ κ < 2381707/250000000 = .009526828
                         (root .009526827724; .0095268 itself is below the root, so not certifiable).  Budget c1' ≥ 0 on
                         t ∈ [9526/10^6, 1]: BankBannerBud.
Premises: BankedGraph (BankFitA) + HSContract (BankFitHS1) + P-1S' (hpaid) + P-CALLER' (hcaller)
          + HYPOTHESES hD : 56 ≤ descMass (LEAN-CHAINROW target) and hXD : 2·descMass ≤ excess (LEAN-XBAL target).
Kernel only.
-/
import Nov15.BankFitHS3
import Nov15.BankBannerCert
import Nov15.BankBannerBud

namespace BankBanner
open Finset Module BankNC0 BankWireC BankWireD BankHelp BankFit SafeRungsPrice BankMassF BankFitHS

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- descent mass D of a banked graph. -/
noncomputable def descMass (G : BankedGraph K Fld Bank) : ℤ :=
  ∑ k, max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0

/-- excess mass X = Σ bank |Δh| - Σ field climb. -/
noncomputable def excess (G : BankedGraph K Fld Bank) : ℤ :=
  ∑ k, (dh (ht (G.N.src k)) (ht (G.N.dst k)) : ℤ) - ∑ f, (G.cl f : ℤ)

/-- per call: HS cuts + an arbitrary mass premise X ≤ excess. -/
theorem price_hsX (G : BankedGraph K Fld Bank) (hc : HSContract G.N) {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1)
    (hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ s)) (X : ℝ) (hX : X ≤ (excess G : ℝ))
    (paid : Bank → ℝ) (hpaid : ∀ k, bankPrice G s k ≤ paid k) :
    400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s) + 104 * (1 + (7:ℝ) ^ s - (8:ℝ) ^ s)
      + helperCredit G.N s G.Mn ≤ ∑ k, paid k := by
  classical
  set gg : ℕ → ℝ := fun d : ℕ => (d : ℝ) ^ s with hgg
  obtain ⟨p0, pm, pc⟩ := rpow_price hs0 hs1 10
  have h0 : gg 0 = 0 := p0
  have hcc : ∀ L, 2 ≤ L → L ≤ 8 → 0 ≤ cc gg L := by
    intro L h2 h8
    obtain ⟨j, rfl⟩ : ∃ j, L = j + 1 := ⟨L - 1, by omega⟩
    have := pc j (by omega)
    simp only [cc, hgg, Nat.add_sub_cancel]
    push_cast at this ⊢
    rw [show (j:ℝ) + 1 + 1 = j + 2 by ring]
    linarith
  have hD9 : 0 ≤ gg 9 - gg 8 := by have := pm 8 (by norm_num); simp only [hgg]; push_cast at this ⊢; linarith
  let bk : Bank → ℕ := fun k => dh (ht (G.N.src k)) (ht (G.N.dst k))
  let fl : Fld → ℕ := fun f => dh (ht (G.N.A f)) (ht (G.N.B f))
  have hbk : ∀ k, bk k ≤ 9 := fun k => by
    have := ht_le (G.N.src k); have := ht_le (G.N.dst k); simp only [bk, dh]; omega
  have hfl : ∀ f, fl f = G.cl f := fun f => by
    have := (G.climb f).2; simp only [fl, dh, ht]; omega
  have hfl9 : ∀ f, fl f ≤ 9 := fun f => by
    have := ht_le (G.N.A f); have := ht_le (G.N.B f); simp only [fl, dh]; omega
  have hmin := G.minors
  have m1 := castM M_m1 fl bk 106344 (by have h := mol_hs G.N hmin hc W_m1 M_m1 dec_m1; rw [sep_m1] at h; exact h)
  have m2 := castM M_m2 fl bk 2 (by have h := mol_hs G.N hmin hc W_m2 M_m2 dec_m2; rw [sep_m2] at h; exact h)
  have m3 := castM M_M3 fl bk 8 (by have h := mol_hs G.N hmin hc W_M3 M_M3 dec_M3; rw [sep_M3] at h; exact h)
  have m4 := castM M_m4 fl bk 1 (by have h := mol_hs G.N hmin hc W_m4 M_m4 dec_m4; rw [sep_m4] at h; exact h)
  have m5 := castM M_M5 fl bk 4 (by have h := mol_hs G.N hmin hc W_M5 M_M5 dec_M5; rw [sep_M5] at h; exact h)
  have m6 := castM M_M6 fl bk 28 (by have h := mol_hs G.N hmin hc W_M6 M_M6 dec_M6; rw [sep_M6] at h; exact h)
  have m7 := castM M_M7 fl bk 24 (by have h := mol_hs G.N hmin hc W_M7 M_M7 dec_M7; rw [sep_M7] at h; exact h)
  have m8 := castM M_m8 fl bk 0 (by have h := mol_hs G.N hmin hc W_m8 M_m8 dec_m8; rw [sep_m8] at h; exact h)
  push_cast at m1 m2 m3 m4 m5 m6 m7 m8
  have hmix := mix_sum gg fl bk hbud hcc m1 m2 m3 m4 m5 m6 m7 (by simpa using m8)
  rw [sep_eq gg h0] at hmix
  -- mass: Σ dh ≥ Σ cl + X  (premise)
  have hexR : (excess G : ℝ) = ∑ k, (bk k : ℝ) - ∑ f, (G.cl f : ℝ) := by
    simp only [excess, bk]; push_cast; rfl
  have hmassR : (∑ f, (G.cl f : ℝ)) + X ≤ ∑ k, (bk k : ℝ) := by rw [hexR] at hX; linarith
  have hbank : ∑ k, gg (bk k) = ∑ k, mix gg (bk k) + (gg 9 - gg 8) * ∑ k, (bk k : ℝ) := by
    rw [mul_sum, ← sum_add_distrib]; exact sum_congr rfl (fun k _ => mix_eq gg h0 _ (hbk k))
  have hfield : ∑ f, gg (fl f) = ∑ f, mix gg (fl f) + (gg 9 - gg 8) * ∑ f, (G.cl f : ℝ) := by
    rw [mul_sum, ← sum_add_distrib]
    exact sum_congr rfl (fun f _ => by rw [mix_eq gg h0 _ (hfl9 f), hfl f])
  have hsplit : ∑ f, gg (fl f) = 400 * (8:ℝ) ^ s + helperCredit G.N s G.Mn := by
    rw [← Finset.sum_add_sum_compl G.Mn]
    congr 1
    · rw [Finset.sum_congr rfl (fun f hf' => by rw [hfl f, G.main8 f hf'])]
      simp [Finset.sum_const, G.card, hgg]
  have hpay : ∑ k, gg (bk k) ≤ ∑ k, paid k := sum_le_sum (fun k _ => hpaid k)
  have mD := mul_le_mul_of_nonneg_left hmassR hD9
  have g1 : gg 1 = 1 := by simp [hgg]
  have g7 : gg 7 = (7:ℝ) ^ s := by simp [hgg]
  have g8 : gg 8 = (8:ℝ) ^ s := by simp [hgg]
  have g9 : gg 9 = (9:ℝ) ^ s := by simp [hgg]
  rw [g1, g7, g8] at hmix
  rw [g8, g9] at hbank hfield mD hD9
  nlinarith [hmix, hbank, hfield, hsplit, hpay, mD]

/-- D ≥ 56 and X ≥ 2D give the D56-dir mass X ≥ 112. -/
theorem excess_ge_112 (G : BankedGraph K Fld Bank) (hD : 56 ≤ descMass G) (hXD : 2 * descMass G ≤ excess G) :
    (112 : ℝ) ≤ (excess G : ℝ) := by
  have : (112 : ℤ) ≤ excess G := by omega
  exact_mod_cast this

/-- the D56-dir + HS rung for ANY caller block and any exact Cert of its ceiling (kbar ≥ 9526/10^6). -/
theorem bank_kappa_lt_banner_of_cert (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : 9526 / 1000000 ≤ kbar)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    (G : Fin L → BankedGraph K Fld Bank) (hc : ∀ i, HSContract (G i).N)
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
  have hb := BankBannerBud.cert κ (by norm_num at hk ⊢; linarith) hκ1.le
  unfold BankBannerBud.FceilBank at hb
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

/-- **#7761** (frontier, κ .0038207): its own caller block (2048 calls), D56-dir (D ≥ 56, X ≥ 2D) + HEIGHT-STOP
    ⟹ κ < .009526828 (root .009526827724). -/
theorem bank_kappa_lt_banner (G : Fin 2048 → BankedGraph K Fld Bank) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i)) (hXD : ∀ i, 2 * descMass (G i) ≤ excess (G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankBannerCert.TB - cdat (1 - κ) BankBannerCert.PB) :
    κ < 2381707 / 250000000 := by
  have hcert : Cert (fun s => cdat s BankBannerCert.TB - cdat s BankBannerCert.PB -
      ((2048 : ℕ) : ℝ) * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s)))
      (2381707 / 250000000) := by
    intro t h1 h2
    have := BankBannerCert.cert t h1 h2
    unfold BankBannerCert.FceilBank at this
    push_cast
    linarith
  exact bank_kappa_lt_banner_of_cert 2048 _ _ _ (by norm_num) hcert G hc hD hXD κ hκ0 hκ1 paid hpaid hcaller

end BankBanner
#print axioms BankBanner.price_hsX
#print axioms BankBanner.bank_kappa_lt_banner_of_cert
#print axioms BankBanner.bank_kappa_lt_banner

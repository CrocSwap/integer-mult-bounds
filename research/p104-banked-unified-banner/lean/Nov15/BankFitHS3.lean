/-
BankFitHS3 .  Banked HEIGHT-STOP + FLAG rung as one kernel theorem.
  mix_eq        : f = g - D9·d = c1' m1 + c2 m2 + c3 M3 + c4 m4 + c5 M5 + c6 M6 + c7 M7 + c8 m8 on heights 0..9
                  (c_L = 2g(L) - g(L-1) - g(L+1), c1' = c1 - c3/3 - c5 - c6 - c7), any g with g 0 = 0.
  price_hs      : per call, 400 g8 + 28 D9 + 104 (g1 + g7 - g8) + helperCredit ≤ Σ paid   (s ∈ (0,1], budget c1' ≥ 0)
                  = HS cuts (BankFitHS1.mol_hs on the 8 molecules of BankFitHS2) + flag mass (BankHelp.sum_cuts_gen).
  bank_kappa_lt_hs_of_cert : any L-call caller block + exact Cert of its HS ceiling function (kbar ≥ 1/100) ⟹ κ < kbar.
  bank_kappa_lt_hs : #7761's caller block (2048 calls, BankFitCertHS) ⟹ κ < 19187/1000000 = .019187
                     (root .019186871868).  Budget c1' > 0 on t ∈ [1/100, 1]: BankFitCertBUD.
Premises: BankedGraph (BankFitA) + HSContract (BankFitHS1) + P-1S' (hpaid) + P-CALLER' (hcaller).  Kernel only.
-/
import Nov15.BankFitHS2
import Nov15.BankFitCertHS
import Nov15.BankFitCertBUD

namespace BankFitHS
open Finset Module BankNC0 BankWireC BankWireD BankHelp BankFit SafeRungsPrice BankMassF

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

noncomputable def cc (gg : ℕ → ℝ) (L : ℕ) : ℝ := 2 * gg L - gg (L - 1) - gg (L + 1)

noncomputable def c1' (gg : ℕ → ℝ) : ℝ := cc gg 1 - cc gg 3 / 3 - cc gg 5 - cc gg 6 - cc gg 7

noncomputable def mix (gg : ℕ → ℝ) (d : ℕ) : ℝ :=
  c1' gg / 212688 * (M_m1 d : ℝ) + cc gg 2 / 4 * (M_m2 d : ℝ) + cc gg 3 / 12 * (M_M3 d : ℝ)
  + cc gg 4 / 2 * (M_m4 d : ℝ) + cc gg 5 / 4 * (M_M5 d : ℝ) + cc gg 6 / 28 * (M_M6 d : ℝ)
  + cc gg 7 / 24 * (M_M7 d : ℝ) + cc gg 8 / 2 * (M_m8 d : ℝ)

theorem mix_eq (gg : ℕ → ℝ) (h0 : gg 0 = 0) (d : ℕ) (hd : d ≤ 9) :
    gg d = mix gg d + (gg 9 - gg 8) * d := by
  interval_cases d <;>
    simp [mix, c1', cc, M_m1, M_m2, M_M3, M_m4, M_M5, M_M6, M_M7, M_m8, h0] <;> ring

/-- the separating weights sum to (g1 + g7 - g8)/2 per extra pair. -/
theorem sep_eq (gg : ℕ → ℝ) (h0 : gg 0 = 0) :
    208 * (c1' gg / 212688 * 106344 + cc gg 2 / 4 * 2 + cc gg 3 / 12 * 8 + cc gg 4 / 2 * 1
      + cc gg 5 / 4 * 4 + cc gg 6 / 28 * 28 + cc gg 7 / 24 * 24 + cc gg 8 / 2 * 0)
    = 104 * (gg 1 + gg 7 - gg 8) := by
  simp [c1', cc, h0]; ring

theorem castM {ι κ : Type} [Fintype ι] [Fintype κ] (M : ℕ → ℕ) (a : ι → ℕ) (b : κ → ℕ) (S : ℕ)
    (h : ∑ i, M (a i) + 208 * S ≤ ∑ k, M (b k)) :
    ∑ i, (M (a i) : ℝ) + 208 * (S : ℝ) ≤ ∑ k, (M (b k) : ℝ) := by
  exact_mod_cast h

theorem mix_sum {ι κ : Type} [Fintype ι] [Fintype κ] (gg : ℕ → ℝ) (a : ι → ℕ) (b : κ → ℕ)
    (hc1 : 0 ≤ c1' gg) (hcc : ∀ L, 2 ≤ L → L ≤ 8 → 0 ≤ cc gg L)
    (h1 : ∑ i, (M_m1 (a i) : ℝ) + 208 * 106344 ≤ ∑ k, (M_m1 (b k) : ℝ))
    (h2 : ∑ i, (M_m2 (a i) : ℝ) + 208 * 2 ≤ ∑ k, (M_m2 (b k) : ℝ))
    (h3 : ∑ i, (M_M3 (a i) : ℝ) + 208 * 8 ≤ ∑ k, (M_M3 (b k) : ℝ))
    (h4 : ∑ i, (M_m4 (a i) : ℝ) + 208 * 1 ≤ ∑ k, (M_m4 (b k) : ℝ))
    (h5 : ∑ i, (M_M5 (a i) : ℝ) + 208 * 4 ≤ ∑ k, (M_M5 (b k) : ℝ))
    (h6 : ∑ i, (M_M6 (a i) : ℝ) + 208 * 28 ≤ ∑ k, (M_M6 (b k) : ℝ))
    (h7 : ∑ i, (M_M7 (a i) : ℝ) + 208 * 24 ≤ ∑ k, (M_M7 (b k) : ℝ))
    (h8 : ∑ i, (M_m8 (a i) : ℝ) + 208 * 0 ≤ ∑ k, (M_m8 (b k) : ℝ)) :
    ∑ i, mix gg (a i) + 208 * (c1' gg / 212688 * 106344 + cc gg 2 / 4 * 2 + cc gg 3 / 12 * 8 + cc gg 4 / 2 * 1
      + cc gg 5 / 4 * 4 + cc gg 6 / 28 * 28 + cc gg 7 / 24 * 24 + cc gg 8 / 2 * 0) ≤ ∑ k, mix gg (b k) := by
  simp only [mix, sum_add_distrib, ← mul_sum]
  have k1 := mul_le_mul_of_nonneg_left h1 (div_nonneg hc1 (by norm_num : (0:ℝ) ≤ 212688))
  have k2 := mul_le_mul_of_nonneg_left h2 (div_nonneg (hcc 2 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 4))
  have k3 := mul_le_mul_of_nonneg_left h3 (div_nonneg (hcc 3 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 12))
  have k4 := mul_le_mul_of_nonneg_left h4 (div_nonneg (hcc 4 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 2))
  have k5 := mul_le_mul_of_nonneg_left h5 (div_nonneg (hcc 5 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 4))
  have k6 := mul_le_mul_of_nonneg_left h6 (div_nonneg (hcc 6 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 28))
  have k7 := mul_le_mul_of_nonneg_left h7 (div_nonneg (hcc 7 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 24))
  have k8 := mul_le_mul_of_nonneg_left h8 (div_nonneg (hcc 8 (by norm_num) (by norm_num)) (by norm_num : (0:ℝ) ≤ 2))
  nlinarith [k1, k2, k3, k4, k5, k6, k7, k8]

/-- per call: HS cuts + flag mass. -/
theorem price_hs (G : BankedGraph K Fld Bank) (hc : HSContract G.N) {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1)
    (hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ s))
    (paid : Bank → ℝ) (hpaid : ∀ k, bankPrice G s k ≤ paid k) :
    400 * (8:ℝ) ^ s + 28 * ((9:ℝ) ^ s - (8:ℝ) ^ s) + 104 * (1 + (7:ℝ) ^ s - (8:ℝ) ^ s)
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
  -- banks and fields as height pairs
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
  -- mass: Σ dh ≥ Σ cl + 28
  have hmass := sum_cuts_gen G.N G.minors G.con G.nest G.cl G.climb
  have hmassR : (∑ f, (G.cl f : ℝ)) + 28 ≤ ∑ k, (bk k : ℝ) := by exact_mod_cast hmass
  -- assemble
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

/-- the HS + flag rung for ANY caller block and any exact Cert of its ceiling (kbar ≥ 1/100). -/
theorem bank_kappa_lt_hs_of_cert (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : 1 / 100 ≤ kbar)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    (G : Fin L → BankedGraph K Fld Bank) (hc : ∀ i, HSContract (G i).N) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin L → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) T - cdat (1 - κ) P) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc' := hcert κ hge hκ1.le
  simp only at hc'
  have hb := BankFitCertBUD.cert κ (by linarith) hκ1.le
  unfold BankFitCertBUD.FceilBank at hb
  have hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ (1 - κ)) := by
    have hz : (0:ℝ) ^ (1 - κ) = 0 := Real.zero_rpow (by linarith)
    simp only [c1', cc]
    norm_num [hz]
    linarith
  have each : ∀ i, 400 * (8:ℝ) ^ (1 - κ) + 28 * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      + 104 * (1 + (7:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      ≤ ∑ k, paid i k - helperCredit (G i).N (1 - κ) (G i).Mn := fun i => by
    have := price_hs (G i) (hc i) (s := 1 - κ) (by linarith) (by linarith) hbud _ (hpaid i)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  linarith

/-- **#7761** (frontier): its own caller block (2048 calls), HEIGHT-STOP + flag 14+14 ⟹ κ < .019187. -/
theorem bank_kappa_lt_hs (G : Fin 2048 → BankedGraph K Fld Bank) (hc : ∀ i, HSContract (G i).N)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankFitCertHS.TB - cdat (1 - κ) BankFitCertHS.PB) :
    κ < 19187 / 1000000 := by
  have hcert : Cert (fun s => cdat s BankFitCertHS.TB - cdat s BankFitCertHS.PB -
      ((2048 : ℕ) : ℝ) * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (19187 / 1000000) := by
    intro t h1 h2
    have := BankFitCertHS.cert t h1 h2
    unfold BankFitCertHS.FceilBank at this
    push_cast
    linarith
  exact bank_kappa_lt_hs_of_cert 2048 _ _ _ (by norm_num) hcert G hc κ hκ0 hκ1 paid hpaid hcaller

end BankFitHS
#print axioms BankFitHS.bank_kappa_lt_hs_of_cert
#print axioms BankFitHS.bank_kappa_lt_hs

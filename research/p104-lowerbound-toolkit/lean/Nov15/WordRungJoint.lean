/-
WordRungJoint (lane JOINTDR, Nov 20).  The word rung needs only the JOINT premise D + R ≥ 112, and only on AVERAGE
over the calls.
  Every rung headline (WordRung, WordRungGen, WordRungPD, WordRungLat, WordRungLadder, WordRungPort, UniOwnedBank)
  consumes its two halves hD : 56 ≤ D, hR : 56 ≤ R only through `excess_ge_112_halves` (X = D + R ≥ 112, with
  `excess_split_bank` : excess = descMass + hostedRise exact).  The per-call price `price_hsX` is AFFINE in X with
  slope 9^s - 8^s ≥ 0, so the sum over calls only sees Σ_i X_i.
  `portInvX_affine`   : PortInvX n QR h X S s = PortInvX n QR h 0 S s + X (h^s - (h-1)^s).
  `rung_port_joint`   : port-general rung with the single aggregate premise  L·X0 ≤ Σ_i Xe_i  (no per-call wall).
  `rung_joint_P104`   : P104, any caller:  112·L ≤ Σ_i (descMass G_i + hostedRise G_i)  ⟹  κ < kbar.
  `rung_joint_7113`   : the #7113 value κ < .0093453742 under the aggregate joint premise.
  `joint_of_halves`   : the old per-call halves imply the aggregate premise (so this strictly generalises).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.WordRungPort

set_option linter.unusedSectionVars false

namespace UniJoint
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankMassF BankFitHS
  BankCallerGen UniOwnedBank NoFlow UniWC UniPort

/-- the rung invoice is affine in the decoder mass X. -/
theorem portInvX_affine (n QR h : ℕ) (X S s : ℝ) :
    PortInvX n QR h X S s = PortInvX n QR h 0 S s + X * ((h : ℝ) ^ s - ((h : ℝ) - 1) ^ s) := by
  unfold PortInvX; ring

theorem slope_nonneg (h : ℕ) (hh : 1 ≤ h) {s : ℝ} (hs : 0 ≤ s) :
    0 ≤ (h : ℝ) ^ s - ((h : ℝ) - 1) ^ s := by
  have h1 : (1 : ℝ) ≤ h := by exact_mod_cast hh
  have := Real.rpow_le_rpow (by linarith : (0:ℝ) ≤ (h : ℝ) - 1) (by linarith : (h : ℝ) - 1 ≤ h) hs
  linarith

/-- **rung_port_joint**: the port-parametric rung with ONE aggregate premise L·X0 ≤ Σ_i Xe_i on the per-call
decoder masses (X0 = (ρD + ρR) n in `rung_port`); `hprice` is the per-call rung premise at X = Xe i. -/
theorem rung_port_joint (n QR h : ℕ) (hh : 1 ≤ h) (X0 S kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * PortInvX n QR h X0 S s) kbar)
    (spec cred : Fin L → ℝ → ℝ) (Xe : Fin L → ℝ)
    (hsum : (L : ℝ) * X0 ≤ ∑ i, Xe i)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hprice : kbar ≤ κ → ∀ i, PortInvX n QR h (Xe i) S (1 - κ) ≤ spec i (1 - κ) - cred i (1 - κ))
    (hV : cdat (1 - κ) P + ∑ i, spec i (1 - κ) ≤ cdat (1 - κ) T + ∑ i, cred i (1 - κ)) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc' := hcert κ hge hκ1.le
  simp only at hc'
  set c := (h : ℝ) ^ (1 - κ) - ((h : ℝ) - 1) ^ (1 - κ) with hcdef
  have hc0 : 0 ≤ c := slope_nonneg h hh (by linarith)
  have each' : ∀ i, PortInvX n QR h 0 S (1 - κ) + Xe i * c ≤ spec i (1 - κ) - cred i (1 - κ) := by
    intro i; have := hprice hge i; rw [portInvX_affine n QR h (Xe i) S (1 - κ)] at this; exact this
  have hs := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each' i)
  rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    ← Finset.sum_mul, Finset.sum_sub_distrib] at hs
  rw [portInvX_affine n QR h X0 S (1 - κ)] at hc'
  have hm : (L : ℝ) * X0 * c ≤ (∑ i, Xe i) * c := mul_le_mul_of_nonneg_right hsum hc0
  nlinarith

/-- **rung_joint_P104** (any caller): the rung under the aggregate joint premise 112·L ≤ Σ_i (D_i + R_i). -/
theorem rung_joint_P104 (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : 46726871 / 5000000000 ≤ kbar)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i)) (hc : ∀ i, HSContract (G i).N)
    (hJ : (112 : ℤ) * L ≤ ∑ i, (descMass (G i) + hostedRise (G i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) P + ∑ i, ∑ k, BankPrem.specInvoice (G i) (1 - κ) k ≤
      cdat (1 - κ) T + ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn) :
    κ < kbar := by
  refine rung_port_joint 104 96 9 (by norm_num) 112 0 kbar L T P ?_
    (fun i s => ∑ k, BankPrem.specInvoice (G i) s k) (fun i s => helperCredit (G i).N s (G i).Mn)
    (fun i => (excess (G i) : ℝ)) ?_ κ hκ0 hκ1 ?_ hV
  · intro t h1 h2
    have := hcert t h1 h2
    have e : ∀ s : ℝ, PortInvX 104 96 9 112 0 s =
        400 * (8:ℝ) ^ s + 112 * ((9:ℝ) ^ s - (8:ℝ) ^ s) + 104 * (1 + (7:ℝ) ^ s - (8:ℝ) ^ s) := by
      intro s
      have h1 : ((9 : ℕ) : ℝ) - 1 = 8 := by norm_num
      have h2 : ((9 : ℕ) : ℝ) - 2 = 7 := by norm_num
      have h3 : ((mains 104 96 : ℕ) : ℝ) = 400 := by norm_num [mains]
      simp only [PortInvX, h1, h2, h3, zero_mul, add_zero]
      norm_num
    simp only [e]
    exact this
  · have hJ' : ((112 * L : ℤ) : ℝ) ≤ ((∑ i, (descMass (G i) + hostedRise (G i)) : ℤ) : ℝ) := by
      exact_mod_cast hJ
    push_cast at hJ'
    have hx : ∀ i, (excess (G i) : ℝ) = (descMass (G i) : ℝ) + (hostedRise (G i) : ℝ) := by
      intro i; rw [excess_split_bank]; push_cast; ring
    simp only [hx]
    linarith
  · intro hge i
    have hb := UniBud.cert κ (by linarith) hκ1.le
    unfold UniBud.FceilBank at hb
    have hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ (1 - κ)) := by
      have hz : (0:ℝ) ^ (1 - κ) = 0 := Real.zero_rpow (by linarith)
      simp only [c1', cc]
      norm_num [hz]
      linarith
    have := price_hsX (G i) (hc i) (s := 1 - κ) (by linarith) (by linarith) hbud (excess (G i) : ℝ) le_rfl _
      (fun k => BankPrem.bankPrice_le_specInvoice (G i) (by linarith) k)
    have e : PortInvX 104 96 9 (excess (G i) : ℝ) 0 (1 - κ) = 400 * (8:ℝ) ^ (1 - κ)
        + (excess (G i) : ℝ) * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ)) + 104 * (1 + (7:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ)) := by
      have h1 : ((9 : ℕ) : ℝ) - 1 = 8 := by norm_num
      have h2 : ((9 : ℕ) : ℝ) - 2 = 7 := by norm_num
      have h3 : ((mains 104 96 : ℕ) : ℝ) = 400 := by norm_num [mains]
      simp only [PortInvX, h1, h2, h3, zero_mul, add_zero]
      norm_num
    rw [e]; linarith

/-- **rung_joint_7113**: κ < .0093453742 for the #7113 caller under the aggregate joint premise. -/
theorem rung_joint_7113 {Fld Bank : Fin 17 → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)]
    [∀ i, Fintype (Bank i)] [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i)) (hc : ∀ i, HSContract (G i).N)
    (hJ : (112 : ℤ) * 17 ≤ ∑ i, (descMass (G i) + hostedRise (G i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, ∑ k, BankPrem.specInvoice (G i) (1 - κ) k ≤
      cdat (1 - κ) Tcal + ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn) :
    κ < 93453742 / 10000000000 := by
  have hJ' : (112 : ℤ) * ((17 : ℕ) : ℤ) ≤ ∑ i, (descMass (G i) + hostedRise (G i)) := by exact_mod_cast hJ
  exact rung_joint_P104 17 Tcal Pcal _ (by norm_num) (by exact_mod_cast UniUniversal.cert7113) G hc hJ' κ hκ0 hκ1 hV

/-- the old per-call halves imply the aggregate joint premise. -/
theorem joint_of_halves {L : ℕ} {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)]
    [∀ i, Fintype (Bank i)] [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i))
    (hD : ∀ i, 56 ≤ descMass (G i)) (hR : ∀ i, 56 ≤ hostedRise (G i)) :
    (112 : ℤ) * L ≤ ∑ i, (descMass (G i) + hostedRise (G i)) := by
  have : ∑ _i : Fin L, (112 : ℤ) ≤ ∑ i, (descMass (G i) + hostedRise (G i)) :=
    Finset.sum_le_sum (fun i _ => by have := hD i; have := hR i; omega)
  simpa [mul_comm] using this

/-- non-vacuity of the strengthening: an aggregate premise that holds although one call has X = 100 < 112. -/
theorem nonvac_aggregate : ((2 : ℕ) : ℝ) * 112 ≤ ∑ i : Fin 2, (![100, 124] : Fin 2 → ℝ) i ∧
    ¬ ((112 : ℝ) ≤ (![100, 124] : Fin 2 → ℝ) 0) := by
  constructor
  · simp [Fin.sum_univ_two]; norm_num
  · simp; norm_num

end UniJoint

#print axioms UniJoint.rung_port_joint
#print axioms UniJoint.rung_joint_P104
#print axioms UniJoint.rung_joint_7113
#print axioms UniJoint.joint_of_halves
#print axioms UniJoint.nonvac_aggregate

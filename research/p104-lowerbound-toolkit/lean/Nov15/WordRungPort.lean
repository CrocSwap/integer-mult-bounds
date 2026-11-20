/-
WordRungPort (lane RETYPE, Nov 20).  The word rung as a function of the PORT SET, not of P104.
  Parameters of a legal port set P:  n = |P| (ports per call), QR = |Q_R(P)| (R-side sub-pattern; mains M = 2n + 2QR),
  h = label rank (u = h - 1 = main climb), wall densities rhoD, rhoR (D ≥ rhoD·n, R ≥ rhoR·n per call),
  S = S_spec stay mass per call (price pu u s), caller block (L, T, P).
  PortInv n QR h X S s = M u^s + X (h^s - u^s) + n (1 + (u-1)^s - u^s) + S pu u s,   X = (rhoD + rhoR) n   (the per-call rung invoice;
  at (104, 96, 9, 56/104, 56/104, S = 0) it is 400·8^s + 112 (9^s - 8^s) + 104 (1 + 7^s - 8^s)).
  `rung_port`   : Cert (cdat T - cdat P - L·PortInv) kbar  +  per-call RUNG PREMISE (the HS-molecule price, stated at the crossing)
                  + D,R wall premises + Valid  ⟹  κ < kbar.   Pure real-analysis reduction; port-general (no Fin 9, no Ports7113).
  The per-call premise `hprice` is the one place the P104 chart structure lives.  At P104 it is discharged by BankBanner.price_hsX
  (HSContract literal 104/heights 0,1,8,9; eight cut molecules over heights 0..9 — an h = 9 LP certificate).  A general-h price_hsX is NOT
  retyped here: it is the named hypothesis.
  Instances: `rung_port_P104` (any caller, HS banked graphs, = kappa_of_cert_dep recovered), `rung_port_7113` (κ < .0093453742).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniUniversal

set_option linter.unusedSectionVars false

namespace UniPort
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankMassF BankFitHS
  BankCallerGen UniOwnedBank NoFlow UniWC

/-- mains per call: 2n + 2|Q_R|  (400 = 2·104 + 2·96). -/
def mains (n QR : ℕ) : ℕ := 2 * n + 2 * QR

/-- stay price p_u(s) = (u - u^s)/(u - 1). -/
noncomputable def pstay (u s : ℝ) : ℝ := (u - u ^ s) / (u - 1)

/-- per-call rung invoice with an explicit decoder mass X. -/
noncomputable def PortInvX (n QR h : ℕ) (X S s : ℝ) : ℝ :=
  (mains n QR : ℝ) * ((h : ℝ) - 1) ^ s + X * ((h : ℝ) ^ s - ((h : ℝ) - 1) ^ s)
    + (n : ℝ) * (1 + ((h : ℝ) - 2) ^ s - ((h : ℝ) - 1) ^ s) + S * pstay ((h : ℝ) - 1) s

/-- per-call rung invoice at wall densities rhoD, rhoR. -/
noncomputable def PortInv (n QR h : ℕ) (ρD ρR S s : ℝ) : ℝ := PortInvX n QR h ((ρD + ρR) * n) S s

/-- **rung_port**: the port-parametric word rung.
`hprice` = the per-call RUNG PREMISE at the crossing (for any decoder mass X ≤ the call's excess, the invoice is covered by
SPEC payment minus helper credit); `hD`,`hR` = per-port wall premises; `hV` = Theorem-K validity against the caller block. -/
theorem rung_port (n QR h : ℕ) (ρD ρR S kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * PortInv n QR h ρD ρR S s) kbar)
    (spec cred : Fin L → ℝ → ℝ) (Dm Rm Xe : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i) (hX : ∀ i, Dm i + Rm i ≤ Xe i)
    (κ : ℝ) (hκ1 : κ < 1)
    (hprice : kbar ≤ κ → ∀ i, ∀ X : ℝ, X ≤ Xe i → PortInvX n QR h X S (1 - κ) ≤ spec i (1 - κ) - cred i (1 - κ))
    (hV : cdat (1 - κ) P + ∑ i, spec i (1 - κ) ≤ cdat (1 - κ) T + ∑ i, cred i (1 - κ)) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc' := hcert κ hge hκ1.le
  simp only at hc'
  have each : ∀ i, PortInv n QR h ρD ρR S (1 - κ) ≤ spec i (1 - κ) - cred i (1 - κ) := fun i =>
    hprice hge i _ (by have := hD i; have := hR i; have := hX i; nlinarith)
  have hs := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at hs
  linarith

/-- numerics of the P104 specialisation of PortInv. -/
theorem portInv_P104 (s : ℝ) :
    PortInv 104 96 9 (56 / 104) (56 / 104) 0 s =
      400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s) := by
  have h1 : ((9 : ℕ) : ℝ) - 1 = 8 := by norm_num
  have h2 : ((9 : ℕ) : ℝ) - 2 = 7 := by norm_num
  have h3 : ((mains 104 96 : ℕ) : ℝ) = 400 := by norm_num [mains]
  have h4 : ((56 / 104 : ℝ) + 56 / 104) * ((104 : ℕ) : ℝ) = 112 := by norm_num
  simp only [PortInv, PortInvX, h1, h2, h3, h4, zero_mul, add_zero]
  norm_num

/-- **INSTANCE (P104, any caller)**: `rung_port` at n = 104, QR = 96, h = 9, rhoD = rhoR = 56/104, S = 0 recovers
UniUniversal.kappa_of_cert_dep (same hypotheses, same conclusion). -/
theorem rung_port_P104 (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ) (hk : 46726871 / 5000000000 ≤ kbar)
    (hcert : Cert (fun s => cdat s T - cdat s P
      - L * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i)) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i)) (hR : ∀ i, 56 ≤ hostedRise (G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) P + ∑ i, ∑ k, BankPrem.specInvoice (G i) (1 - κ) k ≤
      cdat (1 - κ) T + ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn) :
    κ < kbar := by
  refine rung_port 104 96 9 (56 / 104) (56 / 104) 0 kbar L T P ?_
    (fun i s => ∑ k, BankPrem.specInvoice (G i) s k) (fun i s => helperCredit (G i).N s (G i).Mn)
    (fun i => (descMass (G i) : ℝ)) (fun i => (hostedRise (G i) : ℝ)) (fun i => (excess (G i) : ℝ))
    ?_ ?_ ?_ κ hκ1 ?_ hV
  · intro t h1 h2
    have := hcert t h1 h2
    simp only [portInv_P104]
    exact this
  · intro i; have : (56 : ℝ) ≤ (descMass (G i) : ℝ) := by exact_mod_cast hD i
    norm_num; linarith
  · intro i; have : (56 : ℝ) ≤ (hostedRise (G i) : ℝ) := by exact_mod_cast hR i
    norm_num; linarith
  · intro i; rw [excess_split_bank]; push_cast; exact le_rfl
  · intro hge i X hXi
    have hb := UniBud.cert κ (by linarith) hκ1.le
    unfold UniBud.FceilBank at hb
    have hbud : 0 ≤ c1' (fun d : ℕ => (d : ℝ) ^ (1 - κ)) := by
      have hz : (0:ℝ) ^ (1 - κ) = 0 := Real.zero_rpow (by linarith)
      simp only [c1', cc]
      norm_num [hz]
      linarith
    have := price_hsX (G i) (hc i) (s := 1 - κ) (by linarith) (by linarith) hbud X hXi _
      (fun k => BankPrem.bankPrice_le_specInvoice (G i) (by linarith) k)
    have e : PortInvX 104 96 9 X 0 (1 - κ) = 400 * (8:ℝ) ^ (1 - κ) + X * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
        + 104 * (1 + (7:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ)) := by
      have h1 : ((9 : ℕ) : ℝ) - 1 = 8 := by norm_num
      have h2 : ((9 : ℕ) : ℝ) - 2 = 7 := by norm_num
      have h3 : ((mains 104 96 : ℕ) : ℝ) = 400 := by norm_num [mains]
      simp only [PortInvX, h1, h2, h3, zero_mul, add_zero]
      norm_num
    rw [e]; linarith

/-- **INSTANCE (#7113 caller)**: the P104 value κ < .0093453742 recovered from the port-general statement. -/
theorem rung_port_7113 {Fld Bank : Fin 17 → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)]
    [∀ i, Fintype (Bank i)] [∀ i, LinearOrder (Bank i)]
    (G : ∀ i, BankedGraph ℚ (Fld i) (Bank i)) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i)) (hR : ∀ i, 56 ≤ hostedRise (G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, ∑ k, BankPrem.specInvoice (G i) (1 - κ) k ≤
      cdat (1 - κ) Tcal + ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn) :
    κ < 93453742 / 10000000000 :=
  rung_port_P104 17 Tcal Pcal _ (by norm_num) UniUniversal.cert7113 G hc hD hR κ hκ0 hκ1 hV

end UniPort

#print axioms UniPort.rung_port
#print axioms UniPort.portInv_P104
#print axioms UniPort.rung_port_P104
#print axioms UniPort.rung_port_7113

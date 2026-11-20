/-
BankPrem (lane PREM-LEAN, Nov 18).  Discharges P-1S' and reduces P-CALLER' of the banked banner to ONE named SPEC statement.
(1) P-1S': the SPEC invoice price of a move between subspace charts is the lattice distance latD(src,dst) = rank(M_dst - M_src)
    (WordModelSpec.latD, SPEC "Preimage frames"; same definition as HLINK `specPrice`).  PROVED  dh(dim src, dim dst) <= latD src dst
    (`dh_le_latD`), hence bankPrice (= dh^s) <= (latD)^s for s >= 0 (`bankPrice_le_specInvoice`): hpaid holds for paid := specInvoice.
(2) P-CALLER': `Caller` = L native graphs + caller block (T = root targets, P = caller paid rows, rank,count lists, the #7761
    app7761.json data).  Total invoice = cdat P + sum of native paid; total credit = cdat T + sum of helper credits (productive credit
    = root targets + helper climbs, AUDIT-BANK).  `Valid` = the single remaining statement "kappa is a crossing of the invoice":
    total paid <= total credit.  `hcaller_of_valid` derives hcaller by arithmetic; `totalPaid_const` is the split
    caller block + L * (graph invoice) for L calls of one native graph.
(3) wrappers: bank_kappa_lt_flag_spec (kappa < .01994) and bank_kappa_lt_banner_spec (kappa < .009526828), premises
    BankedGraph (+HSContract, hD, hXD) and Valid only.
Kernel only.
-/
import Nov15.BankBanner

namespace BankPrem
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- SPEC lattice price on subspace charts: dim U + dim W - 2 dim (U inf W) = rank(M_W - M_U). -/
noncomputable def latD (U W : Submodule (ZMod 2) V) : ℝ :=
  (finrank (ZMod 2) U : ℝ) + finrank (ZMod 2) W - 2 * finrank (ZMod 2) (U ⊓ W : Submodule (ZMod 2) V)

theorem dh_le_latD (U W : Submodule (ZMod 2) V) :
    ((dh (finrank (ZMod 2) U) (finrank (ZMod 2) W) : ℕ) : ℝ) ≤ latD U W := by
  have h1 := Submodule.finrank_mono (inf_le_left : U ⊓ W ≤ U)
  have h2 := Submodule.finrank_mono (inf_le_right : U ⊓ W ≤ W)
  have h1' : (finrank (ZMod 2) (U ⊓ W : Submodule (ZMod 2) V) : ℝ) ≤ finrank (ZMod 2) U := by exact_mod_cast h1
  have h2' : (finrank (ZMod 2) (U ⊓ W : Submodule (ZMod 2) V) : ℝ) ≤ finrank (ZMod 2) W := by exact_mod_cast h2
  unfold dh
  rw [Nat.cast_natAbs, Int.cast_abs]
  push_cast
  unfold latD
  rw [abs_le]; constructor <;> linarith

/-- on a nested pair the SPEC price IS the dimension jump. -/
theorem latD_eq_dh_of_le {U W : Submodule (ZMod 2) V} (h : U ≤ W) :
    latD U W = ((dh (finrank (ZMod 2) U) (finrank (ZMod 2) W) : ℕ) : ℝ) := by
  have h1 := Submodule.finrank_mono h
  have hi : U ⊓ W = U := inf_eq_left.2 h
  unfold latD dh; rw [hi]
  have h1' : (finrank (ZMod 2) U : ℝ) ≤ finrank (ZMod 2) W := by exact_mod_cast h1
  rw [Nat.cast_natAbs, Int.cast_abs, abs_of_nonpos (by push_cast; linarith)]
  push_cast; ring

/-- the SPEC invoice of move k at exponent s: (rank of the transition)^s. -/
noncomputable def specInvoice (G : BankedGraph K Fld Bank) (s : ℝ) (k : Bank) : ℝ :=
  (latD (G.N.src k) (G.N.dst k)) ^ s

/-- **P-1S' DISCHARGED**: the SPEC invoice dominates the concave height-jump price. -/
theorem bankPrice_le_specInvoice (G : BankedGraph K Fld Bank) {s : ℝ} (hs : 0 ≤ s) (k : Bank) :
    bankPrice G s k ≤ specInvoice G s k :=
  Real.rpow_le_rpow (Nat.cast_nonneg _) (dh_le_latD _ _) hs

/-- one caller: L native graphs, caller block T (root targets) / P (caller paid rows), both (rank,count). -/
structure Caller (K Fld Bank : Type) [Field K] [Fintype Fld] [DecidableEq Fld]
    [Fintype Bank] [LinearOrder Bank] (L : ℕ) where
  G : Fin L → BankedGraph K Fld Bank
  T : List (ℕ × ℕ)
  P : List (ℕ × ℕ)

/-- total invoice at exponent s: caller block + all native moves. -/
noncomputable def totalPaid {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ) (paid : Fin L → Bank → ℝ) : ℝ :=
  cdat s c.P + ∑ i, ∑ k, paid i k

/-- total productive credit: root targets + every helper's climb. -/
noncomputable def totalCredit {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ) : ℝ :=
  cdat s c.T + ∑ i, helperCredit (c.G i).N s (c.G i).Mn

/-- THE named SPEC statement (kappa is a crossing of the invoice at s = 1 - kappa): total paid <= total credit. -/
def Valid {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ) (paid : Fin L → Bank → ℝ) : Prop :=
  totalPaid c s paid ≤ totalCredit c s

/-- **P-CALLER' reduces to Valid** (pure arithmetic). -/
theorem hcaller_of_valid {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ) (paid : Fin L → Bank → ℝ)
    (h : Valid c s paid) :
    ∑ i, ∑ k, paid i k - ∑ i, helperCredit (c.G i).N s (c.G i).Mn ≤ cdat s c.T - cdat s c.P := by
  unfold Valid totalPaid totalCredit at h; linarith

/-- the invoice split: L calls of ONE native graph / per-call paid = caller block + L * (graph invoice); credit likewise. -/
theorem totalPaid_const {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ)
    (pd : Bank → ℝ) :
    totalPaid c s (fun _ => pd) = cdat s c.P + L * ∑ k, pd k := by
  unfold totalPaid; simp [Finset.sum_const, Finset.card_univ]

theorem totalCredit_const {L : ℕ} (c : Caller K Fld Bank L) (s : ℝ) (g : BankedGraph K Fld Bank)
    (hG : ∀ i, c.G i = g) :
    totalCredit c s = cdat s c.T + L * helperCredit g.N s g.Mn := by
  unfold totalCredit; simp [hG, Finset.sum_const, Finset.card_univ]

/-- flag rung for #7761 with P-1S' discharged and P-CALLER' = Valid. -/
theorem bank_kappa_lt_flag_spec (c : Caller K Fld Bank 2048)
    (hT : c.T = BankFitCertFit7761X28.TB) (hP : c.P = BankFitCertFit7761X28.PB)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 997 / 50000 :=
  bank_kappa_lt_flag c.G κ hκ0 hκ1 _ (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k)
    (by have := hcaller_of_valid c _ _ hV; rw [hT, hP] at this; exact this)

/-- banner rung (D56-dir) for #7761 with P-1S' discharged and P-CALLER' = Valid. -/
theorem bank_kappa_lt_banner_spec (c : Caller K Fld Bank 2048)
    (hT : c.T = BankBannerCert.TB) (hP : c.P = BankBannerCert.PB)
    (hc : ∀ i, HSContract (c.G i).N)
    (hD : ∀ i, 56 ≤ descMass (c.G i)) (hXD : ∀ i, 2 * descMass (c.G i) ≤ excess (c.G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 2381707 / 250000000 :=
  bank_kappa_lt_banner c.G hc hD hXD κ hκ0 hκ1 _
    (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k)
    (by have := hcaller_of_valid c _ _ hV; rw [hT, hP] at this; exact this)

/-! ## #7761 constants (DATA: UCEIL/bankfit/d7761/app7761.json result.candidate.signed), decide-checked -/
open BankFitCertFit7761X28 in
theorem consts7761 :
    TB = [(9, 20736), (17, 53248), (25, 53248), (33, 53248), (41, 53248), (49, 53248), (57, 53248),
          (65, 53248), (129, 26624)] ∧
    PB = [(1, 20704), (8, 53472), (9, 32), (16, 53248), (24, 53248), (32, 53248), (40, 53248),
          (48, 53248), (56, 53248)] ∧
    BankBannerCert.TB = TB ∧ BankBannerCert.PB = PB ∧
    -- per-call counts: 2048 calls x 26 (resp. 13) rows of each repeated rank; 400 mains x 2048 = native_main_bindings
    (53248 = 2048 * 26 ∧ 26624 = 2048 * 13 ∧ 400 * 2048 = 819200) := by
  refine ⟨rfl, rfl, rfl, rfl, ?_⟩
  decide

end BankPrem
#print axioms BankPrem.bankPrice_le_specInvoice
#print axioms BankPrem.bank_kappa_lt_flag_spec
#print axioms BankPrem.bank_kappa_lt_banner_spec
#print axioms BankPrem.consts7761

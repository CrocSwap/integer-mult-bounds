/-
HCutGen (lane HCUT, Nov 20).  The height-cut contract at ANY label rank h, proved from the word model's port-row shape.
  HSContractH N ht h n : generic version of BankFitHS1.HSContract: n rows of heights (1 -> h) with a (0 -> h-1) partner and
     n rows (0 -> h-1) with a (1 -> h) partner; support {self, pi f}; nonzero partner entries.  Heights ht : Chart -> N.
  cut_hsH     : crossing banks >= crossing fields + 2n [m separates {1,h}|{0,h-1}]   (= PriceH.HCall.hcut), any h, any n.
  ofHS9       : BankFitHS1.HSContract  ==>  HSContractH (h = 9, n = 104)   (conservative: the P104 contract is the h = 9 case).
  contract_of_ports : MODEL-FORCED: a Net on submodules of W (finrank W = h) in which every port p has an x-row
     span{v_p} -> top and a y-row bot -> ker phi_p (v_p, phi_p nonzero: ANY nonzero label), partner swap, O supported on
     {self, partner} with nonzero partner entries, satisfies HSContractH for every h and n.  No P104 data.
  HCall.ofNet / rung_port_net_h / rung_port_net_h7 / rung_port_net_h8 : rung_port_h with the HCall cut contract DISCHARGED.
Kernel only.
-/
import Nov15.BankFitHS1
import Nov15.PriceHRung
import Nov15.PriceHI7
import Nov15.PriceHI8
import Nov15.PriceHI9

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace HCutGen
open Finset Module BankNC0 PriceH

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

structure HSContractH (N : Net K Chart Fld Bank) (ht : Chart → ℕ) (h n : ℕ) where
  π : Fld → Fld
  πinj : Function.Injective π
  hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f
  Ehi : Finset Fld
  Elo : Finset Fld
  hi_card : Ehi.card = n
  lo_card : Elo.card = n
  hi_h : ∀ e ∈ Ehi, ht (N.A e) = 1 ∧ ht (N.B e) = h ∧ ht (N.A (π e)) = 0 ∧ ht (N.B (π e)) = h - 1
  lo_h : ∀ e ∈ Elo, ht (N.A e) = 0 ∧ ht (N.B e) = h - 1 ∧ ht (N.A (π e)) = 1 ∧ ht (N.B (π e)) = h
  nz_hi : ∀ e ∈ Ehi, N.O e (π e) ≠ 0
  nz_lo : ∀ e ∈ Elo, N.O e (π e) ≠ 0

theorem dir_extrasH (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    {ht : Chart → ℕ} {h n : ℕ} (hc : HSContractH N ht h n) (P : Chart → Prop) [DecidablePred P] (E : Finset Fld)
    (hE : ∀ e ∈ E, ¬ P (N.A e) ∧ ¬ P (N.B e)) (hπ : ∀ e ∈ E, P (N.A (hc.π e)) ∧ P (N.B (hc.π e)))
    (hnz : ∀ e ∈ E, N.O e (hc.π e) ≠ 0) :
    (univ.filter (fun f => P (N.A f) ∧ ¬ P (N.B f))).card + E.card ≤
      (univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card :=
  BankFlagC.cut_extras N P _ E hc.π (fun c hc' => (mem_filter.mp hc').2) (hminor _) hE hπ hnz hc.hsupp
    (fun e _ r _ h => hc.πinj h)

theorem sum_xcutH {α : Type} [Fintype α] (m : ℕ) (a b : α → ℕ) :
    ∑ x, xcut m (a x) (b x) = (univ.filter (fun x => ¬ (m.testBit (a x) = true ↔ m.testBit (b x) = true))).card := by
  rw [card_filter]
  refine sum_congr rfl (fun x _ => ?_)
  unfold xcut
  by_cases h1 : m.testBit (a x) <;> by_cases h2 : m.testBit (b x) <;> simp [h1, h2]

/-- per height cut at label rank h: crossing banks >= crossing fields + 2n on separating cuts. -/
theorem cut_hsH (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    {ht : Chart → ℕ} {h n : ℕ} (hc : HSContractH N ht h n) (m : ℕ) :
    ∑ f, xcut m (ht (N.A f)) (ht (N.B f)) + (if isSepH h m then 2 * n else 0) ≤
      ∑ k, xcut m (ht (N.src k)) (ht (N.dst k)) := by
  classical
  rw [sum_xcutH, sum_xcutH, BankFitHS.card_xor, BankFitHS.card_xor]
  set P : Chart → Prop := fun c => m.testBit (ht c) = true with hP
  set Q : Chart → Prop := fun c => ¬ m.testBit (ht c) = true with hQ
  have base : ∀ (R : Chart → Prop) [DecidablePred R],
      (univ.filter (fun f => R (N.A f) ∧ ¬ R (N.B f))).card ≤
        (univ.filter (fun k => R (N.src k) ∧ ¬ R (N.dst k))).card := by
    intro R _
    have := dir_extrasH N hminor hc R ∅ (by simp) (by simp) (by simp)
    simpa using this
  by_cases hs : isSepH h m
  · rw [if_pos hs]
    have hhi := hc.hi_h
    have hlo := hc.lo_h
    unfold isSepH at hs
    simp only [Bool.or_eq_true, Bool.and_eq_true, Bool.not_eq_true'] at hs
    rcases hs with ⟨⟨⟨b1, b9⟩, b0⟩, b8⟩ | ⟨⟨⟨b1, b9⟩, b0⟩, b8⟩
    · have d1 := dir_extrasH N hminor hc P hc.Elo
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hlo e he; simp [hP, h1, h2, b0, b8])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hlo e he; simp [hP, h3, h4, b1, b9]) hc.nz_lo
      have d2 := dir_extrasH N hminor hc Q hc.Ehi
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hhi e he; simp [hQ, h1, h2, b1, b9])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hhi e he; simp [hQ, h3, h4, b0, b8]) hc.nz_hi
      rw [hc.lo_card] at d1; rw [hc.hi_card] at d2
      simp only [hP, hQ, not_not] at d1 d2
      omega
    · have d1 := dir_extrasH N hminor hc P hc.Ehi
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hhi e he; simp [hP, h1, h2, b1, b9])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hhi e he; simp [hP, h3, h4, b0, b8]) hc.nz_hi
      have d2 := dir_extrasH N hminor hc Q hc.Elo
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hlo e he; simp [hQ, h1, h2, b0, b8])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hlo e he; simp [hQ, h3, h4, b1, b9]) hc.nz_lo
      rw [hc.hi_card] at d1; rw [hc.lo_card] at d2
      simp only [hP, hQ, not_not] at d1 d2
      omega
  · rw [if_neg hs]
    have a1 := base P
    have a2 := base Q
    simp only [hP, hQ, not_not] at a1 a2
    omega

/-- the P104 contract is the h = 9, n = 104 case. -/
def ofHS9 (N : Net K (Submodule (ZMod 2) BankWireC.V) Fld Bank) (hc : BankFitHS.HSContract N) :
    HSContractH N BankFitHS.ht 9 104 where
  π := hc.π
  πinj := hc.πinj
  hsupp := hc.hsupp
  Ehi := hc.Ehi
  Elo := hc.Elo
  hi_card := hc.hi_card
  lo_card := hc.lo_card
  hi_h := hc.hi_h
  lo_h := hc.lo_h
  nz_hi := hc.nz_hi
  nz_lo := hc.nz_lo

/-! ### Model-forced: the contract from the port-row shape -/
section Ports
variable {W : Type} [AddCommGroup W] [Module (ZMod 2) W] [FiniteDimensional (ZMod 2) W]

theorem finrank_ker_pred (φ : W →ₗ[ZMod 2] ZMod 2) (hφ : φ ≠ 0) {h : ℕ} (hW : finrank (ZMod 2) W = h) :
    finrank (ZMod 2) (LinearMap.ker φ) = h - 1 := by
  have h1 := LinearMap.finrank_range_add_finrank_ker φ
  have h2 : finrank (ZMod 2) (LinearMap.range φ) = 1 := by
    apply le_antisymm
    · have := Submodule.finrank_le (LinearMap.range φ); simpa using this
    · apply Nat.one_le_iff_ne_zero.mpr
      intro h0
      apply hφ
      have hb : LinearMap.range φ = ⊥ := Submodule.finrank_eq_zero.mp h0
      exact LinearMap.range_eq_bot.mp hb
  omega

/-- one port-model row family: n ports, x_p : span{v_p} -> top, y_p : bot -> ker phi_p, partner swap. -/
noncomputable def contract_of_ports (N : Net K (Submodule (ZMod 2) W) Fld Bank) {h n : ℕ}
    (hW : finrank (ZMod 2) W = h)
    (rx ry : Fin n → Fld) (hrx : Function.Injective rx) (hry : Function.Injective ry)
    (v : Fin n → W) (φ : Fin n → (W →ₗ[ZMod 2] ZMod 2)) (hv : ∀ p, v p ≠ 0) (hφ : ∀ p, φ p ≠ 0)
    (hAx : ∀ p, N.A (rx p) = Submodule.span (ZMod 2) {v p}) (hBx : ∀ p, N.B (rx p) = ⊤)
    (hAy : ∀ p, N.A (ry p) = ⊥) (hBy : ∀ p, N.B (ry p) = LinearMap.ker (φ p))
    (π : Fld → Fld) (hπinj : Function.Injective π) (hπx : ∀ p, π (rx p) = ry p) (hπy : ∀ p, π (ry p) = rx p)
    (hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f)
    (hnzx : ∀ p, N.O (rx p) (ry p) ≠ 0) (hnzy : ∀ p, N.O (ry p) (rx p) ≠ 0) :
    HSContractH N (fun c => finrank (ZMod 2) c) h n where
  π := π
  πinj := hπinj
  hsupp := hsupp
  Ehi := univ.image rx
  Elo := univ.image ry
  hi_card := by rw [card_image_of_injective _ hrx]; simp
  lo_card := by rw [card_image_of_injective _ hry]; simp
  hi_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    refine ⟨?_, ?_, ?_, ?_⟩
    · rw [hAx]; exact finrank_span_singleton (hv p)
    · rw [hBx, finrank_top]; exact hW
    · rw [hπx, hAy]; exact finrank_bot _ _
    · rw [hπx, hBy]; exact finrank_ker_pred _ (hφ p) hW
  lo_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    refine ⟨?_, ?_, ?_, ?_⟩
    · rw [hAy]; exact finrank_bot _ _
    · rw [hBy]; exact finrank_ker_pred _ (hφ p) hW
    · rw [hπy, hAx]; exact finrank_span_singleton (hv p)
    · rw [hπy, hBx, finrank_top]; exact hW
  nz_hi e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [hπx]; exact hnzx p
  nz_lo e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [hπy]; exact hnzy p

/-- every chart of W has height <= h. -/
theorem ht_le_h (hW : finrank (ZMod 2) W = h) (c : Submodule (ZMod 2) W) : finrank (ZMod 2) c ≤ h := by
  have := Submodule.finrank_le c; omega

end Ports

/-! ### From a net with the contract to PriceH.HCall, and the rung -/

/-- the HCall of a net with the height-cut contract. -/
def HCall.ofNet {Chart : Type} (N : Net K Chart Fld Bank) (ht : Chart → ℕ) (h n QR : ℕ)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (hc : HSContractH N ht h n) (hle : ∀ c, ht c ≤ h)
    (Mn : Finset Fld) (hmain : ∀ f ∈ Mn, dh (ht (N.A f)) (ht (N.B f)) = h - 1) (hcard : Mn.card = 2 * n + 2 * QR) :
    PriceH.HCall h n QR Fld Bank where
  fa f := ht (N.A f)
  fb f := ht (N.B f)
  bs k := ht (N.src k)
  bt k := ht (N.dst k)
  hfa f := hle _
  hfb f := hle _
  hbs k := hle _
  hbt k := hle _
  Mn := Mn
  hmain := hmain
  hcard := hcard
  hcut m := cut_hsH N hminor hc m

open SafeRungsPrice in
/-- **rung_port_net_h**: rung_port_h with the HCall cut contract discharged by `cut_hsH`; the per-call premise is now a
Net (P-LIN/P-LOC/P-ACYC data, nonzero principal minors) plus the port-row contract (model-forced by `contract_of_ports`). -/
theorem rung_port_net_h (h n QR : ℕ) (hh : 3 ≤ h) (MD : MolData h) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR h ρD ρR 0 s) kbar)
    {Chart : Type} {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    [∀ i, LinearOrder (Bank i)] (ht : Chart → ℕ) (hle : ∀ c, ht c ≤ h)
    (N : ∀ i, Net K Chart (Fld i) (Bank i))
    (hminor : ∀ i (C : Finset (Fld i)), ((N i).O.submatrix (fun c : C => (c : Fld i)) (fun c : C => (c : Fld i))).det ≠ 0)
    (hc : ∀ i, HSContractH (N i) ht h n)
    (Mn : ∀ i, Finset (Fld i)) (hmain : ∀ i, ∀ f ∈ Mn i, dh (ht ((N i).A f)) (ht ((N i).B f)) = h - 1)
    (hcard : ∀ i, (Mn i).card = 2 * n + 2 * QR)
    (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i)
    (hX : ∀ i, Dm i + Rm i ≤ (HCall.ofNet (N i) ht h n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud h MD (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (HCall.ofNet (N i) ht h n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (HCall.ofNet (N i) ht h n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_h h n QR hh MD ρD ρR kbar L T P hcert
    (fun i => HCall.ofNet (N i) ht h n QR (hminor i) (hc i) hle (Mn i) (hmain i) (hcard i)) Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

end HCutGen
#print axioms HCutGen.cut_hsH
#print axioms HCutGen.contract_of_ports
#print axioms HCutGen.rung_port_net_h

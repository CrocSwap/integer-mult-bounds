/-
BankTieB (lane LEAN-TIE, Nov 18).  Fixes AUDIT-BANNERLEAN (2b) and restates the banner with every hypothesis about G.
  gModel G oi oc : the XBal model BUILT FROM G: charts = Submodule (ZMod 2) V (G's own chart type), heights = finrank,
                   moves = G's banks (N.src → N.dst), publics = G's fields (born N.A, finish N.B); only the owned
                   registers (oi = INIT chart, oc = CLEAR chart) are extra data (BankedGraph does not carry them).
  gX             : gModel as a BankBanner.XModel (all chart identities by rfl), so Model.D = descMass G, Model.X = excess G.
  xbal_tied      : Flow(gModel) ∧ W ≥ 0 ⟹ 2·descMass G ≤ excess G.
  bank_kappa_lt_banner_tied : #7761 banner κ < .009526828 with D ≥ 56 from BankTieA.tie_desc_ge_56 and X ≥ 2D from xbal_tied.
NOTE (audit 2b, still true): with free owned registers Flow is always satisfiable and then W = A − D − Σc, so
  "Flow ∧ W ≥ 0" is exactly "A ≥ D + Σc"; W ≥ 0 stays a NAMED premise about the word's real owned registers.
Kernel only.
-/
import Nov15.BankTieA

namespace BankTie
open Finset Module BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall BankWireC

abbrev Chart := Submodule (ZMod 2) V

noncomputable instance : Fintype Chart := by
  have : Finite Chart := Finite.of_injective (fun S : Chart => (S : Set V)) SetLike.coe_injective
  exact Fintype.ofFinite _

noncomputable instance : DecidableEq Chart := Classical.decEq _

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- the XBal event-list model of G itself (plus owned registers). -/
noncomputable def gModel (G : BankedGraph ℚ Fld Bank) {O : Type} (oi oc : O → Chart) : XBal.Model Chart Bank Fld O where
  h c := (ht c : ℤ)
  src := G.N.src
  dst := G.N.dst
  ini := G.N.A
  fin := G.N.B
  oinit := oi
  oclear := oc

noncomputable def gX (G : BankedGraph ℚ Fld Bank) {O : Type} [Fintype O] (oi oc : O → Chart) : XModel G Chart O where
  M := gModel G oi oc
  hsrc := fun _ => rfl
  hdst := fun _ => rfl
  hini := fun _ => rfl
  hfin := fun _ => rfl

theorem xbal_tied (G : BankedGraph ℚ Fld Bank) {O : Type} [Fintype O] (oi oc : O → Chart)
    (hF : (gModel G oi oc).Flow) (hW : 0 ≤ (gModel G oi oc).W) : 2 * descMass G ≤ excess G :=
  xbal_bank G (gX G oi oc) hF hW

/-- **#7761 banner, every hypothesis about the graphs G i** (per call: tied chains, output spec, chain mediation,
owned registers with Flow and W ≥ 0; HSContract; P-1S' hpaid; P-CALLER' hcaller). -/
theorem bank_kappa_lt_banner_tied (G : Fin 2048 → BankedGraph ℚ Fld Bank) (hc : ∀ i, HSContract (G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (G i) T) (h8 : Fintype.card T ≤ 8)
    (hC : ∀ i, Computes (G i) (τ i).xin (τ i).yout) (hM : ∀ i, Mediated (τ i))
    {O : Type} [Fintype O] (oi oc : Fin 2048 → O → Chart)
    (hF : ∀ i, (gModel (G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankBannerCert.TB - cdat (1 - κ) BankBannerCert.PB) :
    κ < 2381707 / 250000000 :=
  bank_kappa_lt_banner G hc (fun i => tie_desc_ge_56 (τ i) h8 (hC i) (hM i))
    (fun i => xbal_tied (G i) (oi i) (oc i) (hF i) (hW i)) κ hκ0 hκ1 paid hpaid hcaller

end BankTie
#print axioms BankTie.xbal_tied
#print axioms BankTie.bank_kappa_lt_banner_tied

/-
BankTieC .  SCALED output spec.  Finding from Bridge7761G1: #7761's output diagonal O(yout t)(xin t) is 1 for 96 of the
104 live pairs but 1/2 for 8, so `Computes` (= 1) of BankTieA is false for the real graph.  ComputesS / MediatedS carry nonzero scalars c t:
  ComputesS : O(yout t)(xin t) = c t ≠ 0, 0 on odd t ≠ s;
  MediatedS : O(yout s)(xin p) = c s · Σ_x d(e x)(xin p) · gath_x s   (gathers normalised by c s, as in Bridge7761D5);
  realisesS, tie_desc_ge_56S, bank_kappa_lt_banner_tiedS : same conclusion as BankTieB with the scaled hypotheses.  Kernel only.
-/
import Nov15.BankTieB

namespace BankTie
open Finset Module BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall BankWireC

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

def ComputesS (G : BankedGraph ℚ Fld Bank) (xin yout : Fin 104 → Fld) (c : Fin 104 → ℚ) : Prop :=
  (∀ t, c t ≠ 0 ∧ G.N.O (yout t) (xin t) = c t) ∧
  ∀ t s, t ≠ s → dot (DF.lq t) (DF.lq s) = 1 → G.N.O (yout s) (xin t) = 0

variable {G : BankedGraph ℚ Fld Bank} {T : Type} [Fintype T]

def MediatedS (τ : ChainTie G T) (c : Fin 104 → ℚ) : Prop :=
  ∀ p s, dot (DF.lq p) (DF.lq s) = 1 →
    G.N.O (τ.yout s) (τ.xin p) = c s *
      ∑ x : (Σ c : T, Fin (τ.L.len c)), G.N.d (τ.e x) (τ.xin p) * (τ.L.chain x.1).gath x.2 s

theorem realisesS (τ : ChainTie G T) (c : Fin 104 → ℚ) (hC : ComputesS G τ.xin τ.yout c)
    (hM : MediatedS τ c) : τ.L.Realises where
  diag := fun t => by
    rw [block_eq_G]
    have h := hM t t (ChainRow.lq_odd t)
    rw [(hC.1 t).2] at h
    exact mul_left_cancel₀ (hC.1 t).1 (by rw [mul_one]; exact h.symm)
  odd := fun t s hts h => by
    rw [block_eq_G]
    have h2 := hM t s h
    rw [hC.2 t s hts h] at h2
    exact (mul_eq_zero.1 h2.symm).resolve_left (hC.1 s).1

theorem tie_desc_ge_56S (τ : ChainTie G T) (c : Fin 104 → ℚ) (h8 : Fintype.card T ≤ 8)
    (hC : ComputesS G τ.xin τ.yout c) (hM : MediatedS τ c) : 56 ≤ descMass G := by
  have := ChainRow.chain_mass_ge_56 τ.L (realisesS τ c hC hM) h8
  have : (56 : ℤ) ≤ (τ.L.descentMass : ℤ) := by exact_mod_cast this
  have := layout_desc_le τ
  linarith

theorem bank_kappa_lt_banner_tiedS (G : Fin 2048 → BankedGraph ℚ Fld Bank) (hc : ∀ i, HSContract (G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (G i) T) (h8 : Fintype.card T ≤ 8) (c : Fin 2048 → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (G i) (τ i).xin (τ i).yout (c i)) (hM : ∀ i, MediatedS (τ i) (c i))
    {O : Type} [Fintype O] (oi oc : Fin 2048 → O → Chart)
    (hF : ∀ i, (gModel (G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankBannerCert.TB - cdat (1 - κ) BankBannerCert.PB) :
    κ < 2381707 / 250000000 :=
  bank_kappa_lt_banner G hc (fun i => tie_desc_ge_56S (τ i) (c i) h8 (hC i) (hM i))
    (fun i => xbal_tied (G i) (oi i) (oc i) (hF i) (hW i)) κ hκ0 hκ1 paid hpaid hcaller

end BankTie
#print axioms BankTie.realisesS
#print axioms BankTie.bank_kappa_lt_banner_tiedS

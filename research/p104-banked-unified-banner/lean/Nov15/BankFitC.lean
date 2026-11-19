/-
BankFitC .  Tight grid version of BankFitA.bank_kappa_lt_flag: #7761 flag rung κ < 19933/1000000
(= .019933; root .0199325064), certificate BankFitCertB (grid denominators 10^6).  Same premises.  Kernel only.
-/
import Nov15.BankFitA
import Nov15.BankFitCertB

namespace BankFit
open Finset Module BankNC0 BankWireC BankWireD BankHelp SafeRungsPrice

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

theorem bank_kappa_lt_flag_tight (G : Fin 2048 → BankedGraph K Fld Bank) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankFitCertFit7761X28B.TB - cdat (1 - κ) BankFitCertFit7761X28B.PB) :
    κ < 19933 / 1000000 := by
  have hcert : Cert (fun s => cdat s BankFitCertFit7761X28B.TB - cdat s BankFitCertFit7761X28B.PB -
      ((2048 : ℕ) : ℝ) * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s))) (19933 / 1000000) := by
    intro t h1 h2
    have := BankFitCertFit7761X28B.cert t h1 h2
    unfold BankFitCertFit7761X28B.FceilBank at this
    push_cast
    linarith
  exact bank_kappa_lt_of_cert 2048 _ _ _ hcert G κ hκ0 hκ1 paid hpaid hcaller

end BankFit
#print axioms BankFit.bank_kappa_lt_flag_tight

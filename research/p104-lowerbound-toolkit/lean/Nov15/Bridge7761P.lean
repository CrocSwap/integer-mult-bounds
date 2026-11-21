/-
Bridge7761P (lane BRIDGE-HO, Nov 18).  Final assembly: BRIDGE7's kappa7761_lt_banner with hO DISCHARGED (hO7761, Bridge7761PG).
The only remaining hypothesis is hV (Valid: the SPEC invoice crossing).  Kernel only.
-/
import Nov15.Bridge7761S2
import Nov15.Bridge7761PG
namespace Bridge7761
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankPrem

theorem kappa7761_lt_banner_hO (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 2381707 / 250000000 :=
  kappa7761_lt_banner hO7761 κ hκ0 hκ1 hV

end Bridge7761
#print axioms Bridge7761.hO7761
#print axioms Bridge7761.kappa7761_lt_banner_hO

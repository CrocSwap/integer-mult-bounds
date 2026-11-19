/-
Bridge7761R3 .  BankedGraph fields `climb`, `cl`, `Mn`, `main8`, `card` for #7761 (fields as Fin 1262, charts ChA7761/ChB7761 of G2):
  cl7761 f = height gain; climb7761 : ChA f <= ChB f and finrank ChB = finrank ChA + cl f; Mn7761 = the 400 main fields (D2 mainL), main8_7761 : cl = 8 on Mn, card_Mn7761 : Mn.card = 400.
Kernel only.
-/
import Nov15.Bridge7761R2
namespace Bridge7761
open Finset Module BankNC0

def clN (f : ℕ) : ℕ := (hp (sl FBK 11 f) - hp (sl FAK 11 f)).toNat
def climbB (f : ℕ) : Bool := leP (sl FAK 11 f) (sl FBK 11 f) && decide (hp (sl FAK 11 f) ≤ hp (sl FBK 11 f))
theorem cb0 : (List.range' 0 421).all climbB = true := by decide +kernel
theorem cb1 : (List.range' 421 421).all climbB = true := by decide +kernel
end Bridge7761

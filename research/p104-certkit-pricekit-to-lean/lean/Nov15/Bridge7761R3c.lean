/- Bridge7761R3c (LEAN-BRIDGE6): main-field facts via a packed bitset MB (tied to D2 mainL by pack_main). -/
import Nov15.Bridge7761R3b
import Nov15.Bridge7761R3D
namespace Bridge7761
open Finset Module BankNC0
def pkbits : List Bool → Nat
  | [] => 0
  | b :: l => (if b then 1 else 0) + 2 * pkbits l
theorem pack_main : pkbits mainL = MB := by decide +kernel
def Mn7761 : Finset (Fin 1262) := Finset.univ.filter (fun f => MB.testBit f = true)
theorem card_Mn7761 : Mn7761.card = 400 := by decide +kernel
theorem main8_chk : ∀ f : Fin 1262, MB.testBit f = true → hp (sl FBK 11 f) - hp (sl FAK 11 f) = 8 := by decide +kernel
end Bridge7761

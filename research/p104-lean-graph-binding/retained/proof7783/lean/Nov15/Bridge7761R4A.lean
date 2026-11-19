/-
Bridge7761R4A .  Side-condition checkers for the #7761 recipe chunks (data in Bridge7761R4D*; 1500 terms per chunk).
Term t of chunk word w with slot width b is `sl w b (t % 1500)`.  Three families:
  chkF n ff fb : field terms  g = sl ff 11 t, owner bank k = sl fb 13 t :  A g = src k      (ids equal, fA g = bS k)
  chkR n rj rk : bank refs    j = sl rj 13 t, owner k = sl rk 13 t     :  j < k, dst j = src k   (bT j = bS k)
  chkO n oj of : output refs  j = sl oj 13 t, output field f = sl of 11 t :  dst j = B f      (bT j = fB f)
Kernel only.
-/
import Nov15.Bridge7761R3
namespace Bridge7761
open Finset Module BankNC0

def chkF (n ff fb : ℕ) : Bool := (List.range n).all fun t =>
  decide (sl ff 11 t < 1262) && decide (sl fb 13 t < 5746) && (sl FAK 11 (sl ff 11 t) == sl BSK 11 (sl fb 13 t))
def chkR (n rj rk : ℕ) : Bool := (List.range n).all fun t =>
  decide (sl rj 13 t < sl rk 13 t) && decide (sl rk 13 t < 5746) && (sl BTK 11 (sl rj 13 t) == sl BSK 11 (sl rk 13 t))
def chkO (n oj of : ℕ) : Bool := (List.range n).all fun t =>
  decide (sl oj 13 t < 5746) && decide (sl of 11 t < 1262) && (sl BTK 11 (sl oj 13 t) == sl FBK 11 (sl of 11 t))
end Bridge7761

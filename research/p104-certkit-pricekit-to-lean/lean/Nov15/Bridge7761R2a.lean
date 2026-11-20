/-
Bridge7761R2a (lane LEAN-BRIDGE6, Nov 18).  Bank nest chunks: nestB over banks [0, 1200) (decide +kernel, O(1) packed chart tables of R1).  Kernel only.
-/
import Nov15.Bridge7761R1
namespace Bridge7761
open Finset Module

def srcId (k : ℕ) : ℕ := sl BSK 11 k
def dstId (k : ℕ) : ℕ := sl BTK 11 k
def nestB (k : ℕ) : Bool := decide (srcId k < 1099) && decide (dstId k < 1099) && (leP (srcId k) (dstId k) || leP (dstId k) (srcId k))
theorem nc0 : (List.range' 0 400).all nestB = true := by decide +kernel
theorem nc1 : (List.range' 400 400).all nestB = true := by decide +kernel
theorem nc2 : (List.range' 800 400).all nestB = true := by decide +kernel
end Bridge7761

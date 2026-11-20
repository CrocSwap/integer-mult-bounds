/-
Bridge7761R2b (lane LEAN-BRIDGE6, Nov 18).  Bank nest chunks: nestB over banks [1200, 2400) (decide +kernel, O(1) packed chart tables of R1).  Kernel only.
-/
import Nov15.Bridge7761R2a
namespace Bridge7761
open Finset Module
theorem nc3 : (List.range' 1200 400).all nestB = true := by decide +kernel
theorem nc4 : (List.range' 1600 400).all nestB = true := by decide +kernel
theorem nc5 : (List.range' 2000 400).all nestB = true := by decide +kernel
end Bridge7761

/-
Bridge7761R2e .  Bank nest chunks: nestB over banks [4800, 6000) (decide +kernel, O(1) packed chart tables of R1).  Kernel only.
-/
import Nov15.Bridge7761R2d
namespace Bridge7761
open Finset Module
theorem nc12 : (List.range' 4800 400).all nestB = true := by decide +kernel
theorem nc13 : (List.range' 5200 400).all nestB = true := by decide +kernel
theorem nc14 : (List.range' 5600 400).all nestB = true := by decide +kernel
end Bridge7761

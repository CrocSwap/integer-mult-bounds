/-
Bridge7761R2c .  Bank nest chunks: nestB over banks [2400, 3600) (decide +kernel, O(1) packed chart tables of R1).  Kernel only.
-/
import Nov15.Bridge7761R2b
namespace Bridge7761
open Finset Module
theorem nc6 : (List.range' 2400 400).all nestB = true := by decide +kernel
theorem nc7 : (List.range' 2800 400).all nestB = true := by decide +kernel
theorem nc8 : (List.range' 3200 400).all nestB = true := by decide +kernel
end Bridge7761

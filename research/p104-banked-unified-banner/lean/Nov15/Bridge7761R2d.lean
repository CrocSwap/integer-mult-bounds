/-
Bridge7761R2d .  Bank nest chunks: nestB over banks [3600, 4800) (decide +kernel, O(1) packed chart tables of R1).  Kernel only.
-/
import Nov15.Bridge7761R2c
namespace Bridge7761
open Finset Module
theorem nc9 : (List.range' 3600 400).all nestB = true := by decide +kernel
theorem nc10 : (List.range' 4000 400).all nestB = true := by decide +kernel
theorem nc11 : (List.range' 4400 400).all nestB = true := by decide +kernel
end Bridge7761

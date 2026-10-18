/-
SPDX-License-Identifier: Apache-2.0
INTENTIONAL COMPILE-FAIL CONTROL. Not imported by any positive source.
After rewriting with proved entry values, ordinary decide must reject 1 = -1.
An import, syntax, elaboration, timeout, or other failure is NOT acceptance.
-/
import P112Damaged

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

open PR1497 P112Cert P112Cert.Damaged

example : matSub (eye 104) (matMul P Q) (5 : Fin 104) (0 : Fin 104) =
    matMul W_bad M (5 : Fin 104) (0 : Fin 104) := by
  rw [residual_entry, damaged_product_entry]
  decide

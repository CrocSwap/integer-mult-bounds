/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0
SOURCE ONLY / NOT YET KERNEL CHECKED.
Source-specific W sign corruption control, in the spirit of the inherited
PR1497 verify.py W-corruption control. This exact damaged entry proof is new.
Proof/source assistance: GPT-6 Pro through ChatGPT (operator-selected label).
-/
import P112Certificate

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace P112Cert.Damaged
open PR1497

/-- Exactly W[5,0] is changed from +1 to -1; all other rows are retained. -/
def W_entries_bad (i : Fin 104) : List (Fin 288 × Int) :=
  if i.val = 5 then [(⟨0, by decide⟩, (-1 : Int))] else W_entries i

def W_bad : Mat 104 288 := fun i => Sparse.row (W_entries_bad i)

theorem original_coefficient : W (5 : Fin 104) (0 : Fin 288) = 1 := by
  decide

theorem damaged_coefficient : W_bad (5 : Fin 104) (0 : Fin 288) = -1 := by
  decide

theorem unchanged_other_rows (i : Fin 104) (hi : i.val ≠ 5) : W_bad i = W i := by
  change Sparse.row (if i.val = 5 then [(⟨0, by decide⟩, (-1 : Int))]
    else W_entries i) = Sparse.row (W_entries i)
  rw [if_neg hi]

/-- The intended left residual at (5,0) is +1, computed through the sound adapter. -/
theorem residual_entry :
    matSub (eye 104) (matMul P Q) (5 : Fin 104) (0 : Fin 104) = 1 := by
  change eye 104 (5 : Fin 104) (0 : Fin 104) -
    rowMul (Sparse.row (P_entries (5 : Fin 104))) Q (0 : Fin 104) = (1 : Int)
  have hp := congrArg (fun v : Row 104 => v (0 : Fin 104))
    (Sparse.rowMul_row (P_entries (5 : Fin 104)) Q)
  change rowMul (Sparse.row (P_entries (5 : Fin 104))) Q (0 : Fin 104) =
    Sparse.eval (P_entries (5 : Fin 104)) Q (0 : Fin 104) at hp
  rw [hp]
  decide

/-- The corrupted right residual at (5,0) is -1, not +1. -/
theorem damaged_product_entry :
    matMul W_bad M (5 : Fin 104) (0 : Fin 104) = -1 := by
  change rowMul (Sparse.row (W_entries_bad (5 : Fin 104))) M (0 : Fin 104) = (-1 : Int)
  have hw := congrArg (fun v : Row 104 => v (0 : Fin 104))
    (Sparse.rowMul_row (W_entries_bad (5 : Fin 104)) M)
  change rowMul (Sparse.row (W_entries_bad (5 : Fin 104))) M (0 : Fin 104) =
    Sparse.eval (W_entries_bad (5 : Fin 104)) M (0 : Fin 104) at hw
  rw [hw]
  decide

theorem not_residual : matSub (eye 104) (matMul P Q) ≠ matMul W_bad M := by
  intro h
  have he := congrArg (fun A : Mat 104 104 => A (5 : Fin 104) (0 : Fin 104)) h
  change matSub (eye 104) (matMul P Q) (5 : Fin 104) (0 : Fin 104) =
    matMul W_bad M (5 : Fin 104) (0 : Fin 104) at he
  rw [residual_entry, damaged_product_entry] at he
  exact (by decide : (1 : Int) ≠ -1) he

theorem no_certificate : ¬ MatrixIdentities M P Q W_bad :=
  fun h => not_residual h.residual

end P112Cert.Damaged

set_option pp.fullNames true
#print axioms P112Cert.Damaged.W_entries_bad
#print axioms P112Cert.Damaged.W_bad
#print axioms P112Cert.Damaged.original_coefficient
#print axioms P112Cert.Damaged.damaged_coefficient
#print axioms P112Cert.Damaged.unchanged_other_rows
#print axioms P112Cert.Damaged.residual_entry
#print axioms P112Cert.Damaged.damaged_product_entry
#print axioms P112Cert.Damaged.not_residual
#print axioms P112Cert.Damaged.no_certificate

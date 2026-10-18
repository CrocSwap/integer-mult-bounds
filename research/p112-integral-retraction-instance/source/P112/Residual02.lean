/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0
P112 numerical instance of the unchanged PR1497/PR1610 bridge.
SOURCE ONLY / NOT YET KERNEL CHECKED. Generated deterministically by generate.py.
Proof/source assistance: GPT-6 Pro through ChatGPT (operator-selected label).
-/
import P112Data

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace P112Cert
open PR1497

/-- Complete residual row 16, not a sampled set of columns. -/
theorem residual_row_016 :
    ∀ j : Fin 104, eye 104 ⟨16, by decide⟩ j - Sparse.eval (P_entries ⟨16, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨16, by decide⟩) M j := by
  decide

/-- Complete residual row 17, not a sampled set of columns. -/
theorem residual_row_017 :
    ∀ j : Fin 104, eye 104 ⟨17, by decide⟩ j - Sparse.eval (P_entries ⟨17, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨17, by decide⟩) M j := by
  decide

/-- Complete residual row 18, not a sampled set of columns. -/
theorem residual_row_018 :
    ∀ j : Fin 104, eye 104 ⟨18, by decide⟩ j - Sparse.eval (P_entries ⟨18, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨18, by decide⟩) M j := by
  decide

/-- Complete residual row 19, not a sampled set of columns. -/
theorem residual_row_019 :
    ∀ j : Fin 104, eye 104 ⟨19, by decide⟩ j - Sparse.eval (P_entries ⟨19, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨19, by decide⟩) M j := by
  decide

/-- Complete residual row 20, not a sampled set of columns. -/
theorem residual_row_020 :
    ∀ j : Fin 104, eye 104 ⟨20, by decide⟩ j - Sparse.eval (P_entries ⟨20, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨20, by decide⟩) M j := by
  decide

/-- Complete residual row 21, not a sampled set of columns. -/
theorem residual_row_021 :
    ∀ j : Fin 104, eye 104 ⟨21, by decide⟩ j - Sparse.eval (P_entries ⟨21, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨21, by decide⟩) M j := by
  decide

/-- Complete residual row 22, not a sampled set of columns. -/
theorem residual_row_022 :
    ∀ j : Fin 104, eye 104 ⟨22, by decide⟩ j - Sparse.eval (P_entries ⟨22, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨22, by decide⟩) M j := by
  decide

/-- Complete residual row 23, not a sampled set of columns. -/
theorem residual_row_023 :
    ∀ j : Fin 104, eye 104 ⟨23, by decide⟩ j - Sparse.eval (P_entries ⟨23, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨23, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_016
#print axioms P112Cert.residual_row_017
#print axioms P112Cert.residual_row_018
#print axioms P112Cert.residual_row_019
#print axioms P112Cert.residual_row_020
#print axioms P112Cert.residual_row_021
#print axioms P112Cert.residual_row_022
#print axioms P112Cert.residual_row_023

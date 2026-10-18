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

/-- Complete residual row 24, not a sampled set of columns. -/
theorem residual_row_024 :
    ∀ j : Fin 104, eye 104 ⟨24, by decide⟩ j - Sparse.eval (P_entries ⟨24, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨24, by decide⟩) M j := by
  decide

/-- Complete residual row 25, not a sampled set of columns. -/
theorem residual_row_025 :
    ∀ j : Fin 104, eye 104 ⟨25, by decide⟩ j - Sparse.eval (P_entries ⟨25, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨25, by decide⟩) M j := by
  decide

/-- Complete residual row 26, not a sampled set of columns. -/
theorem residual_row_026 :
    ∀ j : Fin 104, eye 104 ⟨26, by decide⟩ j - Sparse.eval (P_entries ⟨26, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨26, by decide⟩) M j := by
  decide

/-- Complete residual row 27, not a sampled set of columns. -/
theorem residual_row_027 :
    ∀ j : Fin 104, eye 104 ⟨27, by decide⟩ j - Sparse.eval (P_entries ⟨27, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨27, by decide⟩) M j := by
  decide

/-- Complete residual row 28, not a sampled set of columns. -/
theorem residual_row_028 :
    ∀ j : Fin 104, eye 104 ⟨28, by decide⟩ j - Sparse.eval (P_entries ⟨28, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨28, by decide⟩) M j := by
  decide

/-- Complete residual row 29, not a sampled set of columns. -/
theorem residual_row_029 :
    ∀ j : Fin 104, eye 104 ⟨29, by decide⟩ j - Sparse.eval (P_entries ⟨29, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨29, by decide⟩) M j := by
  decide

/-- Complete residual row 30, not a sampled set of columns. -/
theorem residual_row_030 :
    ∀ j : Fin 104, eye 104 ⟨30, by decide⟩ j - Sparse.eval (P_entries ⟨30, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨30, by decide⟩) M j := by
  decide

/-- Complete residual row 31, not a sampled set of columns. -/
theorem residual_row_031 :
    ∀ j : Fin 104, eye 104 ⟨31, by decide⟩ j - Sparse.eval (P_entries ⟨31, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨31, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_024
#print axioms P112Cert.residual_row_025
#print axioms P112Cert.residual_row_026
#print axioms P112Cert.residual_row_027
#print axioms P112Cert.residual_row_028
#print axioms P112Cert.residual_row_029
#print axioms P112Cert.residual_row_030
#print axioms P112Cert.residual_row_031

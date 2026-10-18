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

/-- Complete residual row 32, not a sampled set of columns. -/
theorem residual_row_032 :
    ∀ j : Fin 104, eye 104 ⟨32, by decide⟩ j - Sparse.eval (P_entries ⟨32, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨32, by decide⟩) M j := by
  decide

/-- Complete residual row 33, not a sampled set of columns. -/
theorem residual_row_033 :
    ∀ j : Fin 104, eye 104 ⟨33, by decide⟩ j - Sparse.eval (P_entries ⟨33, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨33, by decide⟩) M j := by
  decide

/-- Complete residual row 34, not a sampled set of columns. -/
theorem residual_row_034 :
    ∀ j : Fin 104, eye 104 ⟨34, by decide⟩ j - Sparse.eval (P_entries ⟨34, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨34, by decide⟩) M j := by
  decide

/-- Complete residual row 35, not a sampled set of columns. -/
theorem residual_row_035 :
    ∀ j : Fin 104, eye 104 ⟨35, by decide⟩ j - Sparse.eval (P_entries ⟨35, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨35, by decide⟩) M j := by
  decide

/-- Complete residual row 36, not a sampled set of columns. -/
theorem residual_row_036 :
    ∀ j : Fin 104, eye 104 ⟨36, by decide⟩ j - Sparse.eval (P_entries ⟨36, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨36, by decide⟩) M j := by
  decide

/-- Complete residual row 37, not a sampled set of columns. -/
theorem residual_row_037 :
    ∀ j : Fin 104, eye 104 ⟨37, by decide⟩ j - Sparse.eval (P_entries ⟨37, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨37, by decide⟩) M j := by
  decide

/-- Complete residual row 38, not a sampled set of columns. -/
theorem residual_row_038 :
    ∀ j : Fin 104, eye 104 ⟨38, by decide⟩ j - Sparse.eval (P_entries ⟨38, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨38, by decide⟩) M j := by
  decide

/-- Complete residual row 39, not a sampled set of columns. -/
theorem residual_row_039 :
    ∀ j : Fin 104, eye 104 ⟨39, by decide⟩ j - Sparse.eval (P_entries ⟨39, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨39, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_032
#print axioms P112Cert.residual_row_033
#print axioms P112Cert.residual_row_034
#print axioms P112Cert.residual_row_035
#print axioms P112Cert.residual_row_036
#print axioms P112Cert.residual_row_037
#print axioms P112Cert.residual_row_038
#print axioms P112Cert.residual_row_039

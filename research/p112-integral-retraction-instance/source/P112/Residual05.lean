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

/-- Complete residual row 40, not a sampled set of columns. -/
theorem residual_row_040 :
    ∀ j : Fin 104, eye 104 ⟨40, by decide⟩ j - Sparse.eval (P_entries ⟨40, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨40, by decide⟩) M j := by
  decide

/-- Complete residual row 41, not a sampled set of columns. -/
theorem residual_row_041 :
    ∀ j : Fin 104, eye 104 ⟨41, by decide⟩ j - Sparse.eval (P_entries ⟨41, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨41, by decide⟩) M j := by
  decide

/-- Complete residual row 42, not a sampled set of columns. -/
theorem residual_row_042 :
    ∀ j : Fin 104, eye 104 ⟨42, by decide⟩ j - Sparse.eval (P_entries ⟨42, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨42, by decide⟩) M j := by
  decide

/-- Complete residual row 43, not a sampled set of columns. -/
theorem residual_row_043 :
    ∀ j : Fin 104, eye 104 ⟨43, by decide⟩ j - Sparse.eval (P_entries ⟨43, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨43, by decide⟩) M j := by
  decide

/-- Complete residual row 44, not a sampled set of columns. -/
theorem residual_row_044 :
    ∀ j : Fin 104, eye 104 ⟨44, by decide⟩ j - Sparse.eval (P_entries ⟨44, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨44, by decide⟩) M j := by
  decide

/-- Complete residual row 45, not a sampled set of columns. -/
theorem residual_row_045 :
    ∀ j : Fin 104, eye 104 ⟨45, by decide⟩ j - Sparse.eval (P_entries ⟨45, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨45, by decide⟩) M j := by
  decide

/-- Complete residual row 46, not a sampled set of columns. -/
theorem residual_row_046 :
    ∀ j : Fin 104, eye 104 ⟨46, by decide⟩ j - Sparse.eval (P_entries ⟨46, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨46, by decide⟩) M j := by
  decide

/-- Complete residual row 47, not a sampled set of columns. -/
theorem residual_row_047 :
    ∀ j : Fin 104, eye 104 ⟨47, by decide⟩ j - Sparse.eval (P_entries ⟨47, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨47, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_040
#print axioms P112Cert.residual_row_041
#print axioms P112Cert.residual_row_042
#print axioms P112Cert.residual_row_043
#print axioms P112Cert.residual_row_044
#print axioms P112Cert.residual_row_045
#print axioms P112Cert.residual_row_046
#print axioms P112Cert.residual_row_047

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

/-- Complete residual row 96, not a sampled set of columns. -/
theorem residual_row_096 :
    ∀ j : Fin 104, eye 104 ⟨96, by decide⟩ j - Sparse.eval (P_entries ⟨96, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨96, by decide⟩) M j := by
  decide

/-- Complete residual row 97, not a sampled set of columns. -/
theorem residual_row_097 :
    ∀ j : Fin 104, eye 104 ⟨97, by decide⟩ j - Sparse.eval (P_entries ⟨97, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨97, by decide⟩) M j := by
  decide

/-- Complete residual row 98, not a sampled set of columns. -/
theorem residual_row_098 :
    ∀ j : Fin 104, eye 104 ⟨98, by decide⟩ j - Sparse.eval (P_entries ⟨98, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨98, by decide⟩) M j := by
  decide

/-- Complete residual row 99, not a sampled set of columns. -/
theorem residual_row_099 :
    ∀ j : Fin 104, eye 104 ⟨99, by decide⟩ j - Sparse.eval (P_entries ⟨99, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨99, by decide⟩) M j := by
  decide

/-- Complete residual row 100, not a sampled set of columns. -/
theorem residual_row_100 :
    ∀ j : Fin 104, eye 104 ⟨100, by decide⟩ j - Sparse.eval (P_entries ⟨100, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨100, by decide⟩) M j := by
  decide

/-- Complete residual row 101, not a sampled set of columns. -/
theorem residual_row_101 :
    ∀ j : Fin 104, eye 104 ⟨101, by decide⟩ j - Sparse.eval (P_entries ⟨101, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨101, by decide⟩) M j := by
  decide

/-- Complete residual row 102, not a sampled set of columns. -/
theorem residual_row_102 :
    ∀ j : Fin 104, eye 104 ⟨102, by decide⟩ j - Sparse.eval (P_entries ⟨102, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨102, by decide⟩) M j := by
  decide

/-- Complete residual row 103, not a sampled set of columns. -/
theorem residual_row_103 :
    ∀ j : Fin 104, eye 104 ⟨103, by decide⟩ j - Sparse.eval (P_entries ⟨103, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨103, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_096
#print axioms P112Cert.residual_row_097
#print axioms P112Cert.residual_row_098
#print axioms P112Cert.residual_row_099
#print axioms P112Cert.residual_row_100
#print axioms P112Cert.residual_row_101
#print axioms P112Cert.residual_row_102
#print axioms P112Cert.residual_row_103

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

/-- Complete residual row 56, not a sampled set of columns. -/
theorem residual_row_056 :
    ∀ j : Fin 104, eye 104 ⟨56, by decide⟩ j - Sparse.eval (P_entries ⟨56, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨56, by decide⟩) M j := by
  decide

/-- Complete residual row 57, not a sampled set of columns. -/
theorem residual_row_057 :
    ∀ j : Fin 104, eye 104 ⟨57, by decide⟩ j - Sparse.eval (P_entries ⟨57, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨57, by decide⟩) M j := by
  decide

/-- Complete residual row 58, not a sampled set of columns. -/
theorem residual_row_058 :
    ∀ j : Fin 104, eye 104 ⟨58, by decide⟩ j - Sparse.eval (P_entries ⟨58, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨58, by decide⟩) M j := by
  decide

/-- Complete residual row 59, not a sampled set of columns. -/
theorem residual_row_059 :
    ∀ j : Fin 104, eye 104 ⟨59, by decide⟩ j - Sparse.eval (P_entries ⟨59, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨59, by decide⟩) M j := by
  decide

/-- Complete residual row 60, not a sampled set of columns. -/
theorem residual_row_060 :
    ∀ j : Fin 104, eye 104 ⟨60, by decide⟩ j - Sparse.eval (P_entries ⟨60, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨60, by decide⟩) M j := by
  decide

/-- Complete residual row 61, not a sampled set of columns. -/
theorem residual_row_061 :
    ∀ j : Fin 104, eye 104 ⟨61, by decide⟩ j - Sparse.eval (P_entries ⟨61, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨61, by decide⟩) M j := by
  decide

/-- Complete residual row 62, not a sampled set of columns. -/
theorem residual_row_062 :
    ∀ j : Fin 104, eye 104 ⟨62, by decide⟩ j - Sparse.eval (P_entries ⟨62, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨62, by decide⟩) M j := by
  decide

/-- Complete residual row 63, not a sampled set of columns. -/
theorem residual_row_063 :
    ∀ j : Fin 104, eye 104 ⟨63, by decide⟩ j - Sparse.eval (P_entries ⟨63, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨63, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_056
#print axioms P112Cert.residual_row_057
#print axioms P112Cert.residual_row_058
#print axioms P112Cert.residual_row_059
#print axioms P112Cert.residual_row_060
#print axioms P112Cert.residual_row_061
#print axioms P112Cert.residual_row_062
#print axioms P112Cert.residual_row_063

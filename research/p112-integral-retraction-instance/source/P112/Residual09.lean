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

/-- Complete residual row 72, not a sampled set of columns. -/
theorem residual_row_072 :
    ∀ j : Fin 104, eye 104 ⟨72, by decide⟩ j - Sparse.eval (P_entries ⟨72, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨72, by decide⟩) M j := by
  decide

/-- Complete residual row 73, not a sampled set of columns. -/
theorem residual_row_073 :
    ∀ j : Fin 104, eye 104 ⟨73, by decide⟩ j - Sparse.eval (P_entries ⟨73, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨73, by decide⟩) M j := by
  decide

/-- Complete residual row 74, not a sampled set of columns. -/
theorem residual_row_074 :
    ∀ j : Fin 104, eye 104 ⟨74, by decide⟩ j - Sparse.eval (P_entries ⟨74, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨74, by decide⟩) M j := by
  decide

/-- Complete residual row 75, not a sampled set of columns. -/
theorem residual_row_075 :
    ∀ j : Fin 104, eye 104 ⟨75, by decide⟩ j - Sparse.eval (P_entries ⟨75, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨75, by decide⟩) M j := by
  decide

/-- Complete residual row 76, not a sampled set of columns. -/
theorem residual_row_076 :
    ∀ j : Fin 104, eye 104 ⟨76, by decide⟩ j - Sparse.eval (P_entries ⟨76, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨76, by decide⟩) M j := by
  decide

/-- Complete residual row 77, not a sampled set of columns. -/
theorem residual_row_077 :
    ∀ j : Fin 104, eye 104 ⟨77, by decide⟩ j - Sparse.eval (P_entries ⟨77, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨77, by decide⟩) M j := by
  decide

/-- Complete residual row 78, not a sampled set of columns. -/
theorem residual_row_078 :
    ∀ j : Fin 104, eye 104 ⟨78, by decide⟩ j - Sparse.eval (P_entries ⟨78, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨78, by decide⟩) M j := by
  decide

/-- Complete residual row 79, not a sampled set of columns. -/
theorem residual_row_079 :
    ∀ j : Fin 104, eye 104 ⟨79, by decide⟩ j - Sparse.eval (P_entries ⟨79, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨79, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_072
#print axioms P112Cert.residual_row_073
#print axioms P112Cert.residual_row_074
#print axioms P112Cert.residual_row_075
#print axioms P112Cert.residual_row_076
#print axioms P112Cert.residual_row_077
#print axioms P112Cert.residual_row_078
#print axioms P112Cert.residual_row_079

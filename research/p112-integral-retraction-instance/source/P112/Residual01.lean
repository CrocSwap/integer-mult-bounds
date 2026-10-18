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

/-- Complete residual row 8, not a sampled set of columns. -/
theorem residual_row_008 :
    ∀ j : Fin 104, eye 104 ⟨8, by decide⟩ j - Sparse.eval (P_entries ⟨8, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨8, by decide⟩) M j := by
  decide

/-- Complete residual row 9, not a sampled set of columns. -/
theorem residual_row_009 :
    ∀ j : Fin 104, eye 104 ⟨9, by decide⟩ j - Sparse.eval (P_entries ⟨9, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨9, by decide⟩) M j := by
  decide

/-- Complete residual row 10, not a sampled set of columns. -/
theorem residual_row_010 :
    ∀ j : Fin 104, eye 104 ⟨10, by decide⟩ j - Sparse.eval (P_entries ⟨10, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨10, by decide⟩) M j := by
  decide

/-- Complete residual row 11, not a sampled set of columns. -/
theorem residual_row_011 :
    ∀ j : Fin 104, eye 104 ⟨11, by decide⟩ j - Sparse.eval (P_entries ⟨11, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨11, by decide⟩) M j := by
  decide

/-- Complete residual row 12, not a sampled set of columns. -/
theorem residual_row_012 :
    ∀ j : Fin 104, eye 104 ⟨12, by decide⟩ j - Sparse.eval (P_entries ⟨12, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨12, by decide⟩) M j := by
  decide

/-- Complete residual row 13, not a sampled set of columns. -/
theorem residual_row_013 :
    ∀ j : Fin 104, eye 104 ⟨13, by decide⟩ j - Sparse.eval (P_entries ⟨13, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨13, by decide⟩) M j := by
  decide

/-- Complete residual row 14, not a sampled set of columns. -/
theorem residual_row_014 :
    ∀ j : Fin 104, eye 104 ⟨14, by decide⟩ j - Sparse.eval (P_entries ⟨14, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨14, by decide⟩) M j := by
  decide

/-- Complete residual row 15, not a sampled set of columns. -/
theorem residual_row_015 :
    ∀ j : Fin 104, eye 104 ⟨15, by decide⟩ j - Sparse.eval (P_entries ⟨15, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨15, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_008
#print axioms P112Cert.residual_row_009
#print axioms P112Cert.residual_row_010
#print axioms P112Cert.residual_row_011
#print axioms P112Cert.residual_row_012
#print axioms P112Cert.residual_row_013
#print axioms P112Cert.residual_row_014
#print axioms P112Cert.residual_row_015

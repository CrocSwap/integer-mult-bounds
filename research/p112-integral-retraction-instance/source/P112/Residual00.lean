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

/-- Complete residual row 0, not a sampled set of columns. -/
theorem residual_row_000 :
    ∀ j : Fin 104, eye 104 ⟨0, by decide⟩ j - Sparse.eval (P_entries ⟨0, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨0, by decide⟩) M j := by
  decide

/-- Complete residual row 1, not a sampled set of columns. -/
theorem residual_row_001 :
    ∀ j : Fin 104, eye 104 ⟨1, by decide⟩ j - Sparse.eval (P_entries ⟨1, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨1, by decide⟩) M j := by
  decide

/-- Complete residual row 2, not a sampled set of columns. -/
theorem residual_row_002 :
    ∀ j : Fin 104, eye 104 ⟨2, by decide⟩ j - Sparse.eval (P_entries ⟨2, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨2, by decide⟩) M j := by
  decide

/-- Complete residual row 3, not a sampled set of columns. -/
theorem residual_row_003 :
    ∀ j : Fin 104, eye 104 ⟨3, by decide⟩ j - Sparse.eval (P_entries ⟨3, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨3, by decide⟩) M j := by
  decide

/-- Complete residual row 4, not a sampled set of columns. -/
theorem residual_row_004 :
    ∀ j : Fin 104, eye 104 ⟨4, by decide⟩ j - Sparse.eval (P_entries ⟨4, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨4, by decide⟩) M j := by
  decide

/-- Complete residual row 5, not a sampled set of columns. -/
theorem residual_row_005 :
    ∀ j : Fin 104, eye 104 ⟨5, by decide⟩ j - Sparse.eval (P_entries ⟨5, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨5, by decide⟩) M j := by
  decide

/-- Complete residual row 6, not a sampled set of columns. -/
theorem residual_row_006 :
    ∀ j : Fin 104, eye 104 ⟨6, by decide⟩ j - Sparse.eval (P_entries ⟨6, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨6, by decide⟩) M j := by
  decide

/-- Complete residual row 7, not a sampled set of columns. -/
theorem residual_row_007 :
    ∀ j : Fin 104, eye 104 ⟨7, by decide⟩ j - Sparse.eval (P_entries ⟨7, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨7, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_000
#print axioms P112Cert.residual_row_001
#print axioms P112Cert.residual_row_002
#print axioms P112Cert.residual_row_003
#print axioms P112Cert.residual_row_004
#print axioms P112Cert.residual_row_005
#print axioms P112Cert.residual_row_006
#print axioms P112Cert.residual_row_007

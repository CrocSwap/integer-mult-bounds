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

/-- Complete residual row 48, not a sampled set of columns. -/
theorem residual_row_048 :
    ∀ j : Fin 104, eye 104 ⟨48, by decide⟩ j - Sparse.eval (P_entries ⟨48, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨48, by decide⟩) M j := by
  decide

/-- Complete residual row 49, not a sampled set of columns. -/
theorem residual_row_049 :
    ∀ j : Fin 104, eye 104 ⟨49, by decide⟩ j - Sparse.eval (P_entries ⟨49, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨49, by decide⟩) M j := by
  decide

/-- Complete residual row 50, not a sampled set of columns. -/
theorem residual_row_050 :
    ∀ j : Fin 104, eye 104 ⟨50, by decide⟩ j - Sparse.eval (P_entries ⟨50, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨50, by decide⟩) M j := by
  decide

/-- Complete residual row 51, not a sampled set of columns. -/
theorem residual_row_051 :
    ∀ j : Fin 104, eye 104 ⟨51, by decide⟩ j - Sparse.eval (P_entries ⟨51, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨51, by decide⟩) M j := by
  decide

/-- Complete residual row 52, not a sampled set of columns. -/
theorem residual_row_052 :
    ∀ j : Fin 104, eye 104 ⟨52, by decide⟩ j - Sparse.eval (P_entries ⟨52, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨52, by decide⟩) M j := by
  decide

/-- Complete residual row 53, not a sampled set of columns. -/
theorem residual_row_053 :
    ∀ j : Fin 104, eye 104 ⟨53, by decide⟩ j - Sparse.eval (P_entries ⟨53, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨53, by decide⟩) M j := by
  decide

/-- Complete residual row 54, not a sampled set of columns. -/
theorem residual_row_054 :
    ∀ j : Fin 104, eye 104 ⟨54, by decide⟩ j - Sparse.eval (P_entries ⟨54, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨54, by decide⟩) M j := by
  decide

/-- Complete residual row 55, not a sampled set of columns. -/
theorem residual_row_055 :
    ∀ j : Fin 104, eye 104 ⟨55, by decide⟩ j - Sparse.eval (P_entries ⟨55, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨55, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_048
#print axioms P112Cert.residual_row_049
#print axioms P112Cert.residual_row_050
#print axioms P112Cert.residual_row_051
#print axioms P112Cert.residual_row_052
#print axioms P112Cert.residual_row_053
#print axioms P112Cert.residual_row_054
#print axioms P112Cert.residual_row_055

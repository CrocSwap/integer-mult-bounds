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

/-- Complete residual row 64, not a sampled set of columns. -/
theorem residual_row_064 :
    ∀ j : Fin 104, eye 104 ⟨64, by decide⟩ j - Sparse.eval (P_entries ⟨64, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨64, by decide⟩) M j := by
  decide

/-- Complete residual row 65, not a sampled set of columns. -/
theorem residual_row_065 :
    ∀ j : Fin 104, eye 104 ⟨65, by decide⟩ j - Sparse.eval (P_entries ⟨65, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨65, by decide⟩) M j := by
  decide

/-- Complete residual row 66, not a sampled set of columns. -/
theorem residual_row_066 :
    ∀ j : Fin 104, eye 104 ⟨66, by decide⟩ j - Sparse.eval (P_entries ⟨66, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨66, by decide⟩) M j := by
  decide

/-- Complete residual row 67, not a sampled set of columns. -/
theorem residual_row_067 :
    ∀ j : Fin 104, eye 104 ⟨67, by decide⟩ j - Sparse.eval (P_entries ⟨67, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨67, by decide⟩) M j := by
  decide

/-- Complete residual row 68, not a sampled set of columns. -/
theorem residual_row_068 :
    ∀ j : Fin 104, eye 104 ⟨68, by decide⟩ j - Sparse.eval (P_entries ⟨68, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨68, by decide⟩) M j := by
  decide

/-- Complete residual row 69, not a sampled set of columns. -/
theorem residual_row_069 :
    ∀ j : Fin 104, eye 104 ⟨69, by decide⟩ j - Sparse.eval (P_entries ⟨69, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨69, by decide⟩) M j := by
  decide

/-- Complete residual row 70, not a sampled set of columns. -/
theorem residual_row_070 :
    ∀ j : Fin 104, eye 104 ⟨70, by decide⟩ j - Sparse.eval (P_entries ⟨70, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨70, by decide⟩) M j := by
  decide

/-- Complete residual row 71, not a sampled set of columns. -/
theorem residual_row_071 :
    ∀ j : Fin 104, eye 104 ⟨71, by decide⟩ j - Sparse.eval (P_entries ⟨71, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨71, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_064
#print axioms P112Cert.residual_row_065
#print axioms P112Cert.residual_row_066
#print axioms P112Cert.residual_row_067
#print axioms P112Cert.residual_row_068
#print axioms P112Cert.residual_row_069
#print axioms P112Cert.residual_row_070
#print axioms P112Cert.residual_row_071

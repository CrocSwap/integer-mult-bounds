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

/-- Complete residual row 88, not a sampled set of columns. -/
theorem residual_row_088 :
    ∀ j : Fin 104, eye 104 ⟨88, by decide⟩ j - Sparse.eval (P_entries ⟨88, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨88, by decide⟩) M j := by
  decide

/-- Complete residual row 89, not a sampled set of columns. -/
theorem residual_row_089 :
    ∀ j : Fin 104, eye 104 ⟨89, by decide⟩ j - Sparse.eval (P_entries ⟨89, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨89, by decide⟩) M j := by
  decide

/-- Complete residual row 90, not a sampled set of columns. -/
theorem residual_row_090 :
    ∀ j : Fin 104, eye 104 ⟨90, by decide⟩ j - Sparse.eval (P_entries ⟨90, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨90, by decide⟩) M j := by
  decide

/-- Complete residual row 91, not a sampled set of columns. -/
theorem residual_row_091 :
    ∀ j : Fin 104, eye 104 ⟨91, by decide⟩ j - Sparse.eval (P_entries ⟨91, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨91, by decide⟩) M j := by
  decide

/-- Complete residual row 92, not a sampled set of columns. -/
theorem residual_row_092 :
    ∀ j : Fin 104, eye 104 ⟨92, by decide⟩ j - Sparse.eval (P_entries ⟨92, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨92, by decide⟩) M j := by
  decide

/-- Complete residual row 93, not a sampled set of columns. -/
theorem residual_row_093 :
    ∀ j : Fin 104, eye 104 ⟨93, by decide⟩ j - Sparse.eval (P_entries ⟨93, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨93, by decide⟩) M j := by
  decide

/-- Complete residual row 94, not a sampled set of columns. -/
theorem residual_row_094 :
    ∀ j : Fin 104, eye 104 ⟨94, by decide⟩ j - Sparse.eval (P_entries ⟨94, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨94, by decide⟩) M j := by
  decide

/-- Complete residual row 95, not a sampled set of columns. -/
theorem residual_row_095 :
    ∀ j : Fin 104, eye 104 ⟨95, by decide⟩ j - Sparse.eval (P_entries ⟨95, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨95, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_088
#print axioms P112Cert.residual_row_089
#print axioms P112Cert.residual_row_090
#print axioms P112Cert.residual_row_091
#print axioms P112Cert.residual_row_092
#print axioms P112Cert.residual_row_093
#print axioms P112Cert.residual_row_094
#print axioms P112Cert.residual_row_095

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

/-- Complete residual row 80, not a sampled set of columns. -/
theorem residual_row_080 :
    ∀ j : Fin 104, eye 104 ⟨80, by decide⟩ j - Sparse.eval (P_entries ⟨80, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨80, by decide⟩) M j := by
  decide

/-- Complete residual row 81, not a sampled set of columns. -/
theorem residual_row_081 :
    ∀ j : Fin 104, eye 104 ⟨81, by decide⟩ j - Sparse.eval (P_entries ⟨81, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨81, by decide⟩) M j := by
  decide

/-- Complete residual row 82, not a sampled set of columns. -/
theorem residual_row_082 :
    ∀ j : Fin 104, eye 104 ⟨82, by decide⟩ j - Sparse.eval (P_entries ⟨82, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨82, by decide⟩) M j := by
  decide

/-- Complete residual row 83, not a sampled set of columns. -/
theorem residual_row_083 :
    ∀ j : Fin 104, eye 104 ⟨83, by decide⟩ j - Sparse.eval (P_entries ⟨83, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨83, by decide⟩) M j := by
  decide

/-- Complete residual row 84, not a sampled set of columns. -/
theorem residual_row_084 :
    ∀ j : Fin 104, eye 104 ⟨84, by decide⟩ j - Sparse.eval (P_entries ⟨84, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨84, by decide⟩) M j := by
  decide

/-- Complete residual row 85, not a sampled set of columns. -/
theorem residual_row_085 :
    ∀ j : Fin 104, eye 104 ⟨85, by decide⟩ j - Sparse.eval (P_entries ⟨85, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨85, by decide⟩) M j := by
  decide

/-- Complete residual row 86, not a sampled set of columns. -/
theorem residual_row_086 :
    ∀ j : Fin 104, eye 104 ⟨86, by decide⟩ j - Sparse.eval (P_entries ⟨86, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨86, by decide⟩) M j := by
  decide

/-- Complete residual row 87, not a sampled set of columns. -/
theorem residual_row_087 :
    ∀ j : Fin 104, eye 104 ⟨87, by decide⟩ j - Sparse.eval (P_entries ⟨87, by decide⟩) Q j =
      Sparse.eval (W_entries ⟨87, by decide⟩) M j := by
  decide


end P112Cert

set_option pp.fullNames true
#print axioms P112Cert.residual_row_080
#print axioms P112Cert.residual_row_081
#print axioms P112Cert.residual_row_082
#print axioms P112Cert.residual_row_083
#print axioms P112Cert.residual_row_084
#print axioms P112Cert.residual_row_085
#print axioms P112Cert.residual_row_086
#print axioms P112Cert.residual_row_087

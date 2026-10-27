import PhysicalHosting

/-!
Necessary retained-output condition of the existing single-host contract.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

This is a diagnostic for an attempted direct comparison of the entire
parent and hosted invocation. It is not an impossibility theorem for
whole hosting: sequential hybrid layouts or a multi-host theorem can avoid
this particular mismatch.
-/

namespace SourceInvocation

open WholeHosting

/-- Relocation under this contract may change the distinguished host, but
the rest of the retained endpoint is identical for every old/new bank input. -/
theorem retained_rest_equal {ι K A R B C}
    {e : WindowEvent ι R} (contract : PhysicalContract (K := K) (A := A) e B C)
    (s : WindowState ι K A R) (oldBank : B) (newBank : C) :
    (contract.original (s, oldBank)).1.2 =
      (contract.relocated (s, newBank)).1.2 := by
  rw [contract.original_retained, contract.relocated_retained]
  rfl

/-- A differing observation of the second retained component rules out
this contract, independently of the chosen host mask or auxiliary layouts. -/
theorem no_contract_for_different_rest {ι K A R B C O}
    {e : WindowEvent ι R} (contract : PhysicalContract (K := K) (A := A) e B C)
    (s : WindowState ι K A R) (oldBank : B) (newBank : C)
    (observe : R → O) (oldValue newValue : O)
    (old_endpoint : observe (contract.original (s, oldBank)).1.2 = oldValue)
    (new_endpoint : observe (contract.relocated (s, newBank)).1.2 = newValue)
    (different : oldValue ≠ newValue) : False := by
  apply different
  rw [← old_endpoint, ← new_endpoint]
  exact congrArg observe (retained_rest_equal contract s oldBank newBank)

end SourceInvocation

#print axioms SourceInvocation.retained_rest_equal
#print axioms SourceInvocation.no_contract_for_different_rest

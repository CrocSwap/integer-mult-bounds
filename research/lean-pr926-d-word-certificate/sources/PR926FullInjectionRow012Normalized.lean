import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target123 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow012Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [229, 233, 242, 234, 252, 241, 251, 291, 268, 427, 270, 272, 273, 278, 279, 269, 286, 309, 291, 299, 311, 315, 337, 373, 340, 356, 320, 359, 376, 327, 378, 363, 386, 420, 246, 449, 250, 487, 488, 318, 490, 492, 341, 493, 350, 502, 483, 507, 355, 509, 516, 498, 518, 554, 519, 520, 538, 555, 519, 556, 558, 517, 573, 537, 574, 270, 592, 645, 593, 631, 619, 636, 624, 646, 520]
private def rhs0 : List Reg := [229, 233, 234, 241, 242, 246, 250, 251, 252, 268, 269, 272, 273, 278, 279, 286, 299, 309, 311, 315, 318, 320, 327, 337, 340, 341, 350, 355, 356, 359, 363, 373, 376, 378, 386, 420, 427, 449, 483, 487, 488, 490, 492, 493, 498, 502, 507, 509, 516, 517, 518, 537, 538, 554, 555, 556, 558, 573, 574, 592, 593, 619, 624, 631, 636, 645, 646]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [123])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [123]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row012_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 123 =
      injectionVector target original (basisState r) 123 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 123
      (by decide), injection_coordinate target original (basisState r) 123 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow012Normalized
#print axioms CurrentMain.PR926FullInjectionRow012Normalized.row012_basis

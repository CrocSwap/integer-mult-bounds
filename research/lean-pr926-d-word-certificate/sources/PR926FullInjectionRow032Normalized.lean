import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target143 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow032Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [229, 233, 242, 234, 252, 241, 246, 265, 261, 270, 281, 302, 296, 328, 331, 329, 334, 346, 337, 373, 340, 346, 347, 368, 356, 320, 359, 381, 385, 391, 413, 392, 393, 401, 404, 295, 408, 383, 484, 487, 488, 318, 490, 492, 341, 501, 507, 355, 509, 511, 527, 563, 547, 548, 552, 583, 560, 524, 586, 549, 588, 547, 595, 609, 628, 610, 627, 381, 655, 657, 658, 660, 595]
private def rhs0 : List Reg := [229, 233, 234, 241, 242, 246, 252, 261, 265, 270, 281, 295, 296, 302, 318, 320, 328, 329, 331, 334, 337, 340, 341, 347, 355, 356, 359, 368, 373, 383, 385, 391, 392, 393, 401, 404, 408, 413, 484, 487, 488, 490, 492, 501, 507, 509, 511, 524, 527, 548, 549, 552, 560, 563, 583, 586, 588, 609, 610, 627, 628, 655, 657, 658, 660]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [143])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [143]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row032_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 143 =
      injectionVector target original (basisState r) 143 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 143
      (by decide), injection_coordinate target original (basisState r) 143 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow032Normalized
#print axioms CurrentMain.PR926FullInjectionRow032Normalized.row032_basis

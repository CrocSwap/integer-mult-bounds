import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target131 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow020Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [233, 242, 234, 252, 246, 266, 419, 268, 427, 270, 276, 439, 278, 282, 435, 309, 315, 321, 327, 340, 345, 380, 358, 361, 321, 372, 376, 327, 378, 363, 406, 419, 421, 272, 435, 488, 318, 493, 350, 495, 348, 502, 483, 506, 374, 511, 512, 298, 513, 241, 514, 538, 559, 528, 562, 563, 564, 573, 537, 574, 270, 590, 443, 593, 631, 624, 633, 621, 634, 644, 624, 647]
private def rhs0 : List Reg := [233, 234, 241, 242, 246, 252, 266, 268, 272, 276, 278, 282, 298, 309, 315, 318, 340, 345, 348, 350, 358, 361, 363, 372, 374, 376, 378, 380, 406, 421, 427, 439, 443, 483, 488, 493, 495, 502, 506, 511, 512, 513, 514, 528, 537, 538, 559, 562, 563, 564, 573, 574, 590, 593, 621, 631, 633, 634, 644, 647]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [131])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [131]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row020_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 131 =
      injectionVector target original (basisState r) 131 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 131
      (by decide), injection_coordinate target original (basisState r) 131 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow020Normalized
#print axioms CurrentMain.PR926FullInjectionRow020Normalized.row020_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target169 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow058Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [232, 240, 223, 241, 246, 255, 428, 262, 415, 266, 419, 268, 427, 274, 284, 276, 439, 278, 282, 435, 285, 436, 314, 402, 321, 332, 342, 336, 343, 349, 356, 320, 357, 363, 367, 322, 373, 378, 363, 381, 387, 406, 421, 272, 424, 259, 425, 258, 437, 438, 267, 440, 443, 462, 465, 472, 473, 340, 478, 464, 493, 350, 499, 484, 514, 531, 568, 540, 571, 570, 576, 535, 599, 659, 656, 596]
private def rhs0 : List Reg := [223, 232, 240, 241, 246, 255, 258, 259, 262, 266, 267, 268, 272, 274, 276, 278, 282, 284, 285, 314, 320, 321, 322, 332, 336, 340, 342, 343, 349, 350, 356, 357, 367, 373, 378, 381, 387, 402, 406, 415, 419, 421, 424, 425, 427, 428, 435, 436, 437, 438, 439, 440, 443, 462, 464, 465, 472, 473, 478, 484, 493, 499, 514, 531, 535, 540, 568, 570, 571, 576, 596, 599, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (169 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (169 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row058_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 169 =
      injectionVector target original (basisState r) 169 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 169
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 169 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow058Normalized
#print axioms CurrentMain.PR926FullInjectionRow058Normalized.row058_basis

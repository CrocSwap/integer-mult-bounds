import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target162 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow051Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 231, 459, 233, 242, 236, 457, 238, 248, 240, 223, 244, 455, 247, 243, 251, 291, 263, 414, 274, 284, 275, 441, 294, 290, 306, 382, 316, 393, 324, 354, 326, 530, 337, 373, 341, 350, 356, 320, 357, 360, 363, 375, 378, 363, 401, 405, 401, 407, 409, 317, 425, 258, 437, 447, 226, 448, 460, 450, 452, 224, 456, 237, 461, 451, 472, 493, 350, 499, 484, 504, 222, 505, 446, 516, 498, 532, 540, 571, 541, 582, 567, 532, 568, 576, 535, 577, 546, 599, 659, 614, 638, 641, 617, 656, 596]
private def rhs0 : List Reg := [222, 223, 224, 226, 228, 231, 233, 236, 237, 238, 240, 242, 243, 244, 247, 248, 251, 258, 263, 274, 275, 284, 290, 291, 294, 306, 316, 317, 320, 324, 326, 337, 341, 354, 356, 357, 360, 373, 375, 378, 382, 393, 405, 407, 409, 414, 425, 437, 441, 446, 447, 448, 450, 451, 452, 455, 456, 457, 459, 460, 461, 472, 484, 493, 498, 499, 504, 505, 516, 530, 535, 540, 541, 546, 567, 568, 571, 576, 577, 582, 596, 599, 614, 617, 638, 641, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (162 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (162 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row051_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 162 =
      injectionVector target original (basisState r) 162 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 162
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 162 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow051Normalized
#print axioms CurrentMain.PR926FullInjectionRow051Normalized.row051_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target191 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow080Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 232, 247, 243, 265, 261, 270, 280, 260, 281, 287, 309, 315, 321, 322, 331, 329, 333, 334, 346, 335, 364, 340, 343, 345, 380, 351, 377, 353, 371, 356, 320, 361, 321, 363, 369, 365, 372, 373, 378, 363, 379, 338, 387, 417, 433, 423, 465, 486, 488, 318, 493, 350, 495, 348, 496, 336, 504, 222, 506, 374, 512, 298, 525, 528, 531, 568, 540, 571, 550, 563, 570, 576, 535, 585, 586, 549, 599, 659, 622, 403, 633, 621, 634, 656, 596]
private def rhs0 : List Reg := [222, 228, 232, 243, 247, 260, 261, 265, 270, 280, 281, 287, 298, 309, 315, 318, 320, 322, 329, 331, 333, 334, 335, 336, 338, 340, 343, 345, 346, 348, 350, 351, 353, 356, 361, 364, 365, 369, 371, 372, 373, 374, 377, 378, 379, 380, 387, 403, 417, 423, 433, 465, 486, 488, 493, 495, 496, 504, 506, 512, 525, 528, 531, 535, 540, 549, 550, 563, 568, 570, 571, 576, 585, 586, 596, 599, 621, 622, 633, 634, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (191 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (191 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row080_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 191 =
      injectionVector target original (basisState r) 191 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 191
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 191 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow080Normalized
#print axioms CurrentMain.PR926FullInjectionRow080Normalized.row080_basis

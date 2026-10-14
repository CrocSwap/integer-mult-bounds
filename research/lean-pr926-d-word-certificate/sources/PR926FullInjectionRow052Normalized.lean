import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target163 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow052Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [246, 260, 270, 279, 269, 286, 309, 297, 303, 309, 313, 292, 323, 366, 331, 329, 332, 342, 333, 335, 364, 342, 357, 365, 368, 372, 379, 338, 384, 385, 387, 396, 299, 407, 420, 246, 430, 257, 432, 445, 271, 465, 467, 468, 480, 538, 494, 497, 349, 512, 298, 515, 569, 525, 528, 534, 570, 535, 536, 264, 550, 563, 566, 571, 574, 270, 585, 586, 549, 599, 659, 622, 403, 633, 621, 634, 656, 596]
private def rhs0 : List Reg := [257, 260, 264, 269, 271, 279, 286, 292, 297, 298, 299, 303, 313, 323, 329, 331, 332, 333, 335, 338, 349, 357, 364, 365, 366, 368, 372, 379, 384, 385, 387, 396, 403, 407, 420, 430, 432, 445, 465, 467, 468, 480, 494, 497, 512, 515, 525, 528, 534, 535, 536, 538, 549, 550, 563, 566, 569, 570, 571, 574, 585, 586, 596, 599, 621, 622, 633, 634, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (163 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (163 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row052_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 163 =
      injectionVector target original (basisState r) 163 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 163
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 163 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow052Normalized
#print axioms CurrentMain.PR926FullInjectionRow052Normalized.row052_basis

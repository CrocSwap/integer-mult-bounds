import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target212 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow101Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [230, 251, 291, 258, 263, 414, 265, 261, 266, 419, 275, 441, 276, 439, 281, 284, 291, 302, 296, 311, 328, 331, 329, 334, 346, 346, 347, 368, 350, 385, 391, 413, 401, 414, 424, 259, 425, 258, 437, 440, 441, 449, 250, 453, 225, 458, 227, 493, 350, 511, 516, 498, 520, 531, 568, 538, 541, 582, 547, 548, 552, 583, 567, 532, 572, 573, 537, 574, 270, 577, 546, 586, 549, 588, 547, 592, 645, 593, 631, 613, 642, 615, 639, 616, 618, 572, 619, 636, 624, 646, 520]
private def rhs0 : List Reg := [225, 227, 230, 250, 251, 259, 261, 263, 265, 266, 270, 275, 276, 281, 284, 296, 302, 311, 328, 329, 331, 334, 347, 368, 385, 391, 401, 413, 419, 424, 425, 437, 439, 440, 449, 453, 458, 493, 498, 511, 516, 531, 532, 537, 538, 541, 546, 548, 549, 552, 567, 568, 573, 574, 577, 582, 583, 586, 588, 592, 593, 613, 615, 616, 618, 619, 624, 631, 636, 639, 642, 645, 646]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (212 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (212 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row101_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 212 =
      injectionVector target original (basisState r) 212 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 212
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 212 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow101Normalized
#print axioms CurrentMain.PR926FullInjectionRow101Normalized.row101_basis

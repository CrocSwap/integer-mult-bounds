import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target188 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow077Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [229, 238, 248, 244, 455, 249, 239, 265, 261, 270, 281, 288, 304, 292, 300, 410, 305, 394, 314, 402, 315, 331, 329, 333, 335, 364, 340, 345, 380, 375, 377, 378, 363, 389, 310, 399, 400, 297, 407, 412, 293, 416, 449, 250, 454, 245, 461, 451, 488, 318, 509, 510, 375, 524, 525, 526, 543, 530, 533, 542, 384, 544, 312, 546, 561, 525, 563, 594, 643, 606, 649, 614, 638, 626, 611, 629, 608, 641, 617, 648, 589, 654, 601]
private def rhs0 : List Reg := [229, 238, 239, 244, 245, 248, 249, 250, 261, 265, 270, 281, 288, 292, 293, 297, 300, 304, 305, 310, 312, 314, 315, 318, 329, 331, 333, 335, 340, 345, 363, 364, 377, 378, 380, 384, 389, 394, 399, 400, 402, 407, 410, 412, 416, 449, 451, 454, 455, 461, 488, 509, 510, 524, 526, 530, 533, 542, 543, 544, 546, 561, 563, 589, 594, 601, 606, 608, 611, 614, 617, 626, 629, 638, 641, 643, 648, 649, 654]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (188 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (188 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row077_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 188 =
      injectionVector target original (basisState r) 188 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 188
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 188 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow077Normalized
#print axioms CurrentMain.PR926FullInjectionRow077Normalized.row077_basis

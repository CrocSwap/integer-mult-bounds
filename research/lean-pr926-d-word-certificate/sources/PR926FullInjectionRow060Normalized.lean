import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target171 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow060Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [230, 231, 459, 262, 415, 263, 414, 268, 427, 275, 441, 285, 436, 287, 309, 314, 402, 323, 366, 326, 530, 328, 329, 331, 329, 335, 364, 337, 373, 339, 343, 340, 341, 349, 356, 320, 361, 321, 362, 333, 365, 381, 406, 421, 272, 424, 259, 440, 443, 446, 452, 224, 453, 225, 456, 237, 458, 227, 487, 488, 318, 491, 492, 341, 494, 510, 375, 511, 512, 298, 522, 652, 524, 525, 530, 549, 550, 551, 558, 517, 559, 528, 564, 604, 553, 651, 603]
private def rhs0 : List Reg := [224, 225, 227, 230, 231, 237, 259, 262, 263, 268, 272, 275, 285, 287, 298, 309, 314, 318, 320, 321, 323, 326, 328, 331, 333, 335, 337, 339, 340, 343, 349, 356, 361, 362, 364, 365, 366, 373, 375, 381, 402, 406, 414, 415, 421, 424, 427, 436, 440, 441, 443, 446, 452, 453, 456, 458, 459, 487, 488, 491, 492, 494, 510, 511, 512, 517, 522, 524, 525, 528, 549, 550, 551, 553, 558, 559, 564, 603, 604, 651, 652]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (171 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (171 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row060_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 171 =
      injectionVector target original (basisState r) 171 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 171
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 171 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow060Normalized
#print axioms CurrentMain.PR926FullInjectionRow060Normalized.row060_basis

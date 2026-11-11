import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target206 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow095Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 225, 226, 230, 231, 459, 239, 240, 223, 241, 243, 247, 243, 251, 291, 255, 428, 258, 260, 261, 283, 286, 309, 288, 304, 294, 290, 300, 410, 305, 394, 308, 322, 326, 530, 329, 331, 329, 334, 346, 335, 364, 336, 338, 339, 343, 341, 343, 346, 351, 377, 353, 371, 358, 364, 367, 322, 380, 381, 386, 388, 393, 398, 289, 409, 317, 410, 414, 423, 424, 259, 425, 258, 434, 277, 435, 437, 440, 441, 447, 226, 450, 454, 245, 455, 456, 237, 457, 461, 451, 472, 483, 484, 486, 495, 348, 501, 508, 372, 513, 241, 534, 570, 538, 540, 571, 550, 559, 528, 560, 524, 565, 569, 570, 574, 270, 585, 588, 547, 593, 631, 595, 609, 628, 615, 639, 620, 622, 403, 624, 644, 624, 650, 602, 657]
private def rhs0 : List Reg := [225, 230, 231, 237, 239, 240, 245, 247, 251, 255, 259, 260, 261, 270, 277, 283, 286, 288, 289, 290, 291, 294, 300, 304, 305, 308, 309, 317, 326, 331, 334, 335, 336, 338, 339, 341, 348, 351, 353, 358, 367, 371, 372, 377, 380, 381, 386, 388, 393, 394, 398, 403, 409, 414, 423, 424, 425, 428, 434, 435, 437, 440, 441, 447, 450, 451, 454, 455, 456, 457, 459, 461, 472, 483, 484, 486, 495, 501, 508, 513, 524, 528, 530, 534, 538, 540, 547, 550, 559, 560, 565, 569, 571, 574, 585, 588, 593, 595, 602, 609, 615, 620, 622, 628, 631, 639, 644, 650, 657]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (206 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (206 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row095_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 206 =
      injectionVector target original (basisState r) 206 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 206
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 206 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow095Normalized
#print axioms CurrentMain.PR926FullInjectionRow095Normalized.row095_basis

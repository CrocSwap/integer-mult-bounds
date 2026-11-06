import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target154 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow043Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [234, 252, 238, 248, 242, 244, 455, 246, 251, 291, 255, 428, 262, 415, 263, 414, 271, 275, 441, 282, 435, 285, 436, 293, 294, 290, 306, 382, 316, 393, 321, 344, 325, 350, 352, 355, 357, 359, 385, 390, 283, 405, 401, 409, 317, 412, 293, 413, 418, 254, 424, 259, 429, 490, 434, 277, 438, 267, 440, 448, 460, 450, 461, 451, 462, 463, 462, 469, 479, 471, 478, 464, 484, 493, 350, 495, 348, 496, 336, 501, 508, 372, 511, 526, 543, 531, 568, 561, 525, 562, 567, 532, 580, 594, 643, 614, 638, 641, 617, 648, 589]
private def rhs0 : List Reg := [234, 238, 242, 244, 246, 248, 251, 252, 254, 255, 259, 262, 263, 267, 271, 275, 277, 282, 283, 285, 290, 291, 294, 306, 316, 317, 321, 325, 336, 344, 348, 352, 355, 357, 359, 372, 382, 385, 390, 393, 401, 405, 409, 412, 413, 414, 415, 418, 424, 428, 429, 434, 435, 436, 438, 440, 441, 448, 450, 451, 455, 460, 461, 463, 464, 469, 471, 478, 479, 484, 490, 493, 495, 496, 501, 508, 511, 525, 526, 531, 532, 543, 561, 562, 567, 568, 580, 589, 594, 614, 617, 638, 641, 643, 648]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (154 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (154 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row043_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 154 =
      injectionVector target original (basisState r) 154 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 154
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 154 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow043Normalized
#print axioms CurrentMain.PR926FullInjectionRow043Normalized.row043_basis

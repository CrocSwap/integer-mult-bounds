import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target150 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow039Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [233, 242, 235, 240, 223, 241, 242, 251, 291, 253, 229, 255, 428, 262, 415, 263, 414, 275, 441, 282, 435, 283, 285, 436, 298, 300, 410, 301, 411, 305, 394, 306, 382, 310, 314, 402, 318, 319, 321, 340, 342, 345, 380, 350, 351, 377, 357, 372, 374, 378, 363, 386, 387, 394, 397, 308, 398, 289, 403, 406, 407, 409, 317, 410, 418, 254, 424, 259, 429, 490, 434, 277, 438, 267, 440, 448, 460, 450, 462, 463, 462, 478, 464, 485, 486, 486, 490, 491, 493, 350, 495, 348, 496, 336, 500, 509, 511, 529, 531, 568, 553, 565, 567, 532, 604, 553, 623, 635, 632, 620, 649, 652, 653]
private def rhs0 : List Reg := [223, 229, 233, 235, 240, 241, 251, 253, 254, 255, 259, 262, 263, 267, 275, 277, 282, 283, 285, 289, 291, 298, 300, 301, 305, 306, 308, 310, 314, 317, 318, 319, 321, 336, 340, 342, 345, 348, 351, 357, 363, 372, 374, 377, 378, 380, 382, 386, 387, 397, 398, 402, 403, 406, 407, 409, 411, 414, 415, 418, 424, 428, 429, 434, 435, 436, 438, 440, 441, 448, 450, 460, 463, 464, 478, 485, 491, 493, 495, 496, 500, 509, 511, 529, 531, 532, 565, 567, 568, 604, 620, 623, 632, 635, 649, 652, 653]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (150 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (150 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row039_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 150 =
      injectionVector target original (basisState r) 150 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 150
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 150 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow039Normalized
#print axioms CurrentMain.PR926FullInjectionRow039Normalized.row039_basis

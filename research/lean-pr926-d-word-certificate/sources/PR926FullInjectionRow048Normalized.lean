import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target159 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow048Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [246, 265, 261, 270, 279, 269, 281, 286, 309, 287, 303, 313, 292, 314, 402, 315, 321, 322, 329, 330, 352, 340, 344, 325, 346, 349, 360, 364, 370, 384, 386, 387, 396, 299, 406, 420, 246, 426, 430, 257, 431, 273, 442, 256, 462, 464, 465, 474, 509, 477, 478, 464, 487, 488, 318, 489, 228, 490, 492, 341, 495, 348, 496, 336, 498, 511, 548, 583, 585, 597, 657, 598, 658, 615, 639, 640, 616]
private def rhs0 : List Reg := [228, 256, 257, 261, 265, 269, 270, 273, 279, 281, 286, 287, 292, 299, 303, 309, 313, 314, 315, 318, 321, 322, 325, 329, 330, 336, 340, 341, 344, 346, 348, 349, 352, 360, 364, 370, 384, 386, 387, 396, 402, 406, 420, 426, 430, 431, 442, 462, 465, 474, 477, 478, 487, 488, 489, 490, 492, 495, 496, 498, 509, 511, 548, 583, 585, 597, 598, 615, 616, 639, 640, 657, 658]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (159 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (159 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row048_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 159 =
      injectionVector target original (basisState r) 159 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 159
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 159 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow048Normalized
#print axioms CurrentMain.PR926FullInjectionRow048Normalized.row048_basis

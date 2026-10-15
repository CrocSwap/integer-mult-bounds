import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target216 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow105Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 228, 230, 236, 457, 238, 248, 239, 241, 247, 243, 251, 291, 254, 255, 428, 262, 415, 265, 261, 271, 280, 260, 283, 287, 288, 304, 293, 295, 301, 411, 305, 394, 308, 313, 292, 317, 320, 321, 322, 328, 349, 352, 353, 371, 364, 370, 373, 383, 385, 387, 388, 390, 283, 391, 413, 393, 402, 403, 404, 295, 405, 401, 410, 413, 420, 246, 421, 272, 422, 424, 259, 425, 258, 428, 430, 257, 432, 435, 444, 470, 447, 226, 453, 225, 458, 227, 460, 461, 451, 462, 471, 473, 340, 475, 468, 478, 464, 495, 348, 496, 336, 498, 544, 312, 551, 555, 519, 558, 517, 559, 528, 561, 525, 573, 537, 580, 584, 551, 594, 643, 598, 658, 613, 642, 619, 636, 621, 631, 636, 640, 616, 643, 651, 603]
private def rhs0 : List Reg := [222, 223, 225, 226, 227, 228, 230, 236, 238, 239, 241, 243, 246, 247, 248, 251, 254, 255, 257, 258, 259, 260, 261, 262, 265, 271, 272, 280, 287, 288, 291, 292, 293, 301, 304, 305, 308, 312, 313, 317, 320, 321, 322, 328, 336, 340, 348, 349, 352, 353, 364, 370, 371, 373, 383, 385, 387, 388, 390, 391, 393, 394, 401, 402, 403, 404, 405, 410, 411, 415, 420, 421, 422, 424, 425, 430, 432, 435, 444, 447, 451, 453, 457, 458, 460, 461, 462, 464, 468, 470, 471, 473, 475, 478, 495, 496, 498, 517, 519, 525, 528, 537, 544, 555, 558, 559, 561, 573, 580, 584, 594, 598, 603, 613, 616, 619, 621, 631, 640, 642, 651, 658]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (216 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (216 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row105_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 216 =
      injectionVector target original (basisState r) 216 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 216
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 216 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow105Normalized
#print axioms CurrentMain.PR926FullInjectionRow105Normalized.row105_basis

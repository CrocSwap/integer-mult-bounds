import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target218 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow107Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 233, 242, 234, 252, 238, 248, 240, 223, 241, 243, 244, 455, 247, 243, 249, 239, 252, 263, 414, 264, 265, 261, 266, 419, 280, 260, 288, 304, 292, 294, 290, 300, 410, 302, 296, 305, 394, 310, 316, 393, 318, 320, 322, 323, 366, 325, 328, 331, 329, 334, 346, 338, 340, 351, 377, 354, 355, 357, 358, 370, 372, 373, 376, 327, 380, 389, 310, 394, 405, 401, 410, 418, 254, 420, 246, 421, 272, 425, 258, 429, 490, 430, 257, 445, 271, 448, 460, 455, 461, 451, 484, 492, 341, 493, 350, 496, 336, 497, 349, 498, 500, 509, 516, 498, 522, 652, 531, 568, 534, 570, 553, 555, 519, 565, 570, 573, 537, 578, 385, 579, 587, 548, 606, 649, 613, 642, 619, 636, 632, 620, 641, 617, 645, 647, 648, 589]
private def rhs0 : List Reg := [233, 234, 238, 239, 240, 241, 242, 244, 246, 247, 248, 249, 254, 257, 258, 260, 261, 263, 264, 265, 266, 271, 272, 280, 288, 290, 292, 294, 296, 300, 302, 304, 305, 316, 318, 320, 322, 323, 325, 327, 328, 329, 331, 334, 336, 338, 340, 341, 346, 349, 350, 351, 354, 355, 357, 358, 366, 370, 372, 373, 376, 377, 380, 385, 389, 393, 401, 405, 414, 418, 419, 420, 421, 425, 429, 430, 445, 448, 451, 460, 461, 484, 490, 492, 493, 496, 497, 500, 509, 516, 519, 522, 531, 534, 537, 548, 553, 555, 565, 568, 573, 578, 579, 587, 589, 606, 613, 617, 619, 620, 632, 636, 641, 642, 645, 647, 648, 649, 652]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (218 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (218 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row107_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 218 =
      injectionVector target original (basisState r) 218 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 218
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 218 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow107Normalized
#print axioms CurrentMain.PR926FullInjectionRow107Normalized.row107_basis

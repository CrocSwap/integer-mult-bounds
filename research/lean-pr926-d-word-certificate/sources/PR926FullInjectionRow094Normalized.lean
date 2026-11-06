import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target205 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow094Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [231, 459, 235, 243, 244, 455, 247, 243, 252, 261, 263, 414, 269, 272, 279, 269, 280, 260, 281, 287, 304, 305, 394, 308, 309, 313, 292, 328, 335, 364, 338, 339, 343, 341, 348, 351, 377, 353, 371, 357, 360, 363, 367, 322, 369, 365, 370, 376, 327, 379, 338, 380, 389, 310, 391, 413, 396, 299, 397, 308, 402, 403, 406, 407, 420, 246, 425, 258, 431, 273, 432, 442, 256, 445, 271, 446, 447, 226, 449, 250, 454, 245, 496, 336, 508, 372, 514, 519, 521, 531, 568, 561, 525, 575, 539, 580, 581, 303, 587, 548, 592, 645, 594, 643, 604, 553, 613, 642, 626, 611, 630, 607, 641, 617, 652, 654, 601]
private def rhs0 : List Reg := [226, 231, 235, 244, 245, 246, 247, 250, 252, 256, 258, 260, 261, 263, 271, 272, 273, 279, 280, 281, 287, 292, 299, 303, 304, 305, 309, 310, 313, 322, 327, 328, 335, 336, 339, 341, 343, 348, 351, 353, 357, 360, 363, 364, 365, 367, 369, 370, 371, 372, 376, 377, 379, 380, 389, 391, 394, 396, 397, 402, 403, 406, 407, 413, 414, 420, 425, 431, 432, 442, 445, 446, 447, 449, 454, 455, 459, 496, 508, 514, 519, 521, 525, 531, 539, 548, 553, 561, 568, 575, 580, 581, 587, 592, 594, 601, 604, 607, 611, 613, 617, 626, 630, 641, 642, 643, 645, 652, 654]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (205 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (205 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row094_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 205 =
      injectionVector target original (basisState r) 205 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 205
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 205 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow094Normalized
#print axioms CurrentMain.PR926FullInjectionRow094Normalized.row094_basis

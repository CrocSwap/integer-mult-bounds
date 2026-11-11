import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target146 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow035Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 231, 459, 238, 248, 241, 243, 249, 239, 252, 256, 261, 266, 419, 268, 427, 269, 274, 284, 275, 441, 276, 439, 278, 280, 260, 281, 287, 288, 304, 292, 298, 299, 300, 410, 304, 308, 309, 313, 292, 330, 352, 335, 364, 338, 339, 343, 341, 344, 325, 347, 368, 350, 351, 377, 353, 371, 355, 359, 363, 369, 365, 378, 363, 379, 338, 380, 390, 283, 391, 413, 399, 400, 297, 402, 406, 416, 418, 254, 421, 272, 422, 426, 429, 490, 434, 277, 437, 446, 447, 226, 461, 451, 464, 473, 340, 477, 484, 486, 517, 536, 264, 544, 312, 546, 554, 561, 525, 567, 532, 584, 551, 591, 637, 594, 643, 612, 625, 614, 638, 618, 572, 626, 611, 646, 520, 651, 603, 654, 601]
private def rhs0 : List Reg := [223, 226, 231, 238, 239, 241, 243, 248, 249, 252, 254, 256, 260, 261, 264, 266, 268, 269, 272, 274, 275, 276, 277, 278, 280, 281, 283, 284, 287, 288, 297, 298, 299, 300, 308, 309, 312, 313, 325, 330, 335, 339, 340, 341, 343, 344, 347, 350, 351, 352, 353, 355, 359, 364, 365, 368, 369, 371, 377, 378, 379, 380, 390, 391, 399, 400, 402, 406, 410, 413, 416, 418, 419, 421, 422, 426, 427, 429, 434, 437, 439, 441, 446, 447, 451, 459, 461, 464, 473, 477, 484, 486, 490, 517, 520, 525, 532, 536, 544, 546, 551, 554, 561, 567, 572, 584, 591, 594, 601, 603, 611, 612, 614, 618, 625, 626, 637, 638, 643, 646, 651, 654]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (146 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (146 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row035_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 146 =
      injectionVector target original (basisState r) 146 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 146
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 146 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow035Normalized
#print axioms CurrentMain.PR926FullInjectionRow035Normalized.row035_basis

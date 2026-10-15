import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target185 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow074Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [240, 223, 247, 243, 263, 414, 266, 419, 268, 427, 274, 284, 275, 441, 276, 439, 278, 279, 269, 280, 260, 283, 287, 292, 296, 319, 322, 334, 346, 342, 344, 325, 348, 351, 377, 353, 371, 355, 357, 359, 360, 367, 322, 369, 365, 371, 378, 363, 386, 391, 413, 400, 297, 417, 433, 418, 254, 420, 246, 421, 272, 423, 425, 258, 429, 490, 430, 257, 434, 277, 437, 443, 486, 496, 336, 499, 484, 504, 222, 508, 372, 514, 534, 570, 543, 579, 581, 303, 582, 614, 638, 641, 617]
private def rhs0 : List Reg := [222, 223, 240, 243, 246, 247, 254, 257, 258, 260, 263, 266, 268, 269, 272, 274, 275, 276, 277, 278, 279, 280, 283, 284, 287, 292, 296, 297, 303, 319, 325, 334, 336, 342, 344, 346, 348, 351, 353, 355, 357, 359, 360, 363, 365, 367, 369, 372, 377, 378, 386, 391, 400, 413, 414, 417, 418, 419, 420, 421, 423, 425, 427, 429, 430, 433, 434, 437, 439, 441, 443, 484, 486, 490, 496, 499, 504, 508, 514, 534, 543, 570, 579, 581, 582, 614, 617, 638, 641]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (185 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (185 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row074_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 185 =
      injectionVector target original (basisState r) 185 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 185
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 185 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow074Normalized
#print axioms CurrentMain.PR926FullInjectionRow074Normalized.row074_basis

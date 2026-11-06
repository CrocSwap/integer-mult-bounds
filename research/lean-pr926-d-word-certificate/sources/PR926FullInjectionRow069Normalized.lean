import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target180 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow069Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [232, 240, 223, 246, 263, 414, 266, 419, 274, 284, 275, 441, 276, 439, 280, 260, 312, 319, 322, 325, 330, 352, 331, 329, 334, 346, 344, 325, 345, 380, 347, 368, 352, 365, 369, 365, 370, 385, 390, 283, 400, 297, 412, 293, 417, 433, 418, 254, 423, 425, 258, 429, 490, 433, 434, 277, 437, 476, 467, 487, 489, 228, 490, 492, 341, 499, 484, 507, 355, 522, 652, 547, 551, 558, 517, 584, 551, 586, 549, 604, 553, 651, 603]
private def rhs0 : List Reg := [223, 228, 232, 240, 246, 254, 258, 260, 263, 266, 274, 275, 276, 277, 280, 283, 284, 293, 297, 312, 319, 322, 329, 330, 331, 334, 341, 344, 345, 346, 347, 355, 368, 369, 370, 380, 385, 390, 400, 412, 414, 417, 418, 419, 423, 425, 429, 434, 437, 439, 441, 467, 476, 484, 487, 489, 492, 499, 507, 517, 522, 547, 549, 553, 558, 584, 586, 603, 604, 651, 652]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (180 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (180 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row069_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 180 =
      injectionVector target original (basisState r) 180 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 180
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 180 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow069Normalized
#print axioms CurrentMain.PR926FullInjectionRow069Normalized.row069_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target149 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow038Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [234, 252, 242, 279, 269, 287, 288, 304, 294, 290, 300, 410, 305, 394, 307, 392, 316, 393, 323, 366, 336, 341, 344, 325, 345, 380, 348, 349, 357, 358, 378, 363, 381, 385, 389, 310, 399, 404, 295, 405, 401, 407, 408, 383, 416, 420, 246, 426, 430, 257, 431, 273, 442, 256, 462, 463, 462, 478, 464, 484, 494, 495, 348, 501, 507, 355, 510, 375, 530, 533, 542, 384, 581, 303, 606, 649, 614, 638, 626, 611, 629, 608, 641, 617, 654, 601]
private def rhs0 : List Reg := [234, 242, 246, 252, 256, 257, 269, 273, 279, 287, 288, 290, 294, 295, 300, 303, 304, 305, 307, 310, 316, 323, 325, 336, 341, 344, 345, 349, 355, 357, 358, 363, 366, 375, 378, 380, 381, 383, 384, 385, 389, 392, 393, 394, 399, 401, 404, 405, 407, 408, 410, 416, 420, 426, 430, 431, 442, 463, 464, 478, 484, 494, 495, 501, 507, 510, 530, 533, 542, 581, 601, 606, 608, 611, 614, 617, 626, 629, 638, 641, 649, 654]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (149 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (149 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row038_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 149 =
      injectionVector target original (basisState r) 149 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 149
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 149 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow038Normalized
#print axioms CurrentMain.PR926FullInjectionRow038Normalized.row038_basis

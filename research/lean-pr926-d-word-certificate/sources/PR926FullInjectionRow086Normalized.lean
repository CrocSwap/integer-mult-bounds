import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target197 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow086Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [229, 233, 242, 235, 236, 457, 238, 248, 239, 240, 223, 243, 244, 455, 249, 239, 251, 291, 256, 264, 270, 276, 439, 281, 292, 294, 290, 297, 301, 411, 302, 296, 304, 306, 382, 316, 393, 318, 323, 366, 326, 530, 328, 331, 329, 334, 346, 338, 339, 343, 340, 343, 351, 377, 361, 321, 365, 368, 370, 375, 381, 388, 390, 283, 393, 394, 400, 297, 408, 383, 416, 421, 272, 422, 431, 273, 434, 277, 445, 271, 449, 250, 450, 452, 224, 455, 456, 237, 467, 480, 538, 497, 349, 500, 506, 374, 507, 355, 515, 569, 518, 554, 522, 652, 534, 570, 536, 264, 542, 384, 553, 565, 570, 571, 578, 385, 587, 548, 593, 631, 612, 625, 629, 608, 632, 620, 644, 624, 656, 596]
private def rhs0 : List Reg := [223, 224, 229, 233, 235, 236, 237, 238, 240, 242, 243, 244, 248, 249, 250, 251, 256, 270, 271, 272, 273, 276, 277, 281, 283, 290, 291, 292, 294, 296, 301, 302, 304, 306, 316, 318, 321, 323, 326, 328, 329, 331, 334, 338, 339, 340, 346, 349, 351, 355, 361, 365, 366, 368, 370, 374, 375, 377, 381, 382, 383, 384, 385, 388, 390, 394, 400, 408, 411, 416, 421, 422, 431, 434, 439, 445, 449, 450, 452, 456, 457, 467, 480, 497, 500, 506, 507, 515, 518, 522, 530, 534, 536, 538, 542, 548, 553, 554, 565, 569, 571, 578, 587, 593, 596, 608, 612, 620, 624, 625, 629, 631, 632, 644, 652, 656]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (197 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (197 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row086_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 197 =
      injectionVector target original (basisState r) 197 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 197
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 197 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow086Normalized
#print axioms CurrentMain.PR926FullInjectionRow086Normalized.row086_basis

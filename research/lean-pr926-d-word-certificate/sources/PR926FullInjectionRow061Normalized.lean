import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target172 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow061Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [230, 236, 457, 238, 248, 242, 244, 455, 251, 291, 255, 428, 266, 419, 268, 427, 276, 439, 278, 279, 269, 282, 435, 294, 290, 302, 296, 303, 306, 382, 313, 292, 316, 393, 322, 323, 366, 328, 330, 352, 332, 342, 334, 346, 347, 368, 350, 351, 377, 353, 371, 356, 320, 358, 369, 365, 370, 372, 373, 376, 327, 378, 363, 379, 338, 384, 385, 391, 413, 405, 401, 409, 317, 420, 246, 421, 272, 430, 257, 438, 267, 443, 447, 226, 448, 460, 450, 453, 225, 458, 227, 461, 451, 463, 462, 473, 340, 486, 494, 498, 516, 498]
private def rhs0 : List Reg := [225, 226, 227, 230, 236, 238, 242, 244, 246, 248, 251, 255, 257, 266, 267, 268, 269, 272, 276, 278, 279, 282, 290, 291, 292, 294, 296, 302, 303, 306, 313, 316, 317, 320, 322, 323, 327, 328, 330, 332, 334, 338, 340, 342, 346, 347, 350, 351, 352, 353, 356, 358, 363, 365, 366, 368, 369, 370, 371, 372, 373, 376, 377, 378, 379, 382, 384, 385, 391, 393, 401, 405, 409, 413, 419, 420, 421, 427, 428, 430, 435, 438, 439, 443, 447, 448, 450, 451, 453, 455, 457, 458, 460, 461, 462, 463, 473, 486, 494, 516]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (172 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (172 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row061_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 172 =
      injectionVector target original (basisState r) 172 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 172
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 172 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow061Normalized
#print axioms CurrentMain.PR926FullInjectionRow061Normalized.row061_basis

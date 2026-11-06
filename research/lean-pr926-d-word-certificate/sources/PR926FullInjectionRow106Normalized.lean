import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target217 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow106Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 226, 232, 233, 242, 235, 253, 229, 265, 261, 271, 281, 297, 302, 296, 328, 330, 352, 337, 373, 340, 345, 380, 347, 368, 356, 320, 357, 358, 360, 365, 368, 370, 391, 413, 401, 415, 416, 417, 433, 423, 467, 480, 538, 481, 472, 482, 503, 484, 488, 318, 504, 222, 506, 374, 511, 527, 563, 539, 540, 571, 560, 524, 572, 574, 270, 600, 655, 612, 625, 627, 381, 630, 607, 660, 595]
private def rhs0 : List Reg := [226, 229, 232, 233, 235, 242, 253, 261, 265, 270, 271, 281, 296, 297, 302, 318, 320, 328, 330, 337, 340, 345, 347, 352, 356, 357, 358, 360, 365, 370, 373, 374, 380, 381, 391, 401, 413, 415, 416, 417, 423, 433, 467, 472, 480, 481, 482, 484, 488, 503, 504, 506, 511, 524, 527, 538, 539, 540, 560, 563, 571, 572, 574, 595, 600, 607, 612, 625, 627, 630, 655, 660]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (217 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (217 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row106_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 217 =
      injectionVector target original (basisState r) 217 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 217
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 217 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow106Normalized
#print axioms CurrentMain.PR926FullInjectionRow106Normalized.row106_basis

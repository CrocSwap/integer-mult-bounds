import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target176 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow065Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [271, 293, 329, 331, 329, 353, 371, 364, 365, 369, 365, 385, 413, 433, 444, 470, 471, 475, 468, 476, 467, 547, 583, 585, 586, 549]
private def rhs0 : List Reg := [271, 293, 331, 353, 364, 369, 371, 385, 413, 433, 444, 467, 468, 470, 471, 475, 476, 547, 549, 583, 585, 586]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (176 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (176 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row065_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 176 =
      injectionVector target original (basisState r) 176 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 176
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 176 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow065Normalized
#print axioms CurrentMain.PR926FullInjectionRow065Normalized.row065_basis

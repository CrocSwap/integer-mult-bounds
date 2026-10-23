import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target160 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow049Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 249, 239, 251, 291, 306, 382, 307, 392, 309, 319, 321, 336, 341, 344, 325, 345, 380, 358, 361, 321, 367, 322, 375, 376, 327, 377, 378, 363, 381, 404, 295, 406, 408, 383, 409, 317, 426, 431, 273, 442, 256, 448, 460, 449, 250, 450, 454, 245, 465, 474, 509, 493, 350, 506, 374, 507, 355, 511, 512, 298, 514, 524, 528, 550, 562, 585, 586, 549, 622, 403, 633, 621, 634]
private def rhs0 : List Reg := [228, 239, 245, 249, 250, 251, 256, 273, 291, 295, 298, 306, 307, 309, 317, 319, 322, 325, 327, 336, 341, 344, 345, 350, 355, 358, 361, 363, 367, 374, 375, 376, 377, 378, 380, 381, 382, 383, 392, 403, 404, 406, 408, 409, 426, 431, 442, 448, 449, 450, 454, 460, 465, 474, 493, 506, 507, 509, 511, 512, 514, 524, 528, 549, 550, 562, 585, 586, 621, 622, 633, 634]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (160 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (160 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row049_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 160 =
      injectionVector target original (basisState r) 160 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 160
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 160 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow049Normalized
#print axioms CurrentMain.PR926FullInjectionRow049Normalized.row049_basis

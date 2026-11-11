import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target151 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow040Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [232, 233, 242, 242, 247, 243, 287, 290, 307, 392, 314, 402, 321, 336, 337, 373, 343, 344, 325, 350, 351, 377, 356, 320, 359, 360, 363, 367, 322, 378, 363, 387, 404, 295, 406, 408, 383, 409, 317, 426, 431, 273, 442, 256, 462, 463, 462, 478, 464, 486, 489, 228, 496, 336, 504, 222, 507, 355, 511, 513, 241, 516, 498, 531, 568, 534, 570, 552, 583, 566, 569, 570, 588, 547, 599, 659, 615, 639, 640, 616, 656, 596, 657, 658]
private def rhs0 : List Reg := [222, 228, 232, 233, 241, 243, 247, 256, 273, 287, 290, 295, 307, 314, 317, 320, 321, 322, 325, 337, 343, 344, 350, 351, 355, 356, 359, 360, 367, 373, 377, 378, 383, 387, 392, 402, 404, 406, 408, 409, 426, 431, 442, 463, 464, 478, 486, 489, 496, 498, 504, 507, 511, 513, 516, 531, 534, 547, 552, 566, 568, 569, 583, 588, 596, 599, 615, 616, 639, 640, 656, 657, 658, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (151 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (151 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row040_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 151 =
      injectionVector target original (basisState r) 151 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 151
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 151 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow040Normalized
#print axioms CurrentMain.PR926FullInjectionRow040Normalized.row040_basis

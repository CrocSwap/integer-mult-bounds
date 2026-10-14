import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target178 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow067Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [229, 232, 247, 243, 278, 287, 309, 314, 402, 319, 323, 366, 329, 331, 329, 332, 342, 335, 364, 344, 325, 345, 380, 346, 349, 351, 377, 353, 371, 361, 321, 365, 379, 338, 385, 406, 426, 431, 273, 433, 442, 256, 476, 467, 486, 487, 489, 228, 490, 492, 341, 494, 504, 222, 506, 374, 509, 512, 298, 524, 525, 547, 549, 550, 559, 528, 564, 583, 597, 657, 598, 658, 615, 639, 640, 616]
private def rhs0 : List Reg := [222, 228, 229, 232, 243, 247, 256, 273, 278, 287, 298, 309, 314, 319, 321, 323, 325, 331, 332, 335, 338, 341, 342, 344, 345, 346, 349, 351, 353, 361, 364, 365, 366, 371, 374, 377, 379, 380, 385, 402, 406, 426, 431, 433, 442, 467, 476, 486, 487, 489, 490, 492, 494, 504, 506, 509, 512, 524, 525, 528, 547, 549, 550, 559, 564, 583, 597, 598, 615, 616, 639, 640, 657, 658]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (178 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (178 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row067_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 178 =
      injectionVector target original (basisState r) 178 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 178
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 178 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow067Normalized
#print axioms CurrentMain.PR926FullInjectionRow067Normalized.row067_basis

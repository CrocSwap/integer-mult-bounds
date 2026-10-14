import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target213 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow102Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 235, 240, 223, 246, 253, 229, 256, 264, 270, 271, 280, 260, 303, 313, 292, 331, 329, 335, 364, 341, 345, 380, 348, 359, 360, 367, 322, 372, 375, 384, 420, 246, 430, 257, 468, 472, 474, 509, 482, 503, 489, 228, 496, 336, 506, 374, 514, 519, 520, 536, 264, 539, 540, 571, 554, 556, 557, 422, 573, 537, 575, 539, 591, 637, 592, 645, 613, 642, 618, 572, 646, 520]
private def rhs0 : List Reg := [223, 229, 235, 240, 253, 256, 257, 260, 270, 271, 280, 292, 303, 313, 322, 329, 331, 335, 336, 341, 345, 348, 359, 360, 364, 367, 372, 374, 375, 380, 384, 420, 422, 430, 468, 472, 474, 482, 489, 496, 503, 506, 509, 514, 519, 536, 537, 540, 554, 556, 557, 571, 572, 573, 575, 591, 592, 613, 618, 637, 642, 645, 646]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (213 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (213 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row102_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 213 =
      injectionVector target original (basisState r) 213 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 213
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 213 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow102Normalized
#print axioms CurrentMain.PR926FullInjectionRow102Normalized.row102_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target200 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow089Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 233, 242, 235, 247, 243, 260, 265, 261, 281, 286, 309, 288, 304, 291, 294, 290, 298, 301, 411, 302, 296, 306, 382, 310, 315, 316, 393, 323, 366, 334, 346, 340, 342, 345, 380, 351, 377, 353, 371, 361, 321, 369, 365, 385, 388, 389, 310, 391, 413, 395, 311, 396, 299, 397, 308, 398, 289, 399, 403, 405, 401, 409, 317, 484, 488, 318, 497, 349, 506, 374, 515, 569, 534, 570, 535, 566, 571, 573, 537, 575, 539, 599, 659, 656, 596]
private def rhs0 : List Reg := [223, 233, 235, 242, 243, 247, 260, 261, 265, 281, 286, 288, 289, 290, 291, 294, 296, 298, 299, 301, 302, 304, 306, 308, 309, 311, 315, 316, 317, 318, 321, 323, 334, 340, 342, 345, 346, 349, 351, 353, 361, 365, 366, 369, 371, 374, 377, 380, 382, 385, 388, 389, 391, 393, 395, 396, 397, 398, 399, 401, 403, 405, 409, 411, 413, 484, 488, 497, 506, 515, 534, 535, 537, 539, 566, 569, 570, 571, 573, 575, 596, 599, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (200 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (200 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row089_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 200 =
      injectionVector target original (basisState r) 200 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 200
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 200 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow089Normalized
#print axioms CurrentMain.PR926FullInjectionRow089Normalized.row089_basis

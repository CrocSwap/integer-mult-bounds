import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target155 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow044Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [225, 226, 230, 231, 459, 238, 248, 241, 243, 249, 239, 253, 229, 255, 428, 263, 414, 267, 269, 272, 279, 269, 283, 284, 285, 436, 286, 309, 288, 304, 294, 290, 296, 298, 300, 410, 305, 394, 329, 338, 339, 343, 341, 344, 325, 346, 351, 377, 363, 364, 369, 365, 374, 376, 327, 379, 338, 383, 385, 386, 387, 389, 310, 399, 400, 297, 403, 404, 295, 405, 401, 408, 383, 418, 254, 419, 420, 246, 421, 272, 424, 259, 427, 438, 267, 439, 441, 442, 256, 443, 447, 226, 456, 237, 457, 461, 451, 464, 473, 340, 477, 485, 486, 491, 523, 524, 531, 568, 541, 582, 544, 312, 556, 580, 586, 549, 588, 547, 591, 637, 594, 643, 597, 657, 609, 628, 633, 621, 646, 520, 660, 595]
private def rhs0 : List Reg := [225, 229, 230, 231, 237, 238, 239, 241, 243, 246, 248, 249, 253, 254, 255, 256, 259, 263, 279, 283, 284, 285, 286, 288, 290, 294, 295, 296, 297, 298, 300, 304, 305, 309, 310, 312, 325, 327, 329, 339, 340, 341, 343, 344, 346, 351, 363, 364, 365, 369, 374, 376, 377, 379, 385, 386, 387, 389, 394, 399, 400, 401, 403, 404, 405, 408, 410, 414, 418, 419, 420, 421, 424, 427, 428, 436, 438, 439, 441, 442, 443, 447, 451, 456, 457, 459, 461, 464, 473, 477, 485, 486, 491, 520, 523, 524, 531, 541, 544, 547, 549, 556, 568, 580, 582, 586, 588, 591, 594, 595, 597, 609, 621, 628, 633, 637, 643, 646, 657, 660]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (155 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (155 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row044_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 155 =
      injectionVector target original (basisState r) 155 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 155
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 155 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow044Normalized
#print axioms CurrentMain.PR926FullInjectionRow044Normalized.row044_basis

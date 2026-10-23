import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target207 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow096Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 228, 234, 252, 235, 241, 243, 251, 291, 261, 267, 268, 427, 269, 270, 274, 284, 276, 439, 278, 280, 260, 282, 435, 285, 436, 298, 299, 317, 322, 323, 366, 325, 326, 530, 329, 335, 364, 338, 343, 345, 380, 346, 349, 351, 377, 353, 371, 354, 358, 359, 363, 365, 368, 377, 379, 338, 383, 387, 404, 295, 408, 383, 409, 317, 422, 432, 433, 437, 438, 267, 440, 442, 256, 448, 460, 449, 250, 454, 245, 460, 466, 467, 476, 467, 480, 538, 486, 492, 341, 493, 350, 494, 496, 336, 512, 298, 515, 569, 517, 518, 554, 524, 528, 547, 550, 551, 554, 558, 517, 559, 528, 562, 571, 584, 551, 586, 549, 591, 637, 593, 631, 597, 657, 615, 639, 618, 572, 633, 621, 644, 624, 646, 520, 656, 596]
private def rhs0 : List Reg := [222, 223, 228, 234, 235, 241, 243, 245, 250, 251, 252, 256, 260, 261, 268, 269, 270, 274, 276, 278, 280, 282, 284, 285, 291, 295, 299, 322, 323, 325, 326, 329, 335, 336, 341, 343, 345, 346, 349, 350, 351, 353, 354, 358, 359, 363, 364, 365, 366, 368, 371, 379, 380, 387, 404, 408, 409, 422, 427, 432, 433, 435, 436, 437, 438, 439, 440, 442, 448, 449, 454, 466, 476, 480, 486, 492, 493, 494, 496, 512, 515, 518, 520, 524, 530, 538, 547, 549, 550, 558, 559, 562, 569, 571, 572, 584, 586, 591, 593, 596, 597, 615, 618, 621, 624, 631, 633, 637, 639, 644, 646, 656, 657]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (207 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (207 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row096_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 207 =
      injectionVector target original (basisState r) 207 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 207
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 207 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow096Normalized
#print axioms CurrentMain.PR926FullInjectionRow096Normalized.row096_basis

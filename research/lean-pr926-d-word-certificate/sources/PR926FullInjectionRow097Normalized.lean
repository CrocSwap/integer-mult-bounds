import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target208 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow097Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [225, 226, 231, 459, 249, 239, 256, 260, 263, 414, 264, 266, 419, 279, 269, 281, 284, 285, 436, 291, 296, 300, 410, 301, 411, 305, 394, 310, 313, 292, 317, 322, 328, 330, 352, 335, 364, 341, 343, 344, 325, 346, 353, 371, 356, 320, 361, 321, 362, 333, 366, 374, 378, 363, 383, 388, 390, 283, 391, 413, 395, 311, 398, 289, 400, 297, 404, 295, 408, 383, 409, 317, 416, 418, 254, 419, 422, 424, 259, 426, 432, 438, 267, 439, 441, 442, 256, 450, 456, 237, 457, 458, 227, 460, 462, 464, 468, 477, 478, 464, 491, 495, 348, 496, 336, 497, 349, 518, 554, 531, 568, 533, 535, 541, 582, 556, 566, 574, 270, 588, 547, 591, 637, 593, 631, 597, 657, 599, 659, 612, 625, 644, 624, 646, 520]
private def rhs0 : List Reg := [225, 226, 227, 231, 237, 239, 249, 254, 259, 260, 263, 264, 266, 267, 269, 270, 279, 281, 283, 284, 285, 289, 291, 292, 295, 296, 297, 300, 301, 305, 310, 311, 313, 320, 321, 322, 325, 328, 330, 333, 335, 336, 341, 343, 344, 346, 348, 349, 352, 353, 356, 361, 362, 363, 364, 366, 371, 374, 378, 388, 390, 391, 394, 395, 398, 400, 404, 408, 409, 410, 411, 413, 414, 416, 418, 422, 424, 426, 432, 436, 438, 439, 441, 442, 450, 456, 457, 458, 459, 460, 462, 468, 477, 478, 491, 495, 496, 497, 518, 520, 531, 533, 535, 541, 547, 554, 556, 566, 568, 574, 582, 588, 591, 593, 597, 599, 612, 624, 625, 631, 637, 644, 646, 657, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (208 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (208 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row097_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 208 =
      injectionVector target original (basisState r) 208 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 208
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 208 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow097Normalized
#print axioms CurrentMain.PR926FullInjectionRow097Normalized.row097_basis

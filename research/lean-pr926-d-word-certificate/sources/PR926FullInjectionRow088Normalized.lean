import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target199 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow088Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 225, 226, 231, 459, 233, 242, 235, 236, 457, 239, 247, 243, 249, 239, 251, 291, 252, 265, 261, 271, 276, 439, 280, 260, 283, 284, 285, 436, 288, 304, 293, 294, 290, 295, 301, 411, 303, 304, 307, 392, 313, 292, 316, 393, 317, 320, 322, 324, 354, 325, 328, 330, 352, 335, 364, 336, 337, 373, 345, 380, 346, 348, 352, 353, 371, 354, 355, 358, 361, 321, 366, 371, 372, 373, 374, 380, 381, 383, 388, 389, 310, 390, 283, 393, 408, 383, 410, 413, 419, 422, 424, 259, 425, 258, 429, 490, 432, 434, 277, 438, 267, 439, 441, 452, 224, 457, 458, 227, 460, 469, 479, 471, 487, 491, 494, 498, 501, 510, 375, 541, 582, 555, 519, 556, 573, 537, 580, 582, 588, 547, 591, 637, 597, 657, 606, 649, 613, 642, 619, 636, 629, 608, 641, 617, 643, 646, 520]
private def rhs0 : List Reg := [223, 224, 225, 226, 227, 231, 233, 235, 236, 242, 243, 247, 249, 251, 252, 258, 259, 260, 261, 265, 267, 271, 276, 277, 280, 284, 285, 288, 290, 291, 292, 293, 294, 295, 301, 303, 307, 310, 313, 316, 317, 320, 321, 322, 324, 325, 328, 330, 335, 336, 337, 345, 346, 348, 353, 355, 358, 361, 364, 366, 372, 374, 375, 381, 388, 389, 390, 392, 408, 410, 411, 413, 419, 422, 424, 425, 429, 432, 434, 436, 438, 441, 452, 458, 459, 460, 469, 471, 479, 487, 490, 491, 494, 498, 501, 510, 519, 520, 537, 541, 547, 555, 556, 573, 580, 588, 591, 597, 606, 608, 613, 617, 619, 629, 636, 637, 641, 642, 643, 646, 649, 657]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (199 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (199 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row088_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 199 =
      injectionVector target original (basisState r) 199 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 199
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 199 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow088Normalized
#print axioms CurrentMain.PR926FullInjectionRow088Normalized.row088_basis

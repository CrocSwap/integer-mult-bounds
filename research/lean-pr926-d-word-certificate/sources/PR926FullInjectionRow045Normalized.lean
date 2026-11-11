import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target156 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow045Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 230, 234, 252, 235, 239, 251, 291, 252, 255, 428, 256, 260, 261, 266, 419, 267, 270, 286, 309, 288, 304, 294, 290, 301, 411, 305, 394, 306, 382, 307, 392, 308, 317, 325, 328, 329, 335, 364, 336, 341, 344, 325, 347, 368, 353, 371, 354, 356, 320, 359, 361, 321, 365, 367, 322, 368, 369, 365, 375, 381, 383, 386, 388, 393, 409, 317, 410, 416, 417, 433, 421, 272, 422, 431, 273, 433, 447, 226, 450, 454, 245, 455, 458, 227, 461, 451, 464, 466, 467, 473, 340, 474, 509, 476, 467, 477, 480, 538, 484, 492, 341, 506, 374, 507, 355, 511, 515, 569, 518, 554, 536, 264, 540, 571, 547, 551, 558, 517, 559, 528, 560, 524, 569, 571, 585, 588, 547, 593, 631, 595, 597, 657, 609, 628, 612, 625, 622, 403, 634, 644, 624, 651, 603, 656, 596, 657]
private def rhs0 : List Reg := [222, 226, 227, 230, 234, 235, 239, 245, 251, 255, 256, 260, 261, 264, 266, 267, 270, 272, 273, 286, 288, 290, 291, 294, 301, 304, 305, 306, 307, 308, 309, 320, 321, 322, 328, 329, 335, 336, 340, 344, 347, 353, 354, 355, 356, 359, 361, 364, 367, 369, 371, 374, 375, 381, 382, 383, 386, 388, 392, 393, 394, 403, 409, 410, 411, 416, 417, 419, 421, 422, 428, 431, 447, 450, 451, 454, 455, 458, 461, 464, 466, 473, 474, 476, 477, 480, 484, 492, 506, 507, 509, 511, 515, 517, 518, 524, 528, 536, 538, 540, 551, 554, 558, 559, 560, 585, 588, 593, 595, 596, 597, 603, 609, 612, 622, 624, 625, 628, 631, 634, 644, 651, 656]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (156 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (156 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row045_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 156 =
      injectionVector target original (basisState r) 156 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 156
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 156 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow045Normalized
#print axioms CurrentMain.PR926FullInjectionRow045Normalized.row045_basis

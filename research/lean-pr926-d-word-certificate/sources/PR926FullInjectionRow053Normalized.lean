import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target164 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow053Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 225, 226, 234, 252, 243, 247, 243, 253, 229, 256, 260, 262, 415, 272, 274, 284, 279, 269, 280, 260, 299, 300, 410, 301, 411, 306, 382, 307, 392, 317, 318, 320, 323, 366, 324, 354, 325, 326, 530, 328, 332, 342, 337, 373, 340, 346, 347, 368, 359, 360, 361, 321, 363, 366, 369, 365, 372, 373, 378, 363, 379, 338, 380, 381, 383, 396, 299, 398, 289, 416, 417, 433, 418, 254, 419, 420, 246, 421, 272, 424, 259, 426, 427, 432, 434, 277, 438, 267, 439, 442, 256, 452, 224, 457, 458, 227, 459, 462, 472, 473, 340, 478, 464, 482, 503, 495, 348, 498, 499, 484, 504, 222, 505, 446, 509, 517, 531, 568, 534, 570, 536, 264, 540, 571, 552, 583, 554, 556, 568, 570, 584, 551, 598, 658, 612, 625, 616, 617, 618, 572, 632, 620, 637, 640, 616, 650, 602, 651, 603, 656, 596]
private def rhs0 : List Reg := [223, 224, 225, 226, 227, 229, 234, 246, 247, 252, 253, 254, 259, 262, 264, 267, 269, 274, 277, 279, 280, 284, 289, 300, 301, 306, 307, 317, 318, 320, 321, 323, 324, 325, 326, 328, 332, 337, 338, 342, 346, 347, 348, 354, 359, 360, 361, 365, 368, 369, 372, 378, 379, 380, 381, 382, 383, 392, 396, 398, 410, 411, 415, 416, 417, 418, 419, 420, 421, 424, 426, 427, 432, 433, 434, 438, 439, 442, 446, 452, 457, 458, 459, 462, 464, 472, 473, 478, 482, 484, 495, 498, 499, 503, 504, 505, 509, 517, 530, 531, 534, 536, 540, 551, 552, 554, 556, 571, 572, 583, 584, 596, 598, 602, 603, 612, 617, 618, 620, 625, 632, 637, 640, 650, 651, 656, 658]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (164 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (164 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row053_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 164 =
      injectionVector target original (basisState r) 164 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 164
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 164 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow053Normalized
#print axioms CurrentMain.PR926FullInjectionRow053Normalized.row053_basis

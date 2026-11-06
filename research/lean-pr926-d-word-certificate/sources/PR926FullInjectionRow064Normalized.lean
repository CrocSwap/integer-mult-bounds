import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target175 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow064Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 232, 234, 252, 235, 241, 243, 246, 247, 243, 249, 239, 260, 265, 261, 268, 427, 272, 274, 284, 275, 441, 276, 439, 278, 280, 260, 286, 309, 296, 297, 299, 300, 410, 301, 411, 302, 296, 313, 292, 315, 319, 320, 322, 325, 326, 530, 330, 352, 334, 346, 335, 364, 337, 373, 339, 343, 340, 344, 325, 347, 368, 350, 356, 320, 357, 359, 361, 321, 363, 365, 368, 372, 373, 375, 378, 363, 380, 381, 390, 283, 398, 289, 400, 297, 401, 416, 417, 433, 420, 246, 427, 434, 277, 437, 443, 450, 460, 467, 480, 538, 488, 318, 496, 336, 498, 504, 222, 506, 374, 515, 569, 517, 518, 554, 532, 540, 571, 554, 571, 577, 546, 584, 551, 591, 637, 593, 631, 614, 638, 618, 572, 632, 620, 644, 624, 646, 520, 650, 602, 651, 603]
private def rhs0 : List Reg := [223, 232, 234, 235, 239, 241, 247, 249, 252, 261, 265, 268, 272, 274, 275, 276, 277, 278, 280, 283, 284, 286, 289, 292, 299, 300, 301, 302, 309, 313, 315, 318, 319, 321, 322, 326, 330, 334, 335, 336, 337, 339, 340, 343, 344, 346, 347, 350, 352, 356, 357, 359, 361, 364, 365, 372, 374, 375, 378, 380, 381, 390, 398, 400, 401, 410, 411, 416, 417, 420, 433, 434, 437, 439, 441, 443, 450, 460, 467, 480, 488, 496, 498, 504, 506, 515, 517, 518, 520, 530, 532, 538, 540, 546, 551, 569, 572, 577, 584, 591, 593, 602, 603, 614, 618, 620, 624, 631, 632, 637, 638, 644, 646, 650, 651]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (175 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (175 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row064_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 175 =
      injectionVector target original (basisState r) 175 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 175
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 175 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow064Normalized
#print axioms CurrentMain.PR926FullInjectionRow064Normalized.row064_basis

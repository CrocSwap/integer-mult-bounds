import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target192 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow081Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [232, 247, 243, 264, 271, 283, 293, 300, 410, 305, 394, 310, 312, 318, 319, 323, 366, 325, 328, 329, 340, 344, 325, 352, 361, 321, 364, 369, 365, 374, 390, 283, 394, 395, 311, 400, 297, 412, 293, 413, 416, 422, 432, 444, 470, 445, 271, 471, 475, 468, 486, 487, 489, 228, 491, 492, 341, 497, 349, 504, 222, 507, 355, 509, 515, 569, 529, 534, 570, 551, 553, 565, 569, 583, 585, 587, 548, 603, 604, 553, 605, 623, 635, 632, 620]
private def rhs0 : List Reg := [222, 228, 232, 243, 247, 264, 297, 300, 305, 310, 311, 312, 318, 319, 321, 323, 328, 329, 340, 341, 344, 349, 352, 355, 361, 364, 365, 366, 369, 374, 390, 395, 400, 410, 412, 413, 416, 422, 432, 444, 445, 468, 470, 471, 475, 486, 487, 489, 491, 492, 497, 504, 507, 509, 515, 529, 534, 548, 551, 565, 570, 583, 585, 587, 603, 604, 605, 620, 623, 632, 635]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (192 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (192 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row081_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 192 =
      injectionVector target original (basisState r) 192 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 192
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 192 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow081Normalized
#print axioms CurrentMain.PR926FullInjectionRow081Normalized.row081_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target161 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow050Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 228, 230, 235, 236, 457, 238, 248, 244, 455, 246, 247, 243, 249, 239, 254, 266, 419, 267, 288, 304, 300, 410, 305, 394, 322, 324, 354, 328, 329, 331, 329, 335, 364, 337, 373, 356, 320, 357, 360, 385, 389, 310, 399, 428, 433, 435, 447, 226, 449, 250, 453, 225, 454, 245, 458, 227, 461, 451, 472, 476, 467, 484, 486, 487, 492, 341, 510, 375, 511, 522, 652, 523, 549, 551, 558, 517, 559, 528, 564, 585, 586, 549, 604, 553, 621, 631, 633, 621, 636, 651, 603]
private def rhs0 : List Reg := [223, 225, 226, 227, 228, 230, 235, 236, 238, 239, 243, 244, 245, 246, 247, 248, 249, 250, 254, 266, 267, 288, 300, 304, 305, 310, 320, 322, 324, 328, 331, 335, 337, 341, 354, 356, 357, 360, 364, 373, 375, 385, 389, 394, 399, 410, 419, 428, 433, 435, 447, 449, 451, 453, 454, 455, 457, 458, 461, 467, 472, 476, 484, 486, 487, 492, 510, 511, 517, 522, 523, 528, 551, 553, 558, 559, 564, 585, 586, 603, 604, 631, 633, 636, 651, 652]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (161 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (161 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row050_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 161 =
      injectionVector target original (basisState r) 161 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 161
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 161 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow050Normalized
#print axioms CurrentMain.PR926FullInjectionRow050Normalized.row050_basis

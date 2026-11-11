import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target187 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow076Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [231, 459, 236, 457, 238, 248, 242, 244, 455, 246, 266, 419, 276, 439, 283, 288, 304, 289, 294, 290, 301, 411, 302, 296, 304, 313, 292, 316, 393, 319, 322, 334, 346, 347, 368, 349, 352, 365, 391, 413, 394, 405, 401, 418, 254, 429, 490, 434, 277, 446, 447, 226, 451, 452, 224, 456, 237, 461, 451, 463, 462, 473, 340, 486, 490, 522, 652, 529, 534, 570, 542, 384, 545, 328, 547, 548, 553, 558, 517, 565, 578, 385, 581, 303, 583, 587, 548, 601, 603, 623, 635, 626, 611, 629, 608, 632, 620, 653]
private def rhs0 : List Reg := [224, 226, 231, 236, 237, 238, 242, 244, 246, 248, 254, 266, 276, 277, 283, 288, 289, 290, 292, 294, 296, 301, 302, 303, 313, 316, 319, 322, 328, 334, 340, 346, 347, 349, 352, 365, 368, 384, 385, 391, 393, 394, 401, 405, 411, 413, 418, 419, 429, 434, 439, 446, 447, 452, 455, 456, 457, 459, 461, 462, 463, 473, 486, 517, 522, 529, 534, 542, 545, 547, 553, 558, 565, 570, 578, 581, 583, 587, 601, 603, 608, 611, 620, 623, 626, 629, 632, 635, 652, 653]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (187 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (187 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row076_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 187 =
      injectionVector target original (basisState r) 187 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 187
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 187 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow076Normalized
#print axioms CurrentMain.PR926FullInjectionRow076Normalized.row076_basis

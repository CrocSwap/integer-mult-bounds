import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target193 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow082Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [234, 252, 235, 236, 457, 238, 248, 240, 223, 243, 256, 260, 265, 261, 266, 419, 267, 269, 272, 302, 296, 306, 382, 308, 313, 292, 314, 402, 316, 393, 317, 319, 327, 329, 332, 342, 334, 346, 335, 364, 338, 339, 343, 343, 347, 368, 349, 350, 362, 333, 363, 364, 366, 370, 373, 396, 299, 400, 297, 402, 412, 293, 419, 420, 246, 421, 272, 426, 427, 435, 438, 267, 445, 271, 450, 453, 225, 460, 461, 451, 465, 468, 494, 495, 348, 497, 349, 498, 500, 502, 483, 512, 298, 513, 241, 514, 516, 498, 518, 554, 533, 535, 538, 543, 559, 528, 563, 564, 566, 573, 537, 579, 586, 549, 590, 443, 599, 659, 609, 628, 612, 625, 624, 634, 647, 648, 589, 660, 595]
private def rhs0 : List Reg := [223, 225, 234, 235, 236, 238, 240, 241, 243, 246, 248, 252, 256, 260, 261, 265, 266, 269, 271, 292, 293, 296, 297, 298, 299, 302, 306, 308, 313, 314, 316, 317, 319, 327, 329, 332, 333, 334, 335, 338, 339, 342, 346, 347, 348, 350, 362, 363, 366, 368, 370, 373, 382, 393, 396, 400, 412, 420, 421, 426, 427, 435, 438, 443, 445, 450, 451, 453, 457, 460, 461, 465, 468, 483, 494, 495, 497, 500, 502, 512, 513, 514, 516, 518, 528, 533, 535, 537, 538, 543, 549, 554, 559, 563, 564, 566, 573, 579, 586, 589, 590, 595, 599, 609, 612, 624, 625, 628, 634, 647, 648, 659, 660]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (193 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (193 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row082_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 193 =
      injectionVector target original (basisState r) 193 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 193
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 193 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow082Normalized
#print axioms CurrentMain.PR926FullInjectionRow082Normalized.row082_basis

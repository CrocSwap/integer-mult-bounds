import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target194 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow083Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 239, 244, 455, 251, 291, 255, 428, 260, 261, 262, 415, 263, 414, 280, 260, 281, 282, 435, 286, 309, 287, 294, 290, 301, 411, 302, 296, 303, 304, 306, 382, 307, 392, 310, 319, 322, 326, 530, 335, 364, 336, 337, 373, 339, 343, 343, 344, 325, 345, 380, 346, 347, 368, 348, 350, 353, 371, 355, 357, 370, 376, 327, 380, 384, 386, 387, 388, 390, 283, 392, 393, 399, 402, 410, 412, 293, 418, 254, 422, 423, 424, 259, 429, 490, 432, 434, 277, 436, 438, 267, 452, 224, 454, 245, 455, 460, 461, 451, 489, 228, 498, 510, 375, 514, 526, 543, 530, 533, 560, 524, 562, 566, 567, 532, 576, 535, 581, 303, 588, 547, 595, 597, 657, 614, 638, 615, 639, 627, 381, 628, 629, 608, 648, 589, 654, 601, 657, 659, 660, 595]
private def rhs0 : List Reg := [224, 239, 244, 245, 251, 254, 255, 259, 261, 262, 263, 267, 277, 280, 281, 282, 283, 286, 287, 290, 291, 293, 294, 296, 301, 302, 304, 306, 307, 309, 310, 319, 322, 325, 326, 327, 335, 336, 337, 339, 344, 345, 346, 347, 348, 350, 353, 355, 357, 364, 368, 370, 371, 373, 375, 376, 381, 382, 384, 386, 387, 388, 390, 393, 399, 402, 410, 411, 412, 414, 415, 418, 422, 423, 424, 428, 429, 432, 434, 435, 436, 438, 451, 452, 454, 460, 461, 489, 490, 498, 510, 514, 524, 526, 532, 533, 535, 543, 547, 560, 562, 566, 567, 576, 581, 588, 589, 597, 601, 608, 614, 615, 627, 628, 629, 638, 639, 648, 654, 659, 660]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (194 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (194 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row083_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 194 =
      injectionVector target original (basisState r) 194 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 194
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 194 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow083Normalized
#print axioms CurrentMain.PR926FullInjectionRow083Normalized.row083_basis

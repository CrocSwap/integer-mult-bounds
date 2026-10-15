import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target166 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow055Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 224, 225, 226, 228, 229, 230, 234, 252, 235, 241, 243, 256, 258, 260, 261, 262, 415, 265, 261, 268, 427, 269, 272, 274, 284, 275, 441, 276, 439, 278, 279, 269, 283, 286, 309, 296, 297, 302, 296, 303, 309, 312, 314, 402, 315, 320, 325, 329, 335, 364, 336, 341, 347, 368, 350, 351, 377, 353, 371, 355, 356, 320, 357, 360, 361, 321, 364, 365, 367, 322, 368, 369, 365, 370, 373, 375, 376, 327, 384, 386, 397, 308, 401, 407, 412, 293, 414, 423, 426, 427, 430, 257, 432, 438, 267, 440, 441, 453, 225, 457, 467, 480, 538, 486, 490, 491, 505, 446, 509, 510, 375, 515, 569, 518, 554, 523, 529, 532, 534, 570, 536, 264, 538, 564, 570, 571, 574, 270, 576, 535, 577, 546, 586, 549, 599, 659, 612, 625, 614, 638, 623, 635, 624, 656, 596]
private def rhs0 : List Reg := [222, 223, 224, 226, 228, 229, 230, 234, 235, 241, 243, 252, 256, 257, 258, 260, 262, 264, 265, 267, 268, 270, 272, 274, 275, 276, 278, 279, 283, 284, 286, 293, 297, 302, 303, 308, 312, 314, 315, 321, 322, 325, 327, 329, 335, 336, 341, 347, 350, 351, 353, 355, 356, 357, 360, 361, 367, 369, 370, 371, 373, 376, 377, 384, 386, 397, 401, 402, 407, 412, 414, 415, 423, 426, 430, 432, 438, 439, 440, 446, 453, 457, 467, 480, 486, 490, 491, 505, 509, 510, 515, 518, 523, 529, 532, 534, 535, 536, 546, 549, 554, 564, 569, 571, 574, 576, 577, 586, 596, 599, 612, 614, 623, 624, 625, 635, 638, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (166 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (166 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row055_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 166 =
      injectionVector target original (basisState r) 166 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 166
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 166 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow055Normalized
#print axioms CurrentMain.PR926FullInjectionRow055Normalized.row055_basis

import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target119 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow008Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [225, 226, 239, 244, 455, 251, 291, 256, 258, 261, 265, 261, 276, 439, 279, 269, 281, 285, 436, 292, 300, 410, 301, 411, 304, 305, 394, 307, 392, 311, 314, 402, 315, 316, 393, 317, 320, 321, 322, 330, 352, 331, 329, 335, 364, 344, 325, 347, 368, 349, 354, 358, 370, 373, 375, 380, 388, 390, 283, 393, 396, 299, 399, 401, 402, 404, 295, 405, 401, 406, 410, 412, 293, 414, 416, 418, 254, 419, 424, 259, 426, 432, 437, 438, 267, 439, 441, 442, 256, 447, 226, 449, 250, 457, 460, 462, 464, 477, 478, 464, 492, 341, 495, 348, 496, 336, 498, 518, 554, 520, 526, 543, 527, 563, 536, 264, 545, 328, 556, 562, 573, 537, 579, 581, 303, 589, 591, 637, 600, 655, 611, 618, 572, 619, 636, 627, 381, 654, 601]
private def rhs0 : List Reg := [225, 239, 244, 250, 251, 254, 258, 259, 264, 265, 267, 269, 276, 279, 281, 283, 285, 291, 292, 293, 295, 299, 300, 301, 303, 304, 305, 307, 311, 314, 315, 316, 317, 320, 321, 322, 325, 328, 329, 330, 331, 335, 336, 341, 344, 347, 348, 349, 352, 354, 358, 364, 368, 370, 373, 375, 380, 381, 388, 390, 392, 394, 396, 399, 404, 405, 406, 411, 412, 414, 416, 418, 419, 424, 426, 432, 436, 437, 438, 441, 442, 447, 449, 455, 457, 460, 462, 477, 478, 492, 495, 496, 498, 518, 520, 526, 527, 536, 537, 543, 545, 554, 556, 562, 563, 572, 573, 579, 581, 589, 591, 600, 601, 611, 618, 619, 627, 636, 637, 654, 655]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [119])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [119]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row008_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 119 =
      injectionVector target original (basisState r) 119 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 119
      (by decide), injection_coordinate target original (basisState r) 119 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow008Normalized
#print axioms CurrentMain.PR926FullInjectionRow008Normalized.row008_basis

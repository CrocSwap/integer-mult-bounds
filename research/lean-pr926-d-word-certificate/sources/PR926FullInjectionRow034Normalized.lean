import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target145 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow034Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 232, 236, 457, 239, 240, 223, 243, 246, 251, 291, 252, 260, 269, 272, 274, 284, 285, 436, 288, 304, 290, 291, 298, 300, 410, 301, 411, 306, 382, 308, 309, 310, 314, 402, 315, 316, 393, 317, 322, 326, 530, 330, 352, 334, 346, 336, 337, 373, 338, 342, 346, 351, 377, 353, 371, 357, 358, 367, 322, 370, 379, 338, 386, 388, 401, 405, 401, 409, 317, 410, 422, 423, 430, 257, 431, 273, 437, 440, 442, 256, 445, 271, 449, 250, 453, 225, 455, 460, 461, 451, 472, 484, 486, 496, 336, 499, 484, 511, 516, 498, 519, 521, 527, 563, 540, 571, 552, 583, 566, 567, 532, 570, 575, 539, 587, 548, 592, 645, 596, 597, 657, 599, 659, 604, 553, 610, 613, 642, 627, 381, 630, 607, 640, 616, 652, 655, 658]
private def rhs0 : List Reg := [225, 232, 236, 239, 240, 243, 246, 250, 251, 252, 256, 257, 260, 269, 271, 272, 273, 274, 284, 285, 288, 290, 298, 300, 301, 304, 306, 308, 309, 310, 314, 315, 316, 326, 330, 334, 337, 342, 351, 352, 353, 357, 358, 367, 370, 371, 373, 377, 379, 381, 382, 386, 388, 393, 402, 405, 409, 411, 422, 423, 430, 431, 436, 437, 440, 442, 445, 449, 451, 453, 455, 457, 460, 461, 472, 486, 496, 498, 499, 511, 516, 519, 521, 527, 530, 532, 539, 540, 548, 552, 553, 563, 566, 567, 570, 571, 575, 583, 587, 592, 596, 597, 599, 604, 607, 610, 613, 616, 627, 630, 640, 642, 645, 652, 655, 657, 658, 659]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [145])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [145]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row034_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 145 =
      injectionVector target original (basisState r) 145 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 145
      (by decide), injection_coordinate target original (basisState r) 145 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow034Normalized
#print axioms CurrentMain.PR926FullInjectionRow034Normalized.row034_basis

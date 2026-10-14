import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target136 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow025Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [224, 230, 234, 252, 242, 254, 255, 428, 262, 415, 266, 419, 267, 268, 427, 276, 439, 278, 279, 269, 285, 436, 287, 303, 312, 313, 292, 314, 402, 321, 327, 328, 329, 333, 335, 364, 337, 373, 344, 325, 347, 368, 352, 355, 356, 320, 357, 359, 364, 365, 372, 384, 390, 283, 400, 297, 403, 412, 293, 420, 246, 421, 272, 424, 259, 430, 257, 439, 440, 443, 452, 224, 453, 225, 458, 227, 462, 463, 462, 478, 464, 490, 495, 348, 496, 336, 498, 502, 483, 508, 372, 525, 528, 548, 550, 559, 528, 562, 564, 584, 551, 631, 634, 635]
private def rhs0 : List Reg := [225, 227, 230, 234, 242, 246, 252, 254, 255, 257, 259, 262, 266, 267, 268, 269, 272, 276, 278, 279, 283, 285, 287, 292, 293, 297, 303, 312, 313, 314, 320, 321, 325, 327, 328, 329, 333, 335, 336, 337, 344, 347, 348, 352, 355, 356, 357, 359, 365, 368, 373, 384, 390, 400, 402, 403, 412, 415, 419, 420, 421, 424, 427, 428, 430, 436, 440, 443, 452, 453, 458, 463, 464, 478, 483, 490, 495, 496, 498, 502, 508, 525, 548, 550, 551, 559, 562, 564, 584, 631, 634, 635]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [136])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [136]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row025_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 136 =
      injectionVector target original (basisState r) 136 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 136
      (by decide), injection_coordinate target original (basisState r) 136 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow025Normalized
#print axioms CurrentMain.PR926FullInjectionRow025Normalized.row025_basis

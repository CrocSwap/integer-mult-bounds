import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target112 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow001Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 225, 226, 232, 246, 256, 258, 261, 265, 261, 267, 270, 274, 284, 280, 260, 282, 435, 286, 309, 288, 304, 292, 297, 300, 410, 304, 307, 392, 308, 313, 292, 316, 393, 322, 329, 337, 373, 340, 341, 346, 354, 356, 320, 369, 365, 370, 380, 383, 386, 390, 283, 391, 413, 399, 400, 297, 401, 414, 418, 254, 419, 421, 272, 422, 424, 259, 431, 273, 433, 439, 440, 441, 447, 226, 457, 465, 466, 474, 509, 476, 467, 481, 472, 484, 488, 318, 492, 341, 499, 484, 507, 355, 511, 518, 554, 527, 563, 536, 264, 545, 328, 547, 551, 558, 517, 559, 528, 572, 581, 303, 585, 597, 657, 600, 655, 611, 615, 639, 622, 403, 627, 381, 634, 651, 603, 654, 601]
private def rhs0 : List Reg := [223, 225, 232, 246, 254, 256, 258, 259, 260, 264, 265, 267, 270, 272, 273, 274, 280, 282, 283, 284, 286, 288, 300, 303, 307, 308, 309, 313, 316, 318, 320, 322, 328, 329, 337, 340, 346, 354, 355, 356, 365, 369, 370, 373, 380, 381, 383, 386, 390, 391, 392, 393, 399, 400, 401, 403, 410, 413, 414, 418, 419, 421, 422, 424, 431, 433, 435, 439, 440, 441, 447, 457, 465, 466, 467, 472, 474, 476, 481, 488, 492, 499, 507, 509, 511, 517, 518, 527, 528, 536, 545, 547, 551, 554, 558, 559, 563, 572, 581, 585, 597, 600, 601, 603, 611, 615, 622, 627, 634, 639, 651, 654, 655, 657]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [112])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [112]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row001_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 112 =
      injectionVector target original (basisState r) 112 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 112
      (by decide), injection_coordinate target original (basisState r) 112 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow001Normalized
#print axioms CurrentMain.PR926FullInjectionRow001Normalized.row001_basis

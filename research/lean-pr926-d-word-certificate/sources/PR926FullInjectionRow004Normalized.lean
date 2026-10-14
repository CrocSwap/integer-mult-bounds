import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target115 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow004Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 231, 459, 236, 457, 240, 223, 247, 243, 252, 266, 419, 268, 427, 274, 284, 276, 439, 278, 280, 260, 324, 354, 326, 530, 328, 330, 352, 332, 342, 334, 346, 337, 373, 339, 343, 341, 347, 368, 351, 377, 353, 371, 356, 320, 358, 362, 333, 369, 365, 370, 375, 379, 338, 416, 417, 433, 421, 272, 423, 425, 258, 426, 431, 273, 432, 437, 442, 256, 443, 445, 271, 452, 224, 456, 237, 458, 227, 483, 501, 505, 446, 511, 518, 554, 521, 530, 536, 264, 557, 422, 572, 575, 539, 607, 626, 611, 627, 381]
private def rhs0 : List Reg := [223, 224, 227, 228, 231, 236, 237, 240, 243, 247, 252, 256, 258, 260, 264, 266, 268, 271, 272, 273, 274, 276, 278, 280, 284, 320, 324, 326, 328, 330, 332, 333, 334, 337, 338, 339, 341, 342, 343, 346, 347, 351, 352, 353, 354, 356, 358, 362, 365, 368, 369, 370, 371, 373, 375, 377, 379, 381, 416, 417, 419, 421, 422, 423, 425, 426, 427, 431, 432, 433, 437, 439, 442, 443, 445, 446, 452, 456, 457, 458, 459, 483, 501, 505, 511, 518, 521, 536, 539, 554, 557, 572, 575, 607, 611, 626, 627]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [115])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [115]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row004_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 115 =
      injectionVector target original (basisState r) 115 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 115
      (by decide), injection_coordinate target original (basisState r) 115 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow004Normalized
#print axioms CurrentMain.PR926FullInjectionRow004Normalized.row004_basis

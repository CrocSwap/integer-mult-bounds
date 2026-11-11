import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target133 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow022Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 232, 235, 246, 253, 229, 268, 427, 278, 280, 260, 286, 309, 297, 315, 322, 332, 342, 337, 373, 340, 343, 345, 380, 356, 320, 363, 365, 368, 385, 386, 396, 299, 407, 416, 421, 272, 467, 480, 538, 482, 503, 488, 318, 493, 350, 499, 484, 506, 374, 516, 498, 535, 537, 540, 571, 566, 567, 532, 569, 570, 571, 590, 443, 593, 631, 619, 636, 644, 624, 647]
private def rhs0 : List Reg := [228, 229, 232, 235, 246, 253, 260, 268, 272, 278, 280, 286, 297, 299, 309, 315, 318, 320, 322, 332, 337, 340, 342, 343, 345, 350, 356, 363, 365, 368, 373, 374, 380, 385, 386, 396, 407, 416, 421, 427, 443, 467, 480, 482, 484, 488, 493, 498, 499, 503, 506, 516, 532, 535, 537, 538, 540, 566, 567, 569, 570, 590, 593, 619, 624, 631, 636, 644, 647]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [133])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [133]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row022_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 133 =
      injectionVector target original (basisState r) 133 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 133
      (by decide), injection_coordinate target original (basisState r) 133 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow022Normalized
#print axioms CurrentMain.PR926FullInjectionRow022Normalized.row022_basis

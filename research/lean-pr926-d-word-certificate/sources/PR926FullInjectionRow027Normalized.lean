import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target138 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow027Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [228, 233, 242, 235, 241, 242, 246, 247, 243, 252, 253, 229, 265, 261, 268, 427, 278, 279, 269, 281, 293, 297, 303, 313, 292, 319, 321, 332, 342, 334, 346, 349, 351, 377, 353, 371, 361, 321, 365, 368, 369, 365, 376, 327, 378, 363, 379, 338, 384, 385, 417, 433, 420, 246, 421, 272, 423, 430, 257, 432, 445, 271, 462, 463, 462, 465, 467, 478, 464, 480, 538, 482, 503, 483, 493, 350, 495, 348, 496, 336, 497, 349, 501, 511, 515, 569, 536, 264, 537, 540, 571, 569, 573, 537, 590, 443, 593, 631, 619, 636, 644, 624, 647]
private def rhs0 : List Reg := [228, 229, 233, 235, 241, 243, 247, 252, 253, 257, 261, 264, 265, 268, 269, 271, 272, 278, 279, 281, 292, 293, 297, 303, 313, 319, 327, 332, 334, 336, 338, 342, 346, 348, 350, 351, 353, 361, 363, 368, 369, 371, 376, 377, 378, 379, 384, 385, 417, 420, 421, 423, 427, 430, 432, 433, 443, 445, 463, 464, 465, 467, 478, 480, 482, 483, 493, 495, 496, 497, 501, 503, 511, 515, 536, 538, 540, 571, 573, 590, 593, 619, 624, 631, 636, 644, 647]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [138])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [138]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row027_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 138 =
      injectionVector target original (basisState r) 138 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 138
      (by decide), injection_coordinate target original (basisState r) 138 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow027Normalized
#print axioms CurrentMain.PR926FullInjectionRow027Normalized.row027_basis

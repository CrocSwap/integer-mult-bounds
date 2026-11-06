import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target139 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow028Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [224, 231, 459, 232, 234, 252, 240, 223, 242, 274, 284, 283, 323, 366, 324, 354, 326, 530, 341, 351, 377, 357, 360, 375, 379, 338, 425, 258, 437, 438, 267, 439, 456, 237, 463, 462, 465, 472, 473, 340, 494, 496, 336, 499, 484, 502, 483, 505, 446, 513, 241, 514, 529, 540, 571, 565, 576, 535, 599, 659, 620, 621, 623, 635, 631, 656, 596]
private def rhs0 : List Reg := [223, 224, 231, 232, 234, 237, 240, 241, 242, 252, 258, 267, 274, 283, 284, 323, 324, 326, 336, 338, 340, 341, 351, 354, 357, 360, 366, 375, 377, 379, 425, 437, 438, 439, 446, 456, 459, 462, 463, 465, 472, 473, 483, 484, 494, 496, 499, 502, 505, 513, 514, 529, 530, 535, 540, 565, 571, 576, 596, 599, 620, 621, 623, 631, 635, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [139])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [139]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row028_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 139 =
      injectionVector target original (basisState r) 139 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 139
      (by decide), injection_coordinate target original (basisState r) 139 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow028Normalized
#print axioms CurrentMain.PR926FullInjectionRow028Normalized.row028_basis

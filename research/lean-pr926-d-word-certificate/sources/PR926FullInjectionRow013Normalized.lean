import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target124 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow013Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 232, 234, 252, 240, 223, 241, 244, 455, 246, 249, 239, 280, 260, 283, 292, 302, 296, 324, 354, 331, 329, 335, 364, 348, 367, 322, 372, 382, 390, 283, 391, 413, 417, 433, 423, 481, 472, 487, 492, 341, 496, 336, 501, 504, 222, 510, 375, 514, 520, 546, 555, 519, 556, 572, 579, 580, 581, 303, 594, 643, 613, 642, 618, 572, 637, 645, 648, 589]
private def rhs0 : List Reg := [223, 232, 234, 239, 240, 241, 244, 246, 249, 252, 260, 280, 292, 296, 302, 303, 322, 324, 329, 331, 335, 336, 341, 348, 354, 364, 367, 372, 375, 382, 390, 391, 413, 417, 423, 433, 455, 472, 481, 487, 492, 496, 501, 504, 510, 514, 519, 520, 546, 555, 556, 579, 580, 581, 589, 594, 613, 618, 637, 642, 643, 645, 648]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [124])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [124]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row013_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 124 =
      injectionVector target original (basisState r) 124 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 124
      (by decide), injection_coordinate target original (basisState r) 124 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow013Normalized
#print axioms CurrentMain.PR926FullInjectionRow013Normalized.row013_basis

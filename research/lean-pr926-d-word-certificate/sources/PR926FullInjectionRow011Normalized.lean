import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target122 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow011Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [240, 223, 253, 229, 322, 484, 485, 486, 499, 484, 503, 504, 222]
private def rhs0 : List Reg := [222, 223, 229, 240, 253, 322, 485, 486, 499, 503, 504]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [122])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [122]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row011_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 122 =
      injectionVector target original (basisState r) 122 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 122
      (by decide), injection_coordinate target original (basisState r) 122 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow011Normalized
#print axioms CurrentMain.PR926FullInjectionRow011Normalized.row011_basis

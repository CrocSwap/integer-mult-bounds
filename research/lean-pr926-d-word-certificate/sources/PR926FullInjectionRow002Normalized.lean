import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target113 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow002Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [381, 436, 453, 225, 456, 237, 609, 628, 626, 611, 627, 381, 628, 629, 608]
private def rhs0 : List Reg := [225, 237, 436, 453, 456, 608, 609, 611, 626, 627, 629]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [113])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [113]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row002_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 113 =
      injectionVector target original (basisState r) 113 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 113
      (by decide), injection_coordinate target original (basisState r) 113 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow002Normalized
#print axioms CurrentMain.PR926FullInjectionRow002Normalized.row002_basis

import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target120 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow009Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 235, 242, 247, 243, 263, 414, 284, 288, 304, 294, 290, 300, 410, 305, 394, 307, 392, 314, 402, 316, 393, 318, 319, 323, 366, 340, 342, 345, 380, 351, 377, 361, 321, 374, 378, 363, 386, 387, 389, 310, 397, 308, 399, 401, 403, 404, 295, 405, 401, 406, 407, 408, 383, 440, 463, 462, 473, 340, 484, 491, 494, 509, 512, 298, 534, 570, 541, 582, 552, 583, 577, 546, 588, 547, 597, 657, 598, 658, 638]
private def rhs0 : List Reg := [223, 235, 242, 243, 247, 263, 284, 288, 290, 294, 295, 298, 300, 304, 305, 307, 308, 310, 314, 316, 318, 319, 321, 323, 342, 345, 351, 361, 363, 366, 374, 377, 378, 380, 383, 386, 387, 389, 392, 393, 394, 397, 399, 402, 403, 404, 405, 406, 407, 408, 410, 414, 440, 462, 463, 473, 484, 491, 494, 509, 512, 534, 541, 546, 547, 552, 570, 577, 582, 583, 588, 597, 598, 638, 657, 658]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [120])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [120]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row009_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 120 =
      injectionVector target original (basisState r) 120 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 120
      (by decide), injection_coordinate target original (basisState r) 120 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow009Normalized
#print axioms CurrentMain.PR926FullInjectionRow009Normalized.row009_basis

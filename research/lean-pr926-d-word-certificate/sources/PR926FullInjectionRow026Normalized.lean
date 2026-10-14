import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target137 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow026Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [233, 242, 234, 252, 240, 223, 246, 247, 243, 252, 265, 261, 270, 272, 273, 280, 260, 281, 286, 309, 299, 315, 319, 322, 331, 329, 332, 342, 334, 346, 335, 364, 340, 341, 351, 377, 353, 371, 358, 359, 369, 365, 375, 379, 338, 386, 417, 433, 421, 272, 423, 430, 257, 443, 464, 465, 472, 473, 340, 474, 509, 477, 483, 488, 318, 489, 228, 501, 502, 483, 518, 554, 519, 558, 517, 572, 591, 637, 592, 645, 613, 642, 618, 572, 646, 520]
private def rhs0 : List Reg := [223, 228, 233, 234, 240, 242, 243, 246, 247, 257, 260, 261, 265, 270, 273, 280, 281, 286, 299, 309, 315, 318, 319, 322, 329, 331, 332, 334, 335, 338, 341, 342, 346, 351, 353, 358, 359, 364, 365, 369, 371, 375, 377, 379, 386, 417, 421, 423, 430, 433, 443, 464, 465, 472, 473, 474, 477, 488, 489, 501, 502, 509, 517, 518, 519, 520, 554, 558, 591, 592, 613, 618, 637, 642, 645, 646]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [137])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [137]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row026_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 137 =
      injectionVector target original (basisState r) 137 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 137
      (by decide), injection_coordinate target original (basisState r) 137 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow026Normalized
#print axioms CurrentMain.PR926FullInjectionRow026Normalized.row026_basis

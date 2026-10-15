import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target130 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow019Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [233, 242, 235, 238, 248, 244, 455, 247, 243, 248, 249, 239, 250, 253, 229, 270, 271, 290, 294, 290, 297, 302, 296, 316, 393, 319, 331, 329, 335, 364, 341, 344, 325, 345, 380, 358, 365, 368, 375, 391, 413, 392, 404, 295, 405, 401, 408, 383, 417, 433, 423, 432, 445, 271, 449, 250, 454, 245, 461, 451, 465, 467, 472, 474, 509, 480, 538, 482, 503, 499, 484, 504, 222, 506, 374, 507, 355, 518, 554, 521, 536, 264, 539, 540, 571, 557, 422, 574, 270, 575, 539, 612, 625, 630, 607]
private def rhs0 : List Reg := [222, 229, 233, 235, 238, 239, 242, 243, 244, 245, 247, 249, 253, 264, 294, 295, 296, 297, 302, 316, 319, 325, 329, 331, 335, 341, 344, 345, 355, 358, 364, 365, 368, 374, 375, 380, 383, 391, 392, 393, 401, 404, 405, 408, 413, 417, 422, 423, 432, 433, 445, 449, 451, 454, 455, 461, 465, 467, 472, 474, 480, 482, 484, 499, 503, 504, 506, 507, 509, 518, 521, 536, 538, 540, 554, 557, 571, 574, 575, 607, 612, 625, 630]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [130])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [130]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row019_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 130 =
      injectionVector target original (basisState r) 130 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 130
      (by decide), injection_coordinate target original (basisState r) 130 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow019Normalized
#print axioms CurrentMain.PR926FullInjectionRow019Normalized.row019_basis

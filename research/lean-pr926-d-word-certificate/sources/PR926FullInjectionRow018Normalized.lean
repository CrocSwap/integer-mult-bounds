import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target129 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow018Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [235, 240, 223, 253, 229, 274, 284, 280, 260, 298, 303, 313, 292, 321, 324, 354, 329, 331, 329, 334, 346, 335, 364, 336, 346, 352, 357, 360, 361, 321, 364, 365, 367, 322, 372, 381, 384, 417, 433, 423, 425, 258, 440, 482, 503, 487, 492, 341, 498, 510, 375, 511, 512, 298, 514, 547, 552, 583, 555, 519, 556, 584, 551, 585, 588, 547, 591, 637, 592, 645, 615, 639, 640, 616, 642, 646, 520]
private def rhs0 : List Reg := [223, 229, 235, 240, 253, 258, 260, 274, 280, 284, 292, 303, 313, 322, 324, 331, 334, 335, 336, 341, 352, 354, 357, 360, 361, 365, 367, 372, 375, 381, 384, 417, 423, 425, 433, 440, 482, 487, 492, 498, 503, 510, 511, 512, 514, 519, 520, 551, 552, 555, 556, 583, 584, 585, 588, 591, 592, 615, 616, 637, 639, 640, 642, 645, 646]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [129])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [129]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row018_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 129 =
      injectionVector target original (basisState r) 129 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 129
      (by decide), injection_coordinate target original (basisState r) 129 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow018Normalized
#print axioms CurrentMain.PR926FullInjectionRow018Normalized.row018_basis

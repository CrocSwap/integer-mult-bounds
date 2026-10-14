import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target116 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow005Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 231, 459, 233, 242, 235, 236, 457, 240, 223, 242, 263, 414, 271, 274, 284, 275, 441, 280, 260, 293, 296, 303, 314, 402, 319, 327, 333, 334, 346, 342, 349, 351, 377, 352, 353, 371, 369, 365, 371, 378, 363, 386, 391, 413, 400, 297, 403, 412, 293, 413, 417, 433, 423, 425, 258, 437, 446, 447, 226, 452, 224, 456, 237, 463, 462, 469, 479, 471, 473, 340, 484, 499, 484, 504, 222, 523, 525, 526, 543, 528, 534, 570, 544, 312, 561, 525, 581, 303, 582, 594, 643, 606, 649, 614, 638, 626, 611, 629, 608, 641, 617, 648, 589, 654, 601]
private def rhs0 : List Reg := [222, 224, 226, 231, 233, 235, 236, 237, 240, 258, 260, 263, 271, 274, 275, 280, 284, 296, 297, 312, 314, 319, 327, 333, 334, 340, 342, 346, 349, 351, 352, 353, 363, 365, 369, 377, 378, 386, 391, 400, 402, 403, 412, 414, 417, 423, 425, 433, 437, 441, 446, 447, 452, 456, 457, 459, 462, 463, 469, 471, 473, 479, 499, 504, 523, 526, 528, 534, 543, 544, 561, 570, 581, 582, 589, 594, 601, 606, 608, 611, 614, 617, 626, 629, 638, 641, 643, 648, 649, 654]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [116])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [116]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row005_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 116 =
      injectionVector target original (basisState r) 116 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 116
      (by decide), injection_coordinate target original (basisState r) 116 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow005Normalized
#print axioms CurrentMain.PR926FullInjectionRow005Normalized.row005_basis

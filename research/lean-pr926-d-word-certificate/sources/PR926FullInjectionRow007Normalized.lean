import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target118 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow007Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 225, 230, 231, 459, 238, 248, 246, 253, 229, 258, 261, 262, 415, 263, 414, 266, 419, 274, 284, 280, 260, 292, 293, 296, 302, 296, 306, 382, 314, 402, 315, 316, 393, 317, 324, 354, 325, 343, 345, 380, 348, 352, 355, 361, 321, 362, 333, 367, 322, 371, 378, 363, 384, 396, 299, 401, 402, 406, 413, 414, 415, 417, 433, 419, 422, 423, 429, 490, 432, 434, 277, 438, 267, 439, 440, 441, 450, 453, 225, 457, 458, 227, 460, 461, 451, 469, 479, 471, 472, 482, 503, 483, 486, 498, 505, 446, 514, 515, 569, 527, 563, 530, 531, 568, 539, 540, 571, 542, 384, 544, 312, 561, 525, 571, 574, 270, 578, 385, 582, 593, 631, 594, 643, 600, 655, 608, 627, 381, 629, 608, 630, 607, 641, 617, 644, 624, 656, 596]
private def rhs0 : List Reg := [223, 227, 229, 230, 231, 238, 246, 248, 253, 258, 260, 261, 262, 263, 266, 267, 270, 274, 277, 280, 284, 292, 293, 299, 302, 306, 312, 314, 315, 316, 317, 321, 322, 324, 325, 333, 343, 345, 348, 352, 354, 355, 361, 362, 363, 367, 371, 378, 380, 381, 382, 385, 393, 396, 401, 406, 413, 417, 422, 423, 429, 432, 433, 434, 438, 439, 440, 441, 446, 450, 451, 453, 457, 458, 459, 460, 461, 469, 471, 472, 479, 482, 483, 486, 490, 498, 503, 505, 514, 515, 525, 527, 530, 531, 539, 540, 542, 544, 561, 563, 568, 569, 574, 578, 582, 593, 594, 596, 600, 607, 617, 624, 627, 629, 630, 631, 641, 643, 644, 655, 656]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [118])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [118]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row007_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 118 =
      injectionVector target original (basisState r) 118 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 118
      (by decide), injection_coordinate target original (basisState r) 118 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow007Normalized
#print axioms CurrentMain.PR926FullInjectionRow007Normalized.row007_basis

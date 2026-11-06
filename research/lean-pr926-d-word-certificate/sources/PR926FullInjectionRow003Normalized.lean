import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target114 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow003Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 233, 242, 235, 237, 240, 223, 246, 254, 258, 259, 266, 419, 267, 280, 260, 284, 288, 304, 294, 290, 300, 410, 302, 296, 305, 394, 307, 392, 316, 393, 322, 346, 347, 368, 364, 389, 310, 391, 413, 399, 404, 295, 405, 401, 408, 383, 417, 433, 423, 425, 258, 428, 433, 435, 437, 459, 476, 467, 484, 486, 499, 484, 504, 222, 522, 652, 523, 548, 549, 551, 558, 517, 559, 528, 564, 583, 586, 549, 597, 657, 598, 658, 604, 553, 615, 639, 616, 621, 631, 633, 621, 636, 637, 639, 642, 651, 603]
private def rhs0 : List Reg := [222, 233, 235, 237, 240, 242, 246, 254, 259, 260, 266, 267, 280, 284, 288, 290, 294, 295, 296, 300, 302, 304, 305, 307, 310, 316, 322, 346, 347, 364, 368, 383, 389, 391, 392, 393, 394, 399, 401, 404, 405, 408, 410, 413, 417, 419, 423, 425, 428, 435, 437, 459, 467, 476, 486, 499, 504, 517, 522, 523, 528, 548, 551, 553, 558, 559, 564, 583, 586, 597, 598, 603, 604, 615, 616, 631, 633, 636, 637, 642, 651, 652, 657, 658]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [114])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [114]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row003_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 114 =
      injectionVector target original (basisState r) 114 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 114
      (by decide), injection_coordinate target original (basisState r) 114 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow003Normalized
#print axioms CurrentMain.PR926FullInjectionRow003Normalized.row003_basis

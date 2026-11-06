import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target128 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow017Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [231, 459, 235, 236, 457, 240, 223, 253, 229, 263, 414, 274, 284, 275, 441, 280, 260, 291, 297, 300, 410, 301, 411, 305, 394, 306, 382, 307, 392, 310, 319, 323, 366, 341, 344, 325, 345, 380, 361, 321, 365, 368, 381, 385, 388, 395, 311, 398, 289, 404, 295, 408, 383, 409, 317, 425, 258, 432, 433, 437, 445, 271, 446, 447, 226, 452, 224, 456, 237, 467, 480, 538, 482, 503, 497, 349, 507, 355, 510, 375, 515, 569, 518, 554, 521, 530, 533, 535, 536, 264, 538, 539, 557, 422, 566, 571, 576, 535, 599, 659, 612, 625, 630, 607, 656, 596]
private def rhs0 : List Reg := [223, 224, 226, 229, 231, 235, 236, 237, 240, 253, 258, 260, 263, 264, 271, 274, 275, 280, 284, 289, 291, 295, 297, 300, 301, 305, 306, 307, 310, 311, 317, 319, 321, 323, 325, 341, 344, 345, 349, 355, 361, 365, 366, 368, 375, 380, 381, 382, 383, 385, 388, 392, 394, 395, 398, 404, 408, 409, 410, 411, 414, 422, 425, 432, 433, 437, 441, 445, 446, 447, 452, 456, 457, 459, 467, 480, 482, 497, 503, 507, 510, 515, 518, 521, 530, 533, 536, 539, 554, 557, 566, 569, 571, 576, 596, 599, 607, 612, 625, 630, 656, 659]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [128])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [128]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row017_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 128 =
      injectionVector target original (basisState r) 128 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 128
      (by decide), injection_coordinate target original (basisState r) 128 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow017Normalized
#print axioms CurrentMain.PR926FullInjectionRow017Normalized.row017_basis

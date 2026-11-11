import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target142 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow031Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [231, 459, 239, 241, 243, 246, 251, 291, 253, 229, 256, 265, 261, 266, 419, 268, 427, 283, 288, 304, 292, 297, 301, 411, 306, 382, 307, 392, 313, 292, 315, 318, 326, 530, 333, 335, 364, 338, 339, 343, 341, 343, 344, 325, 351, 377, 353, 371, 365, 368, 369, 365, 370, 388, 390, 283, 391, 413, 393, 395, 311, 399, 400, 297, 403, 404, 295, 405, 401, 418, 254, 426, 429, 490, 432, 442, 256, 443, 446, 447, 226, 450, 454, 245, 455, 461, 451, 464, 467, 473, 340, 477, 480, 538, 485, 486, 488, 318, 490, 506, 374, 509, 518, 554, 522, 652, 523, 524, 528, 529, 536, 264, 545, 328, 553, 563, 569, 570, 571, 581, 303, 587, 548, 593, 631, 605, 612, 625, 623, 635, 626, 611, 644, 624, 656, 596]
private def rhs0 : List Reg := [226, 229, 231, 239, 241, 243, 245, 246, 251, 253, 254, 261, 264, 265, 266, 268, 288, 291, 295, 301, 303, 304, 306, 307, 311, 313, 315, 325, 326, 328, 333, 335, 338, 339, 340, 341, 344, 351, 353, 364, 368, 369, 370, 371, 374, 377, 382, 388, 390, 391, 392, 393, 395, 399, 400, 401, 403, 404, 405, 411, 413, 418, 419, 426, 427, 429, 432, 442, 443, 446, 447, 450, 451, 454, 455, 459, 461, 464, 467, 473, 477, 480, 485, 486, 488, 506, 509, 518, 522, 523, 524, 528, 529, 530, 536, 538, 545, 548, 553, 554, 563, 569, 570, 571, 581, 587, 593, 596, 605, 611, 612, 623, 624, 625, 626, 631, 635, 644, 652, 656]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [142])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [142]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row031_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 142 =
      injectionVector target original (basisState r) 142 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 142
      (by decide), injection_coordinate target original (basisState r) 142 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow031Normalized
#print axioms CurrentMain.PR926FullInjectionRow031Normalized.row031_basis

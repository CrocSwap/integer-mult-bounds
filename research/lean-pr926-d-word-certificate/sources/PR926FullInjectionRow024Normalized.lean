import PR926FullInjectionRows
import BitXorRowNormalization

/-! One complete actual target135 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both whole-word pullback
identities remain unchanged from first client7e6233a7. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow024Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [222, 223, 225, 226, 230, 231, 459, 234, 252, 240, 223, 243, 246, 247, 243, 256, 261, 263, 414, 267, 269, 274, 284, 279, 269, 280, 260, 281, 282, 435, 292, 298, 299, 303, 309, 313, 292, 318, 321, 323, 366, 324, 354, 325, 332, 342, 337, 373, 338, 339, 343, 340, 341, 344, 325, 346, 347, 368, 349, 353, 371, 354, 358, 359, 360, 361, 321, 363, 364, 366, 369, 365, 370, 371, 372, 376, 327, 387, 390, 283, 400, 297, 406, 418, 254, 419, 421, 272, 422, 426, 439, 443, 444, 470, 453, 225, 456, 237, 457, 459, 464, 469, 479, 472, 473, 340, 475, 468, 477, 482, 503, 484, 485, 486, 487, 496, 336, 503, 509, 510, 375, 517, 531, 568, 536, 264, 541, 582, 542, 384, 546, 551, 552, 583, 554, 556, 558, 517, 559, 528, 581, 303, 582, 612, 625, 616, 617, 618, 572, 622, 403, 634, 637, 641, 617]
private def rhs0 : List Reg := [222, 226, 230, 231, 234, 237, 240, 246, 247, 252, 254, 256, 260, 261, 263, 264, 267, 272, 274, 279, 280, 281, 282, 283, 284, 297, 298, 299, 309, 313, 318, 323, 324, 327, 332, 336, 337, 338, 339, 341, 342, 343, 344, 346, 347, 349, 353, 358, 359, 360, 361, 363, 364, 365, 368, 369, 370, 372, 373, 375, 376, 384, 387, 390, 400, 403, 406, 414, 418, 419, 421, 422, 426, 435, 439, 443, 444, 453, 456, 457, 464, 468, 469, 470, 472, 473, 475, 477, 479, 482, 484, 485, 486, 487, 496, 509, 510, 528, 531, 536, 541, 542, 546, 551, 552, 554, 556, 558, 559, 568, 572, 581, 583, 612, 616, 618, 622, 625, 634, 637, 641]
private theorem lhs0_exact :
    pullWord helpers (offTarget target (pullWord encoded [135])) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    offTarget target (pullWord original [135]) = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row024_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 135 =
      injectionVector target original (basisState r) 135 := by
  rw [prepared_injection_coordinate target encoded helpers (basisState r) 135
      (by decide), injection_coordinate target original (basisState r) 135 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow024Normalized
#print axioms CurrentMain.PR926FullInjectionRow024Normalized.row024_basis

import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target203 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow092Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [223, 228, 232, 233, 242, 238, 248, 242, 244, 455, 247, 243, 251, 291, 253, 229, 280, 260, 288, 304, 291, 298, 301, 411, 310, 319, 323, 366, 332, 342, 337, 373, 343, 349, 356, 320, 361, 321, 363, 388, 389, 310, 395, 311, 397, 308, 398, 289, 399, 403, 416, 426, 431, 273, 432, 442, 256, 445, 271, 448, 460, 450, 461, 451, 463, 462, 473, 340, 482, 503, 484, 486, 493, 350, 497, 349, 499, 484, 515, 569, 516, 498, 518, 554, 521, 535, 536, 264, 539, 540, 571, 557, 422, 566, 567, 532, 570, 571, 612, 625, 630, 607]
private def rhs0 : List Reg := [223, 228, 229, 232, 233, 238, 243, 244, 247, 248, 251, 253, 256, 260, 264, 271, 273, 280, 288, 289, 298, 301, 304, 308, 311, 319, 320, 321, 323, 332, 337, 340, 342, 343, 350, 356, 361, 363, 366, 373, 388, 389, 395, 397, 398, 399, 403, 411, 416, 422, 426, 431, 432, 442, 445, 448, 450, 451, 455, 460, 461, 462, 463, 473, 482, 486, 493, 497, 498, 499, 503, 515, 516, 518, 521, 532, 535, 536, 539, 540, 554, 557, 566, 567, 569, 570, 607, 612, 625, 630]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (203 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (203 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row092_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 203 =
      injectionVector target original (basisState r) 203 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 203
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 203 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow092Normalized
#print axioms CurrentMain.PR926FullInjectionRow092Normalized.row092_basis

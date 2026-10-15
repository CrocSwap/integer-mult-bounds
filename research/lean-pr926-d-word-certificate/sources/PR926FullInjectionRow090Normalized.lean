import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target201 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow090Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [224, 226, 233, 242, 234, 252, 240, 223, 241, 243, 247, 243, 253, 229, 261, 266, 419, 271, 274, 284, 280, 260, 281, 291, 292, 294, 290, 298, 302, 296, 304, 308, 310, 312, 315, 317, 324, 354, 325, 329, 332, 342, 334, 346, 335, 364, 336, 337, 373, 338, 343, 345, 380, 347, 368, 355, 358, 360, 361, 321, 362, 333, 364, 367, 322, 370, 379, 338, 381, 385, 388, 389, 310, 395, 311, 396, 299, 397, 308, 401, 405, 401, 407, 409, 317, 412, 293, 415, 419, 425, 258, 429, 490, 437, 439, 447, 226, 458, 227, 482, 503, 505, 446, 515, 569, 523, 527, 563, 529, 530, 538, 539, 540, 571, 542, 384, 564, 570, 571, 578, 385, 586, 549, 600, 655, 605, 606, 649, 608, 624, 627, 381, 630, 607, 653, 656, 596]
private def rhs0 : List Reg := [223, 224, 227, 229, 233, 234, 240, 241, 242, 247, 252, 253, 258, 260, 261, 266, 271, 274, 280, 281, 284, 290, 291, 292, 293, 294, 296, 298, 299, 302, 304, 311, 312, 315, 321, 322, 324, 325, 329, 332, 333, 334, 335, 336, 337, 342, 343, 345, 346, 347, 354, 355, 358, 360, 361, 362, 367, 368, 370, 373, 379, 380, 384, 388, 389, 395, 396, 397, 405, 407, 409, 412, 415, 425, 429, 437, 439, 446, 447, 458, 482, 490, 503, 505, 515, 523, 527, 529, 530, 538, 539, 540, 542, 549, 563, 564, 569, 570, 578, 586, 596, 600, 605, 606, 607, 608, 624, 627, 630, 649, 653, 655, 656]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (201 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (201 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row090_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 201 =
      injectionVector target original (basisState r) 201 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 201
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 201 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow090Normalized
#print axioms CurrentMain.PR926FullInjectionRow090Normalized.row090_basis

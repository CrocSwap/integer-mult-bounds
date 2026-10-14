import PR926FullInjectionRows
import BitXorRowNormalization
import BitXorTargetDonorCollector
import PR926InjectionJoinSupport

/-! One complete actual target186 row, using proved multiplicity-preserving
parity normalization instead of661 repeated scans. Both literal donor lists and the public basis statement remain unchanged.
Equivalent destination-filtered identities use the accepted injection-support facts. Equality of computed
normal forms supplies every singleton equation via an arbitrary-state theorem.
This controls resource fit before other rows are admitted. Exact PR915/926
source/attribution and generic structural-sort credit remain in predecessors.
Apache-2.0; OpenAI assistance. Uncompiled source proposal. -/
namespace CurrentMain.PR926FullInjectionRow075Normalized
open BitXor BitXorFiniteBasis BitXorInjectionAdapter BitXorRowPullback
open BitXorRowNormalization PR926PreparationSupport PR926FullInjectionRows
open BitXorTargetDonorCollector PR926InjectionJoinSupport
set_option Elab.async false
private def decodeNat (n : Nat) : Reg := ⟨n % 661, Nat.mod_lt n (by decide)⟩
private theorem decode_key (r : Reg) : decodeNat r.val = r := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt r.isLt

private def lhs0 : List Reg := [227, 230, 236, 457, 240, 223, 242, 247, 243, 262, 415, 265, 261, 270, 274, 284, 280, 260, 281, 285, 436, 287, 296, 298, 302, 296, 309, 315, 319, 323, 366, 333, 340, 345, 380, 361, 321, 371, 385, 387, 400, 297, 401, 402, 412, 293, 417, 433, 423, 424, 259, 425, 258, 437, 440, 447, 226, 457, 458, 227, 463, 462, 473, 340, 488, 318, 494, 499, 484, 504, 222, 506, 374, 512, 298, 525, 546, 562, 582, 594, 643, 600, 655, 607, 610, 625, 628, 648, 589, 660, 595]
private def rhs0 : List Reg := [222, 223, 226, 230, 236, 240, 242, 243, 247, 258, 259, 260, 261, 262, 265, 270, 274, 280, 281, 284, 285, 287, 293, 297, 302, 309, 315, 318, 319, 321, 323, 333, 345, 361, 366, 371, 374, 380, 385, 387, 400, 401, 402, 412, 415, 417, 423, 424, 425, 433, 436, 437, 440, 447, 458, 462, 463, 473, 484, 488, 494, 499, 504, 506, 512, 525, 546, 562, 582, 589, 594, 595, 600, 607, 610, 625, 628, 643, 648, 655, 660]
private theorem lhs0_exact :
    pullWord helpers (collectDonors (186 : Reg) encoded) = lhs0 := by
  decide +kernel
private theorem rhs0_exact :
    collectDonors (186 : Reg) original = rhs0 := by
  decide +kernel
private theorem parity0 :
    normalForm Fin.val decodeNat lhs0 = normalForm Fin.val decodeNat rhs0 := by
  decide +kernel
theorem row075_basis (r : Reg) :
    injectionVector target encoded (run helpers (basisState r)) 186 =
      injectionVector target original (basisState r) 186 := by
  rw [prepared_injection_coordinate_collected target encoded helpers
      encoded_injection.1 encoded_injection.2 (basisState r) 186
      (by decide), injection_coordinate_collected target original
      original_injection.1 original_injection.2 (basisState r) 186 (by decide),
    lhs0_exact, rhs0_exact]
  exact donorXor_eq_of_normalForm Fin.val decodeNat decode_key lhs0 rhs0 parity0
    (basisState r)

end CurrentMain.PR926FullInjectionRow075Normalized
#print axioms CurrentMain.PR926FullInjectionRow075Normalized.row075_basis
